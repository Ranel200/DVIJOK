"""HTTP-роутер модуля orders (ТЗ A3).

Чтение доступно всем сотрудникам; механик видит только свои заказы (ТЗ T5).
Создание/редактирование — ADMIN/MANAGER; смена статуса и добавление позиций —
включая MECHANIC.
"""

from io import BytesIO
from pathlib import Path
from typing import Annotated
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.core.exceptions import BusinessRuleError
from app.core.pagination import Page, PaginationParams
from app.modules.mechanics.repository import MechanicRepository
from app.modules.orders.models import OrderDocument
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderCreate,
    OrderDocumentRead,
    OrderIntakeCreate,
    OrderItemCreate,
    OrderRead,
    OrderStatusUpdate,
    OrderUpdate,
)
from app.modules.orders.service import (
    MAX_DOCUMENT_SIZE_BYTES,
    MAX_DOCUMENTS_PER_UPLOAD,
    OrderService,
)
from app.modules.schedule.repository import ScheduleRepository
from app.modules.schedule.schemas import OrderReservationCreate, SlotRead
from app.modules.schedule.service import ScheduleService
from app.modules.users.models import User
from app.shared.enums import OrderSource, OrderStatus, UserRole

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(get_current_user)])

manage = require_roles(UserRole.ADMIN, UserRole.MANAGER)
staff = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.MECHANIC)


def get_order_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> OrderService:
    return OrderService(OrderRepository(db, current_user.organization_id), current_user)


@router.get("", response_model=Page[OrderRead])
async def list_orders(
    pagination: PaginationParams = Depends(),
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    source: OrderSource | None = Query(default=None),
    mechanic_id: int | None = Query(default=None),
    query: str | None = Query(default=None, description="Поиск: номер / клиент / авто"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db, scope="function"),
    service: OrderService = Depends(get_order_service),
) -> Page[OrderRead]:
    effective_mechanic_id = mechanic_id
    if current_user.role == UserRole.MECHANIC:
        # Механик ограничен своими заказами; -1 гарантирует пустую выдачу без профиля.
        own = await MechanicRepository(db, current_user.organization_id).get_by_user_id(
            current_user.id
        )
        effective_mechanic_id = own.id if own else -1

    items, total = await service.list_page(
        status=status_filter,
        source=source,
        mechanic_id=effective_mechanic_id,
        query=query,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderRead:
    if payload.mechanic_id is not None or payload.scheduled_at is not None:
        raise BusinessRuleError(
            "Создайте заказ без календарного назначения, затем используйте "
            "/orders/{order_id}/reservation"
        )
    return await service.create(payload, created_by_id=current_user.id)


@router.post(
    "/intake",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def create_order_intake(
    payload: OrderIntakeCreate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderRead:
    return await service.create_intake(payload, created_by_id=current_user.id)


@router.post(
    "/{order_id}/reservation",
    response_model=SlotRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def reserve_order_slot(
    order_id: int,
    payload: OrderReservationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db, scope="function"),
    service: OrderService = Depends(get_order_service),
) -> SlotRead:
    await service.lock(order_id)
    duration = await service.appointment_duration(order_id, payload.duration_minutes)
    schedule = ScheduleService(ScheduleRepository(db, current_user.organization_id))
    existing = await schedule.repo.get_slot_by_order(order_id)
    if existing is not None:
        await schedule.repo.delete_slot(existing)
    slot = await schedule.reserve(
        mechanic_id=payload.mechanic_id,
        start_time=payload.start_time,
        duration_minutes=duration,
        order_id=order_id,
        title=f"Заказ {order_id}",
    )
    order = await service.get(order_id)
    order.mechanic_id = payload.mechanic_id
    order.scheduled_at = payload.start_time
    await db.flush()
    return slot


@router.delete(
    "/{order_id}/reservation",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(manage)],
)
async def cancel_order_reservation(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db, scope="function"),
    service: OrderService = Depends(get_order_service),
) -> None:
    order = await service.lock(order_id)
    schedule = ScheduleService(ScheduleRepository(db, current_user.organization_id))
    slot = await schedule.repo.get_slot_by_order(order_id)
    if slot is not None:
        await schedule.repo.delete_slot(slot)
    order.mechanic_id = None
    order.scheduled_at = None
    await db.flush()


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, service: OrderService = Depends(get_order_service)) -> OrderRead:
    return await service.get(order_id)


@router.patch("/{order_id}", response_model=OrderRead, dependencies=[Depends(manage)])
async def update_order(
    order_id: int, payload: OrderUpdate, service: OrderService = Depends(get_order_service)
) -> OrderRead:
    if {"mechanic_id", "scheduled_at"} & payload.model_fields_set:
        raise BusinessRuleError(
            "Для назначения или снятия времени используйте endpoint reservation"
        )
    return await service.update(order_id, payload)


@router.patch("/{order_id}/status", response_model=OrderRead, dependencies=[Depends(staff)])
async def change_order_status(
    order_id: int, payload: OrderStatusUpdate, service: OrderService = Depends(get_order_service)
) -> OrderRead:
    return await service.change_status(order_id, payload.status)


@router.get("/{order_id}/document", response_model=OrderDocumentRead)
async def get_order_document(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderDocument:
    return await service.get_document(order_id)


@router.get("/{order_id}/documents", response_model=list[OrderDocumentRead])
async def list_order_documents(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> list[OrderDocument]:
    return await service.list_documents(order_id)


def _document_response(document: OrderDocument) -> Response:
    encoded_name = quote(document.filename, safe="")
    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}",
            "Content-Length": str(document.size_bytes),
            "X-Content-SHA256": document.sha256,
        },
    )


@router.get(
    "/{order_id}/document/content",
    response_class=Response,
    responses={
        200: {
            "content": {
                "application/pdf": {},
                "text/html": {},
                "image/jpeg": {},
                "image/png": {},
                "image/webp": {},
                "image/gif": {},
            },
            "description": "Документ как вложение",
        }
    },
)
async def download_order_document(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> Response:
    document = await service.get_document(order_id)
    return _document_response(document)


@router.get("/{order_id}/documents/{document_id}/content", response_class=Response)
async def download_specific_order_document(
    order_id: int,
    document_id: int,
    service: OrderService = Depends(get_order_service),
) -> Response:
    return _document_response(await service.get_document(order_id, document_id))


@router.get("/{order_id}/documents/archive", response_class=Response)
async def download_order_documents_archive(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> Response:
    documents = await service.list_documents(order_id)
    if not documents:
        raise BusinessRuleError("У заказа нет документов")
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        for document in documents:
            archive.writestr(f"{document.id}-{Path(document.filename).name}", document.content)
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="order-{order_id}-documents.zip"'
        },
    )


@router.post(
    "/{order_id}/document/generate",
    response_model=OrderDocumentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def generate_order_document(
    order_id: int,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderDocument:
    return await service.generate_document(order_id, current_user.id)


@router.post(
    "/{order_id}/documents/generate",
    response_model=list[OrderDocumentRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def generate_order_documents(
    order_id: int,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> list[OrderDocument]:
    return [await service.generate_document(order_id, current_user.id)]


@router.post(
    "/{order_id}/document/upload",
    response_model=OrderDocumentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def upload_order_document(
    order_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderDocument:
    content = await file.read(MAX_DOCUMENT_SIZE_BYTES + 1)
    return await service.upload_document(
        order_id,
        filename=file.filename,
        content_type=file.content_type,
        content=content,
        created_by_id=current_user.id,
    )


@router.post(
    "/{order_id}/documents/upload",
    response_model=list[OrderDocumentRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def upload_order_documents(
    order_id: int,
    files: Annotated[
        list[UploadFile],
        File(
            description=(
                f"От 1 до {MAX_DOCUMENTS_PER_UPLOAD} "
                "PDF/HTML/JPEG/PNG/WebP/GIF файлов"
            )
        ),
    ],
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> list[OrderDocument]:
    payload = [
        (file.filename, file.content_type, await file.read(MAX_DOCUMENT_SIZE_BYTES + 1))
        for file in files
    ]
    return await service.upload_documents(order_id, payload, current_user.id)


@router.delete(
    "/{order_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(manage)],
)
async def delete_order_document(
    order_id: int,
    document_id: int,
    service: OrderService = Depends(get_order_service),
) -> None:
    await service.delete_document(order_id, document_id)


@router.post(
    "/{order_id}/items",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(staff)],
)
async def add_order_item(
    order_id: int, payload: OrderItemCreate, service: OrderService = Depends(get_order_service)
) -> OrderRead:
    return await service.add_item(order_id, payload)


@router.delete(
    "/{order_id}/items/{item_id}", response_model=OrderRead, dependencies=[Depends(staff)]
)
async def remove_order_item(
    order_id: int, item_id: int, service: OrderService = Depends(get_order_service)
) -> OrderRead:
    return await service.remove_item(order_id, item_id)


@router.delete(
    "/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(manage)]
)
async def delete_order(order_id: int, service: OrderService = Depends(get_order_service)) -> None:
    await service.delete(order_id)

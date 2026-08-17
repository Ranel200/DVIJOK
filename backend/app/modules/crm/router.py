"""Frontend-oriented CRM API for the administrative application."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_feature
from app.modules.crm.schemas import (
    CrmBulkDelete,
    CrmClientBrief,
    CrmColumn,
    CrmOrderRead,
    CrmOrderStatusUpdate,
    CrmOrderWrite,
)
from app.modules.crm.service import CrmService
from app.modules.orders.repository import OrderRepository
from app.modules.services.admin_schemas import AdminServiceRead
from app.modules.services.admin_service import AdminServiceCatalog
from app.modules.services.repository import ServiceRepository
from app.modules.tasks.schemas import TaskEmployee
from app.modules.tasks.service import TaskService
from app.modules.users.models import User
from app.shared.enums import UserRole

router = APIRouter(
    prefix="/crm",
    tags=["crm"],
    dependencies=[
        Depends(require_feature("crm", UserRole.ADMIN, UserRole.MANAGER, UserRole.MECHANIC))
    ],
)


def get_crm_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> CrmService:
    return CrmService(
        OrderRepository(db, current_user.organization_id),
        current_user,
    )


@router.get("/services", response_model=list[AdminServiceRead])
async def list_crm_services(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> list[AdminServiceRead]:
    catalog = AdminServiceCatalog(ServiceRepository(db, current_user.organization_id))
    return await catalog.list()


@router.get("/employees", response_model=list[TaskEmployee])
async def list_crm_employees(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> list[TaskEmployee]:
    return await TaskService(db, current_user).employees()


@router.get("/clients", response_model=list[CrmClientBrief])
async def list_crm_clients(
    service: CrmService = Depends(get_crm_service),
) -> list[CrmClientBrief]:
    return await service.clients()


@router.get("/columns", response_model=list[CrmColumn])
async def list_crm_columns(
    service: CrmService = Depends(get_crm_service),
) -> list[CrmColumn]:
    return await service.columns()


@router.get("/deals", response_model=list[CrmOrderRead])
async def list_crm_deals(
    service: CrmService = Depends(get_crm_service),
) -> list[CrmOrderRead]:
    return await service.list_deals()


@router.post(
    "/orders",
    response_model=CrmOrderRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_crm_order(
    payload: CrmOrderWrite,
    service: CrmService = Depends(get_crm_service),
) -> CrmOrderRead:
    return await service.create(payload)


@router.delete(
    "/orders/bulk",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_crm_orders(
    payload: CrmBulkDelete,
    service: CrmService = Depends(get_crm_service),
) -> None:
    await service.delete_many(payload.ids)


@router.get("/orders/{order_id}", response_model=CrmOrderRead)
async def get_crm_order(
    order_id: int,
    service: CrmService = Depends(get_crm_service),
) -> CrmOrderRead:
    return await service.get(order_id)


@router.put(
    "/orders/{order_id}",
    response_model=CrmOrderRead,
)
async def update_crm_order(
    order_id: int,
    payload: CrmOrderWrite,
    service: CrmService = Depends(get_crm_service),
) -> CrmOrderRead:
    return await service.update(order_id, payload)


@router.patch(
    "/orders/{order_id}/status",
    response_model=CrmOrderRead,
)
async def update_crm_order_status(
    order_id: int,
    payload: CrmOrderStatusUpdate,
    service: CrmService = Depends(get_crm_service),
) -> CrmOrderRead:
    return await service.change_status(order_id, payload.status)


@router.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_crm_order(
    order_id: int,
    service: CrmService = Depends(get_crm_service),
) -> None:
    await service.delete(order_id)

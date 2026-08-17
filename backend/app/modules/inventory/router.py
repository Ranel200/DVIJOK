"""HTTP-роутер модуля inventory (ТЗ A8).

Просмотр — все сотрудники. Управление позициями — ADMIN. Движения по складу —
ADMIN; списание под заказ — ADMIN и MECHANIC (механик списывает запчасти, ТЗ A1).
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.core.pagination import Page, PaginationParams
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    MovementCreate,
    MovementRead,
    WriteOffRequest,
)
from app.modules.inventory.service import InventoryService
from app.modules.users.models import User
from app.shared.enums import InventoryCategory, UserRole

router = APIRouter(
    prefix="/inventory", tags=["inventory"], dependencies=[Depends(get_current_user)]
)

admin_only = require_roles(UserRole.ADMIN)
admin_or_mechanic = require_roles(UserRole.ADMIN, UserRole.MECHANIC)


def get_inventory_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> InventoryService:
    return InventoryService(InventoryRepository(db, current_user.organization_id))


@router.get("", response_model=Page[InventoryItemRead])
async def list_inventory(
    pagination: PaginationParams = Depends(),
    query: str | None = Query(default=None, description="Поиск по названию/артикулу"),
    category: InventoryCategory | None = Query(default=None),
    low_stock: bool = Query(default=False, description="Только позиции ниже минимума"),
    service: InventoryService = Depends(get_inventory_service),
) -> Page[InventoryItemRead]:
    items, total = await service.list_page(
        query=query,
        category=category,
        low_stock=low_stock,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post(
    "",
    response_model=InventoryItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_only)],
)
async def create_item(
    payload: InventoryItemCreate, service: InventoryService = Depends(get_inventory_service)
) -> InventoryItemRead:
    return await service.create(payload)


@router.get("/{item_id}", response_model=InventoryItemRead)
async def get_item(
    item_id: int, service: InventoryService = Depends(get_inventory_service)
) -> InventoryItemRead:
    return await service.get(item_id)


@router.patch("/{item_id}", response_model=InventoryItemRead, dependencies=[Depends(admin_only)])
async def update_item(
    item_id: int,
    payload: InventoryItemUpdate,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryItemRead:
    return await service.update(item_id, payload)


@router.delete(
    "/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_only)]
)
async def delete_item(
    item_id: int, service: InventoryService = Depends(get_inventory_service)
) -> None:
    await service.delete(item_id)


@router.post(
    "/{item_id}/movements", response_model=InventoryItemRead, dependencies=[Depends(admin_only)]
)
async def register_movement(
    item_id: int,
    payload: MovementCreate,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryItemRead:
    item, _ = await service.register_movement(item_id, payload, current_user.id)
    return item


@router.post(
    "/{item_id}/write-off",
    response_model=InventoryItemRead,
    dependencies=[Depends(admin_or_mechanic)],
)
async def write_off(
    item_id: int,
    payload: WriteOffRequest,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryItemRead:
    item, _ = await service.write_off_for_order(
        item_id, payload.quantity, payload.order_id, payload.comment, current_user.id
    )
    return item


@router.get("/{item_id}/movements", response_model=Page[MovementRead])
async def list_movements(
    item_id: int,
    pagination: PaginationParams = Depends(),
    service: InventoryService = Depends(get_inventory_service),
) -> Page[MovementRead]:
    items, total = await service.list_movements(
        item_id, limit=pagination.limit, offset=pagination.offset
    )
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)

"""HTTP-роутер модуля mechanics. Чтение — ADMIN/MANAGER; управление — ADMIN."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.core.pagination import Page, PaginationParams
from app.modules.mechanics.repository import MechanicRepository
from app.modules.mechanics.schemas import MechanicCreate, MechanicRead, MechanicUpdate
from app.modules.mechanics.service import MechanicService
from app.modules.users.models import User
from app.shared.enums import UserRole

router = APIRouter(
    prefix="/mechanics",
    tags=["mechanics"],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))],
)

admin_only = require_roles(UserRole.ADMIN)
_current = require_roles(UserRole.ADMIN, UserRole.MANAGER)


def get_mechanic_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(_current),
) -> MechanicService:
    return MechanicService(MechanicRepository(db, current_user.organization_id))


@router.get("", response_model=Page[MechanicRead])
async def list_mechanics(
    pagination: PaginationParams = Depends(),
    service: MechanicService = Depends(get_mechanic_service),
) -> Page[MechanicRead]:
    items, total = await service.list_page(limit=pagination.limit, offset=pagination.offset)
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post(
    "",
    response_model=MechanicRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_only)],
)
async def create_mechanic(
    payload: MechanicCreate, service: MechanicService = Depends(get_mechanic_service)
) -> MechanicRead:
    return await service.create(payload)


@router.get("/{mechanic_id}", response_model=MechanicRead)
async def get_mechanic(
    mechanic_id: int, service: MechanicService = Depends(get_mechanic_service)
) -> MechanicRead:
    return await service.get(mechanic_id)


@router.patch("/{mechanic_id}", response_model=MechanicRead, dependencies=[Depends(admin_only)])
async def update_mechanic(
    mechanic_id: int,
    payload: MechanicUpdate,
    service: MechanicService = Depends(get_mechanic_service),
) -> MechanicRead:
    return await service.update(mechanic_id, payload)


@router.delete(
    "/{mechanic_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_only)]
)
async def delete_mechanic(
    mechanic_id: int, service: MechanicService = Depends(get_mechanic_service)
) -> None:
    await service.delete(mechanic_id)

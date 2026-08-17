"""HTTP-роутер модуля users. Управление сотрудниками — только для ADMIN (ТЗ A10)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.core.pagination import Page, PaginationParams
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate
from app.modules.users.service import UserService
from app.shared.enums import UserRole

router = APIRouter(prefix="/users", tags=["users"])

admin_only = require_roles(UserRole.ADMIN)


def get_user_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(admin_only),
) -> UserService:
    return UserService(UserRepository(db, current_user.organization_id))


@router.get("", response_model=Page[UserRead], dependencies=[Depends(admin_only)])
async def list_users(
    pagination: PaginationParams = Depends(),
    service: UserService = Depends(get_user_service),
) -> Page[UserRead]:
    items, total = await service.list_page(limit=pagination.limit, offset=pagination.offset)
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_only)],
)
async def create_user(
    payload: UserCreate, service: UserService = Depends(get_user_service)
) -> UserRead:
    return await service.create(payload)


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(admin_only)])
async def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> UserRead:
    return await service.get(user_id)


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(admin_only)])
async def update_user(
    user_id: int, payload: UserUpdate, service: UserService = Depends(get_user_service)
) -> UserRead:
    return await service.update(user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_only)],
)
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)) -> None:
    await service.delete(user_id)

"""HTTP-роутер модуля organizations: публичная регистрация тенанта + настройки.

Регистрация — без аутентификации (создаёт организацию и первого ADMIN).
Настройки (`/me`) — только ADMIN своей организации; organization_id берётся из
текущего пользователя, не из тела запроса.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.core.rate_limit import register_rate_limit
from app.modules.auth.schemas import TokenPair
from app.modules.organizations.repository import OrganizationRepository
from app.modules.organizations.schemas import (
    OrganizationRead,
    OrganizationRegister,
    OrganizationUpdate,
)
from app.modules.organizations.service import OrganizationService
from app.modules.users.models import User
from app.shared.enums import UserRole

router = APIRouter(prefix="/organizations", tags=["organizations"])

admin_only = require_roles(UserRole.ADMIN)


def get_organization_service(
    db: AsyncSession = Depends(get_db, scope="function"),
) -> OrganizationService:
    return OrganizationService(OrganizationRepository(db))


@router.post(
    "/register",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(register_rate_limit)],
)
async def register(
    payload: OrganizationRegister,
    service: OrganizationService = Depends(get_organization_service),
) -> TokenPair:
    access, refresh = await service.register(payload)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=OrganizationRead)
async def get_my_organization(
    current_user: User = Depends(admin_only),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationRead:
    return await service.get(current_user.organization_id)


@router.patch("/me", response_model=OrganizationRead)
async def update_my_organization(
    payload: OrganizationUpdate,
    current_user: User = Depends(admin_only),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationRead:
    return await service.update(current_user.organization_id, payload)

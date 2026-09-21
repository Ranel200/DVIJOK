"""Protected API for the standalone creator/platform admin HTML."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_platform_owner
from app.modules.platform_admin.schemas import (
    PlatformAdminStateUpdate,
    PlatformServiceCreate,
    PlatformServiceUpdate,
)
from app.modules.platform_admin.service import PlatformAdminService
from app.modules.users.models import User

router = APIRouter(prefix="/platform-admin", tags=["platform-admin"])


def get_service(db: AsyncSession = Depends(get_db, scope="function")) -> PlatformAdminService:
    return PlatformAdminService(db)


@router.get("/bootstrap")
async def bootstrap(
    _: User = Depends(require_platform_owner),
    service: PlatformAdminService = Depends(get_service),
) -> dict:
    return await service.bootstrap()


@router.put("/state")
async def update_state(
    payload: PlatformAdminStateUpdate,
    _: User = Depends(require_platform_owner),
    service: PlatformAdminService = Depends(get_service),
) -> dict:
    return await service.update_state(payload)


@router.post("/services", status_code=status.HTTP_201_CREATED)
async def create_service(
    payload: PlatformServiceCreate,
    _: User = Depends(require_platform_owner),
    service: PlatformAdminService = Depends(get_service),
) -> dict:
    return await service.create_organization(payload)


@router.patch("/services/{service_id}")
async def update_service(
    service_id: str,
    payload: PlatformServiceUpdate,
    _: User = Depends(require_platform_owner),
    service: PlatformAdminService = Depends(get_service),
) -> dict:
    return await service.update_organization(service_id, payload)


@router.delete("/services/{service_id}")
async def deactivate_service(
    service_id: str,
    _: User = Depends(require_platform_owner),
    service: PlatformAdminService = Depends(get_service),
) -> dict:
    return await service.update_organization(service_id, PlatformServiceUpdate(is_active=False))

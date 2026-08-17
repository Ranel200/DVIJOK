"""Administrative settings API."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_owner
from app.modules.settings.schemas import SettingsRead, SettingsUpdate
from app.modules.settings.service import MAX_ORGANIZATION_LOGO_BYTES, SettingsService
from app.modules.users.models import User

router = APIRouter(prefix="/settings", tags=["settings"])


def get_settings_service(
    request: Request,
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(require_owner),
) -> SettingsService:
    return SettingsService(
        db,
        current_user,
        current_session_id=getattr(request.state, "staff_session_id", None),
    )


@router.get("", response_model=SettingsRead)
async def get_settings(
    service: SettingsService = Depends(get_settings_service),
) -> SettingsRead:
    return await service.read()


@router.put("", response_model=SettingsRead)
async def update_settings(
    payload: SettingsUpdate,
    service: SettingsService = Depends(get_settings_service),
) -> SettingsRead:
    return await service.update(payload)


@router.post("/logo", response_model=SettingsRead)
async def upload_organization_logo(
    file: Annotated[UploadFile, File()],
    service: SettingsService = Depends(get_settings_service),
) -> SettingsRead:
    return await service.upload_logo(
        filename=file.filename,
        content_type=file.content_type,
        content=await file.read(MAX_ORGANIZATION_LOGO_BYTES + 1),
    )

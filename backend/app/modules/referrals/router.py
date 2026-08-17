"""Административный API постоянной реферальной ссылки текущей организации."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_feature
from app.modules.referrals.repository import ReferralRepository
from app.modules.referrals.schemas import ReferralRead
from app.modules.referrals.service import ReferralService
from app.modules.users.models import User
from app.shared.enums import UserRole

router = APIRouter(prefix="/referrals", tags=["referrals"])
qr_access = require_feature("qr", UserRole.ADMIN, UserRole.MANAGER)


def get_referral_service(
    db: AsyncSession = Depends(get_db, scope="function"),
) -> ReferralService:
    return ReferralService(ReferralRepository(db))


@router.get("/me", response_model=ReferralRead)
async def get_my_referral(
    current_user: User = Depends(qr_access),
    service: ReferralService = Depends(get_referral_service),
) -> ReferralRead:
    return await service.get(current_user.organization_id)


@router.post("/me", response_model=ReferralRead, status_code=status.HTTP_201_CREATED)
async def create_my_referral(
    response: Response,
    current_user: User = Depends(qr_access),
    service: ReferralService = Depends(get_referral_service),
) -> ReferralRead:
    existing = await service.repo.get_by_organization(current_user.organization_id)
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        return service.present(existing)
    return await service.get_or_create(current_user.organization_id)


@router.get("/me/qr.svg", response_class=Response)
async def get_my_referral_qr(
    current_user: User = Depends(qr_access),
    service: ReferralService = Depends(get_referral_service),
) -> Response:
    referral = await service.get(current_user.organization_id)
    return Response(
        content=referral.qr_svg,
        media_type="image/svg+xml",
        headers={"Content-Disposition": 'inline; filename="referral-qr.svg"'},
    )


@router.get("/me/booking-qr.svg", response_class=Response)
async def get_my_public_booking_qr(
    current_user: User = Depends(qr_access),
    service: ReferralService = Depends(get_referral_service),
) -> Response:
    referral = await service.get(current_user.organization_id)
    return Response(
        content=referral.booking_qr_svg,
        media_type="image/svg+xml",
        headers={"Content-Disposition": 'inline; filename="public-booking-qr.svg"'},
    )

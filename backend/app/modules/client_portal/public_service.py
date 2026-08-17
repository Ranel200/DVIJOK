"""Публичная запись по постоянному непрозрачному коду организации."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client_portal.schemas import (
    BookingAvailabilityUiRead,
    BookingOptionsRead,
    BranchDirectoryRead,
    ClientBookingServiceId,
    PublicBookingCreate,
    PublicBookingRead,
    SpecialistDirectoryRead,
)
from app.modules.client_portal.service import ClientPortalService
from app.modules.referrals.repository import ReferralRepository
from app.modules.referrals.service import ReferralService


class PublicBookingService:
    """Разрешает код в tenant и делегирует доменную работу client_portal."""

    def __init__(self, session: AsyncSession) -> None:
        self.portal = ClientPortalService(session)
        self.referrals = ReferralService(ReferralRepository(session))

    async def _organization_id(self, code: str) -> int:
        return await self.referrals.resolve_public_booking_organization(code)

    async def context(self, code: str) -> BranchDirectoryRead:
        organization_id = await self._organization_id(code)
        return await self.portal.frontend_public_branch(organization_id, code)

    async def options(self, code: str) -> BookingOptionsRead:
        organization_id = await self._organization_id(code)
        return await self.portal.frontend_booking_options(None, organization_id)

    async def specialists(self, code: str) -> SpecialistDirectoryRead:
        organization_id = await self._organization_id(code)
        return await self.portal.frontend_specialists(organization_id)

    async def availability(
        self,
        *,
        code: str,
        year: int,
        month: int,
        service_id: ClientBookingServiceId | None,
        specialist_id: int | str,
    ) -> BookingAvailabilityUiRead:
        organization_id = await self._organization_id(code)
        return await self.portal.frontend_booking_availability(
            organization_id=organization_id,
            year=year,
            month=month,
            service_id=service_id,
            master_id=specialist_id,
        )

    async def create(self, code: str, payload: PublicBookingCreate) -> PublicBookingRead:
        organization_id = await self._organization_id(code)
        return await self.portal.create_public_booking(organization_id, payload)

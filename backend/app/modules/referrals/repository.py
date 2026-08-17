"""Доступ к постоянным реферальным кодам организаций."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.referrals.models import OrganizationReferral


class ReferralRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_organization(self, organization_id: int) -> OrganizationReferral | None:
        result = await self.session.execute(
            select(OrganizationReferral).where(
                OrganizationReferral.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> OrganizationReferral | None:
        result = await self.session.execute(
            select(OrganizationReferral).where(OrganizationReferral.code == code)
        )
        return result.scalar_one_or_none()

    async def add(self, referral: OrganizationReferral) -> OrganizationReferral:
        self.session.add(referral)
        await self.session.flush()
        await self.session.refresh(referral)
        return referral

"""Репозиторий модуля organizations.

Organization — сам тенант, а не сущность внутри тенанта, поэтому здесь не
используется BaseRepository (он скоупит запросы по organization_id).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organizations.models import Organization


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, organization_id: int) -> Organization | None:
        return await self.session.get(Organization, organization_id)

    async def get_by_inn(self, inn: str) -> Organization | None:
        result = await self.session.execute(select(Organization).where(Organization.inn == inn))
        return result.scalar_one_or_none()

    async def add(self, organization: Organization) -> Organization:
        self.session.add(organization)
        await self.session.flush()
        await self.session.refresh(organization)
        return organization

    async def update(self, organization: Organization) -> Organization:
        await self.session.flush()
        await self.session.refresh(organization)
        return organization

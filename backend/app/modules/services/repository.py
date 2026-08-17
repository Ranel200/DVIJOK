"""Репозиторий модуля services."""

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from app.modules.mechanics.models import Mechanic
from app.modules.services.models import Service
from app.shared.base_repository import BaseRepository
from app.shared.enums import ServiceCategory


class ServiceRepository(BaseRepository[Service]):
    model = Service

    async def get(self, id_: int) -> Service | None:
        stmt = (
            select(Service)
            .options(selectinload(Service.mechanics).selectinload(Mechanic.user))
            .where(Service.id == id_, Service.organization_id == self.organization_id)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_public_booking(self, keys: tuple[str, ...]) -> list[Service]:
        stmt = (
            select(Service)
            .options(selectinload(Service.mechanics).selectinload(Mechanic.user))
            .where(
                Service.organization_id == self.organization_id,
                Service.public_booking_key.in_(keys),
                Service.is_active.is_(True),
            )
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def search(
        self,
        *,
        query: str | None = None,
        category: ServiceCategory | None = None,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Service], int]:
        # Coarse client booking choices are system records and must not appear
        # in the detailed staff/admin price list.
        conditions = [
            Service.organization_id == self.organization_id,
            Service.public_booking_key.is_(None),
        ]
        if category is not None:
            conditions.append(Service.category == category)
        if active_only:
            conditions.append(Service.is_active.is_(True))
        if query:
            conditions.append(Service.name.ilike(f"%{query}%"))

        base = select(Service).options(selectinload(Service.mechanics).selectinload(Mechanic.user))
        if conditions:
            base = base.where(and_(*conditions))

        total = int(
            (
                await self.session.execute(select(func.count()).select_from(base.subquery()))
            ).scalar_one()
        )
        items = list(
            (await self.session.execute(base.order_by(Service.name).limit(limit).offset(offset)))
            .scalars()
            .all()
        )
        return items, total

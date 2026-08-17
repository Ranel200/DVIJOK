"""Репозиторий модуля client_portal.

Без organization_id-скоупинга (в отличие от BaseRepository) — обслуживает
глобальный кабинет клиента: агрегация по всем организациям, где у клиента есть
CRM-карточка, связанная через Client.client_account_id.
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.clients.models import Client
from app.modules.orders.models import Order
from app.modules.organizations.models import Organization
from app.modules.vehicles.models import Vehicle
from app.shared.enums import OrganizationStatus


class ClientPortalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_active_organizations(self) -> list[Organization]:
        stmt = (
            select(Organization)
            .where(
                Organization.is_active.is_(True),
                Organization.status != OrganizationStatus.SUSPENDED,
            )
            .order_by(Organization.name)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_organization(self, organization_id: int) -> Organization | None:
        """Только активные/не приостановленные — для discovery и бронирования."""
        stmt = select(Organization).where(
            Organization.id == organization_id,
            Organization.is_active.is_(True),
            Organization.status != OrganizationStatus.SUSPENDED,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def lock_organization(self, organization_id: int) -> Organization | None:
        """Сериализует первичное создание CRM-клиента внутри организации."""

        stmt = (
            select(Organization)
            .where(
                Organization.id == organization_id,
                Organization.is_active.is_(True),
                Organization.status != OrganizationStatus.SUSPENDED,
            )
            .with_for_update()
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_organization_any(self, organization_id: int) -> Organization | None:
        """Без фильтра активности — для показа шапки исторической накладной."""
        return await self.session.get(Organization, organization_id)

    async def list_vehicles_by_account(self, client_account_id: int) -> list[Vehicle]:
        # Осознанно кросс-тенантный запрос: клиент видит свои авто across всех
        # автосервисов, где заводил CRM-карточку (связка по client_account_id,
        # не по organization_id) — единственное такое место в проекте.
        stmt = (
            select(Vehicle)
            .join(Client, Client.id == Vehicle.client_id)
            .where(Client.client_account_id == client_account_id)
            .order_by(Vehicle.id.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_vehicle_owned_by_account(
        self, vehicle_id: int, client_account_id: int
    ) -> Vehicle | None:
        stmt = (
            select(Vehicle)
            .join(Client, Client.id == Vehicle.client_id)
            .where(
                Vehicle.id == vehicle_id,
                Client.client_account_id == client_account_id,
            )
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def organization_last_visits(
        self, client_account_id: int
    ) -> dict[int, datetime]:
        stmt = (
            select(Order.organization_id, func.max(Order.created_at))
            .join(Client, Client.id == Order.client_id)
            .where(Client.client_account_id == client_account_id)
            .group_by(Order.organization_id)
        )
        result = await self.session.execute(stmt)
        visits: dict[int, datetime] = {}
        for organization_id, value in result.tuples():
            visits[organization_id] = value
        return visits

    async def list_orders_by_account(
        self, client_account_id: int, *, limit: int, offset: int
    ) -> tuple[list[Order], int]:
        base = (
            select(Order)
            .join(Client, Client.id == Order.client_id)
            .where(Client.client_account_id == client_account_id)
        )
        total = int(
            (
                await self.session.execute(select(func.count()).select_from(base.subquery()))
            ).scalar_one()
        )
        stmt = (
            base.options(
                selectinload(Order.client),
                selectinload(Order.vehicle),
                selectinload(Order.mechanic),
                selectinload(Order.items),
                selectinload(Order.documents),
            )
            .order_by(Order.id.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def get_order_owned_by_account(
        self, order_id: int, client_account_id: int
    ) -> Order | None:
        stmt = (
            select(Order)
            .join(Client, Client.id == Order.client_id)
            .options(
                selectinload(Order.vehicle),
                selectinload(Order.client),
                selectinload(Order.mechanic),
                selectinload(Order.items),
                selectinload(Order.documents),
            )
            .where(Order.id == order_id, Client.client_account_id == client_account_id)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

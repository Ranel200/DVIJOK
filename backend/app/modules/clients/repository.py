"""Репозиторий модуля clients: поиск по имени/телефону/авто и агрегаты по заказам."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import selectinload

from app.modules.clients.models import Client
from app.modules.orders.models import Order
from app.modules.vehicles.models import Vehicle
from app.shared.base_repository import BaseRepository
from app.shared.enums import ClientType, OrderStatus


class ClientRepository(BaseRepository[Client]):
    model = Client

    async def get_by_phone(self, phone: str) -> Client | None:
        result = await self.session.execute(
            select(Client).where(
                Client.phone == phone, Client.organization_id == self.organization_id
            )
        )
        return result.scalar_one_or_none()

    async def lock(self, client_id: int) -> Client | None:
        """Сериализует конкурирующие клиентские записи одного владельца."""

        stmt = (
            select(Client)
            .where(
                Client.id == client_id,
                Client.organization_id == self.organization_id,
            )
            .with_for_update()
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_with_vehicles(self, client_id: int) -> Client | None:
        stmt = (
            select(Client)
            .options(selectinload(Client.vehicles))
            .where(Client.id == client_id, Client.organization_id == self.organization_id)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def search(
        self,
        *,
        query: str | None = None,
        client_type: ClientType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Client], int]:
        conditions = [Client.organization_id == self.organization_id]
        if client_type is not None:
            conditions.append(Client.client_type == client_type)
        if query:
            like = f"%{query}%"
            conditions.append(
                or_(
                    Client.full_name.ilike(like),
                    Client.phone.ilike(like),
                    Vehicle.make.ilike(like),
                    Vehicle.model.ilike(like),
                    Vehicle.license_plate.ilike(like),
                )
            )

        stmt = select(Client)
        count_stmt = select(func.count(func.distinct(Client.id))).select_from(Client)
        if query:
            stmt = stmt.outerjoin(Vehicle, Vehicle.client_id == Client.id)
            count_stmt = count_stmt.outerjoin(Vehicle, Vehicle.client_id == Client.id)
        if conditions:
            where = and_(*conditions)
            stmt = stmt.where(where)
            count_stmt = count_stmt.where(where)

        stmt = stmt.distinct().order_by(Client.id.desc()).limit(limit).offset(offset)
        total = int((await self.session.execute(count_stmt)).scalar_one())
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def stats(self, client_id: int) -> tuple[int, Decimal, datetime | None]:
        """Кол-во визитов, сумма по завершённым заказам, дата последнего визита."""
        stmt = select(
            func.count(Order.id),
            func.coalesce(
                func.sum(case((Order.status == OrderStatus.DONE, Order.total_amount), else_=0)),
                0,
            ),
            func.max(func.coalesce(Order.completed_at, Order.created_at)),
        ).where(Order.client_id == client_id, Order.organization_id == self.organization_id)
        row = (await self.session.execute(stmt)).one()
        return int(row[0]), Decimal(row[1] or 0), row[2]

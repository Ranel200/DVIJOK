"""Репозиторий модуля orders."""

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload

from app.modules.clients.models import Client
from app.modules.mechanics.models import Mechanic
from app.modules.orders.models import Order, OrderItem
from app.modules.vehicles.models import Vehicle
from app.shared.base_repository import BaseRepository
from app.shared.enums import OrderSource, OrderStatus


class OrderRepository(BaseRepository[Order]):
    model = Order

    async def get_with_relations(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.service),
                selectinload(Order.items)
                .selectinload(OrderItem.mechanic)
                .selectinload(Mechanic.user),
                selectinload(Order.documents),
                selectinload(Order.client),
                selectinload(Order.vehicle),
                selectinload(Order.mechanic),
            )
            .where(Order.id == order_id, Order.organization_id == self.organization_id)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_reschedulable_client_order_for_update(
        self,
        *,
        client_id: int,
        vehicle_id: int,
    ) -> Order | None:
        """Возвращает последнюю ещё не принятую в работу клиентскую запись."""

        stmt = (
            select(Order)
            .where(
                Order.organization_id == self.organization_id,
                Order.client_id == client_id,
                Order.vehicle_id == vehicle_id,
                Order.created_by_id.is_(None),
                Order.status == OrderStatus.NEW,
            )
            .order_by(Order.id.desc())
            .limit(1)
            .with_for_update()
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def search(
        self,
        *,
        status: OrderStatus | None = None,
        source: OrderSource | None = None,
        mechanic_id: int | None = None,
        query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Order], int]:
        conditions = [Order.organization_id == self.organization_id]
        if status is not None:
            conditions.append(Order.status == status)
        if source is not None:
            conditions.append(Order.source == source)
        if mechanic_id is not None:
            conditions.append(Order.mechanic_id == mechanic_id)
        if query:
            like = f"%{query}%"
            conditions.append(
                or_(
                    Order.number.ilike(like),
                    Client.full_name.ilike(like),
                    Vehicle.make.ilike(like),
                    Vehicle.model.ilike(like),
                    Vehicle.license_plate.ilike(like),
                )
            )

        stmt = select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.service),
            selectinload(Order.items).selectinload(OrderItem.mechanic).selectinload(Mechanic.user),
            selectinload(Order.documents),
            selectinload(Order.client),
            selectinload(Order.vehicle),
            selectinload(Order.mechanic),
        )
        count_stmt = select(func.count(func.distinct(Order.id))).select_from(Order)
        if query:
            stmt = stmt.join(Client, Client.id == Order.client_id).join(
                Vehicle, Vehicle.id == Order.vehicle_id
            )
            count_stmt = count_stmt.join(Client, Client.id == Order.client_id).join(
                Vehicle, Vehicle.id == Order.vehicle_id
            )
        if conditions:
            where = and_(*conditions)
            stmt = stmt.where(where)
            count_stmt = count_stmt.where(where)

        stmt = stmt.order_by(Order.id.desc()).limit(limit).offset(offset)
        total = int((await self.session.execute(count_stmt)).scalar_one())
        items = list((await self.session.execute(stmt)).scalars().unique().all())
        return items, total

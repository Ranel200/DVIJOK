"""Репозиторий модуля schedule (слоты + блокировки мастеров), скоупленный по организации."""

from datetime import datetime

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.mechanics.models import Mechanic
from app.modules.orders.models import Order, OrderItem
from app.modules.schedule.models import MechanicBlock, MechanicWorkingHours, ScheduleSlot


class ScheduleRepository:
    """Кастомный репозиторий: обслуживает две связанные модели расписания."""

    def __init__(self, session: AsyncSession, organization_id: int) -> None:
        self.session = session
        self.organization_id = organization_id

    # ── Слоты ──────────────────────────────────────────────
    async def get_slot(self, slot_id: int) -> ScheduleSlot | None:
        stmt = (
            select(ScheduleSlot)
            .options(
                selectinload(ScheduleSlot.mechanic),
                selectinload(ScheduleSlot.order).selectinload(Order.client),
                selectinload(ScheduleSlot.order).selectinload(Order.vehicle),
                selectinload(ScheduleSlot.order)
                .selectinload(Order.items)
                .selectinload(OrderItem.service),
            )
            .where(
                ScheduleSlot.id == slot_id,
                ScheduleSlot.organization_id == self.organization_id,
            )
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_slot_by_order(self, order_id: int) -> ScheduleSlot | None:
        stmt = select(ScheduleSlot).where(
            ScheduleSlot.organization_id == self.organization_id,
            ScheduleSlot.order_id == order_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_slot(self, slot: ScheduleSlot) -> ScheduleSlot:
        slot.organization_id = self.organization_id
        self.session.add(slot)
        await self.session.flush()
        await self.session.refresh(slot)
        return slot

    async def lock_mechanic(self, mechanic_id: int) -> Mechanic | None:
        """Сериализует check+insert для одного мастера в PostgreSQL."""
        stmt = (
            select(Mechanic)
            .where(
                Mechanic.id == mechanic_id,
                Mechanic.organization_id == self.organization_id,
            )
            .with_for_update()
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def delete_slot(self, slot: ScheduleSlot) -> None:
        await self.session.delete(slot)
        await self.session.flush()

    async def overlapping_slots(
        self, mechanic_id: int, start: datetime, end: datetime, exclude_id: int | None = None
    ) -> list[ScheduleSlot]:
        # Пересечение интервалов: start < existing.end AND end > existing.start.
        stmt = select(ScheduleSlot).where(
            and_(
                ScheduleSlot.organization_id == self.organization_id,
                ScheduleSlot.mechanic_id == mechanic_id,
                ScheduleSlot.start_time < end,
                ScheduleSlot.end_time > start,
            )
        )
        if exclude_id is not None:
            stmt = stmt.where(ScheduleSlot.id != exclude_id)
        return list((await self.session.execute(stmt)).scalars().all())

    async def slots_in_range(
        self, start: datetime, end: datetime, mechanic_id: int | None = None
    ) -> list[ScheduleSlot]:
        stmt = (
            select(ScheduleSlot)
            .options(
                selectinload(ScheduleSlot.mechanic),
                selectinload(ScheduleSlot.order).selectinload(Order.client),
                selectinload(ScheduleSlot.order).selectinload(Order.vehicle),
                selectinload(ScheduleSlot.order)
                .selectinload(Order.items)
                .selectinload(OrderItem.service),
            )
            .where(
                and_(
                    ScheduleSlot.organization_id == self.organization_id,
                    ScheduleSlot.start_time < end,
                    ScheduleSlot.end_time > start,
                )
            )
        )
        if mechanic_id is not None:
            stmt = stmt.where(ScheduleSlot.mechanic_id == mechanic_id)
        return list(
            (await self.session.execute(stmt.order_by(ScheduleSlot.start_time))).scalars().all()
        )

    # ── Блокировки ─────────────────────────────────────────
    async def get_block(self, block_id: int) -> MechanicBlock | None:
        stmt = select(MechanicBlock).where(
            MechanicBlock.id == block_id, MechanicBlock.organization_id == self.organization_id
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_block(self, block: MechanicBlock) -> MechanicBlock:
        block.organization_id = self.organization_id
        self.session.add(block)
        await self.session.flush()
        await self.session.refresh(block)
        return block

    async def delete_block(self, block: MechanicBlock) -> None:
        await self.session.delete(block)
        await self.session.flush()

    async def overlapping_blocks(
        self, mechanic_id: int, start: datetime, end: datetime
    ) -> list[MechanicBlock]:
        stmt = select(MechanicBlock).where(
            and_(
                MechanicBlock.organization_id == self.organization_id,
                MechanicBlock.mechanic_id == mechanic_id,
                MechanicBlock.start_time < end,
                MechanicBlock.end_time > start,
            )
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def blocks_in_range(
        self, start: datetime, end: datetime, mechanic_id: int | None = None
    ) -> list[MechanicBlock]:
        stmt = select(MechanicBlock).where(
            and_(
                MechanicBlock.organization_id == self.organization_id,
                MechanicBlock.start_time < end,
                MechanicBlock.end_time > start,
            )
        )
        if mechanic_id is not None:
            stmt = stmt.where(MechanicBlock.mechanic_id == mechanic_id)
        return list(
            (await self.session.execute(stmt.order_by(MechanicBlock.start_time))).scalars().all()
        )

    async def working_hours(self, mechanic_id: int) -> list[MechanicWorkingHours]:
        stmt = (
            select(MechanicWorkingHours)
            .where(
                MechanicWorkingHours.organization_id == self.organization_id,
                MechanicWorkingHours.mechanic_id == mechanic_id,
            )
            .order_by(
                MechanicWorkingHours.weekday,
                MechanicWorkingHours.start_time,
            )
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def replace_working_hours(
        self,
        mechanic_id: int,
        intervals: list[MechanicWorkingHours],
    ) -> list[MechanicWorkingHours]:
        await self.session.execute(
            delete(MechanicWorkingHours).where(
                MechanicWorkingHours.organization_id == self.organization_id,
                MechanicWorkingHours.mechanic_id == mechanic_id,
            )
        )
        for interval in intervals:
            interval.organization_id = self.organization_id
            interval.mechanic_id = mechanic_id
            self.session.add(interval)
        await self.session.flush()
        return await self.working_hours(mechanic_id)

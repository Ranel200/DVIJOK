"""Бизнес-логика модуля schedule: проверка пересечений и недельный вид."""

import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import BusinessRuleError, ForbiddenError, NotFoundError
from app.modules.mechanics.models import Mechanic
from app.modules.orders.models import Order
from app.modules.schedule.models import MechanicBlock, MechanicWorkingHours, ScheduleSlot
from app.modules.schedule.repository import ScheduleRepository
from app.modules.schedule.schemas import (
    AvailabilitySuggestions,
    AvailableSlot,
    BlockCreate,
    CalendarBlock,
    CalendarDay,
    CalendarView,
    SlotCreate,
    SlotUpdate,
    WorkingHoursInterval,
    WorkingHoursRead,
)
from app.modules.services.models import Service
from app.modules.users.models import User
from app.shared.enums import UserRole

_DEFAULT_WORKING_HOURS = [
    WorkingHoursInterval(
        weekday=weekday,
        start_time=dt.time(9, 0),
        end_time=dt.time(18, 0),
    )
    for weekday in range(5)
]

_CALENDAR_COLORS = (
    "#43A047",
    "#EC407A",
    "#5C6BC0",
    "#039BE5",
    "#8E24AA",
    "#00897B",
    "#F4511E",
)


class ScheduleService:
    def __init__(self, repo: ScheduleRepository, current_user: User | None = None) -> None:
        self.repo = repo
        self.session = repo.session
        self.organization_id = repo.organization_id
        self.current_user = current_user

    async def _visible_mechanic_id(self, requested_id: int | None) -> int | None:
        """Scope schedule reads to the signed-in master's own mechanic profile.

        Internal booking flows instantiate the service without ``current_user``
        and therefore retain their existing organization-wide behaviour.
        """
        if (
            self.current_user is None
            or self.current_user.is_owner
            or self.current_user.role != UserRole.MECHANIC
        ):
            return requested_id

        own_mechanic_id = (
            await self.session.execute(
                select(Mechanic.id).where(
                    Mechanic.organization_id == self.organization_id,
                    Mechanic.user_id == self.current_user.id,
                    Mechanic.is_active.is_(True),
                )
            )
        ).scalar_one_or_none()
        if requested_id is not None and requested_id != own_mechanic_id:
            raise ForbiddenError("Мастер может просматривать только своё расписание")
        # Primary keys are positive. Zero intentionally produces an empty view
        # for a legacy master account that has no linked mechanic profile.
        return own_mechanic_id or 0

    async def _ensure_mechanic(self, mechanic_id: int, *, lock: bool = False) -> Mechanic:
        if lock:
            mechanic = await self.repo.lock_mechanic(mechanic_id)
            if mechanic is None:
                raise NotFoundError("Мастер не найден")
            return mechanic
        stmt = select(Mechanic).where(
            Mechanic.id == mechanic_id, Mechanic.organization_id == self.organization_id
        )
        mechanic = (await self.session.execute(stmt)).scalar_one_or_none()
        if mechanic is None:
            raise NotFoundError("Мастер не найден")
        return mechanic

    async def _ensure_order(self, order_id: int | None) -> None:
        if order_id is None:
            return
        stmt = select(Order).where(
            Order.id == order_id, Order.organization_id == self.organization_id
        )
        if (await self.session.execute(stmt)).scalar_one_or_none() is None:
            raise NotFoundError("Заказ не найден")

    async def _ensure_free(
        self,
        mechanic_id: int,
        start: dt.datetime,
        end: dt.datetime,
        exclude_slot_id: int | None = None,
    ) -> None:
        if await self.repo.overlapping_slots(mechanic_id, start, end, exclude_slot_id):
            raise BusinessRuleError("Пересечение с другой записью мастера")
        if await self.repo.overlapping_blocks(mechanic_id, start, end):
            raise BusinessRuleError("Мастер заблокирован на это время (болезнь/отпуск)")

    @staticmethod
    def _overlaps_recurring_break(
        mechanic: Mechanic,
        start: dt.datetime,
        end: dt.datetime,
        timezone: ZoneInfo,
    ) -> bool:
        local_start = start.astimezone(timezone)
        local_end = end.astimezone(timezone)
        if local_start.date() != local_end.date():
            return False
        for item in mechanic.schedule_breaks or []:
            try:
                break_start = dt.time.fromisoformat(item["start"])
                break_end = dt.time.fromisoformat(item["end"])
            except (KeyError, TypeError, ValueError):
                continue
            if (
                local_start.timetz().replace(tzinfo=None) < break_end
                and local_end.timetz().replace(tzinfo=None) > break_start
            ):
                return True
        return False

    @staticmethod
    def _require_aware(value: dt.datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise BusinessRuleError("Дата и время должны содержать часовой пояс")

    async def working_hours(self, mechanic_id: int) -> WorkingHoursRead:
        mechanic_id = await self._visible_mechanic_id(mechanic_id) or mechanic_id
        mechanic = await self._ensure_mechanic(mechanic_id)
        stored = await self.repo.working_hours(mechanic_id)
        intervals = [
            WorkingHoursInterval(
                weekday=item.weekday,
                start_time=item.start_time,
                end_time=item.end_time,
            )
            for item in stored
        ]
        return WorkingHoursRead(
            mechanic_id=mechanic_id,
            timezone=settings.SCHEDULE_TIMEZONE,
            uses_default=not mechanic.schedule_configured,
            intervals=intervals if mechanic.schedule_configured else _DEFAULT_WORKING_HOURS,
        )

    async def replace_working_hours(
        self,
        mechanic_id: int,
        intervals: list[WorkingHoursInterval],
    ) -> WorkingHoursRead:
        mechanic = await self._ensure_mechanic(mechanic_id, lock=True)
        ordered = sorted(intervals, key=lambda item: (item.weekday, item.start_time))
        for previous, current in zip(ordered, ordered[1:], strict=False):
            if previous.weekday == current.weekday and current.start_time < previous.end_time:
                raise BusinessRuleError("Рабочие интервалы мастера пересекаются")
        stored = await self.repo.replace_working_hours(
            mechanic_id,
            [
                MechanicWorkingHours(
                    weekday=item.weekday,
                    start_time=item.start_time,
                    end_time=item.end_time,
                )
                for item in ordered
            ],
        )
        mechanic.schedule_configured = True
        await self.session.flush()
        return WorkingHoursRead(
            mechanic_id=mechanic_id,
            timezone=settings.SCHEDULE_TIMEZONE,
            uses_default=False,
            intervals=[
                WorkingHoursInterval(
                    weekday=item.weekday,
                    start_time=item.start_time,
                    end_time=item.end_time,
                )
                for item in stored
            ],
        )

    async def _ensure_within_working_hours(
        self,
        mechanic_id: int,
        start: dt.datetime,
        end: dt.datetime,
    ) -> None:
        self._require_aware(start)
        self._require_aware(end)
        mechanic = await self._ensure_mechanic(mechanic_id)
        # Legacy compatibility: until an explicit schedule is saved, existing
        # booking clients may still reserve arbitrary aware times. Availability
        # suggestions nevertheless use the visible Mon–Fri default.
        if not mechanic.schedule_configured:
            return
        timezone = ZoneInfo(settings.SCHEDULE_TIMEZONE)
        local_start = start.astimezone(timezone)
        local_end = end.astimezone(timezone)
        if local_start.date() != local_end.date():
            raise BusinessRuleError("Запись должна укладываться в один рабочий день")
        schedule = await self.working_hours(mechanic_id)
        fits = any(
            interval.weekday == local_start.weekday()
            and interval.start_time <= local_start.timetz().replace(tzinfo=None)
            and interval.end_time >= local_end.timetz().replace(tzinfo=None)
            for interval in schedule.intervals
        )
        if not fits:
            raise BusinessRuleError("Выбранное время вне рабочего графика мастера")
        if self._overlaps_recurring_break(mechanic, start, end, timezone):
            raise BusinessRuleError("Выбранное время пересекается с перерывом мастера")

    async def reserve(
        self,
        *,
        mechanic_id: int,
        start_time: dt.datetime,
        duration_minutes: int,
        order_id: int,
        title: str | None = None,
    ) -> ScheduleSlot:
        """Атомарный explicit reservation выбранного frontend слота."""
        await self._ensure_mechanic(mechanic_id, lock=True)
        await self._ensure_order(order_id)
        end_time = start_time + dt.timedelta(minutes=duration_minutes)
        await self._ensure_within_working_hours(mechanic_id, start_time, end_time)
        await self._ensure_free(mechanic_id, start_time, end_time)
        return await self.repo.add_slot(
            ScheduleSlot(
                mechanic_id=mechanic_id,
                order_id=order_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
            )
        )

    async def suggestions(
        self,
        *,
        date_from: dt.date,
        date_to: dt.date,
        mechanic_id: int | None,
        service_id: int | None,
        duration_minutes: int | None,
        exclude_slot_id: int | None = None,
    ) -> AvailabilitySuggestions:
        requested_mechanic_id = mechanic_id
        mechanic_id = await self._visible_mechanic_id(mechanic_id)
        if date_to < date_from or (date_to - date_from).days > 31:
            raise BusinessRuleError("Диапазон availability должен быть от 1 до 31 дня")
        service: Service | None = None
        if service_id is not None:
            service = (
                await self.session.execute(
                    select(Service).where(
                        Service.id == service_id,
                        Service.organization_id == self.organization_id,
                        Service.is_active.is_(True),
                    )
                )
            ).scalar_one_or_none()
            if service is None:
                raise NotFoundError("Услуга не найдена")
        duration = (
            service.duration_minutes
            if service is not None
            else duration_minutes or settings.DEFAULT_APPOINTMENT_DURATION_MINUTES
        )
        if duration < 1 or duration > 1440:
            raise BusinessRuleError("Некорректная длительность записи")

        mechanics_stmt = select(Mechanic).where(
            Mechanic.organization_id == self.organization_id,
            Mechanic.is_active.is_(True),
        )
        if mechanic_id is not None:
            mechanics_stmt = mechanics_stmt.where(Mechanic.id == mechanic_id)
        mechanics = list((await self.session.execute(mechanics_stmt)).scalars().all())
        if requested_mechanic_id is not None and not mechanics:
            raise NotFoundError("Мастер не найден")
        if service is not None:
            mechanics = [
                mechanic
                for mechanic in mechanics
                if not mechanic.specializations
                or service.category.value in mechanic.specializations
            ]

        timezone = ZoneInfo(settings.SCHEDULE_TIMEZONE)
        now = dt.datetime.now(dt.UTC)
        result: list[AvailableSlot] = []
        day = date_from
        while day <= date_to:
            for mechanic in mechanics:
                schedule = await self.working_hours(mechanic.id)
                for interval in schedule.intervals:
                    if interval.weekday != day.weekday():
                        continue
                    cursor = dt.datetime.combine(day, interval.start_time, timezone)
                    boundary = dt.datetime.combine(day, interval.end_time, timezone)
                    while cursor + dt.timedelta(minutes=duration) <= boundary:
                        end = cursor + dt.timedelta(minutes=duration)
                        if cursor.astimezone(dt.UTC) >= now:
                            if (
                                not self._overlaps_recurring_break(mechanic, cursor, end, timezone)
                                and not await self.repo.overlapping_slots(
                                    mechanic.id,
                                    cursor,
                                    end,
                                    exclude_slot_id,
                                )
                                and not await self.repo.overlapping_blocks(mechanic.id, cursor, end)
                            ):
                                result.append(
                                    AvailableSlot(
                                        mechanic_id=mechanic.id,
                                        start_time=cursor,
                                        end_time=end,
                                        duration_minutes=duration,
                                    )
                                )
                        cursor += dt.timedelta(minutes=settings.SCHEDULE_SLOT_STEP_MINUTES)
            day += dt.timedelta(days=1)
        result.sort(key=lambda item: (item.start_time, item.mechanic_id))
        return AvailabilitySuggestions(
            date_from=date_from,
            date_to=date_to,
            timezone=settings.SCHEDULE_TIMEZONE,
            duration_minutes=duration,
            slots=result,
        )

    # ── Слоты ──────────────────────────────────────────────
    async def get_slot(self, slot_id: int) -> ScheduleSlot:
        slot = await self.repo.get_slot(slot_id)
        if slot is None:
            raise NotFoundError("Запись расписания не найдена")
        return slot

    async def create_slot(self, data: SlotCreate) -> ScheduleSlot:
        await self._ensure_mechanic(data.mechanic_id, lock=True)
        await self._ensure_order(data.order_id)
        await self._ensure_within_working_hours(data.mechanic_id, data.start_time, data.end_time)
        await self._ensure_free(data.mechanic_id, data.start_time, data.end_time)
        return await self.repo.add_slot(
            ScheduleSlot(
                mechanic_id=data.mechanic_id,
                order_id=data.order_id,
                work_type=data.work_type,
                title=data.title,
                start_time=data.start_time,
                end_time=data.end_time,
            )
        )

    async def update_slot(self, slot_id: int, data: SlotUpdate) -> ScheduleSlot:
        slot = await self.get_slot(slot_id)
        payload = data.model_dump(exclude_unset=True)
        new_mechanic = payload.get("mechanic_id", slot.mechanic_id)
        new_start = payload.get("start_time", slot.start_time)
        new_end = payload.get("end_time", slot.end_time)
        if new_end <= new_start:
            raise BusinessRuleError("end_time должно быть позже start_time")
        if "order_id" in payload:
            await self._ensure_order(payload["order_id"])
        await self._ensure_mechanic(new_mechanic, lock=True)
        await self._ensure_free(new_mechanic, new_start, new_end, exclude_slot_id=slot_id)
        for field, value in payload.items():
            setattr(slot, field, value)
        await self.session.flush()
        return slot

    async def delete_slot(self, slot_id: int) -> None:
        await self.repo.delete_slot(await self.get_slot(slot_id))

    # ── Блокировки ─────────────────────────────────────────
    async def create_block(self, data: BlockCreate) -> MechanicBlock:
        await self._ensure_mechanic(data.mechanic_id)
        return await self.repo.add_block(
            MechanicBlock(
                mechanic_id=data.mechanic_id,
                reason=data.reason,
                start_time=data.start_time,
                end_time=data.end_time,
            )
        )

    async def delete_block(self, block_id: int) -> None:
        block = await self.repo.get_block(block_id)
        if block is None:
            raise NotFoundError("Блокировка не найдена")
        await self.repo.delete_block(block)

    # ── Недельный вид ──────────────────────────────────────
    @staticmethod
    def week_bounds(day: dt.date) -> tuple[dt.datetime, dt.datetime]:
        monday = day - dt.timedelta(days=day.weekday())
        start = dt.datetime.combine(monday, dt.time.min, tzinfo=dt.UTC)
        return start, start + dt.timedelta(days=7)

    async def week(
        self, day: dt.date, mechanic_id: int | None = None
    ) -> tuple[dt.datetime, dt.datetime, list[ScheduleSlot], list[MechanicBlock]]:
        mechanic_id = await self._visible_mechanic_id(mechanic_id)
        start, end = self.week_bounds(day)
        slots = await self.repo.slots_in_range(start, end, mechanic_id)
        blocks = await self.repo.blocks_in_range(start, end, mechanic_id)
        return start, end, slots, blocks

    async def calendar(self, week_start: dt.date) -> CalendarView:
        """UI-проекция недели: доступность и занятые карточки по часам."""
        mechanic_id = await self._visible_mechanic_id(None)
        monday = week_start - dt.timedelta(days=week_start.weekday())
        timezone = ZoneInfo(settings.SCHEDULE_TIMEZONE)
        range_start = dt.datetime.combine(monday, dt.time.min, timezone)
        range_end = range_start + dt.timedelta(days=7)
        slots = await self.repo.slots_in_range(range_start, range_end, mechanic_id)
        blocks = await self.repo.blocks_in_range(range_start, range_end, mechanic_id)
        mechanic_conditions = [
            Mechanic.organization_id == self.organization_id,
            Mechanic.is_active.is_(True),
        ]
        if mechanic_id is not None:
            mechanic_conditions.append(Mechanic.id == mechanic_id)
        mechanics = list(
            (
                await self.session.execute(
                    select(Mechanic)
                    .options(selectinload(Mechanic.user))
                    .where(*mechanic_conditions)
                    .order_by(Mechanic.full_name)
                )
            )
            .scalars()
            .all()
        )

        schedules = {mechanic.id: await self.working_hours(mechanic.id) for mechanic in mechanics}
        starts = [
            item.start_time.hour for schedule in schedules.values() for item in schedule.intervals
        ]
        ends = [
            item.end_time.hour + (1 if item.end_time.minute else 0)
            for schedule in schedules.values()
            for item in schedule.intervals
        ]
        min_hour = min(starts, default=9)
        max_hour = max(ends, default=18)
        times = [f"{hour:02d}:00" for hour in range(min_hour, max_hour)]

        days: list[CalendarDay] = []

        def local_time(value: dt.datetime) -> dt.datetime:
            # SQLite в unit-тестах теряет tzinfo; PostgreSQL возвращает aware datetime.
            return (
                value.replace(tzinfo=timezone)
                if value.tzinfo is None
                else value.astimezone(timezone)
            )

        for offset in range(7):
            day = monday + dt.timedelta(days=offset)
            by_time: dict[str, list[CalendarBlock]] = {time: [] for time in times}
            for time_label in times:
                hour = int(time_label[:2])
                cell_start = dt.datetime.combine(day, dt.time(hour), timezone)
                cell_end = cell_start + dt.timedelta(hours=1)
                for mechanic in mechanics:
                    color = (
                        mechanic.user.calendar_color
                        if mechanic.user is not None
                        else _CALENDAR_COLORS[(mechanic.id - 1) % len(_CALENDAR_COLORS)]
                    )
                    works = any(
                        interval.weekday == day.weekday()
                        and interval.start_time <= cell_start.time()
                        and interval.end_time >= cell_end.time()
                        for interval in schedules[mechanic.id].intervals
                    )
                    matching_block = next(
                        (
                            block
                            for block in blocks
                            if block.mechanic_id == mechanic.id
                            and local_time(block.start_time) < cell_end
                            and local_time(block.end_time) > cell_start
                        ),
                        None,
                    )
                    matching_slot = next(
                        (
                            slot
                            for slot in slots
                            if slot.mechanic_id == mechanic.id
                            and local_time(slot.start_time) < cell_end
                            and local_time(slot.end_time) > cell_start
                        ),
                        None,
                    )
                    on_break = self._overlaps_recurring_break(
                        mechanic, cell_start, cell_end, timezone
                    )
                    if matching_slot is not None:
                        order = matching_slot.order
                        services = (
                            ", ".join(item.description for item in order.items)
                            if order is not None
                            else matching_slot.title
                        )
                        services = services or matching_slot.title
                        by_time[time_label].append(
                            CalendarBlock(
                                id=f"slot-{matching_slot.id}-{day}-{time_label}",
                                employee_id=mechanic.id,
                                employee_name=mechanic.full_name,
                                color=color,
                                status="busy",
                                order_id=order.id if order else None,
                                brand=(order.vehicle.make if order and order.vehicle else None),
                                plate=(
                                    order.vehicle.license_plate if order and order.vehicle else None
                                ),
                                client_name=(
                                    order.client.full_name if order and order.client else None
                                ),
                                service_name=services or None,
                                order_status=order.status.value if order else None,
                            )
                        )
                    elif matching_block is not None or on_break:
                        by_time[time_label].append(
                            CalendarBlock(
                                id=f"block-{matching_block.id}-{day}-{time_label}",
                                employee_id=mechanic.id,
                                employee_name=mechanic.full_name,
                                color=color,
                                status="unavailable",
                                reason=(
                                    matching_block.reason
                                    if matching_block is not None
                                    else "Перерыв"
                                ),
                            )
                        )
                    else:
                        by_time[time_label].append(
                            CalendarBlock(
                                id=f"free-{mechanic.id}-{day}-{time_label}",
                                employee_id=mechanic.id,
                                employee_name=mechanic.full_name,
                                color=color,
                                status="available" if works else "unavailable",
                            )
                        )
            days.append(CalendarDay(date=day, slots=by_time))
        return CalendarView(
            timezone=settings.SCHEDULE_TIMEZONE,
            times=times,
            days=days,
        )

"""Staff-card and monthly schedule projections for the current admin frontend."""

import calendar
import datetime as dt
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate
from app.modules.employees.service import EmployeeService
from app.modules.schedule.admin_schemas import (
    StaffDetail,
    StaffMonthDay,
    StaffMonthRow,
    StaffScheduleSettings,
    StaffWrite,
)
from app.modules.schedule.repository import ScheduleRepository
from app.modules.schedule.schemas import WorkingHoursInterval
from app.modules.schedule.service import ScheduleService
from app.modules.users.models import User
from app.modules.users.roles import (
    DEFAULT_STAFF_ROLE,
    STAFF_ROLE_LABELS,
    STAFF_ROLE_TO_TECHNICAL,
)
from app.shared.enums import UserRole

_ROLE_MAP = STAFF_ROLE_TO_TECHNICAL
_ROLE_KEY = DEFAULT_STAFF_ROLE
_ROLE_LABEL = STAFF_ROLE_LABELS
_EMPTY_DOCUMENTS = {"passport": None, "inn": None, "medicalBook": None}
_EMPTY_ACCESS = {
    "schedule": False,
    "crm": False,
    "services": False,
    "tasks": False,
    "qr": False,
    "settings": False,
}
_DEFAULT_INTERVALS = [
    WorkingHoursInterval(
        weekday=weekday,
        start_time=dt.time(9),
        end_time=dt.time(18),
    )
    for weekday in range(5)
]


class ScheduleAdminService:
    def __init__(self, session, current_user: User) -> None:
        self.session = session
        self.current_user = current_user
        self.organization_id = current_user.organization_id
        self.employees = EmployeeService(session, self.organization_id)
        self.schedule = ScheduleService(ScheduleRepository(session, self.organization_id))

    @staticmethod
    def _role_key(role: UserRole, stored: str | None = None) -> str:
        return stored if stored in _ROLE_MAP else _ROLE_KEY[role]

    @classmethod
    def _role_label(cls, role: UserRole, stored: str | None = None) -> str:
        return _ROLE_LABEL[cls._role_key(role, stored)]

    @classmethod
    def _display_role(cls, user: User) -> str:
        if user.is_owner:
            return "Владелец"
        return cls._role_label(user.role, user.staff_role_key)

    @staticmethod
    def _documents(value: dict | None) -> dict[str, dict | None]:
        return {**_EMPTY_DOCUMENTS, **(value or {})}

    @staticmethod
    def _access(value: dict | None) -> dict[str, bool]:
        return {**_EMPTY_ACCESS, **(value or {})}

    @classmethod
    def _writable_access(cls, role_key: str, value: dict | None) -> dict[str, bool]:
        access = cls._access(value)
        access["settings"] = False
        if role_key not in {"senior_admin", "junior_admin"}:
            access["qr"] = False
        return access

    async def detail(self, user_id: int) -> StaffDetail:
        employee = await self.employees.get(user_id)
        role_key = self._role_key(employee.role, employee.staff_role_key)
        return StaffDetail(
            id=employee.id,
            name=employee.full_name,
            role=(
                "Владелец"
                if employee.is_owner
                else self._role_label(employee.role, employee.staff_role_key)
            ),
            role_key=role_key,
            phone=employee.phone or "",
            email=str(employee.email) if employee.email is not None else "",
            duties=employee.duties or "",
            rate=employee.rate,
            color=employee.calendar_color,
            avatar_bg=employee.calendar_color,
            documents=self._documents(employee.documents),
            access=self._access(employee.ui_permissions),
            login=employee.login or "",
            # Пароль никогда не возвращается из backend.
            password="",
        )

    @staticmethod
    def _role(value: str) -> UserRole:
        if value not in _ROLE_MAP:
            raise BusinessRuleError("Неизвестная роль сотрудника")
        return _ROLE_MAP[value]

    async def create(self, data: StaffWrite) -> StaffDetail:
        name = data.name.strip()
        phone = data.phone.strip()
        login = data.login.strip()
        access = self._writable_access(data.role, data.access)
        if not name:
            raise BusinessRuleError("Напишите ФИО сотрудника")
        if not phone:
            raise BusinessRuleError("Введите номер телефона сотрудника")
        if not login:
            raise BusinessRuleError("Придумайте логин сотрудника")
        if len(login) < 3:
            raise BusinessRuleError("Логин нового сотрудника должен быть не короче 3 символов")
        if not data.password:
            raise BusinessRuleError("Придумайте пароль сотрудника")
        if len(data.password) < 6:
            raise BusinessRuleError("Пароль нового сотрудника должен быть не короче 6 символов")
        if not any(access.values()):
            raise BusinessRuleError("Выберите разделы, к которым сотрудник получит доступ")
        created = await self.employees.create(
            EmployeeCreate(
                email=data.email,
                login=login,
                password=data.password,
                full_name=name,
                phone=phone,
                role=self._role(data.role),
                staff_role_key=data.role,
                rate=data.rate,
                calendar_color=data.color or "#5C6BC0",
                duties=data.duties or None,
                ui_permissions=access,
                hourly_rate=Decimal(0),
                documents=self._documents(data.documents),
            )
        )
        return await self.detail(created.id)

    async def update(self, user_id: int, data: StaffWrite) -> StaffDetail:
        existing = await self.employees.get(user_id)
        if existing.is_owner and not self.current_user.is_owner:
            raise BusinessRuleError("Изменять владельца может только сам владелец")
        payload = EmployeeUpdate(
            email=data.email,
            login=data.login or None,
            full_name=data.name.strip() or data.login.strip() or existing.full_name,
            phone=data.phone or None,
            role=self._role(data.role),
            staff_role_key=data.role,
            rate=data.rate,
            calendar_color=data.color or "#5C6BC0",
            duties=data.duties or None,
            ui_permissions=self._writable_access(data.role, data.access),
            documents=self._documents(data.documents),
            password=data.password if data.password else None,
        )
        await self.employees.update(user_id, payload)
        return await self.detail(user_id)

    async def delete(self, user_id: int) -> None:
        existing = await self.employees.get(user_id)
        if existing.is_owner:
            raise BusinessRuleError("Владельца организации нельзя удалить как сотрудника")
        await self.employees.deactivate(user_id, self.current_user.id)

    async def _users(self) -> list[User]:
        conditions = [
            User.organization_id == self.organization_id,
            User.is_active.is_(True),
        ]
        # Мастер видит в разделе расписания только собственную строку.
        # Ограничение выполняется на backend, поэтому его нельзя обойти
        # прямым запросом к API или изменением frontend.
        if self.current_user.role == UserRole.MECHANIC and not self.current_user.is_owner:
            conditions.append(User.id == self.current_user.id)
        return list(
            (
                await self.session.execute(
                    select(User)
                    .options(selectinload(User.mechanic))
                    .where(*conditions)
                    .order_by(User.full_name)
                )
            )
            .scalars()
            .all()
        )

    @staticmethod
    def _break_minutes(user: User) -> int:
        total = 0
        values = user.schedule_breaks or (user.mechanic.schedule_breaks if user.mechanic else [])
        for item in values:
            try:
                start = dt.time.fromisoformat(item["start"])
                end = dt.time.fromisoformat(item["end"])
            except (KeyError, TypeError, ValueError):
                continue
            total += (
                dt.datetime.combine(dt.date.min, end) - dt.datetime.combine(dt.date.min, start)
            ).seconds // 60
        return total

    @staticmethod
    def _stored_intervals(user: User) -> list[WorkingHoursInterval]:
        result: list[WorkingHoursInterval] = []
        for item in user.schedule_intervals:
            try:
                result.append(
                    WorkingHoursInterval(
                        weekday=int(item["weekday"]),
                        start_time=dt.time.fromisoformat(str(item["start"])),
                        end_time=dt.time.fromisoformat(str(item["end"])),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
        return result

    async def month(self, year: int, month: int) -> list[StaffMonthRow]:
        if month < 0 or month > 11:
            raise BusinessRuleError("month должен быть от 0 до 11")
        result: list[StaffMonthRow] = []
        days_count = calendar.monthrange(year, month + 1)[1]
        for user in await self._users():
            intervals = self._stored_intervals(user)
            if not intervals and user.mechanic is not None:
                intervals = (await self.schedule.working_hours(user.mechanic.id)).intervals
            if not intervals:
                intervals = _DEFAULT_INTERVALS
            by_weekday = {interval.weekday: interval for interval in intervals}
            days: list[StaffMonthDay] = []
            total_minutes = 0
            total_days = 0
            break_minutes = self._break_minutes(user)
            for day_number in range(1, days_count + 1):
                day = dt.date(year, month + 1, day_number)
                interval = by_weekday.get(day.weekday())
                if interval is None:
                    days.append(
                        StaffMonthDay(
                            day=day_number,
                            active=False,
                            start=None,
                            end=None,
                        )
                    )
                    continue
                minutes = int(
                    (
                        dt.datetime.combine(day, interval.end_time)
                        - dt.datetime.combine(day, interval.start_time)
                    ).total_seconds()
                    // 60
                )
                total_days += 1
                total_minutes += max(0, minutes - break_minutes)
                days.append(
                    StaffMonthDay(
                        day=day_number,
                        active=True,
                        start=interval.start_time.strftime("%H:%M"),
                        end=interval.end_time.strftime("%H:%M"),
                    )
                )
            result.append(
                StaffMonthRow(
                    id=user.id,
                    name=user.full_name,
                    role=self._display_role(user),
                    avatar_bg=user.calendar_color,
                    total_days=total_days,
                    total_hours=round(total_minutes / 60),
                    days=days,
                )
            )
        return result

    async def save_settings(self, data: StaffScheduleSettings) -> None:
        users = await self._users()
        if data.employee_id != "all":
            users = [user for user in users if user.id == int(data.employee_id)]
            if not users:
                raise NotFoundError("Сотрудник не найден")
        intervals = [
            WorkingHoursInterval(
                # Frontend/JS: Sunday=0; backend/Python: Monday=0.
                weekday=(weekday - 1) % 7,
                start_time=data.start,
                end_time=data.end,
            )
            for weekday in sorted(set(data.work_days))
        ]
        breaks = [
            {
                "start": item.start.strftime("%H:%M"),
                "end": item.end.strftime("%H:%M"),
            }
            for item in data.breaks
        ]
        stored_intervals = [
            {
                "weekday": item.weekday,
                "start": item.start_time.strftime("%H:%M"),
                "end": item.end_time.strftime("%H:%M"),
            }
            for item in intervals
        ]
        for user in users:
            user.schedule_intervals = stored_intervals
            user.schedule_breaks = breaks
            if user.mechanic is not None:
                await self.schedule.replace_working_hours(user.mechanic.id, intervals)
                user.mechanic.schedule_breaks = breaks
        await self.session.flush()

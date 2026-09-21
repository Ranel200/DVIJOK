"""Compatibility contracts for the ready-made schedule/staff admin screens."""

from datetime import time
from decimal import Decimal

from pydantic import ConfigDict, EmailStr, Field, field_validator, model_validator

from app.shared.base_schema import StrictModel


class AdminScheduleModel(StrictModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class StaffMonthDay(AdminScheduleModel):
    day: int
    active: bool
    start: str | None
    end: str | None


class StaffMonthRow(AdminScheduleModel):
    id: int
    name: str
    role: str
    avatar_bg: str = Field(alias="avatarBg")
    total_days: int = Field(alias="totalDays")
    total_hours: int = Field(alias="totalHours")
    days: list[StaffMonthDay]


class StaffDetail(AdminScheduleModel):
    id: int
    name: str
    role: str
    role_key: str = Field(alias="roleKey")
    phone: str
    email: str
    duties: str
    rate: Decimal | None
    color: str
    avatar_bg: str = Field(alias="avatarBg")
    documents: dict[str, dict | None]
    access: dict[str, bool]
    login: str
    password: str


class StaffWrite(AdminScheduleModel):
    role: str
    name: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=20)
    email: EmailStr | None = None
    duties: str = ""
    rate: Decimal | None = Field(default=None, ge=0)
    color: str | None = None
    documents: dict[str, dict | None] = Field(default_factory=dict)
    access: dict[str, bool] = Field(default_factory=dict)
    login: str = ""
    password: str = Field(default="", max_length=72)

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_as_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class ScheduleBreak(AdminScheduleModel):
    start: time
    end: time

    @model_validator(mode="after")
    def validate_interval(self) -> "ScheduleBreak":
        if self.end <= self.start:
            raise ValueError("Начало перерыва должно быть раньше окончания")
        return self


class ScheduleWorkPeriod(AdminScheduleModel):
    start: time
    end: time

    @model_validator(mode="after")
    def validate_interval(self) -> "ScheduleWorkPeriod":
        if self.end <= self.start:
            raise ValueError("Начало рабочего периода должно быть раньше окончания")
        return self


class StaffScheduleSettings(AdminScheduleModel):
    type: str = "workdays"
    slot_step: int = Field(default=60, alias="slotStep", ge=1, le=1440)
    work_periods: list[ScheduleWorkPeriod] = Field(default_factory=list, alias="workPeriods")
    # Старый контракт оставлен для обратной совместимости клиентов.
    start: time | None = None
    end: time | None = None
    breaks: list[ScheduleBreak] = Field(default_factory=list)
    work_days: list[int] = Field(alias="workDays", min_length=1)
    employee_ids: list[int | str] = Field(default_factory=list, alias="employeeIds")
    employee_id: int | str | None = Field(default=None, alias="employeeId")

    @property
    def resolved_periods(self) -> list[ScheduleWorkPeriod]:
        if self.work_periods:
            return self.work_periods
        if self.start is not None and self.end is not None:
            return [ScheduleWorkPeriod(start=self.start, end=self.end)]
        return []

    @property
    def resolved_employee_ids(self) -> list[int | str]:
        return self.employee_ids or ([self.employee_id] if self.employee_id is not None else [])

    @model_validator(mode="after")
    def validate_settings(self) -> "StaffScheduleSettings":
        if self.type != "workdays":
            raise ValueError("Поддерживается только тип workdays")
        periods = self.resolved_periods
        if not periods:
            raise ValueError("Укажите хотя бы один рабочий период")
        targets = self.resolved_employee_ids
        if not targets:
            raise ValueError("Выберите хотя бы одного сотрудника")
        if any(day < 0 or day > 6 for day in self.work_days):
            raise ValueError("День недели должен быть от 0 до 6")
        if any(isinstance(item, str) and item != "all" for item in targets):
            raise ValueError("employeeIds должны содержать числа или 'all'")
        ordered = sorted(periods, key=lambda item: item.start)
        if any(left.end > right.start for left, right in zip(ordered, ordered[1:])):
            raise ValueError("Рабочие периоды не должны пересекаться")
        for item in self.breaks:
            if not any(item.start >= period.start and item.end <= period.end for period in periods):
                raise ValueError("Перерыв должен находиться внутри рабочего периода")
        return self

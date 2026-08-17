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


class StaffScheduleSettings(AdminScheduleModel):
    type: str = "workdays"
    start: time
    end: time
    breaks: list[ScheduleBreak] = Field(default_factory=list)
    work_days: list[int] = Field(alias="workDays", min_length=1)
    employee_id: int | str = Field(alias="employeeId")

    @model_validator(mode="after")
    def validate_settings(self) -> "StaffScheduleSettings":
        if self.type != "workdays":
            raise ValueError("Поддерживается только тип workdays")
        if self.end <= self.start:
            raise ValueError("Начало рабочего дня должно быть раньше окончания")
        if any(day < 0 or day > 6 for day in self.work_days):
            raise ValueError("День недели должен быть от 0 до 6")
        if isinstance(self.employee_id, str) and self.employee_id != "all":
            raise ValueError("employeeId должен быть числом или 'all'")
        for item in self.breaks:
            if item.start < self.start or item.end > self.end:
                raise ValueError("Перерыв должен находиться внутри рабочего дня")
        return self

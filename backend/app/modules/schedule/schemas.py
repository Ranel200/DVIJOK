"""Схемы модуля schedule (ТЗ A4)."""

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.shared.base_schema import ORMSchema, TimestampedRead
from app.shared.enums import ServiceCategory


class _Interval(ORMSchema):
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def _check_interval(self) -> "_Interval":
        if self.end_time <= self.start_time:
            raise ValueError("end_time должно быть позже start_time")
        return self


class SlotCreate(_Interval):
    mechanic_id: int
    order_id: int | None = None
    work_type: ServiceCategory | None = None
    title: str | None = None


class SlotUpdate(ORMSchema):
    mechanic_id: int | None = None
    order_id: int | None = None
    work_type: ServiceCategory | None = None
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


class SlotRead(TimestampedRead):
    mechanic_id: int
    order_id: int | None
    work_type: ServiceCategory | None
    title: str | None
    start_time: datetime
    end_time: datetime


class BlockCreate(_Interval):
    mechanic_id: int
    reason: str | None = None


class BlockRead(TimestampedRead):
    mechanic_id: int
    reason: str | None
    start_time: datetime
    end_time: datetime


class WeekView(BaseModel):
    week_start: datetime
    week_end: datetime
    slots: list[SlotRead]
    blocks: list[BlockRead]


class CalendarBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    employee_id: int = Field(alias="employeeId")
    employee_name: str = Field(alias="employeeName")
    color: str
    status: str
    order_id: int | None = Field(default=None, alias="orderId")
    brand: str | None = None
    plate: str | None = None
    client_name: str | None = Field(default=None, alias="clientName")
    service_name: str | None = Field(default=None, alias="serviceName")
    order_status: str | None = Field(default=None, alias="orderStatus")
    reason: str | None = None


class CalendarDay(BaseModel):
    date: date
    slots: dict[str, list[CalendarBlock]]


class CalendarView(BaseModel):
    timezone: str
    times: list[str]
    days: list[CalendarDay]


class WorkingHoursInterval(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def _check_times(self) -> "WorkingHoursInterval":
        if self.end_time <= self.start_time:
            raise ValueError("end_time должно быть позже start_time")
        return self


class WorkingHoursReplace(BaseModel):
    intervals: list[WorkingHoursInterval]


class WorkingHoursRead(BaseModel):
    mechanic_id: int
    timezone: str
    uses_default: bool
    intervals: list[WorkingHoursInterval]


class AvailableSlot(BaseModel):
    mechanic_id: int
    start_time: datetime
    end_time: datetime
    duration_minutes: int


class AvailabilitySuggestions(BaseModel):
    date_from: date
    date_to: date
    timezone: str
    duration_minutes: int
    slots: list[AvailableSlot]


class OrderReservationCreate(BaseModel):
    mechanic_id: int
    start_time: datetime
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)

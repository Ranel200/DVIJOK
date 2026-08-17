"""Схемы модуля mechanics (ТЗ A7)."""

from decimal import Decimal

from pydantic import Field

from app.shared.base_schema import ORMSchema, TimestampedRead
from app.shared.enums import ServiceCategory


class MechanicBase(ORMSchema):
    full_name: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    specializations: list[ServiceCategory] = Field(default_factory=list)
    hired_year: int | None = Field(default=None, ge=1950, le=2100)
    hourly_rate: Decimal = Field(default=Decimal(0), ge=0)
    commission_percent: Decimal = Field(default=Decimal(0), ge=0, le=100)


class MechanicCreate(MechanicBase):
    user_id: int | None = None


class MechanicUpdate(ORMSchema):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    specializations: list[ServiceCategory] | None = None
    hired_year: int | None = Field(default=None, ge=1950, le=2100)
    hourly_rate: Decimal | None = Field(default=None, ge=0)
    commission_percent: Decimal | None = Field(default=None, ge=0, le=100)
    user_id: int | None = None
    is_active: bool | None = None


class MechanicRead(TimestampedRead):
    user_id: int | None
    full_name: str
    phone: str | None
    specializations: list[str]
    hired_year: int | None
    hourly_rate: Decimal
    commission_percent: Decimal
    rating: Decimal
    is_active: bool

"""Схемы модуля vehicles."""

from datetime import date

from pydantic import Field

from app.shared.base_schema import ORMSchema, TimestampedRead


class VehicleBase(ORMSchema):
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1900, le=2100)
    license_plate: str | None = Field(default=None, max_length=15)
    vin: str | None = Field(default=None, max_length=17)
    color: str | None = Field(default=None, max_length=50)
    mileage: int | None = Field(default=None, ge=0, le=999_999)
    next_service_mileage: int | None = Field(default=None, ge=0)
    last_service_at: date | None = None


class VehicleCreate(VehicleBase):
    client_id: int


class VehicleUpdate(ORMSchema):
    make: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1900, le=2100)
    license_plate: str | None = Field(default=None, max_length=15)
    vin: str | None = Field(default=None, max_length=17)
    color: str | None = Field(default=None, max_length=50)
    mileage: int | None = Field(default=None, ge=0, le=999_999)
    next_service_mileage: int | None = Field(default=None, ge=0)
    last_service_at: date | None = None


class VehicleRead(TimestampedRead):
    client_id: int | None
    make: str
    model: str
    year: int | None
    license_plate: str | None
    vin: str | None
    color: str | None
    mileage: int | None
    next_service_mileage: int | None
    last_service_at: date | None

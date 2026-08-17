"""Публичные схемы автомобилей клиентского аккаунта."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientVehicleInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    plate: str = Field(min_length=1, max_length=15)
    plate_type: Literal["ru", "foreign"] = Field(default="ru", alias="plateType")
    vin: str = Field(min_length=17, max_length=17)
    year: int | None = Field(default=None, ge=1900, le=2100)
    color: str | None = Field(default=None, max_length=50)
    mileage: int | None = Field(default=None, ge=0, le=999_999)

    @field_validator("brand", "model", "plate", "vin", mode="before")
    @classmethod
    def strip_required(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("color", mode="before")
    @classmethod
    def empty_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("year", "mileage", mode="before")
    @classmethod
    def empty_optional_number(cls, value: object) -> object:
        return None if value == "" else value


class ClientVehicleUpdate(ClientVehicleInput):
    pass


class ClientVehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    brand: str
    model: str
    plate: str
    plate_type: Literal["ru", "foreign"] = Field(alias="plateType")
    vin: str
    year: int | None
    color: str
    mileage: int | None

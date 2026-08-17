"""Схемы модуля services (каталог услуг)."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.shared.base_schema import ORMSchema, TimestampedRead
from app.shared.enums import ServiceCategory, ServicePriceType


class ServiceBase(ORMSchema):
    name: str = Field(min_length=1, max_length=255)
    category: ServiceCategory
    description: str | None = None
    base_price: Decimal = Field(default=Decimal(0), ge=0)
    price_type: ServicePriceType = ServicePriceType.FIXED
    price_to: Decimal | None = Field(default=None, ge=0)
    internal_notes: str | None = None
    mechanic_ids: list[int] = Field(default_factory=list)
    labor_hours: Decimal = Field(default=Decimal(0), ge=0)
    duration_minutes: int = Field(default=60, ge=1)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_price_range(self) -> "ServiceBase":
        if self.price_type == ServicePriceType.RANGE:
            if self.price_to is None or self.price_to < self.base_price:
                raise ValueError("Для диапазона price_to должен быть не меньше base_price")
        return self


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(ORMSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: ServiceCategory | None = None
    description: str | None = None
    base_price: Decimal | None = Field(default=None, ge=0)
    price_type: ServicePriceType | None = None
    price_to: Decimal | None = Field(default=None, ge=0)
    internal_notes: str | None = None
    mechanic_ids: list[int] | None = None
    labor_hours: Decimal | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class ServiceRead(TimestampedRead):
    name: str
    category: ServiceCategory
    description: str | None
    base_price: Decimal
    price_type: ServicePriceType
    price_to: Decimal | None
    internal_notes: str | None
    mechanic_ids: list[int]
    labor_hours: Decimal
    duration_minutes: int
    is_active: bool


class PopularService(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    orders_per_month: int = Field(alias="ordersPerMonth")


class ServiceSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_services: int = Field(alias="totalServices")
    average_check: Decimal = Field(alias="averageCheck")
    popular_service: PopularService | None = Field(alias="popularService")
    revenue_per_month: Decimal = Field(alias="revenuePerMonth")
    active_masters: int = Field(alias="activeMasters")


class ServiceImportError(ORMSchema):
    row_number: int | None = None
    field: str
    message: str


class ServiceImportRow(ORMSchema):
    row_number: int
    name: str
    base_price: Decimal


class ServiceImportReport(ORMSchema):
    valid: bool
    total_rows: int
    valid_rows: int
    imported_rows: int = 0
    errors: list[ServiceImportError]
    rows: list[ServiceImportRow]

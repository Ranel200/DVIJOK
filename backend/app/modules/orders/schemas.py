"""Схемы модуля orders (ТЗ A3)."""

from datetime import datetime
from decimal import Decimal

from pydantic import EmailStr, Field, model_validator

from app.shared.base_schema import ORMSchema, StrictModel, TimestampedRead
from app.shared.enums import (
    OrderDocumentSource,
    OrderItemType,
    OrderSource,
    OrderStatus,
    PaymentStatus,
)


class OrderClientSummary(ORMSchema):
    id: int
    full_name: str
    phone: str
    email: str | None


class OrderVehicleSummary(ORMSchema):
    id: int
    make: str
    model: str
    year: int | None
    license_plate: str | None
    vin: str | None
    color: str | None


class OrderMechanicSummary(ORMSchema):
    id: int
    full_name: str


class OrderItemCreate(StrictModel):
    item_type: OrderItemType = OrderItemType.SERVICE
    service_id: int | None = None
    inventory_item_id: int | None = None
    mechanic_id: int | None = None
    # Если не заданы — подставляются из каталога услуг / складской позиции.
    description: str | None = None
    quantity: Decimal = Field(default=Decimal(1), gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)
    discount_percent: Decimal = Field(default=Decimal(0), ge=0, le=100)
    labor_hours: Decimal | None = Field(default=None, ge=0)


class OrderItemRead(ORMSchema):
    id: int
    item_type: OrderItemType
    service_id: int | None
    inventory_item_id: int | None
    mechanic_id: int | None
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal
    labor_hours: Decimal | None
    total_price: Decimal


class OrderCreate(StrictModel):
    client_id: int | None = None
    vehicle_id: int | None = None
    mechanic_id: int | None = None
    source: OrderSource = OrderSource.OTHER
    comment: str | None = None
    mileage: int | None = Field(default=None, ge=0, le=999_999)
    scheduled_at: datetime | None = None
    items: list[OrderItemCreate] = Field(default_factory=list)


class OrderIntakeClient(StrictModel):
    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=5, max_length=20)
    email: EmailStr | None = None


class OrderIntakeVehicle(StrictModel):
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1900, le=2100)
    license_plate: str | None = Field(default=None, max_length=15)
    vin: str | None = Field(default=None, max_length=17)
    color: str | None = Field(default=None, max_length=50)
    mileage: int | None = Field(default=None, ge=0, le=999_999)


class OrderIntakeCreate(StrictModel):
    """Атомарное создание CRM-заказа с выбором или созданием справочников."""

    client_id: int | None = None
    client: OrderIntakeClient | None = None
    vehicle_id: int | None = None
    vehicle: OrderIntakeVehicle | None = None
    source: OrderSource = OrderSource.OTHER
    comment: str | None = None
    mileage: int | None = Field(default=None, ge=0, le=999_999)
    items: list[OrderItemCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references(self) -> "OrderIntakeCreate":
        if (self.client_id is None) == (self.client is None):
            raise ValueError("Укажите ровно одно из полей client_id или client")
        if (self.vehicle_id is None) == (self.vehicle is None):
            raise ValueError("Укажите ровно одно из полей vehicle_id или vehicle")
        return self


class OrderUpdate(StrictModel):
    mechanic_id: int | None = None
    source: OrderSource | None = None
    comment: str | None = None
    mileage: int | None = Field(default=None, ge=0, le=999_999)
    scheduled_at: datetime | None = None
    payment_status: PaymentStatus | None = None


class OrderStatusUpdate(StrictModel):
    status: OrderStatus


class OrderDocumentRead(TimestampedRead):
    order_id: int
    source: OrderDocumentSource
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    created_by_id: int | None


class OrderRead(TimestampedRead):
    number: str
    client_id: int | None
    vehicle_id: int | None
    mechanic_id: int | None
    created_by_id: int | None
    status: OrderStatus
    source: OrderSource
    payment_status: PaymentStatus
    total_amount: Decimal
    mileage: int | None
    comment: str | None
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    items: list[OrderItemRead]
    documents: list[OrderDocumentRead]
    document: OrderDocumentRead | None
    client: OrderClientSummary | None
    vehicle: OrderVehicleSummary | None
    mechanic: OrderMechanicSummary | None

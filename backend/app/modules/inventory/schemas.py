"""Схемы модуля inventory (ТЗ A8)."""

from datetime import datetime
from decimal import Decimal

from pydantic import Field, computed_field

from app.shared.base_schema import ORMSchema, StrictModel, TimestampedRead
from app.shared.enums import InventoryCategory, MovementType, StockStatus


class InventoryItemBase(ORMSchema):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    category: InventoryCategory
    unit: str = Field(default="шт", max_length=20)
    quantity: Decimal = Field(default=Decimal(0), ge=0)
    min_quantity: Decimal = Field(default=Decimal(0), ge=0)
    purchase_price: Decimal = Field(default=Decimal(0), ge=0)
    sale_price: Decimal = Field(default=Decimal(0), ge=0)
    location: str | None = Field(default=None, max_length=100)


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(ORMSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: InventoryCategory | None = None
    unit: str | None = Field(default=None, max_length=20)
    min_quantity: Decimal | None = Field(default=None, ge=0)
    purchase_price: Decimal | None = Field(default=None, ge=0)
    sale_price: Decimal | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class InventoryItemRead(TimestampedRead):
    sku: str
    name: str
    category: InventoryCategory
    unit: str
    quantity: Decimal
    min_quantity: Decimal
    purchase_price: Decimal
    sale_price: Decimal
    location: str | None
    is_active: bool

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stock_status(self) -> StockStatus:
        """Критично (≤ половины минимума или 0) / Мало (≤ минимума) / Норма."""
        if self.quantity <= 0 or (self.min_quantity > 0 and self.quantity <= self.min_quantity / 2):
            return StockStatus.CRITICAL
        if self.quantity <= self.min_quantity:
            return StockStatus.LOW
        return StockStatus.NORMAL


class MovementCreate(StrictModel):
    movement_type: MovementType
    quantity: Decimal = Field(gt=0)
    order_id: int | None = None
    comment: str | None = None


class WriteOffRequest(StrictModel):
    """Списание запчасти под заказ-наряд (ТЗ A8.3)."""

    quantity: Decimal = Field(gt=0)
    order_id: int | None = None
    comment: str | None = None


class MovementRead(ORMSchema):
    id: int
    inventory_item_id: int
    order_id: int | None
    movement_type: MovementType
    quantity: Decimal
    comment: str | None
    created_by_id: int | None
    created_at: datetime

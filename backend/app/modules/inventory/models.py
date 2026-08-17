"""Склад (ТЗ A8): позиции и движения товара (приход/расход/возврат/списание)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, IntPKMixin, TimestampMixin
from app.shared.enums import InventoryCategory, MovementType


class InventoryItem(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "inventory_items"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    sku: Mapped[str] = mapped_column(String(50), index=True)  # артикул
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[InventoryCategory] = mapped_column(
        Enum(InventoryCategory, native_enum=False, length=20), index=True
    )
    unit: Mapped[str] = mapped_column(String(20), default="шт")
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    min_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # порог сигнала
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # цена закупки
    sale_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    location: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )

    # Артикул уникален в рамках организации, не глобально.
    __table_args__ = (UniqueConstraint("organization_id", "sku", name="uq_inventory_org_sku"),)


class StockMovement(Base, IntPKMixin):
    __tablename__ = "stock_movements"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    inventory_item_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="CASCADE"), index=True
    )
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))
    movement_type: Mapped[MovementType] = mapped_column(
        Enum(MovementType, native_enum=False, length=20)
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    comment: Mapped[str | None] = mapped_column(Text)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    item: Mapped["InventoryItem"] = relationship(back_populates="movements")

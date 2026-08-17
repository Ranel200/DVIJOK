"""Заказ-наряд (ТЗ A3) и его позиции (услуги + запчасти).

OrderItem — мост между Order и Service / InventoryItem. Цена фиксируется в
позиции (snapshot), чтобы изменение прайса не искажало закрытые наряды.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, IntPKMixin, TimestampMixin
from app.shared.enums import (
    OrderDocumentSource,
    OrderItemType,
    OrderSource,
    OrderStatus,
    PaymentStatus,
)

if TYPE_CHECKING:
    from app.modules.clients.models import Client
    from app.modules.inventory.models import InventoryItem
    from app.modules.mechanics.models import Mechanic
    from app.modules.services.models import Service
    from app.modules.vehicles.models import Vehicle


class Order(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "orders"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    number: Mapped[str] = mapped_column(String(20), index=True)
    # CRM allows creating a draft before the customer or vehicle is known.
    # References are filled later when the administrator adds those details.
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id"), index=True, nullable=True
    )
    vehicle_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicles.id"), index=True, nullable=True
    )
    mechanic_id: Mapped[int | None] = mapped_column(
        ForeignKey("mechanics.id", ondelete="SET NULL"), index=True
    )
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=20), default=OrderStatus.NEW, index=True
    )
    source: Mapped[OrderSource] = mapped_column(
        Enum(OrderSource, native_enum=False, length=20),
        default=OrderSource.OTHER,
        index=True,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, length=20), default=PaymentStatus.UNPAID
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    mileage: Mapped[int | None] = mapped_column(Integer)  # фиксация пробега (ТЗ A3.4)
    comment: Mapped[str | None] = mapped_column(Text)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    client: Mapped["Client | None"] = relationship(back_populates="orders")
    vehicle: Mapped["Vehicle | None"] = relationship(back_populates="orders")
    mechanic: Mapped["Mechanic | None"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )
    documents: Mapped[list["OrderDocument"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="OrderDocument.id",
    )

    @property
    def document(self) -> "OrderDocument | None":
        """Backward-compatible latest document for older API consumers."""

        return self.documents[-1] if self.documents else None

    __table_args__ = (
        Index("ix_orders_status_scheduled", "status", "scheduled_at"),
        UniqueConstraint(
            "organization_id",
            "number",
            name="uq_orders_organization_number",
        ),
    )


class OrderItem(Base, IntPKMixin):
    __tablename__ = "order_items"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    item_type: Mapped[OrderItemType] = mapped_column(
        Enum(OrderItemType, native_enum=False, length=20), default=OrderItemType.SERVICE
    )
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id", ondelete="SET NULL"))
    inventory_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="SET NULL")
    )
    mechanic_id: Mapped[int | None] = mapped_column(
        ForeignKey("mechanics.id", ondelete="SET NULL"), index=True
    )
    description: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    labor_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    order: Mapped["Order"] = relationship(back_populates="items")
    service: Mapped["Service | None"] = relationship()
    inventory_item: Mapped["InventoryItem | None"] = relationship()
    mechanic: Mapped["Mechanic | None"] = relationship()


class OrderDocument(Base, IntPKMixin, TimestampMixin):
    """Generated or uploaded document attached to an order."""

    __tablename__ = "order_documents"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[OrderDocumentSource] = mapped_column(
        Enum(OrderDocumentSource, native_enum=False, length=20)
    )
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(String(64))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    order: Mapped["Order"] = relationship(back_populates="documents")

    __table_args__ = (
        CheckConstraint("size_bytes > 0", name="ck_order_documents_size_positive"),
        Index("ix_order_documents_order_id", "order_id"),
    )

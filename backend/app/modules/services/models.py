"""Каталог услуг автосервиса с нормо-часами и базовой ценой."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, IntPKMixin, TimestampMixin
from app.shared.enums import ServiceCategory, ServicePriceType

if TYPE_CHECKING:
    from app.modules.mechanics.models import Mechanic


service_mechanics = Table(
    "service_mechanics",
    Base.metadata,
    Column("service_id", ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
    Column("mechanic_id", ForeignKey("mechanics.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("service_id", "mechanic_id", name="uq_service_mechanics_pair"),
)


class Service(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "services"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "public_booking_key",
            name="uq_services_organization_public_booking_key",
        ),
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    # Stable identifier for the two coarse choices shown by the client UI.
    # Detailed services remain available to the staff/admin contour.
    public_booking_key: Mapped[str | None] = mapped_column(String(20))
    category: Mapped[ServiceCategory] = mapped_column(
        Enum(ServiceCategory, native_enum=False, length=20), index=True
    )
    admin_category: Mapped[str] = mapped_column(String(20), default="other", index=True)
    description: Mapped[str | None] = mapped_column(Text)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    price_type: Mapped[ServicePriceType] = mapped_column(
        Enum(ServicePriceType, native_enum=False, length=20),
        default=ServicePriceType.FIXED,
    )
    price_to: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    internal_notes: Mapped[str | None] = mapped_column(Text)
    labor_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)  # нормо-часы
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    mechanics: Mapped[list["Mechanic"]] = relationship(
        secondary=service_mechanics,
        back_populates="services",
        lazy="selectin",
    )

    @property
    def mechanic_ids(self) -> list[int]:
        return [mechanic.id for mechanic in self.mechanics]

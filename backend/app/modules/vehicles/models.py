"""Автомобиль клиента (ТЗ A5.3 / B3). Тех.паспорт (узлы) — отдельный модуль System B."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, IntPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.clients.models import Client
    from app.modules.orders.models import Order


class Vehicle(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "vehicles"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    # A CRM draft can contain vehicle details before the customer is known.
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), index=True, nullable=True
    )
    make: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column(Integer)
    license_plate: Mapped[str | None] = mapped_column(String(15), index=True)
    vin: Mapped[str | None] = mapped_column(String(17))
    color: Mapped[str | None] = mapped_column(String(50))
    mileage: Mapped[int | None] = mapped_column(Integer)
    next_service_mileage: Mapped[int | None] = mapped_column(Integer)
    last_service_at: Mapped[date | None] = mapped_column(Date)

    client: Mapped["Client | None"] = relationship(back_populates="vehicles")
    orders: Mapped[list["Order"]] = relationship(back_populates="vehicle")

    # VIN уникален в рамках организации, не глобально — разные тенанты могут
    # обслуживать один и тот же физический автомобиль.
    __table_args__ = (UniqueConstraint("organization_id", "vin", name="uq_vehicles_org_vin"),)

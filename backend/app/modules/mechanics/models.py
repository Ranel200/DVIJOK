"""Мастер — рабочий ресурс автосервиса (ТЗ A7). Может иметь учётную запись User."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, IntPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.orders.models import Order
    from app.modules.schedule.models import ScheduleSlot
    from app.modules.services.models import Service
    from app.modules.users.models import User


class Mechanic(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "mechanics"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), unique=True
    )
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    # Специализации (ТЗ A7.2): список направлений, например ["to", "chassis"].
    specializations: Mapped[list[str]] = mapped_column(JSON, default=list)
    hired_year: Mapped[int | None] = mapped_column(Integer)
    # Зарплатные настройки (ТЗ A7.3): ставка + процент от выработки.
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0)
    schedule_configured: Mapped[bool] = mapped_column(Boolean, default=False)
    schedule_breaks: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User | None"] = relationship(back_populates="mechanic")
    orders: Mapped[list["Order"]] = relationship(back_populates="mechanic")
    schedule_slots: Mapped[list["ScheduleSlot"]] = relationship(back_populates="mechanic")
    services: Mapped[list["Service"]] = relationship(
        secondary="service_mechanics",
        back_populates="mechanics",
    )

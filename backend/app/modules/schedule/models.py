"""Расписание (ТЗ A4): слоты записи мастеров и блокировки (болезнь/отпуск)."""

from datetime import datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, IntPKMixin, TimestampMixin
from app.shared.enums import ServiceCategory

if TYPE_CHECKING:
    from app.modules.mechanics.models import Mechanic
    from app.modules.orders.models import Order


class ScheduleSlot(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "schedule_slots"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    mechanic_id: Mapped[int] = mapped_column(
        ForeignKey("mechanics.id", ondelete="CASCADE"), index=True
    )
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))
    work_type: Mapped[ServiceCategory | None] = mapped_column(
        Enum(ServiceCategory, native_enum=False, length=20)
    )
    title: Mapped[str | None] = mapped_column(String(255))  # «марка авто + услуга»
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    mechanic: Mapped["Mechanic"] = relationship(back_populates="schedule_slots")
    order: Mapped["Order | None"] = relationship()

    # Композитный индекс для детекта пересечений брони у мастера.
    __table_args__ = (Index("ix_schedule_mechanic_start", "mechanic_id", "start_time"),)


class MechanicBlock(Base, IntPKMixin, TimestampMixin):
    """Блокировка мастера/поста на период (ТЗ A4: болезнь, отпуск)."""

    __tablename__ = "mechanic_blocks"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    mechanic_id: Mapped[int] = mapped_column(
        ForeignKey("mechanics.id", ondelete="CASCADE"), index=True
    )
    reason: Mapped[str | None] = mapped_column(Text)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MechanicWorkingHours(Base, IntPKMixin, TimestampMixin):
    """Повторяющийся локальный рабочий интервал (weekday: Monday=0)."""

    __tablename__ = "mechanic_working_hours"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    mechanic_id: Mapped[int] = mapped_column(
        ForeignKey("mechanics.id", ondelete="CASCADE"), index=True
    )
    weekday: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time())
    end_time: Mapped[time] = mapped_column(Time())

    __table_args__ = (
        CheckConstraint(
            "weekday >= 0 AND weekday <= 6",
            name="ck_mechanic_working_hours_weekday",
        ),
        CheckConstraint(
            "end_time > start_time",
            name="ck_mechanic_working_hours_interval",
        ),
        UniqueConstraint(
            "mechanic_id",
            "weekday",
            "start_time",
            "end_time",
            name="uq_mechanic_working_hours_interval",
        ),
    )

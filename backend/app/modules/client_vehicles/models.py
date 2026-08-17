"""Автомобиль клиента, доступный для записи в любую организацию."""

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, IntPKMixin, TimestampMixin


class ClientVehicle(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "client_vehicles"

    client_account_id: Mapped[int] = mapped_column(
        ForeignKey("client_accounts.id", ondelete="CASCADE"), index=True
    )
    brand: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    plate: Mapped[str] = mapped_column(String(15), index=True)
    plate_type: Mapped[str] = mapped_column(String(16), default="ru")
    vin: Mapped[str | None] = mapped_column(String(17), index=True)
    year: Mapped[int | None] = mapped_column(Integer)
    color: Mapped[str | None] = mapped_column(String(50))
    mileage: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint(
            "client_account_id",
            "vin",
            name="uq_client_vehicles_account_vin",
        ),
        CheckConstraint(
            "plate_type IN ('ru', 'foreign')",
            name="ck_client_vehicles_plate_type",
        ),
    )

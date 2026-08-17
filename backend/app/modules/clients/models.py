"""Клиент автосервиса (ТЗ A5). Вычисляемые поля (визиты, сумма, последний визит)
считаются в сервисе агрегатными запросами, не хранятся."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, IntPKMixin, TimestampMixin
from app.shared.enums import ClientType

if TYPE_CHECKING:
    from app.modules.orders.models import Order
    from app.modules.vehicles.models import Vehicle


class Client(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "clients"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20), index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    birth_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    client_type: Mapped[ClientType] = mapped_column(
        Enum(ClientType, native_enum=False, length=20), default=ClientType.NEW, index=True
    )
    # Баланс и бонусные баллы (ТЗ A5.3).
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    bonus_points: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    # Подписки на уведомления / согласие на маркетинг (ТЗ B8.5).
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Связь с глобальной клиентской учёткой (Система B, client_auth.ClientAccount).
    # FK по имени таблицы — без импорта модуля, чтобы не тянуть client_auth сюда.
    client_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("client_accounts.id", ondelete="SET NULL"), index=True, nullable=True
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="client")

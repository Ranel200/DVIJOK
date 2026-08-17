"""Организация-тенант (автосервис). Регистрация и настройки/подписка."""

from datetime import date

from sqlalchemy import Boolean, Date, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, IntPKMixin, TimestampMixin
from app.shared.enums import LegalForm, OrganizationStatus, TaxSystem


class Organization(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    tax_system: Mapped[TaxSystem] = mapped_column(Enum(TaxSystem, native_enum=False, length=20))
    legal_form: Mapped[LegalForm] = mapped_column(Enum(LegalForm, native_enum=False, length=20))
    legal_address: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(20))
    head_name: Mapped[str | None] = mapped_column(String(255))
    ogrn: Mapped[str | None] = mapped_column(String(15))
    email: Mapped[str | None] = mapped_column(String(255))
    # Length matches the migration already applied in production. Input validation
    # in the settings schema still limits a bank account number to 34 characters.
    bank_account: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    subscription_plan: Mapped[str] = mapped_column(String(50), default="PRO")
    subscription_started_at: Mapped[date | None] = mapped_column(Date)
    status: Mapped[OrganizationStatus] = mapped_column(
        Enum(OrganizationStatus, native_enum=False, length=20), default=OrganizationStatus.TRIAL
    )
    subscription_until: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    next_order_number: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

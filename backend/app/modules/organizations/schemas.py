"""Схемы модуля organizations: регистрация тенанта и настройки профиля."""

from datetime import date

from pydantic import EmailStr, Field

from app.shared.base_schema import StrictModel, TimestampedRead
from app.shared.enums import LegalForm, OrganizationStatus, TaxSystem


class OrganizationRegister(StrictModel):
    """Регистрация автосервиса: профиль организации + первый администратор."""

    name: str = Field(min_length=1, max_length=255)
    inn: str = Field(min_length=10, max_length=12)
    tax_system: TaxSystem
    legal_form: LegalForm
    legal_address: str = Field(min_length=1)
    phone: str = Field(min_length=1, max_length=20)

    admin_full_name: str = Field(min_length=1, max_length=255)
    admin_email: EmailStr
    admin_password: str = Field(min_length=6, max_length=72)


class OrganizationUpdate(StrictModel):
    """Настройки — профильные поля. Статус/подписку правит только сама платформа."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    legal_address: str | None = Field(default=None, min_length=1)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    tax_system: TaxSystem | None = None


class OrganizationRead(TimestampedRead):
    name: str
    inn: str
    tax_system: TaxSystem
    legal_form: LegalForm
    legal_address: str
    phone: str
    status: OrganizationStatus
    subscription_until: date | None
    is_active: bool

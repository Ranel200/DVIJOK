"""Схемы модуля client_auth."""

from pydantic import Field, field_validator

from app.modules.client_auth.phone import normalize_client_phone
from app.shared.base_schema import StrictModel, TimestampedRead


class OtpRequest(StrictModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        return normalize_client_phone(value)


class OtpRequestResponse(StrictModel):
    detail: str
    debug_code: str | None = None


class OtpVerify(StrictModel):
    phone: str
    code: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    # Опционально для обратной совместимости старых клиентов API.
    referral_code: str | None = Field(default=None, min_length=8, max_length=64)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        return normalize_client_phone(value)


class ClientAccountRead(TimestampedRead):
    phone: str
    full_name: str | None
    telegram_id: str | None
    vk_id: str | None
    is_active: bool


class ClientAccountUpdate(StrictModel):
    full_name: str = Field(min_length=1, max_length=255)

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Введите ФИО")
        return value


class LinkTokenRead(StrictModel):
    link_token: str

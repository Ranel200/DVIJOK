"""Схемы аутентификации."""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.modules.users.schemas import UserRead
from app.shared.base_schema import StrictModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token: str | None = None
    token_type: str = "bearer"


class RefreshRequest(StrictModel):
    refresh_token: str | None = None


class StaffSession(TokenPair):
    """TokenPair плюс поля, которые уже ожидает готовая admin-панель."""

    token: str
    user: UserRead


class StaffUser(BaseModel):
    user: UserRead


class SubscriptionSelection(StrictModel):
    plan: Literal["standard", "pro", "premium"]


class AdminFrontendRegister(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    head_name: str = Field(min_length=1, max_length=255, alias="headName")
    legal_type: str = Field(alias="legalType")
    inn: str = Field(min_length=10, max_length=12)
    tax_system: str = Field(alias="taxSystem")
    phone: str = Field(min_length=1, max_length=20)
    email: EmailStr
    contact_name: str = Field(min_length=1, max_length=255, alias="contactName")
    address: str = Field(min_length=1)
    password: str = Field(min_length=6, max_length=72)
    password_confirm: str = Field(alias="passwordConfirm")
    consent: bool

    @model_validator(mode="after")
    def validate_registration(self) -> "AdminFrontendRegister":
        if self.password != self.password_confirm:
            raise ValueError("Пароли не совпадают")
        if not self.consent:
            raise ValueError("Необходимо согласие на обработку данных")
        return self

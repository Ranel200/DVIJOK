"""Контракт экрана настроек admin frontend без раскрытия секретов."""

from datetime import date, datetime

from pydantic import ConfigDict, EmailStr, Field, field_validator, model_validator

from app.shared.base_schema import StrictModel


class SettingsModel(StrictModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ServiceSettings(SettingsModel):
    name: str
    head_name: str = Field(alias="headName")
    legal_type: str = Field(alias="legalType")
    tax_system: str = Field(alias="taxSystem")
    inn: str
    ogrn: str
    bank_account: str = Field(alias="bankAccount")
    phone: str
    email: str
    address: str
    logo: str
    description: str


class ServiceSettingsUpdate(SettingsModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    head_name: str | None = Field(default=None, max_length=255, alias="headName")
    legal_type: str | None = Field(default=None, alias="legalType")
    tax_system: str | None = Field(default=None, alias="taxSystem")
    inn: str | None = Field(default=None, min_length=10, max_length=12)
    ogrn: str | None = Field(default=None, max_length=15)
    bank_account: str | None = Field(default=None, max_length=34, alias="bankAccount")
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    logo: str | None = Field(default=None, max_length=2_500_000)
    description: str | None = None

    @field_validator("email", "bank_account", mode="before")
    @classmethod
    def empty_optional_as_none(cls, value: object) -> object:
        """Treat blank optional form fields as omitted values."""
        if isinstance(value, str) and not value.strip():
            return None
        return value


class SubscriptionFeature(SettingsModel):
    icon: str
    label: str


class SubscriptionSettings(SettingsModel):
    status: str
    plan: str
    active_until: date | None = Field(alias="activeUntil")
    days_left: int = Field(alias="daysLeft")
    used_months: int = Field(alias="usedMonths")
    total_months: int = Field(alias="totalMonths")
    features: list[SubscriptionFeature]


class SecuritySession(SettingsModel):
    id: str
    current: bool
    type: str
    device_name: str = Field(alias="deviceName")
    browser: str
    city: str
    country: str
    ip: str
    last_active_at: datetime | None = Field(alias="lastActiveAt")


class SecuritySettings(SettingsModel):
    current_password: str = Field(alias="currentPassword")
    password_changed_at: date = Field(alias="passwordChangedAt")
    security_level: str = Field(alias="securityLevel")
    email_confirm_enabled: bool = Field(alias="emailConfirmEnabled")
    email: str
    phone_confirm_enabled: bool = Field(alias="phoneConfirmEnabled")
    phone: str
    sessions: list[SecuritySession]
    login_history: list[dict] = Field(alias="loginHistory")


class SettingsRead(SettingsModel):
    service: ServiceSettings
    subscription: SubscriptionSettings
    security: SecuritySettings


class PasswordChange(SettingsModel):
    # Имена совместимы с текущим frontend: currentPassword фактически новый пароль.
    current_password: str = Field(min_length=6, max_length=72, alias="currentPassword")
    old_password: str = Field(min_length=1, max_length=72, alias="oldPassword")
    password_changed_at: date | None = Field(default=None, alias="passwordChangedAt")
    code: str | None = None


class SettingsUpdate(SettingsModel):
    service: ServiceSettingsUpdate | None = None
    security: PasswordChange | None = None
    action: str | None = None
    email: EmailStr | None = None

    @model_validator(mode="after")
    def validate_operation(self) -> "SettingsUpdate":
        count = sum(
            (
                self.service is not None,
                self.security is not None,
                self.action is not None,
            )
        )
        if count != 1:
            raise ValueError("Укажите ровно одну операцию настроек")
        if self.action is not None and self.action != "sendPasswordCode":
            raise ValueError("Неизвестное действие настроек")
        return self

"""Контракты единой карточки сотрудника для административного приложения."""

from decimal import Decimal

from pydantic import ConfigDict, EmailStr, Field, model_validator

from app.modules.users.schemas import UserBase, UserUpdate
from app.shared.base_schema import ORMSchema
from app.shared.enums import ServiceCategory, UserRole


class EmployeeCreate(UserBase):
    email: EmailStr | None = None
    password: str = Field(min_length=6, max_length=72)
    specializations: list[ServiceCategory] = Field(default_factory=list)
    hired_year: int | None = Field(default=None, ge=1950, le=2100)
    hourly_rate: Decimal = Field(default=Decimal(0), ge=0)
    commission_percent: Decimal = Field(default=Decimal(0), ge=0, le=100)
    documents: dict[str, dict | None] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_login_identity(self) -> "EmployeeCreate":
        if self.email is None and self.login is None:
            raise ValueError("Для сотрудника обязателен логин или email")
        return self


class EmployeeUpdate(UserUpdate):
    email: EmailStr | None = None
    specializations: list[ServiceCategory] | None = None
    hired_year: int | None = Field(default=None, ge=1950, le=2100)
    hourly_rate: Decimal | None = Field(default=None, ge=0)
    commission_percent: Decimal | None = Field(default=None, ge=0, le=100)
    documents: dict[str, dict | None] | None = None


class EmployeeRead(ORMSchema):
    id: int
    mechanic_id: int | None
    email: EmailStr | None
    full_name: str
    phone: str | None
    login: str | None
    role: UserRole
    staff_role_key: str
    rate: Decimal | None
    is_active: bool
    is_owner: bool
    calendar_color: str
    duties: str | None
    ui_permissions: dict[str, bool]
    documents: dict[str, dict | None]
    specializations: list[str]
    hired_year: int | None
    hourly_rate: Decimal
    commission_percent: Decimal
    rating: Decimal
    schedule_configured: bool


class EmployeeDocumentRead(ORMSchema):
    model_config = ConfigDict(from_attributes=True, extra="forbid", populate_by_name=True)

    id: int
    kind: str
    name: str
    file_name: str = Field(alias="fileName")
    content_type: str = Field(alias="contentType")
    size_bytes: int = Field(alias="sizeBytes")
    sha256: str
    download_url: str = Field(alias="downloadUrl")

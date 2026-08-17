"""Pydantic-схемы модуля users."""

from decimal import Decimal

from pydantic import EmailStr, Field, computed_field, field_validator

from app.modules.users.roles import STAFF_ROLE_LABELS
from app.shared.base_schema import ORMSchema, TimestampedRead
from app.shared.enums import UserRole


class UserBase(ORMSchema):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    login: str | None = Field(default=None, min_length=3, max_length=100)
    staff_role_key: str | None = Field(default=None, max_length=30)
    rate: Decimal | None = Field(default=None, ge=0)
    role: UserRole = UserRole.MANAGER
    calendar_color: str = "#5C6BC0"
    duties: str | None = None
    ui_permissions: dict[str, bool] = Field(default_factory=dict)

    @field_validator("calendar_color")
    @classmethod
    def validate_calendar_color(cls, value: str) -> str:
        if len(value) != 7 or not value.startswith("#"):
            raise ValueError("calendar_color должен быть в формате #RRGGBB")
        try:
            int(value[1:], 16)
        except ValueError as exc:
            raise ValueError("calendar_color должен быть в формате #RRGGBB") from exc
        return value.upper()


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72)


class UserUpdate(ORMSchema):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    login: str | None = Field(default=None, min_length=3, max_length=100)
    staff_role_key: str | None = Field(default=None, max_length=30)
    rate: Decimal | None = Field(default=None, ge=0)
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=72)
    calendar_color: str | None = None
    duties: str | None = None
    ui_permissions: dict[str, bool] | None = None

    @field_validator("calendar_color")
    @classmethod
    def validate_calendar_color(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if len(value) != 7 or not value.startswith("#"):
            raise ValueError("calendar_color должен быть в формате #RRGGBB")
        try:
            int(value[1:], 16)
        except ValueError as exc:
            raise ValueError("calendar_color должен быть в формате #RRGGBB") from exc
        return value.upper()


class UserRead(TimestampedRead):
    email: EmailStr | None
    full_name: str
    phone: str | None
    login: str | None
    role: UserRole
    staff_role_key: str
    rate: Decimal | None
    is_owner: bool = Field(default=False, serialization_alias="isOwner")
    subscription_plan: str = Field(default="none", serialization_alias="subscriptionPlan")
    is_active: bool
    calendar_color: str
    duties: str | None
    ui_permissions: dict[str, bool]

    @computed_field
    @property
    def name(self) -> str:
        """Совместимое отображаемое имя для готовой admin-панели."""
        return self.full_name

    @computed_field(alias="roleLabel")
    @property
    def role_label(self) -> str:
        return STAFF_ROLE_LABELS.get(self.staff_role_key, self.role.value)

    @computed_field
    @property
    def access(self) -> dict[str, bool]:
        return self.ui_permissions

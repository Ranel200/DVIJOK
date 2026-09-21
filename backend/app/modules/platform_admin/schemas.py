"""Contracts for the creator/platform admin console."""

from decimal import Decimal
from typing import Any

from pydantic import EmailStr, Field

from app.shared.base_schema import StrictModel


class PlatformPlan(StrictModel):
    key: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(default=Decimal("0"), ge=0)
    description: str = ""
    features: list[str] = Field(default_factory=list)
    featured: bool = False


class PlatformExpense(StrictModel):
    category: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(ge=0)
    comment: str = ""
    date: str = ""


class PlatformLead(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    city: str = ""
    contact: str = ""
    phone: str = ""
    source: str = ""
    status: str = "Новый лид"
    created: str = ""


class PlatformEmployee(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = ""
    role: str = ""
    access: str = ""
    last: str = ""
    status: str = "Активен"


class PlatformAdminStateUpdate(StrictModel):
    plans: list[PlatformPlan] | None = None
    expenses: list[PlatformExpense] | None = None
    leads: list[PlatformLead] | None = None
    employees: list[PlatformEmployee] | None = None
    settings: dict[str, Any] | None = None


class PlatformServiceCreate(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    city: str = ""
    email: str = ""
    plan: str = "Стандарт"
    inn: str | None = Field(default=None, min_length=10, max_length=12)
    phone: str = Field(min_length=1, max_length=20)
    owner_name: str = Field(min_length=1, max_length=255)
    owner_email: EmailStr
    owner_login: str = Field(min_length=11, max_length=100)
    owner_password: str = Field(min_length=6, max_length=72)


class PlatformServiceUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    city: str | None = None
    email: str | None = None
    plan: str | None = None
    status: str | None = None
    note: str | None = None
    is_active: bool | None = None

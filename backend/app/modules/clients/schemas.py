"""Схемы модуля clients (ТЗ A5)."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.modules.vehicles.schemas import VehicleRead
from app.shared.base_schema import ORMSchema, TimestampedRead
from app.shared.enums import ClientType


class ClientBase(ORMSchema):
    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=5, max_length=20)
    email: EmailStr | None = None
    birth_date: date | None = None
    notes: str | None = None
    client_type: ClientType = ClientType.NEW
    marketing_consent: bool = False
    notifications_enabled: bool = True


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ORMSchema):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=5, max_length=20)
    email: EmailStr | None = None
    birth_date: date | None = None
    notes: str | None = None
    client_type: ClientType | None = None
    marketing_consent: bool | None = None
    notifications_enabled: bool | None = None
    is_active: bool | None = None


class ClientRead(TimestampedRead):
    full_name: str
    phone: str
    email: str | None
    birth_date: date | None
    notes: str | None
    client_type: ClientType
    balance: Decimal
    bonus_points: Decimal
    marketing_consent: bool
    notifications_enabled: bool
    is_active: bool


class ClientStats(BaseModel):
    """Агрегаты для таблицы и карточки клиента (ТЗ A5.2/A5.3)."""

    visits_count: int
    total_spent: Decimal
    last_visit: datetime | None


class ClientListItem(ClientRead):
    stats: ClientStats


class ClientDetail(ClientRead):
    stats: ClientStats
    vehicles: list[VehicleRead]

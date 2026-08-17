"""Базовые Pydantic-схемы (v2).

ORMSchema — чтение из ORM (from_attributes) + extra="forbid": лишние/неожиданные
поля в теле запроса отклоняются (защита от mass-assignment). StrictModel — то же
для входных схем, не привязанных к ORM.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Базовая схема ввода: запрещает необъявленные поля."""

    model_config = ConfigDict(extra="forbid")


class ORMSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class TimestampedRead(ORMSchema):
    id: int
    created_at: datetime
    updated_at: datetime

"""Пагинация: параметры запроса и обёртка ответа."""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    """Зависимость FastAPI для limit/offset (по умолчанию 50, максимум 200)."""

    def __init__(
        self,
        limit: int = Query(50, ge=1, le=200, description="Размер страницы"),
        offset: int = Query(0, ge=0, description="Смещение"),
    ) -> None:
        self.limit = limit
        self.offset = offset


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int

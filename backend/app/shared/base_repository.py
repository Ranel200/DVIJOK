"""Generic async-репозиторий: единый CRUD без дублирования по модулям."""

from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Доступ к данным одной модели, изолированный по организации (tenant scoping).

    Все запросы фильтруются по organization_id текущего пользователя — модуль не
    может ни прочитать, ни случайно привязать (через FK) сущность чужой организации.
    """

    model: type[ModelType]

    def __init__(self, session: AsyncSession, organization_id: int | None = None) -> None:
        """organization_id опционален только для auth-контура (поиск пользователя
        по email/id ещё до того, как известна его организация) — там используются
        отдельные unscoped-методы, не generic get/list/count ниже."""
        self.session = session
        self.organization_id = organization_id

    async def get(self, id_: int) -> ModelType | None:
        stmt = select(self.model).where(
            self.model.id == id_,  # type: ignore[attr-defined]
            self.model.organization_id == self.organization_id,  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        order_by: Any | None = None,
    ) -> list[ModelType]:
        stmt = select(self.model).where(
            self.model.organization_id == self.organization_id  # type: ignore[attr-defined]
        )
        stmt = stmt.order_by(
            order_by if order_by is not None else self.model.id.desc()  # type: ignore[attr-defined]
        )
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.organization_id == self.organization_id)  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def add(self, obj: ModelType) -> ModelType:
        if obj.organization_id is None:  # type: ignore[attr-defined]
            obj.organization_id = self.organization_id  # type: ignore[attr-defined]
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)
        await self.session.flush()

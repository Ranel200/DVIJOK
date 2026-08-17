"""Бизнес-логика модуля mechanics."""

from sqlalchemy import select

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.mechanics.models import Mechanic
from app.modules.mechanics.repository import MechanicRepository
from app.modules.mechanics.schemas import MechanicCreate, MechanicUpdate
from app.modules.users.models import User


class MechanicService:
    def __init__(self, repo: MechanicRepository) -> None:
        self.repo = repo

    async def get(self, mechanic_id: int) -> Mechanic:
        mechanic = await self.repo.get(mechanic_id)
        if mechanic is None:
            raise NotFoundError("Мастер не найден")
        return mechanic

    async def list_page(self, *, limit: int, offset: int) -> tuple[list[Mechanic], int]:
        items = await self.repo.list(limit=limit, offset=offset)
        total = await self.repo.count()
        return items, total

    async def _validate_user_link(self, user_id: int | None, exclude_id: int | None = None) -> None:
        if user_id is None:
            return
        stmt = select(User).where(
            User.id == user_id, User.organization_id == self.repo.organization_id
        )
        if (await self.repo.session.execute(stmt)).scalar_one_or_none() is None:
            raise NotFoundError("Пользователь для привязки не найден")
        linked = await self.repo.get_by_user_id(user_id)
        if linked and linked.id != exclude_id:
            raise ConflictError("Этот пользователь уже привязан к другому мастеру")

    async def create(self, data: MechanicCreate) -> Mechanic:
        await self._validate_user_link(data.user_id)
        payload = data.model_dump()
        payload["specializations"] = [s.value for s in data.specializations]
        return await self.repo.add(Mechanic(**payload))

    async def update(self, mechanic_id: int, data: MechanicUpdate) -> Mechanic:
        mechanic = await self.get(mechanic_id)
        payload = data.model_dump(exclude_unset=True)
        if "user_id" in payload:
            await self._validate_user_link(payload["user_id"], exclude_id=mechanic_id)
        if "specializations" in payload and payload["specializations"] is not None:
            payload["specializations"] = [
                s.value if hasattr(s, "value") else s for s in payload["specializations"]
            ]
        for field, value in payload.items():
            setattr(mechanic, field, value)
        return await self.repo.add(mechanic)

    async def delete(self, mechanic_id: int) -> None:
        await self.repo.delete(await self.get(mechanic_id))

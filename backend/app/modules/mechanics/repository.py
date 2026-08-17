"""Репозиторий модуля mechanics."""

from sqlalchemy import select

from app.modules.mechanics.models import Mechanic
from app.shared.base_repository import BaseRepository


class MechanicRepository(BaseRepository[Mechanic]):
    model = Mechanic

    async def get_by_user_id(self, user_id: int) -> Mechanic | None:
        result = await self.session.execute(
            select(Mechanic).where(
                Mechanic.user_id == user_id, Mechanic.organization_id == self.organization_id
            )
        )
        return result.scalar_one_or_none()

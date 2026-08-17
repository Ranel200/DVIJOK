"""Репозиторий модуля vehicles."""

from sqlalchemy import func, select

from app.modules.vehicles.models import Vehicle
from app.shared.base_repository import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
    model = Vehicle

    async def get_by_vin(self, vin: str) -> Vehicle | None:
        result = await self.session.execute(
            select(Vehicle).where(
                Vehicle.vin == vin, Vehicle.organization_id == self.organization_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_client(
        self, client_id: int, *, limit: int = 50, offset: int = 0
    ) -> tuple[list[Vehicle], int]:
        base = select(Vehicle).where(
            Vehicle.client_id == client_id, Vehicle.organization_id == self.organization_id
        )
        total = int(
            (
                await self.session.execute(select(func.count()).select_from(base.subquery()))
            ).scalar_one()
        )
        items = list(
            (
                await self.session.execute(
                    base.order_by(Vehicle.id.desc()).limit(limit).offset(offset)
                )
            )
            .scalars()
            .all()
        )
        return items, total

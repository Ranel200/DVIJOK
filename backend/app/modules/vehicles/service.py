"""Бизнес-логика модуля vehicles."""

from sqlalchemy import select

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.clients.models import Client
from app.modules.vehicles.models import Vehicle
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.schemas import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(self, repo: VehicleRepository) -> None:
        self.repo = repo

    async def get(self, vehicle_id: int) -> Vehicle:
        vehicle = await self.repo.get(vehicle_id)
        if vehicle is None:
            raise NotFoundError("Автомобиль не найден")
        return vehicle

    async def _ensure_client(self, client_id: int) -> None:
        stmt = select(Client).where(
            Client.id == client_id, Client.organization_id == self.repo.organization_id
        )
        if (await self.repo.session.execute(stmt)).scalar_one_or_none() is None:
            raise NotFoundError("Клиент не найден")

    async def _ensure_vin_free(self, vin: str | None, exclude_id: int | None = None) -> None:
        if not vin:
            return
        existing = await self.repo.get_by_vin(vin)
        if existing and existing.id != exclude_id:
            raise ConflictError("Автомобиль с таким VIN уже существует")

    async def list_for_client(
        self, client_id: int, *, limit: int, offset: int
    ) -> tuple[list[Vehicle], int]:
        return await self.repo.list_by_client(client_id, limit=limit, offset=offset)

    async def list_page(self, *, limit: int, offset: int) -> tuple[list[Vehicle], int]:
        items = await self.repo.list(limit=limit, offset=offset)
        total = await self.repo.count()
        return items, total

    async def create(self, data: VehicleCreate) -> Vehicle:
        await self._ensure_client(data.client_id)
        await self._ensure_vin_free(data.vin)
        return await self.repo.add(Vehicle(**data.model_dump()))

    async def update(self, vehicle_id: int, data: VehicleUpdate) -> Vehicle:
        vehicle = await self.get(vehicle_id)
        payload = data.model_dump(exclude_unset=True)
        if "vin" in payload:
            await self._ensure_vin_free(payload["vin"], exclude_id=vehicle_id)
        for field, value in payload.items():
            setattr(vehicle, field, value)
        return await self.repo.add(vehicle)

    async def delete(self, vehicle_id: int) -> None:
        await self.repo.delete(await self.get(vehicle_id))

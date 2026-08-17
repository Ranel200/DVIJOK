"""CRUD глобальных автомобилей клиента и безопасное владение ими."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.client_vehicles.models import ClientVehicle
from app.modules.client_vehicles.schemas import ClientVehicleInput, ClientVehicleRead


class ClientVehicleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _compact(value: str) -> str:
        return value.replace(" ", "").upper()

    @classmethod
    def _normalize_vehicle(cls, vehicle: ClientVehicle) -> None:
        vehicle.brand = vehicle.brand.strip()
        vehicle.model = vehicle.model.strip()
        vehicle.plate = vehicle.plate.strip().upper()
        vehicle.vin = cls._compact(vehicle.vin) if vehicle.vin else None
        vehicle.color = vehicle.color.strip() if vehicle.color else None

    async def list_owned(self, client_account_id: int) -> list[ClientVehicle]:
        stmt = (
            select(ClientVehicle)
            .where(ClientVehicle.client_account_id == client_account_id)
            .order_by(ClientVehicle.created_at, ClientVehicle.id)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_owned(self, vehicle_id: int, client_account_id: int) -> ClientVehicle:
        vehicle = await self.find_owned(vehicle_id, client_account_id)
        if vehicle is None:
            raise NotFoundError("Автомобиль не найден")
        return vehicle

    async def find_owned(
        self, vehicle_id: int, client_account_id: int
    ) -> ClientVehicle | None:
        stmt = select(ClientVehicle).where(
            ClientVehicle.id == vehicle_id,
            ClientVehicle.client_account_id == client_account_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def _get_by_vin(
        self, client_account_id: int, vin: str
    ) -> ClientVehicle | None:
        stmt = select(ClientVehicle).where(
            ClientVehicle.client_account_id == client_account_id,
            ClientVehicle.vin == self._compact(vin),
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create(
        self, client_account_id: int, data: ClientVehicleInput
    ) -> ClientVehicle:
        if await self._get_by_vin(client_account_id, data.vin) is not None:
            raise BusinessRuleError("Автомобиль с этим VIN уже добавлен")
        vehicle = ClientVehicle(
            client_account_id=client_account_id,
            **data.model_dump(by_alias=False),
        )
        self._normalize_vehicle(vehicle)
        self.session.add(vehicle)
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle

    async def update(
        self,
        vehicle_id: int,
        client_account_id: int,
        data: ClientVehicleInput,
    ) -> ClientVehicle:
        vehicle = await self.get_owned(vehicle_id, client_account_id)
        duplicate = await self._get_by_vin(client_account_id, data.vin)
        if duplicate is not None and duplicate.id != vehicle.id:
            raise BusinessRuleError("Автомобиль с этим VIN уже добавлен")
        for key, value in data.model_dump(by_alias=False).items():
            setattr(vehicle, key, value)
        self._normalize_vehicle(vehicle)
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle

    async def get_or_create_from_booking(
        self,
        *,
        client_account_id: int,
        brand: str,
        model: str,
        plate: str,
        plate_type: str,
    ) -> ClientVehicle:
        normalized_plate = plate.strip().upper()
        stmt = select(ClientVehicle).where(
            ClientVehicle.client_account_id == client_account_id,
            ClientVehicle.plate == normalized_plate,
        )
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing is not None:
            return existing
        vehicle = ClientVehicle(
            client_account_id=client_account_id,
            brand=brand,
            model=model,
            plate=normalized_plate,
            plate_type=plate_type,
            vin=None,
            year=None,
            color=None,
            mileage=None,
        )
        self._normalize_vehicle(vehicle)
        self.session.add(vehicle)
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle

    @staticmethod
    def read(vehicle: ClientVehicle) -> ClientVehicleRead:
        return ClientVehicleRead(
            id=str(vehicle.id),
            brand=vehicle.brand,
            model=vehicle.model,
            plate=vehicle.plate,
            plate_type=vehicle.plate_type,
            vin=vehicle.vin or "",
            year=vehicle.year,
            color=vehicle.color or "",
            mileage=vehicle.mileage,
        )

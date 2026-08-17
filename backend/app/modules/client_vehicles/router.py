"""Точные endpoint'ы автомобилей, используемые клиентским frontend."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_client
from app.modules.client_auth.models import ClientAccount
from app.modules.client_portal.schemas import ClientCarsRead
from app.modules.client_portal.service import ClientPortalService
from app.modules.client_vehicles.schemas import ClientVehicleInput, ClientVehicleRead
from app.modules.client_vehicles.service import ClientVehicleService

router = APIRouter(
    prefix="/cars",
    tags=["client-cars"],
    dependencies=[Depends(get_current_client)],
)


def get_client_vehicle_service(
    db: AsyncSession = Depends(get_db, scope="function"),
) -> ClientVehicleService:
    return ClientVehicleService(db)


@router.get("", response_model=ClientCarsRead)
async def list_cars(
    client_account: ClientAccount = Depends(get_current_client),
    db: AsyncSession = Depends(get_db, scope="function"),
) -> ClientCarsRead:
    return await ClientPortalService(db).frontend_cars(client_account.id)


@router.get("/{vehicle_id}", response_model=ClientVehicleRead)
async def get_car(
    vehicle_id: int,
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientVehicleService = Depends(get_client_vehicle_service),
) -> ClientVehicleRead:
    vehicle = await service.get_owned(vehicle_id, client_account.id)
    return service.read(vehicle)


@router.post("", response_model=ClientVehicleRead, status_code=status.HTTP_201_CREATED)
async def create_car(
    payload: ClientVehicleInput,
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientVehicleService = Depends(get_client_vehicle_service),
) -> ClientVehicleRead:
    vehicle = await service.create(client_account.id, payload)
    return service.read(vehicle)


@router.put("/{vehicle_id}", response_model=ClientVehicleRead)
async def update_car(
    vehicle_id: int,
    payload: ClientVehicleInput,
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientVehicleService = Depends(get_client_vehicle_service),
) -> ClientVehicleRead:
    vehicle = await service.update(vehicle_id, client_account.id, payload)
    return service.read(vehicle)

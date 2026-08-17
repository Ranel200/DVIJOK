"""HTTP-роутер модуля vehicles. Доступ: ADMIN и MANAGER."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.core.pagination import Page, PaginationParams
from app.modules.users.models import User
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.schemas import VehicleCreate, VehicleRead, VehicleUpdate
from app.modules.vehicles.service import VehicleService
from app.shared.enums import UserRole

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))],
)


def get_vehicle_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> VehicleService:
    return VehicleService(VehicleRepository(db, current_user.organization_id))


@router.get("", response_model=Page[VehicleRead])
async def list_vehicles(
    pagination: PaginationParams = Depends(),
    client_id: int | None = Query(default=None, description="Фильтр по клиенту"),
    service: VehicleService = Depends(get_vehicle_service),
) -> Page[VehicleRead]:
    if client_id is not None:
        items, total = await service.list_for_client(
            client_id, limit=pagination.limit, offset=pagination.offset
        )
    else:
        items, total = await service.list_page(limit=pagination.limit, offset=pagination.offset)
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    payload: VehicleCreate, service: VehicleService = Depends(get_vehicle_service)
) -> VehicleRead:
    return await service.create(payload)


@router.get("/{vehicle_id}", response_model=VehicleRead)
async def get_vehicle(
    vehicle_id: int, service: VehicleService = Depends(get_vehicle_service)
) -> VehicleRead:
    return await service.get(vehicle_id)


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: int, payload: VehicleUpdate, service: VehicleService = Depends(get_vehicle_service)
) -> VehicleRead:
    return await service.update(vehicle_id, payload)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: int, service: VehicleService = Depends(get_vehicle_service)
) -> None:
    await service.delete(vehicle_id)

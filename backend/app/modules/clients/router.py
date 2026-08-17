"""HTTP-роутер модуля clients. Доступ: ADMIN и MANAGER (механику база клиентов
недоступна — ТЗ A1)."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.core.pagination import Page, PaginationParams
from app.modules.clients.repository import ClientRepository
from app.modules.clients.schemas import (
    ClientCreate,
    ClientDetail,
    ClientListItem,
    ClientRead,
    ClientUpdate,
)
from app.modules.clients.service import ClientService
from app.modules.users.models import User
from app.modules.vehicles.schemas import VehicleRead
from app.shared.enums import ClientType, UserRole

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))],
)


def get_client_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> ClientService:
    return ClientService(ClientRepository(db, current_user.organization_id))


@router.get("", response_model=Page[ClientListItem])
async def list_clients(
    pagination: PaginationParams = Depends(),
    query: str | None = Query(default=None, description="Поиск: имя / телефон / авто"),
    client_type: ClientType | None = Query(default=None, description="Фильтр по типу"),
    service: ClientService = Depends(get_client_service),
) -> Page[ClientListItem]:
    enriched, total = await service.list_page(
        query=query, client_type=client_type, limit=pagination.limit, offset=pagination.offset
    )
    items = [
        ClientListItem(**ClientRead.model_validate(client).model_dump(), stats=stats)
        for client, stats in enriched
    ]
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate, service: ClientService = Depends(get_client_service)
) -> ClientRead:
    return await service.create(payload)


@router.get("/{client_id}", response_model=ClientDetail)
async def get_client(
    client_id: int, service: ClientService = Depends(get_client_service)
) -> ClientDetail:
    client, stats = await service.get_detail(client_id)
    return ClientDetail(
        **ClientRead.model_validate(client).model_dump(),
        stats=stats,
        vehicles=[VehicleRead.model_validate(v) for v in client.vehicles],
    )


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: int, payload: ClientUpdate, service: ClientService = Depends(get_client_service)
) -> ClientRead:
    return await service.update(client_id, payload)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int, service: ClientService = Depends(get_client_service)
) -> None:
    await service.delete(client_id)

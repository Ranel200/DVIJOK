"""Бизнес-логика модуля clients."""

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.clients.models import Client
from app.modules.clients.repository import ClientRepository
from app.modules.clients.schemas import ClientCreate, ClientStats, ClientUpdate
from app.shared.enums import ClientType


class ClientService:
    def __init__(self, repo: ClientRepository) -> None:
        self.repo = repo

    async def get(self, client_id: int) -> Client:
        client = await self.repo.get(client_id)
        if client is None:
            raise NotFoundError("Клиент не найден")
        return client

    async def _stats(self, client_id: int) -> ClientStats:
        visits, total, last = await self.repo.stats(client_id)
        return ClientStats(visits_count=visits, total_spent=total, last_visit=last)

    async def list_page(
        self,
        *,
        query: str | None,
        client_type: ClientType | None,
        limit: int,
        offset: int,
    ) -> tuple[list[tuple[Client, ClientStats]], int]:
        clients, total = await self.repo.search(
            query=query, client_type=client_type, limit=limit, offset=offset
        )
        enriched = [(c, await self._stats(c.id)) for c in clients]
        return enriched, total

    async def get_detail(self, client_id: int) -> tuple[Client, ClientStats]:
        client = await self.repo.get_with_vehicles(client_id)
        if client is None:
            raise NotFoundError("Клиент не найден")
        return client, await self._stats(client_id)

    async def create(self, data: ClientCreate) -> Client:
        if await self.repo.get_by_phone(data.phone):
            raise ConflictError("Клиент с таким телефоном уже существует")
        return await self.repo.add(Client(**data.model_dump()))

    async def update(self, client_id: int, data: ClientUpdate) -> Client:
        client = await self.get(client_id)
        payload = data.model_dump(exclude_unset=True)
        if "phone" in payload and payload["phone"] != client.phone:
            existing = await self.repo.get_by_phone(payload["phone"])
            if existing and existing.id != client_id:
                raise ConflictError("Телефон занят другим клиентом")
        for field, value in payload.items():
            setattr(client, field, value)
        return await self.repo.add(client)

    async def delete(self, client_id: int) -> None:
        await self.repo.delete(await self.get(client_id))

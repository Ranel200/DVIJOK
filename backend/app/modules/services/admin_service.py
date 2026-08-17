"""Mapping between UI service cards and the domain service catalog."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select

from app.core.exceptions import NotFoundError
from app.modules.mechanics.models import Mechanic
from app.modules.orders.models import Order, OrderItem
from app.modules.services.admin_schemas import (
    AdminServiceRead,
    AdminServiceWrite,
    ServiceMasterBrief,
)
from app.modules.services.models import Service
from app.modules.services.repository import ServiceRepository
from app.modules.services.schemas import ServiceCreate, ServiceUpdate
from app.modules.services.service import ServiceCatalogService
from app.shared.enums import OrderStatus, ServiceCategory, ServicePriceType

_CATEGORY_FROM_UI = {
    "maintenance": ServiceCategory.TO,
    "diagnostics": ServiceCategory.DIAGNOSTICS,
    "repair": ServiceCategory.OTHER,
    "body": ServiceCategory.BODY,
    "other": ServiceCategory.OTHER,
}
_CATEGORY_TO_UI = {
    ServiceCategory.TO: "maintenance",
    ServiceCategory.DIAGNOSTICS: "diagnostics",
    ServiceCategory.BODY: "body",
}


class AdminServiceCatalog:
    def __init__(self, repo: ServiceRepository) -> None:
        self.repo = repo
        self.session = repo.session
        self.organization_id = repo.organization_id
        self.catalog = ServiceCatalogService(repo)

    async def _order_counts(self) -> dict[int, int]:
        rows = (
            await self.session.execute(
                select(OrderItem.service_id, func.count(OrderItem.id))
                .join(Order, Order.id == OrderItem.order_id)
                .where(
                    OrderItem.organization_id == self.organization_id,
                    OrderItem.service_id.is_not(None),
                    Order.status != OrderStatus.CANCELLED,
                )
                .group_by(OrderItem.service_id)
            )
        ).all()
        return {service_id: int(count) for service_id, count in rows}

    @staticmethod
    def _master(mechanic: Mechanic) -> ServiceMasterBrief:
        return ServiceMasterBrief(
            id=mechanic.user_id or mechanic.id,
            name=mechanic.full_name,
            role="Мастер",
        )

    @staticmethod
    def _price_note(service: Service) -> str:
        if service.price_type == ServicePriceType.NEGOTIABLE:
            return "договорная"
        if service.price_type == ServicePriceType.RANGE:
            if service.price_to is not None and service.price_to > service.base_price:
                return f"{service.base_price}–{service.price_to} ₽"
            return f"от {service.base_price} ₽"
        return "фиксированная"

    def _read(self, service: Service, count: int) -> AdminServiceRead:
        masters = [self._master(mechanic) for mechanic in service.mechanics]
        return AdminServiceRead(
            id=service.id,
            title=service.name,
            description=service.description or "",
            category=service.admin_category or _CATEGORY_TO_UI.get(service.category, "repair"),
            price_type=service.price_type.value,
            price=service.base_price,
            price_to=service.price_to,
            price_note=self._price_note(service),
            duration_hours=(Decimal(service.duration_minutes) / Decimal(60)),
            orders_count=count,
            status="active" if service.is_active else "hidden",
            master=masters[0] if masters else None,
            masters=masters,
            notes=service.internal_notes or "",
        )

    async def list(self) -> list[AdminServiceRead]:
        services, _ = await self.catalog.list_page(
            query=None,
            category=None,
            active_only=False,
            limit=200,
            offset=0,
        )
        counts = await self._order_counts()
        return [self._read(service, counts.get(service.id, 0)) for service in services]

    async def masters(self) -> list[ServiceMasterBrief]:
        mechanics = list(
            (
                await self.session.execute(
                    select(Mechanic)
                    .where(
                        Mechanic.organization_id == self.organization_id,
                        Mechanic.is_active.is_(True),
                        Mechanic.user_id.is_not(None),
                    )
                    .order_by(Mechanic.full_name)
                )
            )
            .scalars()
            .all()
        )
        return [self._master(mechanic) for mechanic in mechanics]

    async def get(self, service_id: int) -> AdminServiceRead:
        service = await self.catalog.get(service_id)
        counts = await self._order_counts()
        return self._read(service, counts.get(service.id, 0))

    async def _mechanic_ids(self, values: list[int | str]) -> list[int]:
        user_ids = {int(value) for value in values if value != "all"}
        if not user_ids:
            return []
        mechanics = list(
            (
                await self.session.execute(
                    select(Mechanic).where(
                        Mechanic.organization_id == self.organization_id,
                        Mechanic.user_id.in_(user_ids),
                        Mechanic.is_active.is_(True),
                    )
                )
            )
            .scalars()
            .all()
        )
        if {item.user_id for item in mechanics} != user_ids:
            raise NotFoundError("Один или несколько мастеров не найдены")
        by_user = {item.user_id: item.id for item in mechanics}
        return [by_user[user_id] for user_id in user_ids]

    @staticmethod
    def _duration_minutes(data: AdminServiceWrite) -> int:
        value = data.duration * (60 if data.duration_unit == "hours" else 1)
        return max(1, int(value))

    async def create(self, data: AdminServiceWrite) -> AdminServiceRead:
        category = _CATEGORY_FROM_UI.get(data.category)
        if category is None:
            raise NotFoundError("Категория услуги не найдена")
        price_type = ServicePriceType(data.price_type)
        service = await self.catalog.create(
            ServiceCreate(
                name=data.title,
                category=category,
                description=data.description or None,
                base_price=data.price,
                price_type=price_type,
                price_to=(data.price_to or data.price)
                if price_type == ServicePriceType.RANGE
                else None,
                internal_notes=data.notes or None,
                mechanic_ids=await self._mechanic_ids(data.masters),
                duration_minutes=self._duration_minutes(data),
                is_active=data.status == "active",
            )
        )
        service.admin_category = data.category
        await self.session.flush()
        return self._read(service, 0)

    async def update(self, service_id: int, data: AdminServiceWrite) -> AdminServiceRead:
        category = _CATEGORY_FROM_UI.get(data.category)
        if category is None:
            raise NotFoundError("Категория услуги не найдена")
        price_type = ServicePriceType(data.price_type)
        service = await self.catalog.update(
            service_id,
            ServiceUpdate(
                name=data.title,
                category=category,
                description=data.description or None,
                base_price=data.price,
                price_type=price_type,
                price_to=(data.price_to or data.price)
                if price_type == ServicePriceType.RANGE
                else None,
                internal_notes=data.notes or None,
                mechanic_ids=await self._mechanic_ids(data.masters),
                duration_minutes=self._duration_minutes(data),
                is_active=data.status == "active",
            ),
        )
        service.admin_category = data.category
        await self.session.flush()
        counts = await self._order_counts()
        return self._read(service, counts.get(service.id, 0))

    async def delete(self, service_id: int) -> None:
        await self.catalog.delete(service_id)

    async def delete_many(self, ids: list[int]) -> None:
        for service_id in list(dict.fromkeys(ids)):
            await self.delete(service_id)

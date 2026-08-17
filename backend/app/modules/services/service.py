"""Бизнес-логика модуля services."""

import datetime as dt
from decimal import Decimal

from sqlalchemy import func, select

from app.core.config import settings
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.mechanics.models import Mechanic
from app.modules.orders.models import Order, OrderItem
from app.modules.organizations.models import Organization
from app.modules.services.importer import normalize_name, parse_workbook
from app.modules.services.models import Service
from app.modules.services.repository import ServiceRepository
from app.modules.services.schemas import (
    PopularService,
    ServiceCreate,
    ServiceImportError,
    ServiceImportReport,
    ServiceSummary,
    ServiceUpdate,
)
from app.shared.enums import OrderStatus, ServiceCategory, ServicePriceType


class ServiceCatalogService:
    def __init__(self, repo: ServiceRepository) -> None:
        self.repo = repo

    async def get(self, service_id: int) -> Service:
        service = await self.repo.get(service_id)
        if service is None:
            raise NotFoundError("Услуга не найдена")
        return service

    async def list_page(
        self,
        *,
        query: str | None,
        category: ServiceCategory | None,
        active_only: bool,
        limit: int,
        offset: int,
    ) -> tuple[list[Service], int]:
        return await self.repo.search(
            query=query,
            category=category,
            active_only=active_only,
            limit=limit,
            offset=offset,
        )

    async def create(self, data: ServiceCreate) -> Service:
        payload = data.model_dump()
        mechanic_ids = payload.pop("mechanic_ids")
        service = Service(**payload)
        service.mechanics = await self._resolve_mechanics(mechanic_ids)
        return await self.repo.add(service)

    async def update(self, service_id: int, data: ServiceUpdate) -> Service:
        service = await self.get(service_id)
        payload = data.model_dump(exclude_unset=True)
        mechanic_ids = payload.pop("mechanic_ids", None)
        for field, value in payload.items():
            setattr(service, field, value)
        if service.price_type == ServicePriceType.RANGE:
            if service.price_to is None or service.price_to < service.base_price:
                raise BusinessRuleError("Для диапазона price_to должен быть не меньше base_price")
        if mechanic_ids is not None:
            service.mechanics = await self._resolve_mechanics(mechanic_ids)
        return await self.repo.add(service)

    async def _resolve_mechanics(self, mechanic_ids: list[int]) -> list[Mechanic]:
        unique_ids = list(dict.fromkeys(mechanic_ids))
        if not unique_ids:
            return []
        mechanics = list(
            (
                await self.repo.session.execute(
                    select(Mechanic).where(
                        Mechanic.organization_id == self.repo.organization_id,
                        Mechanic.id.in_(unique_ids),
                    )
                )
            )
            .scalars()
            .all()
        )
        if len(mechanics) != len(unique_ids):
            raise NotFoundError("Один или несколько мастеров не найдены")
        by_id = {mechanic.id: mechanic for mechanic in mechanics}
        return [by_id[id_] for id_ in unique_ids]

    async def summary(self) -> ServiceSummary:
        session = self.repo.session
        organization_id = self.repo.organization_id
        month_ago = dt.datetime.now(dt.UTC) - dt.timedelta(days=30)
        # TimestampMixin stores created_at as a timezone-naive timestamp, while
        # Order.completed_at is timezone-aware.  asyncpg rejects an aware value
        # bound to the former, so each comparison must use the matching shape.
        created_month_ago = month_ago.replace(tzinfo=None)
        total_services = int(
            (
                await session.execute(
                    select(func.count(Service.id)).where(Service.organization_id == organization_id)
                )
            ).scalar_one()
        )
        average_check = Decimal(
            (
                await session.execute(
                    select(func.coalesce(func.avg(Order.total_amount), 0)).where(
                        Order.organization_id == organization_id,
                        Order.status != OrderStatus.CANCELLED,
                    )
                )
            ).scalar_one()
        )
        popular_row = (
            await session.execute(
                select(Service.name, func.count(OrderItem.id).label("orders_count"))
                .join(OrderItem, OrderItem.service_id == Service.id)
                .join(Order, Order.id == OrderItem.order_id)
                .where(
                    Service.organization_id == organization_id,
                    Order.created_at >= created_month_ago,
                    Order.status != OrderStatus.CANCELLED,
                )
                .group_by(Service.id, Service.name)
                .order_by(func.count(OrderItem.id).desc(), Service.name)
                .limit(1)
            )
        ).first()
        revenue = Decimal(
            (
                await session.execute(
                    select(func.coalesce(func.sum(Order.total_amount), 0)).where(
                        Order.organization_id == organization_id,
                        Order.status == OrderStatus.DONE,
                        Order.completed_at >= month_ago,
                    )
                )
            ).scalar_one()
        )
        active_masters = int(
            (
                await session.execute(
                    select(func.count(Mechanic.id)).where(
                        Mechanic.organization_id == organization_id,
                        Mechanic.is_active.is_(True),
                    )
                )
            ).scalar_one()
        )
        return ServiceSummary(
            total_services=total_services,
            average_check=average_check,
            popular_service=(
                PopularService(name=popular_row[0], orders_per_month=int(popular_row[1]))
                if popular_row
                else None
            ),
            revenue_per_month=revenue,
            active_masters=active_masters,
        )

    async def delete(self, service_id: int) -> None:
        await self.repo.delete(await self.get(service_id))

    async def _existing_names(self) -> set[str]:
        result = await self.repo.session.execute(
            select(Service.name).where(Service.organization_id == self.repo.organization_id)
        )
        return {normalize_name(name) for name in result.scalars().all()}

    async def preview_import(
        self,
        data: bytes,
        filename: str | None,
    ) -> ServiceImportReport:
        if not filename or not filename.casefold().endswith(".xlsx"):
            return ServiceImportReport(
                valid=False,
                total_rows=0,
                valid_rows=0,
                errors=[
                    ServiceImportError(
                        field="file",
                        message="Поддерживаются только файлы .xlsx",
                    )
                ],
                rows=[],
            )
        if len(data) > settings.SERVICE_IMPORT_MAX_FILE_BYTES:
            return ServiceImportReport(
                valid=False,
                total_rows=0,
                valid_rows=0,
                errors=[
                    ServiceImportError(
                        field="file",
                        message=(
                            f"Размер файла превышает {settings.SERVICE_IMPORT_MAX_FILE_BYTES} байт"
                        ),
                    )
                ],
                rows=[],
            )
        return parse_workbook(data, await self._existing_names()).report

    async def apply_import(
        self,
        data: bytes,
        filename: str | None,
    ) -> ServiceImportReport:
        # Serialize imports for one tenant, then validate again against the
        # current catalog. Preview is advisory; apply is the source of truth.
        await self.repo.session.execute(
            select(Organization)
            .where(Organization.id == self.repo.organization_id)
            .with_for_update()
        )
        report = await self.preview_import(data, filename)
        if not report.valid:
            return report
        for row in report.rows:
            self.repo.session.add(
                Service(
                    organization_id=self.repo.organization_id,
                    name=row.name,
                    category=ServiceCategory.OTHER,
                    admin_category="other",
                    description=None,
                    base_price=row.base_price,
                    price_type=ServicePriceType.FIXED,
                    price_to=None,
                    internal_notes=None,
                    labor_hours=0,
                    duration_minutes=60,
                    is_active=True,
                )
            )
        await self.repo.session.flush()
        report.imported_rows = len(report.rows)
        return report

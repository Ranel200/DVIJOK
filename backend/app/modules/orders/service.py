"""Бизнес-логика модуля orders: статусная машина, позиции, пересчёт суммы.

Позиции не загружаются лениво (async): при создании сумма считается из локального
списка, при изменении заказ перечитывается с selectinload(items).
"""

import datetime as dt
import hashlib
import html
import math
import re
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.clients.models import Client
from app.modules.clients.repository import ClientRepository
from app.modules.inventory.models import InventoryItem
from app.modules.mechanics.models import Mechanic
from app.modules.notifications.service import NotificationService
from app.modules.orders.models import Order, OrderDocument, OrderItem
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderCreate,
    OrderIntakeCreate,
    OrderItemCreate,
    OrderUpdate,
)
from app.modules.organizations.models import Organization
from app.modules.services.models import Service
from app.modules.users.models import User
from app.modules.vehicles.models import Vehicle
from app.modules.vehicles.repository import VehicleRepository
from app.shared.enums import OrderDocumentSource, OrderItemType, OrderStatus, UserRole

# Допустимые переходы статусов заказ-наряда (ТЗ A3.3).
ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.NEW: {
        OrderStatus.PRIMARY,
        OrderStatus.DIAGNOSTICS,
        OrderStatus.APPROVAL,
        OrderStatus.SECONDARY,
        OrderStatus.WAITING,
        OrderStatus.IN_PROGRESS,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PRIMARY: {
        OrderStatus.DIAGNOSTICS,
        OrderStatus.APPROVAL,
        OrderStatus.WAITING,
        OrderStatus.IN_PROGRESS,
        OrderStatus.CANCELLED,
    },
    OrderStatus.DIAGNOSTICS: {
        OrderStatus.APPROVAL,
        OrderStatus.SECONDARY,
        OrderStatus.WAITING,
        OrderStatus.IN_PROGRESS,
        OrderStatus.CANCELLED,
    },
    OrderStatus.APPROVAL: {
        OrderStatus.SECONDARY,
        OrderStatus.WAITING,
        OrderStatus.IN_PROGRESS,
        OrderStatus.DONE,
        OrderStatus.CANCELLED,
    },
    OrderStatus.SECONDARY: {
        OrderStatus.WAITING,
        OrderStatus.IN_PROGRESS,
        OrderStatus.CANCELLED,
    },
    OrderStatus.WAITING: {OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED},
    OrderStatus.IN_PROGRESS: {
        OrderStatus.WAITING,
        OrderStatus.AGREEMENT,
        OrderStatus.DONE,
        OrderStatus.CANCELLED,
    },
    OrderStatus.AGREEMENT: {OrderStatus.DONE, OrderStatus.CANCELLED},
    OrderStatus.DONE: set(),
    OrderStatus.CANCELLED: set(),
}

_EDITABLE_STATUSES = {
    OrderStatus.NEW,
    OrderStatus.PRIMARY,
    OrderStatus.DIAGNOSTICS,
    OrderStatus.APPROVAL,
    OrderStatus.SECONDARY,
    OrderStatus.WAITING,
    OrderStatus.IN_PROGRESS,
    OrderStatus.AGREEMENT,
}
MAX_DOCUMENT_SIZE_BYTES = 2 * 1024 * 1024
MAX_DOCUMENTS_PER_UPLOAD = 10
_UPLOAD_TYPES = {
    "application/pdf": {".pdf"},
    "text/html": {".html", ".htm"},
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
    "image/gif": {".gif"},
}


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class OrderService:
    def __init__(self, repo: OrderRepository, current_user: User | None = None) -> None:
        self.repo = repo
        self.session = repo.session
        self.organization_id = repo.organization_id
        self.current_user = current_user

    async def _next_order_number(self) -> str:
        organization = (
            await self.session.execute(
                select(Organization)
                .where(Organization.id == self.organization_id)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if organization is None:
            raise NotFoundError("Организация не найдена")
        number = organization.next_order_number
        organization.next_order_number += 1
        return str(number)

    async def _ensure_access(self, order: Order) -> None:
        if self.current_user is None or self.current_user.role != UserRole.MECHANIC:
            return
        mechanic_id = (
            await self.session.execute(
                select(Mechanic.id).where(
                    Mechanic.organization_id == self.organization_id,
                    Mechanic.user_id == self.current_user.id,
                )
            )
        ).scalar_one_or_none()
        if mechanic_id is None or order.mechanic_id != mechanic_id:
            raise NotFoundError("Заказ не найден")

    async def get(self, order_id: int) -> Order:
        order = await self.repo.get_with_relations(order_id)
        if order is None:
            raise NotFoundError("Заказ не найден")
        await self._ensure_access(order)
        return order

    async def lock(self, order_id: int) -> Order:
        stmt = (
            select(Order)
            .where(
                Order.id == order_id,
                Order.organization_id == self.organization_id,
            )
            .with_for_update()
        )
        order = (await self.session.execute(stmt)).scalar_one_or_none()
        if order is None:
            raise NotFoundError("Заказ не найден")
        await self._ensure_access(order)
        return order

    async def appointment_duration(
        self,
        order_id: int,
        explicit_minutes: int | None = None,
    ) -> int:
        if explicit_minutes is not None:
            return explicit_minutes
        order = await self.get(order_id)
        service_ids = [
            item.service_id
            for item in order.items
            if item.item_type == OrderItemType.SERVICE and item.service_id is not None
        ]
        if not service_ids:
            return settings.DEFAULT_APPOINTMENT_DURATION_MINUTES
        services = list(
            (
                await self.session.execute(
                    select(Service).where(
                        Service.id.in_(service_ids),
                        Service.organization_id == self.organization_id,
                    )
                )
            )
            .scalars()
            .all()
        )
        durations = {service.id: service.duration_minutes for service in services}
        total = sum(
            durations.get(item.service_id, 0) * float(item.quantity)
            for item in order.items
            if item.service_id is not None
        )
        return max(1, math.ceil(total)) or settings.DEFAULT_APPOINTMENT_DURATION_MINUTES

    async def list_page(
        self, *, status, source, mechanic_id, query, limit, offset
    ) -> tuple[list[Order], int]:
        return await self.repo.search(
            status=status,
            source=source,
            mechanic_id=mechanic_id,
            query=query,
            limit=limit,
            offset=offset,
        )

    async def _build_item(self, order_id: int, data: OrderItemCreate) -> OrderItem:
        description = data.description
        unit_price = data.unit_price
        labor_hours = data.labor_hours
        service_id: int | None = None
        inventory_item_id: int | None = None

        if data.mechanic_id is not None:
            mechanic = (
                await self.session.execute(
                    select(Mechanic).where(
                        Mechanic.id == data.mechanic_id,
                        Mechanic.organization_id == self.organization_id,
                        Mechanic.is_active.is_(True),
                    )
                )
            ).scalar_one_or_none()
            if mechanic is None:
                raise NotFoundError("Мастер не найден")

        if data.item_type == OrderItemType.SERVICE:
            if data.service_id is None:
                raise BusinessRuleError("Для услуги обязателен service_id")
            service = (
                await self.session.execute(
                    select(Service).where(
                        Service.id == data.service_id,
                        Service.organization_id == self.organization_id,
                    )
                )
            ).scalar_one_or_none()
            if service is None:
                raise NotFoundError("Услуга не найдена")
            service_id = service.id
            description = description or service.name
            unit_price = service.base_price if unit_price is None else unit_price
            labor_hours = service.labor_hours if labor_hours is None else labor_hours
        else:
            if data.inventory_item_id is None:
                raise BusinessRuleError("Для запчасти обязателен inventory_item_id")
            part = (
                await self.session.execute(
                    select(InventoryItem).where(
                        InventoryItem.id == data.inventory_item_id,
                        InventoryItem.organization_id == self.organization_id,
                    )
                )
            ).scalar_one_or_none()
            if part is None:
                raise NotFoundError("Складская позиция не найдена")
            inventory_item_id = part.id
            description = description or part.name
            unit_price = part.sale_price if unit_price is None else unit_price

        unit_price = unit_price or Decimal(0)
        discount_multiplier = (Decimal(100) - data.discount_percent) / Decimal(100)
        item = OrderItem(
            organization_id=self.organization_id,
            order_id=order_id,
            item_type=data.item_type,
            service_id=service_id,
            inventory_item_id=inventory_item_id,
            mechanic_id=data.mechanic_id,
            description=description or "—",
            quantity=data.quantity,
            unit_price=unit_price,
            discount_percent=data.discount_percent,
            labor_hours=labor_hours,
            total_price=(unit_price * data.quantity * discount_multiplier).quantize(
                Decimal("0.01")
            ),
        )
        return item

    async def _validate_refs(
        self, client_id: int | None, vehicle_id: int | None, mechanic_id: int | None
    ) -> None:
        if client_id is not None:
            client = (
                await self.session.execute(
                    select(Client).where(
                        Client.id == client_id,
                        Client.organization_id == self.organization_id,
                    )
                )
            ).scalar_one_or_none()
            if client is None:
                raise NotFoundError("Клиент не найден")
        if vehicle_id is not None:
            vehicle = (
                await self.session.execute(
                    select(Vehicle).where(
                        Vehicle.id == vehicle_id,
                        Vehicle.organization_id == self.organization_id,
                    )
                )
            ).scalar_one_or_none()
            if vehicle is None:
                raise NotFoundError("Автомобиль не найден")
            if (
                client_id is not None
                and vehicle.client_id is not None
                and vehicle.client_id != client_id
            ):
                raise BusinessRuleError("Автомобиль не принадлежит указанному клиенту")
        if mechanic_id is not None:
            mechanic = (
                await self.session.execute(
                    select(Mechanic).where(
                        Mechanic.id == mechanic_id,
                        Mechanic.organization_id == self.organization_id,
                    )
                )
            ).scalar_one_or_none()
            if mechanic is None:
                raise NotFoundError("Мастер не найден")

    async def create(self, data: OrderCreate, created_by_id: int | None) -> Order:
        await self._validate_refs(data.client_id, data.vehicle_id, data.mechanic_id)
        order = Order(
            organization_id=self.organization_id,
            number=await self._next_order_number(),
            client_id=data.client_id,
            vehicle_id=data.vehicle_id,
            mechanic_id=data.mechanic_id,
            created_by_id=created_by_id,
            source=data.source,
            comment=data.comment,
            mileage=data.mileage,
            scheduled_at=data.scheduled_at,
            status=OrderStatus.NEW,
        )
        self.session.add(order)
        await self.session.flush()

        total = Decimal(0)
        for item_data in data.items:
            item = await self._build_item(order.id, item_data)
            self.session.add(item)
            total += item.total_price
        order.total_amount = total
        await self.session.flush()
        created = await self.get(order.id)
        await NotificationService(self.session).enqueue_order_status(created)
        return created

    async def create_intake(self, data: OrderIntakeCreate, created_by_id: int | None) -> Order:
        """Создаёт клиентскую карточку, автомобиль и заказ в одной транзакции.

        Время и мастер здесь намеренно не назначаются: пользователь сначала
        получает предложения availability, затем явно резервирует выбранный slot.
        """
        client_repo = ClientRepository(self.session, self.organization_id)
        if data.client_id is not None:
            client = await client_repo.get(data.client_id)
            if client is None:
                raise NotFoundError("Клиент не найден")
        else:
            assert data.client is not None
            normalized_phone = data.client.phone.strip()
            client = await client_repo.get_by_phone(normalized_phone)
            if client is None:
                client = await client_repo.add(
                    Client(
                        organization_id=self.organization_id,
                        full_name=data.client.full_name.strip(),
                        phone=normalized_phone,
                        email=str(data.client.email) if data.client.email else None,
                    )
                )

        vehicle_repo = VehicleRepository(self.session, self.organization_id)
        if data.vehicle_id is not None:
            vehicle = await vehicle_repo.get(data.vehicle_id)
            if vehicle is None:
                raise NotFoundError("Автомобиль не найден")
        else:
            assert data.vehicle is not None
            vehicle = None
            if data.vehicle.vin:
                vehicle = await vehicle_repo.get_by_vin(data.vehicle.vin.strip())
            if vehicle is None:
                vehicle = await vehicle_repo.add(
                    Vehicle(
                        organization_id=self.organization_id,
                        client_id=client.id,
                        make=data.vehicle.make.strip(),
                        model=data.vehicle.model.strip(),
                        year=data.vehicle.year,
                        license_plate=(
                            data.vehicle.license_plate.strip()
                            if data.vehicle.license_plate
                            else None
                        ),
                        vin=data.vehicle.vin.strip() if data.vehicle.vin else None,
                        color=data.vehicle.color.strip() if data.vehicle.color else None,
                        mileage=data.vehicle.mileage,
                    )
                )

        if vehicle.client_id is None:
            vehicle.client_id = client.id
        elif vehicle.client_id != client.id:
            raise BusinessRuleError("Автомобиль не принадлежит указанному клиенту")

        return await self.create(
            OrderCreate(
                client_id=client.id,
                vehicle_id=vehicle.id,
                source=data.source,
                comment=data.comment,
                mileage=data.mileage,
                items=data.items,
            ),
            created_by_id=created_by_id,
        )

    async def update(self, order_id: int, data: OrderUpdate) -> Order:
        order = await self.get(order_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "source" and value is None:
                continue
            setattr(order, field, value)
        await self.session.flush()
        return await self.get(order_id)

    async def add_item(self, order_id: int, data: OrderItemCreate) -> Order:
        order = await self.get(order_id)
        if order.status not in _EDITABLE_STATUSES:
            raise BusinessRuleError("Нельзя менять состав закрытого/отменённого заказа")
        item = await self._build_item(order.id, data)
        self.session.add(item)
        order.items.append(item)
        order.total_amount = sum((i.total_price for i in order.items), Decimal(0))
        await self.session.flush()
        return await self.get(order_id)

    async def remove_item(self, order_id: int, item_id: int) -> Order:
        order = await self.get(order_id)
        if order.status not in _EDITABLE_STATUSES:
            raise BusinessRuleError("Нельзя менять состав закрытого/отменённого заказа")
        target = next((i for i in order.items if i.id == item_id), None)
        if target is None:
            raise NotFoundError("Позиция заказа не найдена")
        await self.session.delete(target)
        order.items.remove(target)
        order.total_amount = sum((i.total_price for i in order.items), Decimal(0))
        await self.session.flush()
        return await self.get(order_id)

    async def replace_items(self, order_id: int, items: list[OrderItemCreate]) -> Order:
        order = await self.get(order_id)
        if order.status not in _EDITABLE_STATUSES:
            raise BusinessRuleError("Нельзя менять состав закрытого/отменённого заказа")
        for item in list(order.items):
            await self.session.delete(item)
        order.items.clear()
        total = Decimal(0)
        for item_data in items:
            item = await self._build_item(order.id, item_data)
            self.session.add(item)
            order.items.append(item)
            total += item.total_price
        order.total_amount = total
        await self.session.flush()
        return await self.get(order_id)

    async def change_status(
        self,
        order_id: int,
        new_status: OrderStatus,
        *,
        validate_transition: bool = True,
        require_completion_document: bool = True,
    ) -> Order:
        order = await self.get(order_id)
        if new_status == order.status:
            return order
        if validate_transition and new_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
            raise BusinessRuleError(
                f"Недопустимый переход статуса: {order.status.value} → {new_status.value}"
            )
        if require_completion_document and new_status == OrderStatus.DONE and not order.documents:
            raise BusinessRuleError(
                "Для перевода заказа в статус «Готово» сначала оформите заказ-наряд"
            )
        order.status = new_status
        if new_status == OrderStatus.IN_PROGRESS and order.started_at is None:
            order.started_at = _now()
        if new_status == OrderStatus.DONE:
            order.completed_at = _now()
        else:
            order.completed_at = None
        await self.session.flush()
        updated = await self.get(order_id)
        await NotificationService(self.session).enqueue_order_status(updated)
        return updated

    async def list_documents(self, order_id: int) -> list[OrderDocument]:
        return list((await self.get(order_id)).documents)

    async def get_document(
        self, order_id: int, document_id: int | None = None
    ) -> OrderDocument:
        order = await self.get(order_id)
        if document_id is None:
            if not order.documents:
                raise NotFoundError("Заказ-наряд ещё не оформлен")
            return order.documents[-1]
        document = next((item for item in order.documents if item.id == document_id), None)
        if document is None:
            raise NotFoundError("Заказ-наряд ещё не оформлен")
        return document

    @staticmethod
    def _check_document_addable(order: Order) -> None:
        if order.status == OrderStatus.CANCELLED or (
            order.status == OrderStatus.DONE and order.documents
        ):
            raise BusinessRuleError("Документ закрытого или отменённого заказа нельзя заменить")

    @staticmethod
    def _check_document_deletable(order: Order) -> None:
        if order.status in {OrderStatus.DONE, OrderStatus.CANCELLED}:
            raise BusinessRuleError("Документ закрытого или отменённого заказа нельзя удалить")

    async def _save_document(
        self,
        order: Order,
        *,
        source: OrderDocumentSource,
        filename: str,
        content_type: str,
        content: bytes,
        created_by_id: int | None,
        check_addable: bool = True,
    ) -> OrderDocument:
        if check_addable:
            self._check_document_addable(order)
        if not content:
            raise BusinessRuleError("Файл пуст")
        if len(content) > MAX_DOCUMENT_SIZE_BYTES:
            raise BusinessRuleError(
                f"Размер файла превышает {MAX_DOCUMENT_SIZE_BYTES // (1024 * 1024)} МБ"
            )
        document = OrderDocument(
            organization_id=self.organization_id,
            order_id=order.id,
            source=source,
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            content=content,
            created_by_id=created_by_id,
        )
        self.session.add(document)
        order.documents.append(document)
        await self.session.flush()
        return document

    async def delete_document(self, order_id: int, document_id: int) -> None:
        order = await self.get(order_id)
        self._check_document_deletable(order)
        document = await self.get_document(order_id, document_id)
        order.documents.remove(document)
        await self.session.delete(document)
        await self.session.flush()

    async def generate_document(
        self,
        order_id: int,
        created_by_id: int | None,
    ) -> OrderDocument:
        order = await self.get(order_id)
        organization = await self.session.get(Organization, self.organization_id)
        if organization is None:
            raise NotFoundError("Организация не найдена")

        def esc(value: object) -> str:
            return html.escape(str(value if value not in (None, "") else "—"))

        rows = "".join(
            "<tr>"
            f"<td>{esc(index)}</td><td>{esc(item.description)}</td>"
            f"<td>{esc(item.item_type.value)}</td><td>{esc(item.quantity)}</td>"
            f"<td>{esc(item.unit_price)}</td><td>{esc(item.total_price)}</td>"
            "</tr>"
            for index, item in enumerate(order.items, 1)
        )
        if not rows:
            rows = '<tr><td colspan="6">Позиции отсутствуют</td></tr>'
        generated_at = _now()
        client_name = order.client.full_name if order.client else None
        client_phone = order.client.phone if order.client else None
        vehicle_make = order.vehicle.make if order.vehicle else None
        vehicle_model = order.vehicle.model if order.vehicle else None
        vehicle_plate = order.vehicle.license_plate if order.vehicle else None
        vehicle_vin = order.vehicle.vin if order.vehicle else None
        body = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><title>Заказ-наряд {esc(order.number)}</title>
<style>
body{{font:14px Arial,sans-serif;color:#222;max-width:900px;margin:32px auto}}
h1{{font-size:24px}} .meta{{display:grid;grid-template-columns:1fr 1fr;gap:8px 24px}}
table{{width:100%;border-collapse:collapse;margin-top:24px}}
th,td{{border:1px solid #999;padding:7px;text-align:left}} th{{background:#eee}}
.total{{font-size:18px;text-align:right;margin-top:16px}} .signatures{{display:flex;
justify-content:space-between;margin-top:64px}} @media print{{body{{margin:12mm}}}}
</style></head><body>
<h1>Заказ-наряд № {esc(order.number)}</h1>
<div class="meta">
<div><b>Исполнитель:</b> {esc(organization.name)}</div>
<div><b>ИНН:</b> {esc(organization.inn)}</div>
<div><b>Адрес:</b> {esc(organization.legal_address)}</div>
<div><b>Телефон:</b> {esc(organization.phone)}</div>
<div><b>Заказчик:</b> {esc(client_name)}</div>
<div><b>Телефон заказчика:</b> {esc(client_phone)}</div>
<div><b>Автомобиль:</b> {esc(vehicle_make)} {esc(vehicle_model)}</div>
<div><b>Госномер / VIN:</b> {esc(vehicle_plate)} / {esc(vehicle_vin)}</div>
<div><b>Пробег:</b> {esc(order.mileage)}</div>
<div><b>Дата оформления:</b> {esc(generated_at.strftime("%d.%m.%Y %H:%M UTC"))}</div>
</div>
<p><b>Комментарий:</b> {esc(order.comment)}</p>
<table><thead><tr><th>№</th><th>Наименование</th><th>Тип</th><th>Кол-во</th>
<th>Цена</th><th>Сумма</th></tr></thead><tbody>{rows}</tbody></table>
<p class="total"><b>Итого: {esc(order.total_amount)} ₽</b></p>
<div class="signatures"><span>Исполнитель: __________________</span>
<span>Заказчик: __________________</span></div>
</body></html>"""
        return await self._save_document(
            order,
            source=OrderDocumentSource.GENERATED,
            filename=f"order-{re.sub(r'[^A-Za-z0-9_-]', '_', order.number)}.html",
            content_type="text/html",
            content=body.encode("utf-8"),
            created_by_id=created_by_id,
        )

    async def upload_document(
        self,
        order_id: int,
        *,
        filename: str | None,
        content_type: str | None,
        content: bytes,
        created_by_id: int | None,
    ) -> OrderDocument:
        order = await self.get(order_id)
        safe_name, normalized_type = self._validate_document_upload(
            filename=filename,
            content_type=content_type,
            content=content,
        )
        return await self._save_document(
            order,
            source=OrderDocumentSource.UPLOADED,
            filename=safe_name,
            content_type=normalized_type,
            content=content,
            created_by_id=created_by_id,
        )

    @staticmethod
    def _validate_document_upload(
        *, filename: str | None, content_type: str | None, content: bytes
    ) -> tuple[str, str]:
        safe_name = Path(filename or "").name
        normalized_type = (content_type or "").split(";", 1)[0].strip().lower()
        suffix = Path(safe_name).suffix.lower()
        if not content:
            raise BusinessRuleError("Файл пуст")
        if len(content) > MAX_DOCUMENT_SIZE_BYTES:
            raise BusinessRuleError(
                f"Размер файла превышает {MAX_DOCUMENT_SIZE_BYTES // (1024 * 1024)} МБ"
            )
        if (
            not safe_name
            or normalized_type not in _UPLOAD_TYPES
            or suffix not in _UPLOAD_TYPES[normalized_type]
        ):
            raise BusinessRuleError("Поддерживаются PDF, HTML, JPEG, PNG, WebP и GIF")
        if normalized_type == "application/pdf" and not content.startswith(b"%PDF-"):
            raise BusinessRuleError("Содержимое файла не является PDF")
        if normalized_type == "text/html":
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise BusinessRuleError("HTML должен быть в кодировке UTF-8") from exc
            if not re.search(r"<!doctype\s+html|<html(?:\s|>)", text, re.IGNORECASE):
                raise BusinessRuleError("Содержимое файла не является HTML")
            if re.search(r"<script(?:\s|>)", text, re.IGNORECASE):
                raise BusinessRuleError("HTML с исполняемыми скриптами не принимается")
        image_signatures = {
            "image/jpeg": content.startswith(b"\xff\xd8\xff"),
            "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
            "image/webp": content.startswith(b"RIFF") and content[8:12] == b"WEBP",
            "image/gif": content.startswith((b"GIF87a", b"GIF89a")),
        }
        if normalized_type in image_signatures and not image_signatures[normalized_type]:
            raise BusinessRuleError("Содержимое файла не соответствует формату")
        return safe_name, normalized_type

    async def upload_documents(
        self,
        order_id: int,
        files: list[tuple[str | None, str | None, bytes]],
        created_by_id: int | None,
    ) -> list[OrderDocument]:
        if not files:
            raise BusinessRuleError("Выберите хотя бы один файл")
        if len(files) > MAX_DOCUMENTS_PER_UPLOAD:
            raise BusinessRuleError(
                f"За один раз можно загрузить не более {MAX_DOCUMENTS_PER_UPLOAD} файлов"
            )
        order = await self.get(order_id)
        self._check_document_addable(order)
        prepared = [
            (
                *self._validate_document_upload(
                    filename=filename,
                    content_type=content_type,
                    content=content,
                ),
                content,
            )
            for filename, content_type, content in files
        ]
        result: list[OrderDocument] = []
        for filename, content_type, content in prepared:
            result.append(
                await self._save_document(
                    order,
                    source=OrderDocumentSource.UPLOADED,
                    filename=filename,
                    content_type=content_type,
                    content=content,
                    created_by_id=created_by_id,
                    check_addable=False,
                )
            )
        return result

    async def delete(self, order_id: int) -> None:
        order = await self.repo.get(order_id)
        if order is None:
            raise NotFoundError("Заказ не найден")
        await self.repo.delete(order)

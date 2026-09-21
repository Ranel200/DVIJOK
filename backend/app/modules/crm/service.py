"""Оркестрация CRM поверх доменных клиентов, автомобилей и заказов."""

import datetime as dt
from collections.abc import Iterable
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.clients.models import Client
from app.modules.crm.schemas import (
    CrmClientBrief,
    CrmColumn,
    CrmDocument,
    CrmMarkerCreate,
    CrmMarkerRead,
    CrmOrderLineRead,
    CrmOrderRead,
    CrmOrderWrite,
)
from app.modules.mechanics.models import Mechanic
from app.modules.orders.models import Order, OrderItem, OrderMarker
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderCreate,
    OrderItemCreate,
)
from app.modules.orders.service import OrderService
from app.modules.schedule.repository import ScheduleRepository
from app.modules.schedule.service import ScheduleService
from app.modules.users.models import User
from app.modules.vehicles.models import Vehicle
from app.shared.enums import OrderItemType, OrderStatus

CRM_COLUMNS = (
    (OrderStatus.NEW, "Новая сделка", "linear-gradient(94.25deg, #6B8CFF 0%, #214ACD 100%)"),
    (
        OrderStatus.PRIMARY,
        "Первичная запись",
        "linear-gradient(94.25deg, #5C9FC4 0%, #02517F 100%)",
    ),
    (OrderStatus.DIAGNOSTICS, "Диагностика", "linear-gradient(94.25deg, #F6B75F 0%, #CA720C 100%)"),
    (OrderStatus.APPROVAL, "Согласование", "linear-gradient(94.25deg, #C96CEC 0%, #8617BC 100%)"),
    (
        OrderStatus.SECONDARY,
        "Вторичная запись",
        "linear-gradient(94.25deg, #64C9F2 0%, #09557E 100%)",
    ),
    (OrderStatus.IN_PROGRESS, "В работе", "linear-gradient(94.25deg, #F28C50 0%, #B94608 100%)"),
    (OrderStatus.WAITING, "Ожидание", "linear-gradient(94.25deg, #9566D3 0%, #430890 100%)"),
    (OrderStatus.DONE, "Выдано/завершено", "linear-gradient(94.25deg, #7FCB37 0%, #006D1F 100%)"),
)
CRM_STATUSES = {item[0] for item in CRM_COLUMNS}
_MONTHS = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)
_DEFAULT_MARKERS = (
    ("Сы мэра", "rgb(67, 252, 30)"),
    ("Постояшка", "rgb(138, 65, 255)"),
    ("Конфликтный", "rgb(189, 35, 30)"),
)


class CrmService:
    def __init__(self, repo: OrderRepository, current_user: User) -> None:
        self.repo = repo
        self.session = repo.session
        self.organization_id = repo.organization_id
        self.current_user = current_user
        # The CRM grant is organization-wide. A mechanic with this explicit
        # grant works with the board like an administrator, rather than being
        # limited to orders assigned to their mechanic profile.
        self.orders = OrderService(repo)

    async def markers(self) -> list[CrmMarkerRead]:
        rows = list(
            (
                await self.session.execute(
                    select(OrderMarker)
                    .where(OrderMarker.organization_id == self.organization_id)
                    .order_by(OrderMarker.id)
                )
            )
            .scalars()
            .all()
        )
        if not rows:
            rows = [
                OrderMarker(organization_id=self.organization_id, name=name, color=color)
                for name, color in _DEFAULT_MARKERS
            ]
            self.session.add_all(rows)
            await self.session.flush()
        return [CrmMarkerRead(id=item.id, name=item.name, color=item.color) for item in rows]

    async def create_marker(self, data: CrmMarkerCreate) -> CrmMarkerRead:
        name = data.name.strip()
        duplicate = (
            await self.session.execute(
                select(OrderMarker).where(
                    OrderMarker.organization_id == self.organization_id,
                    OrderMarker.name == name,
                )
            )
        ).scalar_one_or_none()
        if duplicate is not None:
            raise BusinessRuleError("Маркер с таким названием уже существует")
        marker = OrderMarker(
            organization_id=self.organization_id,
            name=name,
            color=data.color.strip(),
        )
        self.session.add(marker)
        await self.session.flush()
        return CrmMarkerRead(id=marker.id, name=marker.name, color=marker.color)

    async def _set_marker(self, order: Order, marker_id: int | None) -> None:
        if marker_id is None:
            order.marker = None
            order.marker_id = None
            return
        marker = (
            await self.session.execute(
                select(OrderMarker).where(
                    OrderMarker.id == marker_id,
                    OrderMarker.organization_id == self.organization_id,
                )
            )
        ).scalar_one_or_none()
        if marker is None:
            raise NotFoundError("Маркер не найден")
        order.marker = marker

    async def _all_orders(self) -> list[Order]:
        orders, _ = await self.repo.search(
            status=None,
            source=None,
            mechanic_id=None,
            query=None,
            limit=500,
            offset=0,
        )
        return [order for order in orders if order.status != OrderStatus.CANCELLED]

    @staticmethod
    def _stage(status: OrderStatus) -> OrderStatus:
        return OrderStatus.APPROVAL if status == OrderStatus.AGREEMENT else status

    @staticmethod
    def _date_label(value) -> str:
        if value is None:
            return ""
        if isinstance(value, dt.datetime):
            aware = value if value.tzinfo is not None else value.replace(tzinfo=dt.UTC)
            value = aware.astimezone(ZoneInfo(settings.SCHEDULE_TIMEZONE))
        return f"{value.day} {_MONTHS[value.month - 1]}"

    @staticmethod
    def _number(order: Order) -> int:
        try:
            return int(order.number)
        except ValueError:
            return order.id

    @staticmethod
    def _scheduled_fields(value: dt.datetime | None) -> tuple[str, str]:
        """Return the date/time in the timezone used by the booking UI.

        PostgreSQL returns timestamptz values in UTC.  The admin form expects a
        Russian date mask and the same local time that the client selected.
        """

        if value is None:
            return "", ""
        aware = value if value.tzinfo is not None else value.replace(tzinfo=dt.UTC)
        local = aware.astimezone(ZoneInfo(settings.SCHEDULE_TIMEZONE))
        return local.strftime("%d.%m.%Y"), local.strftime("%H:%M")

    def _read(self, order: Order) -> CrmOrderRead:
        client = order.client
        vehicle = order.vehicle
        mechanic_names: list[str] = []
        lines: list[CrmOrderLineRead] = []
        for item in order.items:
            mechanic = item.mechanic
            if mechanic is not None and mechanic.full_name not in mechanic_names:
                mechanic_names.append(mechanic.full_name)
            lines.append(
                CrmOrderLineRead(
                    id=item.id,
                    service_id=item.service_id or 0,
                    price=item.unit_price,
                    discount=item.discount_percent,
                    master_id=mechanic.user_id if mechanic else None,
                )
            )
        if not mechanic_names and order.mechanic is not None:
            mechanic_names.append(order.mechanic.full_name)
        documents = [
            CrmDocument(
                id=document.id,
                color="#B3C8FF",
                title=document.filename,
                meta=(
                    f"{vehicle.make if vehicle else ''} "
                    f"{vehicle.model if vehicle else ''} · {order.total_amount} ₽"
                ).strip(),
                date=f"Сформирован: {self._date_label(document.created_at)}",
                download_url=(f"/api/v1/orders/{order.id}/documents/{document.id}/content"),
            )
            for document in order.documents
        ]
        scheduled_date, scheduled_time = self._scheduled_fields(order.scheduled_at)
        return CrmOrderRead(
            id=order.id,
            number=self._number(order),
            status=self._stage(order.status),
            client_name=client.full_name if client else "",
            phone=client.phone if client else "",
            email=(client.email or "") if client else "",
            description=order.comment or "",
            date=scheduled_date,
            time=scheduled_time,
            appointment_master_id=(
                order.mechanic.user_id if order.mechanic is not None else None
            ),
            marker_id=order.marker_id,
            marker_color=order.marker.color if order.marker else None,
            source=order.source,
            plate=(vehicle.license_plate or "") if vehicle else "",
            brand=vehicle.make if vehicle else "",
            model=vehicle.model if vehicle else "",
            car_brand=(f"{vehicle.make} {vehicle.model}".strip() if vehicle else ""),
            car_year=vehicle.year if vehicle else None,
            year=vehicle.year if vehicle else None,
            color=(vehicle.color or "") if vehicle else "",
            vin=(vehicle.vin or "") if vehicle else "",
            mileage=(
                order.mileage
                if order.mileage is not None
                else vehicle.mileage if vehicle is not None else None
            ),
            amount=order.total_amount,
            services=[item.description for item in order.items],
            master=mechanic_names[0] if mechanic_names else "",
            masters=", ".join(mechanic_names),
            lines=lines,
            documents=documents,
            created_at=self._date_label(order.created_at),
            updated_at=self._date_label(order.updated_at),
        )

    async def list_deals(self) -> list[CrmOrderRead]:
        return [self._read(order) for order in await self._all_orders()]

    async def columns(self) -> list[CrmColumn]:
        grouped: dict[OrderStatus, list[CrmOrderRead]] = {status: [] for status in CRM_STATUSES}
        for order in await self._all_orders():
            stage = self._stage(order.status)
            if stage in grouped:
                grouped[stage].append(self._read(order))
        return [
            CrmColumn(id=status, title=title, gradient=gradient, items=grouped[status])
            for status, title, gradient in CRM_COLUMNS
        ]

    async def clients(self) -> list[CrmClientBrief]:
        rows = list(
            (
                await self.session.execute(
                    select(Client)
                    .where(Client.organization_id == self.organization_id)
                    .order_by(Client.full_name)
                )
            )
            .scalars()
            .all()
        )
        return [
            CrmClientBrief(
                id=client.id,
                name=client.full_name,
                phone=client.phone,
                email=client.email or "",
            )
            for client in rows
        ]

    async def _mechanic_ids(self, user_ids: Iterable[int | None]) -> dict[int, int]:
        ids = {value for value in user_ids if value is not None}
        if not ids:
            return {}
        mechanics = list(
            (
                await self.session.execute(
                    select(Mechanic).where(
                        Mechanic.organization_id == self.organization_id,
                        Mechanic.user_id.in_(ids),
                        Mechanic.is_active.is_(True),
                    )
                )
            )
            .scalars()
            .all()
        )
        result = {mechanic.user_id: mechanic.id for mechanic in mechanics if mechanic.user_id}
        if set(result) != ids:
            raise NotFoundError("Один или несколько выбранных мастеров не найдены")
        return result

    async def _items(self, data: CrmOrderWrite) -> list[OrderItemCreate]:
        mechanics = await self._mechanic_ids(line.master_id for line in data.lines)
        return [
            OrderItemCreate(
                item_type=OrderItemType.SERVICE,
                service_id=line.service_id,
                mechanic_id=(mechanics.get(line.master_id) if line.master_id is not None else None),
                unit_price=line.price,
                discount_percent=line.discount,
            )
            for line in data.lines
        ]

    @staticmethod
    def _appointment_start(data: CrmOrderWrite) -> dt.datetime:
        if not data.date.strip() or not data.time.strip():
            raise BusinessRuleError("Для записи укажите дату и время")
        raw = f"{data.date.strip()} {data.time.strip()}"
        parsed: dt.datetime | None = None
        for pattern in ("%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M"):
            try:
                parsed = dt.datetime.strptime(raw, pattern)
                break
            except ValueError:
                continue
        if parsed is None:
            raise BusinessRuleError("Дата и время записи указаны некорректно")
        return parsed.replace(tzinfo=ZoneInfo(settings.SCHEDULE_TIMEZONE))

    async def _sync_reservation(self, order: Order, data: CrmOrderWrite) -> Order:
        schedule = ScheduleService(ScheduleRepository(self.session, self.organization_id))
        existing = await schedule.repo.get_slot_by_order(order.id)

        if not data.reserve_slot:
            if existing is not None:
                await schedule.repo.delete_slot(existing)
            order.mechanic_id = None
            order.scheduled_at = None
            await self.session.flush()
            return await self.orders.get(order.id)

        start = self._appointment_start(data)
        duration = await self.orders.appointment_duration(order.id)
        mechanic_id: int | None = None
        if data.appointment_master_id is not None:
            mechanics = await self._mechanic_ids([data.appointment_master_id])
            mechanic_id = mechanics.get(data.appointment_master_id)
            if mechanic_id is None:
                raise BusinessRuleError("Выбранный сотрудник не является мастером")
        else:
            suggestions = await schedule.suggestions(
                date_from=start.date(),
                date_to=start.date(),
                mechanic_id=None,
                service_id=None,
                duration_minutes=duration,
                exclude_slot_id=existing.id if existing is not None else None,
            )
            selected_start = start.astimezone(ZoneInfo(settings.SCHEDULE_TIMEZONE))
            mechanic_id = next(
                (
                    slot.mechanic_id
                    for slot in suggestions.slots
                    if slot.start_time.astimezone(ZoneInfo(settings.SCHEDULE_TIMEZONE))
                    == selected_start
                ),
                None,
            )
            if mechanic_id is None:
                raise BusinessRuleError("На выбранное время нет свободного мастера")

        if existing is not None:
            await schedule.repo.delete_slot(existing)
        await schedule.reserve(
            mechanic_id=mechanic_id,
            start_time=start,
            duration_minutes=duration,
            order_id=order.id,
            title=f"Заказ {order.id}",
        )
        order.mechanic_id = mechanic_id
        order.scheduled_at = start
        await self.session.flush()
        await self.session.refresh(order, attribute_names=["mechanic"])
        return await self.orders.get(order.id)

    @staticmethod
    def _has_client_data(data: CrmOrderWrite) -> bool:
        return bool(data.client_name.strip() or data.phone.strip() or data.email)

    @staticmethod
    def _has_vehicle_data(data: CrmOrderWrite) -> bool:
        return bool(
            data.brand.strip()
            or data.model.strip()
            or data.plate.strip()
            or data.vin.strip()
            or data.color.strip()
            or data.year is not None
            or data.mileage is not None
        )

    async def _new_client(self, data: CrmOrderWrite) -> Client:
        phone = data.phone.strip()
        if phone:
            existing = (
                await self.session.execute(
                    select(Client).where(
                        Client.organization_id == self.organization_id,
                        Client.phone == phone,
                    )
                )
            ).scalar_one_or_none()
            if existing is not None:
                return existing
        client = Client(
            organization_id=self.organization_id,
            full_name=data.client_name.strip(),
            phone=phone,
            email=str(data.email) if data.email else None,
        )
        self.session.add(client)
        await self.session.flush()
        return client

    async def _new_vehicle(self, data: CrmOrderWrite, client_id: int | None) -> Vehicle:
        vin = data.vin.strip()
        if vin:
            existing = (
                await self.session.execute(
                    select(Vehicle).where(
                        Vehicle.organization_id == self.organization_id,
                        Vehicle.vin == vin,
                    )
                )
            ).scalar_one_or_none()
            if existing is not None:
                return existing
        vehicle = Vehicle(
            organization_id=self.organization_id,
            client_id=client_id,
            make=data.brand.strip(),
            model=data.model.strip(),
            year=data.year,
            license_plate=data.plate.strip() or None,
            vin=vin or None,
            color=data.color.strip() or None,
            mileage=data.mileage,
        )
        self.session.add(vehicle)
        await self.session.flush()
        return vehicle

    async def create(self, data: CrmOrderWrite) -> CrmOrderRead:
        if data.status == OrderStatus.DONE:
            raise BusinessRuleError(
                "Новый заказ нельзя сразу завершить: сначала оформите заказ-наряд"
            )
        client = await self._new_client(data) if self._has_client_data(data) else None
        vehicle = (
            await self._new_vehicle(data, client.id if client else None)
            if self._has_vehicle_data(data)
            else None
        )
        if client is not None and vehicle is not None and vehicle.client_id is None:
            vehicle.client_id = client.id
        order = await self.orders.create(
            OrderCreate(
                client_id=client.id if client else None,
                vehicle_id=vehicle.id if vehicle else None,
                source=data.source,
                comment=data.description or None,
                mileage=data.mileage,
                items=await self._items(data),
            ),
            created_by_id=self.current_user.id,
        )
        if "marker_id" in data.model_fields_set:
            await self._set_marker(order, data.marker_id)
        await self.session.flush()
        if data.status != OrderStatus.NEW:
            order = await self.orders.change_status(order.id, data.status)
        if "reserve_slot" in data.model_fields_set:
            order = await self._sync_reservation(order, data)
        return self._read(order)

    async def _load_for_update(self, order_id: int) -> Order:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.mechanic),
                selectinload(Order.documents),
                selectinload(Order.client),
                selectinload(Order.vehicle),
                selectinload(Order.mechanic),
            )
            .where(
                Order.id == order_id,
                Order.organization_id == self.organization_id,
            )
            .with_for_update()
        )
        order = (await self.session.execute(stmt)).scalar_one_or_none()
        if order is None:
            raise NotFoundError("Заказ не найден")
        return order

    async def update(self, order_id: int, data: CrmOrderWrite) -> CrmOrderRead:
        order = await self._load_for_update(order_id)
        if order.status in {OrderStatus.DONE, OrderStatus.CANCELLED}:
            raise BusinessRuleError("Закрытый или отменённый заказ нельзя редактировать")
        if order.client is None and self._has_client_data(data):
            order.client = await self._new_client(data)
        elif order.client is not None:
            order.client.full_name = data.client_name.strip()
            order.client.phone = data.phone.strip()
            order.client.email = str(data.email) if data.email else None

        if order.vehicle is None and self._has_vehicle_data(data):
            order.vehicle = await self._new_vehicle(data, order.client.id if order.client else None)
        elif order.vehicle is not None:
            order.vehicle.make = data.brand.strip()
            order.vehicle.model = data.model.strip()
            order.vehicle.year = data.year
            order.vehicle.license_plate = data.plate.strip() or None
            order.vehicle.vin = data.vin.strip() or None
            order.vehicle.color = data.color.strip() or None
            order.vehicle.mileage = data.mileage
        if order.client is not None and order.vehicle is not None:
            if order.vehicle.client_id is None:
                order.vehicle.client_id = order.client.id
            elif order.vehicle.client_id != order.client.id:
                raise BusinessRuleError("Автомобиль принадлежит другому клиенту")
        order.source = data.source
        if "marker_id" in data.model_fields_set:
            await self._set_marker(order, data.marker_id)
        order.comment = data.description.strip() or None
        order.mileage = data.mileage
        await self.orders.replace_items(order.id, await self._items(data))
        if data.status != order.status:
            await self.orders.change_status(
                order.id,
                data.status,
                validate_transition=False,
                require_completion_document=False,
            )
        order = await self.orders.get(order.id)
        if "reserve_slot" in data.model_fields_set:
            order = await self._sync_reservation(order, data)
        return self._read(order)

    async def get(self, order_id: int) -> CrmOrderRead:
        return self._read(await self.orders.get(order_id))

    async def change_status(self, order_id: int, status: OrderStatus) -> CrmOrderRead:
        order = await self.orders.change_status(
            order_id,
            status,
            validate_transition=False,
            require_completion_document=False,
        )
        return self._read(order)

    async def delete(self, order_id: int) -> None:
        await self.orders.delete(order_id)

    async def delete_many(self, ids: list[int]) -> None:
        for order_id in list(dict.fromkeys(ids)):
            await self.orders.delete(order_id)

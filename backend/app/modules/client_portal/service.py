"""Бизнес-логика client_portal: оркестрация staff-модулей для клиентского кабинета.

Сервис вызывает сервисы/репозитории других модулей (clients, vehicles, orders,
schedule, services, mechanics, organizations) — межмодульная оркестрация через
сервисный слой, тот же паттерн, что и у inventory.service.register_movement.
"""

import calendar
import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.client_auth.models import ClientAccount
from app.modules.client_auth.repository import ClientAuthRepository
from app.modules.client_portal.repository import ClientPortalRepository
from app.modules.client_portal.schemas import (
    AvailabilityRead,
    AvailableBookingSlot,
    BlockPublic,
    BookingAvailabilityUiRead,
    BookingCreate,
    BookingMasterOption,
    BookingOptionsRead,
    BookingRead,
    BranchDirectoryRead,
    BranchRead,
    ClientAppointmentRead,
    ClientBookingServiceId,
    ClientBotRead,
    ClientCarRead,
    ClientCarsRead,
    ClientHistoryItem,
    ClientHistoryRead,
    ClientMaintenanceItem,
    ClientRepairRead,
    ClientRepairStatus,
    FrontendBookingCreate,
    InvoiceItemRead,
    InvoiceRead,
    MechanicPublic,
    MyOrderRead,
    MyVehicleRead,
    OrganizationPublic,
    PublicBookingCreate,
    PublicBookingRead,
    SelectOption,
    ServiceCardRead,
    ServiceDirectoryRead,
    ServicePublic,
    SlotPublic,
    SpecialistDirectoryRead,
    SpecialistRead,
    VehicleInput,
)
from app.modules.client_vehicles.models import ClientVehicle
from app.modules.client_vehicles.service import ClientVehicleService
from app.modules.clients.models import Client
from app.modules.clients.repository import ClientRepository
from app.modules.mechanics.models import Mechanic
from app.modules.notifications.service import MessengerService
from app.modules.orders.models import Order
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import OrderCreate, OrderItemCreate, OrderUpdate
from app.modules.orders.service import OrderService
from app.modules.organizations.models import Organization
from app.modules.schedule.models import ScheduleSlot
from app.modules.schedule.repository import ScheduleRepository
from app.modules.schedule.schemas import (
    AvailableSlot,
    SlotCreate,
    SlotUpdate,
    WorkingHoursInterval,
)
from app.modules.schedule.service import ScheduleService
from app.modules.services.models import Service
from app.modules.services.repository import ServiceRepository
from app.modules.vehicles.models import Vehicle
from app.modules.vehicles.repository import VehicleRepository
from app.shared.enums import NotificationChannel, OrderItemType, OrderSource, OrderStatus

_STATUS_LABELS: dict[OrderStatus, str] = {
    OrderStatus.NEW: "Записан",
    OrderStatus.PRIMARY: "Записан",
    OrderStatus.DIAGNOSTICS: "В работе",
    OrderStatus.APPROVAL: "Согласование",
    OrderStatus.SECONDARY: "Записан",
    OrderStatus.WAITING: "Согласование",
    OrderStatus.IN_PROGRESS: "В работе",
    OrderStatus.AGREEMENT: "Согласование",
    OrderStatus.DONE: "Готово",
    OrderStatus.CANCELLED: "Отменён",
}

_DEFAULT_SLOT_MINUTES = 60
_CLIENT_BOOKING_KEYS = ("diagnostics", "repair")
_CLIENT_BOOKING_LABELS = {
    "diagnostics": "Диагностика",
    "repair": "Ремонт",
}
_RU_MONTHS = (
    "",
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
_RU_WEEKDAYS = (
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
)


class ClientPortalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ClientPortalRepository(session)

    # ── Discovery ──────────────────────────────────────────

    async def list_organizations(self) -> list[OrganizationPublic]:
        orgs = await self.repo.list_active_organizations()
        return [OrganizationPublic.model_validate(o) for o in orgs]

    @staticmethod
    def _city(address: str) -> str:
        first = address.split(",", 1)[0].strip()
        return first if first else "Город не указан"

    @staticmethod
    def _visit_label(value: dt.datetime | None) -> str:
        if value is None:
            return ""
        return f"{value.day} {_RU_MONTHS[value.month]} {value.year}"

    async def _organization_hours(self, organization_id: int) -> str:
        mechanics = list(
            (
                await self.session.execute(
                    select(Mechanic).where(
                        Mechanic.organization_id == organization_id,
                        Mechanic.is_active.is_(True),
                    )
                )
            )
            .scalars()
            .all()
        )
        if not mechanics:
            return "По предварительной записи"
        schedule = ScheduleService(ScheduleRepository(self.session, organization_id))
        timezone = ZoneInfo(settings.SCHEDULE_TIMEZONE)
        local_now = dt.datetime.now(timezone)
        intervals: list[WorkingHoursInterval] = []
        for mechanic in mechanics:
            working = await schedule.working_hours(mechanic.id)
            intervals.extend(
                item for item in working.intervals if item.weekday == local_now.weekday()
            )
        if not intervals:
            return "Сегодня выходной"
        first = min(item.start_time for item in intervals)
        last = max(item.end_time for item in intervals)
        if first <= local_now.time().replace(tzinfo=None) < last:
            return f"Открыто до {last.strftime('%H:%M')}"
        return f"Сегодня {first.strftime('%H:%M')}–{last.strftime('%H:%M')}"

    async def _next_opening_time(self, organization_id: int) -> str:
        mechanics = await self.list_mechanics(organization_id)
        if not mechanics:
            return ""
        timezone = ZoneInfo(settings.SCHEDULE_TIMEZONE)
        local_now = dt.datetime.now(timezone)
        schedule = ScheduleService(ScheduleRepository(self.session, organization_id))
        candidates: list[dt.datetime] = []
        for mechanic in mechanics:
            working = await schedule.working_hours(mechanic.id)
            for offset in range(8):
                day = local_now.date() + dt.timedelta(days=offset)
                for interval in working.intervals:
                    if interval.weekday != day.weekday():
                        continue
                    candidate = dt.datetime.combine(day, interval.start_time, timezone)
                    if candidate > local_now:
                        candidates.append(candidate)
        return min(candidates).strftime("%H:%M") if candidates else ""

    async def frontend_service_directory(
        self,
        client_account_id: int,
        query: str = "",
    ) -> ServiceDirectoryRead:
        organizations = await self.repo.list_active_organizations()
        visits = await self.repo.organization_last_visits(client_account_id)
        needle = query.strip().casefold()
        cards: list[ServiceCardRead] = []
        for organization in organizations:
            services = await self.list_services(organization.id)
            searchable = " ".join(
                [
                    organization.name,
                    organization.legal_address,
                    organization.description or "",
                    *(item.name for item in services),
                ]
            ).casefold()
            if needle and needle not in searchable:
                continue
            cards.append(
                ServiceCardRead(
                    id=str(organization.id),
                    name=organization.name,
                    address=organization.legal_address,
                    hours=await self._organization_hours(organization.id),
                    description=organization.description or "",
                    rating=0,
                    reviews=0,
                    last_visit=self._visit_label(visits.get(organization.id)),
                    logo=organization.logo or "",
                )
            )
        your_ids = set(visits)
        return ServiceDirectoryRead(
            city=self._city(organizations[0].legal_address) if organizations else "",
            yours=[card for card in cards if int(card.id) in your_ids],
            all=[card for card in cards if int(card.id) not in your_ids],
        )

    async def frontend_branches(self) -> BranchDirectoryRead:
        organizations = await self.repo.list_active_organizations()
        branches: list[BranchRead] = []
        for organization in organizations:
            hours = await self._organization_hours(organization.id)
            is_open = hours.startswith("Открыто до ")
            if is_open:
                until = hours.removeprefix("Открыто до ")
            else:
                until = await self._next_opening_time(organization.id)
            branches.append(
                BranchRead(
                    id=str(organization.id),
                    name=organization.name,
                    address=organization.legal_address,
                    is_open=is_open,
                    until=until,
                    map_src="/client/icons/record/map.png",
                )
            )
        return BranchDirectoryRead(
            city=self._city(organizations[0].legal_address) if organizations else "",
            branches=branches,
        )

    async def frontend_public_branch(
        self,
        organization_id: int,
        public_code: str,
    ) -> BranchDirectoryRead:
        """Возвращает только организацию ссылки; её внутренний ID наружу не уходит."""
        organization = await self._get_organization_or_404(organization_id)
        hours = await self._organization_hours(organization.id)
        is_open = hours.startswith("Открыто до ")
        until = (
            hours.removeprefix("Открыто до ")
            if is_open
            else await self._next_opening_time(organization.id)
        )
        return BranchDirectoryRead(
            city=self._city(organization.legal_address),
            branches=[
                BranchRead(
                    id=public_code,
                    name=organization.name,
                    address=organization.legal_address,
                    is_open=is_open,
                    until=until,
                    map_src="/client/icons/record/map.png",
                )
            ],
        )

    async def frontend_specialists(self, organization_id: int) -> SpecialistDirectoryRead:
        mechanics = await self.list_mechanics(organization_id)
        services = await self.list_services(organization_id)
        price = min((item.base_price for item in services), default=0)
        today = dt.datetime.now(ZoneInfo(settings.SCHEDULE_TIMEZONE)).date()
        date_to = today + dt.timedelta(days=30)
        schedule = ScheduleService(ScheduleRepository(self.session, organization_id))
        result: list[SpecialistRead] = []
        colors = (
            "var(--dvijok-accent-coral)",
            "var(--dvijok-accent-cyan)",
            "var(--dvijok-blue-pale)",
        )
        for index, mechanic in enumerate(mechanics):
            suggestions = await schedule.suggestions(
                date_from=today,
                date_to=date_to,
                mechanic_id=mechanic.id,
                service_id=None,
                duration_minutes=_DEFAULT_SLOT_MINUTES,
            )
            first_date = (
                suggestions.slots[0].start_time.astimezone(ZoneInfo(suggestions.timezone)).date()
                if suggestions.slots
                else None
            )
            slots = []
            if first_date is not None:
                slots = [
                    item.start_time.astimezone(ZoneInfo(suggestions.timezone)).strftime("%H:%M")
                    for item in suggestions.slots
                    if item.start_time.astimezone(ZoneInfo(suggestions.timezone)).date()
                    == first_date
                ]
            nearest_date = (
                f"{_RU_WEEKDAYS[first_date.weekday()]}, "
                f"{first_date.day} {_RU_MONTHS[first_date.month]}"
                if first_date is not None
                else "Нет свободных дат"
            )
            result.append(
                SpecialistRead(
                    id=str(mechanic.id),
                    name=mechanic.full_name,
                    role="Мастер",
                    avatar_color=colors[index % len(colors)],
                    rating=mechanic.rating,
                    reviews=0,
                    price=price,
                    nearest_date=nearest_date,
                    slots=slots,
                )
            )
        return SpecialistDirectoryRead(specialists=result)

    async def _get_organization_or_404(self, organization_id: int) -> Organization:
        org = await self.repo.get_organization(organization_id)
        if org is None:
            raise NotFoundError("Автосервис не найден")
        return org

    async def list_services(self, organization_id: int) -> list[ServicePublic]:
        await self._get_organization_or_404(organization_id)
        repo = ServiceRepository(self.session, organization_id)
        items, _ = await repo.search(active_only=True, limit=200, offset=0)
        return [ServicePublic.model_validate(s) for s in items]

    async def _public_booking_services(self, organization_id: int) -> dict[str, Service]:
        items = await ServiceRepository(self.session, organization_id).list_public_booking(
            _CLIENT_BOOKING_KEYS
        )
        return {
            item.public_booking_key: item for item in items if item.public_booking_key is not None
        }

    async def _resolve_frontend_service_id(
        self,
        organization_id: int,
        service_id: ClientBookingServiceId,
    ) -> int:
        # Numeric IDs remain accepted for old links/API consumers. The current
        # frontend sends stable keys from its original mock contract.
        if isinstance(service_id, int):
            return service_id
        service = (await self._public_booking_services(organization_id)).get(service_id)
        if service is None:
            raise NotFoundError("Услуга не найдена")
        return service.id

    async def list_mechanics(self, organization_id: int) -> list[MechanicPublic]:
        await self._get_organization_or_404(organization_id)
        stmt = (
            select(Mechanic)
            .where(Mechanic.organization_id == organization_id, Mechanic.is_active.is_(True))
            .order_by(Mechanic.full_name)
        )
        items = list((await self.session.execute(stmt)).scalars().all())
        return [MechanicPublic.model_validate(m) for m in items]

    async def get_availability(
        self, organization_id: int, day: dt.date, mechanic_id: int | None
    ) -> AvailabilityRead:
        await self._get_organization_or_404(organization_id)
        schedule_service = ScheduleService(ScheduleRepository(self.session, organization_id))
        _, _, slots, blocks = await schedule_service.week(day, mechanic_id)
        day_slots = [s for s in slots if s.start_time.date() == day]
        day_blocks = [b for b in blocks if b.start_time.date() == day]
        return AvailabilityRead(
            date=day,
            slots=[SlotPublic.model_validate(s) for s in day_slots],
            blocks=[BlockPublic.model_validate(b) for b in day_blocks],
        )

    async def frontend_booking_options(
        self,
        client_account_id: int | None,
        organization_id: int,
    ) -> BookingOptionsRead:
        public_services = await self._public_booking_services(organization_id)
        # Backward compatibility for databases not yet upgraded. The data
        # migration seeds both stable client choices for every organization.
        if all(key in public_services for key in _CLIENT_BOOKING_KEYS):
            service_options = [
                SelectOption(
                    value=key,
                    label=_CLIENT_BOOKING_LABELS[key],
                    # The client chooses only a coarse visit type. Its final
                    # price is determined by the service after inspection.
                    price=None,
                )
                for key in _CLIENT_BOOKING_KEYS
            ]
        else:
            services = await self.list_services(organization_id)
            service_options = [
                SelectOption(
                    value=str(item.id),
                    label=item.name,
                    price=item.base_price,
                )
                for item in services
            ]
        mechanics = await self.list_mechanics(organization_id)
        global_vehicles = (
            await ClientVehicleService(self.session).list_owned(client_account_id)
            if client_account_id is not None
            else []
        )
        legacy_vehicles = (
            self._unique_vehicles(await self.repo.list_vehicles_by_account(client_account_id))
            if client_account_id is not None
            else []
        )
        return BookingOptionsRead(
            service_options=service_options,
            car_options=[
                SelectOption(
                    value=str(item.id),
                    label=" · ".join(
                        part
                        for part in (
                            (
                                f"{item.brand} {item.model}"
                                if isinstance(item, ClientVehicle)
                                else f"{item.make} {item.model}"
                            ),
                            (item.plate if isinstance(item, ClientVehicle) else item.license_plate),
                        )
                        if part
                    ),
                )
                for item in (global_vehicles or legacy_vehicles)
            ],
            masters=[
                BookingMasterOption(
                    id="any",
                    name="Любой мастер",
                    subtitle="Определяется автоматически",
                ),
                *[
                    BookingMasterOption(
                        id=str(item.id),
                        name=item.full_name,
                        subtitle="Услуги",
                    )
                    for item in mechanics
                ],
            ],
        )

    async def frontend_booking_availability(
        self,
        *,
        organization_id: int,
        year: int,
        month: int,
        service_id: ClientBookingServiceId | None,
        master_id: int | str,
    ) -> BookingAvailabilityUiRead:
        await self._get_organization_or_404(organization_id)
        if not 0 <= month <= 11:
            raise BusinessRuleError("Месяц должен быть от 0 до 11")
        date_from = dt.date(year, month + 1, 1)
        date_to = dt.date(year, month + 1, calendar.monthrange(year, month + 1)[1])
        if service_id is None:
            public_services = await self._public_booking_services(organization_id)
            if "diagnostics" in public_services:
                resolved_service_id = public_services["diagnostics"].id
            else:
                services = await self.list_services(organization_id)
                if not services:
                    raise NotFoundError("В автосервисе нет доступных услуг")
                resolved_service_id = services[0].id
        else:
            resolved_service_id = await self._resolve_frontend_service_id(
                organization_id, service_id
            )
        mechanic_id = None if master_id == "any" else int(master_id)
        suggestions = await ScheduleService(
            ScheduleRepository(self.session, organization_id)
        ).suggestions(
            date_from=date_from,
            date_to=date_to,
            mechanic_id=mechanic_id,
            service_id=resolved_service_id,
            duration_minutes=None,
        )
        timezone = ZoneInfo(suggestions.timezone)
        slots = [
            AvailableBookingSlot(
                date=item.start_time.astimezone(timezone).date().isoformat(),
                time=item.start_time.astimezone(timezone).strftime("%H:%M"),
                master_id=str(item.mechanic_id),
                start_time=item.start_time,
                end_time=item.end_time,
            )
            for item in suggestions.slots
        ]
        days = dict.fromkeys(range(1, date_to.day + 1), False)
        for item in slots:
            days[dt.date.fromisoformat(item.date).day] = True
        return BookingAvailabilityUiRead(
            days=days,
            slots=slots,
            timezone=suggestions.timezone,
        )

    # ── Бронирование ───────────────────────────────────────

    async def _get_or_create_client(
        self, organization_id: int, client_account: ClientAccount, full_name: str
    ) -> Client:
        client_repo = ClientRepository(self.session, organization_id)
        client = await client_repo.get_by_phone(client_account.phone)
        if client is None:
            if await self.repo.lock_organization(organization_id) is None:
                raise NotFoundError("Автосервис не найден")
            client = await client_repo.get_by_phone(client_account.phone)
        if client is None:
            return await client_repo.add(
                Client(
                    organization_id=organization_id,
                    full_name=full_name,
                    phone=client_account.phone,
                    client_account_id=client_account.id,
                )
            )
        if client.client_account_id is None:
            client.client_account_id = client_account.id
            await self.session.flush()
        if (
            client.client_account_id == client_account.id
            and client.full_name == f"Клиент {client_account.phone}"
            and full_name != client.full_name
        ):
            client.full_name = full_name
            await self.session.flush()
        return client

    async def _get_or_create_public_client(
        self,
        organization_id: int,
        full_name: str,
        phone: str,
    ) -> Client:
        """Создаёт CRM-карточку без регистрации; существующую учётку лишь связывает."""
        account = await ClientAuthRepository(self.session).get_by_phone(phone)
        client_repo = ClientRepository(self.session, organization_id)
        client = await client_repo.get_by_phone(phone)
        if client is None:
            if await self.repo.lock_organization(organization_id) is None:
                raise NotFoundError("Автосервис не найден")
            client = await client_repo.get_by_phone(phone)
        if client is None:
            return await client_repo.add(
                Client(
                    organization_id=organization_id,
                    full_name=full_name,
                    phone=phone,
                    client_account_id=account.id if account is not None else None,
                )
            )
        if account is not None and client.client_account_id is None:
            client.client_account_id = account.id
            await self.session.flush()
        return client

    async def _get_or_create_vehicle(
        self, organization_id: int, client_id: int, data: VehicleInput
    ) -> Vehicle:
        vehicle_repo = VehicleRepository(self.session, organization_id)
        if data.vin:
            existing = await vehicle_repo.get_by_vin(data.vin)
            if existing is not None:
                if existing.client_id != client_id:
                    raise BusinessRuleError(
                        "Автомобиль с этим VIN уже привязан к другому клиенту в этом автосервисе"
                    )
                return await self._sync_organization_vehicle(existing, data)
        if data.license_plate:
            client_vehicles, _ = await vehicle_repo.list_by_client(client_id, limit=1000, offset=0)
            compact_plate = data.license_plate.replace(" ", "").upper()
            existing = next(
                (
                    item
                    for item in client_vehicles
                    if item.license_plate
                    and item.license_plate.replace(" ", "").upper() == compact_plate
                ),
                None,
            )
            if existing is not None:
                return await self._sync_organization_vehicle(existing, data)
        return await vehicle_repo.add(
            Vehicle(
                organization_id=organization_id,
                client_id=client_id,
                make=data.make,
                model=data.model,
                year=data.year,
                vin=data.vin,
                license_plate=data.license_plate,
                color=data.color,
                mileage=data.mileage,
            )
        )

    async def _sync_organization_vehicle(
        self,
        vehicle: Vehicle,
        data: VehicleInput,
    ) -> Vehicle:
        """Обновляет рабочую копию машины из глобального профиля клиента."""
        vehicle.make = data.make
        vehicle.model = data.model
        vehicle.year = data.year
        vehicle.vin = data.vin
        vehicle.license_plate = data.license_plate
        vehicle.color = data.color
        vehicle.mileage = data.mileage
        await self.session.flush()
        return vehicle

    async def _vehicle_selected_by_client(
        self,
        organization_id: int,
        client_account_id: int,
        target_client_id: int,
        vehicle_id: int,
    ) -> Vehicle:
        global_vehicle = await ClientVehicleService(self.session).find_owned(
            vehicle_id, client_account_id
        )
        if global_vehicle is not None:
            return await self._get_or_create_vehicle(
                organization_id,
                target_client_id,
                VehicleInput(
                    make=global_vehicle.brand,
                    model=global_vehicle.model,
                    year=global_vehicle.year,
                    vin=global_vehicle.vin,
                    license_plate=global_vehicle.plate,
                    color=global_vehicle.color,
                    mileage=global_vehicle.mileage,
                ),
            )
        source = await self.repo.get_vehicle_owned_by_account(vehicle_id, client_account_id)
        if source is None:
            raise NotFoundError("Автомобиль не найден")
        if source.organization_id == organization_id and source.client_id == target_client_id:
            return source
        return await self._get_or_create_vehicle(
            organization_id,
            target_client_id,
            VehicleInput(
                make=source.make,
                model=source.model,
                year=source.year,
                vin=source.vin,
                license_plate=source.license_plate,
                color=source.color,
                mileage=source.mileage,
            ),
        )

    async def _prepare_frontend_booking(
        self,
        *,
        organization_id: int,
        service_id: ClientBookingServiceId,
        selected_mechanic_id: int | str,
        booking_date: dt.date,
        booking_time: str,
        exclude_slot_id: int | None = None,
    ) -> tuple[Service, dt.datetime, AvailableSlot, ScheduleService, int]:
        await self._get_organization_or_404(organization_id)
        resolved_service_id = await self._resolve_frontend_service_id(organization_id, service_id)
        selected_service = await ServiceRepository(self.session, organization_id).get(
            resolved_service_id
        )
        if selected_service is None or not selected_service.is_active:
            raise NotFoundError("Услуга не найдена")

        timezone = ZoneInfo(settings.SCHEDULE_TIMEZONE)
        local_time = dt.time.fromisoformat(booking_time)
        start_time = dt.datetime.combine(booking_date, local_time, timezone)
        if start_time.astimezone(dt.UTC) <= dt.datetime.now(dt.UTC):
            raise BusinessRuleError("Нельзя записаться на прошедшее время")

        requested_mechanic = None if selected_mechanic_id == "any" else int(selected_mechanic_id)
        schedule = ScheduleService(ScheduleRepository(self.session, organization_id))
        suggestions = await schedule.suggestions(
            date_from=booking_date,
            date_to=booking_date,
            mechanic_id=requested_mechanic,
            service_id=selected_service.id,
            duration_minutes=None,
            exclude_slot_id=exclude_slot_id,
        )
        chosen = next(
            (item for item in suggestions.slots if item.start_time == start_time),
            None,
        )
        if chosen is None:
            raise BusinessRuleError("Выбранное время уже занято или недоступно")
        return (
            selected_service,
            start_time,
            chosen,
            schedule,
            suggestions.duration_minutes,
        )

    async def _reschedulable_frontend_booking(
        self,
        *,
        organization_id: int,
        client: Client,
        vehicle: Vehicle,
    ) -> tuple[Order | None, ScheduleSlot | None]:
        client_repo = ClientRepository(self.session, organization_id)
        if await client_repo.lock(client.id) is None:
            raise NotFoundError("Клиент не найден")
        order = await OrderRepository(
            self.session,
            organization_id,
        ).get_reschedulable_client_order_for_update(
            client_id=client.id,
            vehicle_id=vehicle.id,
        )
        if order is None:
            return None, None
        slot = await ScheduleRepository(
            self.session,
            organization_id,
        ).get_slot_by_order(order.id)
        return order, slot

    async def _create_reserved_frontend_order(
        self,
        *,
        organization_id: int,
        client: Client,
        vehicle: Vehicle,
        selected_service: Service,
        start_time: dt.datetime,
        chosen: AvailableSlot,
        schedule: ScheduleService,
        duration_minutes: int,
        source: OrderSource,
        existing_order: Order | None = None,
        existing_slot: ScheduleSlot | None = None,
    ) -> BookingRead:
        item = OrderItemCreate(
            item_type=OrderItemType.SERVICE,
            service_id=selected_service.id,
            mechanic_id=chosen.mechanic_id,
        )
        order_service = OrderService(OrderRepository(self.session, organization_id))
        if existing_order is None:
            order = await order_service.create(
                OrderCreate(
                    client_id=client.id,
                    vehicle_id=vehicle.id,
                    mechanic_id=chosen.mechanic_id,
                    source=source,
                    mileage=vehicle.mileage,
                    scheduled_at=start_time,
                    items=[item],
                ),
                created_by_id=None,
            )
        else:
            await order_service.update(
                existing_order.id,
                OrderUpdate(
                    mechanic_id=chosen.mechanic_id,
                    mileage=vehicle.mileage,
                    scheduled_at=start_time,
                ),
            )
            order = await order_service.replace_items(existing_order.id, [item])
        title = f"{vehicle.make} {vehicle.model} — {selected_service.name}"
        if existing_slot is None:
            slot = await schedule.reserve(
                mechanic_id=chosen.mechanic_id,
                start_time=start_time,
                duration_minutes=duration_minutes,
                order_id=order.id,
                title=title,
            )
        else:
            slot = await schedule.update_slot(
                existing_slot.id,
                SlotUpdate(
                    mechanic_id=chosen.mechanic_id,
                    title=title,
                    start_time=start_time,
                    end_time=start_time + dt.timedelta(minutes=duration_minutes),
                ),
            )
        return BookingRead(
            order_id=order.id,
            number=order.number,
            organization_id=organization_id,
            status=order.status,
            mechanic_id=chosen.mechanic_id,
            slot_id=slot.id,
            start_time=start_time,
            end_time=slot.end_time,
        )

    async def create_frontend_booking(
        self,
        client_account: ClientAccount,
        data: FrontendBookingCreate,
    ) -> BookingRead:
        organization_id = data.organization_id
        await self._get_organization_or_404(organization_id)
        if data.client is not None:
            if data.client.phone != client_account.phone:
                raise BusinessRuleError(
                    "Номер телефона в записи не совпадает с авторизованным клиентом"
                )
            if not client_account.full_name or (
                client_account.full_name == f"Клиент {client_account.phone}"
            ):
                client_account.full_name = data.client.name.strip()
                await self.session.flush()
        if not client_account.full_name:
            # Активный старый booking-flow не запрашивает ФИО. Сохраняем
            # совместимость для аккаунтов, созданных только по номеру телефона.
            client_account.full_name = f"Клиент {client_account.phone}"
            await self.session.flush()

        client = await self._get_or_create_client(
            organization_id,
            client_account,
            client_account.full_name,
        )
        locked_client = await ClientRepository(self.session, organization_id).lock(client.id)
        if locked_client is None:
            raise NotFoundError("Клиент не найден")
        client = locked_client
        if data.client is not None:
            global_vehicle = await ClientVehicleService(self.session).get_or_create_from_booking(
                client_account_id=client_account.id,
                brand=data.client.brand,
                model=data.client.model,
                plate=data.client.plate,
                plate_type=data.client.plate_type,
            )
            vehicle = await self._get_or_create_vehicle(
                organization_id,
                client.id,
                VehicleInput(
                    make=global_vehicle.brand,
                    model=global_vehicle.model,
                    year=global_vehicle.year,
                    vin=global_vehicle.vin,
                    license_plate=global_vehicle.plate,
                    color=global_vehicle.color,
                    mileage=global_vehicle.mileage,
                ),
            )
        else:
            assert data.car_id is not None
            vehicle = await self._vehicle_selected_by_client(
                organization_id,
                client_account.id,
                client.id,
                data.car_id,
            )
        existing_order, existing_slot = await self._reschedulable_frontend_booking(
            organization_id=organization_id,
            client=client,
            vehicle=vehicle,
        )
        (
            selected_service,
            start_time,
            chosen,
            schedule,
            duration_minutes,
        ) = await self._prepare_frontend_booking(
            organization_id=organization_id,
            service_id=data.service_id,
            selected_mechanic_id=data.selected_mechanic_id,
            booking_date=data.date,
            booking_time=data.time,
            exclude_slot_id=existing_slot.id if existing_slot is not None else None,
        )
        return await self._create_reserved_frontend_order(
            organization_id=organization_id,
            client=client,
            vehicle=vehicle,
            selected_service=selected_service,
            start_time=start_time,
            chosen=chosen,
            schedule=schedule,
            duration_minutes=duration_minutes,
            source=OrderSource.WEBSITE,
            existing_order=existing_order,
            existing_slot=existing_slot,
        )

    async def create_public_booking(
        self,
        organization_id: int,
        data: PublicBookingCreate,
    ) -> PublicBookingRead:
        await self._get_organization_or_404(organization_id)
        client = await self._get_or_create_public_client(
            organization_id,
            data.client.name,
            data.client.phone,
        )
        locked_client = await ClientRepository(self.session, organization_id).lock(client.id)
        if locked_client is None:
            raise NotFoundError("Клиент не найден")
        client = locked_client
        vehicle = await self._get_or_create_vehicle(
            organization_id,
            client.id,
            VehicleInput(
                make=data.client.brand,
                model=data.client.model,
                license_plate=data.client.plate,
            ),
        )
        existing_order, existing_slot = await self._reschedulable_frontend_booking(
            organization_id=organization_id,
            client=client,
            vehicle=vehicle,
        )
        (
            selected_service,
            start_time,
            chosen,
            schedule,
            duration_minutes,
        ) = await self._prepare_frontend_booking(
            organization_id=organization_id,
            service_id=data.service_id,
            selected_mechanic_id=data.selected_mechanic_id,
            booking_date=data.date,
            booking_time=data.time,
            exclude_slot_id=existing_slot.id if existing_slot is not None else None,
        )
        booking = await self._create_reserved_frontend_order(
            organization_id=organization_id,
            client=client,
            vehicle=vehicle,
            selected_service=selected_service,
            start_time=start_time,
            chosen=chosen,
            schedule=schedule,
            duration_minutes=duration_minutes,
            source=OrderSource.REFERRAL,
            existing_order=existing_order,
            existing_slot=existing_slot,
        )
        return PublicBookingRead(
            number=booking.number,
            status=booking.status,
            start_time=booking.start_time,
            end_time=booking.end_time,
        )

    async def create_booking(
        self, client_account: ClientAccount, data: BookingCreate
    ) -> BookingRead:
        await self._get_organization_or_404(data.organization_id)
        client = await self._get_or_create_client(
            data.organization_id, client_account, data.full_name
        )
        vehicle = await self._get_or_create_vehicle(data.organization_id, client.id, data.vehicle)

        duration_minutes = _DEFAULT_SLOT_MINUTES
        service_name: str | None = None
        items: list[OrderItemCreate] = []
        if data.service_id is not None:
            service_repo = ServiceRepository(self.session, data.organization_id)
            service = await service_repo.get(data.service_id)
            if service is None:
                raise NotFoundError("Услуга не найдена")
            items.append(OrderItemCreate(item_type=OrderItemType.SERVICE, service_id=service.id))
            service_name = service.name
            if service.duration_minutes:
                duration_minutes = service.duration_minutes

        order_service = OrderService(OrderRepository(self.session, data.organization_id))
        order = await order_service.create(
            OrderCreate(
                client_id=client.id,
                vehicle_id=vehicle.id,
                mechanic_id=data.mechanic_id,
                scheduled_at=data.start_time,
                items=items,
            ),
            created_by_id=None,
        )

        end_time = data.start_time + dt.timedelta(minutes=duration_minutes)
        slot_id: int | None = None
        if data.mechanic_id is not None:
            schedule_service = ScheduleService(
                ScheduleRepository(self.session, data.organization_id)
            )
            title = f"{vehicle.make} {vehicle.model}"
            if service_name:
                title += f" — {service_name}"
            slot = await schedule_service.create_slot(
                SlotCreate(
                    mechanic_id=data.mechanic_id,
                    order_id=order.id,
                    title=title,
                    start_time=data.start_time,
                    end_time=end_time,
                )
            )
            slot_id = slot.id

        return BookingRead(
            order_id=order.id,
            number=order.number,
            organization_id=data.organization_id,
            status=order.status,
            mechanic_id=data.mechanic_id,
            slot_id=slot_id,
            start_time=data.start_time,
            end_time=end_time,
        )

    # ── Кабинет клиента ──────────────────────────────────────

    async def list_my_vehicles(self, client_account_id: int) -> list[MyVehicleRead]:
        vehicles = await self.repo.list_vehicles_by_account(client_account_id)
        return [MyVehicleRead.model_validate(v) for v in vehicles]

    @staticmethod
    def _order_services(order) -> str:
        descriptions = [item.description for item in order.items if item.description]
        return ", ".join(descriptions) or "Обслуживание автомобиля"

    @staticmethod
    def _local_datetime(value: dt.datetime | None) -> str:
        if value is None:
            return "—"
        timezone = ZoneInfo(settings.SCHEDULE_TIMEZONE)
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.UTC)
        return value.astimezone(timezone).strftime("%d.%m.%Y %H:%M")

    @staticmethod
    def _maintenance(vehicle: Vehicle) -> list[ClientMaintenanceItem]:
        result = [
            ClientMaintenanceItem(
                label="Крайний пробег",
                value=(
                    f"{vehicle.mileage:,} км".replace(",", " ")
                    if vehicle.mileage is not None
                    else "Нет данных"
                ),
            )
        ]
        if vehicle.next_service_mileage is not None:
            result.append(
                ClientMaintenanceItem(
                    label="ТО",
                    value=f"рекомендовано на {vehicle.next_service_mileage:,} км".replace(",", " "),
                )
            )
        if vehicle.last_service_at is not None:
            result.append(
                ClientMaintenanceItem(
                    label="Последнее обслуживание",
                    value=vehicle.last_service_at.strftime("%d.%m.%Y"),
                )
            )
        return result

    @staticmethod
    def _client_vehicle_maintenance(
        vehicle: ClientVehicle,
    ) -> list[ClientMaintenanceItem]:
        return [
            ClientMaintenanceItem(
                label="Крайний пробег",
                value=(
                    f"{vehicle.mileage:,} км".replace(",", " ")
                    if vehicle.mileage is not None
                    else "Нет данных"
                ),
            )
        ]

    @staticmethod
    def _vehicle_identity(vehicle: Vehicle | ClientVehicle) -> tuple[str, str]:
        if vehicle.vin:
            return "vin", vehicle.vin.replace(" ", "").upper()
        plate = vehicle.plate if isinstance(vehicle, ClientVehicle) else vehicle.license_plate
        if plate:
            return "plate", plate.replace(" ", "").upper()
        return "row", str(vehicle.id)

    @classmethod
    def _unique_vehicles(cls, vehicles: list[Vehicle]) -> list[Vehicle]:
        result = []
        seen = set()
        for vehicle in vehicles:
            identity = cls._vehicle_identity(vehicle)
            if identity in seen:
                continue
            seen.add(identity)
            result.append(vehicle)
        return result

    def _repair(self, order: Order, vehicle: Vehicle) -> ClientRepairRead:
        status = order.status
        if status in {
            OrderStatus.NEW,
            OrderStatus.PRIMARY,
            OrderStatus.SECONDARY,
        }:
            current = 0
        elif status in {OrderStatus.DIAGNOSTICS, OrderStatus.IN_PROGRESS}:
            current = 1
        elif status in {OrderStatus.APPROVAL, OrderStatus.AGREEMENT, OrderStatus.WAITING}:
            current = 2
        else:
            current = 3

        def state(index: int) -> str:
            if status == OrderStatus.DONE:
                return "done"
            if index < current:
                return "done"
            if index == current:
                return "current"
            return "inactive"

        mechanic_name = order.mechanic.full_name if order.mechanic else "Мастер не назначен"
        statuses = [
            ClientRepairStatus(
                id="booked",
                title="Записан",
                subtitle=self._local_datetime(order.scheduled_at),
                color="#093095",
                state=state(0),
            ),
            ClientRepairStatus(
                id="in_progress",
                title="В работе",
                subtitle=f"Мастер: {mechanic_name}",
                color="#D45813",
                state=state(1),
            ),
            ClientRepairStatus(
                id="needs_approval",
                title="Нуждается в согласовании",
                subtitle="Ожидает вашего ответа",
                color="#430890",
                state=state(2),
                action=(
                    "Связаться с мастером"
                    if status in {OrderStatus.APPROVAL, OrderStatus.AGREEMENT}
                    else None
                ),
            ),
            ClientRepairStatus(
                id="ready",
                title="Готово",
                subtitle=(
                    "Автомобиль готов"
                    if status == OrderStatus.DONE
                    else "Ожидайте выполнения услуги"
                ),
                color="#157848",
                state=state(3),
            ),
        ]
        return ClientRepairRead(
            order_number=order.number,
            car_label=f"{vehicle.make} {vehicle.model}",
            statuses=statuses,
        )

    @staticmethod
    def _bot_label(url: str, fallback: str) -> str:
        value = url.rstrip("/").rsplit("/", 1)[-1]
        return f"@{value}" if value else fallback

    async def frontend_cars(self, client_account_id: int) -> ClientCarsRead:
        tenant_vehicles = await self.repo.list_vehicles_by_account(client_account_id)
        global_vehicles = await ClientVehicleService(self.session).list_owned(client_account_id)
        orders, _ = await self.repo.list_orders_by_account(
            client_account_id,
            limit=1000,
            offset=0,
        )
        organizations = {
            organization_id: await self.repo.get_organization_any(organization_id)
            for organization_id in {item.organization_id for item in orders}
        }
        now = dt.datetime.now(dt.UTC)
        groups: dict[tuple[str, str], list[Vehicle]] = {}
        for vehicle in tenant_vehicles:
            groups.setdefault(self._vehicle_identity(vehicle), []).append(vehicle)
        result: list[ClientCarRead] = []
        display_vehicles: list[tuple[ClientVehicle | Vehicle, list[Vehicle]]] = (
            [
                (vehicle, groups.get(self._vehicle_identity(vehicle), []))
                for vehicle in global_vehicles
            ]
            if global_vehicles
            else [(group[0], group) for group in groups.values()]
        )
        for display_vehicle, group in display_vehicles:
            vehicle_ids = {item.id for item in group}
            vehicle_orders = [item for item in orders if item.vehicle_id in vehicle_ids]
            active = [
                item
                for item in vehicle_orders
                if item.status not in {OrderStatus.DONE, OrderStatus.CANCELLED}
            ]
            future = [
                item
                for item in active
                if item.scheduled_at is not None
                and (
                    item.scheduled_at.replace(tzinfo=dt.UTC)
                    if item.scheduled_at.tzinfo is None
                    else item.scheduled_at
                )
                >= now
            ]
            next_order = (
                min(
                    future,
                    key=lambda item: item.scheduled_at if item.scheduled_at is not None else now,
                )
                if future
                else None
            )
            latest_order = active[0] if active else None
            appointment = None
            brand = (
                display_vehicle.brand
                if isinstance(display_vehicle, ClientVehicle)
                else display_vehicle.make
            )
            model = display_vehicle.model
            plate = (
                display_vehicle.plate
                if isinstance(display_vehicle, ClientVehicle)
                else display_vehicle.license_plate or ""
            )
            if next_order is not None:
                organization = organizations.get(next_order.organization_id)
                appointment = ClientAppointmentRead(
                    service_name=organization.name if organization else "Автосервис",
                    datetime=self._local_datetime(next_order.scheduled_at),
                    service=self._order_services(next_order),
                    master=(
                        next_order.mechanic.full_name
                        if next_order.mechanic is not None
                        else "Будет назначен"
                    ),
                    car=f"{brand} {model}",
                )
            repair_vehicle = group[0] if group else None
            result.append(
                ClientCarRead(
                    id=str(display_vehicle.id),
                    brand=brand,
                    model=model,
                    year=display_vehicle.year,
                    color=display_vehicle.color or "",
                    plate=plate,
                    plate_type=(
                        display_vehicle.plate_type
                        if isinstance(display_vehicle, ClientVehicle)
                        else "ru"
                    ),
                    vin=display_vehicle.vin or "",
                    mileage=display_vehicle.mileage,
                    next_appointment=appointment,
                    maintenance=(
                        self._client_vehicle_maintenance(display_vehicle)
                        if isinstance(display_vehicle, ClientVehicle)
                        else self._maintenance(display_vehicle)
                    ),
                    repair=(
                        self._repair(latest_order, repair_vehicle)
                        if latest_order is not None and repair_vehicle is not None
                        else None
                    ),
                )
            )

        bots = []
        messengers = MessengerService(self.session)
        for bot_id, fallback, icon, url in (
            (
                "tg",
                "Telegram",
                "/client/icons/my-car/tg.png",
                settings.TELEGRAM_BOT_PUBLIC_URL,
            ),
            ("vk", "VK", "/client/icons/my-car/vk.png", settings.VK_BOT_PUBLIC_URL),
            ("max", "MAX", "/client/icons/my-car/max.png", settings.MAX_BOT_PUBLIC_URL),
        ):
            if url:
                bots.append(
                    ClientBotRead(
                        id=bot_id,
                        label=self._bot_label(url, fallback),
                        icon=icon,
                        href=await messengers.link_url(
                            client_account_id,
                            NotificationChannel(bot_id if bot_id != "tg" else "telegram"),
                        ),
                    )
                )
        return ClientCarsRead(cars=result, bots=bots)

    async def list_my_orders(
        self, client_account_id: int, *, limit: int, offset: int
    ) -> tuple[list[MyOrderRead], int]:
        orders, total = await self.repo.list_orders_by_account(
            client_account_id, limit=limit, offset=offset
        )
        items = [
            MyOrderRead(
                id=o.id,
                organization_id=o.organization_id,
                number=o.number,
                status=o.status,
                status_label=_STATUS_LABELS[o.status],
                payment_status=o.payment_status,
                total_amount=o.total_amount,
                scheduled_at=o.scheduled_at,
                started_at=o.started_at,
                completed_at=o.completed_at,
                created_at=o.created_at,
            )
            for o in orders
        ]
        return items, total

    @staticmethod
    def _frontend_history_status(status: OrderStatus) -> str:
        if status in {OrderStatus.DIAGNOSTICS, OrderStatus.IN_PROGRESS}:
            return "in_progress"
        if status in {OrderStatus.APPROVAL, OrderStatus.AGREEMENT, OrderStatus.WAITING}:
            return "approval"
        if status in {OrderStatus.DONE, OrderStatus.CANCELLED}:
            return "completed"
        return "new"

    async def frontend_history(self, client_account_id: int) -> ClientHistoryRead:
        orders, _ = await self.repo.list_orders_by_account(
            client_account_id,
            limit=1000,
            offset=0,
        )
        organizations = {
            organization_id: await self.repo.get_organization_any(organization_id)
            for organization_id in {item.organization_id for item in orders}
        }
        items = []
        for order in orders:
            organization = organizations.get(order.organization_id)
            date_value = order.scheduled_at or order.created_at
            items.append(
                ClientHistoryItem(
                    id=str(order.id),
                    title=self._order_services(order),
                    status=self._frontend_history_status(order.status),
                    car_brand=(
                        f"{order.vehicle.make} {order.vehicle.model}" if order.vehicle else ""
                    ),
                    car_plate=(order.vehicle.license_plate or "") if order.vehicle else "",
                    service_name=organization.name if organization else "Автосервис",
                    service_address=organization.legal_address if organization else "",
                    master=(order.mechanic.full_name if order.mechanic else "Мастер не назначен"),
                    datetime=self._local_datetime(date_value),
                    amount=float(order.total_amount),
                    order_number=order.number,
                    order_ready=bool(order.documents),
                    month_label=f"{_RU_MONTHS[date_value.month].capitalize()} {date_value.year}",
                )
            )
        return ClientHistoryRead(items=items)

    async def frontend_order_document(
        self,
        order_id: int,
        client_account_id: int,
    ) -> tuple[bytes, str, str]:
        order = await self.repo.get_order_owned_by_account(order_id, client_account_id)
        if order is None:
            raise NotFoundError("Заказ не найден")
        document = order.document
        if document is None:
            raise NotFoundError("Заказ-наряд ещё не готов")
        return document.content, document.content_type, document.filename

    async def get_invoice(self, order_id: int, client_account_id: int) -> InvoiceRead:
        order = await self.repo.get_order_owned_by_account(order_id, client_account_id)
        if order is None:
            raise NotFoundError("Заказ не найден")
        organization = await self.repo.get_organization_any(order.organization_id)
        assert organization is not None  # organization_id всегда валиден (FK CASCADE)

        vehicle_line = f"{order.vehicle.make} {order.vehicle.model}" if order.vehicle else ""
        if order.vehicle and order.vehicle.license_plate:
            vehicle_line += f", {order.vehicle.license_plate}"

        return InvoiceRead(
            order_number=order.number,
            organization_name=organization.name,
            organization_phone=organization.phone,
            organization_address=organization.legal_address,
            client_full_name=order.client.full_name if order.client else "",
            client_phone=order.client.phone if order.client else "",
            vehicle=vehicle_line,
            items=[
                InvoiceItemRead(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                )
                for item in order.items
            ],
            total_amount=order.total_amount,
            created_at=order.created_at,
            completed_at=order.completed_at,
        )

"""Схемы модуля client_portal (Система B): discovery, бронирование, кабинет клиента."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.client_auth.phone import normalize_client_phone
from app.shared.base_schema import ORMSchema, StrictModel
from app.shared.enums import OrderStatus, PaymentStatus, ServiceCategory

# ── Discovery ──────────────────────────────────────────────


class OrganizationPublic(ORMSchema):
    id: int
    name: str
    phone: str
    legal_address: str


class ServicePublic(ORMSchema):
    id: int
    name: str
    category: ServiceCategory
    description: str | None
    base_price: Decimal
    duration_minutes: int


class MechanicPublic(ORMSchema):
    id: int
    full_name: str
    specializations: list[str]
    rating: Decimal


class SlotPublic(ORMSchema):
    id: int
    mechanic_id: int
    start_time: datetime
    end_time: datetime


class BlockPublic(ORMSchema):
    id: int
    mechanic_id: int
    start_time: datetime
    end_time: datetime


class AvailabilityRead(BaseModel):
    date: date
    slots: list[SlotPublic]
    blocks: list[BlockPublic]


# ── Бронирование ───────────────────────────────────────────


class VehicleInput(StrictModel):
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1900, le=2100)
    vin: str | None = Field(default=None, max_length=17)
    license_plate: str | None = Field(default=None, max_length=15)
    color: str | None = Field(default=None, max_length=50)
    mileage: int | None = Field(default=None, ge=0, le=999_999)


class BookingCreate(StrictModel):
    organization_id: int
    full_name: str = Field(min_length=1, max_length=255)
    vehicle: VehicleInput
    service_id: int | None = None
    mechanic_id: int | None = None  # None = "любой мастер"
    start_time: datetime


class BookingRead(BaseModel):
    order_id: int
    number: str
    organization_id: int
    status: OrderStatus
    mechanic_id: int | None
    slot_id: int | None
    start_time: datetime
    end_time: datetime


# ── Кабинет клиента ────────────────────────────────────────


class MyVehicleRead(ORMSchema):
    id: int
    organization_id: int
    client_id: int
    make: str
    model: str
    year: int | None
    license_plate: str | None
    vin: str | None
    color: str | None
    mileage: int | None
    next_service_mileage: int | None
    last_service_at: date | None


class MyOrderRead(BaseModel):
    id: int
    organization_id: int
    number: str
    status: OrderStatus
    status_label: str
    payment_status: PaymentStatus
    total_amount: Decimal
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class InvoiceItemRead(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal


class InvoiceRead(BaseModel):
    order_number: str
    organization_name: str
    organization_phone: str
    organization_address: str
    client_full_name: str
    client_phone: str
    vehicle: str
    items: list[InvoiceItemRead]
    total_amount: Decimal
    created_at: datetime
    completed_at: datetime | None


# ── Готовые проекции клиентского frontend ──────────────────


class ClientUiModel(BaseModel):
    """camelCase-контракт, который может использовать UI без знания ORM."""

    model_config = ConfigDict(populate_by_name=True)


ClientBookingServiceId: TypeAlias = int | Literal["diagnostics", "repair"]


class ServiceCardRead(ClientUiModel):
    id: str
    name: str
    address: str
    hours: str
    description: str
    rating: Decimal
    reviews: int
    last_visit: str = Field(default="", alias="lastVisit")
    logo: str = ""


class ServiceDirectoryRead(ClientUiModel):
    city: str
    yours: list[ServiceCardRead]
    all: list[ServiceCardRead]


class SelectOption(ClientUiModel):
    value: str
    label: str
    price: Decimal | None = None


class BookingMasterOption(ClientUiModel):
    id: str
    name: str
    subtitle: str


class BookingOptionsRead(ClientUiModel):
    service_options: list[SelectOption] = Field(alias="serviceOptions")
    car_options: list[SelectOption] = Field(alias="carOptions")
    masters: list[BookingMasterOption]
    # Время зависит от даты/услуги/мастера и приходит из availability.
    time_slots: list[str] = Field(default_factory=list, alias="timeSlots")


class AvailableBookingSlot(ClientUiModel):
    date: str
    time: str
    master_id: str = Field(alias="masterId")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")


class BookingAvailabilityUiRead(ClientUiModel):
    days: dict[int, bool]
    slots: list[AvailableBookingSlot]
    timezone: str


class FrontendBookingClient(ClientUiModel):
    name: str = Field(min_length=1, max_length=255)
    phone: str
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    plate_type: Literal["ru", "foreign"] = Field(default="ru", alias="plateType")
    plate: str = Field(min_length=1, max_length=15)
    consent_personal: bool = Field(alias="consentPersonal")
    consent_transfer: bool = Field(alias="consentTransfer")

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        return normalize_client_phone(value)


class FrontendBookingCreate(ClientUiModel):
    # shopId/carId/masterId — старый контракт. branchId/client/specialistId —
    # текущий клиентский frontend. Оба варианта остаются рабочими.
    shop_id: int | None = Field(default=None, alias="shopId")
    branch_id: int | None = Field(default=None, alias="branchId")
    shop_name: str | None = Field(default=None, alias="shopName")
    service_id: ClientBookingServiceId = Field(alias="serviceId")
    car_id: int | None = Field(default=None, alias="carId")
    master_id: int | Literal["any"] = Field(default="any", alias="masterId")
    specialist_id: int | Literal["any"] | None = Field(default=None, alias="specialistId")
    date: date
    time: str
    client: FrontendBookingClient | None = None

    @model_validator(mode="after")
    def validate_variants(self) -> "FrontendBookingCreate":
        if self.shop_id is None and self.branch_id is None:
            raise ValueError("Передайте shopId или branchId")
        if self.car_id is None and self.client is None:
            raise ValueError("Передайте carId или данные client")
        if self.client is not None and (
            not self.client.consent_personal or not self.client.consent_transfer
        ):
            raise ValueError("Необходимо согласие на обработку и передачу данных")
        return self

    @property
    def organization_id(self) -> int:
        value = self.branch_id if self.branch_id is not None else self.shop_id
        assert value is not None
        return value

    @property
    def selected_mechanic_id(self) -> int | Literal["any"]:
        return self.specialist_id if self.specialist_id is not None else self.master_id

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("Время должно иметь формат HH:MM") from exc
        return value


class PublicBookingCreate(ClientUiModel):
    """Гостевая запись: организацию определяет код в URL, а не тело запроса."""

    service_id: ClientBookingServiceId = Field(alias="serviceId")
    master_id: int | Literal["any"] = Field(default="any", alias="masterId")
    specialist_id: int | Literal["any"] | None = Field(default=None, alias="specialistId")
    date: date
    time: str
    client: FrontendBookingClient

    @property
    def selected_mechanic_id(self) -> int | Literal["any"]:
        return self.specialist_id if self.specialist_id is not None else self.master_id

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("Время должно иметь формат HH:MM") from exc
        return value

    @model_validator(mode="after")
    def validate_consents(self) -> "PublicBookingCreate":
        if not self.client.consent_personal or not self.client.consent_transfer:
            raise ValueError("Необходимо согласие на обработку и передачу данных")
        return self


class PublicBookingRead(ClientUiModel):
    """Безопасное подтверждение без внутренних идентификаторов."""

    number: str
    status: OrderStatus
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")


class ClientAppointmentRead(ClientUiModel):
    service_name: str = Field(alias="serviceName")
    datetime: str
    service: str
    master: str
    car: str


class ClientMaintenanceItem(ClientUiModel):
    label: str
    value: str


class ClientRepairStatus(ClientUiModel):
    id: str
    title: str
    subtitle: str
    color: str
    state: Literal["done", "current", "inactive"]
    action: str | None = None


class ClientRepairRead(ClientUiModel):
    order_number: str = Field(alias="orderNumber")
    car_label: str = Field(alias="carLabel")
    statuses: list[ClientRepairStatus]


class ClientCarRead(ClientUiModel):
    id: str
    brand: str
    model: str = ""
    year: int | None
    color: str
    plate: str
    plate_type: Literal["ru", "foreign"] = Field(default="ru", alias="plateType")
    vin: str
    mileage: int | None = None
    next_appointment: ClientAppointmentRead | None = Field(alias="nextAppointment")
    maintenance: list[ClientMaintenanceItem]
    repair: ClientRepairRead | None


class ClientBotRead(ClientUiModel):
    id: str
    label: str
    icon: str
    href: str


class ClientCarsRead(ClientUiModel):
    cars: list[ClientCarRead]
    bots: list[ClientBotRead]


class BranchRead(ClientUiModel):
    id: str
    name: str
    address: str
    is_open: bool = Field(alias="isOpen")
    until: str
    map_src: str = Field(alias="mapSrc")


class BranchDirectoryRead(ClientUiModel):
    city: str
    branches: list[BranchRead]


class SpecialistRead(ClientUiModel):
    id: str
    name: str
    role: str
    avatar_color: str = Field(alias="avatarColor")
    rating: Decimal
    reviews: int
    price: Decimal
    nearest_date: str = Field(alias="nearestDate")
    slots: list[str]


class SpecialistDirectoryRead(ClientUiModel):
    specialists: list[SpecialistRead]


class ClientHistoryItem(ClientUiModel):
    id: str
    title: str
    status: Literal["new", "in_progress", "approval", "completed"]
    car_brand: str = Field(alias="carBrand")
    car_plate: str = Field(alias="carPlate")
    service_name: str = Field(alias="serviceName")
    service_address: str = Field(alias="serviceAddress")
    master: str
    datetime: str
    amount: float
    order_number: str = Field(alias="orderNumber")
    order_ready: bool = Field(alias="orderReady")
    month_label: str = Field(alias="monthLabel")


class ClientHistoryRead(ClientUiModel):
    items: list[ClientHistoryItem]

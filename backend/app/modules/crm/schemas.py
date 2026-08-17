"""Контракты CRM, совпадающие с полями административного frontend."""

from decimal import Decimal

from pydantic import ConfigDict, EmailStr, Field, field_validator, model_validator

from app.shared.base_schema import StrictModel
from app.shared.enums import OrderSource, OrderStatus


class CrmModel(StrictModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CrmOrderLine(CrmModel):
    service_id: int = Field(alias="serviceId")
    price: Decimal = Field(ge=0)
    discount: Decimal = Field(default=Decimal(0), ge=0, le=100)
    master_id: int | None = Field(default=None, alias="masterId")


class CrmOrderWrite(CrmModel):
    status: OrderStatus = OrderStatus.NEW
    client_name: str = Field(default="", max_length=255, alias="clientName")
    phone: str = Field(default="", max_length=20)
    email: EmailStr | None = None
    description: str = ""
    date: str = ""
    time: str = ""
    source: OrderSource = OrderSource.OTHER
    lines: list[CrmOrderLine] = Field(default_factory=list)
    plate: str = Field(default="", max_length=15)
    brand: str = Field(default="", max_length=100)
    model: str = Field(default="", max_length=100)
    year: int | None = Field(default=None, ge=1900, le=2100)
    color: str = Field(default="", max_length=50)
    vin: str = Field(default="", max_length=17)
    mileage: int | None = Field(default=None, ge=0, le=999_999)

    @model_validator(mode="before")
    @classmethod
    def ignore_frontend_read_fields(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        read_only_fields = {"id", "number", "amount", "services", "master", "masters"}
        return {key: item for key, item in value.items() if key not in read_only_fields}

    @field_validator("source", mode="before")
    @classmethod
    def blank_source_is_other(cls, value: object) -> object:
        return OrderSource.OTHER if value in (None, "") else value

    @field_validator("email", mode="before")
    @classmethod
    def blank_email_is_none(cls, value: object) -> object:
        return None if value == "" else value

    @field_validator("year", mode="before")
    @classmethod
    def blank_year_is_none(cls, value: object) -> object:
        return None if value == "" else value

    @model_validator(mode="after")
    def validate_frontend_stage(self) -> "CrmOrderWrite":
        if self.status in {OrderStatus.AGREEMENT, OrderStatus.CANCELLED}:
            raise ValueError("Этот статус не используется на CRM-доске")
        return self


class CrmOrderStatusUpdate(CrmModel):
    status: OrderStatus

    @model_validator(mode="after")
    def validate_frontend_stage(self) -> "CrmOrderStatusUpdate":
        if self.status in {OrderStatus.AGREEMENT, OrderStatus.CANCELLED}:
            raise ValueError("Этот статус не используется на CRM-доске")
        return self


class CrmDocument(CrmModel):
    id: int
    color: str
    title: str
    meta: str
    date: str
    download_url: str = Field(alias="downloadUrl")


class CrmOrderLineRead(CrmOrderLine):
    id: int


class CrmOrderRead(CrmModel):
    id: int
    number: int
    status: OrderStatus
    client_name: str = Field(alias="clientName")
    phone: str
    email: str
    description: str
    date: str
    time: str
    source: OrderSource
    plate: str
    brand: str
    model: str
    car_brand: str = Field(alias="carBrand")
    car_year: int | None = Field(alias="carYear")
    year: int | None
    color: str
    vin: str
    mileage: int | None
    amount: Decimal
    services: list[str]
    master: str
    masters: str
    lines: list[CrmOrderLineRead]
    documents: list[CrmDocument]
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class CrmColumn(CrmModel):
    id: OrderStatus
    title: str
    gradient: str
    items: list[CrmOrderRead]


class CrmClientBrief(CrmModel):
    id: int
    name: str
    phone: str
    email: str


class CrmBulkDelete(CrmModel):
    ids: list[int] = Field(min_length=1, max_length=100)

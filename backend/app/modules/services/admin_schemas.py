"""Flat service contracts expected by the ready-made admin services screen."""

from decimal import Decimal

from pydantic import ConfigDict, Field, model_validator

from app.shared.base_schema import StrictModel


class AdminServiceModel(StrictModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ServiceMasterBrief(AdminServiceModel):
    id: int
    name: str
    role: str


class AdminServiceRead(AdminServiceModel):
    id: int
    title: str
    description: str
    category: str
    price_type: str = Field(alias="priceType")
    price: Decimal
    price_to: Decimal | None = Field(alias="priceTo")
    price_note: str = Field(alias="priceNote")
    duration_hours: Decimal = Field(alias="durationHours")
    orders_count: int = Field(alias="ordersCount")
    status: str
    master: ServiceMasterBrief | None
    masters: list[ServiceMasterBrief]
    notes: str


class AdminServiceWrite(AdminServiceModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    category: str
    price_type: str = Field(default="fixed", alias="priceType")
    price: Decimal = Field(default=Decimal(0), ge=0)
    price_to: Decimal | None = Field(default=None, ge=0, alias="priceTo")
    duration: Decimal = Field(default=Decimal(0), ge=0)
    duration_unit: str = Field(default="minutes", alias="durationUnit")
    status: str = "active"
    masters: list[int | str] = Field(default_factory=list)
    notes: str = ""

    @model_validator(mode="after")
    def validate_options(self) -> "AdminServiceWrite":
        if self.price_type not in {"fixed", "range", "negotiable"}:
            raise ValueError("Неизвестный тип цены")
        if self.duration_unit not in {"minutes", "hours"}:
            raise ValueError("durationUnit должен быть minutes или hours")
        if self.status not in {"active", "hidden"}:
            raise ValueError("status должен быть active или hidden")
        if self.price_type == "range" and self.price_to is not None and self.price_to < self.price:
            raise ValueError("priceTo должен быть не меньше price")
        if any(isinstance(value, str) and value != "all" for value in self.masters):
            raise ValueError("masters содержит неизвестный идентификатор")
        return self


class AdminServiceBulkDelete(AdminServiceModel):
    ids: list[int] = Field(min_length=1, max_length=100)

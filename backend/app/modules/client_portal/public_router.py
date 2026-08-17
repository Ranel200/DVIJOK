"""HTTP API гостевой записи без регистрации и без раскрытия tenant ID в URL."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import public_booking_rate_limit
from app.modules.client_portal.public_service import PublicBookingService
from app.modules.client_portal.schemas import (
    BookingAvailabilityUiRead,
    BookingOptionsRead,
    BranchDirectoryRead,
    ClientBookingServiceId,
    PublicBookingCreate,
    PublicBookingRead,
    SpecialistDirectoryRead,
)

router = APIRouter(prefix="/public-booking", tags=["public-booking"])

PublicCode = Annotated[
    str,
    Path(
        min_length=16,
        max_length=16,
        pattern=r"^[A-Za-z0-9_-]{16}$",
        description="Постоянный непрозрачный публичный код автосервиса",
    ),
]


def get_public_booking_service(
    db: AsyncSession = Depends(get_db, scope="function"),
) -> PublicBookingService:
    return PublicBookingService(db)


@router.get("/{code}", response_model=BranchDirectoryRead)
async def public_booking_context(
    code: PublicCode,
    service: PublicBookingService = Depends(get_public_booking_service),
) -> BranchDirectoryRead:
    return await service.context(code)


@router.get("/{code}/options", response_model=BookingOptionsRead)
async def public_booking_options(
    code: PublicCode,
    service: PublicBookingService = Depends(get_public_booking_service),
) -> BookingOptionsRead:
    return await service.options(code)


@router.get("/{code}/specialists", response_model=SpecialistDirectoryRead)
async def public_booking_specialists(
    code: PublicCode,
    service: PublicBookingService = Depends(get_public_booking_service),
) -> SpecialistDirectoryRead:
    return await service.specialists(code)


@router.get("/{code}/availability", response_model=BookingAvailabilityUiRead)
async def public_booking_availability(
    code: PublicCode,
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=0, le=11),
    service_id: ClientBookingServiceId | None = Query(default=None, alias="serviceId"),
    specialist_id: int | Literal["any"] = Query(default="any", alias="specialistId"),
    service: PublicBookingService = Depends(get_public_booking_service),
) -> BookingAvailabilityUiRead:
    return await service.availability(
        code=code,
        year=year,
        month=month,
        service_id=service_id,
        specialist_id=specialist_id,
    )


@router.post(
    "/{code}",
    response_model=PublicBookingRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(public_booking_rate_limit)],
)
async def create_public_booking(
    code: PublicCode,
    payload: PublicBookingCreate,
    service: PublicBookingService = Depends(get_public_booking_service),
) -> PublicBookingRead:
    return await service.create(code, payload)

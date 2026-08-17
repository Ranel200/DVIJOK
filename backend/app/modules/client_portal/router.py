"""HTTP-роутер модуля client_portal (Система B): discovery, бронирование, кабинет.

Доступ везде — по клиентскому JWT (get_current_client), не пересекается со
staff-контуром (require_roles/get_current_user).
"""

import datetime as dt
from typing import Literal
from urllib.parse import quote

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_client
from app.core.pagination import Page, PaginationParams
from app.modules.client_auth.models import ClientAccount
from app.modules.client_portal.schemas import (
    AvailabilityRead,
    BookingAvailabilityUiRead,
    BookingCreate,
    BookingOptionsRead,
    BookingRead,
    BranchDirectoryRead,
    ClientBookingServiceId,
    ClientCarsRead,
    ClientHistoryRead,
    FrontendBookingCreate,
    InvoiceRead,
    MechanicPublic,
    MyOrderRead,
    MyVehicleRead,
    OrganizationPublic,
    ServiceDirectoryRead,
    ServicePublic,
    SpecialistDirectoryRead,
)
from app.modules.client_portal.service import ClientPortalService

router = APIRouter(
    prefix="/client-portal",
    tags=["client-portal"],
    dependencies=[Depends(get_current_client)],
)

frontend_router = APIRouter(
    tags=["client-frontend"],
    dependencies=[Depends(get_current_client)],
)


def get_client_portal_service(
    db: AsyncSession = Depends(get_db, scope="function"),
) -> ClientPortalService:
    return ClientPortalService(db)


@router.get("/organizations", response_model=list[OrganizationPublic])
async def list_organizations(
    service: ClientPortalService = Depends(get_client_portal_service),
) -> list[OrganizationPublic]:
    return await service.list_organizations()


@router.get("/organizations/{organization_id}/services", response_model=list[ServicePublic])
async def list_organization_services(
    organization_id: int, service: ClientPortalService = Depends(get_client_portal_service)
) -> list[ServicePublic]:
    return await service.list_services(organization_id)


@router.get("/organizations/{organization_id}/mechanics", response_model=list[MechanicPublic])
async def list_organization_mechanics(
    organization_id: int, service: ClientPortalService = Depends(get_client_portal_service)
) -> list[MechanicPublic]:
    return await service.list_mechanics(organization_id)


@router.get("/organizations/{organization_id}/availability", response_model=AvailabilityRead)
async def get_availability(
    organization_id: int,
    day: dt.date = Query(..., alias="date", description="Дата для проверки доступности"),
    mechanic_id: int | None = Query(default=None),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> AvailabilityRead:
    return await service.get_availability(organization_id, day, mechanic_id)


@router.post("/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> BookingRead:
    return await service.create_booking(client_account, payload)


@router.get("/me/vehicles", response_model=list[MyVehicleRead])
async def list_my_vehicles(
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> list[MyVehicleRead]:
    return await service.list_my_vehicles(client_account.id)


@router.get("/me/orders", response_model=Page[MyOrderRead])
async def list_my_orders(
    pagination: PaginationParams = Depends(),
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> Page[MyOrderRead]:
    items, total = await service.list_my_orders(
        client_account.id, limit=pagination.limit, offset=pagination.offset
    )
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get("/me/orders/{order_id}/invoice", response_model=InvoiceRead)
async def get_my_order_invoice(
    order_id: int,
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> InvoiceRead:
    return await service.get_invoice(order_id, client_account.id)


# Готовые контракты существующего client frontend. Базовые endpoint'ы выше
# остаются стабильными для других API consumers.


@router.get("/ui/services", response_model=ServiceDirectoryRead)
async def frontend_services(
    query: str = Query(default="", max_length=200),
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> ServiceDirectoryRead:
    return await service.frontend_service_directory(client_account.id, query)


@router.get("/ui/booking/options", response_model=BookingOptionsRead)
async def frontend_booking_options(
    shop_id: int | None = Query(default=None, alias="shopId"),
    branch_id: int | None = Query(default=None, alias="branchId"),
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> BookingOptionsRead:
    organization_id = branch_id if branch_id is not None else shop_id
    if organization_id is None:
        from app.core.exceptions import BusinessRuleError

        raise BusinessRuleError("Передайте shopId или branchId")
    return await service.frontend_booking_options(client_account.id, organization_id)


@router.get("/ui/booking/availability", response_model=BookingAvailabilityUiRead)
async def frontend_booking_availability(
    shop_id: int | None = Query(default=None, alias="shopId"),
    branch_id: int | None = Query(default=None, alias="branchId"),
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=0, le=11),
    service_id: ClientBookingServiceId | None = Query(default=None, alias="serviceId"),
    master_id: int | Literal["any"] = Query(default="any", alias="masterId"),
    specialist_id: int | Literal["any"] | None = Query(default=None, alias="specialistId"),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> BookingAvailabilityUiRead:
    from app.core.exceptions import BusinessRuleError

    organization_id = branch_id if branch_id is not None else shop_id
    if organization_id is None:
        raise BusinessRuleError("Передайте shopId или branchId")
    return await service.frontend_booking_availability(
        organization_id=organization_id,
        year=year,
        month=month,
        service_id=service_id,
        master_id=specialist_id if specialist_id is not None else master_id,
    )


@frontend_router.get("/branches", response_model=BranchDirectoryRead)
async def frontend_branches(
    service: ClientPortalService = Depends(get_client_portal_service),
) -> BranchDirectoryRead:
    return await service.frontend_branches()


@frontend_router.get(
    "/booking/specialists",
    response_model=SpecialistDirectoryRead,
)
async def frontend_specialists(
    branch_id: int = Query(..., alias="branchId"),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> SpecialistDirectoryRead:
    return await service.frontend_specialists(branch_id)


@router.post(
    "/ui/booking",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
)
async def frontend_create_booking(
    payload: FrontendBookingCreate,
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> BookingRead:
    return await service.create_frontend_booking(client_account, payload)


@router.get("/ui/cars", response_model=ClientCarsRead)
async def frontend_cars(
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> ClientCarsRead:
    return await service.frontend_cars(client_account.id)


@router.get("/ui/history", response_model=ClientHistoryRead)
async def frontend_history(
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> ClientHistoryRead:
    return await service.frontend_history(client_account.id)


@router.get("/ui/history/{order_id}/document", response_class=Response)
async def frontend_order_document(
    order_id: int,
    client_account: ClientAccount = Depends(get_current_client),
    service: ClientPortalService = Depends(get_client_portal_service),
) -> Response:
    content, content_type, filename = await service.frontend_order_document(
        order_id,
        client_account.id,
    )
    safe_filename = filename.replace('"', "").replace("\r", "").replace("\n", "")
    encoded_filename = quote(safe_filename, safe="")
    disposition = "inline" if content_type == "application/pdf" else "attachment"
    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": (
                f"{disposition}; filename=order-document; filename*=UTF-8''{encoded_filename}"
            )
        },
    )

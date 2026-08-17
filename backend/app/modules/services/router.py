"""HTTP-роутер модуля services. Чтение — любой авторизованный сотрудник;
управление каталогом — ADMIN и MANAGER."""

from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_feature, require_roles
from app.core.pagination import Page, PaginationParams
from app.modules.services.admin_schemas import (
    AdminServiceBulkDelete,
    AdminServiceRead,
    AdminServiceWrite,
    ServiceMasterBrief,
)
from app.modules.services.admin_service import AdminServiceCatalog
from app.modules.services.importer import build_template
from app.modules.services.repository import ServiceRepository
from app.modules.services.schemas import (
    ServiceCreate,
    ServiceImportReport,
    ServiceRead,
    ServiceSummary,
    ServiceUpdate,
)
from app.modules.services.service import ServiceCatalogService
from app.modules.users.models import User
from app.shared.enums import ServiceCategory, UserRole

router = APIRouter(
    prefix="/services",
    tags=["services"],
    dependencies=[
        Depends(
            require_feature(
                "services", UserRole.ADMIN, UserRole.MANAGER, UserRole.MECHANIC
            )
        )
    ],
)

manage = require_roles(UserRole.ADMIN, UserRole.MANAGER)


def get_catalog_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> ServiceCatalogService:
    return ServiceCatalogService(ServiceRepository(db, current_user.organization_id))


def get_admin_catalog(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> AdminServiceCatalog:
    return AdminServiceCatalog(ServiceRepository(db, current_user.organization_id))


@router.get("", response_model=Page[ServiceRead])
async def list_services(
    pagination: PaginationParams = Depends(),
    query: str | None = Query(default=None, description="Поиск по названию"),
    category: ServiceCategory | None = Query(default=None),
    active_only: bool = Query(default=False),
    service: ServiceCatalogService = Depends(get_catalog_service),
) -> Page[ServiceRead]:
    items, total = await service.list_page(
        query=query,
        category=category,
        active_only=active_only,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def create_service(
    payload: ServiceCreate, service: ServiceCatalogService = Depends(get_catalog_service)
) -> ServiceRead:
    return ServiceRead.model_validate(await service.create(payload))


async def _read_upload(file: UploadFile) -> bytes:
    # One extra byte makes oversized files detectable without unbounded reads.
    from app.core.config import settings

    return await file.read(settings.SERVICE_IMPORT_MAX_FILE_BYTES + 1)


@router.get(
    "/import/template",
    dependencies=[Depends(manage)],
    response_class=StreamingResponse,
)
async def download_import_template() -> StreamingResponse:
    return StreamingResponse(
        BytesIO(build_template()),
        media_type=("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        headers={"Content-Disposition": 'attachment; filename="services-import-template.xlsx"'},
    )


@router.post(
    "/import/preview",
    response_model=ServiceImportReport,
    dependencies=[Depends(manage)],
)
async def preview_import(
    file: Annotated[UploadFile, File()],
    service: ServiceCatalogService = Depends(get_catalog_service),
) -> ServiceImportReport:
    return await service.preview_import(await _read_upload(file), file.filename)


@router.post(
    "/import",
    response_model=ServiceImportReport,
    dependencies=[Depends(manage)],
)
async def apply_import(
    response: Response,
    file: Annotated[UploadFile, File()],
    service: ServiceCatalogService = Depends(get_catalog_service),
) -> ServiceImportReport:
    report = await service.apply_import(await _read_upload(file), file.filename)
    if not report.valid:
        response.status_code = 422
    return report


@router.get("/summary", response_model=ServiceSummary)
async def service_summary(
    service: ServiceCatalogService = Depends(get_catalog_service),
) -> ServiceSummary:
    return await service.summary()


@router.get("/masters", response_model=list[ServiceMasterBrief])
async def list_service_masters(
    service: AdminServiceCatalog = Depends(get_admin_catalog),
) -> list[ServiceMasterBrief]:
    """Dedicated selector source: order services can only be assigned to masters."""

    return await service.masters()


@router.get("/admin", response_model=list[AdminServiceRead])
async def list_admin_services(
    service: AdminServiceCatalog = Depends(get_admin_catalog),
) -> list[AdminServiceRead]:
    return await service.list()


@router.post(
    "/admin",
    response_model=AdminServiceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def create_admin_service(
    payload: AdminServiceWrite,
    service: AdminServiceCatalog = Depends(get_admin_catalog),
) -> AdminServiceRead:
    return await service.create(payload)


@router.delete(
    "/admin/bulk",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(manage)],
)
async def delete_admin_services(
    payload: AdminServiceBulkDelete,
    service: AdminServiceCatalog = Depends(get_admin_catalog),
) -> None:
    await service.delete_many(payload.ids)


@router.get("/admin/{service_id}", response_model=AdminServiceRead)
async def get_admin_service(
    service_id: int,
    service: AdminServiceCatalog = Depends(get_admin_catalog),
) -> AdminServiceRead:
    return await service.get(service_id)


@router.put(
    "/admin/{service_id}",
    response_model=AdminServiceRead,
    dependencies=[Depends(manage)],
)
async def update_admin_service(
    service_id: int,
    payload: AdminServiceWrite,
    service: AdminServiceCatalog = Depends(get_admin_catalog),
) -> AdminServiceRead:
    return await service.update(service_id, payload)


@router.delete(
    "/admin/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(manage)],
)
async def delete_admin_service(
    service_id: int,
    service: AdminServiceCatalog = Depends(get_admin_catalog),
) -> None:
    await service.delete(service_id)


@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(
    service_id: int, service: ServiceCatalogService = Depends(get_catalog_service)
) -> ServiceRead:
    return ServiceRead.model_validate(await service.get(service_id))


@router.patch("/{service_id}", response_model=ServiceRead, dependencies=[Depends(manage)])
async def update_service(
    service_id: int,
    payload: ServiceUpdate,
    service: ServiceCatalogService = Depends(get_catalog_service),
) -> ServiceRead:
    return ServiceRead.model_validate(await service.update(service_id, payload))


@router.delete(
    "/{service_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(manage)]
)
async def delete_service(
    service_id: int, service: ServiceCatalogService = Depends(get_catalog_service)
) -> None:
    await service.delete(service_id)

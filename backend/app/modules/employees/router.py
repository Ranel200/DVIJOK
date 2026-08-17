"""Единый CRUD сотрудников для административного приложения."""

from urllib.parse import quote

from fastapi import APIRouter, Depends, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.modules.employees.documents import (
    MAX_EMPLOYEE_DOCUMENT_BYTES,
    EmployeeDocumentService,
)
from app.modules.employees.schemas import (
    EmployeeCreate,
    EmployeeDocumentRead,
    EmployeeRead,
    EmployeeUpdate,
)
from app.modules.employees.service import EmployeeService
from app.modules.users.models import User
from app.shared.enums import UserRole

router = APIRouter(prefix="/employees", tags=["employees"])
admin_only = require_roles(UserRole.ADMIN)


def get_employee_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(admin_only),
) -> EmployeeService:
    return EmployeeService(db, current_user.organization_id)


def get_employee_document_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(admin_only),
) -> EmployeeDocumentService:
    return EmployeeDocumentService(db, current_user.organization_id)


@router.get("", response_model=list[EmployeeRead])
async def list_employees(
    service: EmployeeService = Depends(get_employee_service),
) -> list[EmployeeRead]:
    return await service.list()


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeRead:
    return await service.create(payload)


@router.get("/{user_id}", response_model=EmployeeRead)
async def get_employee(
    user_id: int,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeRead:
    return await service.get(user_id)


@router.patch("/{user_id}", response_model=EmployeeRead)
async def update_employee(
    user_id: int,
    payload: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeRead:
    return await service.update(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_employee(
    user_id: int,
    current_user: User = Depends(admin_only),
    service: EmployeeService = Depends(get_employee_service),
) -> None:
    await service.deactivate(user_id, current_user.id)


@router.get("/{user_id}/documents", response_model=list[EmployeeDocumentRead])
async def list_employee_documents(
    user_id: int,
    service: EmployeeDocumentService = Depends(get_employee_document_service),
) -> list[EmployeeDocumentRead]:
    return await service.list(user_id)


@router.post("/{user_id}/documents/{kind}", response_model=EmployeeDocumentRead)
async def upload_employee_document(
    user_id: int,
    kind: str,
    file: UploadFile,
    current_user: User = Depends(admin_only),
    service: EmployeeDocumentService = Depends(get_employee_document_service),
) -> EmployeeDocumentRead:
    return await service.save(
        user_id,
        kind,
        filename=file.filename,
        content_type=file.content_type,
        content=await file.read(MAX_EMPLOYEE_DOCUMENT_BYTES + 1),
        created_by_id=current_user.id,
    )


@router.get("/{user_id}/documents/{document_id}/content", response_class=Response)
async def download_employee_document(
    user_id: int,
    document_id: int,
    service: EmployeeDocumentService = Depends(get_employee_document_service),
) -> Response:
    document = await service.get(user_id, document_id)
    encoded_name = quote(document.filename, safe="")
    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}",
            "Content-Length": str(document.size_bytes),
            "X-Content-SHA256": document.sha256,
        },
    )


@router.delete("/{user_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee_document(
    user_id: int,
    document_id: int,
    service: EmployeeDocumentService = Depends(get_employee_document_service),
) -> None:
    await service.delete(user_id, document_id)

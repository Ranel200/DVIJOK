"""Validation, storage, and tenant isolation for personnel files."""

import hashlib
from pathlib import Path

from sqlalchemy import select

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.employees.models import EmployeeDocument
from app.modules.employees.schemas import EmployeeDocumentRead
from app.modules.users.models import User

MAX_EMPLOYEE_DOCUMENT_BYTES = 2 * 1024 * 1024
EMPLOYEE_DOCUMENT_KINDS = {"passport", "inn", "medicalBook"}
_ALLOWED_TYPES = {
    "application/pdf": {".pdf"},
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
    "image/gif": {".gif"},
}


class EmployeeDocumentService:
    def __init__(self, session, organization_id: int) -> None:
        self.session = session
        self.organization_id = organization_id

    async def _employee(self, user_id: int) -> User:
        user = (
            await self.session.execute(
                select(User).where(
                    User.id == user_id,
                    User.organization_id == self.organization_id,
                )
            )
        ).scalar_one_or_none()
        if user is None:
            raise NotFoundError("Сотрудник не найден")
        return user

    @staticmethod
    def _read(document: EmployeeDocument) -> EmployeeDocumentRead:
        return EmployeeDocumentRead(
            id=document.id,
            kind=document.kind,
            name=document.filename,
            file_name=document.filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            sha256=document.sha256,
            download_url=(
                f"/api/v1/employees/{document.user_id}/documents/{document.id}/content"
            ),
        )

    async def list(self, user_id: int) -> list[EmployeeDocumentRead]:
        await self._employee(user_id)
        documents = list(
            (
                await self.session.execute(
                    select(EmployeeDocument)
                    .where(
                        EmployeeDocument.user_id == user_id,
                        EmployeeDocument.organization_id == self.organization_id,
                    )
                    .order_by(EmployeeDocument.id)
                )
            )
            .scalars()
            .all()
        )
        return [self._read(document) for document in documents]

    async def get(self, user_id: int, document_id: int) -> EmployeeDocument:
        await self._employee(user_id)
        document = (
            await self.session.execute(
                select(EmployeeDocument).where(
                    EmployeeDocument.id == document_id,
                    EmployeeDocument.user_id == user_id,
                    EmployeeDocument.organization_id == self.organization_id,
                )
            )
        ).scalar_one_or_none()
        if document is None:
            raise NotFoundError("Документ сотрудника не найден")
        return document

    @staticmethod
    def _validate(kind: str, filename: str | None, content_type: str | None, content: bytes):
        if kind not in EMPLOYEE_DOCUMENT_KINDS:
            raise BusinessRuleError("Неизвестный тип документа сотрудника")
        safe_name = Path(filename or "").name
        media_type = (content_type or "").split(";", 1)[0].strip().lower()
        suffix = Path(safe_name).suffix.lower()
        invalid_type = media_type not in _ALLOWED_TYPES
        invalid_suffix = not invalid_type and suffix not in _ALLOWED_TYPES[media_type]
        if not safe_name or invalid_type or invalid_suffix:
            raise BusinessRuleError("Поддерживаются PDF, JPEG, PNG, WebP и GIF")
        if not content:
            raise BusinessRuleError("Файл пуст")
        if len(content) > MAX_EMPLOYEE_DOCUMENT_BYTES:
            raise BusinessRuleError("Размер файла превышает 2 МБ")
        if media_type == "application/pdf" and not content.startswith(b"%PDF-"):
            raise BusinessRuleError("Содержимое файла не является PDF")
        if media_type == "image/jpeg" and not content.startswith(b"\xff\xd8\xff"):
            raise BusinessRuleError("Содержимое файла не является JPEG")
        if media_type == "image/png" and not content.startswith(b"\x89PNG\r\n\x1a\n"):
            raise BusinessRuleError("Содержимое файла не является PNG")
        if media_type == "image/webp" and not (
            content.startswith(b"RIFF") and content[8:12] == b"WEBP"
        ):
            raise BusinessRuleError("Содержимое файла не является WebP")
        if media_type == "image/gif" and not content.startswith((b"GIF87a", b"GIF89a")):
            raise BusinessRuleError("Содержимое файла не является GIF")
        return safe_name, media_type

    async def save(
        self,
        user_id: int,
        kind: str,
        *,
        filename: str | None,
        content_type: str | None,
        content: bytes,
        created_by_id: int,
    ) -> EmployeeDocumentRead:
        user = await self._employee(user_id)
        safe_name, media_type = self._validate(kind, filename, content_type, content)
        document = (
            await self.session.execute(
                select(EmployeeDocument).where(
                    EmployeeDocument.user_id == user_id,
                    EmployeeDocument.kind == kind,
                )
            )
        ).scalar_one_or_none()
        if document is None:
            document = EmployeeDocument(
                organization_id=self.organization_id,
                user_id=user_id,
                kind=kind,
            )
            self.session.add(document)
        document.filename = safe_name
        document.content_type = media_type
        document.size_bytes = len(content)
        document.sha256 = hashlib.sha256(content).hexdigest()
        document.content = content
        document.created_by_id = created_by_id
        metadata = dict(user.documents or {})
        metadata[kind] = {"name": safe_name, "fileName": safe_name}
        user.documents = metadata
        await self.session.flush()
        return self._read(document)

    async def delete(self, user_id: int, document_id: int) -> None:
        user = await self._employee(user_id)
        document = await self.get(user_id, document_id)
        metadata = dict(user.documents or {})
        metadata[document.kind] = None
        user.documents = metadata
        await self.session.delete(document)
        await self.session.flush()

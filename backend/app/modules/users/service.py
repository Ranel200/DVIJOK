"""Бизнес-логика модуля users (управление сотрудниками)."""

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.roles import STAFF_ROLE_TO_TECHNICAL, default_staff_role
from app.modules.users.schemas import UserCreate, UserUpdate
from app.shared.identifiers import normalize_login, normalize_phone


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def get(self, user_id: int) -> User:
        user = await self.repo.get(user_id)
        if user is None:
            raise NotFoundError("Сотрудник не найден")
        return user

    async def list_page(self, *, limit: int, offset: int) -> tuple[list[User], int]:
        items = await self.repo.list(limit=limit, offset=offset)
        total = await self.repo.count()
        return items, total

    async def create(self, data: UserCreate) -> User:
        email = data.email.strip().lower()
        if await self.repo.get_by_email(email):
            raise ConflictError("Сотрудник с таким email уже существует")
        phone = normalize_phone(data.phone)
        if data.phone and phone is None:
            raise BusinessRuleError("Некорректный номер телефона")
        if phone is not None and await self.repo.get_by_phone(phone):
            raise ConflictError("Сотрудник с таким телефоном уже существует")
        login = normalize_login(data.login)
        if login is not None and await self.repo.get_by_login(login):
            raise ConflictError("Сотрудник с таким логином уже существует")
        staff_role_key = data.staff_role_key or default_staff_role(data.role)
        if STAFF_ROLE_TO_TECHNICAL.get(staff_role_key) != data.role:
            raise BusinessRuleError("Должность не соответствует системной роли")
        user = User(
            email=email,
            full_name=data.full_name,
            phone=phone,
            normalized_phone=phone,
            login=login,
            role=data.role,
            staff_role_key=staff_role_key,
            rate=data.rate,
            calendar_color=data.calendar_color,
            duties=data.duties,
            ui_permissions=data.ui_permissions,
            hashed_password=hash_password(data.password),
        )
        return await self.repo.add(user)

    async def update(self, user_id: int, data: UserUpdate) -> User:
        user = await self.get(user_id)
        payload = data.model_dump(exclude_unset=True)
        if "phone" in payload:
            phone = normalize_phone(payload["phone"])
            if payload["phone"] and phone is None:
                raise BusinessRuleError("Некорректный номер телефона")
            existing = await self.repo.get_by_phone(phone) if phone else None
            if existing is not None and existing.id != user.id:
                raise ConflictError("Сотрудник с таким телефоном уже существует")
            payload["phone"] = phone
            user.normalized_phone = phone
        if "login" in payload:
            login = normalize_login(payload["login"])
            existing = await self.repo.get_by_login(login) if login else None
            if existing is not None and existing.id != user.id:
                raise ConflictError("Сотрудник с таким логином уже существует")
            payload["login"] = login
        if "role" in payload and "staff_role_key" not in payload:
            payload["staff_role_key"] = default_staff_role(payload["role"])
        target_role = payload.get("role", user.role)
        role_key = payload.get("staff_role_key", user.staff_role_key)
        if STAFF_ROLE_TO_TECHNICAL.get(role_key) != target_role:
            raise BusinessRuleError("Должность не соответствует системной роли")
        payload["staff_role_key"] = role_key
        if "password" in payload:
            user.hashed_password = hash_password(payload.pop("password"))
        for field, value in payload.items():
            setattr(user, field, value)
        return await self.repo.add(user)

    async def delete(self, user_id: int) -> None:
        await self.repo.delete(await self.get(user_id))

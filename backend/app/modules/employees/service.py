"""Оркестрация User и Mechanic как одной административной карточки."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.modules.employees.schemas import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.modules.mechanics.models import Mechanic
from app.modules.users.models import User
from app.modules.users.roles import (
    STAFF_ROLE_TO_TECHNICAL,
    default_staff_role,
)
from app.shared.enums import UserRole
from app.shared.identifiers import normalize_login, normalize_phone


class EmployeeService:
    def __init__(self, session: AsyncSession, organization_id: int) -> None:
        self.session = session
        self.organization_id = organization_id

    @staticmethod
    def _read(user: User) -> EmployeeRead:
        mechanic = user.mechanic
        return EmployeeRead(
            id=user.id,
            mechanic_id=mechanic.id if mechanic else None,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            login=user.login,
            role=user.role,
            staff_role_key=user.staff_role_key,
            rate=user.rate,
            is_active=user.is_active,
            is_owner=user.is_owner,
            calendar_color=user.calendar_color,
            duties=user.duties,
            ui_permissions=user.ui_permissions,
            documents=user.documents,
            specializations=mechanic.specializations if mechanic else [],
            hired_year=mechanic.hired_year if mechanic else None,
            hourly_rate=mechanic.hourly_rate if mechanic else Decimal(0),
            commission_percent=mechanic.commission_percent if mechanic else Decimal(0),
            rating=mechanic.rating if mechanic else Decimal(0),
            schedule_configured=mechanic.schedule_configured if mechanic else False,
        )

    async def _get_user(self, user_id: int) -> User:
        stmt = (
            select(User)
            .options(selectinload(User.mechanic))
            .where(User.id == user_id, User.organization_id == self.organization_id)
        )
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if user is None:
            raise NotFoundError("Сотрудник не найден")
        return user

    async def list(self) -> list[EmployeeRead]:
        stmt = (
            select(User)
            .options(selectinload(User.mechanic))
            .where(User.organization_id == self.organization_id)
            .order_by(User.full_name)
        )
        users = list((await self.session.execute(stmt)).scalars().all())
        return [self._read(user) for user in users]

    async def get(self, user_id: int) -> EmployeeRead:
        return self._read(await self._get_user(user_id))

    async def _ensure_email_free(self, email: str, exclude_id: int | None = None) -> None:
        stmt = select(User.id).where(User.email == email)
        if exclude_id is not None:
            stmt = stmt.where(User.id != exclude_id)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError("Сотрудник с таким email уже существует")

    async def _ensure_login_free(self, login: str, exclude_id: int | None = None) -> None:
        stmt = select(User.id).where(User.login == login)
        if exclude_id is not None:
            stmt = stmt.where(User.id != exclude_id)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError("Сотрудник с таким логином уже существует")

    async def _ensure_phone_free(self, phone: str, exclude_id: int | None = None) -> None:
        stmt = select(User.id).where(User.normalized_phone == phone)
        if exclude_id is not None:
            stmt = stmt.where(User.id != exclude_id)
        if (await self.session.execute(stmt)).scalar_one_or_none() is not None:
            raise ConflictError("Сотрудник с таким телефоном уже существует")

    @staticmethod
    def _staff_role(role: UserRole, value: str | None) -> str:
        role_key = value or default_staff_role(role)
        if role_key not in STAFF_ROLE_TO_TECHNICAL:
            raise BusinessRuleError("Неизвестная должность сотрудника")
        if STAFF_ROLE_TO_TECHNICAL[role_key] != role:
            raise BusinessRuleError("Должность не соответствует системной роли")
        return role_key

    async def create(self, data: EmployeeCreate) -> EmployeeRead:
        email = str(data.email).strip().lower() if data.email is not None else None
        if email is not None:
            await self._ensure_email_free(email)
        phone = normalize_phone(data.phone)
        if data.phone and phone is None:
            raise BusinessRuleError("Некорректный номер телефона")
        if phone is not None:
            await self._ensure_phone_free(phone)
        login = normalize_login(data.login)
        if login is not None:
            await self._ensure_login_free(login)
        staff_role_key = self._staff_role(data.role, data.staff_role_key)
        user = User(
            organization_id=self.organization_id,
            email=email,
            full_name=data.full_name.strip(),
            phone=phone,
            normalized_phone=phone,
            login=login,
            role=data.role,
            staff_role_key=staff_role_key,
            rate=data.rate,
            calendar_color=data.calendar_color,
            duties=data.duties,
            ui_permissions=data.ui_permissions,
            documents=data.documents,
            hashed_password=hash_password(data.password),
        )
        self.session.add(user)
        await self.session.flush()
        if data.role == UserRole.MECHANIC:
            self.session.add(
                Mechanic(
                    organization_id=self.organization_id,
                    user_id=user.id,
                    full_name=user.full_name,
                    phone=user.phone,
                    specializations=[item.value for item in data.specializations],
                    hired_year=data.hired_year,
                    hourly_rate=data.hourly_rate,
                    commission_percent=data.commission_percent,
                )
            )
            await self.session.flush()
        return await self.get(user.id)

    async def update(self, user_id: int, data: EmployeeUpdate) -> EmployeeRead:
        user = await self._get_user(user_id)
        payload = data.model_dump(exclude_unset=True)
        mechanic_fields = {
            key: payload.pop(key)
            for key in (
                "specializations",
                "hired_year",
                "hourly_rate",
                "commission_percent",
            )
            if key in payload
        }
        if "email" in payload:
            if payload["email"] is not None:
                email = str(payload["email"]).strip().lower()
                await self._ensure_email_free(email, user.id)
                payload["email"] = email
        if "phone" in payload:
            phone = normalize_phone(payload["phone"])
            if payload["phone"] and phone is None:
                raise BusinessRuleError("Некорректный номер телефона")
            if phone is not None:
                await self._ensure_phone_free(phone, user.id)
            payload["phone"] = phone
            user.normalized_phone = phone
        if "login" in payload:
            login = normalize_login(payload["login"])
            if login is not None:
                await self._ensure_login_free(login, user.id)
            payload["login"] = login
        if "role" in payload and "staff_role_key" not in payload:
            payload["staff_role_key"] = default_staff_role(payload["role"])
        target_role = payload.get("role", user.role)
        target_role_key = payload.get("staff_role_key", user.staff_role_key)
        payload["staff_role_key"] = self._staff_role(target_role, target_role_key)
        if "password" in payload and payload["password"] is not None:
            user.hashed_password = hash_password(payload.pop("password"))
        for field, value in payload.items():
            if value is not None or field in {"email", "login", "phone", "rate"}:
                setattr(user, field, value)

        if user.role == UserRole.MECHANIC and user.mechanic is None:
            user.mechanic = Mechanic(
                organization_id=self.organization_id,
                user_id=user.id,
                full_name=user.full_name,
                phone=user.phone,
            )
        if user.mechanic is not None:
            user.mechanic.full_name = user.full_name
            user.mechanic.phone = user.phone
            user.mechanic.is_active = user.is_active and user.role == UserRole.MECHANIC
            for field, value in mechanic_fields.items():
                if value is not None:
                    if field == "specializations":
                        value = [item.value for item in value]
                    setattr(user.mechanic, field, value)
        await self.session.flush()
        return await self.get(user.id)

    async def deactivate(self, user_id: int, current_user_id: int) -> None:
        if user_id == current_user_id:
            raise ConflictError("Нельзя отключить собственную учётную запись")
        user = await self._get_user(user_id)
        user.is_active = False
        if user.mechanic is not None:
            user.mechanic.is_active = False
        await self.session.flush()

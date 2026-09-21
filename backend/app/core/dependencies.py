"""Сквозные зависимости: аутентификация по JWT и проверка ролей (RBAC).

Матрица доступа по ТЗ A1:
- ADMIN     — все разделы;
- MANAGER   — заказы, расписание, клиенты, склад (просмотр); без финансов/настроек;
- MECHANIC  — только свои заказы и списание со склада.
"""

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.modules.client_auth.models import ClientAccount
from app.modules.client_auth.repository import ClientAuthRepository
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.shared.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db, scope="function"),
) -> User:
    try:
        payload = decode_token(token)
    except Exception as exc:  # jwt.PyJWTError и пр.
        raise UnauthorizedError("Невалидный или просроченный токен") from exc

    if payload.get("type") != "access" or payload.get("actor") == "client":
        raise UnauthorizedError("Ожидался access-токен")

    subject = payload.get("sub")
    if subject is None:
        raise UnauthorizedError("Токен без субъекта")

    user = await UserRepository(db).get_unscoped(int(subject))
    if user is None or not user.is_active:
        raise UnauthorizedError("Пользователь не найден или неактивен")
    request.state.staff_session_id = payload.get("sid")
    return user


def require_roles(*roles: UserRole):
    """Фабрика зависимостей: допускает только перечисленные роли."""

    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError("Недостаточно прав для этого действия")
        return user

    return _checker


async def require_owner(user: User = Depends(get_current_user)) -> User:
    """Допускает только владельца организации независимо от технической роли."""

    if not user.is_owner:
        raise ForbiddenError("Это действие доступно только владельцу организации")
    return user


async def require_platform_owner(user: User = Depends(get_current_user)) -> User:
    """Authorize the separate creator/platform console.

    Tenant owners are intentionally not treated as platform owners in
    production.  For local development the flag allows the existing seeded
    owner account to exercise the new console without introducing a second
    login; production uses an explicit comma-separated allow-list.
    """

    identifiers = {
        value.strip().lower()
        for value in settings.PLATFORM_ADMIN_IDENTIFIERS.split(",")
        if value.strip()
    }
    user_identifiers = {
        value.strip().lower()
        for value in (user.email, user.login, user.phone)
        if value
    }
    explicitly_allowed = bool(identifiers & user_identifiers)
    local_owner = (
        not settings.is_production
        and settings.PLATFORM_ADMIN_ALLOW_OWNER_IN_DEV
        and user.is_owner
    )
    if not explicitly_allowed and not local_owner:
        raise ForbiddenError("Доступно только создателю платформы")
    return user


def require_feature(
    feature: str,
    *roles: UserRole,
    staff_role_keys: tuple[str, ...] = (),
):
    """Require a technical role or an explicitly permitted staff position.

    Empty permission dictionaries keep legacy users working. Once an owner has
    configured the access switches, missing/false features are denied by the
    backend as well as hidden by the frontend.
    """

    async def _checker(user: User = Depends(get_current_user)) -> User:
        technical_role_allowed = not roles or user.role in roles
        staff_role_allowed = user.staff_role_key in staff_role_keys
        if not technical_role_allowed and not staff_role_allowed:
            raise ForbiddenError("Недостаточно прав для этого раздела")
        if user.is_owner:
            return user
        permissions = user.ui_permissions or {}
        if permissions and not permissions.get(feature, False):
            raise ForbiddenError("Доступ к разделу закрыт владельцем")
        return user

    return _checker


async def get_current_client(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db, scope="function"),
) -> ClientAccount:
    """Аутентификация клиентского контура (Система B). Токен staff-контура
    (actor="staff", либо без claim'а actor вовсе) сюда не проходит — и наоборот,
    клиентский токен не проходит get_current_user (там "actor" не проверяется,
    но клиентский sub не резолвится в User)."""
    try:
        payload = decode_token(token)
    except Exception as exc:  # jwt.PyJWTError и пр.
        raise UnauthorizedError("Невалидный или просроченный токен") from exc

    if payload.get("type") != "access" or payload.get("actor") != "client":
        raise UnauthorizedError("Ожидался клиентский access-токен")

    subject = payload.get("sub")
    if subject is None:
        raise UnauthorizedError("Токен без субъекта")

    account = await ClientAuthRepository(db).get_by_id(int(subject))
    if account is None or not account.is_active:
        raise UnauthorizedError("Клиент не найден или неактивен")
    return account

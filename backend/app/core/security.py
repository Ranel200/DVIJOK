"""Хэширование паролей (bcrypt) и работа с JWT (access / refresh).

Два контура токенов, различаются claim'ом "actor": "staff" — Admin-панель
(app.modules.auth, app.core.dependencies.get_current_user), "client" —
клиентский вход по телефону (app.modules.client_auth, get_current_client).
Общий JWT_SECRET/decode_token, но actor не даёт токену одного контура пройти
проверку другого.
"""

import datetime as dt

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    # bcrypt оперирует максимум 72 байтами; усечение делаем явно и детерминированно.
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:72], hashed.encode())
    except ValueError:
        return False


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def create_access_token(
    subject: int | str,
    role: str | None = None,
    session_id: int | None = None,
) -> str:
    expire = _now() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, object] = {
        "sub": str(subject),
        "type": "access",
        "role": role,
        "actor": "staff",
        "iat": _now(),
        "exp": expire,
    }
    if session_id is not None:
        payload["sid"] = session_id
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: int | str,
    *,
    token_id: str | None = None,
    expire_days: int | None = None,
) -> str:
    expire = _now() + dt.timedelta(
        days=expire_days if expire_days is not None else settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload: dict[str, object] = {
        "sub": str(subject),
        "type": "refresh",
        "actor": "staff",
        "iat": _now(),
        "exp": expire,
    }
    if token_id is not None:
        payload["jti"] = token_id
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_client_access_token(client_account_id: int) -> str:
    expire = _now() + dt.timedelta(minutes=settings.CLIENT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, object] = {
        "sub": str(client_account_id),
        "type": "access",
        "actor": "client",
        "iat": _now(),
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_client_refresh_token(
    client_account_id: int,
    *,
    token_id: str | None = None,
    expire_days: int | None = None,
) -> str:
    expire = _now() + dt.timedelta(
        days=(
            expire_days
            if expire_days is not None
            else settings.CLIENT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    )
    payload: dict[str, object] = {
        "sub": str(client_account_id),
        "type": "refresh",
        "actor": "client",
        "iat": _now(),
        "exp": expire,
    }
    if token_id is not None:
        payload["jti"] = token_id
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Декодирование и валидация подписи/срока. Бросает jwt.PyJWTError при ошибке."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

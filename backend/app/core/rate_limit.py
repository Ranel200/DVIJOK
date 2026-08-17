"""Простой in-memory rate limiter (фиксированное окно) для защиты от перебора.

Достаточно для одного инстанса. ВАЖНО (residual): при горизонтальном
масштабировании счётчик нужно вынести в Redis или ограничивать на уровне
API-gateway/ingress — иначе лимит считается по каждому процессу отдельно.
"""

import time

from fastapi import Request

from app.core.config import settings
from app.core.exceptions import AppException


class TooManyRequestsError(AppException):
    status_code = 429
    detail = "Слишком много попыток. Повторите позже."


class InMemoryRateLimiter:
    def __init__(self, max_attempts: int, window_seconds: int) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = {}

    def check(self, key: str) -> None:
        now = time.time()
        window_start = now - self.window_seconds
        bucket = [ts for ts in self._hits.get(key, []) if ts > window_start]
        if len(bucket) >= self.max_attempts:
            raise TooManyRequestsError()
        bucket.append(now)
        self._hits[key] = bucket

    def reset(self) -> None:
        self._hits.clear()


# Лимит попыток входа: window/попыток берём из настроек.
login_limiter = InMemoryRateLimiter(
    max_attempts=settings.LOGIN_RATE_LIMIT_ATTEMPTS,
    window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
)


async def login_rate_limit(request: Request) -> None:
    """Зависимость для эндпоинта логина: лимит по IP клиента."""
    client_ip = request.client.host if request.client else "unknown"
    login_limiter.check(f"login:{client_ip}")

# Лимит регистраций: защита от массового создания организаций.
register_limiter = InMemoryRateLimiter(max_attempts=10, window_seconds=3600)

# Публичная запись не требует аккаунта, поэтому ограничиваем создание заявок
# отдельно от авторизации. Для нескольких backend-инстансов лимит должен быть
# продублирован на ingress/API gateway либо вынесен в Redis.
public_booking_limiter = InMemoryRateLimiter(
    max_attempts=settings.PUBLIC_BOOKING_RATE_LIMIT_ATTEMPTS,
    window_seconds=settings.PUBLIC_BOOKING_RATE_LIMIT_WINDOW_SECONDS,
)


async def register_rate_limit(request: Request) -> None:
    """Зависимость для эндпоинта регистрации: лимит по IP клиента."""
    client_ip = request.client.host if request.client else "unknown"
    register_limiter.check(f"register:{client_ip}")


async def public_booking_rate_limit(request: Request) -> None:
    """Лимит гостевых заявок по IP и публичному коду организации."""
    client_ip = request.client.host if request.client else "unknown"
    code = request.path_params.get("code", "unknown")
    public_booking_limiter.check(f"public-booking:{client_ip}:{code}")

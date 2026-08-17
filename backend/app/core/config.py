"""Конфигурация приложения через Pydantic Settings (загрузка из .env / окружения)."""

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Значение-плейсхолдер: запрещено в production.
DEFAULT_JWT_SECRET = "change-me-in-production-please-min-32-bytes"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Приложение
    APP_NAME: str = "KOMIT CRM API"
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    # Корень клиентского приложения. Локальный Quasar frontend опубликован под /client.
    PUBLIC_CLIENT_BASE_URL: str = "http://localhost:9001/client"
    SCHEDULE_TIMEZONE: str = "Europe/Moscow"
    SCHEDULE_SLOT_STEP_MINUTES: int = 30
    DEFAULT_APPOINTMENT_DURATION_MINUTES: int = 60
    SERVICE_IMPORT_MAX_FILE_BYTES: int = 2 * 1024 * 1024
    SERVICE_IMPORT_MAX_ROWS: int = 2000
    PUBLIC_BOOKING_RATE_LIMIT_ATTEMPTS: int = 10
    PUBLIC_BOOKING_RATE_LIMIT_WINDOW_SECONDS: int = 3600

    # База данных (async-драйвер)
    DATABASE_URL: str = "postgresql+asyncpg://komit:komit@localhost:5432/komit"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Безопасность / JWT
    JWT_SECRET: str = DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REMEMBER_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_COOKIE_NAME: str = "dvijok_refresh"
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: str = "lax"
    REFRESH_COOKIE_DOMAIN: str | None = None

    # Rate limiting логина (защита от brute-force)
    LOGIN_RATE_LIMIT_ATTEMPTS: int = 10
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 300

    # Ограничение размера тела запроса (байт)
    MAX_REQUEST_BODY_BYTES: int = 2 * 1024 * 1024  # 2 МБ

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:9000",
        "http://localhost:9001",
    ]

    # Первичный администратор (scripts/seed.py)
    FIRST_ADMIN_EMAIL: str = "admin@komit.ru"
    FIRST_ADMIN_PASSWORD: str = "admin12345"
    FIRST_ADMIN_NAME: str = "Администратор"

    # Клиентский контур (Система B) — JWT
    CLIENT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 дней, мобильный клиент
    CLIENT_REFRESH_TOKEN_EXPIRE_DAYS: int = 180
    CLIENT_REFRESH_COOKIE_NAME: str = "dvijok_client_refresh"

    # OTP-вход клиента по телефону
    # Existing client UI contains four OTP cells; backend follows that contract.
    OTP_CODE_LENGTH: int = 4
    OTP_CODE_TTL_SECONDS: int = 300
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RATE_LIMIT_ATTEMPTS: int = 5
    OTP_RATE_LIMIT_WINDOW_SECONDS: int = 3600
    OTP_IP_RATE_LIMIT_ATTEMPTS: int = 10
    OTP_IP_RATE_LIMIT_WINDOW_SECONDS: int = 3600
    OTP_PEPPER: str = DEFAULT_JWT_SECRET  # доп. соль хэша кода; в prod задать отдельно
    OTP_PROVIDER: Literal["local", "sms_ru_call", "zvonok_flashcall"] = "local"

    # SMS.ru: авторизация последними четырьмя цифрами входящего номера.
    SMS_RU_API_ID: str = ""
    SMS_RU_CALL_URL: str = "https://sms.ru/code/call"
    SMS_RU_TIMEOUT_SECONDS: float = 10.0

    # Zvonok.com: Flash Call с кодом в последних четырёх цифрах входящего номера.
    ZVONOK_PUBLIC_KEY: str = ""
    ZVONOK_CAMPAIGN_ID: str = ""
    ZVONOK_FLASHCALL_URL: str = (
        "https://zvonok.com/manager/cabapi_external/api/v1/phones/flashcall/"
    )
    ZVONOK_TIMEOUT_SECONDS: float = 10.0

    # Deep-link токен для привязки телеграм/vk аккаунта к ClientAccount
    CLIENT_LINK_TOKEN_TTL_SECONDS: int = 600

    # Уведомления и бот-шлюз
    NOTIFICATIONS_ENABLED: bool = False  # в dev/test — не бить по реальным Bot API
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_PUBLIC_URL: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""
    VK_BOT_TOKEN: str = ""
    VK_BOT_PUBLIC_URL: str = ""
    VK_BOT_SECRET: str = ""
    VK_CONFIRMATION_CODE: str = ""
    VK_API_VERSION: str = "5.199"
    MAX_BOT_TOKEN: str = ""
    MAX_BOT_PUBLIC_URL: str = ""
    MAX_WEBHOOK_SECRET: str = ""
    NOTIFICATION_POLL_INTERVAL_SECONDS: float = 2.0
    NOTIFICATION_MAX_ATTEMPTS: int = 5

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() in {"production", "prod"}

    @model_validator(mode="after")
    def _validate_production(self) -> "Settings":
        """В production запрещаем небезопасные дефолты (fail-fast при старте)."""
        if self.OTP_PROVIDER == "sms_ru_call" and not self.SMS_RU_API_ID:
            raise ValueError("Для OTP_PROVIDER=sms_ru_call требуется SMS_RU_API_ID")
        if self.OTP_PROVIDER == "zvonok_flashcall":
            missing = []
            if not self.ZVONOK_PUBLIC_KEY:
                missing.append("ZVONOK_PUBLIC_KEY")
            if not self.ZVONOK_CAMPAIGN_ID:
                missing.append("ZVONOK_CAMPAIGN_ID")
            if missing:
                raise ValueError(
                    "Для OTP_PROVIDER=zvonok_flashcall требуются " + ", ".join(missing)
                )
        if self.is_production:
            if self.JWT_SECRET == DEFAULT_JWT_SECRET or len(self.JWT_SECRET) < 32:
                raise ValueError(
                    "В production требуется стойкий JWT_SECRET (>= 32 байт). "
                    "Сгенерируйте: openssl rand -hex 32"
                )
            if self.DEBUG:
                raise ValueError("DEBUG должен быть выключен в production")
            if not self.REFRESH_COOKIE_SECURE:
                raise ValueError("REFRESH_COOKIE_SECURE должен быть включён в production")
            if self.NOTIFICATIONS_ENABLED:
                channels = (
                    (
                        "Telegram",
                        self.TELEGRAM_BOT_PUBLIC_URL,
                        self.TELEGRAM_BOT_TOKEN,
                        self.TELEGRAM_WEBHOOK_SECRET,
                    ),
                    (
                        "VK",
                        self.VK_BOT_PUBLIC_URL,
                        self.VK_BOT_TOKEN,
                        self.VK_BOT_SECRET,
                    ),
                    (
                        "MAX",
                        self.MAX_BOT_PUBLIC_URL,
                        self.MAX_BOT_TOKEN,
                        self.MAX_WEBHOOK_SECRET,
                    ),
                )
                configured = [item for item in channels if item[1] or item[2]]
                if not configured:
                    raise ValueError(
                        "При NOTIFICATIONS_ENABLED=true настройте хотя бы один бот"
                    )
                for name, public_url, token, webhook_secret in configured:
                    if not public_url or not token or not webhook_secret:
                        raise ValueError(
                            f"Для {name} требуются public URL, token и webhook secret"
                        )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

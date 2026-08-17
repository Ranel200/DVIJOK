"""Клиентская учётная запись (Система B) — глобальная сущность, вход по телефону.

В отличие от почти всех остальных моделей проекта у ClientAccount НЕТ
organization_id: один физический клиент (по номеру телефона) может
записываться в разные автосервисы (Organization), выбирая их в боте/приложении.
Связь с CRM-карточкой клиента внутри конкретной организации —
`clients.Client.client_account_id` (nullable FK, см. app/modules/clients/models.py).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, IntPKMixin, TimestampMixin


class ClientAccount(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "client_accounts"

    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    telegram_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    vk_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    # Первая реферальная атрибуция неизменяема на уровне сервиса. Nullable
    # сохраняет совместимость с существующими и органически пришедшими клиентами.
    source_organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True, nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ClientRefreshSession(Base, IntPKMixin, TimestampMixin):
    """Revocable, rotating refresh session stored only as a token hash."""

    __tablename__ = "client_refresh_sessions"

    client_account_id: Mapped[int] = mapped_column(
        ForeignKey("client_accounts.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    ip: Mapped[str] = mapped_column(String(64), default="")
    user_agent: Mapped[str] = mapped_column(Text, default="")

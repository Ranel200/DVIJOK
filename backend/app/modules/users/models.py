"""Сотрудник Admin-панели (учётная запись для входа)."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, IntPKMixin, TimestampMixin
from app.shared.enums import UserRole

if TYPE_CHECKING:
    from app.modules.mechanics.models import Mechanic


class User(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "users"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    # Сотрудники могут входить только по логину, поэтому email для них
    # необязателен. Владельцы организаций по-прежнему регистрируются с email.
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    normalized_phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    login: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=20), default=UserRole.MANAGER, index=True
    )
    staff_role_key: Mapped[str] = mapped_column(String(30), default="junior_admin", index=True)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    # Владелец организации отличается от обычного старшего администратора:
    # техническая роль у них одинаковая, но только владелец управляет тарифом
    # и всегда имеет доступ ко всем разделам административного приложения.
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    calendar_color: Mapped[str] = mapped_column(String(7), default="#5C6BC0")
    duties: Mapped[str | None] = mapped_column(Text)
    # Гранты разделов UI; backend проверяет их вместе с технической ролью.
    ui_permissions: Mapped[dict[str, bool]] = mapped_column(JSON, default=dict)
    # Метаданные загруженных кадровых документов; содержимое файлов хранится
    # отдельным документным контуром, когда он будет подключён.
    documents: Mapped[dict[str, dict | None]] = mapped_column(JSON, default=dict)
    # Повторяющийся график нужен всем сотрудникам, не только мастерам. Для
    # мастеров он синхронизируется с mechanic_working_hours, чтобы не менять
    # существующий контур расчёта доступности и клиентских бронирований.
    schedule_intervals: Mapped[list[dict[str, str | int]]] = mapped_column(JSON, default=list)
    schedule_breaks: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    email_confirm_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_confirm_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Опциональная привязка к профилю мастера (1:0..1).
    mechanic: Mapped["Mechanic | None"] = relationship(back_populates="user", uselist=False)

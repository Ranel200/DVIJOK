"""ORM-модели привязок мессенджеров, deep-link токенов и outbox."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, IntPKMixin, TimestampMixin
from app.shared.enums import (
    NotificationChannel,
    NotificationEventType,
    NotificationStatus,
)


class ClientMessengerBinding(Base, IntPKMixin, TimestampMixin):
    """Подтверждённый канал конкретной глобальной клиентской учётки."""

    __tablename__ = "client_messenger_bindings"

    client_account_id: Mapped[int] = mapped_column(
        ForeignKey("client_accounts.id", ondelete="CASCADE"), index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, native_enum=False, length=20), index=True
    )
    external_user_id: Mapped[str] = mapped_column(String(64))
    external_chat_id: Mapped[str] = mapped_column(String(64))
    username: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "client_account_id", "channel", name="uq_messenger_binding_account_channel"
        ),
        UniqueConstraint(
            "channel", "external_user_id", name="uq_messenger_binding_channel_user"
        ),
    )


class ClientMessengerLinkToken(Base, IntPKMixin, TimestampMixin):
    """Одноразовый токен: в БД хранится только SHA-256, не исходное значение."""

    __tablename__ = "client_messenger_link_tokens"

    client_account_id: Mapped[int] = mapped_column(
        ForeignKey("client_accounts.id", ondelete="CASCADE"), index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, native_enum=False, length=20), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class NotificationDelivery(Base, IntPKMixin, TimestampMixin):
    """Транзакционный outbox одного клиентского события в один канал."""

    __tablename__ = "notification_deliveries"

    client_account_id: Mapped[int] = mapped_column(
        ForeignKey("client_accounts.id", ondelete="CASCADE"), index=True
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, native_enum=False, length=20), index=True
    )
    event_type: Mapped[NotificationEventType] = mapped_column(
        Enum(NotificationEventType, native_enum=False, length=40), index=True
    )
    recipient_id: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, native_enum=False, length=20),
        default=NotificationStatus.PENDING,
        index=True,
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True
    )
    last_error: Mapped[str | None] = mapped_column(Text)
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "channel",
            "event_type",
            name="uq_notification_order_channel_event",
        ),
        Index(
            "ix_notification_delivery_ready",
            "status",
            "next_attempt_at",
            "attempts",
        ),
    )

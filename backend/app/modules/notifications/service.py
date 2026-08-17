"""Deep links, подтверждение привязок и транзакционный notification outbox."""

import asyncio
import datetime as dt
import hashlib
import logging
import secrets
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import or_, select, update
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.exceptions import BusinessRuleError
from app.modules.client_auth.models import ClientAccount
from app.modules.notifications.models import (
    ClientMessengerBinding,
    ClientMessengerLinkToken,
    NotificationDelivery,
)
from app.modules.notifications.providers import BotProviders
from app.modules.orders.models import Order
from app.shared.enums import (
    NotificationChannel,
    NotificationEventType,
    NotificationStatus,
    OrderStatus,
)

_STATUS_EVENTS: dict[OrderStatus, NotificationEventType] = {
    OrderStatus.NEW: NotificationEventType.BOOKING_CREATED,
    OrderStatus.DIAGNOSTICS: NotificationEventType.STATUS_IN_PROGRESS,
    OrderStatus.IN_PROGRESS: NotificationEventType.STATUS_IN_PROGRESS,
    OrderStatus.APPROVAL: NotificationEventType.STATUS_AGREEMENT,
    OrderStatus.AGREEMENT: NotificationEventType.STATUS_AGREEMENT,
    OrderStatus.WAITING: NotificationEventType.STATUS_AGREEMENT,
    OrderStatus.DONE: NotificationEventType.STATUS_DONE,
    OrderStatus.CANCELLED: NotificationEventType.STATUS_CANCELLED,
}

logger = logging.getLogger(__name__)

_EVENT_TEXTS: dict[NotificationEventType, str] = {
    NotificationEventType.BOOKING_CREATED: "Вы записаны. Статус: «Записан».",
    NotificationEventType.STATUS_IN_PROGRESS: "Ваш автомобиль в работе.",
    NotificationEventType.STATUS_AGREEMENT: "Статус заказа: «Согласование».",
    NotificationEventType.STATUS_DONE: "Работа завершена. Автомобиль готов.",
    NotificationEventType.STATUS_CANCELLED: "Запись отменена.",
}


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _with_query(url: str, **params: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update(params)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


class MessengerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def public_url(channel: NotificationChannel) -> str:
        return {
            NotificationChannel.TELEGRAM: settings.TELEGRAM_BOT_PUBLIC_URL,
            NotificationChannel.VK: settings.VK_BOT_PUBLIC_URL,
            NotificationChannel.MAX: settings.MAX_BOT_PUBLIC_URL,
        }[channel]

    async def issue_token(self, client_account_id: int, channel: NotificationChannel) -> str:
        now = _now()
        await self.session.execute(
            update(ClientMessengerLinkToken)
            .where(
                ClientMessengerLinkToken.client_account_id == client_account_id,
                ClientMessengerLinkToken.channel == channel,
                ClientMessengerLinkToken.consumed_at.is_(None),
            )
            .values(consumed_at=now)
        )
        token = secrets.token_urlsafe(24)
        self.session.add(
            ClientMessengerLinkToken(
                client_account_id=client_account_id,
                channel=channel,
                token_hash=_token_hash(token),
                expires_at=now
                + dt.timedelta(seconds=settings.CLIENT_LINK_TOKEN_TTL_SECONDS),
            )
        )
        await self.session.flush()
        return token

    async def link_url(self, client_account_id: int, channel: NotificationChannel) -> str:
        base_url = self.public_url(channel)
        if not base_url:
            return ""
        token = await self.issue_token(client_account_id, channel)
        if channel == NotificationChannel.VK:
            return _with_query(base_url, ref=token, ref_source="dvijok")
        return _with_query(base_url, start=token)

    async def bind(
        self,
        *,
        channel: NotificationChannel,
        token: str,
        external_user_id: str,
        external_chat_id: str,
        username: str | None = None,
    ) -> ClientMessengerBinding:
        now = _now()
        link = (
            await self.session.execute(
                select(ClientMessengerLinkToken)
                .where(
                    ClientMessengerLinkToken.token_hash == _token_hash(token),
                    ClientMessengerLinkToken.channel == channel,
                )
                .with_for_update()
            )
        ).scalar_one_or_none()
        if link is None:
            raise BusinessRuleError("Ссылка привязки уже использована или недействительна")
        if link.consumed_at is not None:
            # Провайдер может повторить уже успешно обработанный webhook. Такой
            # повтор идемпотентен, но не позволяет привязать другого получателя.
            existing_binding = (
                await self.session.execute(
                    select(ClientMessengerBinding).where(
                        ClientMessengerBinding.client_account_id
                        == link.client_account_id,
                        ClientMessengerBinding.channel == channel,
                        ClientMessengerBinding.external_user_id == external_user_id,
                        ClientMessengerBinding.external_chat_id == external_chat_id,
                    )
                )
            ).scalar_one_or_none()
            if existing_binding is not None:
                return existing_binding
            raise BusinessRuleError("Ссылка привязки уже использована или недействительна")
        expires_at = link.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=dt.UTC)
        if expires_at <= now:
            link.consumed_at = now
            raise BusinessRuleError("Ссылка привязки истекла")

        occupied = (
            await self.session.execute(
                select(ClientMessengerBinding).where(
                    ClientMessengerBinding.channel == channel,
                    ClientMessengerBinding.external_user_id == external_user_id,
                )
            )
        ).scalar_one_or_none()
        if occupied is not None and occupied.client_account_id != link.client_account_id:
            raise BusinessRuleError("Этот аккаунт мессенджера уже привязан к другому клиенту")

        binding = (
            await self.session.execute(
                select(ClientMessengerBinding).where(
                    ClientMessengerBinding.client_account_id == link.client_account_id,
                    ClientMessengerBinding.channel == channel,
                )
            )
        ).scalar_one_or_none()
        if binding is None:
            binding = ClientMessengerBinding(
                client_account_id=link.client_account_id,
                channel=channel,
                external_user_id=external_user_id,
                external_chat_id=external_chat_id,
                username=username,
            )
            self.session.add(binding)
        else:
            binding.external_user_id = external_user_id
            binding.external_chat_id = external_chat_id
            binding.username = username
            binding.is_active = True
            binding.linked_at = now

        account = await self.session.get(ClientAccount, link.client_account_id)
        if account is not None:
            if channel == NotificationChannel.TELEGRAM:
                account.telegram_id = external_user_id
            elif channel == NotificationChannel.VK:
                account.vk_id = external_user_id
        link.consumed_at = now
        await self.session.flush()
        return binding


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def enqueue_order_status(self, order: Order) -> None:
        event_type = _STATUS_EVENTS.get(order.status)
        client = order.client
        if (
            event_type is None
            or client is None
            or client.client_account_id is None
            or not client.notifications_enabled
        ):
            return
        bindings = list(
            (
                await self.session.execute(
                    select(ClientMessengerBinding).where(
                        ClientMessengerBinding.client_account_id
                        == client.client_account_id,
                        ClientMessengerBinding.is_active.is_(True),
                    )
                )
            )
            .scalars()
            .all()
        )
        if not bindings:
            return
        message = f"ДВИЖОК · Заказ №{order.number}\n{_EVENT_TEXTS[event_type]}"
        values = [
            {
                "client_account_id": client.client_account_id,
                "order_id": order.id,
                "channel": binding.channel,
                "event_type": event_type,
                "recipient_id": binding.external_chat_id,
                "message": message,
                "status": NotificationStatus.PENDING,
                "attempts": 0,
                "next_attempt_at": _now(),
            }
            for binding in bindings
        ]
        dialect = self.session.bind.dialect.name if self.session.bind is not None else ""
        if dialect == "postgresql":
            pg_statement = postgres_insert(NotificationDelivery).values(values)
            pg_statement = pg_statement.on_conflict_do_nothing(
                constraint="uq_notification_order_channel_event"
            )
            await self.session.execute(pg_statement)
        elif dialect == "sqlite":
            sqlite_statement = sqlite_insert(NotificationDelivery).values(values)
            sqlite_statement = sqlite_statement.on_conflict_do_nothing(
                index_elements=["order_id", "channel", "event_type"]
            )
            await self.session.execute(sqlite_statement)
        else:
            for value in values:
                existing = (
                    await self.session.execute(
                        select(NotificationDelivery.id).where(
                            NotificationDelivery.order_id == value["order_id"],
                            NotificationDelivery.channel == value["channel"],
                            NotificationDelivery.event_type == value["event_type"],
                        )
                    )
                ).scalar_one_or_none()
                if existing is None:
                    self.session.add(NotificationDelivery(**value))
        await self.session.flush()


class NotificationDispatcher:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        providers: BotProviders | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.providers = providers or BotProviders()
        self._stop = asyncio.Event()

    async def run_once(self) -> bool:
        now = _now()
        async with self.session_factory() as session, session.begin():
            statement = (
                select(NotificationDelivery)
                .where(
                    NotificationDelivery.status.in_(
                        [NotificationStatus.PENDING, NotificationStatus.FAILED]
                    ),
                    NotificationDelivery.attempts < settings.NOTIFICATION_MAX_ATTEMPTS,
                    or_(
                        NotificationDelivery.next_attempt_at.is_(None),
                        NotificationDelivery.next_attempt_at <= now,
                    ),
                )
                .order_by(NotificationDelivery.id)
                .limit(1)
            )
            if session.bind is not None and session.bind.dialect.name == "postgresql":
                statement = statement.with_for_update(skip_locked=True)
            delivery = (await session.execute(statement)).scalar_one_or_none()
            if delivery is None:
                return False
            try:
                provider_id = await self.providers.send(
                    delivery.channel,
                    delivery.recipient_id,
                    delivery.message,
                )
            except Exception as exc:  # provider/network failure must not affect CRM
                delivery.attempts += 1
                delivery.status = NotificationStatus.FAILED
                delivery.last_error = str(exc)[:2000]
                delivery.next_attempt_at = now + dt.timedelta(
                    seconds=min(300, 2 ** delivery.attempts)
                )
            else:
                delivery.attempts += 1
                delivery.status = NotificationStatus.SENT
                delivery.provider_message_id = provider_id
                delivery.last_error = None
                delivery.next_attempt_at = None
                delivery.sent_at = now
            return True

    async def run_forever(self) -> None:
        while not self._stop.is_set():
            try:
                processed = await self.run_once()
            except Exception:
                logger.exception("Ошибка фонового обработчика notification outbox")
                processed = False
            if processed:
                continue
            try:
                await asyncio.wait_for(
                    self._stop.wait(), timeout=settings.NOTIFICATION_POLL_INTERVAL_SECONDS
                )
            except TimeoutError:
                pass

    def stop(self) -> None:
        self._stop.set()

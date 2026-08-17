"""Привязка ботов, статусная маршрутизация и доставка outbox."""

from urllib.parse import parse_qs, urlsplit

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import BusinessRuleError
from app.modules.client_auth.models import ClientAccount
from app.modules.clients.models import Client
from app.modules.notifications.models import (
    ClientMessengerBinding,
    ClientMessengerLinkToken,
    NotificationDelivery,
)
from app.modules.notifications.service import (
    MessengerService,
    NotificationDispatcher,
)
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import OrderCreate
from app.modules.orders.service import OrderService
from app.shared.enums import (
    NotificationChannel,
    NotificationEventType,
    NotificationStatus,
    OrderStatus,
)


async def _account_and_client(session, organization: int) -> tuple[ClientAccount, Client]:
    account = ClientAccount(phone="+79990007766", full_name="Бот Клиент")
    session.add(account)
    await session.flush()
    client = Client(
        organization_id=organization,
        full_name="Бот Клиент",
        phone=account.phone,
        client_account_id=account.id,
    )
    session.add(client)
    await session.flush()
    return account, client


async def test_deep_link_is_channel_specific_hashed_and_single_use(
    session_factory, organization, monkeypatch
):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_PUBLIC_URL", "https://t.me/dvijok_test_bot")
    async with session_factory() as session:
        account, _ = await _account_and_client(session, organization)
        service = MessengerService(session)
        url = await service.link_url(account.id, NotificationChannel.TELEGRAM)
        token = parse_qs(urlsplit(url).query)["start"][0]
        assert url.startswith("https://t.me/dvijok_test_bot?start=")

        stored = (
            await session.execute(select(ClientMessengerLinkToken))
        ).scalar_one()
        assert stored.token_hash != token
        assert token not in stored.token_hash

        binding = await service.bind(
            channel=NotificationChannel.TELEGRAM,
            token=token,
            external_user_id="telegram-user-42",
            external_chat_id="telegram-chat-42",
            username="tester",
        )
        assert binding.client_account_id == account.id
        assert account.telegram_id == "telegram-user-42"
        repeated = await service.bind(
            channel=NotificationChannel.TELEGRAM,
            token=token,
            external_user_id="telegram-user-42",
            external_chat_id="telegram-chat-42",
        )
        assert repeated.id == binding.id
        with pytest.raises(BusinessRuleError):
            await service.bind(
                channel=NotificationChannel.TELEGRAM,
                token=token,
                external_user_id="another-user",
                external_chat_id="another-chat",
            )


async def test_order_statuses_enqueue_expected_events_once(session_factory, organization):
    async with session_factory() as session:
        account, client = await _account_and_client(session, organization)
        session.add(
            ClientMessengerBinding(
                client_account_id=account.id,
                channel=NotificationChannel.TELEGRAM,
                external_user_id="tg-1",
                external_chat_id="chat-1",
            )
        )
        await session.flush()
        orders = OrderService(OrderRepository(session, organization))
        order = await orders.create(OrderCreate(client_id=client.id), created_by_id=None)
        await orders.change_status(
            order.id,
            OrderStatus.DIAGNOSTICS,
            validate_transition=False,
            require_completion_document=False,
        )
        # diagnostics и in_progress — один клиентский этап «В работе».
        await orders.change_status(
            order.id,
            OrderStatus.IN_PROGRESS,
            validate_transition=False,
            require_completion_document=False,
        )
        await orders.change_status(
            order.id,
            OrderStatus.WAITING,
            validate_transition=False,
            require_completion_document=False,
        )
        await orders.change_status(
            order.id,
            OrderStatus.AGREEMENT,
            validate_transition=False,
            require_completion_document=False,
        )
        await orders.change_status(
            order.id,
            OrderStatus.DONE,
            validate_transition=False,
            require_completion_document=False,
        )

        deliveries = list(
            (
                await session.execute(
                    select(NotificationDelivery).order_by(NotificationDelivery.id)
                )
            )
            .scalars()
            .all()
        )
        assert [item.event_type for item in deliveries] == [
            NotificationEventType.BOOKING_CREATED,
            NotificationEventType.STATUS_IN_PROGRESS,
            NotificationEventType.STATUS_AGREEMENT,
            NotificationEventType.STATUS_DONE,
        ]
        assert "Записан" in deliveries[0].message
        assert "в работе" in deliveries[1].message
        assert "Согласование" in deliveries[2].message
        assert "готов" in deliveries[3].message


class _RecordingProviders:
    def __init__(self) -> None:
        self.calls: list[tuple[NotificationChannel, str, str]] = []

    async def send(
        self, channel: NotificationChannel, recipient_id: str, message: str
    ) -> str:
        self.calls.append((channel, recipient_id, message))
        return "provider-message-1"


async def test_dispatcher_marks_delivery_sent(session_factory, organization):
    async with session_factory() as session:
        account, client = await _account_and_client(session, organization)
        session.add(
            ClientMessengerBinding(
                client_account_id=account.id,
                channel=NotificationChannel.MAX,
                external_user_id="max-user",
                external_chat_id="max-chat",
            )
        )
        await session.flush()
        await OrderService(OrderRepository(session, organization)).create(
            OrderCreate(client_id=client.id), created_by_id=None
        )
        await session.commit()

    providers = _RecordingProviders()
    dispatcher = NotificationDispatcher(session_factory, providers=providers)  # type: ignore[arg-type]
    assert await dispatcher.run_once() is True
    assert len(providers.calls) == 1
    assert providers.calls[0][0] == NotificationChannel.MAX
    assert providers.calls[0][1] == "max-chat"

    async with session_factory() as session:
        delivery = (
            await session.execute(select(NotificationDelivery))
        ).scalar_one()
        assert delivery.status == NotificationStatus.SENT
        assert delivery.provider_message_id == "provider-message-1"
        assert delivery.attempts == 1

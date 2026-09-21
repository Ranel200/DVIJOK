"""Webhook behaviour for the client notification bots."""

from app.modules.notifications.providers import BotProviders
from app.modules.notifications.models import ClientMessengerLinkToken
from app.modules.notifications.service import MessengerService, _order_message
from app.modules.client_auth.models import ClientAccount
from app.shared.enums import NotificationChannel, NotificationEventType
from datetime import datetime, timezone
from sqlalchemy import select


async def test_max_personal_link_is_accepted_without_content_type(client, monkeypatch):
    """MAX may omit Content-Type; a valid personal start event must still bind."""

    token = "test_max_link_token_12345"
    calls: dict[str, str] = {}

    class Binding:
        external_chat_id = "1234567890"

    async def fake_bind(self, **kwargs):
        calls.update({key: str(value) for key, value in kwargs.items() if value is not None})
        return Binding(), True

    async def fake_send_welcome(self, channel, recipient_id):
        calls["welcome_recipient"] = str(recipient_id)
        return []

    monkeypatch.setattr(MessengerService, "bind_with_status", fake_bind)
    monkeypatch.setattr(BotProviders, "send_welcome", fake_send_welcome)

    response = await client.post(
        "/api/v1/bot-gateway/max/webhook",
        content=(
            '{"update_type":"bot_started","chat_id":1234567890,'
            '"user":{"user_id":1234567890,"username":"ivan_petrov"},'
            f'"payload":"{token}"}}'
        ).encode(),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}
    assert calls["token"] == token
    assert calls["welcome_recipient"] == "1234567890"


async def test_personal_bot_link_stays_the_same_across_cabinet_loads(session_factory):
    async with session_factory() as session:
        account = ClientAccount(phone="+79990000001")
        session.add(account)
        await session.flush()

        messenger = MessengerService(session)
        first = await messenger.issue_token(account.id, NotificationChannel.MAX)
        second = await messenger.issue_token(account.id, NotificationChannel.MAX)

        links = list(
            (
                await session.execute(
                    select(ClientMessengerLinkToken).where(
                        ClientMessengerLinkToken.client_account_id == account.id,
                        ClientMessengerLinkToken.channel == NotificationChannel.MAX,
                    )
                )
            ).scalars()
        )
        assert first == second
        assert len(links) == 1


def test_booking_notification_contains_actual_booking_details():
    message = _order_message(
        NotificationEventType.BOOKING_CREATED,
        number="42",
        vehicle_name="Toyota Camry",
        organization_name="Автосервис ДВИЖОК",
        scheduled_at=datetime(2026, 9, 2, 14, 30, tzinfo=timezone.utc),
    )

    assert "🚗 Вы записаны на обслуживание" in message
    assert "Автомобиль: Toyota Camry" in message
    assert "Дата: 02.09.2026" in message
    assert "Время: 14:30" in message
    assert "Автосервис: Автосервис ДВИЖОК" in message


def test_completed_notification_links_to_client_portal():
    message = _order_message(
        NotificationEventType.STATUS_DONE,
        number="42",
        vehicle_name="Toyota Camry",
        organization_name="Автосервис ДВИЖОК",
        scheduled_at=None,
    )

    assert "✅ Ваша машина готова!" in message
    assert "разделе «История»" in message
    assert "https://dvizhok.tech/client" in message

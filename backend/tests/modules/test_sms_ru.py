"""Контракт SMS.ru Code Call без сетевых и платных запросов."""

from urllib.parse import parse_qs

import httpx

from app.core.config import settings
from app.modules.client_auth.sms_ru import SmsRuCallProvider


async def test_sms_ru_provider_sends_phone_api_key_and_local_ip(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.update(parse_qs((await request.aread()).decode()))
        return httpx.Response(
            200,
            json={
                "status": "OK",
                "code": "8642",
                "call_id": "test-call",
                "cost": 0.4,
                "balance": 10.5,
            },
        )

    monkeypatch.setattr(settings, "SMS_RU_API_ID", "not-a-real-key")
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await SmsRuCallProvider(client).request_code(
            "+7 (999) 123-45-67", "127.0.0.1"
        )

    assert captured == {
        "api_id": ["not-a-real-key"],
        "phone": ["79991234567"],
        "ip": ["-1"],
    }
    assert result.code == "8642"
    assert result.call_id == "test-call"
    assert str(result.cost) == "0.4"

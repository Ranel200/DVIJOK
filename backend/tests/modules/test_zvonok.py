"""Контракт Zvonok.com Flash Call без сетевых и платных запросов."""

from urllib.parse import parse_qs

import httpx
import pytest

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError
from app.modules.client_auth.zvonok import ZvonokFlashCallProvider


async def test_zvonok_provider_sends_required_form_fields(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.update(parse_qs((await request.aread()).decode()))
        return httpx.Response(
            200,
            json={
                "status": "ok",
                "data": {
                    "balance": "333.333333",
                    "call_id": 999999999999999,
                    "created": "2023-02-09T12:50:55.621Z",
                    "phone": "+79991234567",
                    "pincode": "8642",
                },
            },
        )

    monkeypatch.setattr(settings, "ZVONOK_PUBLIC_KEY", "not-a-real-key")
    monkeypatch.setattr(settings, "ZVONOK_CAMPAIGN_ID", "123456")
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await ZvonokFlashCallProvider(client).request_code(
            "+7 (999) 123-45-67", "127.0.0.1"
        )

    assert captured == {
        "public_key": ["not-a-real-key"],
        "phone": ["+79991234567"],
        "campaign_id": ["123456"],
    }
    assert result.code == "8642"
    assert result.call_id == "999999999999999"
    assert str(result.balance) == "333.333333"


@pytest.mark.parametrize(
    "response_body",
    [
        {"status": "error", "message": "campaign is not active"},
        {"status": "ok", "data": {}},
        {"status": "ok", "data": {"pincode": "42"}},
    ],
)
async def test_zvonok_provider_rejects_unsuccessful_or_invalid_response(
    monkeypatch, response_body
):
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=response_body)

    monkeypatch.setattr(settings, "ZVONOK_PUBLIC_KEY", "not-a-real-key")
    monkeypatch.setattr(settings, "ZVONOK_CAMPAIGN_ID", "123456")
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ServiceUnavailableError):
            await ZvonokFlashCallProvider(client).request_code("+79991234567", "testclient")


async def test_zvonok_provider_maps_http_failure_to_service_unavailable(monkeypatch):
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"detail": "rate limit"})

    monkeypatch.setattr(settings, "ZVONOK_PUBLIC_KEY", "not-a-real-key")
    monkeypatch.setattr(settings, "ZVONOK_CAMPAIGN_ID", "123456")
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ServiceUnavailableError):
            await ZvonokFlashCallProvider(client).request_code("+79991234567", "testclient")

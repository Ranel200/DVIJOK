"""Минимальные HTTP-адаптеры Telegram, VK и MAX Bot API."""

import secrets

import httpx

from app.core.config import settings
from app.shared.enums import NotificationChannel


class ProviderError(RuntimeError):
    pass


class BotProviders:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def send(
        self,
        channel: NotificationChannel,
        recipient_id: str,
        message: str,
    ) -> str | None:
        if channel == NotificationChannel.TELEGRAM:
            return await self._telegram(recipient_id, message)
        if channel == NotificationChannel.VK:
            return await self._vk(recipient_id, message)
        if channel == NotificationChannel.MAX:
            return await self._max(recipient_id, message)
        raise ProviderError(f"Неизвестный канал: {channel}")

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        if self._client is not None:
            response = await self._client.request(method, url, **kwargs)
        else:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.request(method, url, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Bot API вернул HTTP {response.status_code}") from exc
        return response

    async def _telegram(self, chat_id: str, message: str) -> str | None:
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ProviderError("TELEGRAM_BOT_TOKEN не настроен")
        response = await self._request(
            "POST",
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": message},
        )
        data = response.json()
        if not data.get("ok"):
            raise ProviderError(str(data.get("description") or "Ошибка Telegram Bot API"))
        message_id = (data.get("result") or {}).get("message_id")
        return str(message_id) if message_id is not None else None

    async def _vk(self, peer_id: str, message: str) -> str | None:
        if not settings.VK_BOT_TOKEN:
            raise ProviderError("VK_BOT_TOKEN не настроен")
        response = await self._request(
            "POST",
            "https://api.vk.com/method/messages.send",
            data={
                "access_token": settings.VK_BOT_TOKEN,
                "v": settings.VK_API_VERSION,
                "peer_id": peer_id,
                "random_id": secrets.randbelow(2**31 - 1) + 1,
                "message": message,
            },
        )
        data = response.json()
        if data.get("error"):
            raise ProviderError(str(data["error"].get("error_msg") or "Ошибка VK API"))
        value = data.get("response")
        return str(value) if value is not None else None

    async def _max(self, chat_id: str, message: str) -> str | None:
        if not settings.MAX_BOT_TOKEN:
            raise ProviderError("MAX_BOT_TOKEN не настроен")
        response = await self._request(
            "POST",
            "https://platform-api2.max.ru/messages",
            params={"chat_id": chat_id},
            headers={"Authorization": settings.MAX_BOT_TOKEN},
            json={"text": message},
        )
        data = response.json()
        result = data.get("message") or {}
        message_id = result.get("body", {}).get("mid") or result.get("mid")
        return str(message_id) if message_id is not None else None

"""Публичные webhook-endpoint'ы Telegram, VK и MAX."""

import re
from typing import Any

from fastapi import APIRouter, Depends, Header
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.modules.notifications.service import MessengerService
from app.shared.enums import NotificationChannel

router = APIRouter(prefix="/bot-gateway", tags=["bot-gateway"])

_TOKEN_RE = re.compile(r"(?:^|\s)([A-Za-z0-9_-]{20,64})(?:\s|$)")


def get_messenger_service(
    db: AsyncSession = Depends(get_db, scope="function"),
) -> MessengerService:
    return MessengerService(db)


def _token(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = _TOKEN_RE.search(value.strip())
    return match.group(1) if match else None


@router.post("/telegram/webhook")
async def telegram_webhook(
    payload: dict[str, Any],
    secret: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
    service: MessengerService = Depends(get_messenger_service),
) -> dict[str, bool]:
    if settings.TELEGRAM_WEBHOOK_SECRET and secret != settings.TELEGRAM_WEBHOOK_SECRET:
        raise UnauthorizedError("Неверный секрет Telegram webhook")
    message = payload.get("message") or {}
    text = message.get("text")
    link_token = _token(text)
    sender = message.get("from") or {}
    chat = message.get("chat") or {}
    if link_token and sender.get("id") is not None and chat.get("id") is not None:
        await service.bind(
            channel=NotificationChannel.TELEGRAM,
            token=link_token,
            external_user_id=str(sender["id"]),
            external_chat_id=str(chat["id"]),
            username=sender.get("username"),
        )
    return {"ok": True}


@router.post("/vk/webhook", response_class=PlainTextResponse)
async def vk_webhook(
    payload: dict[str, Any],
    service: MessengerService = Depends(get_messenger_service),
) -> str:
    if settings.VK_BOT_SECRET and payload.get("secret") != settings.VK_BOT_SECRET:
        raise UnauthorizedError("Неверный секрет VK webhook")
    if payload.get("type") == "confirmation":
        return settings.VK_CONFIRMATION_CODE
    if payload.get("type") == "message_new":
        event = payload.get("object") or {}
        message = event.get("message") or event
        link_token = (
            _token(message.get("ref"))
            or _token(message.get("payload"))
            or _token(message.get("text"))
        )
        external_user_id = message.get("from_id")
        peer_id = message.get("peer_id")
        if link_token and external_user_id is not None and peer_id is not None:
            await service.bind(
                channel=NotificationChannel.VK,
                token=link_token,
                external_user_id=str(external_user_id),
                external_chat_id=str(peer_id),
            )
    return "ok"


@router.post("/max/webhook")
async def max_webhook(
    payload: dict[str, Any],
    secret: str | None = Header(default=None, alias="X-Max-Bot-Api-Secret"),
    service: MessengerService = Depends(get_messenger_service),
) -> dict[str, bool]:
    if settings.MAX_WEBHOOK_SECRET and secret != settings.MAX_WEBHOOK_SECRET:
        raise UnauthorizedError("Неверный секрет MAX webhook")
    if payload.get("update_type") == "bot_started":
        sender = payload.get("user") or {}
        link_token = _token(payload.get("payload"))
        external_user_id = sender.get("user_id")
        chat_id = payload.get("chat_id")
        if link_token and external_user_id is not None and chat_id is not None:
            await service.bind(
                channel=NotificationChannel.MAX,
                token=link_token,
                external_user_id=str(external_user_id),
                external_chat_id=str(chat_id),
                username=sender.get("username"),
            )
    return {"ok": True}

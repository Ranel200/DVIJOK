"""Клиент Zvonok.com Flash Call: код — последние четыре цифры входящего номера."""

import logging
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import httpx

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ZvonokFlashCallResult:
    code: str
    call_id: str | None
    balance: Decimal | None


def _decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _provider_detail(payload: object) -> str:
    if not isinstance(payload, dict):
        return "звонок не выполнен"
    nested = payload.get("data")
    candidates = [payload.get("message"), payload.get("detail"), payload.get("error")]
    if isinstance(nested, dict):
        candidates.extend(
            [nested.get("message"), nested.get("detail"), nested.get("error")]
        )
    return next((str(value)[:300] for value in candidates if value), "звонок не выполнен")


def _normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return f"+{digits}"


class ZvonokFlashCallProvider:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def request_code(self, phone: str, user_ip: str) -> ZvonokFlashCallResult:
        del user_ip  # Zvonok.com не принимает IP клиента в контракте Flash Call.
        if not settings.ZVONOK_PUBLIC_KEY or not settings.ZVONOK_CAMPAIGN_ID:
            raise ServiceUnavailableError("Авторизация звонком временно не настроена")

        payload = {
            "public_key": settings.ZVONOK_PUBLIC_KEY,
            "phone": _normalize_phone(phone),
            "campaign_id": settings.ZVONOK_CAMPAIGN_ID,
        }
        try:
            if self._client is not None:
                response = await self._client.post(
                    settings.ZVONOK_FLASHCALL_URL,
                    data=payload,
                    timeout=settings.ZVONOK_TIMEOUT_SECONDS,
                )
            else:
                async with httpx.AsyncClient(timeout=settings.ZVONOK_TIMEOUT_SECONDS) as client:
                    response = await client.post(settings.ZVONOK_FLASHCALL_URL, data=payload)
            response.raise_for_status()
            body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ServiceUnavailableError(
                "Сервис авторизации звонком временно недоступен"
            ) from exc

        if not isinstance(body, dict) or str(body.get("status", "")).lower() != "ok":
            detail = _provider_detail(body)
            logger.warning("Zvonok.com flash call rejected: detail=%s", detail)
            raise ServiceUnavailableError(f"Zvonok.com: {detail}")

        data = body.get("data")
        if not isinstance(data, dict):
            logger.warning("Zvonok.com flash call returned data in an invalid format")
            raise ServiceUnavailableError("Zvonok.com вернул некорректный ответ")

        code = str(data.get("pincode") or "")
        if not re.fullmatch(r"\d{4}", code):
            logger.warning(
                "Zvonok.com flash call returned an invalid pincode: call_id=%s",
                data.get("call_id"),
            )
            raise ServiceUnavailableError("Zvonok.com вернул некорректный код звонка")

        result = ZvonokFlashCallResult(
            code=code,
            call_id=str(data["call_id"]) if data.get("call_id") is not None else None,
            balance=_decimal(data.get("balance")),
        )
        logger.info(
            "Zvonok.com flash call accepted: call_id=%s balance=%s",
            result.call_id,
            result.balance,
        )
        return result

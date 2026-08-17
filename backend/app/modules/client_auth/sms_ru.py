"""Клиент SMS.ru Code Call: код — последние четыре цифры входящего номера."""

import logging
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import httpx

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SmsRuCallResult:
    code: str
    call_id: str | None
    cost: Decimal | None
    balance: Decimal | None


def _decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


class SmsRuCallProvider:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def request_code(self, phone: str, user_ip: str) -> SmsRuCallResult:
        if not settings.SMS_RU_API_ID:
            raise ServiceUnavailableError("Авторизация звонком временно не настроена")
        digits = re.sub(r"\D", "", phone)
        provider_ip = "-1" if user_ip in {"", "127.0.0.1", "::1", "testclient"} else user_ip
        payload = {
            "api_id": settings.SMS_RU_API_ID,
            "phone": digits,
            "ip": provider_ip,
        }
        try:
            if self._client is not None:
                response = await self._client.post(
                    settings.SMS_RU_CALL_URL,
                    data=payload,
                    timeout=settings.SMS_RU_TIMEOUT_SECONDS,
                )
            else:
                async with httpx.AsyncClient(timeout=settings.SMS_RU_TIMEOUT_SECONDS) as client:
                    response = await client.post(settings.SMS_RU_CALL_URL, data=payload)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ServiceUnavailableError(
                "Сервис авторизации звонком временно недоступен"
            ) from exc

        if data.get("status") != "OK":
            detail = str(data.get("status_text") or "звонок не выполнен")[:300]
            logger.warning(
                "SMS.ru code call rejected: status=%s status_code=%s detail=%s",
                data.get("status"),
                data.get("status_code"),
                detail,
            )
            raise ServiceUnavailableError(f"SMS.ru: {detail}")
        code = str(data.get("code") or "")
        if not re.fullmatch(r"\d{4}", code):
            logger.warning(
                "SMS.ru code call returned an invalid code: call_id=%s",
                data.get("call_id"),
            )
            raise ServiceUnavailableError("SMS.ru вернул некорректный код звонка")
        result = SmsRuCallResult(
            code=code,
            call_id=str(data["call_id"]) if data.get("call_id") is not None else None,
            cost=_decimal(data.get("cost")),
            balance=_decimal(data.get("balance")),
        )
        logger.info(
            "SMS.ru code call accepted: call_id=%s cost=%s balance=%s",
            result.call_id,
            result.cost,
            result.balance,
        )
        return result

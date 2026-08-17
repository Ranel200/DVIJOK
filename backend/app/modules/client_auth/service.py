"""Бизнес-логика client_auth: OTP-вход по телефону и deep-link токены бота.

OTP-код и link-токен хранятся in-memory (не Redis) — тот же паттерн, что и
InMemoryRateLimiter в app/core/rate_limit.py (см. residual-комментарий там):
достаточно для одного инстанса, при горизонтальном масштабировании вынести в
Redis.
"""

import datetime as dt
import hashlib
import hmac
import secrets
import time
import uuid

import jwt
from sqlalchemy import select, update

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.rate_limit import InMemoryRateLimiter
from app.core.security import (
    create_client_access_token,
    create_client_refresh_token,
    decode_token,
)
from app.modules.client_auth.models import ClientAccount, ClientRefreshSession
from app.modules.client_auth.repository import ClientAuthRepository
from app.modules.client_auth.sms_ru import SmsRuCallProvider
from app.modules.client_auth.zvonok import ZvonokFlashCallProvider
from app.modules.clients.models import Client
from app.modules.referrals.repository import ReferralRepository
from app.modules.referrals.service import ReferralService


def _hash_code(phone: str, code: str) -> str:
    return hashlib.sha256(f"{phone}:{code}:{settings.OTP_PEPPER}".encode()).hexdigest()


class _OtpEntry:
    __slots__ = ("code_hash", "expires_at", "attempts_left")

    def __init__(self, code_hash: str, expires_at: float, attempts_left: int) -> None:
        self.code_hash = code_hash
        self.expires_at = expires_at
        self.attempts_left = attempts_left


class OtpStore:
    """In-memory TTL-хранилище OTP-кодов. Residual: вынести в Redis при масштабировании."""

    def __init__(self) -> None:
        self._entries: dict[str, _OtpEntry] = {}

    def put(self, phone: str, code: str) -> None:
        self._entries[phone] = _OtpEntry(
            code_hash=_hash_code(phone, code),
            expires_at=time.time() + settings.OTP_CODE_TTL_SECONDS,
            attempts_left=settings.OTP_MAX_ATTEMPTS,
        )

    def verify(self, phone: str, code: str) -> bool:
        entry = self._entries.get(phone)
        if entry is None or entry.expires_at < time.time():
            self._entries.pop(phone, None)
            return False
        if entry.attempts_left <= 0:
            self._entries.pop(phone, None)
            return False
        entry.attempts_left -= 1
        ok = hmac.compare_digest(entry.code_hash, _hash_code(phone, code))
        if ok or entry.attempts_left <= 0:
            self._entries.pop(phone, None)
        return ok

    def reset(self) -> None:
        self._entries.clear()


class LinkTokenStore:
    """In-memory одноразовые deep-link токены (привязка Telegram/VK к ClientAccount)."""

    def __init__(self) -> None:
        self._entries: dict[str, tuple[int, float]] = {}

    def issue(self, client_account_id: int) -> str:
        token = secrets.token_urlsafe(32)
        self._entries[token] = (
            client_account_id,
            time.time() + settings.CLIENT_LINK_TOKEN_TTL_SECONDS,
        )
        return token

    def consume(self, token: str) -> int | None:
        entry = self._entries.pop(token, None)
        if entry is None:
            return None
        account_id, expires_at = entry
        if expires_at < time.time():
            return None
        return account_id

    def reset(self) -> None:
        self._entries.clear()


otp_store = OtpStore()
link_token_store = LinkTokenStore()

# Лимит запросов кода на номер телефона — защита от спама SMS/перебора.
otp_request_limiter = InMemoryRateLimiter(
    max_attempts=settings.OTP_RATE_LIMIT_ATTEMPTS,
    window_seconds=settings.OTP_RATE_LIMIT_WINDOW_SECONDS,
)
otp_ip_limiter = InMemoryRateLimiter(
    max_attempts=settings.OTP_IP_RATE_LIMIT_ATTEMPTS,
    window_seconds=settings.OTP_IP_RATE_LIMIT_WINDOW_SECONDS,
)
def consume_link_token(token: str) -> int | None:
    """Module-level helper для bot_gateway: одноразовое потребление deep-link токена."""
    return link_token_store.consume(token)


class ClientAuthService:
    def __init__(
        self,
        repo: ClientAuthRepository,
        referral_repo: ReferralRepository,
        sms_ru: SmsRuCallProvider | None = None,
        zvonok: ZvonokFlashCallProvider | None = None,
    ) -> None:
        self.repo = repo
        self.referrals = ReferralService(referral_repo)
        self.sms_ru = sms_ru or SmsRuCallProvider()
        self.zvonok = zvonok or ZvonokFlashCallProvider()

    async def request_otp(self, phone: str, user_ip: str) -> str:
        otp_request_limiter.check(f"otp:{phone}")
        otp_ip_limiter.check(f"otp-ip:{user_ip or 'unknown'}")
        if settings.OTP_PROVIDER == "sms_ru_call":
            code = (await self.sms_ru.request_code(phone, user_ip)).code
        elif settings.OTP_PROVIDER == "zvonok_flashcall":
            code = (await self.zvonok.request_code(phone, user_ip)).code
        else:
            code = "".join(
                str(secrets.randbelow(10)) for _ in range(settings.OTP_CODE_LENGTH)
            )
        otp_store.put(phone, code)
        return code

    async def verify_otp(
        self,
        phone: str,
        code: str,
        referral_code: str | None = None,
        full_name: str | None = None,
    ) -> ClientAccount:
        if not otp_store.verify(phone, code):
            raise UnauthorizedError("Неверный или истёкший код")
        account = await self.repo.get_by_phone(phone)

        # Гостевая запись может быть создана раньше client_accounts. Сохраняем
        # её ФИО до привязки карточек, чтобы первый вход по номеру не терял
        # данные из формы /book.
        guest_name = (
            await self.repo.session.execute(
                select(Client.full_name)
                .where(
                    Client.phone == phone,
                    Client.client_account_id.is_(None),
                    Client.full_name.is_not(None),
                    Client.full_name != "",
                    Client.full_name != f"Клиент {phone}",
                )
                .order_by(Client.id.asc())
                .limit(1)
            )
        ).scalar_one_or_none()
        requested_name = full_name.strip() if full_name and full_name.strip() else None
        guest_name = guest_name.strip() if guest_name and guest_name.strip() else None
        if account is None:
            account = await self.repo.add(
                ClientAccount(phone=phone, full_name=requested_name or guest_name)
            )
        elif self._is_generated_name(account.full_name, account.phone):
            profile_name = requested_name or guest_name
            if profile_name:
                account.full_name = profile_name
                await self.repo.session.execute(
                    update(Client)
                    .where(
                        Client.client_account_id == account.id,
                        Client.full_name == f"Клиент {account.phone}",
                    )
                    .values(full_name=account.full_name)
                )
                await self.repo.session.flush()
        if not account.is_active:
            raise UnauthorizedError("Учётная запись деактивирована")
        # Гостевая запись может существовать раньше клиентской учётки. После
        # подтверждения того же телефона связываем такие tenant-карточки, чтобы
        # история и уведомления заработали без повторного создания заказа.
        await self.repo.session.execute(
            update(Client)
            .where(
                Client.phone == phone,
                Client.client_account_id.is_(None),
            )
            .values(client_account_id=account.id)
        )
        # First-touch attribution: once set, even another valid code is ignored.
        # Existing unattributed accounts may be attributed on their first login
        # carrying a referral code.
        if referral_code is not None and account.source_organization_id is None:
            account.source_organization_id = await self.referrals.resolve_organization(
                referral_code
            )
            await self.repo.session.flush()
            await self.repo.session.refresh(account)
        return account

    @staticmethod
    def _is_generated_name(full_name: str | None, phone: str) -> bool:
        return not full_name or full_name == f"Клиент {phone}"

    async def update_profile(
        self,
        account: ClientAccount,
        full_name: str,
    ) -> ClientAccount:
        """Сохраняет ФИО глобального клиента и синхронизирует его CRM-карточки."""
        account.full_name = full_name.strip()
        await self.repo.session.execute(
            update(Client)
            .where(Client.client_account_id == account.id)
            .values(full_name=account.full_name)
        )
        await self.repo.session.flush()
        await self.repo.session.refresh(account)
        return account

    def issue_tokens(self, account: ClientAccount) -> tuple[str, str]:
        return create_client_access_token(account.id), create_client_refresh_token(account.id)

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def _now() -> dt.datetime:
        return dt.datetime.now(dt.UTC)

    async def create_session(
        self,
        account: ClientAccount,
        *,
        ip: str,
        user_agent: str,
    ) -> tuple[str, str]:
        token = create_client_refresh_token(account.id, token_id=uuid.uuid4().hex)
        session = ClientRefreshSession(
            client_account_id=account.id,
            token_hash=self._token_hash(token),
            expires_at=self._now()
            + dt.timedelta(days=settings.CLIENT_REFRESH_TOKEN_EXPIRE_DAYS),
            ip=ip[:64],
            user_agent=user_agent[:2000],
        )
        self.repo.session.add(session)
        await self.repo.session.flush()
        return create_client_access_token(account.id), token

    async def refresh(self, refresh_token: str) -> tuple[str, str | None]:
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Невалидный или просроченный refresh-токен") from exc
        if payload.get("type") != "refresh" or payload.get("actor") != "client":
            raise UnauthorizedError("Ожидался клиентский refresh-токен")
        subject = payload.get("sub")
        if subject is None:
            raise UnauthorizedError("Токен без субъекта")
        account = await self.repo.get_by_id(int(subject))
        if account is None or not account.is_active:
            raise UnauthorizedError("Клиент не найден или неактивен")
        if payload.get("jti") is None:
            # Старые stateless-токены остаются рабочими до истечения срока, но
            # новый frontend получает только rotating sessions.
            return create_client_access_token(account.id), None

        session = (
            await self.repo.session.execute(
                select(ClientRefreshSession).where(
                    ClientRefreshSession.client_account_id == account.id,
                    ClientRefreshSession.token_hash == self._token_hash(refresh_token),
                )
            )
        ).scalar_one_or_none()
        if session is None or session.revoked_at is not None:
            raise UnauthorizedError("Клиентская сессия завершена или не найдена")
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=dt.UTC)
        if expires_at <= self._now():
            raise UnauthorizedError("Клиентская сессия истекла")

        rotated = create_client_refresh_token(account.id, token_id=uuid.uuid4().hex)
        session.token_hash = self._token_hash(rotated)
        session.last_used_at = self._now()
        session.expires_at = self._now() + dt.timedelta(
            days=settings.CLIENT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.repo.session.flush()
        return create_client_access_token(account.id), rotated

    async def revoke(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        session = (
            await self.repo.session.execute(
                select(ClientRefreshSession).where(
                    ClientRefreshSession.token_hash == self._token_hash(refresh_token)
                )
            )
        ).scalar_one_or_none()
        if session is not None and session.revoked_at is None:
            session.revoked_at = self._now()
            await self.repo.session.flush()

    def issue_link_token(self, client_account_id: int) -> str:
        return link_token_store.issue(client_account_id)

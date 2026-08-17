"""Сервис аутентификации сотрудников Admin-панели."""

import datetime as dt
import hashlib
import uuid

import jwt
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import StaffLoginEvent, StaffRefreshSession
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

# Фиксированный хэш для выравнивания времени ответа, когда пользователь не найден
# (защита от user-enumeration по тайминг-атаке).
_DUMMY_HASH = hash_password("timing-attack-equalizer")


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def authenticate(self, identifier: str, password: str) -> User:
        user = await self.repo.get_by_identifier(identifier)
        if user is None:
            # Выполняем фиктивную проверку, чтобы время ответа не выдавало
            # существование идентификатора, затем отвечаем тем же общим сообщением.
            verify_password(password, _DUMMY_HASH)
            raise UnauthorizedError("Неверный телефон, почта, логин или пароль")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Неверный телефон, почта, логин или пароль")
        if not user.is_active:
            raise UnauthorizedError("Учётная запись отключена")
        return user

    def issue_tokens(self, user: User) -> tuple[str, str]:
        """Legacy stateless pair kept for the old organizations/register API."""

        return (
            create_access_token(user.id, user.role.value),
            create_refresh_token(user.id),
        )

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def _now() -> dt.datetime:
        return dt.datetime.now(dt.UTC)

    async def create_session(
        self,
        user: User,
        *,
        remember: bool,
        ip: str,
        user_agent: str,
    ) -> tuple[str, str, StaffRefreshSession]:
        expire_days = (
            settings.REMEMBER_REFRESH_TOKEN_EXPIRE_DAYS
            if remember
            else settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        refresh = create_refresh_token(
            user.id,
            token_id=uuid.uuid4().hex,
            expire_days=expire_days,
        )
        session = StaffRefreshSession(
            organization_id=user.organization_id,
            user_id=user.id,
            token_hash=self._token_hash(refresh),
            expires_at=self._now() + dt.timedelta(days=expire_days),
            remember=remember,
            ip=ip[:64],
            user_agent=user_agent[:2000],
        )
        self.repo.session.add(session)
        await self.repo.session.flush()
        access = create_access_token(user.id, user.role.value, session.id)
        return access, refresh, session

    async def record_login(
        self,
        identifier: str,
        *,
        success: bool,
        user: User | None,
        ip: str,
        user_agent: str,
    ) -> None:
        self.repo.session.add(
            StaffLoginEvent(
                organization_id=user.organization_id if user else None,
                user_id=user.id if user else None,
                identifier=identifier.strip()[:255],
                success=success,
                ip=ip[:64],
                user_agent=user_agent[:2000],
            )
        )
        await self.repo.session.flush()

    async def refresh(self, refresh_token: str) -> tuple[str, str | None, bool]:
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Невалидный refresh-токен") from exc
        if payload.get("type") != "refresh" or payload.get("actor") not in {None, "staff"}:
            raise UnauthorizedError("Ожидался refresh-токен")
        subject = payload.get("sub")
        if subject is None:
            raise UnauthorizedError("Токен без субъекта")
        user = await self.repo.get_unscoped(int(subject))
        if user is None or not user.is_active:
            raise UnauthorizedError("Пользователь не найден или неактивен")
        if payload.get("jti") is None:
            # Backward compatibility for refresh tokens issued before sessions.
            return create_access_token(user.id, user.role.value), None, False

        session = (
            await self.repo.session.execute(
                select(StaffRefreshSession).where(
                    StaffRefreshSession.token_hash == self._token_hash(refresh_token),
                    StaffRefreshSession.user_id == user.id,
                )
            )
        ).scalar_one_or_none()
        if session is None or session.revoked_at is not None:
            raise UnauthorizedError("Сессия завершена или не найдена")
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=dt.UTC)
        if expires_at <= self._now():
            raise UnauthorizedError("Сессия истекла")

        expire_days = (
            settings.REMEMBER_REFRESH_TOKEN_EXPIRE_DAYS
            if session.remember
            else settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        rotated = create_refresh_token(
            user.id,
            token_id=uuid.uuid4().hex,
            expire_days=expire_days,
        )
        session.token_hash = self._token_hash(rotated)
        session.last_used_at = self._now()
        session.expires_at = self._now() + dt.timedelta(days=expire_days)
        await self.repo.session.flush()
        return (
            create_access_token(user.id, user.role.value, session.id),
            rotated,
            session.remember,
        )

    async def revoke_token(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        session = (
            await self.repo.session.execute(
                select(StaffRefreshSession).where(
                    StaffRefreshSession.token_hash == self._token_hash(refresh_token)
                )
            )
        ).scalar_one_or_none()
        if session is not None and session.revoked_at is None:
            session.revoked_at = self._now()
            await self.repo.session.flush()

    async def revoke_session(self, user: User, session_id: int) -> None:
        session = (
            await self.repo.session.execute(
                select(StaffRefreshSession).where(
                    StaffRefreshSession.id == session_id,
                    StaffRefreshSession.user_id == user.id,
                )
            )
        ).scalar_one_or_none()
        if session is None:
            raise UnauthorizedError("Сессия не найдена")
        session.revoked_at = self._now()
        await self.repo.session.flush()

    async def revoke_other_sessions(self, user: User, current_session_id: int | None) -> None:
        sessions = list(
            (
                await self.repo.session.execute(
                    select(StaffRefreshSession).where(
                        StaffRefreshSession.user_id == user.id,
                        StaffRefreshSession.revoked_at.is_(None),
                    )
                )
            )
            .scalars()
            .all()
        )
        now = self._now()
        for session in sessions:
            if session.id != current_session_id:
                session.revoked_at = now
        await self.repo.session.flush()

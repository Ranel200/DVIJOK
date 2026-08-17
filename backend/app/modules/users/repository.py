"""Репозиторий модуля users."""

from sqlalchemy import select

from app.modules.users.models import User
from app.shared.base_repository import BaseRepository
from app.shared.identifiers import normalize_email, normalize_login, normalize_phone


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == normalize_email(email))
        )
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str) -> User | None:
        normalized = normalize_login(login)
        if normalized is None:
            return None
        result = await self.session.execute(select(User).where(User.login == normalized))
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        normalized = normalize_phone(phone)
        if normalized is None:
            return None
        result = await self.session.execute(
            select(User).where(User.normalized_phone == normalized)
        )
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> User | None:
        """Resolve an identifier without ambiguous cross-namespace matches."""

        if normalize_phone(identifier) is not None:
            return await self.get_by_phone(identifier)
        if "@" in identifier:
            return await self.get_by_email(identifier)
        return await self.get_by_login(identifier)

    async def get_unscoped(self, user_id: int) -> User | None:
        """Поиск по id без фильтра по организации — используется auth-контуром
        (login/refresh/get_current_user), где organization_id ещё не известен."""
        return await self.session.get(User, user_id)

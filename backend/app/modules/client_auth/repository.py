"""Репозиторий client_auth.

ClientAccount — глобальная сущность (не tenant-scoped), поэтому здесь, как и в
app/modules/organizations/repository.py, не используется BaseRepository (та
фильтрует все запросы по organization_id).
"""

from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client_auth.models import ClientAccount
from app.modules.client_auth.phone import normalize_client_phone


class ClientAuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, account_id: int) -> ClientAccount | None:
        return await self.session.get(ClientAccount, account_id)

    async def get_by_phone(self, phone: str) -> ClientAccount | None:
        result = await self.session.execute(
            select(ClientAccount).where(ClientAccount.phone == phone)
        )
        account = result.scalar_one_or_none()
        if account is not None:
            return account

        # Backward compatibility for accounts written before canonical phone
        # normalization. The matched row is healed on its next successful OTP.
        accounts = list((await self.session.execute(select(ClientAccount))).scalars().all())
        for candidate in accounts:
            try:
                canonical = normalize_client_phone(candidate.phone)
            except ValueError:
                continue
            if canonical == phone:
                candidate.phone = phone
                await self.session.flush()
                return candidate
        return None

    async def get_by_telegram_id(self, telegram_id: str) -> ClientAccount | None:
        result = await self.session.execute(
            select(ClientAccount).where(ClientAccount.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_id: str) -> ClientAccount | None:
        result = await self.session.execute(
            select(ClientAccount).where(ClientAccount.vk_id == vk_id)
        )
        return result.scalar_one_or_none()

    async def add(self, account: ClientAccount) -> ClientAccount:
        self.session.add(account)
        await self.session.flush()
        await self.session.refresh(account)
        return account

    async def set_messenger_id(
        self, account: ClientAccount, channel: Literal["telegram", "vk"], external_id: str
    ) -> ClientAccount:
        if channel == "telegram":
            account.telegram_id = external_id
        else:
            account.vk_id = external_id
        await self.session.flush()
        await self.session.refresh(account)
        return account

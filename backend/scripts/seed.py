"""Создание первичного администратора (idempotent).

Запуск:  python -m scripts.seed
Параметры берутся из .env (FIRST_ADMIN_*).
"""

import asyncio

from sqlalchemy import select

import app.models  # noqa
from app.core.config import settings
from app.core.database import async_session_factory, engine
from app.core.security import hash_password
from app.modules.organizations.models import Organization
from app.modules.users.models import User
from app.shared.enums import LegalForm, OrganizationStatus, TaxSystem, UserRole


async def main() -> None:
    async with async_session_factory() as session:
        existing = await session.execute(
            select(User).where(User.email == settings.FIRST_ADMIN_EMAIL)
        )
        if existing.scalar_one_or_none() is not None:
            print(f"Администратор уже существует: {settings.FIRST_ADMIN_EMAIL}")
            return

        # Тенант-плейсхолдер для dev-окружения; реальные организации создаются
        # через POST /organizations/register.
        organization = Organization(
            name=settings.APP_NAME,
            inn="0000000000",
            tax_system=TaxSystem.USN,
            legal_form=LegalForm.OOO,
            legal_address="—",
            phone="+70000000000",
            status=OrganizationStatus.ACTIVE,
        )
        session.add(organization)
        await session.flush()

        user = User(
            organization_id=organization.id,
            email=settings.FIRST_ADMIN_EMAIL,
            full_name=settings.FIRST_ADMIN_NAME,
            role=UserRole.ADMIN,
            is_owner=True,
            hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
        )
        session.add(user)
        await session.commit()
        print(f"Создан администратор: {user.email} (пароль из FIRST_ADMIN_PASSWORD)")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

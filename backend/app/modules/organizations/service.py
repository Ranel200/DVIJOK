"""Бизнес-логика модуля organizations: регистрация тенанта + настройки профиля."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.modules.organizations.models import Organization
from app.modules.organizations.repository import OrganizationRepository
from app.modules.organizations.schemas import OrganizationRegister, OrganizationUpdate
from app.modules.services.models import Service
from app.modules.users.models import User
from app.shared.enums import ServiceCategory, ServicePriceType, UserRole
from app.shared.identifiers import normalize_phone


class OrganizationService:
    def __init__(self, repo: OrganizationRepository) -> None:
        self.repo = repo
        self.session: AsyncSession = repo.session

    async def get(self, organization_id: int) -> Organization:
        organization = await self.repo.get(organization_id)
        if organization is None:
            raise NotFoundError("Организация не найдена")
        return organization

    async def update(self, organization_id: int, data: OrganizationUpdate) -> Organization:
        organization = await self.get(organization_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(organization, field, value)
        return await self.repo.update(organization)

    async def register(self, data: OrganizationRegister) -> tuple[str, str]:
        """Создаёт организацию и её первого администратора, выдаёт пару токенов."""
        email = data.admin_email.strip().lower()
        phone = normalize_phone(data.phone)
        if phone is None:
            raise BusinessRuleError("Некорректный номер телефона")
        inn_taken = bool(await self.repo.get_by_inn(data.inn))
        email_taken = (
            await self.session.execute(select(User).where(User.email == email))
        ).scalar_one_or_none() is not None
        phone_taken = (
            await self.session.execute(select(User.id).where(User.normalized_phone == phone))
        ).scalar_one_or_none() is not None
        if inn_taken or email_taken or phone_taken:
            raise ConflictError("Организация или аккаунт с такими данными уже зарегистрированы")

        organization = await self.repo.add(
            Organization(
                name=data.name,
                inn=data.inn,
                tax_system=data.tax_system,
                legal_form=data.legal_form,
                legal_address=data.legal_address,
                phone=phone,
                # Новая admin-панель предлагает владельцу выбрать тариф сразу
                # после регистрации. Уже существующие организации не меняются.
                subscription_plan="NONE",
            )
        )

        # The client application has two stable coarse booking choices. The
        # detailed price list remains separate and can contain any services.
        self.session.add_all(
            [
                Service(
                    organization_id=organization.id,
                    name="Диагностика",
                    public_booking_key="diagnostics",
                    category=ServiceCategory.DIAGNOSTICS,
                    admin_category="diagnostics",
                    base_price=Decimal("0.00"),
                    price_type=ServicePriceType.NEGOTIABLE,
                    duration_minutes=60,
                ),
                Service(
                    organization_id=organization.id,
                    name="Ремонт",
                    public_booking_key="repair",
                    category=ServiceCategory.OTHER,
                    admin_category="repair",
                    base_price=Decimal("0.00"),
                    price_type=ServicePriceType.NEGOTIABLE,
                    duration_minutes=60,
                ),
            ]
        )

        admin = User(
            organization_id=organization.id,
            email=email,
            phone=phone,
            normalized_phone=phone,
            full_name=data.admin_full_name,
            role=UserRole.ADMIN,
            staff_role_key="senior_admin",
            is_owner=True,
            hashed_password=hash_password(data.admin_password),
        )
        self.session.add(admin)
        await self.session.flush()
        await self.session.refresh(admin)

        return (
            create_access_token(admin.id, admin.role.value),
            create_refresh_token(admin.id),
        )

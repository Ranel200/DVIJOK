"""Общие фикстуры тестов: in-memory SQLite (async), переопределение get_db,
авторизованный HTTP-клиент."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  — регистрация моделей в metadata
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import login_limiter, public_booking_limiter
from app.core.security import hash_password
from app.main import app
from app.modules.organizations.models import Organization
from app.modules.users.models import User
from app.shared.base_model import Base
from app.shared.enums import LegalForm, OrganizationStatus, TaxSystem, UserRole

API = "/api/v1"


@pytest.fixture(autouse=True)
def _reset_login_limiter():
    """Сбрасываем счётчик rate-limit между тестами, чтобы лимит не протекал."""
    login_limiter.reset()
    public_booking_limiter.reset()
    yield
    login_limiter.reset()
    public_booking_limiter.reset()


@pytest.fixture(autouse=True)
def _disable_paid_integrations(monkeypatch):
    """Ни один тест не должен случайно вызвать платный OTP-провайдер."""
    monkeypatch.setattr(settings, "OTP_PROVIDER", "local")


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def organization(session_factory):
    async with session_factory() as session:
        org = Organization(
            name="КОМИТ Тест",
            inn="1234567890",
            tax_system=TaxSystem.USN,
            legal_form=LegalForm.OOO,
            legal_address="г. Москва, тестовая",
            phone="+70000000000",
            status=OrganizationStatus.ACTIVE,
        )
        session.add(org)
        await session.commit()
        await session.refresh(org)
        return org.id


@pytest_asyncio.fixture
async def admin(session_factory, organization):
    async with session_factory() as session:
        session.add(
            User(
                organization_id=organization,
                email="admin@komit.ru",
                full_name="Админ",
                role=UserRole.ADMIN,
                is_owner=True,
                hashed_password=hash_password("admin12345"),
            )
        )
        await session.commit()
    return {"email": "admin@komit.ru", "password": "admin12345", "organization_id": organization}


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client, admin):
    resp = await client.post(
        f"{API}/auth/login",
        data={"username": admin["email"], "password": admin["password"]},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

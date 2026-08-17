"""Тесты client_auth: OTP-вход по телефону, get_current_client, deep-link токены.

Роутер client_auth пока не зарегистрирован в app.main (интеграция — отдельная
задача координатора), поэтому тесты поднимают собственное лёгкое FastAPI-
приложение с auth_router + client_auth_router, переиспользуя session_factory
из tests/conftest.py.
"""

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

import app.modules.client_auth.models  # noqa: F401 — регистрация ClientAccount в Base.metadata
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import register_exception_handlers
from app.core.security import hash_password
from app.modules.auth.router import router as auth_router
from app.modules.client_auth.models import ClientAccount
from app.modules.client_auth.router import router as client_auth_router
from app.modules.client_auth.service import (
    consume_link_token,
    link_token_store,
    otp_ip_limiter,
    otp_request_limiter,
    otp_store,
)
from app.modules.client_auth.sms_ru import SmsRuCallProvider, SmsRuCallResult
from app.modules.client_auth.zvonok import ZvonokFlashCallProvider, ZvonokFlashCallResult
from app.modules.clients.models import Client
from app.modules.referrals.models import OrganizationReferral
from app.modules.users.models import User
from app.shared.enums import UserRole
from tests.conftest import API


def _build_app() -> FastAPI:
    test_app = FastAPI()
    register_exception_handlers(test_app)
    test_app.include_router(auth_router, prefix=API)
    test_app.include_router(client_auth_router, prefix=API)
    return test_app


@pytest_asyncio.fixture(autouse=True)
def _reset_client_auth_state():
    otp_store.reset()
    link_token_store.reset()
    otp_request_limiter.reset()
    otp_ip_limiter.reset()
    yield
    otp_store.reset()
    link_token_store.reset()
    otp_request_limiter.reset()
    otp_ip_limiter.reset()


@pytest_asyncio.fixture
async def ca_client(session_factory):
    test_app = _build_app()

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    test_app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def _request_and_get_code(ca_client, phone: str) -> str:
    resp = await ca_client.post(f"{API}/client-auth/otp/request", json={"phone": phone})
    assert resp.status_code == 200, resp.text
    code = resp.json()["debug_code"]
    assert code is not None  # settings.DEBUG=True в тестовом окружении
    assert len(code) == 4
    assert code.isdigit()
    return code


async def test_otp_happy_path_issues_tokens(ca_client):
    phone = "+79990001122"
    code = await _request_and_get_code(ca_client, phone)
    resp = await ca_client.post(
        f"{API}/client-auth/otp/verify", json={"phone": phone, "code": code}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["access_token"] and body["refresh_token"]

    me = await ca_client.get(
        f"{API}/client-auth/me", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["phone"] == phone


async def test_first_login_copies_name_from_guest_crm_card(
    ca_client, session_factory, organization
):
    phone = "+79990001124"
    async with session_factory() as session:
        session.add(
            Client(
                organization_id=organization,
                full_name="Иванов Иван Иванович",
                phone=phone,
            )
        )
        await session.commit()

    code = await _request_and_get_code(ca_client, phone)
    response = await ca_client.post(
        f"{API}/client-auth/otp/verify", json={"phone": phone, "code": code}
    )
    assert response.status_code == 200, response.text

    async with session_factory() as session:
        account = (
            await session.execute(select(ClientAccount).where(ClientAccount.phone == phone))
        ).scalar_one()
        client = (
            await session.execute(select(Client).where(Client.phone == phone))
        ).scalar_one()

    assert account.full_name == "Иванов Иван Иванович"
    assert client.client_account_id == account.id


async def test_profile_name_update_replaces_placeholder_in_linked_crm_clients(
    ca_client, session_factory, organization
):
    phone = "+79990001123"
    placeholder = f"Клиент {phone}"
    async with session_factory() as session:
        account = ClientAccount(phone=phone, full_name=placeholder)
        session.add(account)
        await session.flush()
        session.add(
            Client(
                organization_id=organization,
                full_name=placeholder,
                phone=phone,
                client_account_id=account.id,
            )
        )
        await session.commit()

    code = await _request_and_get_code(ca_client, phone)
    verify = await ca_client.post(
        f"{API}/client-auth/otp/verify", json={"phone": phone, "code": code}
    )
    access_token = verify.json()["access_token"]

    updated = await ca_client.patch(
        f"{API}/client-auth/me",
        json={"full_name": "  Нагимов Ранель  "},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert updated.status_code == 200, updated.text
    assert updated.json()["full_name"] == "Нагимов Ранель"
    async with session_factory() as session:
        account_name = (
            await session.execute(
                select(ClientAccount.full_name).where(ClientAccount.phone == phone)
            )
        ).scalar_one()
        crm_name = (
            await session.execute(select(Client.full_name).where(Client.phone == phone))
        ).scalar_one()
    assert account_name == "Нагимов Ранель"
    assert crm_name == "Нагимов Ранель"


async def test_sms_ru_call_code_is_used_but_never_returned(ca_client, monkeypatch):
    calls = []

    async def fake_call(self, phone: str, user_ip: str) -> SmsRuCallResult:
        calls.append((phone, user_ip))
        return SmsRuCallResult(code="4821", call_id="call-1", cost=None, balance=None)

    monkeypatch.setattr(settings, "OTP_PROVIDER", "sms_ru_call")
    monkeypatch.setattr(settings, "SMS_RU_API_ID", "test-key")
    monkeypatch.setattr(SmsRuCallProvider, "request_code", fake_call)

    requested = await ca_client.post(
        f"{API}/client-auth/otp/request", json={"phone": "+79990001199"}
    )
    assert requested.status_code == 200, requested.text
    assert requested.json()["debug_code"] is None
    assert "последние 4 цифры" in requested.json()["detail"]
    assert calls and calls[0][0] == "+79990001199"

    verified = await ca_client.post(
        f"{API}/client-auth/otp/verify",
        json={"phone": "+79990001199", "code": "4821"},
    )
    assert verified.status_code == 200, verified.text


async def test_sms_ru_calls_are_not_globally_limited(ca_client, monkeypatch):
    calls = 0

    async def fake_call(self, phone: str, user_ip: str) -> SmsRuCallResult:
        nonlocal calls
        calls += 1
        return SmsRuCallResult(code="1357", call_id=str(calls), cost=None, balance=None)

    monkeypatch.setattr(settings, "OTP_PROVIDER", "sms_ru_call")
    monkeypatch.setattr(settings, "SMS_RU_API_ID", "test-key")
    monkeypatch.setattr(SmsRuCallProvider, "request_code", fake_call)

    statuses = []
    for suffix in range(6):
        response = await ca_client.post(
            f"{API}/client-auth/otp/request",
            json={"phone": f"+799911100{suffix:02d}"},
        )
        statuses.append(response.status_code)
    assert statuses == [200] * 6
    assert calls == 6


async def test_zvonok_flashcall_code_is_used_but_never_returned(ca_client, monkeypatch):
    calls = []

    async def fake_call(self, phone: str, user_ip: str) -> ZvonokFlashCallResult:
        calls.append((phone, user_ip))
        return ZvonokFlashCallResult(code="7319", call_id="call-2", balance=None)

    monkeypatch.setattr(settings, "OTP_PROVIDER", "zvonok_flashcall")
    monkeypatch.setattr(settings, "ZVONOK_PUBLIC_KEY", "test-key")
    monkeypatch.setattr(settings, "ZVONOK_CAMPAIGN_ID", "campaign-1")
    monkeypatch.setattr(ZvonokFlashCallProvider, "request_code", fake_call)

    requested = await ca_client.post(
        f"{API}/client-auth/otp/request", json={"phone": "+79990001200"}
    )
    assert requested.status_code == 200, requested.text
    assert requested.json()["debug_code"] is None
    assert "последние 4 цифры" in requested.json()["detail"]
    assert calls and calls[0][0] == "+79990001200"

    verified = await ca_client.post(
        f"{API}/client-auth/otp/verify",
        json={"phone": "+79990001200", "code": "7319"},
    )
    assert verified.status_code == 200, verified.text


async def test_masked_phone_name_cookie_refresh_and_logout(ca_client):
    request = await ca_client.post(
        f"{API}/client-auth/otp/request",
        json={"phone": "8 (999) 111-22-33"},
    )
    assert request.status_code == 200, request.text
    code = request.json()["debug_code"]

    verify = await ca_client.post(
        f"{API}/client-auth/otp/verify",
        json={
            "phone": "+7 999 111 22 33",
            "code": code,
            "full_name": "Иван Клиентский",
        },
    )
    assert verify.status_code == 200, verify.text
    assert settings.CLIENT_REFRESH_COOKIE_NAME in ca_client.cookies

    access = verify.json()["access_token"]
    me = await ca_client.get(
        f"{API}/client-auth/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert me.json()["phone"] == "+79991112233"
    assert me.json()["full_name"] == "Иван Клиентский"

    refreshed = await ca_client.post(f"{API}/client-auth/refresh")
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["access_token"]

    logout = await ca_client.post(
        f"{API}/client-auth/logout",
        headers={"Authorization": f"Bearer {refreshed.json()['access_token']}"},
    )
    assert logout.status_code == 200, logout.text
    assert settings.CLIENT_REFRESH_COOKIE_NAME not in ca_client.cookies


async def test_wrong_code_rejected(ca_client):
    phone = "+79990001133"
    await _request_and_get_code(ca_client, phone)
    resp = await ca_client.post(
        f"{API}/client-auth/otp/verify", json={"phone": phone, "code": "0000"}
    )
    assert resp.status_code == 401


async def test_six_digit_code_is_rejected_by_frontend_contract(ca_client):
    response = await ca_client.post(
        f"{API}/client-auth/otp/verify",
        json={"phone": "+79990001134", "code": "123456"},
    )
    assert response.status_code == 422


async def test_code_exhausted_after_max_attempts(ca_client):
    phone = "+79990001144"
    await _request_and_get_code(ca_client, phone)
    for _ in range(settings.OTP_MAX_ATTEMPTS):
        resp = await ca_client.post(
            f"{API}/client-auth/otp/verify", json={"phone": phone, "code": "0000"}
        )
        assert resp.status_code == 401
    # код инвалидирован даже если бы теперь угадали правильный
    resp = await ca_client.post(
        f"{API}/client-auth/otp/verify", json={"phone": phone, "code": "0000"}
    )
    assert resp.status_code == 401


async def test_expired_code_rejected(ca_client):
    phone = "+79990001177"
    code = await _request_and_get_code(ca_client, phone)
    otp_store._entries[phone].expires_at -= 10_000  # искусственно истёк
    resp = await ca_client.post(
        f"{API}/client-auth/otp/verify", json={"phone": phone, "code": code}
    )
    assert resp.status_code == 401


async def test_otp_request_rate_limited(ca_client):
    phone = "+79990001155"
    statuses = []
    for _ in range(settings.OTP_RATE_LIMIT_ATTEMPTS + 2):
        resp = await ca_client.post(f"{API}/client-auth/otp/request", json={"phone": phone})
        statuses.append(resp.status_code)
    assert 429 in statuses


async def test_staff_token_rejected_on_client_me(ca_client, session_factory, organization):
    async with session_factory() as session:
        session.add(
            User(
                organization_id=organization,
                email="staff@komit.ru",
                full_name="Staff",
                role=UserRole.ADMIN,
                hashed_password=hash_password("staff-pass-1"),
            )
        )
        await session.commit()

    login = await ca_client.post(
        f"{API}/auth/login", data={"username": "staff@komit.ru", "password": "staff-pass-1"}
    )
    assert login.status_code == 200, login.text
    staff_token = login.json()["access_token"]

    resp = await ca_client.get(
        f"{API}/client-auth/me", headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert resp.status_code == 401


async def test_link_token_single_use(ca_client, session_factory):
    async with session_factory() as session:
        account = ClientAccount(phone="+79990001166")
        session.add(account)
        await session.commit()
        await session.refresh(account)
        account_id = account.id

    code = await _request_and_get_code(ca_client, "+79990001166")
    verify = await ca_client.post(
        f"{API}/client-auth/otp/verify", json={"phone": "+79990001166", "code": code}
    )
    access_token = verify.json()["access_token"]

    link = await ca_client.post(
        f"{API}/client-auth/link-token", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert link.status_code == 200, link.text
    token = link.json()["link_token"]

    assert consume_link_token(token) == account_id
    assert consume_link_token(token) is None


async def test_referral_code_attributes_new_client_once(
    ca_client, session_factory, organization
):
    async with session_factory() as session:
        referral = OrganizationReferral(
            organization_id=organization,
            code="ReferralCode0001",
        )
        session.add(referral)
        await session.commit()

    phone = "+79990002211"
    code = await _request_and_get_code(ca_client, phone)
    response = await ca_client.post(
        f"{API}/client-auth/otp/verify",
        json={
            "phone": phone,
            "code": code,
            "referral_code": "ReferralCode0001",
        },
    )
    assert response.status_code == 200, response.text

    async with session_factory() as session:
        from sqlalchemy import select

        account = (
            await session.execute(select(ClientAccount).where(ClientAccount.phone == phone))
        ).scalar_one()
        assert account.source_organization_id == organization


async def test_existing_attribution_cannot_be_changed(
    ca_client, session_factory, organization
):
    async with session_factory() as session:
        from app.modules.organizations.models import Organization
        from app.shared.enums import LegalForm, OrganizationStatus, TaxSystem

        other = Organization(
            name="Другой сервис",
            inn="9876543210",
            tax_system=TaxSystem.USN,
            legal_form=LegalForm.OOO,
            legal_address="г. Москва",
            phone="+70000000001",
            status=OrganizationStatus.ACTIVE,
        )
        session.add(other)
        await session.flush()
        session.add_all(
            [
                OrganizationReferral(
                    organization_id=organization,
                    code="ReferralCode0002",
                ),
                OrganizationReferral(
                    organization_id=other.id,
                    code="ReferralCode0003",
                ),
                ClientAccount(
                    phone="+79990002222",
                    source_organization_id=organization,
                ),
            ]
        )
        await session.commit()

    code = await _request_and_get_code(ca_client, "+79990002222")
    response = await ca_client.post(
        f"{API}/client-auth/otp/verify",
        json={
            "phone": "+79990002222",
            "code": code,
            "referral_code": "ReferralCode0003",
        },
    )
    assert response.status_code == 200, response.text

    async with session_factory() as session:
        from sqlalchemy import select

        account = (
            await session.execute(
                select(ClientAccount).where(ClientAccount.phone == "+79990002222")
            )
        ).scalar_one()
        assert account.source_organization_id == organization


async def test_invalid_referral_rejected_for_unattributed_client(ca_client):
    phone = "+79990002233"
    code = await _request_and_get_code(ca_client, phone)
    response = await ca_client.post(
        f"{API}/client-auth/otp/verify",
        json={
            "phone": phone,
            "code": code,
            "referral_code": "InvalidCode00000",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Недействительный реферальный код"

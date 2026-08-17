"""Тесты безопасности: аутентификация, RBAC, валидация, склад, rate-limit."""

from app.core.config import settings
from app.core.security import hash_password
from app.modules.users.models import User
from app.shared.enums import UserRole
from tests.conftest import API


async def _create_user(session_factory, email, password, role, organization_id):
    async with session_factory() as session:
        session.add(
            User(
                organization_id=organization_id,
                email=email,
                full_name=email,
                role=role,
                hashed_password=hash_password(password),
            )
        )
        await session.commit()


async def _auth_header(client, email, password):
    resp = await client.post(f"{API}/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def test_unauthenticated_requests_blocked(client):
    protected = [
        "/orders",
        "/clients",
        "/inventory",
        "/users",
        "/mechanics",
        "/services",
        "/vehicles",
        "/schedule/week?day=2026-06-14",
    ]
    for path in protected:
        resp = await client.get(f"{API}{path}")
        assert resp.status_code == 401, f"{path} → {resp.status_code}"


async def test_invalid_token_rejected(client):
    resp = await client.get(f"{API}/auth/me", headers={"Authorization": "Bearer not.a.valid.token"})
    assert resp.status_code == 401


async def test_manager_cannot_manage_users(client, session_factory, organization):
    await _create_user(
        session_factory, "manager@komit.ru", "manager-pass-1", UserRole.MANAGER, organization
    )
    headers = await _auth_header(client, "manager@komit.ru", "manager-pass-1")
    resp = await client.get(f"{API}/users", headers=headers)
    assert resp.status_code == 403


async def test_mechanic_cannot_access_clients(client, session_factory, organization):
    await _create_user(
        session_factory, "mech@komit.ru", "mech-pass-12", UserRole.MECHANIC, organization
    )
    headers = await _auth_header(client, "mech@komit.ru", "mech-pass-12")
    resp = await client.get(f"{API}/clients", headers=headers)
    assert resp.status_code == 403


async def test_extra_fields_rejected(auth_client):
    # Попытка задать защищённое поле balance через создание клиента → отклонено
    resp = await auth_client.post(
        f"{API}/clients",
        json={"full_name": "X", "phone": "+70000009001", "balance": 999999},
    )
    assert resp.status_code == 422


async def test_email_normalized_to_lowercase(auth_client, session_factory):
    created = await auth_client.post(
        f"{API}/users",
        json={
            "email": "Mixed.Case@Komit.RU",
            "full_name": "Сотрудник",
            "password": "valid-pass-1",
            "role": "manager",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["email"] == "mixed.case@komit.ru"


async def test_inventory_no_negative_stock(auth_client):
    item = (
        await auth_client.post(
            f"{API}/inventory",
            json={
                "sku": "OIL-1",
                "name": "Масло 5W30",
                "category": "oils",
                "quantity": 5,
                "min_quantity": 2,
                "sale_price": 1000,
            },
        )
    ).json()

    # Списать больше, чем есть, — запрещено
    over = await auth_client.post(f"{API}/inventory/{item['id']}/write-off", json={"quantity": 10})
    assert over.status_code == 422

    # Списать в пределах остатка — остаток уменьшается
    ok = await auth_client.post(f"{API}/inventory/{item['id']}/write-off", json={"quantity": 3})
    assert ok.status_code == 200
    assert float(ok.json()["quantity"]) == 2.0


async def test_login_rate_limit(client):
    statuses = []
    for _ in range(settings.LOGIN_RATE_LIMIT_ATTEMPTS + 3):
        resp = await client.post(
            f"{API}/auth/login",
            data={"username": "victim@komit.ru", "password": "wrong-guess"},
        )
        statuses.append(resp.status_code)
    assert statuses[0] == 401  # первые попытки доходят до проверки пароля
    assert 429 in statuses  # после лимита — блокировка

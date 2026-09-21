"""Creator-console API tests."""

from decimal import Decimal


async def test_platform_bootstrap_is_backend_backed(auth_client):
    response = await auth_client.get("/api/v1/platform-admin/bootstrap")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["services"]
    assert {item["key"] for item in payload["plans"]} == {"standard", "pro", "premium"}
    assert payload["dashboard"]["services"] == len(payload["services"])


async def test_platform_state_is_persisted(auth_client):
    response = await auth_client.put(
        "/api/v1/platform-admin/state",
        json={
            "plans": [
                {
                    "key": "starter",
                    "name": "Старт",
                    "price": "1000",
                    "description": "Тестовый тариф",
                    "features": ["CRM"],
                    "featured": False,
                }
            ],
            "settings": {"platform": "Локальный ДВИЖОК", "domain": "localhost"},
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["plans"][0]["name"] == "Старт"
    assert payload["settings"]["domain"] == "localhost"
    assert Decimal(str(payload["plans"][0]["price"])) == Decimal("1000")


async def test_platform_service_creation_creates_usable_owner(auth_client, session_factory):
    response = await auth_client.post(
        "/api/v1/platform-admin/services",
        json={
            "name": "Новый тестовый сервис",
            "city": "Уфа",
            "email": "office@example.com",
            "plan": "Стандарт",
            "phone": "+7 900 123-45-67",
            "owner_name": "Тестовый Владелец",
            "owner_email": "owner@example.com",
            "owner_login": "testowner11",
            "owner_password": "secure123",
        },
    )
    assert response.status_code == 201, response.text
    assert any(item["name"] == "Новый тестовый сервис" for item in response.json()["services"])

    from app.core.security import verify_password
    from app.modules.users.models import User

    async with session_factory() as session:
        owner = await session.get(User, 2)
        assert owner is not None
        assert owner.email == "owner@example.com"
        assert owner.login == "testowner11"
        assert owner.normalized_phone == "+79001234567"
        assert owner.is_owner is True
        assert verify_password("secure123", owner.hashed_password)


async def test_platform_console_requires_owner(client, session_factory, organization):
    from app.core.security import hash_password
    from app.modules.users.models import User
    from app.shared.enums import UserRole

    async with session_factory() as session:
        session.add(
            User(
                organization_id=organization,
                email="manager@komit.ru",
                full_name="Менеджер",
                role=UserRole.MANAGER,
                hashed_password=hash_password("manager123"),
            )
        )
        await session.commit()
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "manager@komit.ru", "password": "manager123"},
    )
    assert login.status_code == 200, login.text
    client.headers.update({"Authorization": f"Bearer {login.json()['access_token']}"})
    response = await client.get("/api/v1/platform-admin/bootstrap")
    assert response.status_code == 403, response.text

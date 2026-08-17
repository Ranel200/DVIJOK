"""Тесты модуля organizations: регистрация тенанта и изоляция данных между ними."""

from sqlalchemy import select

from app.modules.services.models import Service
from tests.conftest import API


def _register_payload(suffix: str) -> dict:
    return {
        "name": f"Автосервис {suffix}",
        "inn": f"123456789{suffix}",
        "tax_system": "usn",
        "legal_form": "ooo",
        "legal_address": "г. Москва",
        "phone": f"+7000000000{suffix}",
        "admin_full_name": "Администратор",
        "admin_email": f"admin-{suffix}@org.ru",
        "admin_password": "admin12345",
    }


async def test_register_creates_organization_and_admin(client, session_factory):
    resp = await client.post(f"{API}/organizations/register", json=_register_payload("1"))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "access_token" in body and "refresh_token" in body

    headers = {"Authorization": f"Bearer {body['access_token']}"}
    me = await client.get(f"{API}/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "admin"

    org = await client.get(f"{API}/organizations/me", headers=headers)
    assert org.status_code == 200
    assert org.json()["inn"] == "1234567891"

    async with session_factory() as session:
        public_services = list(
            (await session.execute(select(Service).where(Service.public_booking_key.is_not(None))))
            .scalars()
            .all()
        )
    assert {
        item.public_booking_key: (item.name, str(item.base_price)) for item in public_services
    } == {
        "diagnostics": ("Диагностика", "0.00"),
        "repair": ("Ремонт", "0.00"),
    }


async def test_register_duplicate_inn_rejected(client):
    payload = _register_payload("2")
    first = await client.post(f"{API}/organizations/register", json=payload)
    assert first.status_code == 201

    dup = dict(payload)
    dup["admin_email"] = "other@org.ru"
    second = await client.post(f"{API}/organizations/register", json=dup)
    assert second.status_code == 409


async def test_tenant_data_is_isolated(client):
    org_a = (await client.post(f"{API}/organizations/register", json=_register_payload("3"))).json()
    org_b = (await client.post(f"{API}/organizations/register", json=_register_payload("4"))).json()
    headers_a = {"Authorization": f"Bearer {org_a['access_token']}"}
    headers_b = {"Authorization": f"Bearer {org_b['access_token']}"}

    created = await client.post(
        f"{API}/clients",
        json={"full_name": "Клиент A", "phone": "+79990000000"},
        headers=headers_a,
    )
    assert created.status_code == 201
    client_id = created.json()["id"]

    # Виден владельцу-тенанту.
    own = await client.get(f"{API}/clients/{client_id}", headers=headers_a)
    assert own.status_code == 200

    # Не виден другому тенанту — 404, не 200 с чужими данными.
    foreign = await client.get(f"{API}/clients/{client_id}", headers=headers_b)
    assert foreign.status_code == 404

    # Список клиентов другого тенанта пуст.
    listing = await client.get(f"{API}/clients", headers=headers_b)
    assert listing.json()["total"] == 0

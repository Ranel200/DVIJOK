"""Тесты модуля clients и аутентификации."""

from tests.conftest import API


async def test_login_and_me(auth_client):
    resp = await auth_client.get(f"{API}/auth/me")
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


async def test_clients_require_auth(client):
    resp = await client.get(f"{API}/clients")
    assert resp.status_code == 401


async def test_client_crud_and_detail(auth_client):
    # Создание
    created = await auth_client.post(
        f"{API}/clients", json={"full_name": "Иван Петров", "phone": "+79990001122"}
    )
    assert created.status_code == 201, created.text
    client_id = created.json()["id"]

    # Дубликат телефона → 409
    dup = await auth_client.post(
        f"{API}/clients", json={"full_name": "Пётр", "phone": "+79990001122"}
    )
    assert dup.status_code == 409

    # Карточка: статистика и список авто
    detail = await auth_client.get(f"{API}/clients/{client_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["stats"]["visits_count"] == 0
    assert body["vehicles"] == []

    # Добавление автомобиля
    vehicle = await auth_client.post(
        f"{API}/vehicles",
        json={"client_id": client_id, "make": "BMW", "model": "X5", "year": 2020},
    )
    assert vehicle.status_code == 201, vehicle.text

    detail2 = await auth_client.get(f"{API}/clients/{client_id}")
    assert len(detail2.json()["vehicles"]) == 1

    # Список с пагинацией
    listing = await auth_client.get(f"{API}/clients")
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    # Поиск по марке авто
    search = await auth_client.get(f"{API}/clients", params={"query": "BMW"})
    assert search.json()["total"] == 1

    # Обновление типа клиента
    upd = await auth_client.patch(f"{API}/clients/{client_id}", json={"client_type": "vip"})
    assert upd.status_code == 200
    assert upd.json()["client_type"] == "vip"

    # Удаление
    deleted = await auth_client.delete(f"{API}/clients/{client_id}")
    assert deleted.status_code == 204

    missing = await auth_client.get(f"{API}/clients/{client_id}")
    assert missing.status_code == 404

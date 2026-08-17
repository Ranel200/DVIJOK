"""Расширенный каталог услуг административного приложения."""

from tests.conftest import API


async def test_service_price_range_mechanics_and_summary(auth_client):
    mechanic = await auth_client.post(
        f"{API}/mechanics",
        json={"full_name": "Мастер услуги"},
    )
    assert mechanic.status_code == 201, mechanic.text
    mechanic_id = mechanic.json()["id"]

    created = await auth_client.post(
        f"{API}/services",
        json={
            "name": "Кузовной ремонт",
            "category": "body",
            "description": "Ремонт элемента",
            "base_price": 5000,
            "price_type": "range",
            "price_to": 15000,
            "internal_notes": "Согласовать после осмотра",
            "mechanic_ids": [mechanic_id],
            "duration_minutes": 180,
        },
    )
    assert created.status_code == 201, created.text
    service = created.json()
    assert service["price_type"] == "range"
    assert float(service["price_to"]) == 15000
    assert service["mechanic_ids"] == [mechanic_id]
    assert service["internal_notes"] == "Согласовать после осмотра"

    listing = await auth_client.get(f"{API}/services")
    assert listing.status_code == 200
    item = next(row for row in listing.json()["items"] if row["id"] == service["id"])
    assert item["mechanic_ids"] == [mechanic_id]

    summary = await auth_client.get(f"{API}/services/summary")
    assert summary.status_code == 200, summary.text
    assert summary.json()["totalServices"] >= 1
    assert summary.json()["activeMasters"] >= 1


async def test_service_range_and_foreign_mechanic_validation(auth_client):
    invalid_range = await auth_client.post(
        f"{API}/services",
        json={
            "name": "Неверный диапазон",
            "category": "other",
            "base_price": 5000,
            "price_type": "range",
            "price_to": 1000,
        },
    )
    assert invalid_range.status_code == 422

    missing_mechanic = await auth_client.post(
        f"{API}/services",
        json={
            "name": "Чужой мастер",
            "category": "other",
            "mechanic_ids": [999999],
        },
    )
    assert missing_mechanic.status_code == 404

"""Плоский контракт каталога услуг для готового admin frontend."""

from tests.conftest import API


async def test_admin_service_facade_crud(auth_client):
    employee_response = await auth_client.post(
        f"{API}/employees",
        json={
            "email": "service-master@example.com",
            "password": "master-password",
            "full_name": "Смирнов Алексей",
            "role": "mechanic",
        },
    )
    assert employee_response.status_code == 201, employee_response.text
    employee = employee_response.json()

    masters_response = await auth_client.get(f"{API}/services/masters")
    assert masters_response.status_code == 200, masters_response.text
    assert masters_response.json() == [
        {"id": employee["id"], "name": "Смирнов Алексей", "role": "Мастер"}
    ]

    payload = {
        "title": "Замена масла",
        "description": "Масло и фильтр",
        "category": "maintenance",
        "priceType": "fixed",
        "price": 3500,
        "duration": 1,
        "durationUnit": "hours",
        "status": "active",
        "masters": [employee["id"]],
        "notes": "Проверить пробег",
    }
    created_response = await auth_client.post(f"{API}/services/admin", json=payload)
    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    assert created["title"] == "Замена масла"
    assert created["durationHours"] == "1"
    assert created["master"]["id"] == employee["id"]
    assert created["ordersCount"] == 0

    listing = await auth_client.get(f"{API}/services/admin")
    assert listing.status_code == 200, listing.text
    assert isinstance(listing.json(), list)
    assert listing.json()[0]["title"] == "Замена масла"

    payload.update(
        {
            "priceType": "range",
            "price": 4000,
            "priceTo": 5500,
            "category": "repair",
            "duration": 90,
            "durationUnit": "minutes",
            "status": "hidden",
        }
    )
    updated_response = await auth_client.put(f"{API}/services/admin/{created['id']}", json=payload)
    assert updated_response.status_code == 200, updated_response.text
    updated = updated_response.json()
    assert updated["priceType"] == "range"
    assert updated["priceTo"] == "5500.00"
    assert updated["category"] == "repair"
    assert updated["status"] == "hidden"
    assert updated["durationHours"] == "1.5"

    deleted = await auth_client.delete(f"{API}/services/admin/{created['id']}")
    assert deleted.status_code == 204

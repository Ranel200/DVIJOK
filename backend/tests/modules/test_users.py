"""Профили сотрудников административного приложения."""

from tests.conftest import API


async def test_staff_profile_fields_round_trip(auth_client):
    created = await auth_client.post(
        f"{API}/users",
        json={
            "email": "manager-profile@example.com",
            "full_name": "Менеджер Профиль",
            "phone": "+79990001122",
            "role": "manager",
            "password": "strong-pass-123",
            "calendar_color": "#0abcca",
            "duties": "Приём клиентов",
            "ui_permissions": {"schedule": True, "crm": True, "settings": False},
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["calendar_color"] == "#0ABCCA"
    assert body["duties"] == "Приём клиентов"
    assert body["ui_permissions"]["crm"] is True

    updated = await auth_client.patch(
        f"{API}/users/{body['id']}",
        json={"calendar_color": "#ff6f53", "duties": "Старший менеджер"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["calendar_color"] == "#FF6F53"
    assert updated.json()["duties"] == "Старший менеджер"


async def test_staff_color_validation(auth_client):
    response = await auth_client.post(
        f"{API}/users",
        json={
            "email": "invalid-color@example.com",
            "full_name": "Некорректный Цвет",
            "password": "strong-pass-123",
            "calendar_color": "red",
        },
    )
    assert response.status_code == 422


async def test_employee_card_orchestrates_user_and_mechanic(auth_client):
    created = await auth_client.post(
        f"{API}/employees",
        json={
            "email": "mechanic-card@example.com",
            "full_name": "Мастер Карточка",
            "phone": "+79995556677",
            "role": "mechanic",
            "password": "strong-pass-123",
            "calendar_color": "#43A047",
            "duties": "Диагностика и ремонт",
            "ui_permissions": {"schedule": True, "crm": True},
            "specializations": ["diagnostics", "electrical"],
            "hired_year": 2024,
            "hourly_rate": 1200,
            "commission_percent": 15,
        },
    )
    assert created.status_code == 201, created.text
    employee = created.json()
    assert employee["mechanic_id"] is not None
    assert employee["specializations"] == ["diagnostics", "electrical"]
    assert float(employee["hourly_rate"]) == 1200

    updated = await auth_client.patch(
        f"{API}/employees/{employee['id']}",
        json={"full_name": "Мастер Обновлён", "commission_percent": 20},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["full_name"] == "Мастер Обновлён"
    assert float(updated.json()["commission_percent"]) == 20

    listing = await auth_client.get(f"{API}/employees")
    assert listing.status_code == 200
    assert any(item["id"] == employee["id"] for item in listing.json())

    disabled = await auth_client.delete(f"{API}/employees/{employee['id']}")
    assert disabled.status_code == 204
    fetched = await auth_client.get(f"{API}/employees/{employee['id']}")
    assert fetched.json()["is_active"] is False


async def test_frontend_feature_permissions_are_enforced_by_backend(auth_client):
    created = await auth_client.post(
        f"{API}/users",
        json={
            "email": "limited-manager@example.com",
            "login": "limited.manager",
            "full_name": "Ограниченный менеджер",
            "role": "manager",
            "staff_role_key": "junior_admin",
            "password": "123456",
            "ui_permissions": {
                "schedule": True,
                "crm": False,
                "services": False,
                "tasks": False,
                "qr": False,
                "settings": False,
            },
        },
    )
    assert created.status_code == 201, created.text
    login = await auth_client.post(
        f"{API}/auth/login",
        json={"email": "limited.manager", "password": "123456"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["isOwner"] is False
    assert login.json()["user"]["subscriptionPlan"] == "pro"
    auth_client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"

    schedule = await auth_client.get(f"{API}/schedule/employees")
    assert schedule.status_code == 200, schedule.text
    tasks = await auth_client.get(f"{API}/tasks")
    assert tasks.status_code == 403, tasks.text
    assert tasks.json()["message"] == "Доступ к разделу закрыт владельцем"

    subscription = await auth_client.post(
        f"{API}/auth/subscription",
        json={"plan": "premium"},
    )
    assert subscription.status_code == 403, subscription.text


async def test_employee_document_binary_round_trip(auth_client):
    created = await auth_client.post(
        f"{API}/employees",
        json={
            "email": "documented-employee@example.com",
            "full_name": "Сотрудник с документами",
            "role": "manager",
            "password": "123456",
        },
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]

    uploaded = await auth_client.post(
        f"{API}/employees/{user_id}/documents/passport",
        files={"file": ("passport.pdf", b"%PDF-1.4\nprivate", "application/pdf")},
    )
    assert uploaded.status_code == 200, uploaded.text
    document = uploaded.json()
    assert document["kind"] == "passport"
    assert document["fileName"] == "passport.pdf"

    listing = await auth_client.get(f"{API}/employees/{user_id}/documents")
    assert listing.status_code == 200, listing.text
    assert listing.json() == [document]

    content = await auth_client.get(document["downloadUrl"])
    assert content.status_code == 200, content.text
    assert content.content == b"%PDF-1.4\nprivate"

    deleted = await auth_client.delete(
        f"{API}/employees/{user_id}/documents/{document['id']}"
    )
    assert deleted.status_code == 204, deleted.text
    assert (await auth_client.get(f"{API}/employees/{user_id}/documents")).json() == []

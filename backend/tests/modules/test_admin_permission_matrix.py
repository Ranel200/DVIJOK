"""Role and feature-grant matrix used by the administrative frontend."""

from tests.conftest import API


async def _create_staff(auth_client, *, login: str, role: str, role_key: str):
    response = await auth_client.post(
        f"{API}/users",
        json={
            "email": f"{login}@example.com",
            "login": login,
            "full_name": login.replace(".", " ").title(),
            "role": role,
            "staff_role_key": role_key,
            "password": "123456",
            "ui_permissions": {
                "schedule": True,
                "crm": True,
                "services": True,
                "tasks": True,
                "qr": True,
                "settings": True,
            },
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _headers(client, login: str) -> dict[str, str]:
    response = await client.post(
        f"{API}/auth/login",
        json={"email": login, "password": "123456"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_admin_frontend_permission_matrix(auth_client, client):
    senior = await _create_staff(
        auth_client,
        login="matrix.senior",
        role="admin",
        role_key="senior_admin",
    )
    await _create_staff(
        auth_client,
        login="matrix.junior",
        role="manager",
        role_key="junior_admin",
    )
    master = await _create_staff(
        auth_client,
        login="matrix.master",
        role="mechanic",
        role_key="senior_master",
    )

    task = await auth_client.post(
        f"{API}/tasks",
        json={
            "title": "Проверить матрицу прав",
            "employee": {
                "id": master["id"],
                "name": master["full_name"],
                "role": "Мастер",
            },
        },
    )
    assert task.status_code == 201, task.text

    owner_schedule = await auth_client.get(f"{API}/schedule/employees")
    assert owner_schedule.status_code == 200, owner_schedule.text
    assert any(row["role"] == "Владелец" for row in owner_schedule.json())

    master_headers = await _headers(client, "matrix.master")
    assert (
        await client.get(f"{API}/schedule/employees", headers=master_headers)
    ).status_code == 200
    assert (
        await client.get(
            f"{API}/schedule/employees/{senior['id']}", headers=master_headers
        )
    ).status_code == 403
    assert (
        await client.get(f"{API}/services/admin", headers=master_headers)
    ).status_code == 200
    assert (
        await client.post(
            f"{API}/services/admin",
            headers=master_headers,
            json={"title": "Запрещённая услуга", "category": "repair"},
        )
    ).status_code == 403
    assert (await client.get(f"{API}/tasks", headers=master_headers)).status_code == 200
    changed = await client.patch(
        f"{API}/tasks/{task.json()['id']}/status",
        headers=master_headers,
        json={"status": "done"},
    )
    assert changed.status_code == 200, changed.text
    assert (
        await client.post(
            f"{API}/tasks",
            headers=master_headers,
            json={
                "title": "Запрещённая задача",
                "employee": {"id": "all", "name": "Все сотрудники", "role": ""},
            },
        )
    ).status_code == 403
    assert (
        await client.get(f"{API}/crm/services", headers=master_headers)
    ).status_code == 200
    assert (
        await client.get(f"{API}/crm/employees", headers=master_headers)
    ).status_code == 200
    assert (
        await client.post(f"{API}/crm/orders", headers=master_headers, json={})
    ).status_code == 201
    assert (
        await client.get(f"{API}/referrals/me", headers=master_headers)
    ).status_code == 403
    assert (await client.get(f"{API}/settings", headers=master_headers)).status_code == 403

    junior_headers = await _headers(client, "matrix.junior")
    assert (
        await client.get(f"{API}/services/admin", headers=junior_headers)
    ).status_code == 200
    assert (
        await client.post(f"{API}/referrals/me", headers=junior_headers)
    ).status_code in {200, 201}
    assert (await client.get(f"{API}/settings", headers=junior_headers)).status_code == 403
    denied_schedule_change = await client.put(
        f"{API}/schedule/settings",
        headers=junior_headers,
        json={
            "start": "09:00",
            "end": "18:00",
            "workDays": [1, 2, 3, 4, 5],
            "employeeId": senior["id"],
        },
    )
    assert denied_schedule_change.status_code == 403

    senior_headers = await _headers(client, "matrix.senior")
    allowed_schedule_change = await client.put(
        f"{API}/schedule/settings",
        headers=senior_headers,
        json={
            "start": "09:00",
            "end": "18:00",
            "workDays": [1, 2, 3, 4, 5],
            "employeeId": senior["id"],
        },
    )
    assert allowed_schedule_change.status_code == 204, allowed_schedule_change.text
    assert (await client.get(f"{API}/settings", headers=senior_headers)).status_code == 403

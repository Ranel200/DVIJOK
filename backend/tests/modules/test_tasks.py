"""Задачи сотрудников и сводные показатели админки."""

import datetime as dt

from tests.conftest import API


async def _employee(auth_client):
    response = await auth_client.get(f"{API}/tasks/employees")
    assert response.status_code == 200, response.text
    return response.json()[0]


async def test_tasks_frontend_contract_and_summary(auth_client):
    employee = await _employee(auth_client)
    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)

    today_task_response = await auth_client.post(
        f"{API}/tasks",
        json={
            "title": "Позвонить клиенту",
            "description": "Согласовать детали",
            "deadline": today.isoformat(),
            "status": "new",
            "employee": employee,
        },
    )
    assert today_task_response.status_code == 201, today_task_response.text
    today_task = today_task_response.json()
    assert today_task["employee"]["id"] == employee["id"]
    assert today_task["createdAt"]

    overdue_response = await auth_client.post(
        f"{API}/tasks",
        json={
            "title": "Заказать запчасть",
            "description": "",
            "deadline": yesterday.isoformat(),
            "status": "hot",
            "employee": {"id": "all", "name": "Все сотрудники", "role": ""},
        },
    )
    assert overdue_response.status_code == 201, overdue_response.text
    overdue = overdue_response.json()
    assert overdue["employee"]["id"] == "all"

    done_response = await auth_client.post(
        f"{API}/tasks",
        json={
            "title": "Готовая задача",
            "description": "",
            "deadline": today.isoformat(),
            "status": "done",
            "employee": employee,
        },
    )
    assert done_response.status_code == 201, done_response.text

    listing = await auth_client.get(f"{API}/tasks")
    assert listing.status_code == 200
    assert len(listing.json()) == 3

    summary_response = await auth_client.get(f"{API}/tasks/summary")
    assert summary_response.status_code == 200, summary_response.text
    summary = summary_response.json()
    assert summary == {
        "today": {"count": 1, "overdue": 1},
        "planned": 2,
        "donePerWeek": 1,
    }

    completed = await auth_client.patch(
        f"{API}/tasks/{today_task['id']}/status", json={"status": "done"}
    )
    assert completed.status_code == 200, completed.text
    assert completed.json()["status"] == "done"

    deleted = await auth_client.request(
        "DELETE",
        f"{API}/tasks/bulk",
        json={"ids": [overdue["id"], done_response.json()["id"]]},
    )
    assert deleted.status_code == 204
    remaining = await auth_client.get(f"{API}/tasks")
    assert [task["id"] for task in remaining.json()] == [today_task["id"]]


async def test_task_rejects_foreign_employee(auth_client):
    response = await auth_client.post(
        f"{API}/tasks",
        json={
            "title": "Чужая задача",
            "employee": {"id": 999999, "name": "Нет", "role": ""},
        },
    )
    assert response.status_code == 404


async def test_staff_sees_and_changes_only_own_tasks(auth_client, client):
    async def create_staff(login: str):
        response = await auth_client.post(
            f"{API}/users",
            json={
                "email": f"{login}@example.com",
                "login": login,
                "full_name": login.title(),
                "role": "manager",
                "staff_role_key": "junior_admin",
                "password": "123456",
                "ui_permissions": {"tasks": True},
            },
        )
        assert response.status_code == 201, response.text
        return response.json()

    async def staff_headers(login: str) -> dict[str, str]:
        response = await client.post(
            f"{API}/auth/login",
            json={"email": login, "password": "123456"},
        )
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    first = await create_staff("task.first")
    second = await create_staff("task.second")

    async def create_task(title: str, employee: dict):
        response = await auth_client.post(
            f"{API}/tasks",
            json={"title": title, "employee": employee},
        )
        assert response.status_code == 201, response.text
        return response.json()

    first_task = await create_task(
        "Задача первого",
        {"id": first["id"], "name": first["full_name"], "role": "Администратор"},
    )
    second_task = await create_task(
        "Задача второго",
        {"id": second["id"], "name": second["full_name"], "role": "Администратор"},
    )
    unassigned = await create_task(
        "Общая задача",
        {"id": "all", "name": "Все сотрудники", "role": ""},
    )

    first_headers = await staff_headers("task.first")
    first_listing = await client.get(f"{API}/tasks", headers=first_headers)
    assert first_listing.status_code == 200, first_listing.text
    assert [task["id"] for task in first_listing.json()] == [first_task["id"]]

    first_summary = await client.get(f"{API}/tasks/summary", headers=first_headers)
    assert first_summary.status_code == 200, first_summary.text
    assert first_summary.json()["planned"] == 1

    own_update = await client.patch(
        f"{API}/tasks/{first_task['id']}/status",
        headers=first_headers,
        json={"status": "done"},
    )
    assert own_update.status_code == 200, own_update.text

    for hidden_task in (second_task, unassigned):
        hidden_update = await client.patch(
            f"{API}/tasks/{hidden_task['id']}/status",
            headers=first_headers,
            json={"status": "done"},
        )
        assert hidden_update.status_code == 404, hidden_update.text

    owner_listing = await auth_client.get(f"{API}/tasks")
    assert owner_listing.status_code == 200, owner_listing.text
    assert {task["id"] for task in owner_listing.json()} == {
        first_task["id"],
        second_task["id"],
        unassigned["id"],
    }

"""Совместимый staff/schedule-контракт административной панели."""

import datetime as dt

from tests.conftest import API


def _staff_payload():
    return {
        "role": "senior_master",
        "name": "Петров Иван Сергеевич",
        "phone": "+79990001122",
        "email": "schedule-master@example.com",
        "duties": "Ремонт",
        "rate": 1200,
        "color": "#43A047",
        "documents": {
            "passport": {"name": "passport.pdf", "fileName": "passport.pdf"},
            "inn": None,
            "medicalBook": None,
        },
        "access": {
            "schedule": True,
            "crm": True,
            "services": True,
            "tasks": True,
            "qr": False,
            "settings": False,
        },
        "login": "schedule-master@example.com",
        "password": "master-password",
    }


async def test_schedule_staff_facade_and_recurring_break(auth_client):
    created_response = await auth_client.post(f"{API}/schedule/employees", json=_staff_payload())
    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    assert created["name"] == "Петров Иван Сергеевич"
    assert created["roleKey"] == "senior_master"
    assert created["password"] == ""
    assert created["documents"]["passport"]["fileName"] == "passport.pdf"

    settings_response = await auth_client.put(
        f"{API}/schedule/settings",
        json={
            "type": "workdays",
            "start": "09:00",
            "end": "18:00",
            "breaks": [{"start": "12:00", "end": "13:00"}],
            "workDays": [1],
            "employeeId": created["id"],
        },
    )
    assert settings_response.status_code == 204, settings_response.text

    today = dt.date.today()
    next_monday = today + dt.timedelta(days=(7 - today.weekday()) % 7 or 7)
    month_response = await auth_client.get(
        f"{API}/schedule/employees",
        params={"year": next_monday.year, "month": next_monday.month - 1},
    )
    assert month_response.status_code == 200, month_response.text
    row = next(item for item in month_response.json() if item["id"] == created["id"])
    shift = row["days"][next_monday.day - 1]
    assert shift == {
        "day": next_monday.day,
        "active": True,
        "start": "09:00",
        "end": "18:00",
    }

    employee = await auth_client.get(f"{API}/employees/{created['id']}")
    assert employee.status_code == 200
    mechanic_id = employee.json()["mechanic_id"]
    availability = await auth_client.get(
        f"{API}/schedule/availability",
        params={
            "date_from": next_monday.isoformat(),
            "date_to": next_monday.isoformat(),
            "mechanic_id": mechanic_id,
            "duration_minutes": 60,
        },
    )
    assert availability.status_code == 200, availability.text
    local_starts = [slot["start_time"][11:16] for slot in availability.json()["slots"]]
    assert "12:00" not in local_starts

    deleted = await auth_client.delete(f"{API}/schedule/employees/{created['id']}")
    assert deleted.status_code == 204


async def test_staff_frontend_position_login_phone_and_rate_round_trip(auth_client):
    payload = _staff_payload()
    payload.update(
        {
            "role": "junior_master",
            "email": "junior-master@example.com",
            "phone": "8 (999) 555-66-70",
            "login": "junior.master",
            "password": "123456",
            "rate": 30000,
        }
    )
    response = await auth_client.post(f"{API}/schedule/employees", json=payload)
    assert response.status_code == 201, response.text
    employee = response.json()
    assert employee["roleKey"] == "junior_master"
    assert employee["role"] == "Младший мастер"
    assert employee["login"] == "junior.master"
    assert float(employee["rate"]) == 30000

    login = await auth_client.post(
        f"{API}/auth/login",
        json={"email": "junior.master", "password": "123456"},
    )
    assert login.status_code == 200, login.text

    phone_login = await auth_client.post(
        f"{API}/auth/login",
        json={"email": "+7 999 555-66-70", "password": "123456"},
    )
    assert phone_login.status_code == 200, phone_login.text


async def test_staff_can_be_created_without_optional_email(auth_client):
    response = await auth_client.post(
        f"{API}/schedule/employees",
        json={
            "role": "junior_admin",
            "name": "Сотрудник без почты",
            "phone": "+79990003001",
            "login": "staff.without.email",
            "password": "123456",
            "access": {
                "schedule": True,
                "crm": False,
                "services": False,
                "tasks": False,
                "qr": False,
                "settings": False,
            },
        },
    )
    assert response.status_code == 201, response.text
    employee = response.json()
    assert employee["name"] == "Сотрудник без почты"
    assert employee["email"] == ""
    assert employee["phone"] == "+79990003001"
    assert employee["login"] == "staff.without.email"
    assert employee["access"]["schedule"] is True
    assert employee["access"]["crm"] is False

    login = await auth_client.post(
        f"{API}/auth/login",
        json={"email": "staff.without.email", "password": "123456"},
    )
    assert login.status_code == 200, login.text
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    schedule = await auth_client.get(f"{API}/schedule/employees", headers=headers)
    assert schedule.status_code == 200, schedule.text
    crm = await auth_client.get(f"{API}/crm/deals", headers=headers)
    assert crm.status_code == 403, crm.text


async def test_multiple_staff_can_be_created_without_email(auth_client):
    for index, suffix in enumerate(("one", "two"), start=1):
        response = await auth_client.post(
            f"{API}/schedule/employees",
            json={
                "role": "junior_master",
                "name": f"Минимальный сотрудник {index}",
                "phone": f"+7999000310{index}",
                "login": f"minimal.{suffix}",
                "password": "123456",
                "access": {"schedule": True},
            },
        )
        assert response.status_code == 201, response.text


async def test_required_fields_for_new_staff(auth_client):
    base_payload = {
        "role": "junior_master",
        "name": "Обязательный сотрудник",
        "phone": "+79990003201",
        "login": "required.staff",
        "password": "123456",
        "access": {"schedule": True},
    }
    cases = [
        ({"name": ""}, "Напишите ФИО сотрудника"),
        ({"phone": ""}, "Введите номер телефона сотрудника"),
        ({"login": ""}, "Придумайте логин сотрудника"),
        ({"password": ""}, "Придумайте пароль сотрудника"),
        ({"access": {}}, "Выберите разделы, к которым сотрудник получит доступ"),
    ]
    for override, message in cases:
        response = await auth_client.post(
            f"{API}/schedule/employees",
            json={**base_payload, **override},
        )
        assert response.status_code == 422, response.text
        assert response.json()["detail"] == message

    short_login = await auth_client.post(
        f"{API}/schedule/employees",
        json={**base_payload, "login": "ab"},
    )
    assert short_login.status_code == 422, short_login.text

    short_password = await auth_client.post(
        f"{API}/schedule/employees",
        json={**base_payload, "password": "123"},
    )
    assert short_password.status_code == 422, short_password.text


async def test_schedule_settings_persist_for_non_mechanic_employee(auth_client):
    payload = _staff_payload()
    payload.update(
        {
            "role": "junior_admin",
            "email": "scheduled-admin@example.com",
            "phone": "+79995556671",
            "login": "scheduled.admin",
        }
    )
    created = await auth_client.post(f"{API}/schedule/employees", json=payload)
    assert created.status_code == 201, created.text
    employee_id = created.json()["id"]

    settings = await auth_client.put(
        f"{API}/schedule/settings",
        json={
            "type": "workdays",
            "start": "10:00",
            "end": "17:00",
            "breaks": [{"start": "13:00", "end": "13:30"}],
            "workDays": [1],
            "employeeId": employee_id,
        },
    )
    assert settings.status_code == 204, settings.text

    today = dt.date.today()
    next_monday = today + dt.timedelta(days=(7 - today.weekday()) % 7 or 7)
    month = await auth_client.get(
        f"{API}/schedule/employees",
        params={"year": next_monday.year, "month": next_monday.month - 1},
    )
    assert month.status_code == 200, month.text
    row = next(item for item in month.json() if item["id"] == employee_id)
    assert row["days"][next_monday.day - 1] == {
        "day": next_monday.day,
        "active": True,
        "start": "10:00",
        "end": "17:00",
    }


async def test_master_sees_only_own_employee_and_schedule(auth_client, client):
    first_payload = _staff_payload()
    first_payload.update(
        {
            "name": "Первый мастер",
            "email": "schedule-isolation-first@example.com",
            "phone": "+79990002001",
            "login": "schedule.isolation.first",
        }
    )
    second_payload = _staff_payload()
    second_payload.update(
        {
            "name": "Второй мастер",
            "email": "schedule-isolation-second@example.com",
            "phone": "+79990002002",
            "login": "schedule.isolation.second",
        }
    )
    first = await auth_client.post(f"{API}/schedule/employees", json=first_payload)
    second = await auth_client.post(f"{API}/schedule/employees", json=second_payload)
    assert first.status_code == 201, first.text
    assert second.status_code == 201, second.text

    first_employee = await auth_client.get(f"{API}/employees/{first.json()['id']}")
    second_employee = await auth_client.get(f"{API}/employees/{second.json()['id']}")
    first_mechanic_id = first_employee.json()["mechanic_id"]
    second_mechanic_id = second_employee.json()["mechanic_id"]

    login = await client.post(
        f"{API}/auth/login",
        json={"email": "schedule.isolation.first", "password": "master-password"},
    )
    assert login.status_code == 200, login.text
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    today = dt.date.today()
    next_monday = today + dt.timedelta(days=(7 - today.weekday()) % 7 or 7)
    employees = await client.get(
        f"{API}/schedule/employees",
        params={"year": next_monday.year, "month": next_monday.month - 1},
        headers=headers,
    )
    assert employees.status_code == 200, employees.text
    assert [item["id"] for item in employees.json()] == [first.json()["id"]]

    calendar = await client.get(
        f"{API}/schedule/calendar",
        params={"weekStart": next_monday.isoformat()},
        headers=headers,
    )
    assert calendar.status_code == 200, calendar.text
    visible_mechanics = {
        block["employeeId"]
        for day in calendar.json()["days"]
        for blocks in day["slots"].values()
        for block in blocks
    }
    assert visible_mechanics == {first_mechanic_id}
    assert second_mechanic_id not in visible_mechanics

    own_hours = await client.get(
        f"{API}/schedule/mechanics/{first_mechanic_id}/working-hours",
        headers=headers,
    )
    assert own_hours.status_code == 200, own_hours.text

    foreign_hours = await client.get(
        f"{API}/schedule/mechanics/{second_mechanic_id}/working-hours",
        headers=headers,
    )
    assert foreign_hours.status_code == 403, foreign_hours.text

    foreign_week = await client.get(
        f"{API}/schedule/week",
        params={"day": next_monday.isoformat(), "mechanic_id": second_mechanic_id},
        headers=headers,
    )
    assert foreign_week.status_code == 403, foreign_week.text

    foreign_availability = await client.get(
        f"{API}/schedule/availability",
        params={
            "date_from": next_monday.isoformat(),
            "date_to": next_monday.isoformat(),
            "mechanic_id": second_mechanic_id,
        },
        headers=headers,
    )
    assert foreign_availability.status_code == 403, foreign_availability.text

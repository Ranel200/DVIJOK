"""Рабочие графики, предложения времени и explicit order reservation."""

import datetime as dt
from zoneinfo import ZoneInfo

from tests.conftest import API


def _future_weekday() -> dt.date:
    day = dt.datetime.now(ZoneInfo("Europe/Moscow")).date() + dt.timedelta(days=2)
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    return day


async def _create_mechanic(auth_client) -> int:
    response = await auth_client.post(
        f"{API}/mechanics",
        json={"full_name": "Мастер календаря"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_order(auth_client) -> int:
    client = await auth_client.post(
        f"{API}/clients",
        json={"full_name": "Клиент календаря", "phone": "+79991112233"},
    )
    if client.status_code == 409:
        listing = await auth_client.get(
            f"{API}/clients", params={"query": "+79991112233"}
        )
        client_id = listing.json()["items"][0]["id"]
    else:
        assert client.status_code == 201, client.text
        client_id = client.json()["id"]
    vehicle = await auth_client.post(
        f"{API}/vehicles",
        json={"client_id": client_id, "make": "Lada", "model": "Vesta"},
    )
    assert vehicle.status_code == 201, vehicle.text
    order = await auth_client.post(
        f"{API}/orders",
        json={"client_id": client_id, "vehicle_id": vehicle.json()["id"]},
    )
    assert order.status_code == 201, order.text
    assert order.json()["mechanic_id"] is None
    assert order.json()["scheduled_at"] is None
    return order.json()["id"]


async def test_working_hours_and_availability_only_suggest(auth_client):
    mechanic_id = await _create_mechanic(auth_client)
    day = _future_weekday()
    configured = await auth_client.put(
        f"{API}/schedule/mechanics/{mechanic_id}/working-hours",
        json={
            "intervals": [
                {
                    "weekday": day.weekday(),
                    "start_time": "10:00:00",
                    "end_time": "12:00:00",
                }
            ]
        },
    )
    assert configured.status_code == 200, configured.text
    assert configured.json()["uses_default"] is False

    response = await auth_client.get(
        f"{API}/schedule/availability",
        params={
            "date_from": day.isoformat(),
            "date_to": day.isoformat(),
            "mechanic_id": mechanic_id,
            "duration_minutes": 60,
        },
    )
    assert response.status_code == 200, response.text
    slots = response.json()["slots"]
    assert [slot["start_time"][11:16] for slot in slots] == ["10:00", "10:30", "11:00"]

    # Availability is read-only: the same suggestions remain until explicit reserve.
    repeated = await auth_client.get(
        f"{API}/schedule/availability",
        params={
            "date_from": day.isoformat(),
            "date_to": day.isoformat(),
            "mechanic_id": mechanic_id,
            "duration_minutes": 60,
        },
    )
    assert repeated.json()["slots"] == slots


async def test_explicit_reservation_removes_slot_and_prevents_double_booking(auth_client):
    mechanic_id = await _create_mechanic(auth_client)
    day = _future_weekday()
    await auth_client.put(
        f"{API}/schedule/mechanics/{mechanic_id}/working-hours",
        json={
            "intervals": [
                {
                    "weekday": day.weekday(),
                    "start_time": "09:00:00",
                    "end_time": "13:00:00",
                }
            ]
        },
    )
    order_a = await _create_order(auth_client)
    order_b = await _create_order(auth_client)
    selected = dt.datetime.combine(
        day,
        dt.time(10, 0),
        ZoneInfo("Europe/Moscow"),
    ).isoformat()

    reserved = await auth_client.post(
        f"{API}/orders/{order_a}/reservation",
        json={
            "mechanic_id": mechanic_id,
            "start_time": selected,
            "duration_minutes": 60,
        },
    )
    assert reserved.status_code == 201, reserved.text
    assert reserved.json()["order_id"] == order_a

    conflict = await auth_client.post(
        f"{API}/orders/{order_b}/reservation",
        json={
            "mechanic_id": mechanic_id,
            "start_time": selected,
            "duration_minutes": 60,
        },
    )
    assert conflict.status_code == 422
    assert "Пересечение" in conflict.json()["detail"]

    calendar = await auth_client.get(
        f"{API}/schedule/calendar",
        params={"weekStart": day.isoformat()},
    )
    assert calendar.status_code == 200, calendar.text
    body = calendar.json()
    assert body["timezone"] == "Europe/Moscow"
    selected_day = next(item for item in body["days"] if item["date"] == day.isoformat())
    busy = next(
        block
        for block in selected_day["slots"]["10:00"]
        if block["employeeId"] == mechanic_id
    )
    assert busy["status"] == "busy"
    assert busy["orderId"] == order_a
    assert busy["employeeName"] == "Мастер календаря"
    assert busy["brand"] == "Lada"
    assert busy["clientName"] == "Клиент календаря"
    assert busy["serviceName"] == f"Заказ {order_a}"


async def test_empty_config_means_day_off_and_outside_hours_is_rejected(auth_client):
    mechanic_id = await _create_mechanic(auth_client)
    day = _future_weekday()
    response = await auth_client.put(
        f"{API}/schedule/mechanics/{mechanic_id}/working-hours",
        json={"intervals": []},
    )
    assert response.status_code == 200
    assert response.json()["uses_default"] is False

    order_id = await _create_order(auth_client)
    selected = dt.datetime.combine(
        day,
        dt.time(10, 0),
        ZoneInfo("Europe/Moscow"),
    ).isoformat()
    reserve = await auth_client.post(
        f"{API}/orders/{order_id}/reservation",
        json={
            "mechanic_id": mechanic_id,
            "start_time": selected,
            "duration_minutes": 60,
        },
    )
    assert reserve.status_code == 422
    assert "вне рабочего графика" in reserve.json()["detail"]


async def test_staff_order_cannot_bypass_explicit_reservation(auth_client):
    mechanic_id = await _create_mechanic(auth_client)
    client = await auth_client.post(
        f"{API}/clients",
        json={"full_name": "Без обхода", "phone": "+79994445566"},
    )
    vehicle = await auth_client.post(
        f"{API}/vehicles",
        json={
            "client_id": client.json()["id"],
            "make": "UAZ",
            "model": "Patriot",
        },
    )
    response = await auth_client.post(
        f"{API}/orders",
        json={
            "client_id": client.json()["id"],
            "vehicle_id": vehicle.json()["id"],
            "mechanic_id": mechanic_id,
            "scheduled_at": dt.datetime.now(dt.UTC).isoformat(),
        },
    )
    assert response.status_code == 422
    assert "reservation" in response.json()["detail"]

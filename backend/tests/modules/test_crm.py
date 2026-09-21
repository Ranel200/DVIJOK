"""CRM-контракт административного frontend."""

import datetime as dt
from zoneinfo import ZoneInfo

from app.modules.clients.models import Client
from app.modules.orders.models import Order
from app.modules.schedule.models import ScheduleSlot
from app.modules.vehicles.models import Vehicle
from app.shared.enums import OrderSource, OrderStatus
from tests.conftest import API


def _future_weekday() -> dt.date:
    day = dt.datetime.now(ZoneInfo("Europe/Moscow")).date() + dt.timedelta(days=2)
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    return day


async def _crm_refs(auth_client):
    employee_response = await auth_client.post(
        f"{API}/employees",
        json={
            "email": "crm-master@example.com",
            "password": "strong-pass-123",
            "full_name": "Смирнов Алексей",
            "role": "mechanic",
        },
    )
    assert employee_response.status_code == 201, employee_response.text
    employee = employee_response.json()
    service_response = await auth_client.post(
        f"{API}/services",
        json={
            "name": "Замена масла",
            "category": "oil",
            "base_price": 5000,
        },
    )
    assert service_response.status_code == 201, service_response.text
    return employee, service_response.json()


def _payload(employee, service):
    return {
        "id": None,
        "number": 1,
        "status": "diagnostics",
        "clientName": "Иванов Пётр",
        "phone": "+79990001122",
        "email": "client@example.com",
        "description": "Проверить течь",
        "date": "2026-08-10",
        "time": "10:00",
        "source": "call",
        "lines": [
            {
                "serviceId": service["id"],
                "price": 5000,
                "discount": 10,
                "masterId": employee["id"],
            }
        ],
        "plate": "А123ВС116",
        "brand": "Toyota",
        "model": "Camry",
        "year": 2020,
        "color": "Белый",
        "vin": "JT123456789012345",
        "mileage": 45000,
        "amount": 4500,
        "services": ["Замена масла"],
        "master": "Смирнов Алексей",
        "masters": "Смирнов Алексей",
    }


async def test_crm_order_can_be_created_completely_empty(auth_client):
    response = await auth_client.post(f"{API}/crm/orders", json={})
    assert response.status_code == 201, response.text

    created = response.json()
    assert created["status"] == "new"
    assert created["clientName"] == ""
    assert created["phone"] == ""
    assert created["email"] == ""
    assert created["carBrand"] == ""
    assert created["brand"] == ""
    assert created["model"] == ""
    assert created["plate"] == ""
    assert created["lines"] == []
    assert float(created["amount"]) == 0

    clients = await auth_client.get(f"{API}/crm/clients")
    assert clients.status_code == 200
    assert clients.json() == []

    deals = await auth_client.get(f"{API}/crm/deals")
    assert deals.status_code == 200
    assert deals.json()[0]["id"] == created["id"]

    updated = await auth_client.put(
        f"{API}/crm/orders/{created['id']}",
        json={"phone": "+79990000001", "brand": "Lada"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["phone"] == "+79990000001"
    assert updated.json()["brand"] == "Lada"
    assert updated.json()["clientName"] == ""
    assert updated.json()["model"] == ""


async def test_crm_service_can_be_added_without_master(auth_client):
    _, service = await _crm_refs(auth_client)
    response = await auth_client.post(
        f"{API}/crm/orders",
        json={
            "lines": [
                {
                    "serviceId": service["id"],
                    "price": 5000,
                    "discount": 0,
                    "masterId": "",
                }
            ]
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["lines"][0]["masterId"] is None


async def test_crm_order_mileage_is_limited_to_six_digits(auth_client):
    rejected = await auth_client.post(
        f"{API}/crm/orders",
        json={"mileage": 1_000_000},
    )
    assert rejected.status_code == 422, rejected.text

    accepted = await auth_client.post(
        f"{API}/crm/orders",
        json={"mileage": 999_999},
    )
    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["mileage"] == 999_999


async def test_crm_formats_booking_in_local_time_and_uses_vehicle_mileage(
    auth_client,
    session_factory,
    organization,
):
    async with session_factory() as session:
        client = Client(
            organization_id=organization,
            full_name="Клиент Записи",
            phone="+79990009999",
        )
        session.add(client)
        await session.flush()
        vehicle = Vehicle(
            organization_id=organization,
            client_id=client.id,
            make="Bentley",
            model="Continental",
            license_plate="А456АР716",
            mileage=10_000,
        )
        session.add(vehicle)
        await session.flush()
        order = Order(
            organization_id=organization,
            number="4841-test",
            client_id=client.id,
            vehicle_id=vehicle.id,
            status=OrderStatus.NEW,
            source=OrderSource.WEBSITE,
            scheduled_at=dt.datetime(2026, 8, 18, 6, 0, tzinfo=dt.UTC),
            created_at=dt.datetime(2026, 8, 14, 22, 59),
            updated_at=dt.datetime(2026, 8, 14, 22, 59),
        )
        session.add(order)
        await session.commit()
        order_id = order.id

    response = await auth_client.get(f"{API}/crm/orders/{order_id}")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["date"] == "18.08.2026"
    assert body["time"] == "09:00"
    assert body["mileage"] == 10_000
    assert body["createdAt"] == "15 августа"
    assert body["updatedAt"] == "15 августа"


async def test_crm_create_list_columns_and_update(auth_client):
    employee, service = await _crm_refs(auth_client)
    payload = _payload(employee, service)

    created_response = await auth_client.post(f"{API}/crm/orders", json=payload)
    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    assert created["status"] == "diagnostics"
    assert created["clientName"] == "Иванов Пётр"
    assert created["carBrand"] == "Toyota Camry"
    assert float(created["amount"]) == 4500
    assert float(created["lines"][0]["discount"]) == 10
    assert created["lines"][0]["masterId"] == employee["id"]
    # Дата/время из формы не резервируют календарь автоматически.
    assert created["date"] == ""
    assert created["time"] == ""

    deals = await auth_client.get(f"{API}/crm/deals")
    assert deals.status_code == 200, deals.text
    assert deals.json()[0]["id"] == created["id"]

    columns = await auth_client.get(f"{API}/crm/columns")
    assert columns.status_code == 200, columns.text
    assert [column["id"] for column in columns.json()] == [
        "new",
        "primary",
        "diagnostics",
        "approval",
        "secondary",
        "in_progress",
        "waiting",
        "done",
    ]
    diagnostics = next(
        column for column in columns.json() if column["id"] == "diagnostics"
    )
    assert diagnostics["items"][0]["id"] == created["id"]

    payload["status"] = "approval"
    payload["description"] = "Согласовать стоимость"
    updated_response = await auth_client.put(
        f"{API}/crm/orders/{created['id']}", json=payload
    )
    assert updated_response.status_code == 200, updated_response.text
    updated = updated_response.json()
    assert updated["status"] == "approval"
    assert updated["description"] == "Согласовать стоимость"
    assert float(updated["amount"]) == 4500


async def test_crm_explicit_booking_chooses_free_master_and_is_atomic(auth_client):
    employee, service = await _crm_refs(auth_client)
    day = _future_weekday()
    configured = await auth_client.put(
        f"{API}/schedule/mechanics/{employee['mechanic_id']}/working-hours",
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

    payload = _payload(employee, service)
    payload.update(
        {
            "date": day.strftime("%d.%m.%Y"),
            "time": "10:00",
            "reserveSlot": True,
            "appointmentMasterId": None,
        }
    )
    created_response = await auth_client.post(f"{API}/crm/orders", json=payload)
    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    assert created["date"] == day.strftime("%d.%m.%Y")
    assert created["time"] == "10:00"
    assert created["appointmentMasterId"] == employee["id"]

    calendar = await auth_client.get(
        f"{API}/schedule/calendar", params={"weekStart": day.isoformat()}
    )
    assert calendar.status_code == 200, calendar.text
    selected_day = next(
        item for item in calendar.json()["days"] if item["date"] == day.isoformat()
    )
    busy = next(
        block
        for block in selected_day["slots"]["10:00"]
        if block["status"] == "busy"
    )
    assert busy["orderId"] == created["id"]
    assert busy["employeeUserId"] == employee["id"]

    deals_before = await auth_client.get(f"{API}/crm/deals")
    conflict = await auth_client.post(f"{API}/crm/orders", json=payload)
    assert conflict.status_code == 422, conflict.text
    assert "нет свободного мастера" in conflict.json()["detail"]
    deals_after = await auth_client.get(f"{API}/crm/deals")
    assert len(deals_after.json()) == len(deals_before.json())


async def test_crm_marker_persists_and_is_visible_in_calendar(auth_client):
    employee, _ = await _crm_refs(auth_client)
    day = _future_weekday()
    configured = await auth_client.put(
        f"{API}/schedule/mechanics/{employee['mechanic_id']}/working-hours",
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

    marker = await auth_client.post(
        f"{API}/crm/markers",
        json={"name": "Срочный", "color": "rgb(255, 10, 20)"},
    )
    assert marker.status_code == 201, marker.text
    marker_id = marker.json()["id"]

    created = await auth_client.post(
        f"{API}/crm/orders",
        json={
            "clientName": "Быстрый клиент",
            "phone": "+79990004455",
            "date": day.strftime("%d.%m.%Y"),
            "time": "10:00",
            "reserveSlot": True,
            "appointmentMasterId": employee["id"],
            "markerId": marker_id,
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["markerId"] == marker_id
    assert created.json()["markerColor"] == "rgb(255, 10, 20)"

    calendar = await auth_client.get(
        f"{API}/schedule/calendar", params={"weekStart": day.isoformat()}
    )
    selected_day = next(item for item in calendar.json()["days"] if item["date"] == day.isoformat())
    busy = next(block for block in selected_day["slots"]["10:00"] if block["status"] == "busy")
    assert busy["markerColor"] == "rgb(255, 10, 20)"


async def test_crm_status_can_move_between_any_columns_and_delete(auth_client):
    employee, service = await _crm_refs(auth_client)
    payload = _payload(employee, service)
    payload["status"] = "new"
    created = (await auth_client.post(f"{API}/crm/orders", json=payload)).json()

    statuses = [
        "done",
        "new",
        "waiting",
        "primary",
        "secondary",
        "diagnostics",
        "in_progress",
        "approval",
    ]
    for expected in statuses:
        moved = await auth_client.patch(
            f"{API}/crm/orders/{created['id']}/status",
            json={"status": expected},
        )
        assert moved.status_code == 200, moved.text
        assert moved.json()["status"] == expected

    hidden_status = await auth_client.patch(
        f"{API}/crm/orders/{created['id']}/status",
        json={"status": "cancelled"},
    )
    assert hidden_status.status_code == 422

    deleted = await auth_client.delete(f"{API}/crm/orders/{created['id']}")
    assert deleted.status_code == 204
    missing = await auth_client.get(f"{API}/crm/orders/{created['id']}")
    assert missing.status_code == 404


async def test_crm_delete_releases_linked_schedule_slot(
    auth_client, session_factory, organization
):
    employee, service = await _crm_refs(auth_client)
    created = (
        await auth_client.post(f"{API}/crm/orders", json=_payload(employee, service))
    ).json()

    async with session_factory() as session:
        slot = ScheduleSlot(
            organization_id=organization,
            mechanic_id=employee["id"],
            order_id=created["id"],
            start_time=dt.datetime(2026, 8, 18, 7, 0, tzinfo=dt.UTC),
            end_time=dt.datetime(2026, 8, 18, 8, 0, tzinfo=dt.UTC),
        )
        session.add(slot)
        await session.commit()
        slot_id = slot.id

    deleted = await auth_client.delete(f"{API}/crm/orders/{created['id']}")
    assert deleted.status_code == 204, deleted.text

    async with session_factory() as session:
        assert await session.get(ScheduleSlot, slot_id) is None

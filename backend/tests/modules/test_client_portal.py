"""Тесты модуля client_portal: discovery, бронирование, кабинет клиента.

Зависит от client_auth (ClientAccount, create_client_access_token) — до
финальной интеграции (импорт этих символов в app.models / регистрация
роутера в app.main) этот файл падает с ImportError, это ожидаемо.
"""

import datetime as dt
import hashlib

import pytest_asyncio
from sqlalchemy import select

from app.core.security import create_client_access_token
from app.modules.client_auth.models import ClientAccount
from app.modules.client_vehicles.models import ClientVehicle
from app.modules.clients.models import Client
from app.modules.mechanics.models import Mechanic
from app.modules.orders.models import Order, OrderDocument
from app.modules.organizations.models import Organization
from app.modules.referrals.models import OrganizationReferral
from app.modules.schedule.models import ScheduleSlot
from app.modules.services.models import Service
from app.modules.vehicles.models import Vehicle
from app.shared.enums import (
    LegalForm,
    OrderDocumentSource,
    OrderSource,
    OrderStatus,
    OrganizationStatus,
    ServiceCategory,
    TaxSystem,
)
from tests.conftest import API


@pytest_asyncio.fixture
async def client_account(session_factory):
    async with session_factory() as session:
        account = ClientAccount(phone="+79995554433", full_name=None)
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return account.id


@pytest_asyncio.fixture
async def client_token(client_account):
    return create_client_access_token(client_account)


@pytest_asyncio.fixture
async def portal_client(client, client_token):
    client.headers.update({"Authorization": f"Bearer {client_token}"})
    return client


@pytest_asyncio.fixture
async def service_and_mechanic(session_factory, organization):
    async with session_factory() as session:
        service = Service(
            organization_id=organization,
            name="Замена масла",
            category=ServiceCategory.OIL,
            base_price=1500,
            duration_minutes=40,
        )
        diagnostics = Service(
            organization_id=organization,
            name="Диагностика",
            public_booking_key="diagnostics",
            category=ServiceCategory.DIAGNOSTICS,
            admin_category="diagnostics",
            base_price=2500,
            duration_minutes=60,
        )
        repair = Service(
            organization_id=organization,
            name="Ремонт",
            public_booking_key="repair",
            category=ServiceCategory.OTHER,
            admin_category="repair",
            base_price=5000,
            duration_minutes=60,
        )
        mechanic = Mechanic(organization_id=organization, full_name="Иван Мастеров")
        session.add_all([service, diagnostics, repair, mechanic])
        await session.commit()
        await session.refresh(service)
        await session.refresh(diagnostics)
        await session.refresh(repair)
        await session.refresh(mechanic)
        return {
            "service_id": service.id,
            "diagnostics_id": diagnostics.id,
            "repair_id": repair.id,
            "mechanic_id": mechanic.id,
        }


@pytest_asyncio.fixture
async def frontend_vehicle(session_factory, organization, client_account):
    async with session_factory() as session:
        client = Client(
            organization_id=organization,
            full_name="Клиент Тестов",
            phone="+79995554433",
            client_account_id=client_account,
        )
        session.add(client)
        await session.flush()
        vehicle = Vehicle(
            organization_id=organization,
            client_id=client.id,
            make="Toyota",
            model="Camry",
            year=2020,
            color="Белый",
            license_plate="А123ВС116",
            vin="TESTCLIENTVIN0001",
            mileage=50000,
        )
        session.add(vehicle)
        await session.commit()
        await session.refresh(vehicle)
        return vehicle.id


async def test_client_portal_requires_client_token(client, auth_client):
    resp = await client.get(f"{API}/client-portal/organizations")
    assert resp.status_code == 401

    # Staff-токен не должен проходить клиентский контур.
    resp2 = await auth_client.get(f"{API}/client-portal/organizations")
    assert resp2.status_code == 401


async def test_discovery_lists_organization(portal_client, organization, service_and_mechanic):
    orgs = await portal_client.get(f"{API}/client-portal/organizations")
    assert orgs.status_code == 200
    assert any(o["id"] == organization for o in orgs.json())

    services = await portal_client.get(f"{API}/client-portal/organizations/{organization}/services")
    assert services.status_code == 200
    assert len(services.json()) == 1
    assert service_and_mechanic["service_id"] in {item["id"] for item in services.json()}

    mechanics = await portal_client.get(
        f"{API}/client-portal/organizations/{organization}/mechanics"
    )
    assert mechanics.status_code == 200
    assert len(mechanics.json()) == 1


async def test_booking_creates_order_and_slot(portal_client, organization, service_and_mechanic):
    start = (dt.datetime.now(dt.UTC) + dt.timedelta(days=1)).replace(
        minute=0, second=0, microsecond=0
    )
    resp = await portal_client.post(
        f"{API}/client-portal/bookings",
        json={
            "organization_id": organization,
            "full_name": "Клиент Тестов",
            "vehicle": {"make": "Kia", "model": "Rio", "vin": "TESTVIN1234567890"[:17]},
            "service_id": service_and_mechanic["service_id"],
            "mechanic_id": service_and_mechanic["mechanic_id"],
            "start_time": start.isoformat(),
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "new"
    assert body["slot_id"] is not None

    # Пересекающееся бронирование того же мастера должно упасть по 422.
    conflict = await portal_client.post(
        f"{API}/client-portal/bookings",
        json={
            "organization_id": organization,
            "full_name": "Другой Клиент",
            "vehicle": {"make": "Kia", "model": "Sportage"},
            "mechanic_id": service_and_mechanic["mechanic_id"],
            "start_time": start.isoformat(),
        },
    )
    assert conflict.status_code == 422

    my_orders = await portal_client.get(f"{API}/client-portal/me/orders")
    assert my_orders.status_code == 200
    assert my_orders.json()["total"] == 1
    assert my_orders.json()["items"][0]["status_label"] == "Записан"

    my_vehicles = await portal_client.get(f"{API}/client-portal/me/vehicles")
    assert my_vehicles.status_code == 200
    assert len(my_vehicles.json()) == 1

    order_id = my_orders.json()["items"][0]["id"]
    invoice = await portal_client.get(f"{API}/client-portal/me/orders/{order_id}/invoice")
    assert invoice.status_code == 200
    assert invoice.json()["items"][0]["description"] == "Замена масла"


async def test_booking_without_mechanic_skips_slot(portal_client, organization):
    start = dt.datetime.now(dt.UTC) + dt.timedelta(days=2)
    resp = await portal_client.post(
        f"{API}/client-portal/bookings",
        json={
            "organization_id": organization,
            "full_name": "Клиент Без Мастера",
            "vehicle": {"make": "Lada", "model": "Vesta"},
            "start_time": start.isoformat(),
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["slot_id"] is None


async def test_invoice_of_foreign_order_is_not_found(portal_client, organization):
    resp = await portal_client.get(f"{API}/client-portal/me/orders/999999/invoice")
    assert resp.status_code == 404


async def test_existing_frontend_flow_uses_real_availability_and_reserves(
    portal_client,
    organization,
    service_and_mechanic,
    frontend_vehicle,
    session_factory,
):
    directory = await portal_client.get(f"{API}/client-portal/ui/services")
    assert directory.status_code == 200, directory.text
    assert directory.json()["all"][0]["id"] == str(organization)

    options = await portal_client.get(
        f"{API}/client-portal/ui/booking/options",
        params={"shopId": organization},
    )
    assert options.status_code == 200, options.text
    assert options.json()["serviceOptions"] == [
        {"value": "diagnostics", "label": "Диагностика", "price": None},
        {"value": "repair", "label": "Ремонт", "price": None},
    ]
    assert options.json()["carOptions"][0]["value"] == str(frontend_vehicle)
    assert options.json()["masters"][0]["id"] == "any"

    day = dt.date.today() + dt.timedelta(days=1)
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    availability = await portal_client.get(
        f"{API}/client-portal/ui/booking/availability",
        params={
            "shopId": organization,
            "year": day.year,
            "month": day.month - 1,
            "serviceId": "diagnostics",
            "masterId": "any",
        },
    )
    assert availability.status_code == 200, availability.text
    slots = [item for item in availability.json()["slots"] if item["date"] == day.isoformat()]
    assert slots

    payload = {
        "shopId": organization,
        "shopName": "КОМИТ Тест",
        "serviceId": "diagnostics",
        "carId": frontend_vehicle,
        "masterId": "any",
        "date": day.isoformat(),
        "time": slots[0]["time"],
    }
    booked = await portal_client.post(f"{API}/client-portal/ui/booking", json=payload)
    assert booked.status_code == 201, booked.text
    assert booked.json()["slot_id"] is not None
    assert booked.json()["mechanic_id"] == service_and_mechanic["mechanic_id"]

    repeated = await portal_client.post(f"{API}/client-portal/ui/booking", json=payload)
    assert repeated.status_code == 201, repeated.text
    assert repeated.json()["order_id"] == booked.json()["order_id"]
    assert repeated.json()["slot_id"] == booked.json()["slot_id"]

    moved_day = day + dt.timedelta(days=1)
    while moved_day.weekday() >= 5:
        moved_day += dt.timedelta(days=1)
    moved_availability = await portal_client.get(
        f"{API}/client-portal/ui/booking/availability",
        params={
            "shopId": organization,
            "year": moved_day.year,
            "month": moved_day.month - 1,
            "serviceId": "repair",
            "masterId": "any",
        },
    )
    assert moved_availability.status_code == 200, moved_availability.text
    moved_slot = next(
        item
        for item in moved_availability.json()["slots"]
        if item["date"] == moved_day.isoformat()
    )
    moved_payload = {
        **payload,
        "serviceId": "repair",
        "date": moved_day.isoformat(),
        "time": moved_slot["time"],
    }
    moved = await portal_client.post(f"{API}/client-portal/ui/booking", json=moved_payload)
    assert moved.status_code == 201, moved.text
    assert moved.json()["order_id"] == booked.json()["order_id"]
    assert moved.json()["slot_id"] == booked.json()["slot_id"]
    assert moved.json()["start_time"] != booked.json()["start_time"]

    async with session_factory() as session:
        active_orders = list(
            (
                await session.execute(
                    select(Order).where(
                        Order.organization_id == organization,
                        Order.vehicle_id == frontend_vehicle,
                    )
                )
            )
            .scalars()
            .all()
        )
        order_slots = list(
            (
                await session.execute(
                    select(ScheduleSlot).where(
                        ScheduleSlot.order_id == booked.json()["order_id"]
                    )
                )
            )
            .scalars()
            .all()
        )
    assert len(active_orders) == 1
    assert len(order_slots) == 1
    assert active_orders[0].items[0].service_id == service_and_mechanic["repair_id"]
    assert active_orders[0].mileage == 50_000

    cars = await portal_client.get(f"{API}/client-portal/ui/cars")
    assert cars.status_code == 200, cars.text
    assert cars.json()["cars"][0]["nextAppointment"] is not None

    history = await portal_client.get(f"{API}/client-portal/ui/history")
    assert history.status_code == 200, history.text
    assert history.json()["items"][0]["serviceName"] == "КОМИТ Тест"
    assert history.json()["items"][0]["orderReady"] is False

    document = await portal_client.get(
        f"{API}/client-portal/ui/history/{booked.json()['order_id']}/document"
    )
    assert document.status_code == 404

    content = b"%PDF-1.4 client test"
    async with session_factory() as session:
        session.add(
            OrderDocument(
                organization_id=organization,
                order_id=booked.json()["order_id"],
                source=OrderDocumentSource.GENERATED,
                filename="order.pdf",
                content_type="application/pdf",
                size_bytes=len(content),
                sha256=hashlib.sha256(content).hexdigest(),
                content=content,
            )
        )
        await session.commit()

    ready_document = await portal_client.get(
        f"{API}/client-portal/ui/history/{booked.json()['order_id']}/document"
    )
    assert ready_document.status_code == 200
    assert ready_document.headers["content-type"] == "application/pdf"
    assert ready_document.content == content

    async with session_factory() as session:
        accepted_order = await session.get(Order, booked.json()["order_id"])
        assert accepted_order is not None
        accepted_order.status = OrderStatus.IN_PROGRESS
        await session.commit()

    next_day = moved_day + dt.timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += dt.timedelta(days=1)
    next_availability = await portal_client.get(
        f"{API}/client-portal/ui/booking/availability",
        params={
            "shopId": organization,
            "year": next_day.year,
            "month": next_day.month - 1,
            "serviceId": "diagnostics",
            "masterId": "any",
        },
    )
    next_slot = next(
        item
        for item in next_availability.json()["slots"]
        if item["date"] == next_day.isoformat()
    )
    next_booking = await portal_client.post(
        f"{API}/client-portal/ui/booking",
        json={
            **payload,
            "date": next_day.isoformat(),
            "time": next_slot["time"],
        },
    )
    assert next_booking.status_code == 201, next_booking.text
    assert next_booking.json()["order_id"] != booked.json()["order_id"]


async def test_client_vehicle_mileage_is_limited_to_six_digits(portal_client):
    payload = {
        "brand": "Toyota",
        "model": "Camry",
        "plate": "А999АА116",
        "plateType": "ru",
        "vin": "WVWZZZ1JZXW999999",
        "year": 2020,
        "color": "Белый",
        "mileage": 1_000_000,
    }
    rejected = await portal_client.post(f"{API}/cars", json=payload)
    assert rejected.status_code == 422, rejected.text

    payload["mileage"] = 999_999
    accepted = await portal_client.post(f"{API}/cars", json=payload)
    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["mileage"] == 999_999


async def test_booking_syncs_existing_organization_vehicle_from_global_profile(
    portal_client,
    organization,
    client_account,
    service_and_mechanic,
    session_factory,
):
    created = await portal_client.post(
        f"{API}/cars",
        json={
            "brand": "Bentley",
            "model": "Continental",
            "plate": "А456АР116",
            "plateType": "ru",
            "vin": "WVWZZZ1JZXW000099",
            "year": 2020,
            "color": "Жемчужный",
            "mileage": 11_000,
        },
    )
    assert created.status_code == 201, created.text
    global_vehicle_id = created.json()["id"]

    day = dt.date.today() + dt.timedelta(days=1)
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    availability = await portal_client.get(
        f"{API}/client-portal/ui/booking/availability",
        params={
            "shopId": organization,
            "year": day.year,
            "month": day.month - 1,
            "serviceId": "diagnostics",
            "masterId": "any",
        },
    )
    assert availability.status_code == 200, availability.text
    slot = next(item for item in availability.json()["slots"] if item["date"] == day.isoformat())
    payload = {
        "shopId": organization,
        "serviceId": "diagnostics",
        "carId": global_vehicle_id,
        "masterId": "any",
        "date": day.isoformat(),
        "time": slot["time"],
    }
    booked = await portal_client.post(f"{API}/client-portal/ui/booking", json=payload)
    assert booked.status_code == 201, booked.text

    async with session_factory() as session:
        organization_vehicle = (
            await session.execute(
                select(Vehicle).where(
                    Vehicle.organization_id == organization,
                    Vehicle.vin == "WVWZZZ1JZXW000099",
                )
            )
        ).scalar_one()
        organization_vehicle.make = "Старое название"
        organization_vehicle.model = "Старая модель"
        organization_vehicle.year = 1999
        organization_vehicle.color = "Старый цвет"
        organization_vehicle.mileage = 1_100_000
        await session.commit()

    moved_day = day + dt.timedelta(days=1)
    while moved_day.weekday() >= 5:
        moved_day += dt.timedelta(days=1)
    moved_availability = await portal_client.get(
        f"{API}/client-portal/ui/booking/availability",
        params={
            "shopId": organization,
            "year": moved_day.year,
            "month": moved_day.month - 1,
            "serviceId": "repair",
            "masterId": "any",
        },
    )
    assert moved_availability.status_code == 200, moved_availability.text
    moved_slot = next(
        item
        for item in moved_availability.json()["slots"]
        if item["date"] == moved_day.isoformat()
    )
    moved = await portal_client.post(
        f"{API}/client-portal/ui/booking",
        json={
            **payload,
            "serviceId": "repair",
            "date": moved_day.isoformat(),
            "time": moved_slot["time"],
        },
    )
    assert moved.status_code == 201, moved.text
    assert moved.json()["order_id"] == booked.json()["order_id"]

    async with session_factory() as session:
        organization_vehicle = (
            await session.execute(
                select(Vehicle).where(
                    Vehicle.organization_id == organization,
                    Vehicle.vin == "WVWZZZ1JZXW000099",
                )
            )
        ).scalar_one()
        order = await session.get(Order, booked.json()["order_id"])
        global_vehicle = await session.get(ClientVehicle, global_vehicle_id)
    assert global_vehicle is not None
    assert organization_vehicle.make == global_vehicle.brand
    assert organization_vehicle.model == global_vehicle.model
    assert organization_vehicle.year == global_vehicle.year
    assert organization_vehicle.color == global_vehicle.color
    assert global_vehicle.mileage == 11_000
    assert organization_vehicle.mileage == global_vehicle.mileage
    assert order is not None
    assert order.mileage == global_vehicle.mileage


async def test_current_client_frontend_contract_uses_global_vehicle_across_branches(
    portal_client,
    organization,
    client_account,
    service_and_mechanic,
    session_factory,
):
    created = await portal_client.post(
        f"{API}/cars",
        json={
            "brand": "Toyota",
            "model": "Camry",
            "plate": "А123ВС116",
            "plateType": "ru",
            "vin": "WVWZZZ1JZXW000001",
            "year": "2020",
            "color": "Белый",
            "mileage": "50000",
        },
    )
    assert created.status_code == 201, created.text
    vehicle_id = created.json()["id"]
    assert created.json()["model"] == "Camry"
    assert created.json()["plateType"] == "ru"

    updated = await portal_client.put(
        f"{API}/cars/{vehicle_id}",
        json={
            "brand": "Toyota",
            "model": "Camry",
            "plate": "А123ВС116",
            "plateType": "ru",
            "vin": "WVWZZZ1JZXW000001",
            "year": 2020,
            "color": "Серебристый",
            "mileage": 51000,
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["color"] == "Серебристый"

    cars = await portal_client.get(f"{API}/cars")
    assert cars.status_code == 200, cars.text
    assert cars.json()["cars"][0]["brand"] == "Toyota"
    assert cars.json()["cars"][0]["model"] == "Camry"
    assert cars.json()["cars"][0]["mileage"] == 51000

    branches = await portal_client.get(f"{API}/branches")
    assert branches.status_code == 200, branches.text
    assert branches.json()["branches"][0]["id"] == str(organization)

    specialists = await portal_client.get(
        f"{API}/booking/specialists",
        params={"branchId": organization},
    )
    assert specialists.status_code == 200, specialists.text
    assert specialists.json()["specialists"][0]["id"] == str(service_and_mechanic["mechanic_id"])

    options = await portal_client.get(
        f"{API}/client-portal/ui/booking/options",
        params={"branchId": organization},
    )
    assert options.status_code == 200, options.text
    assert options.json()["serviceOptions"][0]["price"] is None

    day = dt.date.today() + dt.timedelta(days=1)
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    availability = await portal_client.get(
        f"{API}/client-portal/ui/booking/availability",
        params={
            "branchId": organization,
            "year": day.year,
            "month": day.month - 1,
            "serviceId": "diagnostics",
            "specialistId": service_and_mechanic["mechanic_id"],
        },
    )
    assert availability.status_code == 200, availability.text
    slot = next(item for item in availability.json()["slots"] if item["date"] == day.isoformat())

    def booking_payload(branch_id, service_id, specialist_id, time):
        return {
            "branchId": branch_id,
            "specialistId": specialist_id,
            "serviceId": service_id,
            "date": day.isoformat(),
            "time": time,
            "client": {
                "name": "Клиент Тестов",
                "phone": "+7 999 555-44-33",
                "brand": "Toyota",
                "model": "Camry",
                "plateType": "ru",
                "plate": "А123ВС116",
                "consentPersonal": True,
                "consentTransfer": True,
            },
        }

    booked = await portal_client.post(
        f"{API}/client-portal/ui/booking",
        json=booking_payload(
            organization,
            "diagnostics",
            service_and_mechanic["mechanic_id"],
            slot["time"],
        ),
    )
    assert booked.status_code == 201, booked.text

    async with session_factory() as session:
        second_org = Organization(
            name="Второй автосервис",
            inn="9876543210",
            tax_system=TaxSystem.USN,
            legal_form=LegalForm.OOO,
            legal_address="г. Москва, второй адрес",
            phone="+70000000001",
            status=OrganizationStatus.ACTIVE,
        )
        session.add(second_org)
        await session.flush()
        second_service = Service(
            organization_id=second_org.id,
            name="Диагностика",
            category=ServiceCategory.DIAGNOSTICS,
            base_price=2000,
            duration_minutes=60,
        )
        second_mechanic = Mechanic(
            organization_id=second_org.id,
            full_name="Второй Мастер",
        )
        session.add_all([second_service, second_mechanic])
        await session.commit()
        second_ids = second_org.id, second_service.id, second_mechanic.id

    second_availability = await portal_client.get(
        f"{API}/client-portal/ui/booking/availability",
        params={
            "branchId": second_ids[0],
            "year": day.year,
            "month": day.month - 1,
            "serviceId": second_ids[1],
            "specialistId": second_ids[2],
        },
    )
    assert second_availability.status_code == 200, second_availability.text
    second_slot = next(
        item for item in second_availability.json()["slots"] if item["date"] == day.isoformat()
    )
    second_booked = await portal_client.post(
        f"{API}/client-portal/ui/booking",
        json=booking_payload(*second_ids, second_slot["time"]),
    )
    assert second_booked.status_code == 201, second_booked.text

    async with session_factory() as session:
        global_vehicles = list(
            (
                await session.execute(
                    select(ClientVehicle).where(ClientVehicle.client_account_id == client_account)
                )
            )
            .scalars()
            .all()
        )
        tenant_vehicles = list(
            (await session.execute(select(Vehicle).where(Vehicle.vin == "WVWZZZ1JZXW000001")))
            .scalars()
            .all()
        )
    assert len(global_vehicles) == 1
    assert {item.organization_id for item in tenant_vehicles} == {
        organization,
        second_ids[0],
    }


async def test_public_booking_link_creates_guest_order_without_registration(
    client,
    organization,
    service_and_mechanic,
    session_factory,
):
    code = "GuestBookingA1B2"
    async with session_factory() as session:
        session.add(OrganizationReferral(organization_id=organization, code=code))
        await session.commit()

    context = await client.get(f"{API}/public-booking/{code}")
    assert context.status_code == 200, context.text
    assert len(context.json()["branches"]) == 1
    branch = context.json()["branches"][0]
    assert branch["id"] == code
    assert branch["name"] == "КОМИТ Тест"
    assert branch["address"] == "г. Москва, тестовая"
    assert "organization_id" not in context.text

    options = await client.get(f"{API}/public-booking/{code}/options")
    assert options.status_code == 200, options.text
    assert options.json()["serviceOptions"] == [
        {"value": "diagnostics", "label": "Диагностика", "price": None},
        {"value": "repair", "label": "Ремонт", "price": None},
    ]
    assert options.json()["carOptions"] == []

    specialists = await client.get(f"{API}/public-booking/{code}/specialists")
    assert specialists.status_code == 200, specialists.text
    assert specialists.json()["specialists"][0]["id"] == str(service_and_mechanic["mechanic_id"])

    day = dt.date.today() + dt.timedelta(days=1)
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    availability = await client.get(
        f"{API}/public-booking/{code}/availability",
        params={
            "year": day.year,
            "month": day.month - 1,
            "serviceId": "diagnostics",
            "specialistId": service_and_mechanic["mechanic_id"],
        },
    )
    assert availability.status_code == 200, availability.text
    slot = next(item for item in availability.json()["slots"] if item["date"] == day.isoformat())
    payload = {
        "specialistId": service_and_mechanic["mechanic_id"],
        "serviceId": "diagnostics",
        "date": day.isoformat(),
        "time": slot["time"],
        "client": {
            "name": "Гостевой Клиент",
            "phone": "+7 999 111-22-33",
            "brand": "Lada",
            "model": "Vesta",
            "plateType": "ru",
            "plate": "А111АА116",
            "consentPersonal": True,
            "consentTransfer": True,
        },
    }
    booked = await client.post(f"{API}/public-booking/{code}", json=payload)
    assert booked.status_code == 201, booked.text
    assert set(booked.json()) == {"number", "status", "startTime", "endTime"}
    assert booked.json()["status"] == "new"

    async with session_factory() as session:
        crm_client = (
            await session.execute(
                select(Client).where(
                    Client.organization_id == organization,
                    Client.phone == "+79991112233",
                )
            )
        ).scalar_one()
        order = (
            await session.execute(
                select(Order).where(
                    Order.organization_id == organization,
                    Order.client_id == crm_client.id,
                )
            )
        ).scalar_one()
        schedule_slot = (
            await session.execute(select(ScheduleSlot).where(ScheduleSlot.order_id == order.id))
        ).scalar_one()
        account = (
            await session.execute(
                select(ClientAccount).where(ClientAccount.phone == "+79991112233")
            )
        ).scalar_one_or_none()
    assert crm_client.client_account_id is None
    assert account is None
    assert order.source == OrderSource.REFERRAL
    assert schedule_slot.mechanic_id == service_and_mechanic["mechanic_id"]

    repeated = await client.post(f"{API}/public-booking/{code}", json=payload)
    assert repeated.status_code == 201, repeated.text
    assert repeated.json()["number"] == booked.json()["number"]

    async with session_factory() as session:
        orders = list(
            (
                await session.execute(
                    select(Order).where(
                        Order.organization_id == organization,
                        Order.client_id == crm_client.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        slots = list(
            (
                await session.execute(
                    select(ScheduleSlot).where(ScheduleSlot.order_id == order.id)
                )
            )
            .scalars()
            .all()
        )
    assert len(orders) == 1
    assert len(slots) == 1


async def test_public_booking_rejects_unknown_code(client):
    response = await client.get(f"{API}/public-booking/UnknownCodeA1B2C")
    assert response.status_code == 404

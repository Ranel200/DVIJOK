"""Тесты модуля orders: создание заказ-наряда, позиции, статусная машина."""

from io import BytesIO
from zipfile import ZipFile

from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import OrderCreate
from app.modules.orders.service import OrderService
from app.modules.organizations.models import Organization
from app.shared.enums import LegalForm, OrganizationStatus, TaxSystem
from tests.conftest import API


async def _setup_refs(auth_client):
    client = (
        await auth_client.post(
            f"{API}/clients", json={"full_name": "Клиент", "phone": "+70000000001"}
        )
    ).json()
    vehicle = (
        await auth_client.post(
            f"{API}/vehicles",
            json={"client_id": client["id"], "make": "Lada", "model": "Vesta"},
        )
    ).json()
    service = (
        await auth_client.post(
            f"{API}/services",
            json={"name": "ТО-1", "category": "to", "base_price": 5000, "labor_hours": 2},
        )
    ).json()
    return client, vehicle, service


async def test_order_lifecycle(auth_client):
    client, vehicle, service = await _setup_refs(auth_client)

    # Создание заказа с одной услугой — цена и нормо-часы из каталога
    created = await auth_client.post(
        f"{API}/orders",
        json={
            "client_id": client["id"],
            "vehicle_id": vehicle["id"],
            "source": "website",
            "items": [{"item_type": "service", "service_id": service["id"]}],
        },
    )
    assert created.status_code == 201, created.text
    order = created.json()
    assert order["status"] == "new"
    assert order["source"] == "website"
    assert order["client"]["full_name"] == "Клиент"
    assert order["client"]["phone"] == "+70000000001"
    assert order["vehicle"]["make"] == "Lada"
    assert order["vehicle"]["model"] == "Vesta"
    assert order["mechanic"] is None
    assert len(order["items"]) == 1
    assert float(order["total_amount"]) == 5000.0
    assert order["number"] == "1"
    order_id = order["id"]

    filtered = await auth_client.get(f"{API}/orders", params={"source": "website"})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["id"] == order_id

    empty = await auth_client.get(f"{API}/orders", params={"source": "call"})
    assert empty.status_code == 200
    assert empty.json()["total"] == 0

    # Недопустимый переход new → done
    bad = await auth_client.patch(f"{API}/orders/{order_id}/status", json={"status": "done"})
    assert bad.status_code == 422

    # new → in_progress (фиксируется started_at)
    started = await auth_client.patch(
        f"{API}/orders/{order_id}/status", json={"status": "in_progress"}
    )
    assert started.status_code == 200
    assert started.json()["status"] == "in_progress"
    assert started.json()["started_at"] is not None

    # Без документа закрытие запрещено.
    no_document = await auth_client.patch(
        f"{API}/orders/{order_id}/status", json={"status": "done"}
    )
    assert no_document.status_code == 422
    assert no_document.json()["detail"] == (
        "Для перевода заказа в статус «Готово» сначала оформите заказ-наряд"
    )

    generated = await auth_client.post(f"{API}/orders/{order_id}/document/generate")
    assert generated.status_code == 201, generated.text
    assert generated.json()["source"] == "generated"
    assert generated.json()["content_type"] == "text/html"
    assert generated.json()["size_bytes"] > 0

    downloaded = await auth_client.get(f"{API}/orders/{order_id}/document/content")
    assert downloaded.status_code == 200
    assert downloaded.headers["content-disposition"].startswith("attachment;")
    assert downloaded.headers["x-content-sha256"] == generated.json()["sha256"]
    text = downloaded.content.decode()
    assert "Заказ-наряд" in text
    assert "Клиент" in text
    assert "Lada Vesta" in text
    assert "ТО-1" in text
    assert "5000.00" in text

    # После оформления in_progress → done фиксирует completed_at.
    done = await auth_client.patch(f"{API}/orders/{order_id}/status", json={"status": "done"})
    assert done.status_code == 200, done.text
    assert done.json()["status"] == "done"
    assert done.json()["completed_at"] is not None
    assert done.json()["document"]["id"] == generated.json()["id"]

    # Состав закрытого заказа менять нельзя
    locked = await auth_client.post(
        f"{API}/orders/{order_id}/items",
        json={"item_type": "service", "service_id": service["id"]},
    )
    assert locked.status_code == 422


async def test_order_numbers_are_sequential_per_organization(session_factory, organization):
    async with session_factory() as session:
        second_organization = Organization(
            name="Второй автосервис",
            inn="0987654321",
            tax_system=TaxSystem.USN,
            legal_form=LegalForm.OOO,
            legal_address="г. Казань, тестовая",
            phone="+70000000009",
            status=OrganizationStatus.ACTIVE,
        )
        session.add(second_organization)
        await session.flush()

        first_service = OrderService(OrderRepository(session, organization))
        second_service = OrderService(OrderRepository(session, second_organization.id))

        first_numbers = [(await first_service.create(OrderCreate(), None)).number for _ in range(2)]
        second_numbers = [
            (await second_service.create(OrderCreate(), None)).number for _ in range(2)
        ]

        assert first_numbers == ["1", "2"]
        assert second_numbers == ["1", "2"]
        assert (await session.get(Organization, organization)).next_order_number == 3
        assert second_organization.next_order_number == 3


async def test_order_agreement_status(auth_client):
    client, vehicle, service = await _setup_refs(auth_client)
    order = (
        await auth_client.post(
            f"{API}/orders",
            json={
                "client_id": client["id"],
                "vehicle_id": vehicle["id"],
                "items": [{"item_type": "service", "service_id": service["id"]}],
            },
        )
    ).json()
    order_id = order["id"]

    await auth_client.patch(f"{API}/orders/{order_id}/status", json={"status": "in_progress"})

    agreed = await auth_client.patch(
        f"{API}/orders/{order_id}/status", json={"status": "agreement"}
    )
    assert agreed.status_code == 200
    assert agreed.json()["status"] == "agreement"

    await auth_client.post(f"{API}/orders/{order_id}/document/generate")
    done = await auth_client.patch(f"{API}/orders/{order_id}/status", json={"status": "done"})
    assert done.status_code == 200
    assert done.json()["status"] == "done"


async def test_order_vehicle_must_belong_to_client(auth_client):
    client_a = (
        await auth_client.post(f"{API}/clients", json={"full_name": "A", "phone": "+70000000002"})
    ).json()
    client_b = (
        await auth_client.post(f"{API}/clients", json={"full_name": "B", "phone": "+70000000003"})
    ).json()
    vehicle_b = (
        await auth_client.post(
            f"{API}/vehicles",
            json={"client_id": client_b["id"], "make": "Kia", "model": "Rio"},
        )
    ).json()

    resp = await auth_client.post(
        f"{API}/orders",
        json={"client_id": client_a["id"], "vehicle_id": vehicle_b["id"], "items": []},
    )
    assert resp.status_code == 422


async def test_order_intake_atomically_creates_and_reuses_refs(auth_client):
    service = (
        await auth_client.post(
            f"{API}/services",
            json={"name": "Диагностика", "category": "diagnostics", "base_price": 2500},
        )
    ).json()
    payload = {
        "client": {
            "full_name": "Новый клиент",
            "phone": "+79991112233",
            "email": "client@example.com",
        },
        "vehicle": {
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "license_plate": "А123ВС116",
            "vin": "JT123456789012345",
            "color": "Белый",
            "mileage": 45000,
        },
        "source": "call",
        "comment": "Создано из CRM",
        "items": [{"service_id": service["id"]}],
    }

    created = await auth_client.post(f"{API}/orders/intake", json=payload)
    assert created.status_code == 201, created.text
    first = created.json()
    assert first["source"] == "call"
    assert first["client"]["full_name"] == "Новый клиент"
    assert first["client"]["email"] == "client@example.com"
    assert first["vehicle"]["vin"] == "JT123456789012345"
    assert first["mechanic"] is None
    assert first["scheduled_at"] is None
    assert float(first["total_amount"]) == 2500

    repeated = await auth_client.post(f"{API}/orders/intake", json=payload)
    assert repeated.status_code == 201, repeated.text
    second = repeated.json()
    assert second["id"] != first["id"]
    assert second["client_id"] == first["client_id"]
    assert second["vehicle_id"] == first["vehicle_id"]


async def test_order_intake_rejects_ambiguous_references(auth_client):
    response = await auth_client.post(
        f"{API}/orders/intake",
        json={
            "client_id": 1,
            "client": {"full_name": "Лишний", "phone": "+79990000000"},
            "vehicle": {"make": "Lada", "model": "Vesta"},
        },
    )
    assert response.status_code == 422


async def test_upload_order_document_and_validation(auth_client):
    client, vehicle, service = await _setup_refs(auth_client)
    order = (
        await auth_client.post(
            f"{API}/orders",
            json={
                "client_id": client["id"],
                "vehicle_id": vehicle["id"],
                "items": [{"item_type": "service", "service_id": service["id"]}],
            },
        )
    ).json()
    order_id = order["id"]

    invalid = await auth_client.post(
        f"{API}/orders/{order_id}/document/upload",
        files={"file": ("narjad.pdf", b"not a pdf", "application/pdf")},
    )
    assert invalid.status_code == 422
    assert invalid.json()["detail"] == "Содержимое файла не является PDF"

    uploaded = await auth_client.post(
        f"{API}/orders/{order_id}/document/upload",
        files={"file": ("narjad.pdf", b"%PDF-1.4\nvalid-test", "application/pdf")},
    )
    assert uploaded.status_code == 201, uploaded.text
    metadata = uploaded.json()
    assert metadata["source"] == "uploaded"
    assert metadata["filename"] == "narjad.pdf"
    assert metadata["content_type"] == "application/pdf"

    fetched = await auth_client.get(f"{API}/orders/{order_id}/document")
    assert fetched.status_code == 200
    assert fetched.json() == metadata

    content = await auth_client.get(f"{API}/orders/{order_id}/document/content")
    assert content.content == b"%PDF-1.4\nvalid-test"


async def test_document_cannot_be_replaced_after_completion(auth_client):
    client, vehicle, service = await _setup_refs(auth_client)
    order = (
        await auth_client.post(
            f"{API}/orders",
            json={
                "client_id": client["id"],
                "vehicle_id": vehicle["id"],
                "items": [{"item_type": "service", "service_id": service["id"]}],
            },
        )
    ).json()
    order_id = order["id"]
    await auth_client.patch(
        f"{API}/orders/{order_id}/status", json={"status": "in_progress"}
    )
    await auth_client.post(f"{API}/orders/{order_id}/document/generate")
    closed = await auth_client.patch(
        f"{API}/orders/{order_id}/status", json={"status": "done"}
    )
    assert closed.status_code == 200

    replace = await auth_client.post(f"{API}/orders/{order_id}/document/generate")
    assert replace.status_code == 422
    assert replace.json()["detail"] == (
        "Документ закрытого или отменённого заказа нельзя заменить"
    )


async def test_first_document_can_be_uploaded_to_completed_crm_order(auth_client):
    client, vehicle, _ = await _setup_refs(auth_client)
    order = (
        await auth_client.post(
            f"{API}/orders",
            json={"client_id": client["id"], "vehicle_id": vehicle["id"], "items": []},
        )
    ).json()
    completed = await auth_client.patch(
        f"{API}/crm/orders/{order['id']}/status",
        json={"status": "done"},
    )
    assert completed.status_code == 200, completed.text

    uploaded = await auth_client.post(
        f"{API}/orders/{order['id']}/documents/upload",
        files=[("files", ("result.png", b"\x89PNG\r\n\x1a\nscan", "image/png"))],
    )
    assert uploaded.status_code == 201, uploaded.text
    assert uploaded.json()[0]["filename"] == "result.png"

    replacement = await auth_client.post(
        f"{API}/orders/{order['id']}/document/generate"
    )
    assert replacement.status_code == 422


async def test_multiple_order_documents_list_download_archive_and_delete(auth_client):
    client, vehicle, service = await _setup_refs(auth_client)
    order = (
        await auth_client.post(
            f"{API}/orders",
            json={
                "client_id": client["id"],
                "vehicle_id": vehicle["id"],
                "items": [{"item_type": "service", "service_id": service["id"]}],
            },
        )
    ).json()
    order_id = order["id"]
    uploaded = await auth_client.post(
        f"{API}/orders/{order_id}/documents/upload",
        files=[
            ("files", ("first.pdf", b"%PDF-1.4\nfirst", "application/pdf")),
            ("files", ("second.html", b"<!doctype html><html>second</html>", "text/html")),
            ("files", ("photo.png", b"\x89PNG\r\n\x1a\nscan", "image/png")),
        ],
    )
    assert uploaded.status_code == 201, uploaded.text
    documents = uploaded.json()
    assert [item["filename"] for item in documents] == [
        "first.pdf",
        "second.html",
        "photo.png",
    ]

    listing = await auth_client.get(f"{API}/orders/{order_id}/documents")
    assert listing.status_code == 200, listing.text
    assert [item["id"] for item in listing.json()] == [item["id"] for item in documents]

    content = await auth_client.get(
        f"{API}/orders/{order_id}/documents/{documents[0]['id']}/content"
    )
    assert content.content == b"%PDF-1.4\nfirst"

    archive = await auth_client.get(f"{API}/orders/{order_id}/documents/archive")
    assert archive.status_code == 200, archive.text
    with ZipFile(BytesIO(archive.content)) as zipped:
        assert len(zipped.namelist()) == 3

    deleted = await auth_client.delete(
        f"{API}/orders/{order_id}/documents/{documents[0]['id']}"
    )
    assert deleted.status_code == 204, deleted.text
    remaining = await auth_client.get(f"{API}/orders/{order_id}/documents")
    assert [item["filename"] for item in remaining.json()] == ["second.html", "photo.png"]

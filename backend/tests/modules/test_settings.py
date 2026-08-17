"""Настройки организации и смена пароля администратора."""

from tests.conftest import API


async def test_settings_read_and_service_update(auth_client):
    response = await auth_client.get(f"{API}/settings")
    assert response.status_code == 200, response.text
    settings = response.json()
    assert settings["service"]["name"] == "КОМИТ Тест"
    assert settings["service"]["legalType"] == "ООО"
    assert settings["service"]["taxSystem"] == "УСН"
    assert settings["security"]["currentPassword"] == ""
    assert "hashed_password" not in response.text
    assert settings["security"]["sessions"][0]["current"] is True

    updated_response = await auth_client.put(
        f"{API}/settings",
        json={
            "service": {
                "name": "Движок Север",
                "headName": "Иванов Иван Иванович",
                "legalType": "ООО",
                "taxSystem": "НДС",
                "inn": "1234567890",
                "ogrn": "1027700132195",
                "bankAccount": "40702810123456789012",
                "phone": "+79991112233",
                "email": "service@example.com",
                "address": "Москва",
                "description": "Автосервис",
            }
        },
    )
    assert updated_response.status_code == 200, updated_response.text
    service = updated_response.json()["service"]
    assert service["name"] == "Движок Север"
    assert service["headName"] == "Иванов Иван Иванович"
    assert service["taxSystem"] == "НДС"
    assert service["email"] == "service@example.com"
    assert service["bankAccount"] == "40702810123456789012"


async def test_settings_service_accepts_blank_optional_fields(auth_client):
    response = await auth_client.put(
        f"{API}/settings",
        json={"service": {"email": "", "bankAccount": ""}},
    )
    assert response.status_code == 200, response.text
    service = response.json()["service"]
    # Организация без собственной почты продолжает показывать email владельца.
    assert service["email"] == "admin@komit.ru"
    assert service["bankAccount"] == ""


async def test_settings_logo_upload_validates_and_persists_image(auth_client):
    uploaded = await auth_client.post(
        f"{API}/settings/logo",
        files={"file": ("logo.png", b"\x89PNG\r\n\x1a\nlogo-data", "image/png")},
    )
    assert uploaded.status_code == 200, uploaded.text
    logo = uploaded.json()["service"]["logo"]
    assert logo.startswith("data:image/png;base64,")

    settings = await auth_client.get(f"{API}/settings")
    assert settings.status_code == 200
    assert settings.json()["service"]["logo"] == logo

    invalid = await auth_client.post(
        f"{API}/settings/logo",
        files={"file": ("logo.svg", b"<svg></svg>", "image/svg+xml")},
    )
    assert invalid.status_code == 422
    assert invalid.json()["detail"] == "Поддерживаются JPEG, PNG, WebP и GIF"


async def test_settings_password_change_verifies_old_password(auth_client, client):
    wrong = await auth_client.put(
        f"{API}/settings",
        json={
            "security": {
                "currentPassword": "new-admin-password",
                "oldPassword": "wrong-password",
                "code": "123456",
            }
        },
    )
    assert wrong.status_code == 401

    changed = await auth_client.put(
        f"{API}/settings",
        json={
            "security": {
                "currentPassword": "new-admin-password",
                "oldPassword": "admin12345",
                "code": "123456",
            }
        },
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["security"]["currentPassword"] == ""

    old_login = await client.post(
        f"{API}/auth/login",
        data={"username": "admin@komit.ru", "password": "admin12345"},
    )
    assert old_login.status_code == 401
    new_login = await client.post(
        f"{API}/auth/login",
        data={"username": "admin@komit.ru", "password": "new-admin-password"},
    )
    assert new_login.status_code == 200, new_login.text

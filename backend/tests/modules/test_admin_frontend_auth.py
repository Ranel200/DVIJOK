"""Совместимый auth-контракт готовой административной панели."""

import pytest

from tests.conftest import API


async def test_admin_frontend_json_login_and_logout(client, admin):
    response = await client.post(
        f"{API}/auth/login",
        json={"email": admin["email"], "password": admin["password"]},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token"] == body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["name"] == "Админ"
    assert body["user"]["full_name"] == "Админ"
    assert body["user"]["isOwner"] is True
    assert body["user"]["subscriptionPlan"] == "pro"

    logout = await client.post(
        f"{API}/auth/logout",
        headers={"Authorization": f"Bearer {body['token']}"},
    )
    assert logout.status_code == 200
    assert logout.json() == {"success": True}


async def test_admin_frontend_registration_facade(client):
    response = await client.post(
        f"{API}/auth/register",
        json={
            "name": "Автосервис Фронт",
            "headName": "Иванов Иван Иванович",
            "legalType": "ИП",
            "inn": "999999999999",
            "taxSystem": "УСН",
            "phone": "+79990000000",
            "email": "front-owner@example.com",
            "contactName": "Петров Пётр Петрович",
            "address": "Казань",
            "password": "secure-password",
            "passwordConfirm": "secure-password",
            "consent": True,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["token"] == body["access_token"]
    assert body["user"]["name"] == "Петров Пётр Петрович"
    assert body["user"]["isOwner"] is True
    assert body["user"]["subscriptionPlan"] == "none"

    tariffs = await client.get(f"{API}/tariffs")
    assert tariffs.status_code == 200, tariffs.text
    assert [item["id"] for item in tariffs.json()] == ["standard", "pro", "premium"]

    selected = await client.post(
        f"{API}/auth/subscription",
        json={"plan": "pro"},
        headers={"Authorization": f"Bearer {body['token']}"},
    )
    assert selected.status_code == 200, selected.text
    assert selected.json()["user"]["subscriptionPlan"] == "pro"

    settings = await client.get(
        f"{API}/settings",
        headers={"Authorization": f"Bearer {body['token']}"},
    )
    assert settings.status_code == 200, settings.text
    assert settings.json()["service"]["headName"] == "Иванов Иван Иванович"


@pytest.mark.parametrize("legal_type", ["ЗАО", "ПАО"])
async def test_registration_accepts_all_frontend_legal_forms_and_phone_login(client, legal_type):
    suffix = legal_type.lower()
    phone = "+7 (999) 100-20-30" if legal_type == "ЗАО" else "8 999 100-20-31"
    response = await client.post(
        f"{API}/auth/register",
        json={
            "name": f"Автосервис {legal_type}",
            "headName": "Иванов Иван Иванович",
            "legalType": legal_type,
            "inn": "9999999991" if legal_type == "ЗАО" else "9999999992",
            "taxSystem": "НДС",
            "phone": phone,
            "email": f"owner-{suffix}@example.com",
            "contactName": "Владелец Телефона",
            "address": "Москва",
            "password": "123456",
            "passwordConfirm": "123456",
            "consent": True,
        },
    )
    assert response.status_code == 201, response.text
    expected_phone = "+79991002030" if legal_type == "ЗАО" else "+79991002031"
    assert response.json()["user"]["phone"] == expected_phone

    login = await client.post(
        f"{API}/auth/login",
        json={"email": phone, "password": "123456"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["phone"] == expected_phone


async def test_login_error_is_compatible_with_frontend(client):
    response = await client.post(
        f"{API}/auth/login",
        json={"email": "+79990000000", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["message"] == response.json()["detail"]


async def test_refresh_cookie_rotation_and_logout_revocation(client, admin):
    login = await client.post(
        f"{API}/auth/login",
        json={"email": admin["email"], "password": admin["password"], "remember": True},
        headers={"user-agent": "Mozilla/5.0 Chrome/140.0"},
    )
    assert login.status_code == 200, login.text
    original_refresh = login.json()["refresh_token"]
    assert client.cookies.get("dvijok_refresh") == original_refresh

    refreshed = await client.post(f"{API}/auth/refresh")
    assert refreshed.status_code == 200, refreshed.text
    body = refreshed.json()
    assert body["token"] == body["access_token"]
    assert body["refresh_token"] != original_refresh
    assert client.cookies.get("dvijok_refresh") == body["refresh_token"]

    replay = await client.post(
        f"{API}/auth/refresh",
        json={"refresh_token": original_refresh},
    )
    assert replay.status_code == 401

    logout = await client.post(
        f"{API}/auth/logout",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert logout.status_code == 200, logout.text
    assert client.cookies.get("dvijok_refresh") is None

    revoked = await client.post(
        f"{API}/auth/refresh",
        json={"refresh_token": body["refresh_token"]},
    )
    assert revoked.status_code == 401

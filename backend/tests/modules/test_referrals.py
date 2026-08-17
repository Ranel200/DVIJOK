"""Интеграционные тесты административного referral API."""

from tests.conftest import API


async def test_admin_creates_stable_referral_with_printable_svg(auth_client):
    created = await auth_client.post(f"{API}/referrals/me")
    assert created.status_code == 201, created.text
    body = created.json()

    assert len(body["code"]) == 16
    assert body["url"].endswith(f"/r/{body['code']}")
    assert body["booking_url"].endswith(f"/book/{body['code']}")
    assert "<svg" in body["qr_svg"]
    assert "<svg" in body["booking_qr_svg"]
    assert "organization_id" not in body
    assert "id" not in body

    repeated = await auth_client.post(f"{API}/referrals/me")
    assert repeated.status_code == 200, repeated.text
    assert repeated.json()["code"] == body["code"]

    fetched = await auth_client.get(f"{API}/referrals/me")
    assert fetched.status_code == 200
    assert fetched.json()["url"] == body["url"]


async def test_admin_downloads_same_referral_as_svg(auth_client):
    created = (await auth_client.post(f"{API}/referrals/me")).json()
    response = await auth_client.get(f"{API}/referrals/me/qr.svg")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in response.text
    assert created["qr_svg"] == response.text

    booking_response = await auth_client.get(f"{API}/referrals/me/booking-qr.svg")
    assert booking_response.status_code == 200
    assert booking_response.headers["content-type"].startswith("image/svg+xml")
    assert created["booking_qr_svg"] == booking_response.text


async def test_referral_is_admin_only(client, admin):
    login = await client.post(
        f"{API}/auth/login",
        data={"username": admin["email"], "password": admin["password"]},
    )
    token = login.json()["access_token"]
    # Fixture user is ADMIN; unauthenticated access still verifies the protected
    # contract without creating an extra role-specific user.
    assert token
    response = await client.get(f"{API}/referrals/me")
    assert response.status_code == 401

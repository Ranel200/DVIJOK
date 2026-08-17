"""Run non-mutating checks against a deployed API from inside its container."""

from __future__ import annotations

import os

import httpx


def main() -> None:
    email = os.environ["FIRST_ADMIN_EMAIL"]
    password = os.environ["FIRST_ADMIN_PASSWORD"]

    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=30) as client:
        health = client.get("/health")
        health.raise_for_status()

        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password, "remember": False},
        )
        login.raise_for_status()
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        me = client.get("/api/v1/auth/me", headers=headers)
        me.raise_for_status()
        services = client.get(
            "/api/v1/services",
            headers=headers,
            params={"limit": 1, "offset": 0},
        )
        services.raise_for_status()

        print(
            "Deployment verification:",
            f"health={health.json().get('status')}",
            f"admin={me.json().get('email')}",
            f"services={services.json().get('total')}",
        )


if __name__ == "__main__":
    main()

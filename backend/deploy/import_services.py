"""Import a validated services workbook through the production HTTP API.

The script is intended to be copied into the API container.  Credentials are
read from the container environment, so they never have to be passed on the
command line.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()

    if not args.workbook.is_file():
        raise SystemExit(f"Workbook not found: {args.workbook}")

    email = os.environ["FIRST_ADMIN_EMAIL"]
    password = os.environ["FIRST_ADMIN_PASSWORD"]

    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=60) as client:
        login = client.post(
            "/auth/login",
            json={"email": email, "password": password, "remember": False},
        )
        login.raise_for_status()
        access_token = login.json()["access_token"]

        with args.workbook.open("rb") as workbook:
            imported = client.post(
                "/services/import",
                headers={"Authorization": f"Bearer {access_token}"},
                files={
                    "file": (
                        args.workbook.name,
                        workbook,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
            )

        if imported.status_code not in (200, 422):
            imported.raise_for_status()

        report = imported.json()
        print(
            "Service import:",
            f"valid={report.get('valid')}",
            f"total={report.get('total_rows')}",
            f"imported={report.get('imported_rows')}",
            f"errors={len(report.get('errors', []))}",
        )
        if not report.get("valid"):
            for error in report.get("errors", []):
                print(
                    f"row={error.get('row_number')}",
                    f"field={error.get('field')}",
                    f"message={error.get('message')}",
                )
            raise SystemExit(1)

        listing = client.get(
            "/services",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"limit": 1, "offset": 0},
        )
        listing.raise_for_status()
        print(f"Organization services total={listing.json()['total']}")


if __name__ == "__main__":
    main()

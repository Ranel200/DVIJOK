"""Idempotent employee accounts matching the admin frontend demo profiles.

Run after migrations with ``python -m scripts.seed_demo_staff``. By default the
script adds the employees to the organization owned by ``admin@komit.ru``;
``DEMO_STAFF_OWNER_EMAIL`` may point to another local owner account.
"""

import asyncio
import os
from decimal import Decimal

from sqlalchemy import select

import app.models  # noqa: F401
from app.core.database import async_session_factory, engine
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate
from app.modules.employees.service import EmployeeService
from app.modules.users.models import User
from app.shared.enums import UserRole

OWNER_EMAIL = os.getenv("DEMO_STAFF_OWNER_EMAIL", "admin@komit.ru").strip().lower()

STAFF = [
    {
        "login": "petrov",
        "name": "Петров Иван Сергеевич",
        "email": "petrov@dvijok.ru",
        "phone": "+79001112233",
        "role": UserRole.MECHANIC,
        "role_key": "senior_master",
        "color": "#43A047",
        "work_days": [1, 2, 3, 4, 5],
        "start": "09:00",
        "end": "18:00",
        "access": {"schedule": True},
    },
    {
        "login": "sidorov",
        "name": "Сидоров Алексей Николаевич",
        "email": "sidorov@dvijok.ru",
        "phone": "+79002223344",
        "role": UserRole.MANAGER,
        "role_key": "junior_admin",
        "color": "#FB8C00",
        "work_days": [1, 2, 3, 4, 5, 6],
        "start": "10:00",
        "end": "19:00",
        "access": {"schedule": True, "crm": True, "tasks": True},
    },
    {
        "login": "smirnov",
        "name": "Смирнов Дмитрий Олегович",
        "email": "smirnov@dvijok.ru",
        "phone": "+79003334455",
        "role": UserRole.ADMIN,
        "role_key": "senior_admin",
        "color": "#039BE5",
        "work_days": [1, 2, 3, 4, 5],
        "start": "08:00",
        "end": "17:00",
        "access": {
            "schedule": True,
            "crm": True,
            "services": True,
            "tasks": True,
            "qr": True,
        },
    },
    {
        "login": "morozova",
        "name": "Морозова Елена Сергеевна",
        "email": "morozova@dvijok.ru",
        "phone": "+79004445566",
        "role": UserRole.MANAGER,
        "role_key": "junior_admin",
        "color": "#F4511E",
        "work_days": [1, 2, 3, 4, 5],
        "start": "09:00",
        "end": "18:00",
        "access": {"crm": True, "services": True},
    },
    {
        "login": "sokolova",
        "name": "Соколова Ирина Алексеевна",
        "email": "sokolova@dvijok.ru",
        "phone": "+79005556677",
        "role": UserRole.ADMIN,
        "role_key": "senior_admin",
        "color": "#7B1FA2",
        "work_days": [1, 2, 3, 4, 5, 6],
        "start": "08:00",
        "end": "16:00",
        "access": {
            "schedule": True,
            "crm": True,
            "services": True,
            "tasks": True,
            "qr": True,
            "settings": True,
        },
    },
]

ACCESS_KEYS = ("schedule", "crm", "services", "tasks", "qr", "settings")


def complete_access(values: dict[str, bool]) -> dict[str, bool]:
    return {key: bool(values.get(key, False)) for key in ACCESS_KEYS}


def stored_intervals(item: dict) -> list[dict[str, str | int]]:
    return [
        {
            # JavaScript Sunday=0, Python Monday=0.
            "weekday": (weekday - 1) % 7,
            "start": item["start"],
            "end": item["end"],
        }
        for weekday in item["work_days"]
    ]


async def main() -> None:
    async with async_session_factory() as session:
        owner = (
            await session.execute(select(User).where(User.email == OWNER_EMAIL))
        ).scalar_one_or_none()
        if owner is None:
            raise RuntimeError(f"Владелец {OWNER_EMAIL} не найден; сначала запустите seed")

        employees = EmployeeService(session, owner.organization_id)
        for item in STAFF:
            existing = (
                await session.execute(select(User).where(User.login == item["login"]))
            ).scalar_one_or_none()
            common = {
                "email": item["email"],
                "login": item["login"],
                "password": item["login"],
                "full_name": item["name"],
                "phone": item["phone"],
                "role": item["role"],
                "staff_role_key": item["role_key"],
                "calendar_color": item["color"],
                "ui_permissions": complete_access(item["access"]),
            }
            if existing is None:
                created = await employees.create(
                    EmployeeCreate(
                        **common,
                        hourly_rate=Decimal(0),
                        commission_percent=Decimal(0),
                    )
                )
                user_id = created.id
                action = "создан"
            else:
                if existing.organization_id != owner.organization_id:
                    raise RuntimeError(
                        f"Логин {item['login']} уже занят в другой организации"
                    )
                updated = await employees.update(existing.id, EmployeeUpdate(**common))
                user_id = updated.id
                action = "обновлён"

            user = await session.get(User, user_id)
            assert user is not None
            user.is_owner = False
            user.is_active = True
            user.schedule_intervals = stored_intervals(item)
            user.schedule_breaks = []
            print(f"{item['login']}: {action}")

        await session.commit()
        print(f"Организация: {owner.organization_id}; владелец: {OWNER_EMAIL}")
        print("Пароль каждого демо-сотрудника совпадает с логином.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

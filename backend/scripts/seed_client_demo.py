"""Idempotent local data for checking the existing client frontend.

Run after migrations with ``python -m scripts.seed_client_demo``.  The OTP is
still requested through the real debug endpoint; this script does not create a
password or bypass client authentication.
"""

import asyncio
from decimal import Decimal

from sqlalchemy import select

import app.models  # noqa: F401
from app.core.database import async_session_factory, engine
from app.modules.client_auth.models import ClientAccount
from app.modules.clients.models import Client
from app.modules.mechanics.models import Mechanic
from app.modules.organizations.models import Organization
from app.modules.services.models import Service
from app.modules.vehicles.models import Vehicle
from app.shared.enums import OrganizationStatus, ServiceCategory

DEMO_CLIENT_PHONE = "+79991112233"
DEMO_CLIENT_NAME = "Иван Клиентский"
DEMO_VIN = "DVIZHOKCLIENT0001"


async def main() -> None:
    async with async_session_factory() as session:
        organization = (
            await session.execute(
                select(Organization)
                .where(
                    Organization.is_active.is_(True),
                    Organization.status != OrganizationStatus.SUSPENDED,
                )
                .order_by(Organization.id)
                .limit(1)
            )
        ).scalar_one_or_none()
        if organization is None:
            raise RuntimeError("Сначала создайте организацию через admin регистрацию/seed")

        account = (
            await session.execute(
                select(ClientAccount).where(ClientAccount.phone == DEMO_CLIENT_PHONE)
            )
        ).scalar_one_or_none()
        if account is None:
            account = ClientAccount(phone=DEMO_CLIENT_PHONE, full_name=DEMO_CLIENT_NAME)
            session.add(account)
            await session.flush()
        elif not account.full_name:
            account.full_name = DEMO_CLIENT_NAME

        client = (
            await session.execute(
                select(Client).where(
                    Client.organization_id == organization.id,
                    Client.client_account_id == account.id,
                )
            )
        ).scalar_one_or_none()
        if client is None:
            client = Client(
                organization_id=organization.id,
                client_account_id=account.id,
                full_name=DEMO_CLIENT_NAME,
                phone=DEMO_CLIENT_PHONE,
            )
            session.add(client)
            await session.flush()

        vehicle = (
            await session.execute(
                select(Vehicle).where(
                    Vehicle.organization_id == organization.id,
                    Vehicle.vin == DEMO_VIN,
                )
            )
        ).scalar_one_or_none()
        if vehicle is None:
            session.add(
                Vehicle(
                    organization_id=organization.id,
                    client_id=client.id,
                    make="Toyota",
                    model="Camry",
                    year=2020,
                    color="Белый",
                    license_plate="А123ВС116",
                    vin=DEMO_VIN,
                    mileage=50000,
                    next_service_mileage=60000,
                )
            )

        service = (
            await session.execute(
                select(Service)
                .where(
                    Service.organization_id == organization.id,
                    Service.is_active.is_(True),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if service is None:
            session.add(
                Service(
                    organization_id=organization.id,
                    name="Диагностика",
                    category=ServiceCategory.DIAGNOSTICS,
                    description="Комплексная диагностика автомобиля",
                    base_price=Decimal("1500.00"),
                    duration_minutes=60,
                )
            )

        mechanic = (
            await session.execute(
                select(Mechanic)
                .where(
                    Mechanic.organization_id == organization.id,
                    Mechanic.is_active.is_(True),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if mechanic is None:
            session.add(
                Mechanic(
                    organization_id=organization.id,
                    full_name="Иван Мастеров",
                )
            )

        await session.commit()
        print(f"Клиент: {DEMO_CLIENT_PHONE} ({DEMO_CLIENT_NAME})")
        print("OTP запросите через POST /api/v1/client-auth/otp/request")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

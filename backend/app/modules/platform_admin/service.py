"""Read models and controlled mutations for the creator console."""

from __future__ import annotations

import calendar
import datetime as dt
import secrets
from collections import Counter, defaultdict
from copy import deepcopy
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.modules.client_auth.models import ClientAccount
from app.modules.clients.models import Client
from app.modules.orders.models import Order
from app.modules.organizations.models import Organization
from app.modules.platform_admin.models import PlatformAdminState
from app.modules.platform_admin.schemas import (
    PlatformAdminStateUpdate,
    PlatformServiceCreate,
    PlatformServiceUpdate,
)
from app.modules.services.models import Service
from app.modules.users.models import User
from app.modules.vehicles.models import Vehicle
from app.shared.enums import (
    LegalForm,
    OrganizationStatus,
    OrderStatus,
    ServiceCategory,
    ServicePriceType,
    TaxSystem,
    UserRole,
)
from app.shared.identifiers import normalize_login, normalize_phone


class PlatformAdminService:
    """Backend-backed view model for the standalone creator HTML."""

    DEFAULT_STATE = {
        "plans": [
            {
                "key": "standard",
                "name": "Стандарт",
                "price": 5990,
                "description": "Для небольших автомастерских с одним сотрудником.",
                "features": ["CRM для клиентов и авто", "Календарь записей", "История ремонтов"],
                "featured": False,
            },
            {
                "key": "pro",
                "name": "Про",
                "price": 6990,
                "description": "Для автомастерских с двумя и больше сотрудниками.",
                "features": ["Неограниченное число сотрудников", "График работы мастеров", "Базовая аналитика"],
                "featured": True,
            },
            {
                "key": "premium",
                "name": "Премиум",
                "price": 7990,
                "description": "Для компаний с двумя и более автомастерскими.",
                "features": ["Несколько автомастерских", "Общая база", "Централизованное управление"],
                "featured": False,
            },
        ],
        "expenses": [],
        "leads": [],
        "employees": [],
        "settings": {
            "platform": "ДВИЖОК",
            "domain": "dvizhok.tech",
            "trial": "14 дней",
            "support": "support@dvizhok.tech",
        },
        "organization_notes": {},
    }

    STATUS_LABELS = {
        OrganizationStatus.ACTIVE: "Активна",
        OrganizationStatus.TRIAL: "Trial",
        OrganizationStatus.SUSPENDED: "Просрочена",
    }
    PLAN_LABELS = {"standard": "Стандарт", "pro": "Про", "premium": "Премиум"}

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _state_row(self) -> PlatformAdminState:
        row = await self.session.get(PlatformAdminState, 1)
        if row is None:
            row = PlatformAdminState(id=1, data=deepcopy(self.DEFAULT_STATE))
            self.session.add(row)
            await self.session.flush()
        data = dict(row.data or {})
        changed = False
        for key, value in self.DEFAULT_STATE.items():
            if key not in data:
                data[key] = deepcopy(value)
                changed = True
        if changed:
            row.data = data
            await self.session.flush()
        return row

    @staticmethod
    def _date_label(value: dt.date | dt.datetime | None) -> str:
        if value is None:
            return "—"
        if isinstance(value, dt.datetime):
            value = value.date()
        return value.strftime("%d.%m.%Y")

    @staticmethod
    def _city(address: str | None) -> str:
        if not address:
            return "—"
        first = address.split(",", 1)[0].strip()
        return first.removeprefix("г.").strip() or first

    async def _org_rows(self) -> list[dict]:
        organizations = list(
            (
                await self.session.execute(
                    select(Organization)
                    .where(Organization.is_active.is_(True))
                    .order_by(Organization.id)
                )
            )
            .scalars()
            .all()
        )
        if not organizations:
            return []
        org_ids = [org.id for org in organizations]
        user_counts = dict(
            (
                await self.session.execute(
                    select(User.organization_id, func.count(User.id))
                    .where(User.organization_id.in_(org_ids), User.is_active.is_(True))
                    .group_by(User.organization_id)
                )
            ).all()
        )
        client_counts = dict(
            (
                await self.session.execute(
                    select(Client.organization_id, func.count(Client.id))
                    .where(Client.organization_id.in_(org_ids), Client.is_active.is_(True))
                    .group_by(Client.organization_id)
                )
            ).all()
        )
        notes = (await self._state_row()).data.get("organization_notes", {})
        plans = {
            str(item.get("key", "")).lower(): item
            for item in (await self._state_row()).data.get("plans", [])
        }
        result: list[dict] = []
        for org in organizations:
            key = str(org.subscription_plan or "standard").lower()
            plan = plans.get(key) or plans.get("standard") or {}
            result.append(
                {
                    "id": f"STO-{org.id:04d}",
                    "organization_id": org.id,
                    "name": org.name,
                    "city": self._city(org.legal_address),
                    "plan": plan.get("name", self.PLAN_LABELS.get(key, key.title())),
                    "plan_key": key,
                    "price": float(plan.get("price") or 0),
                    "users": int(client_counts.get(org.id, 0)),
                    "staff": int(user_counts.get(org.id, 0)),
                    "status": self.STATUS_LABELS.get(org.status, str(org.status)),
                    "active": self._date_label(org.updated_at),
                    "created": self._date_label(org.created_at),
                    "email": org.email or "",
                    "note": notes.get(str(org.id), ""),
                    "subscription_until": self._date_label(org.subscription_until),
                }
            )
        return result

    async def _user_rows(self) -> list[dict]:
        accounts = list(
            (
                await self.session.execute(
                    select(ClientAccount).order_by(ClientAccount.id.desc())
                )
            )
            .scalars()
            .all()
        )
        if not accounts:
            return []
        account_ids = [account.id for account in accounts]
        rows = list(
            (
                await self.session.execute(
                    select(Client, Organization)
                    .join(Organization, Organization.id == Client.organization_id)
                    .where(Client.client_account_id.in_(account_ids))
                    .options(selectinload(Client.vehicles))
                )
            ).all()
        )
        grouped: dict[int, dict] = defaultdict(lambda: {"cars": [], "stos": []})
        for client, organization in rows:
            entry = grouped[client.client_account_id]
            if organization.name not in entry["stos"]:
                entry["stos"].append(organization.name)
            for vehicle in client.vehicles:
                label = " ".join(filter(None, [vehicle.make, vehicle.model])) or "Автомобиль"
                if vehicle.license_plate:
                    label += f" · {vehicle.license_plate}"
                if label not in entry["cars"]:
                    entry["cars"].append(label)
        return [
            {
                "id": f"USR-{account.id}",
                "cars": grouped[account.id]["cars"],
                "sto": ", ".join(grouped[account.id]["stos"]) or "—",
                "reg": self._date_label(account.created_at),
                "active": self._date_label(account.updated_at),
            }
            for account in accounts
        ]

    async def bootstrap(self) -> dict:
        state = (await self._state_row()).data
        services = await self._org_rows()
        users = await self._user_rows()
        plan_items = list(state.get("plans", []))
        plan_by_name = {str(p.get("name")): p for p in plan_items}
        subscriptions = [
            {
                "service": service["name"],
                "city": service["city"],
                "plan": service["plan"],
                "price": service["price"],
                "next": service["subscription_until"],
                "discount": 0,
                "status": service["status"],
            }
            for service in services
        ]
        now = dt.datetime.now(dt.UTC)
        month_start = dt.datetime(now.year, now.month, 1, tzinfo=dt.UTC)
        revenue_stmt = select(
            func.coalesce(func.sum(Order.total_amount), 0),
            func.count(Order.id),
        ).where(Order.status == OrderStatus.DONE, Order.completed_at >= month_start)
        revenue, completed_orders = (await self.session.execute(revenue_stmt)).one()
        revenue = Decimal(revenue or 0)
        mrr = sum(Decimal(str(item.get("price") or 0)) for item in services if item["status"] == "Активна")
        city_counts = Counter(item["city"] for item in services)
        plan_counts = Counter(item["plan"] for item in services)
        new_orgs = sum(
            1
            for item in services
            if item["created"] != "—" and item["created"].endswith(now.strftime(".%m.%Y"))
        )
        months = []
        growth = []
        revenue_series = []
        for offset in range(6, -1, -1):
            month_index = now.year * 12 + now.month - 1 - offset
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            label = calendar.month_abbr[month]
            start = dt.datetime(year, month, 1, tzinfo=dt.UTC)
            end = dt.datetime(year + (month == 12), 1 if month == 12 else month + 1, 1, tzinfo=dt.UTC)
            # Organization timestamps are stored without a timezone, while order
            # completion timestamps are timezone-aware. PostgreSQL does not mix
            # the two representations when binding query parameters.
            organization_start = start.replace(tzinfo=None)
            organization_end = end.replace(tzinfo=None)
            org_count = int(
                (
                    await self.session.execute(
                        select(func.count(Organization.id)).where(
                            Organization.created_at >= organization_start,
                            Organization.created_at < organization_end,
                        )
                    )
                ).scalar_one()
            )
            month_revenue = Decimal(
                (
                    await self.session.execute(
                        select(func.coalesce(func.sum(Order.total_amount), 0)).where(
                            Order.status == OrderStatus.DONE,
                            Order.completed_at >= start,
                            Order.completed_at < end,
                        )
                    )
                ).scalar_one()
                or 0
            )
            months.append(label)
            growth.append(org_count)
            revenue_series.append(float(month_revenue))
        dashboard = {
            "mrr": float(mrr),
            "revenue": float(revenue),
            "services": len(services),
            "arpu": float(mrr / len(services)) if services else 0,
            "new_services": new_orgs,
            "churned_services": sum(1 for item in services if item["status"] == "Просрочена"),
            "users": len(users),
            "cars": sum(len(item["cars"]) for item in users),
            "completed_orders": int(completed_orders or 0),
            "plan_counts": dict(plan_counts),
            "city_counts": dict(city_counts),
            "attention": {
                "overdue": sum(1 for item in services if item["status"] == "Просрочена"),
                "trial_soon": sum(1 for item in services if item["status"] == "Trial"),
                "failed_payments": 0,
                "inactive": 0,
                "errors": 0,
            },
            "months": months,
            "growth": growth,
            "revenue_series": revenue_series,
        }
        recent_orders = list(
            (
                await self.session.execute(
                    select(Order, Organization)
                    .join(Organization, Organization.id == Order.organization_id)
                    .where(Order.status == OrderStatus.DONE)
                    .order_by(Order.completed_at.desc())
                    .limit(20)
                )
            ).all()
        )
        return {
            "services": services,
            "users": users,
            "plans": plan_items,
            "subscriptions": subscriptions,
            "expenses": state.get("expenses", []),
            "leads": state.get("leads", []),
            "employees": state.get("employees", []),
            "settings": state.get("settings", {}),
            "dashboard": dashboard,
            "finance": {
                "recent_orders": [
                    {
                        "date": self._date_label(order.completed_at),
                        "service": organization.name,
                        "number": order.number,
                        "amount": float(order.total_amount or 0),
                    }
                    for order, organization in recent_orders
                ]
            },
            "system": {
                "api": "ok",
                "database": "ok",
                "server": "managed",
                "payments": "not_configured",
                "auth": "ok",
                "notifications": "configured" if settings.NOTIFICATIONS_ENABLED else "disabled",
                "audit": [],
            },
        }

    async def update_state(self, payload: PlatformAdminStateUpdate) -> dict:
        row = await self._state_row()
        data = dict(row.data or {})
        # ``PlatformPlan.price``/``PlatformExpense.amount`` are Decimal values;
        # store the JSON-safe representation in the JSON column.
        for key, value in payload.model_dump(mode="json", exclude_unset=True).items():
            if value is not None:
                data[key] = value
        row.data = data
        await self.session.flush()
        return await self.bootstrap()

    @staticmethod
    def _org_id(display_id: str) -> int:
        try:
            return int(display_id.removeprefix("STO-"))
        except ValueError as exc:
            raise NotFoundError("Неверный идентификатор автосервиса") from exc

    async def update_organization(self, display_id: str, payload: PlatformServiceUpdate) -> dict:
        organization = await self.session.get(Organization, self._org_id(display_id))
        if organization is None:
            raise NotFoundError("Автосервис не найден")
        values = payload.model_dump(exclude_unset=True)
        if "name" in values:
            organization.name = values["name"]
        if "city" in values and values["city"]:
            organization.legal_address = f"г. {values['city']}"
        if "email" in values:
            organization.email = values["email"] or None
        if "plan" in values and values["plan"]:
            plans = (await self._state_row()).data.get("plans", [])
            plan_key = next(
                (str(item.get("key")) for item in plans if item.get("name") == values["plan"]),
                str(values["plan"]).lower(),
            )
            organization.subscription_plan = plan_key.upper()
        if "status" in values and values["status"]:
            status = values["status"]
            organization.status = {
                "Активна": OrganizationStatus.ACTIVE,
                "Trial": OrganizationStatus.TRIAL,
                "Просрочена": OrganizationStatus.SUSPENDED,
            }.get(status, OrganizationStatus.ACTIVE)
        if "is_active" in values and values["is_active"] is not None:
            organization.is_active = values["is_active"]
            if not values["is_active"]:
                organization.status = OrganizationStatus.SUSPENDED
        if "note" in values:
            row = await self._state_row()
            data = dict(row.data or {})
            notes = dict(data.get("organization_notes", {}))
            notes[str(organization.id)] = values["note"] or ""
            data["organization_notes"] = notes
            row.data = data
        await self.session.flush()
        return await self.bootstrap()

    async def create_organization(self, payload: PlatformServiceCreate) -> dict:
        owner_email = str(payload.owner_email).strip().lower()
        owner_login = normalize_login(payload.owner_login)
        owner_phone = normalize_phone(payload.phone)
        if owner_phone is None:
            raise BusinessRuleError("Некорректный номер телефона владельца")
        credentials_taken = (
            await self.session.execute(
                select(User.id).where(
                    (User.email == owner_email)
                    | (User.login == owner_login)
                    | (User.normalized_phone == owner_phone)
                )
            )
        ).scalar_one_or_none()
        if credentials_taken is not None:
            raise ConflictError("Email, логин или номер владельца уже используются")
        inn = payload.inn
        if not inn:
            while True:
                # Keep generated INN numeric; token_hex may contain a-f.
                inn = str(900000000000 + secrets.randbelow(99999999999))
                if (await self.session.execute(select(Organization.id).where(Organization.inn == inn))).scalar_one_or_none() is None:
                    break
        if (await self.session.execute(select(Organization.id).where(Organization.inn == inn))).scalar_one_or_none() is not None:
            raise ConflictError("Организация с таким ИНН уже существует")
        plans = (await self._state_row()).data.get("plans", [])
        plan_key = next(
            (str(item.get("key")) for item in plans if item.get("name") == payload.plan),
            payload.plan.lower(),
        )
        organization = Organization(
            name=payload.name,
            inn=inn,
            tax_system=TaxSystem.USN,
            legal_form=LegalForm.OOO,
            legal_address=f"г. {payload.city}" if payload.city else "Не указан",
            phone=owner_phone,
            email=payload.email or None,
            head_name=payload.name,
            subscription_plan=plan_key.upper(),
            status=OrganizationStatus.TRIAL,
        )
        self.session.add(organization)
        await self.session.flush()
        # The creator console creates a real tenant owner account using the
        # credentials supplied in its form.  No generated credentials are lost.
        self.session.add(
            User(
                organization_id=organization.id,
                email=owner_email,
                phone=owner_phone,
                normalized_phone=owner_phone,
                login=owner_login,
                full_name=payload.owner_name,
                role=UserRole.ADMIN,
                staff_role_key="senior_admin",
                is_owner=True,
                hashed_password=hash_password(payload.owner_password),
            )
        )
        self.session.add_all(
            [
                Service(
                    organization_id=organization.id,
                    name="Диагностика",
                    public_booking_key="diagnostics",
                    category=ServiceCategory.DIAGNOSTICS,
                    admin_category="diagnostics",
                    price_type=ServicePriceType.NEGOTIABLE,
                    duration_minutes=60,
                ),
                Service(
                    organization_id=organization.id,
                    name="Ремонт",
                    public_booking_key="repair",
                    category=ServiceCategory.OTHER,
                    admin_category="repair",
                    price_type=ServicePriceType.NEGOTIABLE,
                    duration_minutes=60,
                ),
            ]
        )
        await self.session.flush()
        return await self.bootstrap()

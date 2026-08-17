"""Агрегатор моделей.

Импортирует все ORM-классы, чтобы они зарегистрировались в Base.metadata до
конфигурации мапперов (нужно для разрешения строковых relationship и для
Alembic autogenerate). Импортировать этот модуль в alembic/env.py и app/main.py.
"""

from app.modules.auth.models import StaffLoginEvent, StaffRefreshSession
from app.modules.client_auth.models import ClientAccount, ClientRefreshSession
from app.modules.client_vehicles.models import ClientVehicle
from app.modules.clients.models import Client
from app.modules.employees.models import EmployeeDocument
from app.modules.inventory.models import InventoryItem, StockMovement
from app.modules.mechanics.models import Mechanic
from app.modules.notifications.models import (
    ClientMessengerBinding,
    ClientMessengerLinkToken,
    NotificationDelivery,
)
from app.modules.orders.models import Order, OrderDocument, OrderItem
from app.modules.organizations.models import Organization
from app.modules.referrals.models import OrganizationReferral
from app.modules.schedule.models import MechanicBlock, MechanicWorkingHours, ScheduleSlot
from app.modules.services.models import Service
from app.modules.tasks.models import Task
from app.modules.users.models import User
from app.modules.vehicles.models import Vehicle
from app.shared.base_model import Base

__all__ = [
    "Base",
    "Organization",
    "OrganizationReferral",
    "StaffRefreshSession",
    "StaffLoginEvent",
    "User",
    "ClientAccount",
    "ClientRefreshSession",
    "ClientVehicle",
    "EmployeeDocument",
    "Mechanic",
    "ClientMessengerBinding",
    "ClientMessengerLinkToken",
    "NotificationDelivery",
    "Client",
    "Vehicle",
    "Service",
    "Order",
    "OrderItem",
    "OrderDocument",
    "ScheduleSlot",
    "MechanicBlock",
    "MechanicWorkingHours",
    "InventoryItem",
    "StockMovement",
    "Task",
]

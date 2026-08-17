"""Перечисления домена. Все enum строковые (str) — стабильны в БД и API.

Цвета бейджей/типов работ из ТЗ вынесены в значения комментариями.
"""

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MECHANIC = "mechanic"


class OrderStatus(str, enum.Enum):
    NEW = "new"  # Новый        — фиолетовый
    PRIMARY = "primary"  # Первичная запись
    DIAGNOSTICS = "diagnostics"  # Диагностика
    APPROVAL = "approval"  # Согласование в CRM
    SECONDARY = "secondary"  # Вторичная запись
    WAITING = "waiting"  # Ожидание     — синий
    IN_PROGRESS = "in_progress"  # В работе     — оранжевый
    AGREEMENT = "agreement"  # Согласование — жёлтый
    DONE = "done"  # Готово       — зелёный
    CANCELLED = "cancelled"  # Отменён      — серый


class OrderSource(str, enum.Enum):
    """Канал, из которого организация получила заказ."""

    CALL = "call"
    WEBSITE = "website"
    AVITO = "avito"
    REFERRAL = "referral"
    WALK_IN = "walk_in"
    OTHER = "other"


class TaxSystem(str, enum.Enum):
    USN = "usn"
    NDS = "nds"


class LegalForm(str, enum.Enum):
    IP = "ip"
    OOO = "ooo"
    OAO = "oao"
    ZAO = "zao"
    PAO = "pao"


class OrganizationStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"


class ClientType(str, enum.Enum):
    NEW = "new"  # Новый   — фиолетовый
    ACTIVE = "active"  # Активный — оранжевый
    VIP = "vip"  # VIP     — зелёный


class ServiceCategory(str, enum.Enum):
    """Категории услуг — используются и для цветовой кодировки расписания (ТЗ A4)."""

    TO = "to"  # ТО          — синий
    CHASSIS = "chassis"  # Ходовая     — красный
    DIAGNOSTICS = "diagnostics"  # Диагностика — жёлтый
    OIL = "oil"  # Масло       — зелёный
    TIRES = "tires"  # Шины        — голубой
    AC = "ac"  # Кондиционер — оранжевый
    BODY = "body"  # Кузов       — розовый
    ELECTRICAL = "electrical"  # Электрика
    OTHER = "other"  # Прочее


class ServicePriceType(str, enum.Enum):
    FIXED = "fixed"
    RANGE = "range"
    NEGOTIABLE = "negotiable"


class TaskStatus(str, enum.Enum):
    NEW = "new"
    HOT = "hot"
    BURNED = "burned"
    DONE = "done"


class OrderItemType(str, enum.Enum):
    SERVICE = "service"  # работа/услуга из каталога
    PART = "part"  # запчасть со склада


class OrderDocumentSource(str, enum.Enum):
    GENERATED = "generated"
    UPLOADED = "uploaded"


class InventoryCategory(str, enum.Enum):
    OILS = "oils"  # Масла
    BRAKES = "brakes"  # Тормоза
    FILTERS = "filters"  # Фильтры
    IGNITION = "ignition"  # Зажигание
    FLUIDS = "fluids"  # Жидкости
    OTHER = "other"


class StockStatus(str, enum.Enum):
    """Вычисляемый статус остатка (ТЗ A8)."""

    CRITICAL = "critical"  # красный
    LOW = "low"  # жёлтый
    NORMAL = "normal"  # зелёный


class MovementType(str, enum.Enum):
    IN = "in"  # приход
    OUT = "out"  # расход
    RETURN = "return"  # возврат
    WRITE_OFF = "write_off"  # списание под заказ-наряд


class NotificationChannel(str, enum.Enum):
    TELEGRAM = "telegram"
    VK = "vk"
    MAX = "max"


class NotificationEventType(str, enum.Enum):
    BOOKING_CREATED = "booking_created"  # "Вы записаны"
    STATUS_IN_PROGRESS = "status_in_progress"  # "Ваша машина в процессе"
    STATUS_AGREEMENT = "status_agreement"  # "Нуждается в согласовании"
    STATUS_DONE = "status_done"  # "Готово"
    STATUS_CANCELLED = "status_cancelled"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

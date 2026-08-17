"""Stable admin-UI positions mapped to backend authorization roles."""

from app.shared.enums import UserRole

STAFF_ROLE_TO_TECHNICAL = {
    "senior_admin": UserRole.ADMIN,
    "junior_admin": UserRole.MANAGER,
    "senior_master": UserRole.MECHANIC,
    "junior_master": UserRole.MECHANIC,
}

DEFAULT_STAFF_ROLE = {
    UserRole.ADMIN: "senior_admin",
    UserRole.MANAGER: "junior_admin",
    UserRole.MECHANIC: "senior_master",
}

STAFF_ROLE_LABELS = {
    "senior_admin": "Старший администратор",
    "junior_admin": "Младший администратор",
    "senior_master": "Старший мастер",
    "junior_master": "Младший мастер",
}


def default_staff_role(role: UserRole) -> str:
    return DEFAULT_STAFF_ROLE[role]


def technical_role(staff_role_key: str) -> UserRole:
    return STAFF_ROLE_TO_TECHNICAL[staff_role_key]


def staff_role_label(staff_role_key: str) -> str:
    return STAFF_ROLE_LABELS[staff_role_key]

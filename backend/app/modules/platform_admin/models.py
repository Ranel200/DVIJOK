"""Persisted state owned by the platform creator console.

Business entities (organizations, clients, orders and vehicles) are read from
their canonical tables.  This small JSON document is only for platform-level
concepts that do not yet have a tenant-domain model (plans, leads, internal
expenses and creator-console settings).
"""

from typing import Any

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, IntPKMixin, TimestampMixin


class PlatformAdminState(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "platform_admin_states"

    # Singleton row (id=1) is created lazily by the service on first use.
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

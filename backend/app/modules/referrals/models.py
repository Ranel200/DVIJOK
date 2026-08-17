"""Постоянный публичный реферальный код автосервиса."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, IntPKMixin, TimestampMixin


class OrganizationReferral(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "organization_referrals"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, index=True
    )
    # Код публичен, но непрозрачен: не содержит внутренних ID и не является
    # аутентификационным секретом. 16 url-safe символов дают 96 бит энтропии.
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)

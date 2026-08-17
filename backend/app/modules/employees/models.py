"""Private personnel documents belonging to an organization employee."""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, IntPKMixin, TimestampMixin


class EmployeeDocument(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "employee_documents"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(30))
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(String(64))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    __table_args__ = (
        UniqueConstraint("user_id", "kind", name="uq_employee_documents_user_kind"),
        CheckConstraint("size_bytes > 0", name="ck_employee_documents_size_positive"),
    )

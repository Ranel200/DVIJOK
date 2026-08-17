"""Allow staff accounts without email.

Revision ID: f8e2a4c6b0d1
Revises: f7d9e1a3b5c7
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f8e2a4c6b0d1"
down_revision: str | None = "f7d9e1a3b5c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        nullable=True,
    )


def downgrade() -> None:
    # Downgrade сохраняет созданные login-only аккаунты и восстанавливает
    # прежнее NOT NULL ограничение с уникальными техническими адресами.
    op.execute("UPDATE users SET email = 'staff-' || id || '@invalid.local' WHERE email IS NULL")
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        nullable=False,
    )

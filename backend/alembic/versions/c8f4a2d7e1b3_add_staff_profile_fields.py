"""add staff profile fields for admin calendar

Revision ID: c8f4a2d7e1b3
Revises: b6e1c4a2d9f0
Create Date: 2026-08-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c8f4a2d7e1b3"
down_revision: str | None = "b6e1c4a2d9f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "calendar_color",
            sa.String(length=7),
            server_default="#5C6BC0",
            nullable=False,
        ),
    )
    op.add_column("users", sa.Column("duties", sa.Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "ui_permissions",
            sa.JSON(),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
    )
    op.alter_column("users", "calendar_color", server_default=None)
    op.alter_column("users", "ui_permissions", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "ui_permissions")
    op.drop_column("users", "duties")
    op.drop_column("users", "calendar_color")

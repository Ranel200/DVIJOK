"""add recurring schedules for every staff member

Revision ID: e3a7b2d9c5f1
Revises: e2f6a1c8d4b0
Create Date: 2026-08-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e3a7b2d9c5f1"
down_revision: str | None = "e2f6a1c8d4b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "schedule_intervals",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "schedule_breaks",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )
    op.alter_column("users", "schedule_intervals", server_default=None)
    op.alter_column("users", "schedule_breaks", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "schedule_breaks")
    op.drop_column("users", "schedule_intervals")

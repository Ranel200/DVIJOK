"""add staff document metadata and recurring mechanic breaks

Revision ID: d5a2e7c9b4f3
Revises: d4f1c6b8a3e2
Create Date: 2026-08-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d5a2e7c9b4f3"
down_revision: str | None = "d4f1c6b8a3e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "documents",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )
    op.alter_column("users", "documents", server_default=None)
    op.add_column(
        "mechanics",
        sa.Column(
            "schedule_breaks",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )
    op.alter_column("mechanics", "schedule_breaks", server_default=None)


def downgrade() -> None:
    op.drop_column("mechanics", "schedule_breaks")
    op.drop_column("users", "documents")

"""Add persisted state for the creator/platform admin console.

Revision ID: fd7c9e1a2b3c
Revises: fc6a8b0d2e4f
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "fd7c9e1a2b3c"
down_revision: str | None = "fc6a8b0d2e4f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "platform_admin_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("platform_admin_states")

"""Add organization bank account for admin service settings.

Revision ID: fa4c6e8b0d2f
Revises: f9a3b5c7d1e2
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "fa4c6e8b0d2f"
down_revision: str | None = "f9a3b5c7d1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("bank_account", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "bank_account")

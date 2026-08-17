"""add administrative settings fields

Revision ID: d4f1c6b8a3e2
Revises: d3e9b5a2c7f1
Create Date: 2026-08-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d4f1c6b8a3e2"
down_revision: str | None = "d3e9b5a2c7f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("head_name", sa.String(length=255), nullable=True))
    op.add_column("organizations", sa.Column("ogrn", sa.String(length=15), nullable=True))
    op.add_column("organizations", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("organizations", sa.Column("logo", sa.Text(), nullable=True))
    op.add_column("organizations", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "organizations",
        sa.Column(
            "subscription_plan",
            sa.String(length=50),
            nullable=False,
            server_default="PRO",
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("subscription_started_at", sa.Date(), nullable=True),
    )
    op.alter_column("organizations", "subscription_plan", server_default=None)
    op.add_column(
        "users",
        sa.Column(
            "password_changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "password_changed_at")
    op.drop_column("organizations", "subscription_started_at")
    op.drop_column("organizations", "subscription_plan")
    op.drop_column("organizations", "description")
    op.drop_column("organizations", "logo")
    op.drop_column("organizations", "email")
    op.drop_column("organizations", "ogrn")
    op.drop_column("organizations", "head_name")

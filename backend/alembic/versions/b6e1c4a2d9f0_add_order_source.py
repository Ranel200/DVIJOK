"""add order acquisition source

Revision ID: b6e1c4a2d9f0
Revises: 9c4f2a8e1d70
Create Date: 2026-08-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b6e1c4a2d9f0"
down_revision: str | None = "9c4f2a8e1d70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column(
            "source",
            sa.Enum(
                "CALL",
                "WEBSITE",
                "AVITO",
                "REFERRAL",
                "WALK_IN",
                "OTHER",
                name="ordersource",
                native_enum=False,
                length=20,
            ),
            server_default="OTHER",
            nullable=False,
        ),
    )
    op.alter_column("orders", "source", server_default=None)
    op.create_index("ix_orders_source", "orders", ["source"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_orders_source", table_name="orders")
    op.drop_column("orders", "source")

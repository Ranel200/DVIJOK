"""add CRM order line assignment and discount fields

Revision ID: d2c8a4f1b6e9
Revises: d1a7f3c9e5b2
Create Date: 2026-08-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d2c8a4f1b6e9"
down_revision: str | None = "d1a7f3c9e5b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "order_items",
        sa.Column(
            "discount_percent",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "order_items",
        sa.Column("mechanic_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_order_items_mechanic_id_mechanics",
        "order_items",
        "mechanics",
        ["mechanic_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_order_items_mechanic_id",
        "order_items",
        ["mechanic_id"],
        unique=False,
    )
    op.alter_column("order_items", "discount_percent", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_order_items_mechanic_id", table_name="order_items")
    op.drop_constraint(
        "fk_order_items_mechanic_id_mechanics",
        "order_items",
        type_="foreignkey",
    )
    op.drop_column("order_items", "mechanic_id")
    op.drop_column("order_items", "discount_percent")

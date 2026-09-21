"""Add persistent CRM markers and per-employee schedule slot step.

Revision ID: fe8a0c2d4b6e
Revises: fd7c9e1a2b3c
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "fe8a0c2d4b6e"
down_revision: str | None = "fd7c9e1a2b3c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "order_markers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_order_markers_org_name"),
    )
    op.create_index("ix_order_markers_organization_id", "order_markers", ["organization_id"])
    op.add_column("orders", sa.Column("marker_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_orders_marker_id_order_markers",
        "orders",
        "order_markers",
        ["marker_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_orders_marker_id", "orders", ["marker_id"])
    op.add_column(
        "users",
        sa.Column("schedule_slot_step", sa.Integer(), server_default="60", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "schedule_slot_step")
    op.drop_index("ix_orders_marker_id", table_name="orders")
    op.drop_constraint("fk_orders_marker_id_order_markers", "orders", type_="foreignkey")
    op.drop_column("orders", "marker_id")
    op.drop_index("ix_order_markers_organization_id", table_name="order_markers")
    op.drop_table("order_markers")

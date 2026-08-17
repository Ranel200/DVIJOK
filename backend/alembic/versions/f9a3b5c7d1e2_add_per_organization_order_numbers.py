"""Add per-organization order numbering.

Revision ID: f9a3b5c7d1e2
Revises: f8e2a4c6b0d1
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f9a3b5c7d1e2"
down_revision: str | None = "f8e2a4c6b0d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _orders_table() -> sa.TableClause:
    return sa.table(
        "orders",
        sa.column("id", sa.Integer()),
        sa.column("organization_id", sa.Integer()),
        sa.column("number", sa.String(length=20)),
        sa.column("created_at", sa.DateTime()),
    )


def _organizations_table() -> sa.TableClause:
    return sa.table(
        "organizations",
        sa.column("id", sa.Integer()),
        sa.column("next_order_number", sa.Integer()),
    )


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "next_order_number",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
    )
    op.drop_index("ix_orders_number", table_name="orders")
    op.create_index("ix_orders_number", "orders", ["number"], unique=False)

    bind = op.get_bind()
    orders = _orders_table()
    counters: dict[int, int] = {}
    rows = bind.execute(
        sa.select(orders.c.id, orders.c.organization_id).order_by(
            orders.c.organization_id,
            orders.c.created_at,
            orders.c.id,
        )
    )
    for row in rows:
        organization_id = int(row.organization_id)
        number = counters.get(organization_id, 0) + 1
        counters[organization_id] = number
        bind.execute(sa.update(orders).where(orders.c.id == row.id).values(number=str(number)))

    organizations = _organizations_table()
    for organization_id, last_number in counters.items():
        bind.execute(
            sa.update(organizations)
            .where(organizations.c.id == organization_id)
            .values(next_order_number=last_number + 1)
        )

    op.create_unique_constraint(
        "uq_orders_organization_number",
        "orders",
        ["organization_id", "number"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_orders_organization_number",
        "orders",
        type_="unique",
    )
    op.drop_index("ix_orders_number", table_name="orders")

    bind = op.get_bind()
    orders = _orders_table()
    rows = bind.execute(sa.select(orders.c.id).order_by(orders.c.id))
    for row in rows:
        bind.execute(
            sa.update(orders).where(orders.c.id == row.id).values(number=str(4830 + int(row.id)))
        )

    op.create_index("ix_orders_number", "orders", ["number"], unique=True)
    op.drop_column("organizations", "next_order_number")

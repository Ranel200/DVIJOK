"""Reconcile per-organization order number counters.

Revision ID: fb5d7e9a1c3f
Revises: f9a3b5c7d1e2, fa4c6e8b0d2f
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "fb5d7e9a1c3f"
down_revision: tuple[str, str] = ("f9a3b5c7d1e2", "fa4c6e8b0d2f")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ``number`` is populated as a decimal string by the preceding migration.
    # Keep a counter ahead of both its current value and all persisted orders.
    op.execute(
        sa.text(
            """
            UPDATE organizations AS organization
            SET next_order_number = GREATEST(
                organization.next_order_number,
                COALESCE(numbers.last_number, 0) + 1
            )
            FROM (
                SELECT organization_id, MAX(number::integer) AS last_number
                FROM orders
                GROUP BY organization_id
            ) AS numbers
            WHERE organization.id = numbers.organization_id
            """
        )
    )


def downgrade() -> None:
    # Counter repair is intentionally forward-only: lowering it could recreate
    # the unique-number collision this migration removes.
    pass

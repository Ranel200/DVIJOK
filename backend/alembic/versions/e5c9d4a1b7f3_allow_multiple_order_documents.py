"""allow multiple documents per order

Revision ID: e5c9d4a1b7f3
Revises: e4b8c3d0a6f2
Create Date: 2026-08-06
"""

from collections.abc import Sequence

from alembic import op

revision: str = "e5c9d4a1b7f3"
down_revision: str | None = "e4b8c3d0a6f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_order_documents_order_id",
        "order_documents",
        type_="unique",
    )
    op.create_index(
        "ix_order_documents_order_id",
        "order_documents",
        ["order_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_order_documents_order_id", table_name="order_documents")
    op.create_unique_constraint(
        "uq_order_documents_order_id",
        "order_documents",
        ["order_id"],
    )

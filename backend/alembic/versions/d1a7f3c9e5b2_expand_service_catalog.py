"""expand service catalog for admin UI

Revision ID: d1a7f3c9e5b2
Revises: c8f4a2d7e1b3
Create Date: 2026-08-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d1a7f3c9e5b2"
down_revision: str | None = "c8f4a2d7e1b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "services",
        sa.Column(
            "price_type",
            sa.Enum(
                "FIXED",
                "RANGE",
                "NEGOTIABLE",
                name="servicepricetype",
                native_enum=False,
                length=20,
            ),
            server_default="FIXED",
            nullable=False,
        ),
    )
    op.add_column("services", sa.Column("price_to", sa.Numeric(10, 2), nullable=True))
    op.add_column("services", sa.Column("internal_notes", sa.Text(), nullable=True))
    op.alter_column("services", "price_type", server_default=None)
    op.create_table(
        "service_mechanics",
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("mechanic_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mechanic_id"], ["mechanics.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("service_id", "mechanic_id", name="uq_service_mechanics_pair"),
    )


def downgrade() -> None:
    op.drop_table("service_mechanics")
    op.drop_column("services", "internal_notes")
    op.drop_column("services", "price_to")
    op.drop_column("services", "price_type")

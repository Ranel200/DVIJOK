"""preserve categories selected by the admin frontend

Revision ID: e4b8c3d0a6f2
Revises: e3a7b2d9c5f1
Create Date: 2026-08-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e4b8c3d0a6f2"
down_revision: str | None = "e3a7b2d9c5f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "services",
        sa.Column(
            "admin_category",
            sa.String(length=20),
            nullable=False,
            server_default="other",
        ),
    )
    op.execute(
        sa.text(
            """
            UPDATE services
            SET admin_category = CASE
                WHEN category IN ('TO', 'to') THEN 'maintenance'
                WHEN category IN ('DIAGNOSTICS', 'diagnostics') THEN 'diagnostics'
                WHEN category IN ('BODY', 'body') THEN 'body'
                WHEN category IN ('OTHER', 'other') THEN 'other'
                ELSE 'repair'
            END
            """
        )
    )
    op.alter_column("services", "admin_category", server_default=None)
    op.create_index("ix_services_admin_category", "services", ["admin_category"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_services_admin_category", table_name="services")
    op.drop_column("services", "admin_category")

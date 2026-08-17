"""remove placeholder prices from client booking choices

Revision ID: f7d9e1a3b5c7
Revises: f6c8d0e2a4b6
Create Date: 2026-08-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f7d9e1a3b5c7"
down_revision: str | None = "f6c8d0e2a4b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE services
            SET base_price = 0,
                price_type = 'NEGOTIABLE'
            WHERE public_booking_key IN ('diagnostics', 'repair')
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE services
            SET base_price = CASE public_booking_key
                    WHEN 'diagnostics' THEN 2500.00
                    WHEN 'repair' THEN 5000.00
                END,
                price_type = 'FIXED'
            WHERE public_booking_key IN ('diagnostics', 'repair')
            """
        )
    )

"""add stable client booking services

Revision ID: f6c8d0e2a4b6
Revises: f5b7c9d1e3a5
Create Date: 2026-08-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f6c8d0e2a4b6"
down_revision: str | None = "f5b7c9d1e3a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "services",
        sa.Column("public_booking_key", sa.String(length=20), nullable=True),
    )
    op.create_unique_constraint(
        "uq_services_organization_public_booking_key",
        "services",
        ["organization_id", "public_booking_key"],
    )

    # Match the two stable values used by the client frontend. Existing
    # detailed services remain untouched and visible in the admin catalog.
    op.execute(
        sa.text(
            """
            INSERT INTO services (
                organization_id,
                name,
                public_booking_key,
                category,
                admin_category,
                description,
                base_price,
                price_type,
                price_to,
                internal_notes,
                labor_hours,
                duration_minutes,
                is_active
            )
            SELECT
                organizations.id,
                'Диагностика',
                'diagnostics',
                'DIAGNOSTICS',
                'diagnostics',
                NULL,
                2500.00,
                'FIXED',
                NULL,
                NULL,
                0,
                60,
                TRUE
            FROM organizations
            WHERE NOT EXISTS (
                SELECT 1
                FROM services
                WHERE services.organization_id = organizations.id
                  AND services.public_booking_key = 'diagnostics'
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO services (
                organization_id,
                name,
                public_booking_key,
                category,
                admin_category,
                description,
                base_price,
                price_type,
                price_to,
                internal_notes,
                labor_hours,
                duration_minutes,
                is_active
            )
            SELECT
                organizations.id,
                'Ремонт',
                'repair',
                'OTHER',
                'repair',
                NULL,
                5000.00,
                'FIXED',
                NULL,
                NULL,
                0,
                60,
                TRUE
            FROM organizations
            WHERE NOT EXISTS (
                SELECT 1
                FROM services
                WHERE services.organization_id = organizations.id
                  AND services.public_booking_key = 'repair'
            )
            """
        )
    )


def downgrade() -> None:
    # Keep the two ordinary service rows to avoid deleting order history.
    op.drop_constraint(
        "uq_services_organization_public_booking_key",
        "services",
        type_="unique",
    )
    op.drop_column("services", "public_booking_key")

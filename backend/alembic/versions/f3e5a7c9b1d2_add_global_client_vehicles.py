"""add global client vehicles

Revision ID: f3e5a7c9b1d2
Revises: f2d4e6a8b0c1
Create Date: 2026-08-09
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f3e5a7c9b1d2"
down_revision: str | None = "f2d4e6a8b0c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "client_vehicles",
        sa.Column("client_account_id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("plate", sa.String(length=15), nullable=False),
        sa.Column("plate_type", sa.String(length=16), nullable=False),
        sa.Column("vin", sa.String(length=17), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("color", sa.String(length=50), nullable=True),
        sa.Column("mileage", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "plate_type IN ('ru', 'foreign')",
            name="ck_client_vehicles_plate_type",
        ),
        sa.ForeignKeyConstraint(
            ["client_account_id"],
            ["client_accounts.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "client_account_id",
            "vin",
            name="uq_client_vehicles_account_vin",
        ),
    )
    op.create_index(
        op.f("ix_client_vehicles_client_account_id"),
        "client_vehicles",
        ["client_account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_client_vehicles_plate"),
        "client_vehicles",
        ["plate"],
        unique=False,
    )
    op.create_index(
        op.f("ix_client_vehicles_vin"),
        "client_vehicles",
        ["vin"],
        unique=False,
    )

    # Existing tenant vehicles are copied forward without changing or deleting
    # their CRM rows. DISTINCT ON collapses the same physical car already seen
    # by one account in several organizations.
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            sa.text(
                """
                INSERT INTO client_vehicles (
                    client_account_id, brand, model, plate, plate_type, vin,
                    year, color, mileage, created_at, updated_at
                )
                SELECT DISTINCT ON (
                    c.client_account_id,
                    COALESCE(
                        NULLIF(UPPER(REPLACE(v.vin, ' ', '')), ''),
                        NULLIF(UPPER(REPLACE(v.license_plate, ' ', '')), ''),
                        'vehicle:' || v.id::text
                    )
                )
                    c.client_account_id,
                    v.make,
                    v.model,
                    LEFT(COALESCE(NULLIF(v.license_plate, ''), 'НЕТ-' || v.id::text), 15),
                    CASE
                        WHEN COALESCE(v.license_plate, '') ~ '^[A-Za-z0-9 -]+$'
                        THEN 'foreign'
                        ELSE 'ru'
                    END,
                    NULLIF(UPPER(REPLACE(v.vin, ' ', '')), ''),
                    v.year,
                    v.color,
                    v.mileage,
                    v.created_at,
                    v.updated_at
                FROM vehicles AS v
                JOIN clients AS c ON c.id = v.client_id
                WHERE c.client_account_id IS NOT NULL
                ORDER BY
                    c.client_account_id,
                    COALESCE(
                        NULLIF(UPPER(REPLACE(v.vin, ' ', '')), ''),
                        NULLIF(UPPER(REPLACE(v.license_plate, ' ', '')), ''),
                        'vehicle:' || v.id::text
                    ),
                    v.updated_at DESC,
                    v.id DESC
                """
            )
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_client_vehicles_vin"), table_name="client_vehicles")
    op.drop_index(op.f("ix_client_vehicles_plate"), table_name="client_vehicles")
    op.drop_index(
        op.f("ix_client_vehicles_client_account_id"),
        table_name="client_vehicles",
    )
    op.drop_table("client_vehicles")

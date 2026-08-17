"""add staff login identity and preserve frontend positions

Revision ID: e2f6a1c8d4b0
Revises: d5a2e7c9b4f3
Create Date: 2026-08-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e2f6a1c8d4b0"
down_revision: str | None = "d5a2e7c9b4f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("normalized_phone", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("login", sa.String(length=100), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "staff_role_key",
            sa.String(length=30),
            nullable=False,
            server_default="junior_admin",
        ),
    )
    op.add_column("users", sa.Column("rate", sa.Numeric(precision=12, scale=2), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE users
            SET staff_role_key = CASE
                WHEN role IN ('ADMIN', 'admin') THEN 'senior_admin'
                WHEN role IN ('MANAGER', 'manager') THEN 'junior_admin'
                WHEN role IN ('MECHANIC', 'mechanic') THEN 'senior_master'
                ELSE 'junior_admin'
            END
            """
        )
    )
    op.alter_column("users", "staff_role_key", server_default=None)

    # Backfill only unambiguous Russian numbers.  Duplicate legacy numbers stay
    # NULL in normalized_phone so adding the unique index never blocks upgrade.
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            sa.text(
                r"""
                WITH cleaned AS (
                    SELECT id, regexp_replace(phone, '[^0-9]', '', 'g') AS digits
                    FROM users
                    WHERE phone IS NOT NULL
                ), candidates AS (
                    SELECT id,
                           CASE
                               WHEN length(digits) = 10 THEN '+7' || digits
                               WHEN length(digits) = 11 AND left(digits, 1) IN ('7', '8')
                                   THEN '+7' || substring(digits FROM 2)
                               ELSE NULL
                           END AS normalized
                    FROM cleaned
                ), unique_phones AS (
                    SELECT normalized
                    FROM candidates
                    WHERE normalized IS NOT NULL
                    GROUP BY normalized
                    HAVING count(*) = 1
                )
                UPDATE users AS target
                SET normalized_phone = candidates.normalized,
                    phone = candidates.normalized
                FROM candidates
                JOIN unique_phones USING (normalized)
                WHERE target.id = candidates.id
                """
            )
        )

    op.create_index("ix_users_normalized_phone", "users", ["normalized_phone"], unique=True)
    op.create_index("ix_users_login", "users", ["login"], unique=True)
    op.create_index("ix_users_staff_role_key", "users", ["staff_role_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_staff_role_key", table_name="users")
    op.drop_index("ix_users_login", table_name="users")
    op.drop_index("ix_users_normalized_phone", table_name="users")
    op.drop_column("users", "rate")
    op.drop_column("users", "staff_role_key")
    op.drop_column("users", "login")
    op.drop_column("users", "normalized_phone")

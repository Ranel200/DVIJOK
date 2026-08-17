"""add organization owner flag

Revision ID: f4a6b8c0d2e4
Revises: f3e5a7c9b1d2
Create Date: 2026-08-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f4a6b8c0d2e4"
down_revision: str | None = "f3e5a7c9b1d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_owner",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # Сохраняем совместимость развёрнутых баз: владельцем становится самый
    # ранний активный ADMIN каждой организации. Остальные старшие
    # администраторы остаются обычными сотрудниками.
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            sa.text(
                """
                UPDATE users AS target
                SET is_owner = true
                FROM (
                    SELECT DISTINCT ON (organization_id) id
                    FROM users
                    WHERE role IN ('ADMIN', 'admin') AND is_active = true
                    ORDER BY organization_id, id
                ) AS owners
                WHERE target.id = owners.id
                """
            )
        )
    else:
        op.execute(
            sa.text(
                """
                UPDATE users
                SET is_owner = true
                WHERE id IN (
                    SELECT MIN(id)
                    FROM users
                    WHERE role IN ('ADMIN', 'admin') AND is_active = true
                    GROUP BY organization_id
                )
                """
            )
        )


def downgrade() -> None:
    op.drop_column("users", "is_owner")

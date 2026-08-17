"""add organization referrals and immutable client attribution

Revision ID: 7d3a1f0c2b4e
Revises: 41b7e2a9d6c0
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7d3a1f0c2b4e"
down_revision: str | None = "41b7e2a9d6c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_referrals",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_organization_referrals_organization_id",
        "organization_referrals",
        ["organization_id"],
        unique=True,
    )
    op.create_index(
        "ix_organization_referrals_code",
        "organization_referrals",
        ["code"],
        unique=True,
    )
    op.add_column(
        "client_accounts",
        sa.Column("source_organization_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_client_accounts_source_organization_id_organizations",
        "client_accounts",
        "organizations",
        ["source_organization_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_client_accounts_source_organization_id",
        "client_accounts",
        ["source_organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_client_accounts_source_organization_id",
        table_name="client_accounts",
    )
    op.drop_constraint(
        "fk_client_accounts_source_organization_id_organizations",
        "client_accounts",
        type_="foreignkey",
    )
    op.drop_column("client_accounts", "source_organization_id")
    op.drop_index(
        "ix_organization_referrals_code",
        table_name="organization_referrals",
    )
    op.drop_index(
        "ix_organization_referrals_organization_id",
        table_name="organization_referrals",
    )
    op.drop_table("organization_referrals")

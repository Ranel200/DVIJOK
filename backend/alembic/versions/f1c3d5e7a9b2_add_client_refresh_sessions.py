"""add revocable client refresh sessions

Revision ID: f1c3d5e7a9b2
Revises: e8b2c7d4f0a6
Create Date: 2026-08-07
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f1c3d5e7a9b2"
down_revision: str | None = "e8b2c7d4f0a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "client_refresh_sessions",
        sa.Column("client_account_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["client_account_id"], ["client_accounts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_client_refresh_sessions_client_account_id",
        "client_refresh_sessions",
        ["client_account_id"],
    )
    op.create_index(
        "ix_client_refresh_sessions_token_hash",
        "client_refresh_sessions",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_client_refresh_sessions_expires_at",
        "client_refresh_sessions",
        ["expires_at"],
    )
    op.create_index(
        "ix_client_refresh_sessions_revoked_at",
        "client_refresh_sessions",
        ["revoked_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_client_refresh_sessions_revoked_at", table_name="client_refresh_sessions"
    )
    op.drop_index(
        "ix_client_refresh_sessions_expires_at", table_name="client_refresh_sessions"
    )
    op.drop_index(
        "ix_client_refresh_sessions_token_hash", table_name="client_refresh_sessions"
    )
    op.drop_index(
        "ix_client_refresh_sessions_client_account_id",
        table_name="client_refresh_sessions",
    )
    op.drop_table("client_refresh_sessions")

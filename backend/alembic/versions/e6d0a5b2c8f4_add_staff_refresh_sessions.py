"""add revocable staff refresh sessions and login audit

Revision ID: e6d0a5b2c8f4
Revises: e5c9d4a1b7f3
Create Date: 2026-08-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e6d0a5b2c8f4"
down_revision: str | None = "e5c9d4a1b7f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "email_confirm_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "phone_confirm_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column("users", "email_confirm_enabled", server_default=None)
    op.alter_column("users", "phone_confirm_enabled", server_default=None)

    op.create_table(
        "staff_refresh_sessions",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("remember", sa.Boolean(), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_staff_refresh_sessions_organization_id",
        "staff_refresh_sessions",
        ["organization_id"],
    )
    op.create_index(
        "ix_staff_refresh_sessions_user_id", "staff_refresh_sessions", ["user_id"]
    )
    op.create_index(
        "ix_staff_refresh_sessions_token_hash",
        "staff_refresh_sessions",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_staff_refresh_sessions_expires_at", "staff_refresh_sessions", ["expires_at"]
    )
    op.create_index(
        "ix_staff_refresh_sessions_revoked_at", "staff_refresh_sessions", ["revoked_at"]
    )

    op.create_table(
        "staff_login_events",
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("identifier", sa.String(length=255), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_staff_login_events_organization_id", "staff_login_events", ["organization_id"]
    )
    op.create_index("ix_staff_login_events_user_id", "staff_login_events", ["user_id"])
    op.create_index("ix_staff_login_events_success", "staff_login_events", ["success"])


def downgrade() -> None:
    op.drop_index("ix_staff_login_events_success", table_name="staff_login_events")
    op.drop_index("ix_staff_login_events_user_id", table_name="staff_login_events")
    op.drop_index("ix_staff_login_events_organization_id", table_name="staff_login_events")
    op.drop_table("staff_login_events")
    op.drop_index("ix_staff_refresh_sessions_revoked_at", table_name="staff_refresh_sessions")
    op.drop_index("ix_staff_refresh_sessions_expires_at", table_name="staff_refresh_sessions")
    op.drop_index("ix_staff_refresh_sessions_token_hash", table_name="staff_refresh_sessions")
    op.drop_index("ix_staff_refresh_sessions_user_id", table_name="staff_refresh_sessions")
    op.drop_index(
        "ix_staff_refresh_sessions_organization_id", table_name="staff_refresh_sessions"
    )
    op.drop_table("staff_refresh_sessions")
    op.drop_column("users", "phone_confirm_enabled")
    op.drop_column("users", "email_confirm_enabled")

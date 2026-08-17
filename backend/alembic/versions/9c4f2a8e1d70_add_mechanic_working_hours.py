"""add individual mechanic working hours

Revision ID: 9c4f2a8e1d70
Revises: 8f3c2d91a6b4
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "9c4f2a8e1d70"
down_revision: str | None = "8f3c2d91a6b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "mechanics",
        sa.Column(
            "schedule_configured",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.alter_column("mechanics", "schedule_configured", server_default=None)
    op.create_table(
        "mechanic_working_hours",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("mechanic_id", sa.Integer(), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
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
            "weekday >= 0 AND weekday <= 6",
            name="ck_mechanic_working_hours_weekday",
        ),
        sa.CheckConstraint(
            "end_time > start_time",
            name="ck_mechanic_working_hours_interval",
        ),
        sa.ForeignKeyConstraint(
            ["mechanic_id"], ["mechanics.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "mechanic_id",
            "weekday",
            "start_time",
            "end_time",
            name="uq_mechanic_working_hours_interval",
        ),
    )
    op.create_index(
        "ix_mechanic_working_hours_mechanic_id",
        "mechanic_working_hours",
        ["mechanic_id"],
        unique=False,
    )
    op.create_index(
        "ix_mechanic_working_hours_organization_id",
        "mechanic_working_hours",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mechanic_working_hours_organization_id",
        table_name="mechanic_working_hours",
    )
    op.drop_index(
        "ix_mechanic_working_hours_mechanic_id",
        table_name="mechanic_working_hours",
    )
    op.drop_table("mechanic_working_hours")
    op.drop_column("mechanics", "schedule_configured")

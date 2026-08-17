"""add private employee document storage

Revision ID: e7a1b6c3d9f5
Revises: e6d0a5b2c8f4
Create Date: 2026-08-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e7a1b6c3d9f5"
down_revision: str | None = "e6d0a5b2c8f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employee_documents",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("size_bytes > 0", name="ck_employee_documents_size_positive"),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "kind", name="uq_employee_documents_user_kind"),
    )
    op.create_index(
        "ix_employee_documents_organization_id",
        "employee_documents",
        ["organization_id"],
    )
    op.create_index("ix_employee_documents_user_id", "employee_documents", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_employee_documents_user_id", table_name="employee_documents")
    op.drop_index("ix_employee_documents_organization_id", table_name="employee_documents")
    op.drop_table("employee_documents")

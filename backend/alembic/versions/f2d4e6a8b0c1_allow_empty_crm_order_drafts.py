"""allow CRM orders to start as empty drafts

Revision ID: f2d4e6a8b0c1
Revises: f1c3d5e7a9b2
Create Date: 2026-08-07
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f2d4e6a8b0c1"
down_revision: str | None = "f1c3d5e7a9b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("orders", "client_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("orders", "vehicle_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("vehicles", "client_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column("vehicles", "client_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("orders", "vehicle_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("orders", "client_id", existing_type=sa.Integer(), nullable=False)

"""Store client registration consents on the global account.

Revision ID: fc6a8b0d2e4f
Revises: fb5d7e9a1c3f
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


revision: str = "fc6a8b0d2e4f"
down_revision: str | None = "fb5d7e9a1c3f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for name in ("consent_personal", "consent_transfer", "consent_marketing"):
        op.add_column(
            "client_accounts",
            sa.Column(name, sa.Boolean(), nullable=False, server_default=sa.false()),
        )
        # Existing accounts are not backfilled. Their historical consent state
        # remains unchanged; new registrations set these fields explicitly.
        op.alter_column("client_accounts", name, server_default=None)


def downgrade() -> None:
    for name in ("consent_marketing", "consent_transfer", "consent_personal"):
        op.drop_column("client_accounts", name)

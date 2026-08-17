"""allow free status moves on the CRM board

Revision ID: e8b2c7d4f0a6
Revises: e7a1b6c3d9f5
Create Date: 2026-08-07
"""

from collections.abc import Sequence

from alembic import op

revision: str = "e8b2c7d4f0a6"
down_revision: str | None = "e7a1b6c3d9f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DROP TRIGGER IF EXISTS trg_orders_done_document ON orders")
    op.execute("DROP FUNCTION IF EXISTS enforce_done_order_document()")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(
        """
        CREATE FUNCTION enforce_done_order_document() RETURNS trigger AS $$
        BEGIN
            IF NEW.status = 'DONE'
               AND NOT EXISTS (
                   SELECT 1 FROM order_documents d WHERE d.order_id = NEW.id
               )
            THEN
                RAISE EXCEPTION 'completed order must have an order document';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_orders_done_document
        BEFORE INSERT OR UPDATE OF status ON orders
        FOR EACH ROW EXECUTE FUNCTION enforce_done_order_document()
        """
    )

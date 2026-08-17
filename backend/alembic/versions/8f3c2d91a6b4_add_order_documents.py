"""add order documents and enforce documents for completed orders

Revision ID: 8f3c2d91a6b4
Revises: 7d3a1f0c2b4e
Create Date: 2026-07-28 22:20:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "8f3c2d91a6b4"
down_revision: str | None = "7d3a1f0c2b4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "order_documents",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column(
            "source",
            sa.Enum(
                "GENERATED",
                "UPLOADED",
                name="orderdocumentsource",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
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
            "size_bytes > 0",
            name="ck_order_documents_size_positive",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "order_id",
            name="uq_order_documents_order_id",
        ),
    )
    op.create_index(
        "ix_order_documents_organization_id",
        "order_documents",
        ["organization_id"],
        unique=False,
    )

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
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
        op.execute(
            """
            CREATE FUNCTION prevent_completed_order_document_delete() RETURNS trigger AS $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM orders o
                    WHERE o.id = OLD.order_id AND o.status = 'DONE'
                )
                THEN
                    RAISE EXCEPTION 'cannot delete document of completed order';
                END IF;
                RETURN OLD;
            END;
            $$ LANGUAGE plpgsql
            """
        )
        op.execute(
            """
            CREATE TRIGGER trg_order_documents_protect_done
            BEFORE DELETE ON order_documents
            FOR EACH ROW EXECUTE FUNCTION prevent_completed_order_document_delete()
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "DROP TRIGGER IF EXISTS trg_order_documents_protect_done "
            "ON order_documents"
        )
        op.execute(
            "DROP FUNCTION IF EXISTS prevent_completed_order_document_delete()"
        )
        op.execute("DROP TRIGGER IF EXISTS trg_orders_done_document ON orders")
        op.execute("DROP FUNCTION IF EXISTS enforce_done_order_document()")
    op.drop_index(
        "ix_order_documents_organization_id",
        table_name="order_documents",
    )
    op.drop_table("order_documents")

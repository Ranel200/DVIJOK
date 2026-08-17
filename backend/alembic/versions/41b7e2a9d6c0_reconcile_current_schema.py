"""reconcile legacy initial schema with the current tenant/client models

Revision ID: 41b7e2a9d6c0
Revises: ca9578f833fe
Create Date: 2026-07-28

The original initial revision predates tenant scoping and the client backend.
This forward-only reconciliation keeps that applied revision immutable while
making both clean installs and legacy databases converge on the current schema.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "41b7e2a9d6c0"
down_revision: str | None = "ca9578f833fe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TENANT_TABLES = (
    "users",
    "clients",
    "mechanics",
    "vehicles",
    "services",
    "orders",
    "order_items",
    "schedule_slots",
    "mechanic_blocks",
    "inventory_items",
    "stock_movements",
)


def _inspector():
    return inspect(op.get_bind())


def _has_table(table_name: str) -> bool:
    return _inspector().has_table(table_name)


def _has_column(table_name: str, column_name: str) -> bool:
    return column_name in {
        column["name"] for column in _inspector().get_columns(table_name)
    }


def _has_index(table_name: str, index_name: str) -> bool:
    return any(
        index["name"] == index_name
        for index in _inspector().get_indexes(table_name)
    )


def _has_fk(table_name: str, columns: tuple[str, ...]) -> bool:
    return any(
        tuple(fk["constrained_columns"]) == columns
        for fk in _inspector().get_foreign_keys(table_name)
    )


def _has_unique(table_name: str, constraint_name: str) -> bool:
    return any(
        constraint["name"] == constraint_name
        for constraint in _inspector().get_unique_constraints(table_name)
    )


def _create_organizations() -> None:
    if _has_table("organizations"):
        return
    op.create_table(
        "organizations",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("inn", sa.String(length=12), nullable=False),
        sa.Column("tax_system", sa.String(length=20), nullable=False),
        sa.Column("legal_form", sa.String(length=20), nullable=False),
        sa.Column("legal_address", sa.Text(), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("subscription_until", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organizations_inn", "organizations", ["inn"], unique=True)


def _create_client_accounts() -> None:
    if _has_table("client_accounts"):
        return
    op.create_table(
        "client_accounts",
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("telegram_id", sa.String(length=64), nullable=True),
        sa.Column("vk_id", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_client_accounts_phone", "client_accounts", ["phone"], unique=True
    )
    op.create_index(
        "ix_client_accounts_telegram_id",
        "client_accounts",
        ["telegram_id"],
        unique=True,
    )
    op.create_index(
        "ix_client_accounts_vk_id",
        "client_accounts",
        ["vk_id"],
        unique=True,
    )


def _legacy_rows_exist() -> bool:
    bind = op.get_bind()
    for table_name in TENANT_TABLES:
        if not _has_column(table_name, "organization_id"):
            if bind.execute(sa.text(f'SELECT 1 FROM "{table_name}" LIMIT 1')).first():
                return True
    return False


def _create_legacy_organization() -> int:
    """Create an explicit quarantine tenant for pre-tenant legacy rows."""
    result = op.get_bind().execute(
        sa.text(
            """
            INSERT INTO organizations
                (name, inn, tax_system, legal_form, legal_address, phone,
                 status, subscription_until, is_active)
            VALUES
                (:name, :inn, :tax_system, :legal_form, :address, :phone,
                 :status, NULL, true)
            RETURNING id
            """
        ),
        {
            "name": "Legacy data (migration)",
            "inn": "000000000000",
            "tax_system": "USN",
            "legal_form": "OOO",
            "address": "Требуется назначить организацию",
            "phone": "+70000000000",
            "status": "ACTIVE",
        },
    )
    return int(result.scalar_one())


def _add_tenant_scope(table_name: str, legacy_organization_id: int | None) -> None:
    if not _has_column(table_name, "organization_id"):
        op.add_column(
            table_name,
            sa.Column("organization_id", sa.Integer(), nullable=True),
        )
        if legacy_organization_id is not None:
            op.execute(
                sa.text(
                    f'UPDATE "{table_name}" '
                    "SET organization_id = :organization_id "
                    "WHERE organization_id IS NULL"
                ).bindparams(organization_id=legacy_organization_id)
            )
        op.alter_column(
            table_name,
            "organization_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
    if not _has_fk(table_name, ("organization_id",)):
        op.create_foreign_key(
            f"fk_{table_name}_organization_id_organizations",
            table_name,
            "organizations",
            ["organization_id"],
            ["id"],
            ondelete="CASCADE",
        )
    index_name = f"ix_{table_name}_organization_id"
    if not _has_index(table_name, index_name):
        op.create_index(index_name, table_name, ["organization_id"], unique=False)


def _add_client_link() -> None:
    if not _has_column("clients", "client_account_id"):
        op.add_column(
            "clients",
            sa.Column("client_account_id", sa.Integer(), nullable=True),
        )
    if not _has_fk("clients", ("client_account_id",)):
        op.create_foreign_key(
            "fk_clients_client_account_id_client_accounts",
            "clients",
            "client_accounts",
            ["client_account_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if not _has_index("clients", "ix_clients_client_account_id"):
        op.create_index(
            "ix_clients_client_account_id",
            "clients",
            ["client_account_id"],
            unique=False,
        )


def _reconcile_tenant_uniqueness() -> None:
    inventory_indexes = {
        index["name"]: index for index in _inspector().get_indexes("inventory_items")
    }
    sku_index = inventory_indexes.get("ix_inventory_items_sku")
    if sku_index and sku_index.get("unique"):
        op.drop_index("ix_inventory_items_sku", table_name="inventory_items")
        op.create_index(
            "ix_inventory_items_sku",
            "inventory_items",
            ["sku"],
            unique=False,
        )
    if not _has_unique("inventory_items", "uq_inventory_org_sku"):
        op.create_unique_constraint(
            "uq_inventory_org_sku",
            "inventory_items",
            ["organization_id", "sku"],
        )
    for constraint in _inspector().get_unique_constraints("vehicles"):
        if constraint["column_names"] == ["vin"]:
            op.drop_constraint(
                constraint["name"],
                "vehicles",
                type_="unique",
            )
    if not _has_unique("vehicles", "uq_vehicles_org_vin"):
        op.create_unique_constraint(
            "uq_vehicles_org_vin",
            "vehicles",
            ["organization_id", "vin"],
        )


def upgrade() -> None:
    _create_organizations()
    _create_client_accounts()
    legacy_organization_id = (
        _create_legacy_organization() if _legacy_rows_exist() else None
    )
    for table_name in TENANT_TABLES:
        _add_tenant_scope(table_name, legacy_organization_id)
    _add_client_link()
    _reconcile_tenant_uniqueness()


def downgrade() -> None:
    # Forward-only reconciliation: columns may have existed before Alembic knew
    # about them. Dropping them would destroy valid tenant/client data.
    pass

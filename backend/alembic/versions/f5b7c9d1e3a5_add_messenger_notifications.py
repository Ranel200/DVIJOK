"""add messenger bindings and notification outbox

Revision ID: f5b7c9d1e3a5
Revises: f4a6b8c0d2e4
Create Date: 2026-08-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f5b7c9d1e3a5"
down_revision: str | None = "f4a6b8c0d2e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "client_messenger_bindings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_account_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("external_user_id", sa.String(length=64), nullable=False),
        sa.Column("external_chat_id", sa.String(length=64), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "linked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["client_account_id"], ["client_accounts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "client_account_id", "channel", name="uq_messenger_binding_account_channel"
        ),
        sa.UniqueConstraint(
            "channel", "external_user_id", name="uq_messenger_binding_channel_user"
        ),
    )
    op.create_index(
        "ix_client_messenger_bindings_client_account_id",
        "client_messenger_bindings",
        ["client_account_id"],
    )
    op.create_index(
        "ix_client_messenger_bindings_channel",
        "client_messenger_bindings",
        ["channel"],
    )
    op.create_index(
        "ix_client_messenger_bindings_is_active",
        "client_messenger_bindings",
        ["is_active"],
    )

    op.create_table(
        "client_messenger_link_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_account_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["client_account_id"], ["client_accounts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_client_messenger_link_tokens_client_account_id",
        "client_messenger_link_tokens",
        ["client_account_id"],
    )
    op.create_index(
        "ix_client_messenger_link_tokens_channel",
        "client_messenger_link_tokens",
        ["channel"],
    )
    op.create_index(
        "ix_client_messenger_link_tokens_token_hash",
        "client_messenger_link_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_client_messenger_link_tokens_expires_at",
        "client_messenger_link_tokens",
        ["expires_at"],
    )
    op.create_index(
        "ix_client_messenger_link_tokens_consumed_at",
        "client_messenger_link_tokens",
        ["consumed_at"],
    )

    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_account_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("recipient_id", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["client_account_id"], ["client_accounts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "order_id",
            "channel",
            "event_type",
            name="uq_notification_order_channel_event",
        ),
    )
    for column in ("client_account_id", "order_id", "channel", "event_type", "status"):
        op.create_index(
            f"ix_notification_deliveries_{column}", "notification_deliveries", [column]
        )
    op.create_index(
        "ix_notification_deliveries_next_attempt_at",
        "notification_deliveries",
        ["next_attempt_at"],
    )
    op.create_index(
        "ix_notification_delivery_ready",
        "notification_deliveries",
        ["status", "next_attempt_at", "attempts"],
    )

    # Сохраняем уже существующие Telegram/VK-привязки из client_accounts.
    # Для развёрнутых баз старые колонки остаются совместимыми.
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            sa.text(
                """
                INSERT INTO client_messenger_bindings
                    (client_account_id, channel, external_user_id, external_chat_id,
                     is_active, linked_at)
                SELECT id, 'TELEGRAM', telegram_id, telegram_id, true, CURRENT_TIMESTAMP
                FROM client_accounts WHERE telegram_id IS NOT NULL
                ON CONFLICT DO NOTHING
                """
            )
        )
        op.execute(
            sa.text(
                """
                INSERT INTO client_messenger_bindings
                    (client_account_id, channel, external_user_id, external_chat_id,
                     is_active, linked_at)
                SELECT id, 'VK', vk_id, vk_id, true, CURRENT_TIMESTAMP
                FROM client_accounts WHERE vk_id IS NOT NULL
                ON CONFLICT DO NOTHING
                """
            )
        )
    else:
        op.execute(
            sa.text(
                """
                INSERT OR IGNORE INTO client_messenger_bindings
                    (client_account_id, channel, external_user_id, external_chat_id,
                     is_active, linked_at)
                SELECT id, 'TELEGRAM', telegram_id, telegram_id, 1, CURRENT_TIMESTAMP
                FROM client_accounts WHERE telegram_id IS NOT NULL
                """
            )
        )
        op.execute(
            sa.text(
                """
                INSERT OR IGNORE INTO client_messenger_bindings
                    (client_account_id, channel, external_user_id, external_chat_id,
                     is_active, linked_at)
                SELECT id, 'VK', vk_id, vk_id, 1, CURRENT_TIMESTAMP
                FROM client_accounts WHERE vk_id IS NOT NULL
                """
            )
        )


def downgrade() -> None:
    op.drop_index("ix_notification_delivery_ready", table_name="notification_deliveries")
    for column in (
        "next_attempt_at",
        "status",
        "event_type",
        "channel",
        "order_id",
        "client_account_id",
    ):
        op.drop_index(f"ix_notification_deliveries_{column}", table_name="notification_deliveries")
    op.drop_table("notification_deliveries")

    for column in ("consumed_at", "expires_at", "token_hash", "channel", "client_account_id"):
        op.drop_index(
            f"ix_client_messenger_link_tokens_{column}",
            table_name="client_messenger_link_tokens",
        )
    op.drop_table("client_messenger_link_tokens")

    for column in ("is_active", "channel", "client_account_id"):
        op.drop_index(
            f"ix_client_messenger_bindings_{column}",
            table_name="client_messenger_bindings",
        )
    op.drop_table("client_messenger_bindings")

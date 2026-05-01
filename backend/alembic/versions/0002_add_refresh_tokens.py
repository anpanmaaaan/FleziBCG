"""add_refresh_tokens

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-01 00:00:00.000000

WHY: Adds the refresh_tokens table required by P0-A-03A (RefreshToken
foundation). Refresh tokens are stored as SHA-256 hashes only — raw token
values are never persisted.

INVARIANT: This migration creates ONE new table only. It does NOT modify any
existing tables or indexes.

DOWNGRADE: Drops the refresh_tokens table and its indexes. All other tables
remain untouched.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("token_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        # SECURITY: SHA-256 hex digest of raw token. Never the raw token.
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("token_family_id", sa.String(length=64), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoke_reason", sa.String(length=256), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_refresh_token_hash"),
        sa.UniqueConstraint("token_id"),
    )
    op.create_index(
        "ix_refresh_tokens_token_id",
        "refresh_tokens",
        ["token_id"],
        unique=True,
    )
    op.create_index(
        "ix_refresh_tokens_tenant_user",
        "refresh_tokens",
        ["tenant_id", "user_id"],
    )
    op.create_index(
        "ix_refresh_tokens_session_id",
        "refresh_tokens",
        ["session_id"],
    )
    op.create_index(
        "ix_refresh_tokens_family",
        "refresh_tokens",
        ["token_family_id"],
    )
    op.create_index(
        "ix_refresh_tokens_expires_at",
        "refresh_tokens",
        ["expires_at"],
    )


def downgrade() -> None:
    # INVARIANT: drop indexes before table (required order for some dialects).
    op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_family", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_session_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_tenant_user", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_token_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

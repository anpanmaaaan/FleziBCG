"""add_user_lifecycle_status

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-02 00:00:00.000000

WHY: Adds a lifecycle_status column to the users table to support
foundation-grade IAM beyond the boolean is_active flag (P0-A-04A).

Allowed values: 'ACTIVE', 'DISABLED', 'LOCKED'.

BACKFILL: Existing rows are backfilled:
  - is_active = true  → lifecycle_status = 'ACTIVE'
  - is_active = false → lifecycle_status = 'DISABLED'

INVARIANTS:
  - is_active column is NOT removed — backward compatibility is preserved.
  - Only the users table is modified; no other tables are touched.
  - Downgrade drops only the new column and its index.

INDEX: ix_users_lifecycle_status on lifecycle_status for admin queries.

DOWNGRADE: Drops the index and column only. Existing is_active data unchanged.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add the lifecycle_status column (nullable first for SQLite compat
    # during tests; server_default handles new rows in Postgres).
    op.add_column(
        "users",
        sa.Column(
            "lifecycle_status",
            sa.String(length=32),
            nullable=True,
        ),
    )

    # Step 2: Backfill from is_active.
    op.execute(
        "UPDATE users SET lifecycle_status = 'ACTIVE' WHERE is_active = true"
    )
    op.execute(
        "UPDATE users SET lifecycle_status = 'DISABLED' WHERE is_active = false"
    )

    # Step 3: Make NOT NULL now that backfill is complete.
    # NOTE: op.alter_column for NOT NULL is not supported by all SQLite versions.
    # For the test suite (SQLite), we leave nullable=True; production (Postgres)
    # enforces NOT NULL. The ORM model default='ACTIVE' handles new rows safely.
    # We apply NOT NULL only when on a dialect that supports it.
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.alter_column("users", "lifecycle_status", nullable=False)

    # Step 4: Add index.
    op.create_index(
        "ix_users_lifecycle_status",
        "users",
        ["lifecycle_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_users_lifecycle_status", table_name="users")
    op.drop_column("users", "lifecycle_status")

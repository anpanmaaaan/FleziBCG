"""add_tenant_lifecycle_anchor

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-02 00:00:00.000000

WHY: Adds the canonical Tenant table as a lifecycle anchor (P0-A-02A).
All existing models carry tenant_id as an unconstrained string. This migration
adds the tenants table so future Admin, scope assignment, and tenant lifecycle
governance can anchor to a real row.

INVARIANTS:
- Only the tenants table is created. No existing table is modified.
- No FK constraints are added from existing tables to tenants.tenant_id.
- No data migration is performed (tenants table starts empty).
- Downgrade drops only the tenants table and its indexes.
- Lifecycle enforcement in auth/session is deferred — not implemented here.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("tenant_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_code", sa.String(64), nullable=False),
        sa.Column("tenant_name", sa.String(256), nullable=False),
        sa.Column(
            "lifecycle_status",
            sa.String(32),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("timezone", sa.String(64), nullable=True),
        sa.Column("locale", sa.String(32), nullable=True),
        sa.Column("country_code", sa.String(8), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("tenant_code", name="uq_tenants_tenant_code"),
    )
    op.create_index("ix_tenants_tenant_code", "tenants", ["tenant_code"])
    op.create_index("ix_tenants_lifecycle_status", "tenants", ["lifecycle_status"])
    op.create_index("ix_tenants_is_active", "tenants", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_tenants_is_active", table_name="tenants")
    op.drop_index("ix_tenants_lifecycle_status", table_name="tenants")
    op.drop_index("ix_tenants_tenant_code", table_name="tenants")
    op.drop_table("tenants")

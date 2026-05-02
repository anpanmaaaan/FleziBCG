"""Add reason_codes table for unified reason code foundation (MMD-BE-07)

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-02 00:00:00.000000

WHY: Per reason-code-foundation-contract.md v1.0 (Sections 6-8), implement
minimal unified reason code reference data model. Reason codes provide
classification context across operational domains (execution, downtime, quality,
material, maintenance) without owning operational events.

Graph repair note (P0-A-MIG-01): this migration was rebased from duplicate
revision id 0004 to 0010 so Alembic revision IDs remain unique and the graph
has a single canonical head.

This table is independent of downtime_reasons (operational downtime data);
they serve different purposes:
  - reason_codes: generic classification reference, tenant-scoped, MMD governed
  - downtime_reasons: execution-scoped operational reason selection
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reason_codes",
        sa.Column("reason_code_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("reason_domain", sa.String(length=32), nullable=False),
        sa.Column("reason_category", sa.String(length=64), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("reason_name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("lifecycle_status", sa.String(length=16), nullable=False, server_default="DRAFT"),
        sa.Column("requires_comment", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
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
        sa.PrimaryKeyConstraint("reason_code_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "reason_domain",
            "reason_code",
            name="uq_reason_codes_tenant_domain_code",
        ),
    )
    op.create_index(
        "ix_reason_codes_tenant_id",
        "reason_codes",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_reason_codes_tenant_domain_category",
        "reason_codes",
        ["tenant_id", "reason_domain", "reason_category"],
        unique=False,
    )
    op.create_index(
        "ix_reason_codes_tenant_status_active",
        "reason_codes",
        ["tenant_id", "lifecycle_status", "is_active"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_reason_codes_tenant_status_active",
        table_name="reason_codes",
    )
    op.drop_index(
        "ix_reason_codes_tenant_domain_category",
        table_name="reason_codes",
    )
    op.drop_index(
        "ix_reason_codes_tenant_id",
        table_name="reason_codes",
    )
    op.drop_table("reason_codes")

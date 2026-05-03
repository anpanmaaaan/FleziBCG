"""Add governed resource identity fields to approval_requests (P0-A-13)

Revision ID: 0011
Revises: 0010
Create Date: 2026-05-03 00:00:00.000000

WHY: Per approved-service-generic-extension-contract.md and
governed-action-approval-applicability-contract.md, add nullable governed
resource identity foundation to ApprovalRequest.

This migration is additive only. Current subject_type/subject_ref remain
supported for backward compatibility. New governed_resource_* fields are
optional (nullable) and require no data backfill.

This slice implements schema foundation only. No generic approval runtime
behavior is implemented. No governed action type enforcement is added.
No scope-aware rule matching is implemented.

Candidate fields added per P0-A-11B and P0-A-11C:
  - governed_resource_type: identifies the governed domain entity class
  - governed_resource_id: identifies the authoritative backend instance
  - governed_resource_display_ref: operator-friendly reference (display only)
  - governed_resource_tenant_id: align with backend tenant truth
  - governed_resource_scope_ref: canonical scope reference
  - governed_action_type: governed transition intent

All fields are nullable. Existing requests without governed fields remain valid.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add governed resource identity fields to approval_requests
    op.add_column(
        "approval_requests",
        sa.Column("governed_resource_type", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "approval_requests",
        sa.Column("governed_resource_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "approval_requests",
        sa.Column("governed_resource_display_ref", sa.String(length=256), nullable=True),
    )
    op.add_column(
        "approval_requests",
        sa.Column("governed_resource_tenant_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "approval_requests",
        sa.Column("governed_resource_scope_ref", sa.String(length=256), nullable=True),
    )
    op.add_column(
        "approval_requests",
        sa.Column("governed_action_type", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    # Remove governed resource identity fields from approval_requests
    op.drop_column("approval_requests", "governed_action_type")
    op.drop_column("approval_requests", "governed_resource_scope_ref")
    op.drop_column("approval_requests", "governed_resource_tenant_id")
    op.drop_column("approval_requests", "governed_resource_display_ref")
    op.drop_column("approval_requests", "governed_resource_id")
    op.drop_column("approval_requests", "governed_resource_type")

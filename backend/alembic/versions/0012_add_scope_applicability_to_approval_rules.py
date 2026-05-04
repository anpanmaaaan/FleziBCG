"""Add scope applicability fields to approval_rules (P0-A-15A)

Revision ID: 0012
Revises: 0011
Create Date: 2026-05-04 00:00:00.000000

WHY: Per approval-rule-scope-applicability-contract.md (P0-A-14), add nullable
scope applicability fields to ApprovalRule as the schema foundation for future
scope-aware rule matching.

This migration is additive only. All new columns are nullable. Existing
approval_rules rows remain valid without any backfill.

Fields added per P0-A-14 contract §6:
  - governed_action_type: future match against governed action type namespace
  - governed_resource_type: future match against specific resource type
  - scope_ref: future match against canonical scope path (e.g. plant/01)
  - scope_type: future match against scope level (e.g. "plant")
  - priority: future explicit tie-break if multiple rules match at same level
  - effective_from: future time-bounded activation
  - effective_to: future time-bounded expiry

No runtime matching logic is implemented in this slice.
No API or frontend changes are made.
No MMD files are touched.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("approval_rules", sa.Column("governed_action_type", sa.String(64), nullable=True))
    op.add_column("approval_rules", sa.Column("governed_resource_type", sa.String(64), nullable=True))
    op.add_column("approval_rules", sa.Column("scope_ref", sa.String(256), nullable=True))
    op.add_column("approval_rules", sa.Column("scope_type", sa.String(32), nullable=True))
    op.add_column("approval_rules", sa.Column("priority", sa.Integer(), nullable=True))
    op.add_column("approval_rules", sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True))
    op.add_column("approval_rules", sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("approval_rules", "effective_to")
    op.drop_column("approval_rules", "effective_from")
    op.drop_column("approval_rules", "priority")
    op.drop_column("approval_rules", "scope_type")
    op.drop_column("approval_rules", "scope_ref")
    op.drop_column("approval_rules", "governed_resource_type")
    op.drop_column("approval_rules", "governed_action_type")

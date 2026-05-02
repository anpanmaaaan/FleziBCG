"""drop operation_claims and operation_claim_audit_logs tables

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-02 00:00:00.000000

WHY: Finalises claim retirement. OperationClaim / OperationClaimAuditLog were
replaced by StationSession as the canonical execution ownership model
(P0-C-08 retirement programme). All API routes, frontend client surface,
service functions, tests, and seed scripts that referenced claim tables were
removed in H14B–H16C. This migration drops the now-unreferenced tables.

Boundary lock:
- operation_claim_audit_logs is dropped first (FK child → operation_claims).
- operation_claims is dropped second (FK parent).
- station_scope_value column on operations is NOT touched here (separate concern).
- StationSession tables are NOT touched.
- Queue/station API behaviour is unchanged.

Governance:
- CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED (H13)
- Drop order approved in H16 contract.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop child table first (FK: operation_claim_audit_logs.claim_id → operation_claims.id)
    op.drop_index("ix_operation_claim_audit_logs_station_scope_id", table_name="operation_claim_audit_logs")
    op.drop_index("ix_operation_claim_audit_logs_operation_id", table_name="operation_claim_audit_logs")
    op.drop_index("ix_operation_claim_audit_logs_tenant_id", table_name="operation_claim_audit_logs")
    op.drop_index("ix_operation_claim_audit_logs_claim_id", table_name="operation_claim_audit_logs")
    op.drop_table("operation_claim_audit_logs")

    # Drop parent table second
    op.drop_index("uq_operation_claims_operation_active", table_name="operation_claims")
    op.drop_index("ix_operation_claims_expires_at", table_name="operation_claims")
    op.drop_index("ix_operation_claims_claimed_by_user_id", table_name="operation_claims")
    op.drop_index("ix_operation_claims_station_scope_id", table_name="operation_claims")
    op.drop_index("ix_operation_claims_operation_id", table_name="operation_claims")
    op.drop_index("ix_operation_claims_tenant_id", table_name="operation_claims")
    op.drop_table("operation_claims")


def downgrade() -> None:
    # Recreate parent table first
    op.create_table(
        "operation_claims",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column(
            "operation_id",
            sa.Integer(),
            sa.ForeignKey("operations.id"),
            nullable=False,
        ),
        sa.Column(
            "station_scope_id",
            sa.Integer(),
            sa.ForeignKey("scopes.id"),
            nullable=False,
        ),
        sa.Column("claimed_by_user_id", sa.String(length=64), nullable=False),
        sa.Column(
            "claimed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("release_reason", sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_operation_claims_tenant_id", "operation_claims", ["tenant_id"])
    op.create_index("ix_operation_claims_operation_id", "operation_claims", ["operation_id"])
    op.create_index("ix_operation_claims_station_scope_id", "operation_claims", ["station_scope_id"])
    op.create_index("ix_operation_claims_claimed_by_user_id", "operation_claims", ["claimed_by_user_id"])
    op.create_index("ix_operation_claims_expires_at", "operation_claims", ["expires_at"])
    # Partial unique index: only one active (unreleased) claim per operation
    op.create_index(
        "uq_operation_claims_operation_active",
        "operation_claims",
        ["operation_id"],
        unique=True,
        postgresql_where=sa.text("released_at IS NULL"),
    )

    # Recreate child table second
    op.create_table(
        "operation_claim_audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "claim_id",
            sa.Integer(),
            sa.ForeignKey("operation_claims.id"),
            nullable=True,
        ),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column(
            "operation_id",
            sa.Integer(),
            sa.ForeignKey("operations.id"),
            nullable=False,
        ),
        sa.Column(
            "station_scope_id",
            sa.Integer(),
            sa.ForeignKey("scopes.id"),
            nullable=False,
        ),
        sa.Column("actor_user_id", sa.String(length=64), nullable=False),
        sa.Column("acting_role_code", sa.String(length=32), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_operation_claim_audit_logs_claim_id", "operation_claim_audit_logs", ["claim_id"])
    op.create_index("ix_operation_claim_audit_logs_tenant_id", "operation_claim_audit_logs", ["tenant_id"])
    op.create_index("ix_operation_claim_audit_logs_operation_id", "operation_claim_audit_logs", ["operation_id"])
    op.create_index("ix_operation_claim_audit_logs_station_scope_id", "operation_claim_audit_logs", ["station_scope_id"])

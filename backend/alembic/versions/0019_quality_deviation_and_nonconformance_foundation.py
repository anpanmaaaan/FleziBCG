"""Add quality deviation and nonconformance foundation schema

Revision ID: 0019
Revises: 0018
Create Date: 2026-05-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0019"
down_revision: Union[str, None] = "0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quality_deviation_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hold_id", sa.Integer(), nullable=False),
        sa.Column("gate_instance_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("requested_by", sa.String(length=128), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_by", sa.String(length=128), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_comment", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["hold_id"], ["quality_holds.id"]),
        sa.ForeignKeyConstraint(["gate_instance_id"], ["quality_gate_instances.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quality_deviation_requests_hold_id",
        "quality_deviation_requests",
        ["hold_id"],
    )
    op.create_index(
        "ix_quality_deviation_requests_gate_instance_id",
        "quality_deviation_requests",
        ["gate_instance_id"],
    )
    op.create_index(
        "ix_quality_deviation_requests_tenant_id",
        "quality_deviation_requests",
        ["tenant_id"],
    )

    op.create_table(
        "quality_nonconformances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nc_code", sa.String(length=64), nullable=False),
        sa.Column("operation_id", sa.Integer(), nullable=False),
        sa.Column("hold_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("disposition_code", sa.String(length=64), nullable=True),
        sa.Column("reported_by", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["hold_id"], ["quality_holds.id"]),
        sa.ForeignKeyConstraint(["operation_id"], ["operations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "nc_code",
            name="uq_quality_nonconformances_tenant_nc_code",
        ),
    )
    op.create_index(
        "ix_quality_nonconformances_operation_id",
        "quality_nonconformances",
        ["operation_id"],
    )
    op.create_index(
        "ix_quality_nonconformances_hold_id",
        "quality_nonconformances",
        ["hold_id"],
    )
    op.create_index(
        "ix_quality_nonconformances_tenant_id",
        "quality_nonconformances",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_quality_nonconformances_tenant_id",
        table_name="quality_nonconformances",
    )
    op.drop_index(
        "ix_quality_nonconformances_hold_id",
        table_name="quality_nonconformances",
    )
    op.drop_index(
        "ix_quality_nonconformances_operation_id",
        table_name="quality_nonconformances",
    )
    op.drop_table("quality_nonconformances")

    op.drop_index(
        "ix_quality_deviation_requests_tenant_id",
        table_name="quality_deviation_requests",
    )
    op.drop_index(
        "ix_quality_deviation_requests_gate_instance_id",
        table_name="quality_deviation_requests",
    )
    op.drop_index(
        "ix_quality_deviation_requests_hold_id",
        table_name="quality_deviation_requests",
    )
    op.drop_table("quality_deviation_requests")

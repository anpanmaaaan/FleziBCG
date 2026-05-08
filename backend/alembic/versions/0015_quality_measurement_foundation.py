"""Initial Quality Lite measurement foundation tables

Revision ID: 0015
Revises: 0014
Create Date: 2026-05-07 00:00:00.000000

WHY: Introduce backend-authoritative Quality Lite persistence for:
- QC measurement submission records
- per-item measured values
- quality hold queue rows for out-of-spec evaluation results
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quality_measurement_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("operation_id", sa.Integer(), nullable=False),
        sa.Column("submitted_by", sa.String(length=128), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("quality_status", sa.String(length=32), nullable=False),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["operation_id"], ["operations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quality_measurement_records_operation_id",
        "quality_measurement_records",
        ["operation_id"],
    )
    op.create_index(
        "ix_quality_measurement_records_tenant_id",
        "quality_measurement_records",
        ["tenant_id"],
    )

    op.create_table(
        "quality_measurement_values",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("measurement_record_id", sa.Integer(), nullable=False),
        sa.Column("item_code", sa.String(length=64), nullable=False),
        sa.Column("measured_value", sa.Float(), nullable=False),
        sa.Column("lower_limit", sa.Float(), nullable=True),
        sa.Column("upper_limit", sa.Float(), nullable=True),
        sa.Column("is_within_spec", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["measurement_record_id"], ["quality_measurement_records.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quality_measurement_values_measurement_record_id",
        "quality_measurement_values",
        ["measurement_record_id"],
    )

    op.create_table(
        "quality_holds",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("operation_id", sa.Integer(), nullable=False),
        sa.Column("measurement_record_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=256), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["measurement_record_id"], ["quality_measurement_records.id"]),
        sa.ForeignKeyConstraint(["operation_id"], ["operations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("measurement_record_id", name="uq_quality_holds_measurement_record_id"),
    )
    op.create_index("ix_quality_holds_operation_id", "quality_holds", ["operation_id"])
    op.create_index("ix_quality_holds_tenant_id", "quality_holds", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_quality_holds_tenant_id", table_name="quality_holds")
    op.drop_index("ix_quality_holds_operation_id", table_name="quality_holds")
    op.drop_table("quality_holds")

    op.drop_index(
        "ix_quality_measurement_values_measurement_record_id",
        table_name="quality_measurement_values",
    )
    op.drop_table("quality_measurement_values")

    op.drop_index(
        "ix_quality_measurement_records_tenant_id",
        table_name="quality_measurement_records",
    )
    op.drop_index(
        "ix_quality_measurement_records_operation_id",
        table_name="quality_measurement_records",
    )
    op.drop_table("quality_measurement_records")

"""Add quality gate foundation schema

Revision ID: 0017
Revises: 0016
Create Date: 2026-05-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quality_gate_definitions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gate_type", sa.String(length=32), nullable=False),
        sa.Column("rule_set_version", sa.String(length=64), nullable=False),
        sa.Column("applicability_scope_type", sa.String(length=32), nullable=True),
        sa.Column("applicability_scope_value", sa.String(length=128), nullable=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_quality_gate_definitions_tenant_code"),
    )
    op.create_index(
        "ix_quality_gate_definitions_tenant_id",
        "quality_gate_definitions",
        ["tenant_id"],
    )

    op.create_table(
        "quality_gate_instances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("gate_definition_id", sa.Integer(), nullable=False),
        sa.Column("operation_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.Column("opened_by", sa.String(length=128), nullable=False),
        sa.Column("closed_by", sa.String(length=128), nullable=True),
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
        sa.ForeignKeyConstraint(["gate_definition_id"], ["quality_gate_definitions.id"]),
        sa.ForeignKeyConstraint(["operation_id"], ["operations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quality_gate_instances_gate_definition_id",
        "quality_gate_instances",
        ["gate_definition_id"],
    )
    op.create_index(
        "ix_quality_gate_instances_operation_id",
        "quality_gate_instances",
        ["operation_id"],
    )
    op.create_index(
        "ix_quality_gate_instances_tenant_id",
        "quality_gate_instances",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_quality_gate_instances_tenant_id", table_name="quality_gate_instances")
    op.drop_index("ix_quality_gate_instances_operation_id", table_name="quality_gate_instances")
    op.drop_index(
        "ix_quality_gate_instances_gate_definition_id",
        table_name="quality_gate_instances",
    )
    op.drop_table("quality_gate_instances")

    op.drop_index(
        "ix_quality_gate_definitions_tenant_id",
        table_name="quality_gate_definitions",
    )
    op.drop_table("quality_gate_definitions")

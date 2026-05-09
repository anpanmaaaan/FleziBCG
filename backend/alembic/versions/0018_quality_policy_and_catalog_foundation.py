"""Add quality policy and catalog foundation schema

Revision ID: 0018
Revises: 0017
Create Date: 2026-05-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018"
down_revision: Union[str, None] = "0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quality_applicability_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("policy_code", sa.String(length=64), nullable=False),
        sa.Column("policy_name", sa.String(length=128), nullable=False),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("scope_value", sa.String(length=128), nullable=False),
        sa.Column("qc_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("gate_definition_id", sa.Integer(), nullable=True),
        sa.Column("lifecycle_status", sa.String(length=16), nullable=False, server_default="DRAFT"),
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
        sa.ForeignKeyConstraint(["gate_definition_id"], ["quality_gate_definitions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "policy_code",
            name="uq_quality_applicability_policies_tenant_code",
        ),
    )
    op.create_index(
        "ix_quality_applicability_policies_tenant_id",
        "quality_applicability_policies",
        ["tenant_id"],
    )

    op.create_table(
        "quality_rule_sets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_set_code", sa.String(length=64), nullable=False),
        sa.Column("rule_set_name", sa.String(length=128), nullable=False),
        sa.Column("rule_set_version", sa.String(length=64), nullable=False),
        sa.Column("lifecycle_status", sa.String(length=16), nullable=False, server_default="DRAFT"),
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
        sa.UniqueConstraint(
            "tenant_id",
            "rule_set_code",
            "rule_set_version",
            name="uq_quality_rule_sets_tenant_code_version",
        ),
    )
    op.create_index(
        "ix_quality_rule_sets_tenant_id",
        "quality_rule_sets",
        ["tenant_id"],
    )

    op.create_table(
        "quality_rule_definitions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_set_id", sa.Integer(), nullable=False),
        sa.Column("item_code", sa.String(length=64), nullable=False),
        sa.Column("evaluation_operator", sa.String(length=32), nullable=False),
        sa.Column("lower_limit", sa.Float(), nullable=True),
        sa.Column("upper_limit", sa.Float(), nullable=True),
        sa.Column("expected_boolean", sa.Boolean(), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["rule_set_id"], ["quality_rule_sets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quality_rule_definitions_rule_set_id",
        "quality_rule_definitions",
        ["rule_set_id"],
    )

    op.create_table(
        "quality_disposition_catalog",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("disposition_code", sa.String(length=64), nullable=False),
        sa.Column("disposition_name", sa.String(length=128), nullable=False),
        sa.Column("lifecycle_status", sa.String(length=16), nullable=False, server_default="DRAFT"),
        sa.Column("requires_comment", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requires_quality_approval", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("releases_hold", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("quality_status_target", sa.String(length=32), nullable=False),
        sa.Column("review_status_target", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.UniqueConstraint(
            "tenant_id",
            "disposition_code",
            name="uq_quality_disposition_catalog_tenant_code",
        ),
    )
    op.create_index(
        "ix_quality_disposition_catalog_tenant_id",
        "quality_disposition_catalog",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_quality_disposition_catalog_tenant_id",
        table_name="quality_disposition_catalog",
    )
    op.drop_table("quality_disposition_catalog")

    op.drop_index(
        "ix_quality_rule_definitions_rule_set_id",
        table_name="quality_rule_definitions",
    )
    op.drop_table("quality_rule_definitions")

    op.drop_index("ix_quality_rule_sets_tenant_id", table_name="quality_rule_sets")
    op.drop_table("quality_rule_sets")

    op.drop_index(
        "ix_quality_applicability_policies_tenant_id",
        table_name="quality_applicability_policies",
    )
    op.drop_table("quality_applicability_policies")

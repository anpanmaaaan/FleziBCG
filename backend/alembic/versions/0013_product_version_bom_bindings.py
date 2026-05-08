"""Add product_version_bom_bindings table (MMD-BE-14)

Revision ID: 0013
Revises: 0011
Create Date: 2026-05-06 00:00:00.000000

WHY: Per bom-product-version-binding-governance-contract.md (MMD-BOM-WRITE-02),
introduce the ProductVersionBomBinding association table that links a Product
Version to a BOM for definition applicability purposes.

This is a new table addition only. No existing tables are modified.
All constraints match the ORM model definition.

Boundary lock (MMD-BE-14):
- Definition applicability metadata only.
- No execution/material/inventory/ERP/traceability/quality columns.
- binding_type PRIMARY only in this slice.
- One ACTIVE PRIMARY binding per PV enforced at service layer.
- Historical REMOVED rows remain queryable.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_version_bom_bindings",
        sa.Column("binding_id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "product_id",
            sa.String(64),
            sa.ForeignKey("products.product_id"),
            nullable=False,
        ),
        sa.Column(
            "product_version_id",
            sa.String(64),
            sa.ForeignKey("product_versions.product_version_id"),
            nullable=False,
        ),
        sa.Column(
            "bom_id",
            sa.String(64),
            sa.ForeignKey("boms.bom_id"),
            nullable=False,
        ),
        sa.Column("binding_type", sa.String(16), nullable=False, server_default="PRIMARY"),
        sa.Column("binding_status", sa.String(16), nullable=False, server_default="ACTIVE"),
        sa.Column("notes", sa.Text, nullable=True),
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
        sa.Column("created_by", sa.String(64), nullable=False),
        sa.Column("updated_by", sa.String(64), nullable=True),
    )
    op.create_index(
        "ix_product_version_bom_bindings_tenant_id",
        "product_version_bom_bindings",
        ["tenant_id"],
    )
    op.create_index(
        "ix_product_version_bom_bindings_product_id",
        "product_version_bom_bindings",
        ["product_id"],
    )
    op.create_index(
        "ix_product_version_bom_bindings_product_version_id",
        "product_version_bom_bindings",
        ["product_version_id"],
    )
    op.create_index(
        "ix_product_version_bom_bindings_bom_id",
        "product_version_bom_bindings",
        ["bom_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_product_version_bom_bindings_bom_id",
        table_name="product_version_bom_bindings",
    )
    op.drop_index(
        "ix_product_version_bom_bindings_product_version_id",
        table_name="product_version_bom_bindings",
    )
    op.drop_index(
        "ix_product_version_bom_bindings_product_id",
        table_name="product_version_bom_bindings",
    )
    op.drop_index(
        "ix_product_version_bom_bindings_tenant_id",
        table_name="product_version_bom_bindings",
    )
    op.drop_table("product_version_bom_bindings")

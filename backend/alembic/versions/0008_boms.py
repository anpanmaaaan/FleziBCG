"""boms and bom_items tables (MMD-BE-05)

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-02 00:00:00.000000

WHY: Introduces minimal BOM backend read model foundation for MMD Product
Definition. This revision is read-model only and intentionally excludes BOM
write workflows and runtime material behavior.

Boundary lock:
- No product_version_id on boms in this revision.
- No fields for inventory movement, backflush, ERP posting, genealogy, or
  quality acceptance behavior.
- Product-scoped BOM read model only.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "boms",
        sa.Column("bom_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "product_id",
            sa.String(64),
            sa.ForeignKey("products.product_id"),
            nullable=False,
        ),
        sa.Column("bom_code", sa.String(64), nullable=False),
        sa.Column("bom_name", sa.String(256), nullable=False),
        sa.Column("lifecycle_status", sa.String(16), nullable=False, server_default="DRAFT"),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.UniqueConstraint(
            "tenant_id",
            "product_id",
            "bom_code",
            name="uq_boms_tenant_product_code",
        ),
    )
    op.create_index("ix_boms_tenant_id", "boms", ["tenant_id"])
    op.create_index("ix_boms_product_id", "boms", ["product_id"])
    op.create_index("ix_boms_tenant_product", "boms", ["tenant_id", "product_id"])

    op.create_table(
        "bom_items",
        sa.Column("bom_item_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("bom_id", sa.String(64), sa.ForeignKey("boms.bom_id"), nullable=False),
        sa.Column(
            "component_product_id",
            sa.String(64),
            sa.ForeignKey("products.product_id"),
            nullable=False,
        ),
        sa.Column("line_no", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit_of_measure", sa.String(32), nullable=False),
        sa.Column("scrap_factor", sa.Float(), nullable=True),
        sa.Column("reference_designator", sa.String(128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.UniqueConstraint(
            "tenant_id",
            "bom_id",
            "line_no",
            name="uq_bom_items_tenant_bom_line_no",
        ),
    )
    op.create_index("ix_bom_items_tenant_id", "bom_items", ["tenant_id"])
    op.create_index("ix_bom_items_bom_id", "bom_items", ["bom_id"])
    op.create_index("ix_bom_items_component_product_id", "bom_items", ["component_product_id"])
    op.create_index("ix_bom_items_tenant_bom", "bom_items", ["tenant_id", "bom_id"])


def downgrade() -> None:
    op.drop_index("ix_bom_items_tenant_bom", table_name="bom_items")
    op.drop_index("ix_bom_items_component_product_id", table_name="bom_items")
    op.drop_index("ix_bom_items_bom_id", table_name="bom_items")
    op.drop_index("ix_bom_items_tenant_id", table_name="bom_items")
    op.drop_table("bom_items")

    op.drop_index("ix_boms_tenant_product", table_name="boms")
    op.drop_index("ix_boms_product_id", table_name="boms")
    op.drop_index("ix_boms_tenant_id", table_name="boms")
    op.drop_table("boms")

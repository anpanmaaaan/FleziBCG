"""product_versions table (MMD-BE-03)

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-02 00:00:00.000000

WHY: Introduces product_versions as the minimal backend read model for the
Product Version foundation contract (P0-B MMD baseline, MMD-BE-03).

Product Version represents a versioned manufacturing definition context for a
product. It does NOT replace ERP/PLM revision truth. No BOM, Routing, or
Resource Requirement bindings are added in this revision.

INVARIANTS:
- product_versions.product_id FK → products.product_id (existing table).
- Unique constraint: (tenant_id, product_id, version_code).
- is_current is advisory; no partial unique index is added (deferred per
  MMD-BE-03 contract decision — see docs/audit/mmd-be-03-*).
- All nullable columns have no default; non-nullable columns have explicit
  server defaults where applicable.
- Downgrade drops only product_versions and its indexes.

Out of scope:
  - BOM / Routing / Resource Requirement binding to product version
  - Product Version write-path / lifecycle workflow
  - ERP/PLM master data sync
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_versions",
        sa.Column("product_version_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "product_id",
            sa.String(64),
            sa.ForeignKey("products.product_id"),
            nullable=False,
        ),
        sa.Column("version_code", sa.String(64), nullable=False),
        sa.Column("version_name", sa.String(256), nullable=True),
        sa.Column(
            "lifecycle_status",
            sa.String(16),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column(
            "is_current",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
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
            "tenant_id", "product_id", "version_code",
            name="uq_product_versions_tenant_product_code",
        ),
    )
    op.create_index(
        "ix_product_versions_tenant_id",
        "product_versions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_product_versions_product_id",
        "product_versions",
        ["product_id"],
    )
    op.create_index(
        "ix_product_versions_tenant_product",
        "product_versions",
        ["tenant_id", "product_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_product_versions_tenant_product", table_name="product_versions")
    op.drop_index("ix_product_versions_product_id", table_name="product_versions")
    op.drop_index("ix_product_versions_tenant_id", table_name="product_versions")
    op.drop_table("product_versions")

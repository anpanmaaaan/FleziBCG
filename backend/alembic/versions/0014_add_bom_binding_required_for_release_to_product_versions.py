"""Add bom_binding_required_for_release to product_versions (MMD-BE-14C)

Revision ID: 0014
Revises: 0013
Create Date: 2026-05-06 00:00:00.000000

WHY: Per product-version-release-bom-binding-validation-policy-contract.md
(MMD-BE-14B), add a per-Product Version policy flag that controls whether
release requires an active PRIMARY BOM binding to a RELEASED BOM.

Migration rules:
- Default false: all existing Product Versions are unaffected.
- No existing RELEASED Product Version is invalidated.
- No BOM lifecycle changes.
- No binding rows created.
- No Product Version lifecycle changes.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "product_versions",
        sa.Column(
            "bom_binding_required_for_release",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("product_versions", "bom_binding_required_for_release")

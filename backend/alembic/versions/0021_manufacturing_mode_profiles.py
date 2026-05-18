"""Add manufacturing mode profile anchors

Revision ID: 0021
Revises: 0020
Create Date: 2026-05-17 00:00:00.000000

WHY: The pilot runtime remains discrete execution, but the product must support
future batch/process customers without hard-coding a tenant as discrete-only.
This migration adds the minimum profile anchors only. It does not add recipe,
phase, batch, weighing, ISA-88, or eBR runtime behavior.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0021"
down_revision: Union[str, None] = "0020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column(
            "manufacturing_mode_default",
            sa.String(32),
            nullable=False,
            server_default="DISCRETE",
        ),
    )
    op.create_check_constraint(
        "ck_tenants_manufacturing_mode_default",
        "tenants",
        "manufacturing_mode_default IN ('DISCRETE', 'BATCH_PROCESS')",
    )
    op.create_index(
        "ix_tenants_manufacturing_mode_default",
        "tenants",
        ["manufacturing_mode_default"],
    )

    op.add_column(
        "plants",
        sa.Column("manufacturing_mode_profile", sa.String(32), nullable=True),
    )
    op.create_check_constraint(
        "ck_plants_manufacturing_mode_profile",
        "plants",
        "manufacturing_mode_profile IS NULL OR "
        "manufacturing_mode_profile IN ('DISCRETE', 'BATCH_PROCESS')",
    )
    op.create_index(
        "ix_plants_manufacturing_mode_profile",
        "plants",
        ["manufacturing_mode_profile"],
    )

    op.add_column(
        "scopes",
        sa.Column("manufacturing_mode_profile", sa.String(32), nullable=True),
    )
    op.create_check_constraint(
        "ck_scopes_manufacturing_mode_profile",
        "scopes",
        "manufacturing_mode_profile IS NULL OR "
        "manufacturing_mode_profile IN ('DISCRETE', 'BATCH_PROCESS')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_scopes_manufacturing_mode_profile",
        "scopes",
        type_="check",
    )
    op.drop_column("scopes", "manufacturing_mode_profile")

    op.drop_index("ix_plants_manufacturing_mode_profile", table_name="plants")
    op.drop_constraint(
        "ck_plants_manufacturing_mode_profile",
        "plants",
        type_="check",
    )
    op.drop_column("plants", "manufacturing_mode_profile")

    op.drop_index("ix_tenants_manufacturing_mode_default", table_name="tenants")
    op.drop_constraint(
        "ck_tenants_manufacturing_mode_default",
        "tenants",
        type_="check",
    )
    op.drop_column("tenants", "manufacturing_mode_default")


"""Add quality disposition decision persistence

Revision ID: 0016
Revises: 0015
Create Date: 2026-05-07 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quality_disposition_decisions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hold_id", sa.Integer(), nullable=False),
        sa.Column("disposition_code", sa.String(length=64), nullable=False),
        sa.Column("decided_by", sa.String(length=128), nullable=False),
        sa.Column("comment", sa.String(length=512), nullable=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["hold_id"], ["quality_holds.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quality_disposition_decisions_hold_id",
        "quality_disposition_decisions",
        ["hold_id"],
    )
    op.create_index(
        "ix_quality_disposition_decisions_tenant_id",
        "quality_disposition_decisions",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_quality_disposition_decisions_tenant_id",
        table_name="quality_disposition_decisions",
    )
    op.drop_index(
        "ix_quality_disposition_decisions_hold_id",
        table_name="quality_disposition_decisions",
    )
    op.drop_table("quality_disposition_decisions")

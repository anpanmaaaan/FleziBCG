"""routing_operations extended fields (MMD-BE-01)

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-01 00:00:00.000000

WHY: Per routing-foundation-contract.md v1.2 (Section 3 + Section 13), the
RoutingOperation aggregate is extended with 3 nullable RoutingOperation-owned
fields:
  - setup_time (DOUBLE PRECISION) — operation prep time before run begins
  - run_time_per_unit (DOUBLE PRECISION) — time per unit during steady-state run
  - work_center_code (VARCHAR 64) — work center identifier; tenant-scoped string

All columns are nullable. No default. No backfill required (existing rows
keep NULL semantics, which is valid per contract Section 8 soft invariants).

This is a manual Alembic revision (not autogenerate) per baseline policy
(0001_baseline.py header comment). All future schema changes follow this
pattern until autogenerate trust is established.

Out of scope:
  - required_skill / required_skill_level — deferred to ResourceRequirement
  - qc_checkpoint_count — rejected as RoutingOperation column (Quality Lite owns)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "routing_operations",
        sa.Column("setup_time", sa.Float(), nullable=True),
    )
    op.add_column(
        "routing_operations",
        sa.Column("run_time_per_unit", sa.Float(), nullable=True),
    )
    op.add_column(
        "routing_operations",
        sa.Column("work_center_code", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("routing_operations", "work_center_code")
    op.drop_column("routing_operations", "run_time_per_unit")
    op.drop_column("routing_operations", "setup_time")

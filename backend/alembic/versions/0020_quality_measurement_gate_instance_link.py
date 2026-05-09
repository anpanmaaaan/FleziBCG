"""Link quality measurement records to gate instances

Revision ID: 0020
Revises: 0019
Create Date: 2026-05-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0020"
down_revision: Union[str, None] = "0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "quality_measurement_records",
        sa.Column("gate_instance_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_quality_measurement_records_gate_instance_id",
        "quality_measurement_records",
        "quality_gate_instances",
        ["gate_instance_id"],
        ["id"],
    )
    op.create_index(
        "ix_quality_measurement_records_gate_instance_id",
        "quality_measurement_records",
        ["gate_instance_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_quality_measurement_records_gate_instance_id",
        table_name="quality_measurement_records",
    )
    op.drop_constraint(
        "fk_quality_measurement_records_gate_instance_id",
        "quality_measurement_records",
        type_="foreignkey",
    )
    op.drop_column("quality_measurement_records", "gate_instance_id")

"""add_plant_hierarchy

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-02 00:00:00.000000

WHY: Adds the Plant / Area / Line / Station / Equipment ORM foundation
(P0-A-05A). Creates five new tables for the tenant-scoped manufacturing
hierarchy. No existing tables are modified.

HIERARCHY:
  Plant → Area → Line → Station → Equipment

INVARIANTS:
  - All five tables include tenant_id (soft string reference, no Tenant table
    exists yet in this phase).
  - Internal hierarchy FKs are created between the new tables only.
  - No existing table (users, operations, station_sessions, etc.) is touched.
  - No data migration is performed.
  - Downgrade drops the five new tables in reverse dependency order:
      equipment → stations → lines → areas → plants
  - Operation.station_scope_value and StationSession.station_id remain plain
    strings. FK binding to stations is deferred to a future slice.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 1. plants — root of hierarchy, no parent FK
    # -----------------------------------------------------------------------
    op.create_table(
        "plants",
        sa.Column("plant_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("plant_code", sa.String(64), nullable=False),
        sa.Column("plant_name", sa.String(256), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=True),
        sa.Column("country_code", sa.String(8), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint("tenant_id", "plant_code", name="uq_plants_tenant_code"),
    )
    op.create_index("ix_plants_tenant_id", "plants", ["tenant_id"])

    # -----------------------------------------------------------------------
    # 2. areas — child of plants
    # -----------------------------------------------------------------------
    op.create_table(
        "areas",
        sa.Column("area_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "plant_id",
            sa.String(64),
            sa.ForeignKey("plants.plant_id", name="fk_areas_plant_id"),
            nullable=False,
        ),
        sa.Column("area_code", sa.String(64), nullable=False),
        sa.Column("area_name", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id", "plant_id", "area_code", name="uq_areas_tenant_plant_code"
        ),
    )
    op.create_index("ix_areas_tenant_id", "areas", ["tenant_id"])
    op.create_index("ix_areas_plant_id", "areas", ["plant_id"])

    # -----------------------------------------------------------------------
    # 3. lines — child of areas
    # -----------------------------------------------------------------------
    op.create_table(
        "lines",
        sa.Column("line_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "area_id",
            sa.String(64),
            sa.ForeignKey("areas.area_id", name="fk_lines_area_id"),
            nullable=False,
        ),
        sa.Column("line_code", sa.String(64), nullable=False),
        sa.Column("line_name", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id", "area_id", "line_code", name="uq_lines_tenant_area_code"
        ),
    )
    op.create_index("ix_lines_tenant_id", "lines", ["tenant_id"])
    op.create_index("ix_lines_area_id", "lines", ["area_id"])

    # -----------------------------------------------------------------------
    # 4. stations — child of lines
    # -----------------------------------------------------------------------
    op.create_table(
        "stations",
        sa.Column("station_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "line_id",
            sa.String(64),
            sa.ForeignKey("lines.line_id", name="fk_stations_line_id"),
            nullable=False,
        ),
        sa.Column("station_code", sa.String(64), nullable=False),
        sa.Column("station_name", sa.String(256), nullable=False),
        sa.Column("station_type", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id", "line_id", "station_code", name="uq_stations_tenant_line_code"
        ),
    )
    op.create_index("ix_stations_tenant_id", "stations", ["tenant_id"])
    op.create_index("ix_stations_line_id", "stations", ["line_id"])

    # -----------------------------------------------------------------------
    # 5. equipment — child of stations
    # -----------------------------------------------------------------------
    op.create_table(
        "equipment",
        sa.Column("equipment_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "station_id",
            sa.String(64),
            sa.ForeignKey("stations.station_id", name="fk_equipment_station_id"),
            nullable=False,
        ),
        sa.Column("equipment_code", sa.String(64), nullable=False),
        sa.Column("equipment_name", sa.String(256), nullable=False),
        sa.Column("equipment_type", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "station_id",
            "equipment_code",
            name="uq_equipment_tenant_station_code",
        ),
    )
    op.create_index("ix_equipment_tenant_id", "equipment", ["tenant_id"])
    op.create_index("ix_equipment_station_id", "equipment", ["station_id"])


def downgrade() -> None:
    # Drop in reverse dependency order: leaf first, root last.
    op.drop_index("ix_equipment_station_id", table_name="equipment")
    op.drop_index("ix_equipment_tenant_id", table_name="equipment")
    op.drop_table("equipment")

    op.drop_index("ix_stations_line_id", table_name="stations")
    op.drop_index("ix_stations_tenant_id", table_name="stations")
    op.drop_table("stations")

    op.drop_index("ix_lines_area_id", table_name="lines")
    op.drop_index("ix_lines_tenant_id", table_name="lines")
    op.drop_table("lines")

    op.drop_index("ix_areas_plant_id", table_name="areas")
    op.drop_index("ix_areas_tenant_id", table_name="areas")
    op.drop_table("areas")

    op.drop_index("ix_plants_tenant_id", table_name="plants")
    op.drop_table("plants")

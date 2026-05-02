"""Plant / Area / Line / Station / Equipment ORM foundation (P0-A-05A).

Hierarchy: Plant → Area → Line → Station → Equipment

Design decisions:
- All five entities are tenant-scoped via tenant_id (soft string reference —
  no Tenant ORM table exists yet in this phase).
- String primary keys follow the existing project pattern (user_id, routing_id…).
- Internal hierarchy FKs are explicit and NOT NULL — a child must belong to
  exactly one parent. No orphan nodes are allowed.
- is_active flag follows the existing project boolean pattern.
- metadata_json is TEXT (JSON serialised by the application layer) — no native
  JSON column type required, matching resource_requirement.py pattern.
- station_type / equipment_type allow classification without a DB-native enum
  (same approach as lifecycle_status on User).
- Operation.station_scope_value and StationSession.station_id remain plain
  strings in this slice. FK binding to the new stations table is deferred to
  a future slice to avoid breaking existing execution tests.

WHY NOT modify existing models: Existing string columns (station_scope_value,
  StationSession.station_id, etc.) are not touched — doing so would require
  coordinated migration of execution data and is explicitly out of scope.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Plant(Base):
    """Root of the plant hierarchy.

    A Plant is the top-level manufacturing site within a tenant.
    Each plant is uniquely identified by (tenant_id, plant_code).
    """

    __tablename__ = "plants"
    __table_args__ = (
        UniqueConstraint("tenant_id", "plant_code", name="uq_plants_tenant_code"),
        Index("ix_plants_tenant_id", "tenant_id"),
    )

    plant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    plant_code: Mapped[str] = mapped_column(String(64), nullable=False)
    plant_name: Mapped[str] = mapped_column(String(256), nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    areas: Mapped[list[Area]] = relationship(
        "Area",
        back_populates="plant",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("is_active", True)
        super().__init__(**kwargs)


class Area(Base):
    """Production area within a plant.

    An Area groups Lines under one plant. Each area is uniquely identified
    by (tenant_id, plant_id, area_code).
    """

    __tablename__ = "areas"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "plant_id", "area_code", name="uq_areas_tenant_plant_code"
        ),
        Index("ix_areas_tenant_id", "tenant_id"),
    )

    area_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    plant_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("plants.plant_id", name="fk_areas_plant_id"),
        nullable=False,
        index=True,
    )
    area_code: Mapped[str] = mapped_column(String(64), nullable=False)
    area_name: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    plant: Mapped[Plant] = relationship("Plant", back_populates="areas")
    lines: Mapped[list[Line]] = relationship(
        "Line",
        back_populates="area",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("is_active", True)
        super().__init__(**kwargs)


class Line(Base):
    """Production line within an area.

    A Line groups Stations. Each line is uniquely identified by
    (tenant_id, area_id, line_code).
    """

    __tablename__ = "lines"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "area_id", "line_code", name="uq_lines_tenant_area_code"
        ),
        Index("ix_lines_tenant_id", "tenant_id"),
    )

    line_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    area_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("areas.area_id", name="fk_lines_area_id"),
        nullable=False,
        index=True,
    )
    line_code: Mapped[str] = mapped_column(String(64), nullable=False)
    line_name: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    area: Mapped[Area] = relationship("Area", back_populates="lines")
    stations: Mapped[list[Station]] = relationship(
        "Station",
        back_populates="line",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("is_active", True)
        super().__init__(**kwargs)


class Station(Base):
    """Work station within a line.

    A Station represents a physical or logical work position. Each station
    is uniquely identified by (tenant_id, line_id, station_code).

    FUTURE: station_id will be referenced by StationSession.station_id and
    Operation.station_scope_value in a future slice. Today those remain plain
    string columns to avoid breaking existing execution tests.
    """

    __tablename__ = "stations"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "line_id", "station_code", name="uq_stations_tenant_line_code"
        ),
        Index("ix_stations_tenant_id", "tenant_id"),
    )

    station_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    line_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("lines.line_id", name="fk_stations_line_id"),
        nullable=False,
        index=True,
    )
    station_code: Mapped[str] = mapped_column(String(64), nullable=False)
    station_name: Mapped[str] = mapped_column(String(256), nullable=False)
    station_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    line: Mapped[Line] = relationship("Line", back_populates="stations")
    equipment_list: Mapped[list[Equipment]] = relationship(
        "Equipment",
        back_populates="station",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("is_active", True)
        super().__init__(**kwargs)


class Equipment(Base):
    """Equipment asset assigned to a station.

    Equipment represents a physical machine/tool at a station. Each item is
    uniquely identified by (tenant_id, station_id, equipment_code).

    FUTURE: equipment_id will be referenced by StationSession.equipment_id
    in a future slice.
    """

    __tablename__ = "equipment"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "station_id",
            "equipment_code",
            name="uq_equipment_tenant_station_code",
        ),
        Index("ix_equipment_tenant_id", "tenant_id"),
    )

    equipment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    station_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("stations.station_id", name="fk_equipment_station_id"),
        nullable=False,
        index=True,
    )
    equipment_code: Mapped[str] = mapped_column(String(64), nullable=False)
    equipment_name: Mapped[str] = mapped_column(String(256), nullable=False)
    equipment_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    station: Mapped[Station] = relationship("Station", back_populates="equipment_list")

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("is_active", True)
        super().__init__(**kwargs)

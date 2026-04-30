from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text

from app.db.base import Base


class StationSession(Base):
    __tablename__ = "station_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    station_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    operator_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="OPEN", index=True)
    equipment_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_operation_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("operations.id"),
        nullable=True,
        index=True,
    )
    event_name_status: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


Index(
    "uq_station_sessions_tenant_station_active_open",
    StationSession.tenant_id,
    StationSession.station_id,
    unique=True,
    postgresql_where=text("status = 'OPEN' AND closed_at IS NULL"),
)

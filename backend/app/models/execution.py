from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.master import Operation


# INTENT: This enum defines the alphabet of the execution state machine.
# _derive_status() in operation_service maps these to StatusEnum values.
class ExecutionEventType(str, Enum):
    OP_STARTED = "OP_STARTED"
    QTY_REPORTED = "QTY_REPORTED"
    NG_REPORTED = "NG_REPORTED"
    QC_MEASURE_RECORDED = "QC_MEASURE_RECORDED"
    OP_COMPLETED = "OP_COMPLETED"
    OP_ABORTED = "OP_ABORTED"
    # Canonical v1 event names per station-execution-command-event-contracts.md §7.5/§7.6.
    # New events introduced after the canonical-naming directive use lower_snake
    # strings; legacy UPPER_SNAKE entries above remain until the envelope migration.
    EXECUTION_PAUSED = "execution_paused"
    EXECUTION_RESUMED = "execution_resumed"
    DOWNTIME_STARTED = "downtime_started"
    DOWNTIME_ENDED = "downtime_ended"
    OPERATION_CLOSED_AT_STATION = "operation_closed_at_station"
    OPERATION_REOPENED = "operation_reopened"


# Interim downtime reason catalog (minimal, replace with canonical infra when available)
class DowntimeReasonClass(str, Enum):
    UNSPECIFIED = "UNSPECIFIED"
    PLANNED_MAINTENANCE = "PLANNED_MAINTENANCE"
    UNPLANNED_BREAKDOWN = "UNPLANNED_BREAKDOWN"
    MATERIAL_SHORTAGE = "MATERIAL_SHORTAGE"
    QUALITY_HOLD = "QUALITY_HOLD"
    OTHER = "OTHER"


class ExecutionEvent(Base):
    __tablename__ = "execution_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id"), nullable=False
    )
    work_order_id: Mapped[int] = mapped_column(
        ForeignKey("work_orders.id"), nullable=False
    )
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # WHY: Default "default" preserves backward compatibility with
    # pre-multi-tenant seed data. New events always receive an explicit tenant_id.
    tenant_id: Mapped[str] = mapped_column(
        String(64), nullable=False, default="default"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    operation: Mapped[Operation] = relationship("Operation", back_populates="events")

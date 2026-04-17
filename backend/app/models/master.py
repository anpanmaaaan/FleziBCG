from app.models.execution import ExecutionEvent
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


# EDGE: Enum includes display-only values (PENDING, BLOCKED, LATE, COMPLETED_LATE)
# that are NOT part of the execution state machine (PLANNED→IN_PROGRESS→COMPLETED|ABORTED).
# They exist for PO/WO-level status columns and legacy seed data.
class StatusEnum(str, Enum):
    planned = "PLANNED"
    pending = "PENDING"
    in_progress = "IN_PROGRESS"
    completed = "COMPLETED"
    completed_late = "COMPLETED_LATE"
    aborted = "ABORTED"
    blocked = "BLOCKED"
    late = "LATE"


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    route_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=StatusEnum.pending.value
    )
    planned_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    work_orders: Mapped[list["WorkOrder"]] = relationship(
        "WorkOrder",
        back_populates="production_order",
        cascade="all, delete-orphan",
    )


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id"), nullable=False
    )
    work_order_number: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=StatusEnum.pending.value
    )
    planned_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    production_order: Mapped[ProductionOrder] = relationship(
        "ProductionOrder", back_populates="work_orders"
    )
    operations: Mapped[list["Operation"]] = relationship(
        "Operation",
        back_populates="work_order",
        cascade="all, delete-orphan",
    )


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_number: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    work_order_id: Mapped[int] = mapped_column(
        ForeignKey("work_orders.id"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    # WHY: Indexed because station-execution queries filter by this value
    # on every operator page load.
    station_scope_value: Mapped[str] = mapped_column(
        String(128), nullable=False, default="STATION_01", index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=StatusEnum.pending.value
    )
    planned_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # INTENT: Snapshot fields are materialized projections updated in the same
    # transaction as the ExecutionEvent write. The append-only event log is the
    # source of truth; these columns exist for fast reads.
    completed_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    good_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scrap_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qc_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    work_order: Mapped[WorkOrder] = relationship(
        "WorkOrder", back_populates="operations"
    )
    # WHY: cascade="all, delete-orphan" ensures test teardown can remove
    # operations without orphan event rows. In production, events are append-only
    # and operations are never deleted.
    events: Mapped[list["ExecutionEvent"]] = relationship(
        "ExecutionEvent",
        back_populates="operation",
        cascade="all, delete-orphan",
    )

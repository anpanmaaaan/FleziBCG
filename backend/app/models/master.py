from app.models.execution import ExecutionEvent
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


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
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=StatusEnum.pending.value)
    planned_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    work_orders: Mapped[list["WorkOrder"]] = relationship(
        "WorkOrder",
        back_populates="production_order",
        cascade="all, delete-orphan",
    )


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"), nullable=False)
    work_order_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=StatusEnum.pending.value)
    planned_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    production_order: Mapped[ProductionOrder] = relationship("ProductionOrder", back_populates="work_orders")
    operations: Mapped[list["Operation"]] = relationship(
        "Operation",
        back_populates="work_order",
        cascade="all, delete-orphan",
    )


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    station_scope_value: Mapped[str] = mapped_column(String(128), nullable=False, default="STATION_01", index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=StatusEnum.pending.value)
    planned_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    good_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scrap_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Snapshot fields represent current derived state / projection values
    # and are not the raw append-only event source-of-truth.
    qc_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    work_order: Mapped[WorkOrder] = relationship("WorkOrder", back_populates="operations")
    events: Mapped[list["ExecutionEvent"]] = relationship(
        "ExecutionEvent",
        back_populates="operation",
        cascade="all, delete-orphan",
    )

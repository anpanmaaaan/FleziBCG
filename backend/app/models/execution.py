from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ExecutionEventType(str, Enum):
    OP_STARTED = "OP_STARTED"
    QTY_REPORTED = "QTY_REPORTED"
    NG_REPORTED = "NG_REPORTED"
    QC_MEASURE_RECORDED = "QC_MEASURE_RECORDED"
    OP_COMPLETED = "OP_COMPLETED"


class ExecutionEvent(Base):
    __tablename__ = "execution_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    production_order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"), nullable=False)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    operation_id: Mapped[int] = mapped_column(ForeignKey("operations.id"), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, default="default")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    operation: Mapped["Operation"] = relationship("Operation", back_populates="events")

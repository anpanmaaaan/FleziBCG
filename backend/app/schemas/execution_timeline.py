from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import BaseSchema


# WHY: Literal, not Enum — TimingStatus is a derived classification computed
# at query time, not stored in the DB, so enum registry is unnecessary.
TimingStatus = Literal["EARLY", "ON_TIME", "LATE"]


class ExecutionTimelineOperation(BaseSchema):
    operation_id: int
    operation_number: str
    sequence: int
    name: str
    workstation: str
    status: str
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    # EDGE: delay_minutes is None when the operation has not started — zero
    # delay and no-data are semantically different for Gantt visualization.
    delay_minutes: int | None = None
    timing_status: TimingStatus = "ON_TIME"
    qc_required: bool = False


class WorkOrderExecutionTimeline(BaseSchema):
    work_order_id: int
    work_order_number: str
    production_order_id: int
    production_order_number: str
    operations: list[ExecutionTimelineOperation] = Field(default_factory=list)

from datetime import datetime

from pydantic import BaseModel


class OperationListItem(BaseModel):
    id: int
    operation_number: str
    name: str
    sequence: int
    status: str
    supervisor_bucket: str | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    quantity: int
    completed_qty: int = 0
    progress: int = 0
    work_order_number: str | None = None
    work_center: str | None = None
    delay_minutes: int | None = None
    block_reason_code: str | None = None
    qc_risk_flag: bool = False
    wo_blocked_operations: int = 0
    wo_delayed_operations: int = 0
    cycle_time_minutes: int | None = None
    cycle_time_delta: int | None = None
    delay_count: int = 0
    delay_frequency: float = 0
    repeat_flag: bool = False
    qc_fail_count: int = 0
    high_variance_flag: bool = False
    often_late_flag: bool = False
    route_step: str | None = None

    class Config:
        from_attributes = True


class OperationDetail(OperationListItem):
    work_order_id: int
    work_order_number: str
    production_order_id: int
    production_order_number: str
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    good_qty: int = 0
    scrap_qty: int = 0
    qc_required: bool = False


class OperationStartRequest(BaseModel):
    operator_id: str | None = None
    started_at: datetime | None = None


class OperationReportQuantityRequest(BaseModel):
    good_qty: int
    scrap_qty: int = 0
    operator_id: str | None = None


class OperationCompleteRequest(BaseModel):
    operator_id: str | None = None
    completed_at: datetime | None = None


class OperationAbortRequest(BaseModel):
    operator_id: str | None = None
    reason_code: str | None = None


class OperationPauseRequest(BaseModel):
    reason_code: str | None = None
    note: str | None = None



# Request schema for start_downtime
from app.models.execution import DowntimeReasonClass

class OperationStartDowntimeRequest(BaseModel):
    reason_class: DowntimeReasonClass
    note: str | None = None

class OperationResumeRequest(BaseModel):
    note: str | None = None

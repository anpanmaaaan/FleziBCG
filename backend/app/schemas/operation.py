from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class OperationListItem(BaseModel):
    id: int
    operation_number: str
    name: str
    sequence: int
    status: str
    closure_status: str = "OPEN"
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

    model_config = ConfigDict(from_attributes=True)


class OperationDetail(OperationListItem):
    work_order_id: int
    production_order_id: int
    production_order_number: str
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    good_qty: int = 0
    scrap_qty: int = 0
    qc_required: bool = False
    # Derived from downtime_started/downtime_ended events on the append-only log:
    # true iff started_count > ended_count. Projected alongside status so
    # consumers can distinguish "blocked by downtime" without inspecting events.
    downtime_open: bool = False
    # Per-operation command capabilities derived from current backend guards
    # (status + downtime_open). Canonical command names per
    # station-execution-command-event-contracts.md §3. Identity-scoped guards
    # (session ownership, station-busy) are NOT encoded here — callers must
    # still enforce those. Missing action ⇒ backend will reject the command.
    allowed_actions: list[str] = []
    # Accumulated runtime durations derived from append-only events.
    # Includes closed intervals plus any currently open interval up to now.
    paused_total_ms: int = 0
    downtime_total_ms: int = 0
    reopen_count: int = 0
    last_reopened_at: datetime | None = None
    last_reopened_by: str | None = None
    last_closed_at: datetime | None = None
    last_closed_by: str | None = None


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


class OperationStartDowntimeRequest(BaseModel):
    # Canonical path: reason_code resolves to a `downtime_reasons` master row.
    # Classification (reason_group) is derived server-side from the master row
    # and is not a client input.
    reason_code: str
    note: str | None = None

    @field_validator("reason_code")
    @classmethod
    def _reason_code_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("reason_code must be a non-blank string")
        return stripped


class OperationEndDowntimeRequest(BaseModel):
    note: str | None = None


class OperationResumeRequest(BaseModel):
    note: str | None = None


class OperationCloseRequest(BaseModel):
    note: str | None = None


class OperationReopenRequest(BaseModel):
    reason: str

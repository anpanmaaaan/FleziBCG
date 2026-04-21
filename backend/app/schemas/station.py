from datetime import datetime

from pydantic import BaseModel, Field


class ClaimRequest(BaseModel):
    reason: str | None = None
    duration_minutes: int | None = Field(default=None, ge=1)


class ReleaseClaimRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=512)


class ClaimSummary(BaseModel):
    state: str
    expires_at: datetime | None = None
    claimed_by_user_id: str | None = None


class StationQueueItem(BaseModel):
    operation_id: int
    operation_number: str
    name: str
    work_order_number: str
    production_order_number: str
    status: str
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    claim: ClaimSummary
    # Source of truth: append-only event log. downtime is open iff
    # DOWNTIME_STARTED count > DOWNTIME_ENDED count for the operation.
    # Projected on the list so the cockpit can flag "⛔ Downtime" without
    # fetching per-operation detail. Does not drive any state transitions.
    downtime_open: bool = False


class ClaimResponse(BaseModel):
    operation_id: int
    station_scope_value: str
    claimed_by_user_id: str
    claimed_at: datetime
    expires_at: datetime
    state: str


class StationQueueResponse(BaseModel):
    items: list[StationQueueItem]
    station_scope_value: str

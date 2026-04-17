from datetime import datetime

from pydantic import BaseModel, Field


class ClaimRequest(BaseModel):
    reason: str | None = None
    # EDGE: duration_minutes is Optional — when None, the service layer
    # applies a default claim TTL. ge=1 prevents zero-length claims.
    duration_minutes: int | None = Field(default=None, ge=1)


# WHY: ReleaseClaimRequest requires a mandatory reason — release is an
# audit-significant action. Contrast with ClaimRequest.reason which is Optional.
class ReleaseClaimRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=512)


# INTENT: ClaimSummary is embedded inside StationQueueItem — provides inline
# claim visibility so the frontend renders claim state without a second call.
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

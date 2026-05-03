from datetime import datetime

from pydantic import BaseModel

class SessionOwnershipSummary(BaseModel):
    target_owner_type: str
    session_id: str | None = None
    station_id: str | None = None
    session_status: str | None = None
    operator_user_id: str | None = None
    owner_state: str
    has_open_session: bool = False


class StationQueueItem(BaseModel):
    operation_id: int
    operation_number: str
    name: str
    work_order_number: str
    production_order_number: str
    status: str
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    ownership: SessionOwnershipSummary
    # Source of truth: append-only event log. downtime is open iff
    # DOWNTIME_STARTED count > DOWNTIME_ENDED count for the operation.
    # Projected on the list so the cockpit can flag "⛔ Downtime" without
    # fetching per-operation detail. Does not drive any state transitions.
    downtime_open: bool = False


class StationQueueResponse(BaseModel):
    items: list[StationQueueItem]
    station_scope_value: str

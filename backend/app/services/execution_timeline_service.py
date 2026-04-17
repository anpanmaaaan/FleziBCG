from collections import defaultdict
from datetime import datetime, timezone

from app.models.execution import ExecutionEvent, ExecutionEventType
from app.schemas.execution_timeline import (
    ExecutionTimelineOperation,
    WorkOrderExecutionTimeline,
)

TIMING_TOLERANCE_MINUTES = 0


def _parse_event_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None

    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _event_time(event: ExecutionEvent, payload_key: str) -> datetime:
    # INTENT: Payload timestamp is preferred because events may be backfilled
    # with an explicit timestamp; created_at is a fallback for legacy events.
    parsed = _parse_event_timestamp(event.payload.get(payload_key))
    return parsed or event.created_at


def _align_for_diff(reference_time: datetime, planned_end: datetime) -> datetime:
    """Align datetime awareness before subtraction to avoid naive/aware runtime errors."""
    if reference_time.tzinfo is None and planned_end.tzinfo is not None:
        return reference_time.replace(tzinfo=planned_end.tzinfo)
    if reference_time.tzinfo is not None and planned_end.tzinfo is None:
        return reference_time.replace(tzinfo=None)
    return reference_time


def _derive_actual_start(operation, events: list[ExecutionEvent]) -> datetime | None:
    # EDGE: Uses the first OP_STARTED event (deterministic by created_at, id)
    # rather than the last, because re-starts are not part of the state machine.
    started_events = [
        event
        for event in events
        if event.event_type == ExecutionEventType.OP_STARTED.value
    ]
    if started_events:
        # Deterministic ordering even when created_at timestamps are equal.
        started_events.sort(key=lambda event: (event.created_at, event.id))
        return _event_time(started_events[0], "started_at")

    # Snapshot fallback keeps response usable for legacy/backfilled datasets.
    return operation.actual_start


def _derive_actual_end(operation, events: list[ExecutionEvent]) -> datetime | None:
    # EDGE: Uses the last OP_COMPLETED event — if multiple completions exist
    # (e.g., partial completions), the final one is the authoritative end time.
    completed_events = [
        event
        for event in events
        if event.event_type == ExecutionEventType.OP_COMPLETED.value
    ]
    if completed_events:
        # Deterministic ordering even when created_at timestamps are equal.
        completed_events.sort(key=lambda event: (event.created_at, event.id))
        return _event_time(completed_events[-1], "completed_at")

    # Snapshot fallback keeps response usable for legacy/backfilled datasets.
    return operation.actual_end


def _derive_status(operation, events: list[ExecutionEvent]) -> str:
    if any(
        event.event_type == ExecutionEventType.OP_COMPLETED.value for event in events
    ):
        return "COMPLETED"
    if any(event.event_type == ExecutionEventType.OP_STARTED.value for event in events):
        return "IN_PROGRESS"
    return operation.status or "PENDING"


def _derive_delay_minutes(
    status: str, planned_end: datetime | None, actual_end: datetime | None
) -> int | None:
    if planned_end is None:
        # No plan baseline means delay cannot be computed reliably.
        return None

    if status == "COMPLETED" and actual_end is not None:
        reference_time = actual_end
    elif status == "IN_PROGRESS":
        reference_time = datetime.now(timezone.utc)
    else:
        # PENDING/BLOCKED/etc. are intentionally delay-free in this visualization projection.
        return None

    reference_time = _align_for_diff(reference_time, planned_end)

    delta_minutes = int((reference_time - planned_end).total_seconds() / 60)
    return delta_minutes


def _derive_timing_status(delay_minutes: int | None) -> str:
    if delay_minutes is None:
        return "ON_TIME"
    if delay_minutes > TIMING_TOLERANCE_MINUTES:
        return "LATE"
    if delay_minutes < -TIMING_TOLERANCE_MINUTES:
        return "EARLY"
    return "ON_TIME"


def build_work_order_execution_timeline(
    work_order, events: list[ExecutionEvent]
) -> WorkOrderExecutionTimeline:
    events_by_operation_id: dict[int, list[ExecutionEvent]] = defaultdict(list)
    for event in events:
        events_by_operation_id[event.operation_id].append(event)

    timeline_operations: list[ExecutionTimelineOperation] = []

    for operation in sorted(work_order.operations, key=lambda item: item.sequence):
        operation_events = events_by_operation_id.get(operation.id, [])

        actual_start = _derive_actual_start(operation, operation_events)
        actual_end = _derive_actual_end(operation, operation_events)
        status = _derive_status(operation, operation_events)
        delay_minutes = _derive_delay_minutes(status, operation.planned_end, actual_end)
        timing_status = _derive_timing_status(delay_minutes)

        timeline_operations.append(
            ExecutionTimelineOperation(
                operation_id=operation.id,
                operation_number=operation.operation_number,
                sequence=operation.sequence,
                name=operation.name,
                workstation="N/A",
                status=status,
                planned_start=operation.planned_start,
                planned_end=operation.planned_end,
                actual_start=actual_start,
                actual_end=actual_end,
                delay_minutes=delay_minutes,
                timing_status=timing_status,
                qc_required=operation.qc_required,
            )
        )

    return WorkOrderExecutionTimeline(
        work_order_id=work_order.id,
        work_order_number=work_order.work_order_number,
        production_order_id=work_order.production_order_id,
        production_order_number=work_order.production_order.order_number,
        operations=timeline_operations,
    )

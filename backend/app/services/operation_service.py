

from sqlalchemy.orm import Session
from app.schemas.operation import OperationDetail

class StartDowntimeConflictError(ValueError):
    pass


class EndDowntimeConflictError(ValueError):
    pass


def end_downtime(
    db: Session,
    operation,
    request,
    actor_user_id: str,
    tenant_id: str = "default",
) -> OperationDetail:
    """
    End an open downtime. Rejects when no open downtime exists or the record
    is closed. Persists `downtime_ended` event. Does not auto-resume execution
    per canonical contract: execution must remain non-running until an
    explicit `resume_execution` command.
    """
    from app.models.execution import ExecutionEventType
    from app.models.master import StatusEnum
    from app.repositories.execution_event_repository import (
        create_execution_event,
        get_events_for_operation,
    )
    from app.repositories.operation_repository import get_operation_by_id

    if operation.tenant_id != tenant_id:
        raise EndDowntimeConflictError("TENANT_MISMATCH")

    # Contracts §10 STATE_* family: closed records reject before any state work.
    if operation.status in (
        StatusEnum.completed.value,
        StatusEnum.completed_late.value,
        StatusEnum.aborted.value,
    ):
        raise EndDowntimeConflictError("STATE_CLOSED_RECORD")

    # Open-downtime guard: count started vs ended events on the append-only log.
    events = get_events_for_operation(db, operation.id)
    started_count = sum(
        1
        for e in events
        if e.event_type == ExecutionEventType.DOWNTIME_STARTED.value
    )
    ended_count = sum(
        1
        for e in events
        if e.event_type == ExecutionEventType.DOWNTIME_ENDED.value
    )
    if started_count <= ended_count:
        raise EndDowntimeConflictError("STATE_NO_OPEN_DOWNTIME")

    ended_at = datetime.utcnow()
    payload = {
        "actor_user_id": actor_user_id,
        "note": getattr(request, "note", None),
        "ended_at": ended_at.isoformat(),
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.DOWNTIME_ENDED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    # INVARIANT: do NOT auto-resume execution. Clearing the downtime blocker
    # only removes one resume precondition; an explicit resume_execution
    # command is still required (station-execution-state-matrix.md RESUME-001).
    #
    # EDGE: start_downtime moves RUNNING→BLOCKED as its policy. Without this
    # step the snapshot would stay BLOCKED after the downtime ends, and
    # resume_execution would reject it with STATE_NOT_PAUSED — the aggregate
    # becomes dead-ended. When no open downtime remains and the sole blocker
    # was this downtime, transition BLOCKED→PAUSED so an explicit
    # resume_execution becomes valid. PAUSED is non-running, so this is
    # state-clearing, not auto-resume.
    no_open_downtime_remains = started_count <= (ended_count + 1)
    if no_open_downtime_remains and operation.status == StatusEnum.blocked.value:
        operation = mark_operation_paused(db, operation)

    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after downtime end event.")

    return derive_operation_detail(db, operation)


def start_downtime(
    db: Session,
    operation,
    request,
    actor_user_id: str,
    tenant_id: str = "default",
) -> OperationDetail:
    """
    Start downtime for an operation. Allowed only if status is RUNNING or PAUSED, no open downtime, not completed/closed.
    Requires valid reason_class. Persists downtime_started event. Updates state per policy.
    """
    from app.models.execution import DowntimeReasonClass, ExecutionEventType
    from app.schemas.operation import OperationStartDowntimeRequest

    if operation.tenant_id != tenant_id:
        raise StartDowntimeConflictError("TENANT_MISMATCH")
    if operation.status not in (StatusEnum.in_progress.value, StatusEnum.paused.value):
        if operation.status in (StatusEnum.completed.value, StatusEnum.completed_late.value, StatusEnum.aborted.value):
            raise StartDowntimeConflictError("STATE_CLOSED")
        raise StartDowntimeConflictError("STATE_NOT_RUNNING_OR_PAUSED")

    # Check for existing open downtime (event log scan, minimal interim logic)
    events = get_events_for_operation(db, operation.id)
    downtime_open = any(e.event_type == ExecutionEventType.DOWNTIME_STARTED.value for e in events)
    if downtime_open:
        raise StartDowntimeConflictError("DOWNTIME_ALREADY_OPEN")

    # Validate reason_class
    if not hasattr(request, "reason_class") or request.reason_class not in DowntimeReasonClass:
        raise StartDowntimeConflictError("INVALID_REASON_CLASS")

    started_at = datetime.utcnow()
    payload = {
        "actor_user_id": actor_user_id,
        "reason_class": request.reason_class,
        "note": getattr(request, "note", None),
        "started_at": started_at.isoformat(),
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.DOWNTIME_STARTED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    # Policy: If PAUSED, stay PAUSED. If RUNNING, become BLOCKED (minimal interim logic).
    if operation.status == StatusEnum.in_progress.value:
        operation.status = StatusEnum.blocked.value
        db.add(operation)
        db.commit()
        db.refresh(operation)

    # Re-read operation for state derivation and return detail.
    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after downtime start event.")

    return derive_operation_detail(db, operation)
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.execution import ExecutionEventType
from app.models.master import StatusEnum
from app.repositories.execution_event_repository import (
    create_execution_event,
    get_events_for_operation,
)
from app.repositories.operation_repository import (
    get_operation_by_id,
    get_in_progress_operations_by_station,
    mark_operation_started,
    mark_operation_reported,
    mark_operation_paused,
    mark_operation_resumed,
    mark_operation_completed,
    mark_operation_aborted,
)
from app.schemas.operation import (
    OperationDetail,
    OperationStartRequest,
    OperationReportQuantityRequest,
    OperationCompleteRequest,
    OperationAbortRequest,
    OperationPauseRequest,
    OperationResumeRequest,
)
from app.services.work_order_execution_service import recompute_work_order


# WHY: Execution state machine: PLANNED→IN_PROGRESS→COMPLETED|ABORTED.
# State is *derived* from the append-only ExecutionEvent log, NOT stored
# directly. The snapshot fields on Operation (status, actual_start, etc.)
# are materialized caches updated in the same transaction for query performance.
class StartOperationConflictError(ValueError):
    pass


class CompleteOperationConflictError(ValueError):
    pass


# Machine-readable rejection codes for pause_execution, per
# station-execution-command-event-contracts.md §10 error families.
class PauseExecutionConflictError(ValueError):
    pass


class ResumeExecutionConflictError(ValueError):
    pass


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


# INTENT: Terminal states (ABORTED, COMPLETED) are checked first because
# they are irreversible — once reached, no subsequent event changes them.
def _derive_status(events: list) -> str:
    if any(event.event_type == ExecutionEventType.OP_ABORTED.value for event in events):
        return StatusEnum.aborted.value
    if any(
        event.event_type == ExecutionEventType.OP_COMPLETED.value for event in events
    ):
        return StatusEnum.completed.value
    if any(event.event_type == ExecutionEventType.OP_STARTED.value for event in events):
        # PAUSED/RUNNING is ordered last-wins between execution_paused and
        # execution_resumed after start. Events are returned chronologically by
        # the repository (created_at, id) so we can rely on iteration order.
        last_runtime_event: str | None = None
        for event in events:
            if event.event_type in (
                ExecutionEventType.EXECUTION_PAUSED.value,
                ExecutionEventType.EXECUTION_RESUMED.value,
            ):
                last_runtime_event = event.event_type
        if last_runtime_event == ExecutionEventType.EXECUTION_PAUSED.value:
            return StatusEnum.paused.value
        return StatusEnum.in_progress.value
    # Current model intentionally converges PLANNED as execution-pending state.
    # UI mapping is responsible for rendering this as Pending/Ready for operators.
    return StatusEnum.planned.value


def _derive_progress(operation_quantity: int, completed_qty: int) -> int:
    if operation_quantity <= 0:
        return 0
    return min(int(completed_qty * 100 / operation_quantity), 100)


def derive_operation_detail(db: Session, operation) -> OperationDetail:
    events = get_events_for_operation(db, operation.id)
    actual_start = None
    actual_end = None
    completed_qty = 0
    good_qty = 0
    scrap_qty = 0
    downtime_started_count = 0
    downtime_ended_count = 0

    for event in events:
        if event.event_type == ExecutionEventType.OP_STARTED.value:
            actual_start = (
                _parse_timestamp(event.payload.get("started_at")) or actual_start
            )
        if event.event_type == ExecutionEventType.OP_COMPLETED.value:
            actual_end = (
                _parse_timestamp(event.payload.get("completed_at")) or actual_end
            )
        if event.event_type == ExecutionEventType.QTY_REPORTED.value:
            good_qty += int(event.payload.get("good_qty", 0))
            scrap_qty += int(event.payload.get("scrap_qty", 0))
        if event.event_type == ExecutionEventType.NG_REPORTED.value:
            scrap_qty += int(event.payload.get("ng_quantity", 0))
        if event.event_type == ExecutionEventType.DOWNTIME_STARTED.value:
            downtime_started_count += 1
        if event.event_type == ExecutionEventType.DOWNTIME_ENDED.value:
            downtime_ended_count += 1

    completed_qty = good_qty + scrap_qty
    status = _derive_status(events)
    progress = _derive_progress(operation.quantity, completed_qty)
    # Source of truth: append-only event log. A downtime is open iff strictly
    # more DOWNTIME_STARTED than DOWNTIME_ENDED events exist. This flag is
    # projection-only and does NOT drive status — callers still use the
    # existing state machine for transitions.
    downtime_open = downtime_started_count > downtime_ended_count

    return OperationDetail(
        id=operation.id,
        operation_number=operation.operation_number,
        name=operation.name,
        sequence=operation.sequence,
        status=status,
        planned_start=operation.planned_start,
        planned_end=operation.planned_end,
        quantity=operation.quantity,
        completed_qty=completed_qty,
        progress=progress,
        work_order_id=operation.work_order_id,
        work_order_number=operation.work_order.work_order_number,
        production_order_id=operation.work_order.production_order_id,
        production_order_number=operation.work_order.production_order.order_number,
        actual_start=actual_start,
        actual_end=actual_end,
        good_qty=good_qty,
        scrap_qty=scrap_qty,
        qc_required=operation.qc_required,
        downtime_open=downtime_open,
    )


def start_operation(
    db: Session, operation, request: OperationStartRequest, tenant_id: str = "default"
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    if operation.status != StatusEnum.planned.value:
        raise StartOperationConflictError("Operation must be PLANNED to start.")

    # EDGE: An operator can only run one operation at a time per station.
    # We scan all IN_PROGRESS operations at the same station and check
    # their OP_STARTED events for a matching operator_id.
    operator_id = (request.operator_id or "").strip()
    if operator_id:
        running_candidates = get_in_progress_operations_by_station(
            db,
            tenant_id=tenant_id,
            station_scope_value=operation.station_scope_value,
            exclude_operation_id=operation.id,
        )
        for running_op in running_candidates:
            running_events = get_events_for_operation(db, running_op.id)
            for event in running_events:
                if event.event_type != ExecutionEventType.OP_STARTED.value:
                    continue
                event_operator_id = str(event.payload.get("operator_id") or "").strip()
                if event_operator_id == operator_id:
                    raise StartOperationConflictError(
                        "Operator already has a RUNNING operation at this station."
                    )

    start_time = request.started_at or datetime.utcnow()
    payload = {
        "operator_id": request.operator_id,
        "started_at": start_time.isoformat(),
    }

    # INVARIANT: Event is appended before the snapshot is updated.
    # The event log is the source of truth; the snapshot is a cache.
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.OP_STARTED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    # Snapshot update (derived state) in service layer only.
    operation = mark_operation_started(db, operation, start_time)
    recompute_work_order(db, operation.work_order_id)

    # Re-read operation for state derivation and return detail.
    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after event creation.")

    return derive_operation_detail(db, operation)


def report_quantity(
    db: Session,
    operation,
    request: OperationReportQuantityRequest,
    tenant_id: str = "default",
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    if operation.status != StatusEnum.in_progress.value:
        raise ValueError("Operation must be IN_PROGRESS to report quantity.")

    if request.good_qty < 0 or request.scrap_qty < 0:
        raise ValueError("Quantities must be non-negative.")

    if request.good_qty + request.scrap_qty <= 0:
        raise ValueError(
            "At least one of good_qty or scrap_qty must be greater than zero."
        )

    payload = {
        "operator_id": request.operator_id,
        "good_qty": request.good_qty,
        "scrap_qty": request.scrap_qty,
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.QTY_REPORTED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    # Snapshot update as derived state in service.
    operation = mark_operation_reported(
        db, operation, request.good_qty, request.scrap_qty
    )

    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after quantity report event")

    return derive_operation_detail(db, operation)


def complete_operation(
    db: Session,
    operation,
    request: OperationCompleteRequest,
    tenant_id: str = "default",
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    # EDGE: Two-step status check gives distinct error messages — a COMPLETED
    # operation gets a "cannot complete again" error, while a PLANNED one
    # gets "must be IN_PROGRESS". This helps operators diagnose issues.
    if operation.status == StatusEnum.completed.value:
        raise CompleteOperationConflictError(
            "Operation already completed; cannot complete again."
        )
    if operation.status != StatusEnum.in_progress.value:
        raise CompleteOperationConflictError(
            "Operation must be IN_PROGRESS to complete."
        )

    completed_at = request.completed_at or datetime.utcnow()
    payload = {
        "operator_id": request.operator_id,
        "completed_at": completed_at.isoformat(),
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.OP_COMPLETED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    # Snapshot update (derived state) in service layer.
    operation = mark_operation_completed(db, operation, completed_at)
    recompute_work_order(db, operation.work_order_id)

    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after completion event")

    return derive_operation_detail(db, operation)


def pause_operation(
    db: Session,
    operation,
    request: OperationPauseRequest,
    *,
    actor_user_id: str,
    tenant_id: str = "default",
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")

    # State guard per station-execution-state-matrix.md PAUSE-001:
    # allowed only when execution_status = RUNNING and closure_status = OPEN.
    # Machine-readable rejection codes follow contracts §10 STATE_* family.
    if operation.status in (
        StatusEnum.completed.value,
        StatusEnum.completed_late.value,
        StatusEnum.aborted.value,
    ):
        raise PauseExecutionConflictError("STATE_CLOSED")
    if operation.status == StatusEnum.paused.value:
        raise PauseExecutionConflictError("STATE_ALREADY_PAUSED")
    if operation.status != StatusEnum.in_progress.value:
        raise PauseExecutionConflictError("STATE_NOT_RUNNING")

    paused_at = datetime.utcnow()
    payload = {
        "actor_user_id": actor_user_id,
        "reason_code": request.reason_code,
        "note": request.note,
        "paused_at": paused_at.isoformat(),
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.EXECUTION_PAUSED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    operation = mark_operation_paused(db, operation)

    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after pause event")

    return derive_operation_detail(db, operation)


def resume_operation(
    db: Session,
    operation,
    request: OperationResumeRequest,
    *,
    actor_user_id: str,
    tenant_id: str = "default",
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")

    # State guard per station-execution-state-matrix.md RESUME-001:
    # allowed only when execution_status = PAUSED, closure_status = OPEN, and
    # no downtime is currently open. Remaining canonical blockers (QC hold,
    # review pending) are deferred until those state dimensions are modeled.
    if operation.status in (
        StatusEnum.completed.value,
        StatusEnum.completed_late.value,
        StatusEnum.aborted.value,
    ):
        raise ResumeExecutionConflictError("STATE_CLOSED")

    # Open-downtime guard. Source of truth is the append-only event log
    # (DOWNTIME_STARTED > DOWNTIME_ENDED ⇒ downtime open). Checked ahead of
    # STATE_NOT_PAUSED so that a BLOCKED-with-open-downtime record rejects
    # with the actionable code (end the downtime first) rather than a
    # confusing STATE_NOT_PAUSED. A PAUSED-with-open-downtime record (downtime
    # started while already PAUSED) is also caught here, which is the
    # correctness-critical case end_downtime's BLOCKED→PAUSED transition
    # cannot cover.
    events = get_events_for_operation(db, operation.id)
    downtime_started_count = sum(
        1
        for e in events
        if e.event_type == ExecutionEventType.DOWNTIME_STARTED.value
    )
    downtime_ended_count = sum(
        1
        for e in events
        if e.event_type == ExecutionEventType.DOWNTIME_ENDED.value
    )
    if downtime_started_count > downtime_ended_count:
        raise ResumeExecutionConflictError("STATE_DOWNTIME_OPEN")

    if operation.status != StatusEnum.paused.value:
        raise ResumeExecutionConflictError("STATE_NOT_PAUSED")

    # Competing running execution at same station (canonical: "no other execution
    # already running"). An operation with status IN_PROGRESS is actively running;
    # paused peers are fine.
    competing = get_in_progress_operations_by_station(
        db,
        tenant_id=tenant_id,
        station_scope_value=operation.station_scope_value,
        exclude_operation_id=operation.id,
    )
    if competing:
        raise ResumeExecutionConflictError("STATE_STATION_BUSY")

    resumed_at = datetime.utcnow()
    payload = {
        "actor_user_id": actor_user_id,
        "note": request.note,
        "resumed_at": resumed_at.isoformat(),
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.EXECUTION_RESUMED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    operation = mark_operation_resumed(db, operation)

    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after resume event")

    return derive_operation_detail(db, operation)


def abort_operation(
    db: Session,
    operation,
    request: OperationAbortRequest,
    tenant_id: str = "default",
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    if operation.status in (StatusEnum.completed.value, StatusEnum.aborted.value):
        raise ValueError("Operation already completed or aborted; cannot abort.")

    aborted_at = datetime.utcnow()
    payload = {
        "operator_id": request.operator_id,
        "reason_code": request.reason_code,
        "aborted_at": aborted_at.isoformat(),
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.OP_ABORTED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    operation = mark_operation_aborted(db, operation, aborted_at)
    recompute_work_order(db, operation.work_order_id)

    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after abort event")

    return derive_operation_detail(db, operation)

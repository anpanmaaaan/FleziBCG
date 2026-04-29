from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import case, func as sa_func, select
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import ClosureStatusEnum, Operation, StatusEnum
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.repositories.downtime_reason_repository import get_downtime_reason_by_code
from app.repositories.execution_event_repository import (
    create_execution_event,
    get_events_for_operation,
)
from app.repositories.operation_repository import (
    get_in_progress_operations_by_station,
    get_operation_by_id,
    mark_operation_aborted,
    mark_operation_closed,
    mark_operation_completed,
    mark_operation_paused,
    mark_operation_reported,
    mark_operation_reopened,
    mark_operation_resumed,
    mark_operation_started,
)
from app.schemas.operation import (
    OperationAbortRequest,
    OperationCloseRequest,
    OperationCompleteRequest,
    OperationDetail,
    OperationPauseRequest,
    OperationReopenRequest,
    OperationReportQuantityRequest,
    OperationResumeRequest,
    OperationStartRequest,
)
from app.services.work_order_execution_service import recompute_work_order


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
    if operation.tenant_id != tenant_id:
        raise EndDowntimeConflictError("TENANT_MISMATCH")
    _ensure_operation_open_for_write(operation)

    # Open-downtime guard: count started vs ended events on the append-only log.
    events = get_events_for_operation(db, operation.id)
    started_count = sum(
        1 for e in events if e.event_type == ExecutionEventType.DOWNTIME_STARTED.value
    )
    ended_count = sum(
        1 for e in events if e.event_type == ExecutionEventType.DOWNTIME_ENDED.value
    )
    if started_count <= ended_count:
        raise EndDowntimeConflictError("STATE_NO_OPEN_DOWNTIME")

    ended_at = _utcnow_naive()
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
    Start downtime for an operation. Allowed only if status is RUNNING or
    PAUSED, no open downtime, and the operation record is not closed.
    Requires a valid, active DB-backed `reason_code` from the
    `downtime_reasons` master-data table. Persists `downtime_started` event
    and updates state per policy.
    """
    if operation.tenant_id != tenant_id:
        raise StartDowntimeConflictError("TENANT_MISMATCH")
    _ensure_operation_open_for_write(operation)
    if operation.status not in (StatusEnum.in_progress.value, StatusEnum.paused.value):
        raise StartDowntimeConflictError("STATE_NOT_RUNNING_OR_PAUSED")

    # Open-downtime truth is append-only-log based: open iff
    # DOWNTIME_STARTED count > DOWNTIME_ENDED count.
    events = get_events_for_operation(db, operation.id)
    downtime_started_count = sum(
        1 for e in events if e.event_type == ExecutionEventType.DOWNTIME_STARTED.value
    )
    downtime_ended_count = sum(
        1 for e in events if e.event_type == ExecutionEventType.DOWNTIME_ENDED.value
    )
    downtime_open = downtime_started_count > downtime_ended_count
    if downtime_open:
        raise StartDowntimeConflictError("DOWNTIME_ALREADY_OPEN")

    # Reason is resolved only from DB-backed master data. The request schema
    # already guarantees a non-blank reason_code, so a missing value here
    # would be a programming error, not a user input error.
    reason_code = (getattr(request, "reason_code", None) or "").strip()
    if not reason_code:
        raise StartDowntimeConflictError("INVALID_REASON_CODE")

    reason = get_downtime_reason_by_code(
        db, tenant_id=operation.tenant_id, reason_code=reason_code
    )
    if reason is None:
        raise StartDowntimeConflictError("INVALID_REASON_CODE")
    if not reason.active_flag:
        raise StartDowntimeConflictError("INACTIVE_REASON")

    started_at = _utcnow_naive()
    payload = {
        "actor_user_id": actor_user_id,
        "reason_code": reason.reason_code,
        "reason_name": reason.reason_name,
        "reason_group": reason.reason_group,
        "planned_flag": reason.planned_flag,
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


def _utcnow_naive() -> datetime:
    # datetime.utcnow() is deprecated; emit a timezone-aware UTC instant and
    # strip the tzinfo so it still lands cleanly in naive DateTime columns
    # (planned_start, actual_start, etc.) without changing storage semantics.
    return datetime.now(timezone.utc).replace(tzinfo=None)


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


class ClosedRecordConflictError(ValueError):
    pass


class CloseOperationConflictError(ValueError):
    pass


class ReopenOperationConflictError(ValueError):
    pass


def _ensure_operation_open_for_write(operation) -> None:
    if operation.closure_status == ClosureStatusEnum.closed.value:
        raise ClosedRecordConflictError("STATE_CLOSED_RECORD")


def _restore_claim_continuity_for_reopen(db: Session, *, operation, tenant_id: str) -> None:
    now = datetime.now(timezone.utc)
    active_claim = db.scalar(
        select(OperationClaim)
        .where(
            OperationClaim.tenant_id == tenant_id,
            OperationClaim.operation_id == operation.id,
            OperationClaim.released_at.is_(None),
        )
        .order_by(OperationClaim.id.desc())
        .with_for_update()
    )
    if active_claim is not None:
        extended_expiry = max(
            active_claim.expires_at,
            now + timedelta(minutes=settings.claim_default_ttl_minutes),
        )
        if extended_expiry != active_claim.expires_at:
            active_claim.expires_at = extended_expiry
            db.add(active_claim)
            db.flush()
        return

    last_claim = db.scalar(
        select(OperationClaim)
        .where(
            OperationClaim.tenant_id == tenant_id,
            OperationClaim.operation_id == operation.id,
        )
        .order_by(OperationClaim.claimed_at.desc(), OperationClaim.id.desc())
        .with_for_update()
    )
    if last_claim is None:
        return

    conflicting_claim = db.scalar(
        select(OperationClaim)
        .where(
            OperationClaim.tenant_id == tenant_id,
            OperationClaim.claimed_by_user_id == last_claim.claimed_by_user_id,
            OperationClaim.station_scope_id == last_claim.station_scope_id,
            OperationClaim.released_at.is_(None),
            OperationClaim.operation_id != operation.id,
        )
        .order_by(OperationClaim.id.desc())
        .with_for_update()
    )
    if conflicting_claim is not None and conflicting_claim.expires_at > now:
        raise ReopenOperationConflictError("STATE_REOPEN_OWNER_HAS_OTHER_ACTIVE_CLAIM")

    restored_claim = OperationClaim(
        tenant_id=tenant_id,
        operation_id=operation.id,
        station_scope_id=last_claim.station_scope_id,
        claimed_by_user_id=last_claim.claimed_by_user_id,
        claimed_at=now,
        expires_at=now + timedelta(minutes=settings.claim_default_ttl_minutes),
    )
    db.add(restored_claim)
    db.flush()
    db.add(
        OperationClaimAuditLog(
            claim_id=restored_claim.id,
            tenant_id=tenant_id,
            operation_id=operation.id,
            station_scope_id=last_claim.station_scope_id,
            actor_user_id=last_claim.claimed_by_user_id,
            acting_role_code=None,
            event_type="CLAIM_RESTORED_ON_REOPEN",
            reason="reopen claim continuity restored",
        )
    )
    db.flush()


@dataclass(frozen=True)
class OperationRuntimeProjection:
    status: str
    downtime_open: bool


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _normalize_dt(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.replace(tzinfo=None)
    return value


def _event_timestamp(event, payload_keys: tuple[str, ...]) -> Optional[datetime]:
    payload = event.payload if isinstance(event.payload, dict) else {}
    for key in payload_keys:
        parsed = _parse_timestamp(payload.get(key))
        if parsed is not None:
            return _normalize_dt(parsed)
    return _normalize_dt(getattr(event, "created_at", None))


def _accumulate_event_interval_ms(
    events: list,
    *,
    start_event_type: str,
    end_event_type: str,
    start_payload_keys: tuple[str, ...],
    end_payload_keys: tuple[str, ...],
    now_naive: datetime,
) -> int:
    total_ms = 0
    open_started_at: datetime | None = None

    for event in events:
        if event.event_type == start_event_type:
            started_at = _event_timestamp(event, start_payload_keys)
            if started_at is not None and open_started_at is None:
                open_started_at = started_at
            continue

        if event.event_type != end_event_type:
            continue

        ended_at = _event_timestamp(event, end_payload_keys)
        if open_started_at is None or ended_at is None:
            open_started_at = None
            continue

        if ended_at > open_started_at:
            total_ms += int((ended_at - open_started_at).total_seconds() * 1000)
        open_started_at = None

    if open_started_at is not None and now_naive > open_started_at:
        total_ms += int((now_naive - open_started_at).total_seconds() * 1000)

    return total_ms


_RUNTIME_EVENT_TYPES_FOR_LAST_SIGNAL = (
    ExecutionEventType.EXECUTION_PAUSED.value,
    ExecutionEventType.EXECUTION_RESUMED.value,
    ExecutionEventType.DOWNTIME_ENDED.value,
    ExecutionEventType.OP_COMPLETED.value,
    ExecutionEventType.OP_ABORTED.value,
    ExecutionEventType.OPERATION_REOPENED.value,
)


def _derive_status_from_runtime_facts(
    *,
    has_started: bool,
    has_completed: bool,
    has_aborted: bool,
    downtime_started_count: int,
    downtime_ended_count: int,
    last_runtime_event: str | None,
) -> str:
    if has_aborted:
        return StatusEnum.aborted.value
    if has_completed:
        if last_runtime_event in (
            ExecutionEventType.OPERATION_REOPENED.value,
            ExecutionEventType.EXECUTION_PAUSED.value,
            ExecutionEventType.DOWNTIME_ENDED.value,
        ):
            return StatusEnum.paused.value
        if last_runtime_event == ExecutionEventType.EXECUTION_RESUMED.value:
            return StatusEnum.in_progress.value
        return StatusEnum.completed.value
    if has_started:
        if downtime_started_count > downtime_ended_count:
            return StatusEnum.blocked.value
        if last_runtime_event in (
            ExecutionEventType.EXECUTION_PAUSED.value,
            ExecutionEventType.DOWNTIME_ENDED.value,
        ):
            return StatusEnum.paused.value
        return StatusEnum.in_progress.value
    return StatusEnum.planned.value


def derive_operation_runtime_projection_for_ids(
    db: Session,
    *,
    tenant_id: str,
    operation_ids: list[int],
) -> dict[int, OperationRuntimeProjection]:
    if not operation_ids:
        return {}

    started_sum = sa_func.sum(
        case(
            (ExecutionEvent.event_type == ExecutionEventType.OP_STARTED.value, 1),
            else_=0,
        )
    )
    completed_sum = sa_func.sum(
        case(
            (ExecutionEvent.event_type == ExecutionEventType.OP_COMPLETED.value, 1),
            else_=0,
        )
    )
    aborted_sum = sa_func.sum(
        case(
            (ExecutionEvent.event_type == ExecutionEventType.OP_ABORTED.value, 1),
            else_=0,
        )
    )
    downtime_started_sum = sa_func.sum(
        case(
            (
                ExecutionEvent.event_type == ExecutionEventType.DOWNTIME_STARTED.value,
                1,
            ),
            else_=0,
        )
    )
    downtime_ended_sum = sa_func.sum(
        case(
            (ExecutionEvent.event_type == ExecutionEventType.DOWNTIME_ENDED.value, 1),
            else_=0,
        )
    )

    counts_rows = db.execute(
        select(
            ExecutionEvent.operation_id,
            started_sum.label("started_count"),
            completed_sum.label("completed_count"),
            aborted_sum.label("aborted_count"),
            downtime_started_sum.label("downtime_started_count"),
            downtime_ended_sum.label("downtime_ended_count"),
        )
        .where(
            ExecutionEvent.tenant_id == tenant_id,
            ExecutionEvent.operation_id.in_(operation_ids),
            ExecutionEvent.event_type.in_(
                [
                    ExecutionEventType.OP_STARTED.value,
                    ExecutionEventType.OP_COMPLETED.value,
                    ExecutionEventType.OP_ABORTED.value,
                    ExecutionEventType.DOWNTIME_STARTED.value,
                    ExecutionEventType.DOWNTIME_ENDED.value,
                ]
            ),
        )
        .group_by(ExecutionEvent.operation_id)
    ).all()

    counts_by_operation_id: dict[int, dict[str, int]] = {
        operation_id: {
            "started_count": 0,
            "completed_count": 0,
            "aborted_count": 0,
            "downtime_started_count": 0,
            "downtime_ended_count": 0,
        }
        for operation_id in operation_ids
    }
    for (
        operation_id,
        started_count,
        completed_count,
        aborted_count,
        downtime_started_count,
        downtime_ended_count,
    ) in counts_rows:
        counts_by_operation_id[operation_id] = {
            "started_count": int(started_count or 0),
            "completed_count": int(completed_count or 0),
            "aborted_count": int(aborted_count or 0),
            "downtime_started_count": int(downtime_started_count or 0),
            "downtime_ended_count": int(downtime_ended_count or 0),
        }

    runtime_signal_subquery = (
        select(
            ExecutionEvent.operation_id.label("operation_id"),
            ExecutionEvent.event_type.label("event_type"),
            sa_func.row_number()
            .over(
                partition_by=ExecutionEvent.operation_id,
                order_by=(ExecutionEvent.created_at.desc(), ExecutionEvent.id.desc()),
            )
            .label("row_num"),
        )
        .where(
            ExecutionEvent.tenant_id == tenant_id,
            ExecutionEvent.operation_id.in_(operation_ids),
            ExecutionEvent.event_type.in_(_RUNTIME_EVENT_TYPES_FOR_LAST_SIGNAL),
        )
        .subquery()
    )

    runtime_signal_rows = db.execute(
        select(
            runtime_signal_subquery.c.operation_id,
            runtime_signal_subquery.c.event_type,
        ).where(runtime_signal_subquery.c.row_num == 1)
    ).all()
    last_runtime_event_by_operation_id: dict[int, str] = {
        operation_id: event_type for operation_id, event_type in runtime_signal_rows
    }

    projection_by_operation_id: dict[int, OperationRuntimeProjection] = {}
    for operation_id in operation_ids:
        counts = counts_by_operation_id[operation_id]
        status = _derive_status_from_runtime_facts(
            has_started=counts["started_count"] > 0,
            has_completed=counts["completed_count"] > 0,
            has_aborted=counts["aborted_count"] > 0,
            downtime_started_count=counts["downtime_started_count"],
            downtime_ended_count=counts["downtime_ended_count"],
            last_runtime_event=last_runtime_event_by_operation_id.get(operation_id),
        )
        projection_by_operation_id[operation_id] = OperationRuntimeProjection(
            status=status,
            downtime_open=(
                counts["downtime_started_count"] > counts["downtime_ended_count"]
            ),
        )
    return projection_by_operation_id


def reconcile_operation_status_projection(
    db: Session,
    *,
    operation,
    tenant_id: str,
):
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    projection = derive_operation_runtime_projection_for_ids(
        db,
        tenant_id=tenant_id,
        operation_ids=[operation.id],
    ).get(operation.id)
    if projection is None:
        return operation
    if operation.status != projection.status:
        operation.status = projection.status
        db.add(operation)
        db.commit()
        db.refresh(operation)
    return operation


def detect_operation_status_projection_mismatches(
    db: Session,
    *,
    tenant_id: str,
    operation_ids: list[int],
) -> list[dict[str, str | int]]:
    projection_by_operation_id = derive_operation_runtime_projection_for_ids(
        db,
        tenant_id=tenant_id,
        operation_ids=operation_ids,
    )
    operations = list(
        db.scalars(
            select(Operation).where(
                Operation.tenant_id == tenant_id,
                Operation.id.in_(operation_ids),
            )
        )
    )
    mismatches: list[dict[str, str | int]] = []
    for operation in operations:
        projection = projection_by_operation_id.get(operation.id)
        if projection is None:
            continue
        if operation.status == projection.status:
            continue
        mismatches.append(
            {
                "operation_id": operation.id,
                "operation_number": operation.operation_number,
                "snapshot_status": operation.status,
                "derived_status": projection.status,
            }
        )
    return mismatches


# INTENT: Terminal states (ABORTED, COMPLETED) are checked first because
# they are irreversible — once reached, no subsequent event changes them.
def _derive_status(events: list) -> str:
    # An open downtime (DOWNTIME_STARTED > DOWNTIME_ENDED on the append-only
    # log) is a runtime blocker and wins over PAUSED/RUNNING. end_downtime
    # does not auto-resume — an explicit resume_execution is still required
    # to leave the non-running state (station-execution-state-matrix.md).
    #
    # Runtime state is last-wins between four signals, tracked in arrival
    # order (events arrive chronologically from the repository):
    #   EXECUTION_PAUSED  → non-running (explicit pause)
    #   EXECUTION_RESUMED → running
    #   DOWNTIME_STARTED  → counted toward the open-downtime check
    #   DOWNTIME_ENDED    → non-running (end_downtime transitions
    #                       BLOCKED→PAUSED on the snapshot and never
    #                       auto-resumes; a matching PAUSED→PAUSED case
    #                       also trivially holds).
    started_count = 0
    completed_count = 0
    aborted_count = 0
    downtime_started_count = 0
    downtime_ended_count = 0
    last_runtime_event: str | None = None
    for event in events:
        if event.event_type == ExecutionEventType.OP_STARTED.value:
            started_count += 1
        elif event.event_type == ExecutionEventType.OP_COMPLETED.value:
            completed_count += 1
            last_runtime_event = event.event_type
        elif event.event_type == ExecutionEventType.OP_ABORTED.value:
            aborted_count += 1
            last_runtime_event = event.event_type
        elif event.event_type == ExecutionEventType.DOWNTIME_STARTED.value:
            downtime_started_count += 1
        elif event.event_type == ExecutionEventType.DOWNTIME_ENDED.value:
            downtime_ended_count += 1
            last_runtime_event = event.event_type
        elif event.event_type in (
            ExecutionEventType.EXECUTION_PAUSED.value,
            ExecutionEventType.EXECUTION_RESUMED.value,
            ExecutionEventType.OPERATION_REOPENED.value,
        ):
            last_runtime_event = event.event_type
    return _derive_status_from_runtime_facts(
        has_started=started_count > 0,
        has_completed=completed_count > 0,
        has_aborted=aborted_count > 0,
        downtime_started_count=downtime_started_count,
        downtime_ended_count=downtime_ended_count,
        last_runtime_event=last_runtime_event,
    )


def _derive_progress(operation_quantity: int, completed_qty: int) -> int:
    if operation_quantity <= 0:
        return 0
    return min(int(completed_qty * 100 / operation_quantity), 100)


# Mirrors the guards in start_operation / report_quantity / pause_operation /
# resume_operation / complete_operation / start_downtime / end_downtime.
# Identity-scoped guards (claim ownership, station-busy competition) are NOT
# encoded — the command handlers still enforce those at request time.
# Canonical names per station-execution-command-event-contracts.md §3.
_CLOSED_STATUSES = frozenset(
    {
        StatusEnum.aborted.value,
    }
)


def _derive_allowed_actions(
    status: str,
    downtime_open: bool,
    closure_status: str = ClosureStatusEnum.open.value,
) -> list[str]:
    if closure_status == ClosureStatusEnum.closed.value:
        return ["reopen_operation"]

    if status in _CLOSED_STATUSES:
        return []

    actions: list[str] = []

    if status == StatusEnum.planned.value:
        actions.append("start_execution")
        return actions

    if status == StatusEnum.in_progress.value:
        # report_quantity / pause_operation / complete_operation each require
        # status == IN_PROGRESS and nothing else at the snapshot level.
        actions.append("report_production")
        actions.append("pause_execution")
        actions.append("complete_execution")

    if status == StatusEnum.paused.value and not downtime_open:
        actions.append("resume_execution")

    if (
        status in (StatusEnum.in_progress.value, StatusEnum.paused.value)
        and not downtime_open
    ):
        actions.append("start_downtime")

    if downtime_open:
        actions.append("end_downtime")

    if status in (StatusEnum.completed.value, StatusEnum.completed_late.value):
        actions.append("close_operation")

    return actions


def derive_operation_detail(db: Session, operation) -> OperationDetail:
    events = get_events_for_operation(db, operation.id)
    now_naive = _utcnow_naive()
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
    # Detail semantics must be internally consistent: action affordances are
    # derived from the same runtime-truth status exposed in `status`, not from
    # potentially stale snapshot projection on operation.status.
    allowed_actions = _derive_allowed_actions(
        status,
        downtime_open,
        operation.closure_status,
    )
    paused_total_ms = _accumulate_event_interval_ms(
        events,
        start_event_type=ExecutionEventType.EXECUTION_PAUSED.value,
        end_event_type=ExecutionEventType.EXECUTION_RESUMED.value,
        start_payload_keys=("paused_at",),
        end_payload_keys=("resumed_at",),
        now_naive=now_naive,
    )
    downtime_total_ms = _accumulate_event_interval_ms(
        events,
        start_event_type=ExecutionEventType.DOWNTIME_STARTED.value,
        end_event_type=ExecutionEventType.DOWNTIME_ENDED.value,
        start_payload_keys=("started_at",),
        end_payload_keys=("ended_at",),
        now_naive=now_naive,
    )

    return OperationDetail(
        id=operation.id,
        operation_number=operation.operation_number,
        name=operation.name,
        sequence=operation.sequence,
        status=status,
        closure_status=operation.closure_status,
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
        allowed_actions=allowed_actions,
        paused_total_ms=paused_total_ms,
        downtime_total_ms=downtime_total_ms,
        reopen_count=operation.reopen_count,
        last_reopened_at=operation.last_reopened_at,
        last_reopened_by=operation.last_reopened_by,
        last_closed_at=operation.last_closed_at,
        last_closed_by=operation.last_closed_by,
    )


def close_operation(
    db: Session,
    operation,
    request: OperationCloseRequest,
    *,
    actor_user_id: str,
    tenant_id: str = "default",
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    if operation.closure_status == ClosureStatusEnum.closed.value:
        raise CloseOperationConflictError("STATE_ALREADY_CLOSED")

    detail = derive_operation_detail(db, operation)
    if detail.status not in (
        StatusEnum.completed.value,
        StatusEnum.completed_late.value,
    ):
        raise CloseOperationConflictError("STATE_NOT_COMPLETED")

    closed_at = _utcnow_naive()
    payload = {
        "actor_user_id": actor_user_id,
        "note": request.note,
        "closed_at": closed_at.isoformat(),
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.OPERATION_CLOSED_AT_STATION.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    operation = mark_operation_closed(
        db,
        operation,
        closed_at=closed_at,
        closed_by=actor_user_id,
    )
    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after close event")
    return derive_operation_detail(db, operation)


def reopen_operation(
    db: Session,
    operation,
    request: OperationReopenRequest,
    *,
    actor_user_id: str,
    tenant_id: str = "default",
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    if operation.closure_status != ClosureStatusEnum.closed.value:
        raise ReopenOperationConflictError("STATE_NOT_CLOSED")

    reason = (request.reason or "").strip()
    if not reason:
        raise ReopenOperationConflictError("REOPEN_REASON_REQUIRED")

    _restore_claim_continuity_for_reopen(db, operation=operation, tenant_id=tenant_id)

    reopened_at = _utcnow_naive()
    payload = {
        "actor_user_id": actor_user_id,
        "reason": reason,
        "reopened_at": reopened_at.isoformat(),
    }

    create_execution_event(
        db=db,
        event_type=ExecutionEventType.OPERATION_REOPENED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    operation = mark_operation_reopened(
        db,
        operation,
        reopened_at=reopened_at,
        reopened_by=actor_user_id,
    )
    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after reopen event")
    return derive_operation_detail(db, operation)


def start_operation(
    db: Session, operation, request: OperationStartRequest, tenant_id: str = "default"
) -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    _ensure_operation_open_for_write(operation)
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

    start_time = request.started_at or _utcnow_naive()
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
    _ensure_operation_open_for_write(operation)
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
    _ensure_operation_open_for_write(operation)
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

    completed_at = request.completed_at or _utcnow_naive()
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
    _ensure_operation_open_for_write(operation)

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

    paused_at = _utcnow_naive()
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
    _ensure_operation_open_for_write(operation)

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
        1 for e in events if e.event_type == ExecutionEventType.DOWNTIME_STARTED.value
    )
    downtime_ended_count = sum(
        1 for e in events if e.event_type == ExecutionEventType.DOWNTIME_ENDED.value
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

    resumed_at = _utcnow_naive()
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
    _ensure_operation_open_for_write(operation)
    if operation.status in (StatusEnum.completed.value, StatusEnum.aborted.value):
        raise ValueError("Operation already completed or aborted; cannot abort.")

    aborted_at = _utcnow_naive()
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

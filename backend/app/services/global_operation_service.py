from datetime import datetime, timezone
from math import sqrt

from sqlalchemy.orm import Session

from app.models.master import StatusEnum
from app.repositories.operation_repository import (
    get_operations_by_names,
    get_operations_by_work_order,
)
from app.schemas.operation import OperationListItem

# INTENT: Domain heuristic constants for supervisor alerting. These are
# business-tunable thresholds, not arbitrary magic numbers.
REPEAT_DELAY_MIN_COUNT = 2
OFTEN_LATE_FREQUENCY_THRESHOLD = 0.5
HIGH_VARIANCE_STDDEV_THRESHOLD_MINUTES = 20


def _derive_progress(quantity: int, completed_qty: int) -> int:
    if quantity <= 0:
        return 0
    return min(int((completed_qty * 100) / quantity), 100)


def _derive_delay_minutes(
    status: str, planned_end: datetime | None, actual_end: datetime | None
) -> int | None:
    if planned_end is None:
        return None

    if status == StatusEnum.completed.value and actual_end is not None:
        reference_time = actual_end
    elif status in (
        StatusEnum.in_progress.value,
        StatusEnum.late.value,
        StatusEnum.blocked.value,
    ):
        reference_time = datetime.now(timezone.utc)
    else:
        return None

    if reference_time.tzinfo is None and planned_end.tzinfo is not None:
        reference_time = reference_time.replace(tzinfo=planned_end.tzinfo)
    if reference_time.tzinfo is not None and planned_end.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=None)

    delay = int((reference_time - planned_end).total_seconds() / 60)
    return max(delay, 0)


def _derive_cycle_time_minutes(
    actual_start: datetime | None, actual_end: datetime | None
) -> int | None:
    if actual_start is None or actual_end is None:
        return None

    if actual_end.tzinfo is None and actual_start.tzinfo is not None:
        actual_end = actual_end.replace(tzinfo=actual_start.tzinfo)
    if actual_end.tzinfo is not None and actual_start.tzinfo is None:
        actual_end = actual_end.replace(tzinfo=None)

    cycle_minutes = int((actual_end - actual_start).total_seconds() / 60)
    return max(cycle_minutes, 0)


def _derive_planned_cycle_minutes(
    planned_start: datetime | None, planned_end: datetime | None
) -> int | None:
    if planned_start is None or planned_end is None:
        return None

    if planned_end.tzinfo is None and planned_start.tzinfo is not None:
        planned_end = planned_end.replace(tzinfo=planned_start.tzinfo)
    if planned_end.tzinfo is not None and planned_start.tzinfo is None:
        planned_end = planned_end.replace(tzinfo=None)

    planned_minutes = int((planned_end - planned_start).total_seconds() / 60)
    return max(planned_minutes, 0)


def _derive_cycle_time_delta(operation) -> int | None:
    cycle_minutes = _derive_cycle_time_minutes(
        operation.actual_start, operation.actual_end
    )
    planned_cycle_minutes = _derive_planned_cycle_minutes(
        operation.planned_start, operation.planned_end
    )

    if cycle_minutes is None or planned_cycle_minutes is None:
        return None

    return cycle_minutes - planned_cycle_minutes


def _derive_stddev(values: list[int]) -> float:
    if len(values) <= 1:
        return 0

    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return sqrt(variance)


def _derive_supervisor_bucket(status: str, delay_minutes: int | None) -> str:
    if status == StatusEnum.blocked.value:
        return "BLOCKED"
    if status == StatusEnum.late.value:
        return "DELAYED"
    if (
        delay_minutes is not None
        and delay_minutes > 0
        and status
        in (
            StatusEnum.in_progress.value,
            StatusEnum.completed.value,
        )
    ):
        return "DELAYED"
    if status == StatusEnum.in_progress.value:
        return "IN_PROGRESS"
    return "OTHER"


def build_work_order_operation_summaries(
    db: Session, work_order_id: int
) -> list[OperationListItem]:
    operations = get_operations_by_work_order(db, work_order_id)
    process_step_names = sorted({operation.name for operation in operations})
    historical_operations = get_operations_by_names(db, process_step_names)

    history_by_process_step: dict[str, list] = {name: [] for name in process_step_names}
    for historical_operation in historical_operations:
        history_by_process_step.setdefault(historical_operation.name, []).append(
            historical_operation
        )

    operation_projections = []
    for operation in operations:
        delay_minutes = _derive_delay_minutes(
            operation.status, operation.planned_end, operation.actual_end
        )
        supervisor_bucket = _derive_supervisor_bucket(operation.status, delay_minutes)

        operation_history = history_by_process_step.get(operation.name, [])
        historical_delay_minutes = [
            _derive_delay_minutes(item.status, item.planned_end, item.actual_end)
            for item in operation_history
        ]
        delayed_count = sum(
            1 for value in historical_delay_minutes if value is not None and value > 0
        )
        history_total = len(operation_history)
        delay_frequency = (delayed_count / history_total) if history_total > 0 else 0

        historical_cycle_minutes = [
            _derive_cycle_time_minutes(item.actual_start, item.actual_end)
            for item in operation_history
        ]
        historical_cycle_minutes = [
            value for value in historical_cycle_minutes if value is not None
        ]

        historical_cycle_deltas = [
            _derive_cycle_time_delta(item) for item in operation_history
        ]
        historical_cycle_deltas = [
            value for value in historical_cycle_deltas if value is not None
        ]

        cycle_time_delta = _derive_cycle_time_delta(operation)
        cycle_time_minutes = _derive_cycle_time_minutes(
            operation.actual_start, operation.actual_end
        )
        qc_fail_count = sum(
            1 for item in operation_history if (item.scrap_qty or 0) > 0
        )

        operation_projections.append(
            (
                operation,
                delay_minutes,
                supervisor_bucket,
                cycle_time_minutes,
                cycle_time_delta,
                delayed_count,
                delay_frequency,
                history_total >= REPEAT_DELAY_MIN_COUNT,
                qc_fail_count,
                _derive_stddev([int(value) for value in historical_cycle_minutes])
                >= HIGH_VARIANCE_STDDEV_THRESHOLD_MINUTES,
                delay_frequency >= OFTEN_LATE_FREQUENCY_THRESHOLD,
            )
        )

    wo_blocked_operations = sum(
        1 for _, _, bucket, *_ in operation_projections if bucket == "BLOCKED"
    )
    wo_delayed_operations = sum(
        1 for _, _, bucket, *_ in operation_projections if bucket == "DELAYED"
    )

    return [
        OperationListItem(
            id=operation.id,
            operation_number=operation.operation_number,
            name=operation.name,
            sequence=operation.sequence,
            status=operation.status,
            supervisor_bucket=supervisor_bucket,
            planned_start=operation.planned_start,
            planned_end=operation.planned_end,
            quantity=operation.quantity,
            completed_qty=operation.completed_qty,
            progress=_derive_progress(operation.quantity, operation.completed_qty),
            work_order_number=operation.work_order.work_order_number
            if operation.work_order
            else None,
            work_center=None,
            delay_minutes=delay_minutes,
            block_reason_code="STATUS_BLOCKED_UNSPECIFIED"
            if operation.status == StatusEnum.blocked.value
            else None,
            qc_risk_flag=bool(operation.qc_required),
            wo_blocked_operations=wo_blocked_operations,
            wo_delayed_operations=wo_delayed_operations,
            cycle_time_minutes=cycle_time_minutes,
            cycle_time_delta=cycle_time_delta,
            delay_count=delay_count,
            delay_frequency=round(delay_frequency, 3),
            repeat_flag=repeat_flag,
            qc_fail_count=qc_fail_count,
            high_variance_flag=high_variance_flag,
            often_late_flag=often_late_flag,
            route_step=operation.work_order.production_order.route_id
            if operation.work_order and operation.work_order.production_order
            else None,
        )
        for (
            operation,
            delay_minutes,
            supervisor_bucket,
            cycle_time_minutes,
            cycle_time_delta,
            delay_count,
            delay_frequency,
            repeat_flag,
            qc_fail_count,
            high_variance_flag,
            often_late_flag,
        ) in operation_projections
    ]

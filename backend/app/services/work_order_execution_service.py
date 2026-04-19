from datetime import datetime

from sqlalchemy.orm import Session

from app.models.master import StatusEnum, WorkOrder
from app.repositories.work_order_repository import get_work_order_by_id


def _is_completed_operation(status: str) -> bool:
    return status == StatusEnum.completed.value


def _is_started_operation(status: str) -> bool:
    return status in {
        StatusEnum.in_progress.value,
        StatusEnum.paused.value,
        StatusEnum.completed.value,
        StatusEnum.completed_late.value,
        StatusEnum.aborted.value,
    }


# WHY: Work order status is a pure derivation from its child operations.
# COMPLETED_LATE is distinguished from COMPLETED only when both planned_end
# and actual_end are available; otherwise we cannot assess timeliness.
def _derive_work_order_status(
    *,
    completed_ops: int,
    total_ops: int,
    any_started: bool,
    planned_end: datetime | None,
    actual_end: datetime | None,
    now: datetime,
) -> str:
    if total_ops > 0 and completed_ops == total_ops:
        if planned_end is not None and actual_end is not None:
            if actual_end <= planned_end:
                return StatusEnum.completed.value
            return StatusEnum.completed_late.value
        return StatusEnum.completed.value

    if planned_end is not None and completed_ops < total_ops and now > planned_end:
        return StatusEnum.late.value

    if any_started:
        return StatusEnum.in_progress.value

    return StatusEnum.planned.value


def recompute_work_order(db: Session, work_order_id: int) -> WorkOrder:
    work_order = get_work_order_by_id(db, work_order_id)
    if not work_order:
        raise ValueError("Work order not found")

    operations = list(work_order.operations or [])
    total_ops = len(operations)
    completed_ops = sum(
        1 for operation in operations if _is_completed_operation(operation.status)
    )
    any_started = any(
        _is_started_operation(operation.status) or operation.actual_start is not None
        for operation in operations
    )

    completed_end_times = [
        operation.actual_end
        for operation in operations
        if _is_completed_operation(operation.status)
        and operation.actual_end is not None
    ]

    actual_end = max(completed_end_times) if completed_end_times else None

    started_times = [
        operation.actual_start
        for operation in operations
        if operation.actual_start is not None
    ]
    actual_start = min(started_times) if started_times else None

    now = datetime.utcnow()
    work_order.status = _derive_work_order_status(
        completed_ops=completed_ops,
        total_ops=total_ops,
        any_started=any_started,
        planned_end=work_order.planned_end,
        actual_end=actual_end,
        now=now,
    )
    work_order.actual_start = actual_start
    work_order.actual_end = (
        actual_end if completed_ops == total_ops and total_ops > 0 else None
    )

    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    return work_order


def build_work_order_summary_projection(
    work_order,
) -> dict[str, int | str | datetime | None]:
    operations = list(work_order.operations or [])
    operations_count = len(operations)
    completed_operations = sum(
        1 for operation in operations if _is_completed_operation(operation.status)
    )

    overall_progress = 0
    if operations_count > 0:
        overall_progress = int((completed_operations * 100) / operations_count)

    return {
        "id": work_order.id,
        "work_order_number": work_order.work_order_number,
        "status": work_order.status,
        "planned_start": work_order.planned_start,
        "planned_end": work_order.planned_end,
        "actual_start": work_order.actual_start,
        "actual_end": work_order.actual_end,
        "operations_count": operations_count,
        "completed_operations": completed_operations,
        "overall_progress": overall_progress,
    }

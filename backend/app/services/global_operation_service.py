from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.master import StatusEnum
from app.repositories.operation_repository import get_operations_by_work_order
from app.schemas.operation import OperationListItem


def _derive_progress(quantity: int, completed_qty: int) -> int:
    if quantity <= 0:
        return 0
    return min(int((completed_qty * 100) / quantity), 100)


def _derive_delay_minutes(status: str, planned_end: datetime | None, actual_end: datetime | None) -> int | None:
    if planned_end is None:
        return None

    if status == StatusEnum.completed.value and actual_end is not None:
        reference_time = actual_end
    elif status in (StatusEnum.in_progress.value, StatusEnum.late.value, StatusEnum.blocked.value):
        reference_time = datetime.now(timezone.utc)
    else:
        return None

    if reference_time.tzinfo is None and planned_end.tzinfo is not None:
        reference_time = reference_time.replace(tzinfo=planned_end.tzinfo)
    if reference_time.tzinfo is not None and planned_end.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=None)

    delay = int((reference_time - planned_end).total_seconds() / 60)
    return max(delay, 0)


def _derive_supervisor_bucket(status: str, delay_minutes: int | None) -> str:
    if status == StatusEnum.blocked.value:
        return "BLOCKED"
    if status == StatusEnum.late.value:
        return "DELAYED"
    if delay_minutes is not None and delay_minutes > 0 and status in (
        StatusEnum.in_progress.value,
        StatusEnum.completed.value,
    ):
        return "DELAYED"
    if status == StatusEnum.in_progress.value:
        return "IN_PROGRESS"
    return "OTHER"


def build_work_order_operation_summaries(db: Session, work_order_id: int) -> list[OperationListItem]:
    operations = get_operations_by_work_order(db, work_order_id)

    operation_projections = []
    for operation in operations:
        delay_minutes = _derive_delay_minutes(operation.status, operation.planned_end, operation.actual_end)
        supervisor_bucket = _derive_supervisor_bucket(operation.status, delay_minutes)
        operation_projections.append((operation, delay_minutes, supervisor_bucket))

    wo_blocked_operations = sum(1 for _, _, bucket in operation_projections if bucket == "BLOCKED")
    wo_delayed_operations = sum(1 for _, _, bucket in operation_projections if bucket == "DELAYED")

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
            work_order_number=operation.work_order.work_order_number if operation.work_order else None,
            work_center=None,
            delay_minutes=delay_minutes,
            block_reason_code="STATUS_BLOCKED_UNSPECIFIED" if operation.status == StatusEnum.blocked.value else None,
            qc_risk_flag=bool(operation.qc_required),
            wo_blocked_operations=wo_blocked_operations,
            wo_delayed_operations=wo_delayed_operations,
        )
        for operation, delay_minutes, supervisor_bucket in operation_projections
    ]

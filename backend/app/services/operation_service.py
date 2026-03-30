from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.execution import ExecutionEventType
from app.models.master import StatusEnum
from app.repositories.execution_event_repository import create_execution_event, get_events_for_operation
from app.repositories.operation_repository import get_operation_by_id
from app.schemas.operation import OperationDetail, OperationStartRequest


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _derive_status(events: list) -> str:
    if any(event.event_type == ExecutionEventType.OP_COMPLETED.value for event in events):
        return StatusEnum.completed.value
    if any(event.event_type == ExecutionEventType.OP_STARTED.value for event in events):
        return StatusEnum.in_progress.value
    return StatusEnum.pending.value


def _derive_progress(operation_quantity: int, completed_qty: int) -> int:
    if operation_quantity <= 0:
        return 0
    return min(int(completed_qty * 100 / operation_quantity), 100)


def derive_operation_detail(db: Session, operation) -> OperationDetail:
    events = get_events_for_operation(db, operation.id)
    actual_start = None
    actual_end = None
    completed_qty = operation.completed_qty or 0
    good_qty = operation.good_qty or 0
    scrap_qty = operation.scrap_qty or 0

    for event in events:
        if event.event_type == ExecutionEventType.OP_STARTED.value:
            actual_start = _parse_timestamp(event.payload.get("started_at")) or actual_start
        if event.event_type == ExecutionEventType.OP_COMPLETED.value:
            actual_end = _parse_timestamp(event.payload.get("completed_at")) or actual_end
        if event.event_type == ExecutionEventType.QTY_REPORTED.value:
            completed_qty = max(completed_qty, int(event.payload.get("quantity", completed_qty)))
            good_qty = int(event.payload.get("good_quantity", completed_qty))
        if event.event_type == ExecutionEventType.NG_REPORTED.value:
            scrap_qty = int(event.payload.get("ng_quantity", scrap_qty))

    status = _derive_status(events)
    progress = _derive_progress(operation.quantity, completed_qty)

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
    )


def start_operation(db: Session, operation, request: OperationStartRequest) -> OperationDetail:
    if operation.status == StatusEnum.completed.value:
        raise ValueError("Cannot start an operation that is already completed.")

    payload = {
        "operator_id": request.operator_id,
        "started_at": request.started_at.isoformat() if request.started_at else datetime.utcnow().isoformat(),
    }
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.OP_STARTED.value,
        production_order_id=operation.work_order.production_order_id,
        work_order_id=operation.work_order_id,
        operation_id=operation.id,
        payload=payload,
        tenant_id=operation.tenant_id,
    )

    # Re-read the operation with related entities to derive state.
    operation = get_operation_by_id(db, operation.id)
    if not operation:
        raise ValueError("Operation not found after event creation.")

    return derive_operation_detail(db, operation)

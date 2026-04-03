from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.execution import ExecutionEventType
from app.models.master import StatusEnum
from app.repositories.execution_event_repository import create_execution_event, get_events_for_operation
from app.repositories.operation_repository import (
    get_operation_by_id,
    mark_operation_started,
    mark_operation_reported,
    mark_operation_completed,
    mark_operation_aborted,
)
from app.schemas.operation import (
    OperationDetail,
    OperationStartRequest,
    OperationReportQuantityRequest,
    OperationCompleteRequest,
    OperationAbortRequest,
)
from app.services.work_order_execution_service import recompute_work_order


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _derive_status(events: list) -> str:
    if any(event.event_type == ExecutionEventType.OP_ABORTED.value for event in events):
        return StatusEnum.aborted.value
    if any(event.event_type == ExecutionEventType.OP_COMPLETED.value for event in events):
        return StatusEnum.completed.value
    if any(event.event_type == ExecutionEventType.OP_STARTED.value for event in events):
        return StatusEnum.in_progress.value
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

    for event in events:
        if event.event_type == ExecutionEventType.OP_STARTED.value:
            actual_start = _parse_timestamp(event.payload.get("started_at")) or actual_start
        if event.event_type == ExecutionEventType.OP_COMPLETED.value:
            actual_end = _parse_timestamp(event.payload.get("completed_at")) or actual_end
        if event.event_type == ExecutionEventType.QTY_REPORTED.value:
            good_qty += int(event.payload.get("good_qty", 0))
            scrap_qty += int(event.payload.get("scrap_qty", 0))
        if event.event_type == ExecutionEventType.NG_REPORTED.value:
            scrap_qty += int(event.payload.get("ng_quantity", 0))

    completed_qty = good_qty + scrap_qty
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


def start_operation(db: Session, operation, request: OperationStartRequest, tenant_id: str = "default") -> OperationDetail:
    if operation.tenant_id != tenant_id:
        raise ValueError("Operation does not belong to the requesting tenant.")
    if operation.status in (
        StatusEnum.in_progress.value,
        StatusEnum.completed.value,
        StatusEnum.aborted.value,
    ):
        raise ValueError("Operation already started or completed; cannot start again.")

    start_time = request.started_at or datetime.utcnow()
    payload = {
        "operator_id": request.operator_id,
        "started_at": start_time.isoformat(),
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
        raise ValueError("At least one of good_qty or scrap_qty must be greater than zero.")

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
    operation = mark_operation_reported(db, operation, request.good_qty, request.scrap_qty)

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
    if operation.status in (StatusEnum.completed.value, StatusEnum.aborted.value):
        raise ValueError("Operation already completed; cannot complete again.")
    if operation.status != StatusEnum.in_progress.value:
        raise ValueError("Operation must be IN_PROGRESS to complete.")

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

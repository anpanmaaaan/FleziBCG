from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.execution import ExecutionEvent


# INTENT: This is the only write path for execution events. The append-only
# event log is the source of truth for operation status (via _derive_status).
def create_execution_event(
    db: Session,
    event_type: str,
    production_order_id: int,
    work_order_id: int,
    operation_id: int,
    payload: dict,
    tenant_id: str = "default",
) -> ExecutionEvent:
    event = ExecutionEvent(
        event_type=event_type,
        production_order_id=production_order_id,
        work_order_id=work_order_id,
        operation_id=operation_id,
        payload=payload,
        tenant_id=tenant_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_events_for_operation(db: Session, operation_id: int) -> list[ExecutionEvent]:
    # WHY: Order by created_at alone may not be stable if two events share the
    # same timestamp (sub-ms inserts). Adding id as tiebreaker guarantees
    # deterministic chronological order.
    statement = (
        select(ExecutionEvent)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.created_at)
    )
    return list(db.scalars(statement))


def get_events_for_work_order(
    db: Session, work_order_id: int, tenant_id: str
) -> list[ExecutionEvent]:
    statement = (
        select(ExecutionEvent)
        .where(ExecutionEvent.work_order_id == work_order_id)
        .where(ExecutionEvent.tenant_id == tenant_id)
        .order_by(
            ExecutionEvent.operation_id, ExecutionEvent.created_at, ExecutionEvent.id
        )
    )
    return list(db.scalars(statement))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.execution import ExecutionEvent


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
    statement = select(ExecutionEvent).where(ExecutionEvent.operation_id == operation_id).order_by(ExecutionEvent.created_at)
    return list(db.scalars(statement))

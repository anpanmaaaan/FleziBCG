from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.execution_event_repository import get_events_for_work_order
from app.repositories.work_order_repository import get_work_order_by_id_or_number
from app.schemas.execution_timeline import WorkOrderExecutionTimeline
from app.security.dependencies import RequestIdentity, require_permission
from app.services.execution_timeline_service import build_work_order_execution_timeline

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/work-orders/{work_order_id}/execution-timeline",
    response_model=WorkOrderExecutionTimeline,
)
def read_execution_timeline(
    work_order_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("VIEW")),
):
    """ExecutionTimeline API - read-only, visualization only."""
    # For visualization only - no execution control.
    work_order = get_work_order_by_id_or_number(
        db, work_order_id, tenant_id=identity.tenant_id
    )
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")

    events = get_events_for_work_order(db, work_order.id, tenant_id=identity.tenant_id)
    return build_work_order_execution_timeline(work_order, events)

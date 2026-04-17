from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.master import Operation, WorkOrder


def get_work_orders_for_dashboard(db: Session, tenant_id: str) -> list[WorkOrder]:
    statement = (
        select(WorkOrder).where(WorkOrder.tenant_id == tenant_id).order_by(WorkOrder.id)
    )
    return list(db.scalars(statement))


def get_operation_status_counts_for_dashboard(
    db: Session, tenant_id: str
) -> dict[str, int]:
    statement = (
        select(Operation.status, func.count(Operation.id))
        .where(Operation.tenant_id == tenant_id)
        .group_by(Operation.status)
    )

    rows = db.execute(statement).all()
    return {str(status): int(count) for status, count in rows}


def get_blocked_operation_counts_by_work_order(
    db: Session, tenant_id: str
) -> dict[str, int]:
    statement = (
        select(WorkOrder.work_order_number, func.count(Operation.id))
        .join(Operation, Operation.work_order_id == WorkOrder.id)
        .where(WorkOrder.tenant_id == tenant_id)
        .where(Operation.tenant_id == tenant_id)
        .where(Operation.status == "BLOCKED")
        .group_by(WorkOrder.work_order_number)
    )

    rows = db.execute(statement).all()
    return {str(work_order_number): int(count) for work_order_number, count in rows}

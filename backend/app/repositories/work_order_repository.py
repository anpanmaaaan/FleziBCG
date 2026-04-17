from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.master import WorkOrder


def get_work_order_by_id(db: Session, work_order_id: int) -> WorkOrder | None:
    statement = (
        select(WorkOrder)
        .options(selectinload(WorkOrder.operations))
        .where(WorkOrder.id == work_order_id)
    )
    return db.scalar(statement)


def get_work_order_by_id_or_number(
    db: Session,
    work_order_ref: str,
    tenant_id: str,
) -> WorkOrder | None:
    statement = (
        select(WorkOrder)
        .options(
            selectinload(WorkOrder.production_order),
            selectinload(WorkOrder.operations),
        )
        .where(WorkOrder.tenant_id == tenant_id)
    )

    if work_order_ref.isdigit():
        statement = statement.where(WorkOrder.id == int(work_order_ref))
    else:
        statement = statement.where(WorkOrder.work_order_number == work_order_ref)

    return db.scalar(statement)

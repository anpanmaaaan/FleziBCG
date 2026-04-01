from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.session import Session

from app.models.master import Operation, WorkOrder, StatusEnum


def get_operations_by_work_order(db: Session, work_order_id: int) -> list[Operation]:
    statement = (
        select(Operation)
        .where(Operation.work_order_id == work_order_id)
        .order_by(Operation.sequence)
    )
    return list(db.scalars(statement))


def get_operation_by_id(db: Session, operation_id: int) -> Operation | None:
    statement = (
        select(Operation)
        .where(Operation.id == operation_id)
        .options(selectinload(Operation.work_order).selectinload(WorkOrder.production_order))
    )
    return db.scalar(statement)


def count_operations(db: Session) -> int:
    statement = select(func.count()).select_from(Operation)
    return db.scalar(statement) or 0


def count_operations_by_status(db: Session, status: str) -> int:
    statement = select(func.count()).select_from(Operation).where(Operation.status == status)
    return db.scalar(statement) or 0


def mark_operation_started(db: Session, operation: Operation, started_at):
    operation.status = StatusEnum.in_progress.value
    if operation.actual_start is None:
        operation.actual_start = started_at

    db.add(operation)
    db.commit()
    db.refresh(operation)
    return operation

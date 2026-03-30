from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.session import Session

from app.models.master import ProductionOrder, WorkOrder


def get_production_orders(db: Session) -> list[ProductionOrder]:
    statement = (
        select(ProductionOrder)
        .options(selectinload(ProductionOrder.work_orders))
        .order_by(ProductionOrder.id)
    )
    return list(db.scalars(statement))


def get_production_order_by_id(db: Session, order_id: int) -> ProductionOrder | None:
    statement = (
        select(ProductionOrder)
        .where(ProductionOrder.id == order_id)
        .options(
            selectinload(ProductionOrder.work_orders).selectinload(WorkOrder.operations)
        )
    )
    return db.scalar(statement)


def count_production_orders(db: Session) -> int:
    statement = select(func.count()).select_from(ProductionOrder)
    return db.scalar(statement) or 0


def count_work_orders(db: Session) -> int:
    statement = select(func.count()).select_from(WorkOrder)
    return db.scalar(statement) or 0

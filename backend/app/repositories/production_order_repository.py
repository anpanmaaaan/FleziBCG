from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.session import Session

from app.models.master import ProductionOrder, WorkOrder


def get_production_orders(
    db: Session, tenant_id: str | None = None
) -> list[ProductionOrder]:
    # WHY: selectinload eagerly loads work_orders in one additional query,
    # avoiding N+1 on list endpoints.
    statement = (
        select(ProductionOrder)
        .options(selectinload(ProductionOrder.work_orders))
        .order_by(ProductionOrder.id)
    )
    # EDGE: When tenant_id is None, returns all tenants. Used only by
    # system-level admin queries; normal API always supplies a tenant_id.
    if tenant_id is not None:
        statement = statement.where(ProductionOrder.tenant_id == tenant_id)
    return list(db.scalars(statement))


def get_production_order_by_id(
    db: Session, order_id: int, tenant_id: str | None = None
) -> ProductionOrder | None:
    statement = (
        select(ProductionOrder)
        .where(ProductionOrder.id == order_id)
        .options(
            selectinload(ProductionOrder.work_orders).selectinload(WorkOrder.operations)
        )
    )
    if tenant_id is not None:
        statement = statement.where(ProductionOrder.tenant_id == tenant_id)
    return db.scalar(statement)


def get_production_order_by_number(
    db: Session, order_number: str, tenant_id: str | None = None
) -> ProductionOrder | None:
    statement = (
        select(ProductionOrder)
        .where(ProductionOrder.order_number == order_number)
        .options(
            selectinload(ProductionOrder.work_orders).selectinload(WorkOrder.operations)
        )
    )
    if tenant_id is not None:
        statement = statement.where(ProductionOrder.tenant_id == tenant_id)
    return db.scalar(statement)


def count_production_orders(db: Session) -> int:
    statement = select(func.count()).select_from(ProductionOrder)
    return db.scalar(statement) or 0


def count_work_orders(db: Session) -> int:
    statement = select(func.count()).select_from(WorkOrder)
    return db.scalar(statement) or 0

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repositories.production_order_repository import (
    get_production_order_by_id,
    get_production_order_by_number,
    get_production_orders,
)

logger = logging.getLogger(__name__)
from app.schemas.production_order import ProductionOrderDetail, ProductionOrderSummary, WorkOrderSummary
from app.schemas.operation import OperationListItem
from app.repositories.operation_repository import get_operations_by_work_order
from app.db.session import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _compute_production_order_progress(order) -> int | None:
    if not order.work_orders:
        return None
    total = len(order.work_orders)
    if total == 0:
        return None
    completed = sum(1 for wo in order.work_orders if wo.status == "COMPLETED")
    return int(completed * 100 / total)


def _build_work_order_summary(work_order) -> WorkOrderSummary:
    return WorkOrderSummary(
        id=work_order.id,
        work_order_number=work_order.work_order_number,
        status=work_order.status,
        planned_start=work_order.planned_start,
        planned_end=work_order.planned_end,
        actual_start=work_order.actual_start,
        actual_end=work_order.actual_end,
        operations_count=len(work_order.operations) if work_order.operations is not None else 0,
        overall_progress=0,  # TODO: compute from execution events once event data is in place
    )


def _build_production_order_summary(order) -> ProductionOrderSummary:
    return ProductionOrderSummary(
        id=order.id,
        order_number=order.order_number,
        product_name=order.product_name,
        quantity=order.quantity,
        status=order.status,
        serial_number=getattr(order, "serial_number", None),
        lot_id=getattr(order, "lot_id", None),
        customer=getattr(order, "customer", None),
        priority=getattr(order, "priority", None),
        machine_number=getattr(order, "machine_number", None),
        route_id=order.route_id,
        material_code=getattr(order, "material_code", None),
        assignee=getattr(order, "assignee", None),
        department=getattr(order, "department", None),
        released_date=getattr(order, "released_date", None),
        planned_start_date=order.planned_start,
        planned_completion_date=order.planned_end,
        actual_start_date=getattr(order, "actual_start", None),
        actual_completion_date=getattr(order, "actual_end", None),
        progress=_compute_production_order_progress(order),
    )


@router.get("/production-orders", response_model=list[ProductionOrderSummary])
def read_production_orders(db: Session = Depends(get_db)):
    try:
        orders = get_production_orders(db)
        return [_build_production_order_summary(order) for order in orders]
    except Exception as exc:
        logger.exception("Failed to load production orders")
        raise HTTPException(status_code=500, detail="Failed to load production orders")


@router.get("/production-orders/{order_id}", response_model=ProductionOrderDetail)
def read_production_order(order_id: str, db: Session = Depends(get_db)):
    try:
        order = None

        if order_id.isdigit():
            order = get_production_order_by_id(db, int(order_id))

        if order is None:
            order = get_production_order_by_number(db, order_id)

        if not order:
            raise HTTPException(status_code=404, detail="Production order not found")

        return ProductionOrderDetail(
            id=order.id,
            order_number=order.order_number,
            product_name=order.product_name,
            quantity=order.quantity,
            status=order.status,
            serial_number=getattr(order, "serial_number", None),
            lot_id=getattr(order, "lot_id", None),
            customer=getattr(order, "customer", None),
            priority=getattr(order, "priority", None),
            machine_number=getattr(order, "machine_number", None),
            route_id=order.route_id,
            material_code=getattr(order, "material_code", None),
            assignee=getattr(order, "assignee", None),
            department=getattr(order, "department", None),
            released_date=getattr(order, "released_date", None),
            planned_start_date=order.planned_start,
            planned_completion_date=order.planned_end,
            actual_start_date=getattr(order, "actual_start", None),
            actual_completion_date=getattr(order, "actual_end", None),
            progress=_compute_production_order_progress(order),
            work_orders=[_build_work_order_summary(wo) for wo in order.work_orders],
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to load production order %s", order_id)
        raise HTTPException(status_code=500, detail="Failed to load production order")


@router.get("/work-orders/{wo_id}/operations", response_model=list[OperationListItem])
def read_work_order_operations(wo_id: int, db: Session = Depends(get_db)):
    operations = get_operations_by_work_order(db, wo_id)
    return [
        OperationListItem(
            id=operation.id,
            operation_number=operation.operation_number,
            name=operation.name,
            sequence=operation.sequence,
            status=operation.status,
            planned_start=operation.planned_start,
            planned_end=operation.planned_end,
            quantity=operation.quantity,
            completed_qty=operation.completed_qty,
            progress=0,  # TODO: derive runtime progress from events
        )
        for operation in operations
    ]

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.schemas.operation import OperationStartRequest
from app.services.operation_service import start_operation

SEED_PREFIX = "PH6-STATION"
TENANT_ID = "default"
STATION_SCOPE = "STATION_01"
OPERATOR_USER_ID = "opr-001"


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _reset_station_seed(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(ProductionOrder.order_number.like(f"{SEED_PREFIX}-%"))
        )
    )
    if not po_ids:
        db.commit()
        return

    wo_ids = list(db.scalars(select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))))
    if wo_ids:
        operation_ids = list(db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids))))
        if operation_ids:
            db.execute(delete(OperationClaimAuditLog).where(OperationClaimAuditLog.operation_id.in_(operation_ids)))
            db.execute(delete(OperationClaim).where(OperationClaim.operation_id.in_(operation_ids)))
        db.execute(delete(ExecutionEvent).where(ExecutionEvent.work_order_id.in_(wo_ids)))
        db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))

    db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.commit()


def seed_station_execution_for_opr() -> None:
    init_db()

    with SessionLocal() as db:
        _reset_station_seed(db)

        production_order = ProductionOrder(
            order_number=f"{SEED_PREFIX}-PO-001",
            route_id=f"{SEED_PREFIX}-R-01",
            product_name="Station Execution Demo Product",
            quantity=30,
            status=StatusEnum.planned.value,
            planned_start=_dt("2099-06-01T08:00:00"),
            planned_end=_dt("2099-06-01T17:00:00"),
            tenant_id=TENANT_ID,
        )
        db.add(production_order)
        db.flush()

        work_order = WorkOrder(
            production_order_id=production_order.id,
            work_order_number=f"{SEED_PREFIX}-WO-001",
            status=StatusEnum.planned.value,
            planned_start=_dt("2099-06-01T08:00:00"),
            planned_end=_dt("2099-06-01T17:00:00"),
            tenant_id=TENANT_ID,
        )
        db.add(work_order)
        db.flush()

        operations = [
            Operation(
                operation_number=f"{SEED_PREFIX}-OP-001",
                work_order_id=work_order.id,
                sequence=10,
                name="Load Material",
                status=StatusEnum.planned.value,
                planned_start=_dt("2099-06-01T08:10:00"),
                planned_end=_dt("2099-06-01T09:00:00"),
                quantity=10,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=False,
                station_scope_value=STATION_SCOPE,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number=f"{SEED_PREFIX}-OP-002",
                work_order_id=work_order.id,
                sequence=20,
                name="Machine Run",
                status=StatusEnum.planned.value,
                planned_start=_dt("2099-06-01T09:10:00"),
                planned_end=_dt("2099-06-01T11:00:00"),
                quantity=10,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=False,
                station_scope_value=STATION_SCOPE,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number=f"{SEED_PREFIX}-OP-003",
                work_order_id=work_order.id,
                sequence=30,
                name="Visual Check",
                status=StatusEnum.planned.value,
                planned_start=_dt("2099-06-01T11:10:00"),
                planned_end=_dt("2099-06-01T12:00:00"),
                quantity=10,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=True,
                station_scope_value=STATION_SCOPE,
                tenant_id=TENANT_ID,
            ),
        ]

        db.add_all(operations)
        db.commit()

        # Put one operation into IN_PROGRESS so station queue shows mixed states.
        operation_in_progress = db.scalar(
            select(Operation).where(Operation.operation_number == f"{SEED_PREFIX}-OP-002")
        )
        if operation_in_progress is None:
            raise RuntimeError("Seeded operation not found: PH6-STATION-OP-002")

        start_operation(
            db,
            operation_in_progress,
            OperationStartRequest(
                operator_id=OPERATOR_USER_ID,
                started_at=_dt("2099-06-01T09:15:00"),
            ),
            tenant_id=TENANT_ID,
        )

        seeded_rows = list(
            db.scalars(
                select(Operation)
                .where(Operation.operation_number.like(f"{SEED_PREFIX}-%"))
                .order_by(Operation.sequence.asc())
            )
        )

        print("Station execution seed ready.")
        print(f"operator user_id: {OPERATOR_USER_ID} (username: operator)")
        print(f"station scope: {STATION_SCOPE}")
        print(f"production order: {production_order.order_number}")
        print(f"work order: {work_order.work_order_number}")
        print("operations:")
        for operation in seeded_rows:
            print(
                f"  - id={operation.id}, number={operation.operation_number}, "
                f"status={operation.status}, station={operation.station_scope_value}"
            )


if __name__ == "__main__":
    seed_station_execution_for_opr()

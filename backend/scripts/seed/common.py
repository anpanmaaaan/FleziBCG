from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.execution import ExecutionEvent
from app.models.master import Operation, ProductionOrder, WorkOrder, StatusEnum
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.repositories.operation_repository import get_operation_by_id
from app.schemas.operation import (
    OperationAbortRequest,
    OperationCompleteRequest,
    OperationStartRequest,
)
from app.services.operation_service import (
    abort_operation,
    complete_operation,
    start_operation,
)

SEED_PREFIX = "PH6-DEMO"
TENANT_ID = "default"


@dataclass
class ScenarioContext:
    production_order: ProductionOrder
    work_order: WorkOrder
    operations: list[Operation]


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def reset_seed_dataset(db: Session) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{SEED_PREFIX}-%")
            )
        )
    )
    if not po_ids:
        db.commit()
        return

    wo_ids = list(
        db.scalars(
            select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))
        )
    )
    if wo_ids:
        operation_ids = list(
            db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids)))
        )
        if operation_ids:
            db.execute(
                delete(OperationClaimAuditLog).where(
                    OperationClaimAuditLog.operation_id.in_(operation_ids)
                )
            )
            db.execute(
                delete(OperationClaim).where(
                    OperationClaim.operation_id.in_(operation_ids)
                )
            )
        db.execute(
            delete(ExecutionEvent).where(ExecutionEvent.work_order_id.in_(wo_ids))
        )
        db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))

    db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.commit()


def create_production_order(
    db: Session, *, scenario_code: str, planned_start: str, planned_end: str
) -> ProductionOrder:
    production_order = ProductionOrder(
        order_number=f"{SEED_PREFIX}-{scenario_code}-PO",
        route_id=f"{SEED_PREFIX}-{scenario_code}",
        product_name=f"Scenario {scenario_code} Product",
        quantity=30,
        status=StatusEnum.planned.value,
        planned_start=_dt(planned_start),
        planned_end=_dt(planned_end),
        tenant_id=TENANT_ID,
    )
    db.add(production_order)
    db.flush()
    return production_order


def create_work_order(
    db: Session,
    *,
    production_order: ProductionOrder,
    scenario_code: str,
    planned_start: str,
    planned_end: str,
) -> WorkOrder:
    work_order = WorkOrder(
        production_order_id=production_order.id,
        work_order_number=f"{SEED_PREFIX}-{scenario_code}-WO",
        status=StatusEnum.planned.value,
        planned_start=_dt(planned_start),
        planned_end=_dt(planned_end),
        tenant_id=TENANT_ID,
    )
    db.add(work_order)
    db.flush()
    return work_order


def create_operation(
    db: Session,
    *,
    work_order: WorkOrder,
    scenario_code: str,
    sequence: int,
    name: str,
    planned_start: str,
    planned_end: str,
    quantity: int = 10,
    qc_required: bool = False,
) -> Operation:
    operation = Operation(
        operation_number=f"{SEED_PREFIX}-{scenario_code}-OP-{sequence:03d}",
        work_order_id=work_order.id,
        sequence=sequence,
        name=name,
        status=StatusEnum.pending.value,
        planned_start=_dt(planned_start),
        planned_end=_dt(planned_end),
        quantity=quantity,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=qc_required,
        tenant_id=TENANT_ID,
    )
    db.add(operation)
    db.flush()
    return operation


def run_start(
    db: Session, operation_id: int, started_at: datetime | None = None
) -> Operation:
    operation = get_operation_by_id(db, operation_id)
    if operation is None:
        raise ValueError(f"Operation {operation_id} not found")
    start_operation(
        db,
        operation,
        OperationStartRequest(
            operator_id=f"seed-user-{operation_id}", started_at=started_at
        ),
        tenant_id=TENANT_ID,
    )
    refreshed = get_operation_by_id(db, operation_id)
    if refreshed is None:
        raise ValueError(f"Operation {operation_id} missing after start")
    return refreshed


def run_complete(
    db: Session, operation_id: int, completed_at: datetime | None = None
) -> Operation:
    operation = get_operation_by_id(db, operation_id)
    if operation is None:
        raise ValueError(f"Operation {operation_id} not found")
    complete_operation(
        db,
        operation,
        OperationCompleteRequest(operator_id="seed-user", completed_at=completed_at),
        tenant_id=TENANT_ID,
    )
    refreshed = get_operation_by_id(db, operation_id)
    if refreshed is None:
        raise ValueError(f"Operation {operation_id} missing after completion")
    return refreshed


def run_abort(db: Session, operation_id: int, *, reason_code: str) -> Operation:
    operation = get_operation_by_id(db, operation_id)
    if operation is None:
        raise ValueError(f"Operation {operation_id} not found")
    abort_operation(
        db,
        operation,
        OperationAbortRequest(operator_id="seed-user", reason_code=reason_code),
        tenant_id=TENANT_ID,
    )
    refreshed = get_operation_by_id(db, operation_id)
    if refreshed is None:
        raise ValueError(f"Operation {operation_id} missing after abort")
    return refreshed


def mark_blocked_for_incident_seed(
    db: Session, operation_id: int, *, reason_code: str
) -> Operation:
    operation = get_operation_by_id(db, operation_id)
    if operation is None:
        raise ValueError(f"Operation {operation_id} not found")

    # Phase 6A scope keeps runtime behavior unchanged; blocked simulation is seed-only.
    operation.status = StatusEnum.blocked.value
    db.add(operation)
    db.commit()
    db.refresh(operation)
    return operation


def create_scenario_context(
    db: Session,
    *,
    scenario_code: str,
    wo_planned_start: str,
    wo_planned_end: str,
    operation_name_prefix: str,
    operation_plans: list[tuple[int, str, str, str, bool]],
) -> ScenarioContext:
    po = create_production_order(
        db,
        scenario_code=scenario_code,
        planned_start=wo_planned_start,
        planned_end=wo_planned_end,
    )
    wo = create_work_order(
        db,
        production_order=po,
        scenario_code=scenario_code,
        planned_start=wo_planned_start,
        planned_end=wo_planned_end,
    )

    operations: list[Operation] = []
    for (
        sequence,
        planned_start,
        planned_end,
        step_suffix,
        qc_required,
    ) in operation_plans:
        operations.append(
            create_operation(
                db,
                work_order=wo,
                scenario_code=scenario_code,
                sequence=sequence,
                name=f"{operation_name_prefix} {step_suffix}",
                planned_start=planned_start,
                planned_end=planned_end,
                quantity=10,
                qc_required=qc_required,
            )
        )

    db.commit()
    return ScenarioContext(production_order=po, work_order=wo, operations=operations)

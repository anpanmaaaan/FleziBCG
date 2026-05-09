from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.quality import (
    QualityGateDefinition,
    QualityGateInstance,
    QualityNonconformance,
    QualityDeviationRequest,
)
from app.schemas.quality import (
    QualityGateDefinitionCreateRequest,
    QualityGateInstanceOpenRequest,
)
from app.services.quality_service import (
    QualityConflictError,
    create_quality_gate_definition_service,
    list_quality_gate_definitions_service,
    open_quality_gate_instance_service,
)

_PREFIX = "TEST-QG-SVC"


def _purge(db) -> None:
    db.execute(delete(QualityDeviationRequest))
    db.execute(delete(QualityNonconformance))
    db.execute(delete(QualityGateInstance))
    db.execute(delete(QualityGateDefinition).where(QualityGateDefinition.code.like(f"{_PREFIX}-%")))

    op_ids = list(
        db.scalars(
            select(Operation.id).where(Operation.operation_number.like(f"{_PREFIX}-%"))
        )
    )
    if op_ids:
        db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
        wo_ids = list(
            db.scalars(select(WorkOrder.id).where(WorkOrder.operations.any(Operation.id.in_(op_ids))))
        )
        db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
        if wo_ids:
            po_ids = list(
                db.scalars(
                    select(ProductionOrder.id).where(
                        ProductionOrder.work_orders.any(WorkOrder.id.in_(wo_ids))
                    )
                )
            )
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
            if po_ids:
                db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))

    db.commit()


@pytest.fixture
def db_session():
    init_db()
    db = SessionLocal()
    try:
        _purge(db)
        yield db
    finally:
        db.rollback()
        _purge(db)
        db.close()


def _seed_operation(db, *, suffix: str, tenant_id: str) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="quality-gate-test",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 1, 1, 8, 0, 0),
        planned_end=datetime(2099, 1, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 1, 1, 8, 0, 0),
        planned_end=datetime(2099, 1, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="quality-gate-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=tenant_id,
        status=StatusEnum.planned.value,
        quantity=10,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=True,
        station_scope_value=f"{_PREFIX}-ST-{suffix}",
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def test_create_and_list_quality_gate_definitions(db_session):
    created = create_quality_gate_definition_service(
        db_session,
        tenant_id="default",
        actor_user_id="qal-user",
        payload=QualityGateDefinitionCreateRequest(
            code=f"{_PREFIX}-GATE-01",
            name="Gate 01",
            gate_type="PRE_ACCEPTANCE",
            rule_set_version="v1",
            applicability_scope_type="STATION",
            applicability_scope_value="ST-100",
        ),
    )

    assert created.code == f"{_PREFIX}-GATE-01"
    assert created.status == "DRAFT"

    rows = list_quality_gate_definitions_service(db_session, tenant_id="default")
    assert any(row.gate_definition_id == created.gate_definition_id for row in rows)


def test_open_quality_gate_instance_success(db_session):
    op = _seed_operation(db_session, suffix="OPEN", tenant_id="default")
    gate = create_quality_gate_definition_service(
        db_session,
        tenant_id="default",
        actor_user_id="qal-user",
        payload=QualityGateDefinitionCreateRequest(
            code=f"{_PREFIX}-GATE-OPEN",
            name="Gate OPEN",
            gate_type="PRE_ACCEPTANCE",
            rule_set_version="v1",
            applicability_scope_type="STATION",
            applicability_scope_value="ST-OPEN",
        ),
    )

    instance = open_quality_gate_instance_service(
        db_session,
        tenant_id="default",
        actor_user_id="qal-user",
        payload=QualityGateInstanceOpenRequest(
            operation_id=op.id,
            gate_definition_id=gate.gate_definition_id,
        ),
    )

    assert instance.operation_id == op.id
    assert instance.gate_definition_id == gate.gate_definition_id
    assert instance.status == "PENDING_MEASUREMENT"


def test_open_quality_gate_instance_rejects_if_active_exists(db_session):
    op = _seed_operation(db_session, suffix="CONFLICT", tenant_id="default")
    gate = create_quality_gate_definition_service(
        db_session,
        tenant_id="default",
        actor_user_id="qal-user",
        payload=QualityGateDefinitionCreateRequest(
            code=f"{_PREFIX}-GATE-CONFLICT",
            name="Gate CONFLICT",
            gate_type="PRE_ACCEPTANCE",
            rule_set_version="v1",
            applicability_scope_type="STATION",
            applicability_scope_value="ST-CONFLICT",
        ),
    )

    open_quality_gate_instance_service(
        db_session,
        tenant_id="default",
        actor_user_id="qal-user",
        payload=QualityGateInstanceOpenRequest(
            operation_id=op.id,
            gate_definition_id=gate.gate_definition_id,
        ),
    )

    with pytest.raises(QualityConflictError, match="QUALITY_GATE_INSTANCE_ALREADY_ACTIVE"):
        open_quality_gate_instance_service(
            db_session,
            tenant_id="default",
            actor_user_id="qal-user",
            payload=QualityGateInstanceOpenRequest(
                operation_id=op.id,
                gate_definition_id=gate.gate_definition_id,
            ),
        )

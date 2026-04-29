"""
P0-C-01 Work Order / Operation Foundation Alignment Tests.

Scope:
- Tenant isolation: execution write commands reject wrong-tenant callers.
- WorkOrder/Operation hierarchy read: derive_operation_detail populates
  work_order_number and production_order_number from the WO→PO chain.
- WorkOrder and Operation share the same tenant_id at INSERT time.
- No state transition changes. No claim removal. No session-owned migration.

Design evidence:
- docs/design/02_domain/execution/station-execution-state-matrix-v4.md (INV-001/INV-002)
- docs/design/02_domain/product_definition/product-foundation-contract.md (tenant ownership)
- docs/implementation/p0-c-execution-entry-audit.md (P0-C-01 invariant gaps)
"""

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.schemas.operation import (
    OperationCloseRequest,
    OperationStartRequest,
)
from app.services.operation_service import (
    close_operation,
    derive_operation_detail,
    start_operation,
)

_PREFIX = "TEST-WO-OP-FOUNDATION"
_TENANT_A = "tenant_alpha"
_TENANT_B = "tenant_beta"


# ─── Fixture helpers ──────────────────────────────────────────────────────────

def _purge(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX}-%")
            )
        )
    )
    if not po_ids:
        db.commit()
        return
    wo_ids = list(
        db.scalars(select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids)))
    )
    if wo_ids:
        op_ids = list(
            db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids)))
        )
        if op_ids:
            db.execute(
                delete(OperationClaimAuditLog).where(
                    OperationClaimAuditLog.operation_id.in_(op_ids)
                )
            )
            db.execute(
                delete(OperationClaim).where(OperationClaim.operation_id.in_(op_ids))
            )
            db.execute(
                delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids))
            )
            db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
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
        _purge(db)
        db.close()


def _seed_operation(db, suffix: str, tenant_id: str, status: str = StatusEnum.planned.value) -> Operation:
    """Seed a minimal PO→WO→Operation hierarchy under the given tenant."""
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name=f"foundation-test-{suffix}",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        work_order_id=wo.id,
        sequence=10,
        name=f"op-{suffix}",
        status=status,
        station_scope_value=f"STATION_FOUND_{suffix}",
        planned_start=datetime(2099, 9, 1, 9, 0, 0),
        planned_end=datetime(2099, 9, 1, 11, 0, 0),
        quantity=10,
        tenant_id=tenant_id,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


# ─── P0C01-T3: start_operation rejects wrong tenant ──────────────────────────

def test_start_operation_rejects_wrong_tenant(db_session):
    """
    INV: Tenant isolation — start_operation raises when the caller's tenant_id
    does not match the operation's tenant_id.

    This test locks the service-layer guard that was present but untested
    entering P0-C. It confirms that a cross-tenant caller cannot start an
    operation even if they somehow obtain its ID.
    """
    op = _seed_operation(db_session, "T3", tenant_id=_TENANT_A)

    with pytest.raises(ValueError, match="does not belong to the requesting tenant"):
        start_operation(
            db_session,
            op,
            OperationStartRequest(operator_id="operator-from-tenant-b"),
            tenant_id=_TENANT_B,
        )


# ─── P0C01-T4: close_operation rejects wrong tenant ──────────────────────────

def test_close_operation_rejects_wrong_tenant(db_session):
    """
    INV: Tenant isolation — close_operation raises when the caller's tenant_id
    does not match the operation's tenant_id.

    close_operation is one of the highest-impact commands (irreversible without
    a supervised reopen), so this guard is particularly important.
    """
    op = _seed_operation(db_session, "T4", tenant_id=_TENANT_A, status=StatusEnum.completed.value)

    with pytest.raises(ValueError, match="does not belong to the requesting tenant"):
        close_operation(
            db_session,
            op,
            OperationCloseRequest(note="cross-tenant close attempt"),
            actor_user_id="attacker",
            tenant_id=_TENANT_B,
        )


# ─── P0C01-T5: WO→PO→Operation hierarchy reads via derive_operation_detail ───

def test_derive_operation_detail_populates_hierarchy(db_session):
    """
    INV: Projection consistency — derive_operation_detail must expose
    work_order_number and production_order_number from the WO→PO chain.

    This confirms the service reads the full hierarchy correctly so the
    station execution cockpit can display context without extra queries.
    """
    op = _seed_operation(db_session, "T5", tenant_id=_TENANT_A)

    from app.repositories.operation_repository import get_operation_by_id
    op_loaded = get_operation_by_id(db_session, op.id)
    assert op_loaded is not None

    detail = derive_operation_detail(db_session, op_loaded)

    assert detail.work_order_number == f"{_PREFIX}-WO-T5"
    assert detail.production_order_number == f"{_PREFIX}-PO-T5"
    assert detail.work_order_id == op_loaded.work_order_id
    assert detail.production_order_id == op_loaded.work_order.production_order_id
    assert detail.status == StatusEnum.planned.value
    assert detail.closure_status == ClosureStatusEnum.open.value
    assert detail.allowed_actions == ["start_execution"]


# ─── P0C01-T6: WorkOrder tenant_id matches Operation tenant_id ───────────────

def test_work_order_and_operation_share_tenant(db_session):
    """
    INV: Tenant isolation at INSERT — WorkOrder.tenant_id and
    Operation.tenant_id must be identical for a correctly seeded record.

    This test locks the INSERT-time consistency assumption relied upon by all
    service-layer tenant checks. If the seed helper or the model defaults
    ever diverge, this test will catch it before execution write guards fail
    silently.
    """
    op = _seed_operation(db_session, "T6", tenant_id=_TENANT_A)

    wo = db_session.get(WorkOrder, op.work_order_id)
    assert wo is not None
    assert op.tenant_id == _TENANT_A
    assert wo.tenant_id == _TENANT_A
    assert op.tenant_id == wo.tenant_id


# ─── P0C01-T3b: report_quantity rejects wrong tenant ─────────────────────────

def test_report_quantity_rejects_wrong_tenant(db_session):
    """
    INV: Tenant isolation — report_quantity raises when caller's tenant_id
    does not match the operation's tenant_id.
    """
    from app.schemas.operation import OperationReportQuantityRequest
    from app.services.operation_service import report_quantity

    op = _seed_operation(db_session, "T3B", tenant_id=_TENANT_A, status=StatusEnum.in_progress.value)

    with pytest.raises(ValueError, match="does not belong to the requesting tenant"):
        report_quantity(
            db_session,
            op,
            OperationReportQuantityRequest(good_qty=1, scrap_qty=0),
            tenant_id=_TENANT_B,
        )

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.security.dependencies import RequestIdentity
from app.services.station_claim_service import ClaimConflictError, claim_operation

_PREFIX = "TEST-CLAIM-SINGLE-ACTIVE"
_TENANT_ID = "default"
_STATION_SCOPE_VALUE = f"{_PREFIX}-STATION-01"
_OWNER_USER_ID = f"{_PREFIX}-OWNER"
_OTHER_USER_ID = f"{_PREFIX}-OTHER"


def _identity(user_id: str) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username=user_id,
        email=None,
        tenant_id=_TENANT_ID,
        role_code="OPR",
        acting_role_code=None,
        is_authenticated=True,
    )


def _purge(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX}-%")
            )
        )
    )
    if po_ids:
        wo_ids = list(
            db.scalars(
                select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))
            )
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
                db.execute(delete(OperationClaim).where(OperationClaim.operation_id.in_(op_ids)))
                db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
            db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))

    db.execute(
        delete(UserRoleAssignment).where(
            UserRoleAssignment.user_id.in_([_OWNER_USER_ID, _OTHER_USER_ID])
        )
    )
    db.execute(
        delete(Scope).where(
            Scope.scope_value == _STATION_SCOPE_VALUE,
            Scope.tenant_id == _TENANT_ID,
        )
    )
    db.commit()


def _ensure_opr_role(db) -> Role:
    role = db.scalar(select(Role).where(Role.code == "OPR"))
    if role is not None:
        return role
    role = Role(code="OPR", name="Operator", role_type="system", is_system=True)
    db.add(role)
    db.flush()
    return role


@pytest.fixture
def claim_guard_fixture():
    db = SessionLocal()
    try:
        _purge(db)
        opr_role = _ensure_opr_role(db)

        scope = Scope(
            tenant_id=_TENANT_ID,
            scope_type="station",
            scope_value=_STATION_SCOPE_VALUE,
        )
        db.add(scope)
        db.flush()

        db.add_all(
            [
                UserRoleAssignment(
                    user_id=_OWNER_USER_ID,
                    role_id=opr_role.id,
                    scope_id=scope.id,
                    is_primary=True,
                    is_active=True,
                ),
                UserRoleAssignment(
                    user_id=_OTHER_USER_ID,
                    role_id=opr_role.id,
                    scope_id=scope.id,
                    is_primary=True,
                    is_active=True,
                ),
            ]
        )

        po = ProductionOrder(
            order_number=f"{_PREFIX}-PO-001",
            route_id=f"{_PREFIX}-R-01",
            product_name="single active claim guard",
            quantity=10,
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 7, 1, 8, 0, 0),
            planned_end=datetime(2099, 7, 1, 17, 0, 0),
            tenant_id=_TENANT_ID,
        )
        db.add(po)
        db.flush()

        wo = WorkOrder(
            production_order_id=po.id,
            work_order_number=f"{_PREFIX}-WO-001",
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 7, 1, 8, 0, 0),
            planned_end=datetime(2099, 7, 1, 17, 0, 0),
            tenant_id=_TENANT_ID,
        )
        db.add(wo)
        db.flush()

        def mk_op(seq: int, suffix: str) -> Operation:
            minute_slot = seq // 10
            op = Operation(
                operation_number=f"{_PREFIX}-OP-{suffix}",
                work_order_id=wo.id,
                sequence=seq,
                name=f"Claim Guard {suffix}",
                status=StatusEnum.planned.value,
                planned_start=datetime(2099, 7, 1, 9, minute_slot, 0),
                planned_end=datetime(2099, 7, 1, 11, minute_slot, 0),
                quantity=10,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=False,
                station_scope_value=_STATION_SCOPE_VALUE,
                tenant_id=_TENANT_ID,
            )
            db.add(op)
            db.flush()
            return op

        ops = {
            "first": mk_op(10, "FIRST"),
            "second": mk_op(20, "SECOND"),
            "third": mk_op(30, "THIRD"),
        }
        db.commit()
        yield db, ops
    finally:
        _purge(db)
        db.close()


def test_claim_first_operation_succeeds(claim_guard_fixture):
    db, ops = claim_guard_fixture
    claim, _ = claim_operation(db, _identity(_OWNER_USER_ID), ops["first"].id)
    assert claim.operation_id == ops["first"].id


def test_claim_second_planned_operation_rejected_when_first_is_claimed(
    claim_guard_fixture,
):
    db, ops = claim_guard_fixture

    claim_operation(db, _identity(_OWNER_USER_ID), ops["first"].id)

    with pytest.raises(ClaimConflictError, match="already holds another active claim"):
        claim_operation(db, _identity(_OWNER_USER_ID), ops["second"].id)


def test_claim_second_rejected_when_first_is_in_progress(claim_guard_fixture):
    db, ops = claim_guard_fixture

    claim_operation(db, _identity(_OWNER_USER_ID), ops["first"].id)
    first = ops["first"]
    first.status = StatusEnum.in_progress.value
    db.add(first)
    db.commit()

    with pytest.raises(ClaimConflictError, match="already holds another active claim"):
        claim_operation(db, _identity(_OWNER_USER_ID), ops["second"].id)


def test_claim_second_rejected_when_first_is_paused(claim_guard_fixture):
    db, ops = claim_guard_fixture

    claim_operation(db, _identity(_OWNER_USER_ID), ops["first"].id)
    first = ops["first"]
    first.status = StatusEnum.paused.value
    db.add(first)
    db.commit()

    with pytest.raises(ClaimConflictError, match="already holds another active claim"):
        claim_operation(db, _identity(_OWNER_USER_ID), ops["second"].id)


def test_claim_second_rejected_when_first_is_blocked(claim_guard_fixture):
    db, ops = claim_guard_fixture

    claim_operation(db, _identity(_OWNER_USER_ID), ops["first"].id)
    first = ops["first"]
    first.status = StatusEnum.blocked.value
    db.add(first)
    db.commit()

    with pytest.raises(ClaimConflictError, match="already holds another active claim"):
        claim_operation(db, _identity(_OWNER_USER_ID), ops["second"].id)


def test_different_operator_can_claim_different_operation(claim_guard_fixture):
    db, ops = claim_guard_fixture

    claim_operation(db, _identity(_OWNER_USER_ID), ops["first"].id)
    other_claim, _ = claim_operation(db, _identity(_OTHER_USER_ID), ops["second"].id)

    assert other_claim.operation_id == ops["second"].id

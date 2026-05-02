from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_session import StationSession
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    close_operation,
    reopen_operation,
    resume_operation,
)
from app.schemas.operation import (
    OperationCloseRequest,
    OperationReopenRequest,
    OperationResumeRequest,
)
from app.services.station_claim_service import get_station_queue
from app.services.station_session_service import (
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)

_PREFIX = "TEST-REOPEN-CLAIM-CONTINUITY"
_TENANT_ID = "default"
_STATION_SCOPE = f"{_PREFIX}-STATION-01"
_OWNER_USER_ID = f"{_PREFIX}-OWNER"
_OTHER_USER_ID = f"{_PREFIX}-OTHER"
_SUP_USER_ID = f"{_PREFIX}-SUP"


def _identity(user_id: str, role_code: str = "OPR") -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username=user_id,
        email=None,
        tenant_id=_TENANT_ID,
        role_code=role_code,
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
            db.scalars(select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids)))
        )
        if wo_ids:
            op_ids = list(db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids))))
            if op_ids:
                db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
                db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.execute(
        delete(UserRoleAssignment).where(
            UserRoleAssignment.user_id.in_([_OWNER_USER_ID, _OTHER_USER_ID])
        )
    )
    db.execute(delete(Scope).where(Scope.scope_value == _STATION_SCOPE))
    db.commit()


def _ensure_role(db, code: str, name: str) -> Role:
    role = db.scalar(select(Role).where(Role.code == code))
    if role is not None:
        return role
    role = Role(code=code, name=name, role_type="system", is_system=True)
    db.add(role)
    db.flush()
    return role


def _ensure_open_station_session(db, *, user_id: str) -> StationSession:
    identity = _identity(user_id)
    session = get_current_station_session(db, identity, station_id=_STATION_SCOPE)
    if session is None:
        session = open_station_session(db, identity, station_id=_STATION_SCOPE)
    if session.operator_user_id != user_id:
        session = identify_operator_at_station(
            db,
            identity,
            session_id=session.session_id,
            operator_user_id=user_id,
        )
    return session


@pytest.fixture
def db_session():
    init_db()
    db = SessionLocal()
    try:
        _purge(db)
        opr_role = _ensure_role(db, "OPR", "Operator")
        scope = Scope(
            tenant_id=_TENANT_ID,
            scope_type="station",
            scope_value=_STATION_SCOPE,
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
        yield db
    finally:
        _purge(db)
        db.close()


def _seed_operation(db, suffix: str) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="reopen resumability",
        quantity=10,
        status=StatusEnum.planned.value,
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()
    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        work_order_id=wo.id,
        sequence=10,
        name=f"op {suffix}",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value=_STATION_SCOPE,
        quantity=10,
        tenant_id=_TENANT_ID,
    )
    db.add(op)
    db.flush()
    db.commit()
    db.refresh(op)
    return op


def _mark_operation_completed(db, op: Operation) -> Operation:
    wo = db.get(WorkOrder, op.work_order_id)
    assert wo is not None
    db.add_all(
        [
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=wo.production_order_id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"started_at": datetime(2099, 10, 1, 9, 0, 0).isoformat()},
                tenant_id=_TENANT_ID,
            ),
            ExecutionEvent(
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order_id=wo.production_order_id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"completed_at": datetime(2099, 10, 1, 9, 30, 0).isoformat()},
                tenant_id=_TENANT_ID,
            ),
        ]
    )
    op.status = StatusEnum.completed.value
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def test_reopen_restores_last_claim_owner_path_and_resume_is_reachable(db_session):
    db = db_session
    op = _seed_operation(db, "RESTORE")

    _mark_operation_completed(db, op)
    close_operation(
        db,
        op,
        OperationCloseRequest(note="close for reopen"),
        actor_user_id=_SUP_USER_ID,
        tenant_id=_TENANT_ID,
    )

    reopened = reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="resume needed after reopen"),
        actor_user_id=_SUP_USER_ID,
        tenant_id=_TENANT_ID,
    )
    assert reopened.closure_status == ClosureStatusEnum.open.value
    assert reopened.status == StatusEnum.paused.value

    scope_value, items = get_station_queue(db, _identity(_OWNER_USER_ID))
    assert scope_value == _STATION_SCOPE
    queue_item = next(item for item in items if item["operation_id"] == op.id)
    assert queue_item["status"] == StatusEnum.paused.value
    assert queue_item["claim"] is None  # H10: queue claim payload is null-only

    _ensure_open_station_session(db, user_id=_OWNER_USER_ID)
    resumed = resume_operation(
        db,
        op,
        OperationResumeRequest(note="resume after reopen"),
        actor_user_id=_OWNER_USER_ID,
        tenant_id=_TENANT_ID,
    )
    assert resumed.status == StatusEnum.in_progress.value


def test_reopen_preserves_active_claim_continuity_when_claim_still_exists(db_session):
    db = db_session
    op = _seed_operation(db, "CONTINUITY")
    _mark_operation_completed(db, op)

    close_operation(
        db,
        op,
        OperationCloseRequest(note="close for continuity"),
        actor_user_id=_SUP_USER_ID,
        tenant_id=_TENANT_ID,
    )
    reopened = reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="continuity reopen"),
        actor_user_id=_SUP_USER_ID,
        tenant_id=_TENANT_ID,
    )
    assert reopened.status == StatusEnum.paused.value
    assert reopened.closure_status == ClosureStatusEnum.open.value


def test_reopen_skips_claim_restoration_when_owner_has_other_active_claim(db_session):
    db = db_session
    op_reopen = _seed_operation(db, "CONFLICT-REOPEN")
    _mark_operation_completed(db, op_reopen)

    close_operation(
        db,
        op_reopen,
        OperationCloseRequest(note="close conflict"),
        actor_user_id=_SUP_USER_ID,
        tenant_id=_TENANT_ID,
    )

    reopened = reopen_operation(
        db,
        op_reopen,
        OperationReopenRequest(reason="reopen should stay claim-independent"),
        actor_user_id=_SUP_USER_ID,
        tenant_id=_TENANT_ID,
    )
    assert reopened.closure_status == ClosureStatusEnum.open.value
    assert reopened.status == StatusEnum.paused.value

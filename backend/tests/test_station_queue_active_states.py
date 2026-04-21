"""
Regression tests for station queue status-source unification.

Locks the queue-read behavior where runtime status truth is event-derived
(shared with operation detail), not snapshot-driven.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.execution import DowntimeReasonClass, ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.schemas.operation import (
    OperationEndDowntimeRequest,
    OperationPauseRequest,
    OperationStartDowntimeRequest,
    OperationStartRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    derive_operation_detail,
    end_downtime,
    pause_operation,
    start_downtime,
    start_operation,
)
from app.services.station_claim_service import get_station_queue

_PREFIX = "TEST-QUEUE-ACTIVE-STATES"
_STATION_SCOPE_VALUE = f"{_PREFIX}-STATION-01"
_USER_ID = f"{_PREFIX}-USER"
_TENANT_ID = "default"


def _identity() -> RequestIdentity:
    return RequestIdentity(
        user_id=_USER_ID,
        username=_USER_ID,
        email=None,
        tenant_id=_TENANT_ID,
        role_code="OPR",
        is_authenticated=True,
    )


def _purge(db) -> None:
    # RBAC + operations created under the test prefix. Claims and audit logs
    # cascade from operations; events are cleaned explicitly.
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
                db.scalars(
                    select(Operation.id).where(Operation.work_order_id.in_(wo_ids))
                )
            )
            if op_ids:
                db.execute(
                    delete(OperationClaimAuditLog).where(
                        OperationClaimAuditLog.operation_id.in_(op_ids)
                    )
                )
                db.execute(
                    delete(OperationClaim).where(
                        OperationClaim.operation_id.in_(op_ids)
                    )
                )
                db.execute(
                    delete(ExecutionEvent).where(
                        ExecutionEvent.operation_id.in_(op_ids)
                    )
                )
            db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.execute(delete(UserRoleAssignment).where(UserRoleAssignment.user_id == _USER_ID))
    db.execute(
        delete(Scope).where(
            Scope.scope_value == _STATION_SCOPE_VALUE, Scope.tenant_id == _TENANT_ID
        )
    )
    db.commit()


def _ensure_opr_role(db) -> Role:
    # Role.code is globally unique; the canonical OPR role is installed by
    # init_db on most dev environments. Reuse it if present; otherwise insert
    # a minimal row so the test is self-contained.
    opr = db.scalar(select(Role).where(Role.code == "OPR"))
    if opr is not None:
        return opr
    opr = Role(code="OPR", name="Operator", role_type="system", is_system=True)
    db.add(opr)
    db.flush()
    return opr


@pytest.fixture
def station_queue_fixture():
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

        db.add(
            UserRoleAssignment(
                user_id=_USER_ID,
                role_id=opr_role.id,
                scope_id=scope.id,
                is_primary=True,
                is_active=True,
            )
        )

        po = ProductionOrder(
            order_number=f"{_PREFIX}-PO-001",
            route_id=f"{_PREFIX}-R-01",
            product_name="queue active-state round-trip",
            quantity=10,
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 6, 1, 8, 0, 0),
            planned_end=datetime(2099, 6, 1, 17, 0, 0),
            tenant_id=_TENANT_ID,
        )
        db.add(po)
        db.flush()

        wo = WorkOrder(
            production_order_id=po.id,
            work_order_number=f"{_PREFIX}-WO-001",
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 6, 1, 8, 0, 0),
            planned_end=datetime(2099, 6, 1, 17, 0, 0),
            tenant_id=_TENANT_ID,
        )
        db.add(wo)
        db.flush()

        # Four operations covering PLANNED, IN_PROGRESS, PAUSED, BLOCKED.
        def _mk(seq: int, suffix: str) -> Operation:
            op = Operation(
                operation_number=f"{_PREFIX}-OP-{suffix}",
                work_order_id=wo.id,
                sequence=seq,
                name=f"Op {suffix}",
                status=StatusEnum.planned.value,
                planned_start=datetime(2099, 6, 1, 9, seq, 0),
                planned_end=datetime(2099, 6, 1, 11, seq, 0),
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

        op_planned = _mk(10, "PLANNED")
        op_running = _mk(20, "IN_PROGRESS")
        op_paused = _mk(30, "PAUSED")
        op_blocked = _mk(40, "BLOCKED")

        db.commit()

        # Drive the three non-PLANNED ops through the real service layer so
        # the snapshot and event log both reflect the intended runtime state.
        # operator_id=None bypasses the station-busy guard for seeding.
        start_operation(
            db,
            op_running,
            OperationStartRequest(operator_id=None),
            tenant_id=_TENANT_ID,
        )
        start_operation(
            db, op_paused, OperationStartRequest(operator_id=None), tenant_id=_TENANT_ID
        )
        pause_operation(
            db,
            op_paused,
            OperationPauseRequest(reason_code=None, note=None),
            actor_user_id="seed",
            tenant_id=_TENANT_ID,
        )
        start_operation(
            db,
            op_blocked,
            OperationStartRequest(operator_id=None),
            tenant_id=_TENANT_ID,
        )
        start_downtime(
            db,
            op_blocked,
            OperationStartDowntimeRequest(
                reason_class=DowntimeReasonClass.UNPLANNED_BREAKDOWN, note="test"
            ),
            actor_user_id="seed",
            tenant_id=_TENANT_ID,
        )

        # Reload for snapshot-fresh fixtures.
        db.refresh(op_planned)
        db.refresh(op_running)
        db.refresh(op_paused)
        db.refresh(op_blocked)

        yield (
            db,
            {
                "planned": op_planned,
                "running": op_running,
                "paused": op_paused,
                "blocked": op_blocked,
            },
        )
    finally:
        _purge(db)
        db.close()


def _items_by_op_id(items: list[dict]) -> dict[int, dict]:
    return {item["operation_id"]: item for item in items}


def test_station_queue_returns_all_active_non_terminal_states(station_queue_fixture):
    db, ops = station_queue_fixture

    scope_value, items = get_station_queue(db, _identity())
    assert scope_value == _STATION_SCOPE_VALUE

    by_id = _items_by_op_id(items)
    # All four active operations are present.
    assert ops["planned"].id in by_id
    assert ops["running"].id in by_id
    assert ops["paused"].id in by_id
    assert ops["blocked"].id in by_id


def test_station_queue_projects_event_derived_status(station_queue_fixture):
    db, ops = station_queue_fixture
    _, items = get_station_queue(db, _identity())
    by_id = _items_by_op_id(items)

    assert by_id[ops["planned"].id]["status"] == StatusEnum.planned.value
    assert by_id[ops["running"].id]["status"] == StatusEnum.in_progress.value
    assert by_id[ops["paused"].id]["status"] == StatusEnum.paused.value
    assert by_id[ops["blocked"].id]["status"] == StatusEnum.blocked.value


def test_station_queue_downtime_open_reflects_event_log(station_queue_fixture):
    db, ops = station_queue_fixture
    _, items = get_station_queue(db, _identity())
    by_id = _items_by_op_id(items)

    # Only the op with an unmatched DOWNTIME_STARTED has downtime_open=true.
    assert by_id[ops["blocked"].id]["downtime_open"] is True
    assert by_id[ops["planned"].id]["downtime_open"] is False
    assert by_id[ops["running"].id]["downtime_open"] is False
    assert by_id[ops["paused"].id]["downtime_open"] is False


def test_station_queue_downtime_open_clears_after_end_downtime(station_queue_fixture):
    """Realistic round-trip: start_downtime→queue, end_downtime→queue."""
    db, ops = station_queue_fixture

    _, items_during = get_station_queue(db, _identity())
    blocked_during = _items_by_op_id(items_during)[ops["blocked"].id]
    assert blocked_during["status"] == StatusEnum.blocked.value
    assert blocked_during["downtime_open"] is True

    end_downtime(
        db,
        ops["blocked"],
        OperationEndDowntimeRequest(note="test-end"),
        actor_user_id="seed",
        tenant_id=_TENANT_ID,
    )
    db.refresh(ops["blocked"])

    _, items_after = get_station_queue(db, _identity())
    blocked_after = _items_by_op_id(items_after)[ops["blocked"].id]
    # end_downtime transitions BLOCKED → PAUSED on the snapshot. The op must
    # still appear in the queue (PAUSED is an active non-terminal state) and
    # downtime_open flips to False now that DOWNTIME_ENDED balances the started
    # count on the event log.
    assert blocked_after["status"] == StatusEnum.paused.value
    assert blocked_after["downtime_open"] is False


def test_station_queue_excludes_terminal_states(station_queue_fixture):
    db, ops = station_queue_fixture

    # Queue exclusion must follow event-derived terminal truth, not snapshot.
    # Appending OP_COMPLETED / OP_ABORTED events is sufficient to force
    # terminal derived status in the queue projection.
    from app.repositories.execution_event_repository import create_execution_event

    create_execution_event(
        db=db,
        event_type="OP_COMPLETED",
        production_order_id=ops["planned"].work_order.production_order_id,
        work_order_id=ops["planned"].work_order_id,
        operation_id=ops["planned"].id,
        payload={"completed_at": "2099-06-01T12:00:00"},
        tenant_id=_TENANT_ID,
    )
    create_execution_event(
        db=db,
        event_type="OP_COMPLETED",
        production_order_id=ops["running"].work_order.production_order_id,
        work_order_id=ops["running"].work_order_id,
        operation_id=ops["running"].id,
        payload={"completed_at": "2099-06-01T12:01:00"},
        tenant_id=_TENANT_ID,
    )
    create_execution_event(
        db=db,
        event_type="OP_ABORTED",
        production_order_id=ops["paused"].work_order.production_order_id,
        work_order_id=ops["paused"].work_order_id,
        operation_id=ops["paused"].id,
        payload={"aborted_at": "2099-06-01T12:02:00"},
        tenant_id=_TENANT_ID,
    )
    db.commit()

    _, items = get_station_queue(db, _identity())
    by_id = _items_by_op_id(items)
    assert ops["planned"].id not in by_id
    assert ops["running"].id not in by_id
    assert ops["paused"].id not in by_id
    # The BLOCKED op is untouched and must remain visible.
    assert ops["blocked"].id in by_id


def test_station_queue_and_detail_status_parity(station_queue_fixture):
    db, _ops = station_queue_fixture

    _, items = get_station_queue(db, _identity())
    for item in items:
        operation = db.scalar(select(Operation).where(Operation.id == item["operation_id"]))
        assert operation is not None
        detail = derive_operation_detail(db, operation)
        assert item["status"] == detail.status


def test_station_queue_uses_derived_status_when_snapshot_is_stale(
    station_queue_fixture,
):
    db, ops = station_queue_fixture

    # Introduce an intentional mismatch: event-derived remains IN_PROGRESS
    # while snapshot is forcibly set to PAUSED.
    ops["running"].status = StatusEnum.paused.value
    db.add(ops["running"])
    db.commit()

    _, items = get_station_queue(db, _identity())
    by_id = _items_by_op_id(items)

    operation = db.scalar(select(Operation).where(Operation.id == ops["running"].id))
    assert operation is not None
    detail = derive_operation_detail(db, operation)

    assert detail.status == StatusEnum.in_progress.value
    assert by_id[ops["running"].id]["status"] == StatusEnum.in_progress.value


def test_station_queue_claim_fields_unchanged(station_queue_fixture):
    db, ops = station_queue_fixture
    _, items = get_station_queue(db, _identity())
    by_id = _items_by_op_id(items)

    # No claims were created in the fixture; every item must report the
    # canonical unclaimed summary.
    for op_key in ("planned", "running", "paused", "blocked"):
        claim = by_id[ops[op_key].id]["claim"]
        assert claim["state"] == "none"
        assert claim["expires_at"] is None
        assert claim["claimed_by_user_id"] is None

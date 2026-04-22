"""
Regression tests for OperationDetail.allowed_actions projection.

Scope: Proves that _derive_allowed_actions(status, downtime_open) and the
derive_operation_detail round-trip return exactly the canonical lower_snake
action names currently promised by station-execution-command-event-contracts.md
§3. These tests lock the projection behavior as it exists today so backend
refactors cannot silently break the Station Execution cockpit.

Non-goals:
- Does not test claim ownership (not encoded in allowed_actions).
- Does not test station-busy resume blocker (not encoded).
- Does not test QC/review/closure blockers (not yet modeled).
"""

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.execution import DowntimeReasonClass, ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.schemas.operation import (
    OperationEndDowntimeRequest,
    OperationStartDowntimeRequest,
)
from app.services.operation_service import (
    _derive_allowed_actions,
    derive_operation_detail,
    end_downtime,
    start_downtime,
)

CANONICAL_ACTIONS = {
    "start_execution",
    "report_production",
    "pause_execution",
    "resume_execution",
    "start_downtime",
    "end_downtime",
    "complete_execution",
}


# ─── Pure unit tests for _derive_allowed_actions ─────────────────────────────
# These are the authoritative coverage for every (status, downtime_open) combo
# the cockpit can encounter. derive_operation_detail delegates to this function,
# so proving the pure projection is correct is necessary and sufficient for
# snapshot-driven cases. The event round-trip below proves the wiring.


@pytest.mark.parametrize(
    "status, downtime_open, expected",
    [
        # PLANNED: only start_execution is allowed. Nothing else, regardless
        # of the downtime flag (a PLANNED op cannot have downtime events).
        (StatusEnum.planned.value, False, ["start_execution"]),
        # IN_PROGRESS, no downtime: the three execution-level commands plus
        # start_downtime. resume_execution is NOT in the list (running ops
        # cannot resume themselves).
        (
            StatusEnum.in_progress.value,
            False,
            [
                "report_production",
                "pause_execution",
                "complete_execution",
                "start_downtime",
            ],
        ),
        # IN_PROGRESS + downtime_open: a surprising but intentional case today.
        # In practice start_downtime transitions IN_PROGRESS → BLOCKED, so this
        # combination should not appear via normal commands. The pure function
        # still has to answer deterministically — it keeps the IN_PROGRESS action
        # block AND adds end_downtime, but omits start_downtime (already open).
        # Reported explicitly because it looks awkward on paper.
        (
            StatusEnum.in_progress.value,
            True,
            [
                "report_production",
                "pause_execution",
                "complete_execution",
                "end_downtime",
            ],
        ),
        # PAUSED, no downtime: resume_execution + start_downtime.
        (
            StatusEnum.paused.value,
            False,
            ["resume_execution", "start_downtime"],
        ),
        # PAUSED + downtime_open: resume is correctly suppressed (resume_operation
        # rejects with STATE_DOWNTIME_OPEN at the service layer), only end_downtime
        # remains.
        (StatusEnum.paused.value, True, ["end_downtime"]),
        # BLOCKED + downtime_open: only end_downtime. This is the normal way a
        # BLOCKED op appears in practice (start_downtime on RUNNING → BLOCKED).
        (StatusEnum.blocked.value, True, ["end_downtime"]),
        # BLOCKED, no downtime: currently returns []. This is awkward because
        # in the live model the only way to leave BLOCKED is end_downtime, and
        # end_downtime rejects without an open downtime. A BLOCKED snapshot
        # with no open downtime would be stuck. Tested as-is because it matches
        # current pure-projection truth; flagged in the report.
        (StatusEnum.blocked.value, False, []),
        # Closed records return [] regardless of downtime_open.
        (StatusEnum.completed.value, False, []),
        (StatusEnum.completed.value, True, []),
        (StatusEnum.completed_late.value, False, []),
        (StatusEnum.completed_late.value, True, []),
        (StatusEnum.aborted.value, False, []),
        (StatusEnum.aborted.value, True, []),
    ],
    ids=[
        "PLANNED",
        "IN_PROGRESS_no_downtime",
        "IN_PROGRESS_with_downtime_open",
        "PAUSED_no_downtime",
        "PAUSED_with_downtime_open",
        "BLOCKED_with_downtime_open",
        "BLOCKED_no_downtime_awkward",
        "COMPLETED",
        "COMPLETED_with_downtime_open",
        "COMPLETED_LATE",
        "COMPLETED_LATE_with_downtime_open",
        "ABORTED",
        "ABORTED_with_downtime_open",
    ],
)
def test_derive_allowed_actions_matrix(status, downtime_open, expected):
    result = _derive_allowed_actions(status, downtime_open)
    # Exact match, not membership, so ordering and extras both fail the test.
    assert result == expected, (
        f"allowed_actions for status={status}, downtime_open={downtime_open} "
        f"must be exactly {expected!r}, got {result!r}"
    )
    # Every returned name must be canonical (no typos, no legacy UPPER_SNAKE).
    assert set(result).issubset(CANONICAL_ACTIONS), (
        f"Non-canonical action name in {result!r}; "
        f"allowed names: {sorted(CANONICAL_ACTIONS)}"
    )


def test_derive_allowed_actions_never_includes_unknown_actions():
    """Sanity: the pure function never emits anything outside the canonical set."""
    for status_member in StatusEnum:
        for downtime_open in (False, True):
            actions = _derive_allowed_actions(status_member.value, downtime_open)
            unknown = set(actions) - CANONICAL_ACTIONS
            assert unknown == set(), (
                f"Unexpected action(s) {unknown!r} for "
                f"status={status_member.value}, downtime_open={downtime_open}"
            )


def test_derive_allowed_actions_closed_is_always_empty():
    """Closed records cannot emit any action, with or without an open downtime."""
    for closed in (
        StatusEnum.completed.value,
        StatusEnum.completed_late.value,
        StatusEnum.aborted.value,
    ):
        assert _derive_allowed_actions(closed, False) == []
        assert _derive_allowed_actions(closed, True) == []


# ─── Event-driven round-trip against the real session ───────────────────────
# Exercises derive_operation_detail end-to-end: start_downtime ⇒ downtime_open
# flips, allowed_actions loses start_downtime and gains end_downtime; then
# end_downtime ⇒ downtime_open clears, BLOCKED snapshot transitions to PAUSED,
# and allowed_actions returns to the PAUSED set.


_ROUNDTRIP_PREFIX = "TEST-ALLOWED-ACTIONS"


def _purge(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_ROUNDTRIP_PREFIX}-%")
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
            delete(ExecutionEvent).where(ExecutionEvent.work_order_id.in_(wo_ids))
        )
        db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
    db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.commit()


@pytest.fixture
def running_operation():
    """Yields an operation snapshot already in IN_PROGRESS with no events
    written by us yet (status is directly set; the round-trip test inspects
    derive_operation_detail output, not status-derivation semantics)."""
    db = SessionLocal()
    try:
        _purge(db)

        po = ProductionOrder(
            order_number=f"{_ROUNDTRIP_PREFIX}-PO-001",
            route_id=f"{_ROUNDTRIP_PREFIX}-R-01",
            product_name="allowed_actions round-trip",
            quantity=10,
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 6, 1, 8, 0, 0),
            planned_end=datetime(2099, 6, 1, 17, 0, 0),
            tenant_id="default",
        )
        db.add(po)
        db.flush()

        wo = WorkOrder(
            production_order_id=po.id,
            work_order_number=f"{_ROUNDTRIP_PREFIX}-WO-001",
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 6, 1, 8, 0, 0),
            planned_end=datetime(2099, 6, 1, 17, 0, 0),
            tenant_id="default",
        )
        db.add(wo)
        db.flush()

        op = Operation(
            operation_number=f"{_ROUNDTRIP_PREFIX}-OP-001",
            work_order_id=wo.id,
            sequence=10,
            name="round-trip op",
            # We place the snapshot directly in IN_PROGRESS with an OP_STARTED
            # event so _derive_status also returns IN_PROGRESS. This isolates
            # the round-trip test from other projection concerns.
            status=StatusEnum.in_progress.value,
            planned_start=datetime(2099, 6, 1, 9, 0, 0),
            planned_end=datetime(2099, 6, 1, 11, 0, 0),
            quantity=10,
            completed_qty=0,
            good_qty=0,
            scrap_qty=0,
            qc_required=False,
            station_scope_value="STATION_TEST_AA",
            tenant_id="default",
        )
        db.add(op)
        db.flush()

        # Append an OP_STARTED event so _derive_status returns IN_PROGRESS,
        # matching the snapshot. No other events are added.
        from app.models.execution import ExecutionEventType
        from app.repositories.execution_event_repository import create_execution_event

        create_execution_event(
            db=db,
            event_type=ExecutionEventType.OP_STARTED.value,
            production_order_id=po.id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"operator_id": None, "started_at": "2099-06-01T09:15:00"},
            tenant_id="default",
        )
        db.commit()
        db.refresh(op)

        yield db, op
    finally:
        _purge(db)
        db.close()


def test_event_roundtrip_start_then_end_downtime(running_operation):
    db, op = running_operation

    # Baseline: IN_PROGRESS, no downtime → full running set.
    before = derive_operation_detail(db, op)
    assert before.downtime_open is False
    assert before.allowed_actions == [
        "report_production",
        "pause_execution",
        "complete_execution",
        "start_downtime",
    ]

    # Drive start_downtime through the real service. This appends a
    # DOWNTIME_STARTED event AND transitions the snapshot IN_PROGRESS → BLOCKED.
    start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(
            reason_class=DowntimeReasonClass.MATERIAL_SHORTAGE,
            note="roundtrip-test",
        ),
        actor_user_id="test-actor",
        tenant_id="default",
    )
    db.refresh(op)

    # After start_downtime: snapshot is BLOCKED, derived status is BLOCKED
    # (SE-BE-DERIVE-STATUS-BLOCKED-001), downtime_open is true, and
    # allowed_actions must be exactly ["end_downtime"]. start_downtime must
    # disappear; no other action may appear.
    after_start = derive_operation_detail(db, op)
    assert after_start.downtime_open is True
    assert after_start.status == StatusEnum.blocked.value
    assert after_start.allowed_actions == ["end_downtime"], (
        f"After start_downtime expected ['end_downtime'], "
        f"got {after_start.allowed_actions!r}"
    )
    assert "start_downtime" not in after_start.allowed_actions
    assert op.status == StatusEnum.blocked.value

    # Drive end_downtime. Per current backend policy this closes the downtime,
    # transitions BLOCKED → PAUSED on the snapshot (so a subsequent resume
    # becomes addressable), and the projection must reflect the PAUSED set.
    end_downtime(
        db,
        op,
        OperationEndDowntimeRequest(note="roundtrip-test-end"),
        actor_user_id="test-actor",
        tenant_id="default",
    )
    db.refresh(op)

    after_end = derive_operation_detail(db, op)
    assert after_end.downtime_open is False
    # Per SE-BE-DERIVE-STATUS-PAUSED-AFTER-END-DOWNTIME-001, derived status
    # falls back to PAUSED when no explicit EXECUTION_RESUMED has followed the
    # DOWNTIME_ENDED event. Snapshot and derived now agree.
    assert after_end.status == StatusEnum.paused.value
    assert op.status == StatusEnum.paused.value
    assert after_end.allowed_actions == ["resume_execution", "start_downtime"], (
        f"After end_downtime expected PAUSED action set, "
        f"got {after_end.allowed_actions!r}"
    )
    assert "end_downtime" not in after_end.allowed_actions
    # No auto-resume: end_downtime must not have emitted EXECUTION_RESUMED.
    from app.models.execution import ExecutionEventType as _EET
    from app.repositories.execution_event_repository import (
        get_events_for_operation as _get_events,
    )

    roundtrip_events = _get_events(db, op.id)
    assert not any(
        e.event_type == _EET.EXECUTION_RESUMED.value for e in roundtrip_events
    ), "end_downtime must not auto-resume execution"


def test_derive_operation_detail_exposes_accumulated_pause_and_downtime_ms(
    running_operation,
):
    db, op = running_operation

    from app.models.execution import ExecutionEventType
    from app.repositories.execution_event_repository import create_execution_event

    # Two closed pause intervals: 5m + 2m = 7m total.
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.EXECUTION_PAUSED.value,
        production_order_id=op.work_order.production_order_id,
        work_order_id=op.work_order_id,
        operation_id=op.id,
        payload={"paused_at": "2099-06-01T09:20:00"},
        tenant_id="default",
    )
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.EXECUTION_RESUMED.value,
        production_order_id=op.work_order.production_order_id,
        work_order_id=op.work_order_id,
        operation_id=op.id,
        payload={"resumed_at": "2099-06-01T09:25:00"},
        tenant_id="default",
    )
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.EXECUTION_PAUSED.value,
        production_order_id=op.work_order.production_order_id,
        work_order_id=op.work_order_id,
        operation_id=op.id,
        payload={"paused_at": "2099-06-01T09:30:00"},
        tenant_id="default",
    )
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.EXECUTION_RESUMED.value,
        production_order_id=op.work_order.production_order_id,
        work_order_id=op.work_order_id,
        operation_id=op.id,
        payload={"resumed_at": "2099-06-01T09:32:00"},
        tenant_id="default",
    )

    # One closed downtime interval: 6m total.
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.DOWNTIME_STARTED.value,
        production_order_id=op.work_order.production_order_id,
        work_order_id=op.work_order_id,
        operation_id=op.id,
        payload={"started_at": "2099-06-01T09:40:00"},
        tenant_id="default",
    )
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.DOWNTIME_ENDED.value,
        production_order_id=op.work_order.production_order_id,
        work_order_id=op.work_order_id,
        operation_id=op.id,
        payload={"ended_at": "2099-06-01T09:46:00"},
        tenant_id="default",
    )

    detail = derive_operation_detail(db, op)
    assert detail.paused_total_ms == 420000
    assert detail.downtime_total_ms == 360000


def test_blocked_snapshot_and_derived_status_align_during_open_downtime(
    running_operation,
):
    """
    Locks the post-SE-BE-DERIVE-STATUS-BLOCKED-001 contract: when an open
    downtime exists on a started operation, _derive_status(events) returns
    BLOCKED, matching the snapshot. This replaces the prior divergence test
    that documented _derive_status returning IN_PROGRESS in the same scenario.
    """
    db, op = running_operation

    start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(
            reason_class=DowntimeReasonClass.UNPLANNED_BREAKDOWN,
            note="derive-status-blocked",
        ),
        actor_user_id="test-actor",
        tenant_id="default",
    )
    db.refresh(op)

    detail = derive_operation_detail(db, op)
    # Snapshot and derived status now agree: both BLOCKED.
    assert op.status == StatusEnum.blocked.value
    assert detail.status == StatusEnum.blocked.value
    assert detail.downtime_open is True
    # allowed_actions is unchanged by the derive_status fix — snapshot-driven
    # and still correctly yields only ["end_downtime"] for BLOCKED + open
    # downtime.
    assert detail.allowed_actions == ["end_downtime"]


def test_start_downtime_allows_second_cycle_after_end_downtime(running_operation):
    """
    Regression for open-downtime detection: once a downtime is ended,
    start_downtime must be allowed again (started_count == ended_count).
    """
    db, op = running_operation

    start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(
            reason_class=DowntimeReasonClass.MATERIAL_SHORTAGE,
            note="cycle-1-start",
        ),
        actor_user_id="test-actor",
        tenant_id="default",
    )
    db.refresh(op)

    end_downtime(
        db,
        op,
        OperationEndDowntimeRequest(note="cycle-1-end"),
        actor_user_id="test-actor",
        tenant_id="default",
    )
    db.refresh(op)

    second = start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(
            reason_class=DowntimeReasonClass.UNPLANNED_BREAKDOWN,
            note="cycle-2-start",
        ),
        actor_user_id="test-actor",
        tenant_id="default",
    )

    assert second.downtime_open is True
    assert second.status == StatusEnum.blocked.value
    assert second.allowed_actions == ["end_downtime"]


def test_detail_allowed_actions_uses_derived_status_when_snapshot_is_paused(
    running_operation,
):
    db, op = running_operation

    # Introduce stale projection: snapshot says PAUSED while event truth remains
    # IN_PROGRESS (only OP_STARTED exists).
    op.status = StatusEnum.paused.value
    db.add(op)
    db.commit()
    db.refresh(op)

    detail = derive_operation_detail(db, op)

    assert detail.status == StatusEnum.in_progress.value
    assert detail.allowed_actions == [
        "report_production",
        "pause_execution",
        "complete_execution",
        "start_downtime",
    ]


def test_detail_allowed_actions_uses_derived_status_when_snapshot_is_in_progress(
    running_operation,
):
    db, op = running_operation

    # Build PAUSED runtime truth: append a pause event.
    from app.repositories.execution_event_repository import create_execution_event

    create_execution_event(
        db=db,
        event_type="execution_paused",
        production_order_id=op.work_order.production_order_id,
        work_order_id=op.work_order_id,
        operation_id=op.id,
        payload={"paused_at": "2099-06-01T09:20:00", "actor_user_id": "seed"},
        tenant_id="default",
    )

    # Introduce stale projection opposite direction: snapshot says IN_PROGRESS.
    op.status = StatusEnum.in_progress.value
    db.add(op)
    db.commit()
    db.refresh(op)

    detail = derive_operation_detail(db, op)

    assert detail.status == StatusEnum.paused.value
    assert detail.allowed_actions == ["resume_execution", "start_downtime"]

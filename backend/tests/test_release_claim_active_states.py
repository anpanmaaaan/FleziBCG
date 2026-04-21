from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.security.dependencies import RequestIdentity
from app.services.station_claim_service import claim_operation, release_operation_claim
from app.services.station_claim_service import get_operation_claim_status

_PREFIX = "TEST-RELEASE-CLAIM-ACTIVE"
_TENANT_ID = "default"
_STATION_SCOPE_VALUE = f"{_PREFIX}-STATION-01"
_OTHER_STATION_SCOPE_VALUE = f"{_PREFIX}-STATION-02"
_OWNER_USER_ID = f"{_PREFIX}-OWNER"
_OTHER_USER_ID = f"{_PREFIX}-OTHER"
_WRONG_SCOPE_USER_ID = f"{_PREFIX}-WRONG-SCOPE"


def _identity(
    user_id: str,
    *,
    role_code: str = "OPR",
    acting_role_code: str | None = None,
) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username=user_id,
        email=None,
        tenant_id=_TENANT_ID,
        role_code=role_code,
        acting_role_code=acting_role_code,
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

    db.execute(
        delete(UserRoleAssignment).where(
            UserRoleAssignment.user_id.in_(
                [_OWNER_USER_ID, _OTHER_USER_ID, _WRONG_SCOPE_USER_ID]
            )
        )
    )
    db.execute(
        delete(Scope).where(
            Scope.scope_value.like(f"{_PREFIX}-STATION-%"),
            Scope.tenant_id == _TENANT_ID,
        )
    )
    db.commit()


def _ensure_opr_role(db) -> Role:
    opr = db.scalar(select(Role).where(Role.code == "OPR"))
    if opr is not None:
        return opr
    opr = Role(code="OPR", name="Operator", role_type="system", is_system=True)
    db.add(opr)
    db.flush()
    return opr


@pytest.fixture
def release_claim_fixture():
    db = SessionLocal()
    try:
        _purge(db)
        opr_role = _ensure_opr_role(db)

        scope = Scope(
            tenant_id=_TENANT_ID,
            scope_type="station",
            scope_value=_STATION_SCOPE_VALUE,
        )
        other_scope = Scope(
            tenant_id=_TENANT_ID,
            scope_type="station",
            scope_value=_OTHER_STATION_SCOPE_VALUE,
        )
        db.add(scope)
        db.add(other_scope)
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
                UserRoleAssignment(
                    user_id=_WRONG_SCOPE_USER_ID,
                    role_id=opr_role.id,
                    scope_id=other_scope.id,
                    is_primary=True,
                    is_active=True,
                ),
            ]
        )

        po = ProductionOrder(
            order_number=f"{_PREFIX}-PO-001",
            route_id=f"{_PREFIX}-R-01",
            product_name="release claim active states",
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

        def _mk_op(seq: int, suffix: str) -> Operation:
            minute_slot = seq // 10
            op = Operation(
                operation_number=f"{_PREFIX}-OP-{suffix}",
                work_order_id=wo.id,
                sequence=seq,
                name=f"Release Claim {suffix}",
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
            "in_progress": _mk_op(10, "IN_PROGRESS"),
            "paused": _mk_op(20, "PAUSED"),
            "blocked": _mk_op(30, "BLOCKED"),
            "terminal": _mk_op(40, "TERMINAL"),
            "owner_guard": _mk_op(50, "OWNER_GUARD"),
            "override": _mk_op(60, "OVERRIDE"),
        }
        db.commit()
        yield db, ops
    finally:
        _purge(db)
        db.close()


def _claim_as_owner(db, operation_id: int) -> None:
    claim_operation(
        db,
        _identity(_OWNER_USER_ID),
        operation_id,
        reason="test-claim",
    )


def test_release_claim_rejects_in_progress(release_claim_fixture):
    """Guard: release on IN_PROGRESS is blocked to prevent execution dead-end."""
    db, ops = release_claim_fixture
    operation = ops["in_progress"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.in_progress.value
    db.add(operation)
    db.commit()

    with pytest.raises(ValueError, match="active execution state"):
        release_operation_claim(
            db,
            _identity(_OWNER_USER_ID),
            operation.id,
            reason="release-in-progress",
        )


def test_release_claim_rejects_paused(release_claim_fixture):
    """Guard: release on PAUSED is blocked to prevent execution dead-end."""
    db, ops = release_claim_fixture
    operation = ops["paused"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.paused.value
    db.add(operation)
    db.commit()

    with pytest.raises(ValueError, match="active execution state"):
        release_operation_claim(
            db,
            _identity(_OWNER_USER_ID),
            operation.id,
            reason="release-paused",
        )


def test_release_claim_rejects_blocked(release_claim_fixture):
    """Guard: release on BLOCKED is blocked to prevent execution dead-end."""
    db, ops = release_claim_fixture
    operation = ops["blocked"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.blocked.value
    db.add(operation)
    db.commit()

    with pytest.raises(ValueError, match="active execution state"):
        release_operation_claim(
            db,
            _identity(_OWNER_USER_ID),
            operation.id,
            reason="release-blocked",
        )


def test_release_claim_succeeds_on_planned(release_claim_fixture):
    """PLANNED is the only active state where release is safe."""
    db, ops = release_claim_fixture
    operation = ops["owner_guard"]

    _claim_as_owner(db, operation.id)
    # operation is already PLANNED (fixture default)—no status change needed
    db.commit()

    claim, scope_value = release_operation_claim(
        db,
        _identity(_OWNER_USER_ID),
        operation.id,
        reason="release-planned",
    )

    assert scope_value == _STATION_SCOPE_VALUE
    assert claim.released_at is not None
    assert claim.release_reason == "release-planned"


def test_release_claim_rejects_terminal_status(release_claim_fixture):
    db, ops = release_claim_fixture
    operation = ops["terminal"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.completed.value
    db.add(operation)
    db.commit()

    with pytest.raises(
        ValueError, match="Operation is not releasable in current status"
    ):
        release_operation_claim(
            db,
            _identity(_OWNER_USER_ID),
            operation.id,
            reason="release-terminal",
        )


def test_release_claim_rejects_non_owner_without_override(release_claim_fixture):
    """Non-owner cannot release a PLANNED (releasable) operation."""
    db, ops = release_claim_fixture
    operation = ops["override"]

    _claim_as_owner(db, operation.id)
    # Keep PLANNED so the active-execution guard does not fire first.
    db.commit()

    with pytest.raises(
        PermissionError, match="Only the claim owner may release this claim"
    ):
        release_operation_claim(
            db,
            _identity(_OTHER_USER_ID),
            operation.id,
            reason="non-owner-release",
        )


def test_release_claim_allows_admin_support_override_on_planned(release_claim_fixture):
    """ADM/OTS impersonating OPR can release a PLANNED claim owned by another operator."""
    db, ops = release_claim_fixture
    operation = ops["in_progress"]  # reuse; status kept PLANNED

    _claim_as_owner(db, operation.id)
    # Keep PLANNED so the active-execution guard does not fire first.
    db.commit()

    claim, _ = release_operation_claim(
        db,
        _identity(_OTHER_USER_ID, role_code="ADM", acting_role_code="OPR"),
        operation.id,
        reason="support-override",
    )

    assert claim.released_at is not None


def test_release_claim_rejects_wrong_station_scope(release_claim_fixture):
    """Wrong-scope check fires even on PLANNED operations."""
    db, ops = release_claim_fixture
    operation = ops["paused"]  # reuse; status kept PLANNED from fixture

    _claim_as_owner(db, operation.id)
    db.commit()

    with pytest.raises(
        PermissionError, match="Operation is outside your station scope"
    ):
        release_operation_claim(
            db,
            _identity(_WRONG_SCOPE_USER_ID),
            operation.id,
            reason="wrong-scope-release",
        )


def test_get_claim_status_returns_mine_on_in_progress(release_claim_fixture):
    db, ops = release_claim_fixture
    operation = ops["in_progress"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.in_progress.value
    db.add(operation)
    db.commit()

    status = get_operation_claim_status(db, _identity(_OWNER_USER_ID), operation.id)

    assert status["state"] == "mine"
    assert status["claimed_by_user_id"] == _OWNER_USER_ID
    assert status["station_scope_value"] == _STATION_SCOPE_VALUE


def test_get_claim_status_returns_mine_on_paused(release_claim_fixture):
    db, ops = release_claim_fixture
    operation = ops["paused"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.paused.value
    db.add(operation)
    db.commit()

    status = get_operation_claim_status(db, _identity(_OWNER_USER_ID), operation.id)

    assert status["state"] == "mine"
    assert status["claimed_by_user_id"] == _OWNER_USER_ID


def test_get_claim_status_returns_mine_on_blocked(release_claim_fixture):
    db, ops = release_claim_fixture
    operation = ops["blocked"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.blocked.value
    db.add(operation)
    db.commit()

    status = get_operation_claim_status(db, _identity(_OWNER_USER_ID), operation.id)

    assert status["state"] == "mine"
    assert status["claimed_by_user_id"] == _OWNER_USER_ID


def test_get_claim_status_rejects_wrong_station_scope(release_claim_fixture):
    db, ops = release_claim_fixture
    operation = ops["blocked"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.blocked.value
    db.add(operation)
    db.commit()

    with pytest.raises(
        PermissionError, match="Operation is outside your station scope"
    ):
        get_operation_claim_status(db, _identity(_WRONG_SCOPE_USER_ID), operation.id)


def test_get_claim_status_rejects_terminal_status(release_claim_fixture):
    db, ops = release_claim_fixture
    operation = ops["terminal"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.completed.value
    db.add(operation)
    db.commit()

    with pytest.raises(
        ValueError, match="Operation is not releasable in current status"
    ):
        get_operation_claim_status(db, _identity(_OWNER_USER_ID), operation.id)


def test_get_claim_status_expires_stale_claim_on_read(release_claim_fixture):
    db, ops = release_claim_fixture
    operation = ops["paused"]

    _claim_as_owner(db, operation.id)
    operation.status = StatusEnum.paused.value
    db.add(operation)
    db.commit()

    claim = db.scalar(
        select(OperationClaim).where(
            OperationClaim.operation_id == operation.id,
            OperationClaim.tenant_id == _TENANT_ID,
            OperationClaim.released_at.is_(None),
        )
    )
    assert claim is not None
    claim.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.add(claim)
    db.commit()

    status = get_operation_claim_status(db, _identity(_OWNER_USER_ID), operation.id)

    assert status["state"] == "none"
    expired_event = db.scalar(
        select(OperationClaimAuditLog).where(
            OperationClaimAuditLog.operation_id == operation.id,
            OperationClaimAuditLog.event_type == "CLAIM_EXPIRED",
        )
    )
    assert expired_event is not None

"""
Operator Clock Off verification script.

Checks:
1) Complete without claim -> 403
2) Complete when status != IN_PROGRESS -> 409
3) Clock On -> Clock Off -> OP_COMPLETED exists and status COMPLETED
4) Double Clock Off -> 409 and no duplicate OP_COMPLETED
5) Clock On OP A -> Clock Off OP A -> Clock On OP B (same station) -> PASS
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import app
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, RoleScope, Scope, UserRole, UserRoleAssignment
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.models.user import User
from app.security.auth import pwd_context

TENANT_ID = "default"
PASSWORD = "password123"
_SUFFIX = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")

USER_ID = f"verify-clockoff-opr-{_SUFFIX}"
USERNAME = f"verify_clockoff_opr_{_SUFFIX}"
PO_NUMBER = f"PH6-CLOCKOFF-PO-{_SUFFIX}"
WO_NUMBER = f"PH6-CLOCKOFF-WO-{_SUFFIX}"
STATION_SCOPE = "STATION_01"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID,
    }


def _ensure_station_scope(db) -> Scope:
    station_scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == TENANT_ID,
            Scope.scope_type == "station",
            Scope.scope_value == STATION_SCOPE,
        )
    )
    if station_scope is not None:
        return station_scope

    tenant_scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == TENANT_ID,
            Scope.scope_type == "tenant",
            Scope.scope_value == TENANT_ID,
        )
    )
    if tenant_scope is None:
        tenant_scope = Scope(
            tenant_id=TENANT_ID,
            scope_type="tenant",
            scope_value=TENANT_ID,
            parent_scope_id=None,
        )
        db.add(tenant_scope)
        db.flush()

    line_scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == TENANT_ID,
            Scope.scope_type == "line",
            Scope.scope_value == "LINE_A",
        )
    )
    if line_scope is None:
        line_scope = Scope(
            tenant_id=TENANT_ID,
            scope_type="line",
            scope_value="LINE_A",
            parent_scope_id=tenant_scope.id,
        )
        db.add(line_scope)
        db.flush()

    station_scope = Scope(
        tenant_id=TENANT_ID,
        scope_type="station",
        scope_value=STATION_SCOPE,
        parent_scope_id=line_scope.id,
    )
    db.add(station_scope)
    db.flush()
    return station_scope


def _seed_user_and_role(db) -> None:
    role = db.scalar(select(Role).where(Role.code == "OPR"))
    if role is None:
        raise RuntimeError("Role OPR not found")

    user = User(
        user_id=USER_ID,
        username=USERNAME,
        email=f"{USERNAME}@example.com",
        password_hash=pwd_context.hash(PASSWORD),
        tenant_id=TENANT_ID,
        is_active=True,
    )
    db.add(user)
    db.flush()

    user_role = UserRole(
        user_id=USER_ID,
        role_id=role.id,
        tenant_id=TENANT_ID,
        is_active=True,
    )
    db.add(user_role)
    db.flush()

    db.add(
        RoleScope(
            user_role_id=user_role.id,
            scope_type="tenant",
            scope_value=TENANT_ID,
        )
    )

    station_scope = _ensure_station_scope(db)
    db.add(
        UserRoleAssignment(
            user_id=USER_ID,
            role_id=role.id,
            scope_id=station_scope.id,
            is_primary=True,
            is_active=True,
        )
    )


def _seed_operations(db) -> tuple[int, int]:
    po = ProductionOrder(
        order_number=PO_NUMBER,
        route_id="PH6-CLOCKOFF-R01",
        product_name="Clock Off Verify Product",
        quantity=20,
        status=StatusEnum.pending.value,
        planned_start=datetime(2099, 6, 1, 8, 0, 0),
        planned_end=datetime(2099, 6, 1, 12, 0, 0),
        tenant_id=TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=WO_NUMBER,
        status=StatusEnum.pending.value,
        planned_start=datetime(2099, 6, 1, 8, 0, 0),
        planned_end=datetime(2099, 6, 1, 12, 0, 0),
        tenant_id=TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op_a = Operation(
        operation_number=f"PH6-CLOCKOFF-OPA-{_SUFFIX}",
        work_order_id=wo.id,
        sequence=10,
        name="Clock Off A",
        status=StatusEnum.pending.value,
        planned_start=datetime(2099, 6, 1, 8, 10, 0),
        planned_end=datetime(2099, 6, 1, 9, 0, 0),
        quantity=10,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=False,
        station_scope_value=STATION_SCOPE,
        tenant_id=TENANT_ID,
    )
    op_b = Operation(
        operation_number=f"PH6-CLOCKOFF-OPB-{_SUFFIX}",
        work_order_id=wo.id,
        sequence=20,
        name="Clock Off B",
        status=StatusEnum.pending.value,
        planned_start=datetime(2099, 6, 1, 9, 10, 0),
        planned_end=datetime(2099, 6, 1, 10, 0, 0),
        quantity=10,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=False,
        station_scope_value=STATION_SCOPE,
        tenant_id=TENANT_ID,
    )
    db.add_all([op_a, op_b])
    db.commit()
    return op_a.id, op_b.id


def _cleanup(db) -> None:
    operation_ids = list(
        db.scalars(
            select(Operation.id).where(
                Operation.operation_number.like(f"PH6-CLOCKOFF-%-{_SUFFIX}")
            )
        )
    )
    if operation_ids:
        db.execute(
            delete(OperationClaimAuditLog).where(
                OperationClaimAuditLog.operation_id.in_(operation_ids)
            )
        )
        db.execute(
            delete(OperationClaim).where(OperationClaim.operation_id.in_(operation_ids))
        )
        db.execute(
            delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(operation_ids))
        )

    wo_ids = list(
        db.scalars(select(WorkOrder.id).where(WorkOrder.work_order_number == WO_NUMBER))
    )
    if wo_ids:
        db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))

    db.execute(delete(ProductionOrder).where(ProductionOrder.order_number == PO_NUMBER))

    db.execute(delete(UserRoleAssignment).where(UserRoleAssignment.user_id == USER_ID))
    user_roles = list(db.scalars(select(UserRole).where(UserRole.user_id == USER_ID)))
    if user_roles:
        ur_ids = [ur.id for ur in user_roles]
        db.execute(delete(RoleScope).where(RoleScope.user_role_id.in_(ur_ids)))
    db.execute(delete(UserRole).where(UserRole.user_id == USER_ID))
    db.execute(delete(User).where(User.user_id == USER_ID))
    db.commit()


def _login(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": USERNAME, "password": PASSWORD},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Login failed: {response.status_code} {response.text}")
    return response.json()["access_token"]


def _count_completed_events(db, operation_id: int) -> int:
    return len(
        list(
            db.scalars(
                select(ExecutionEvent).where(
                    ExecutionEvent.operation_id == operation_id,
                    ExecutionEvent.event_type == ExecutionEventType.OP_COMPLETED.value,
                )
            )
        )
    )


def _print_results(results: list[Check]) -> None:
    print("\nClock Off Verification")
    print("----------------------")
    for check in results:
        state = "PASS" if check.passed else "FAIL"
        print(f"[{state}] {check.name}: {check.detail}")


def main() -> None:
    init_db()

    with SessionLocal() as db:
        _cleanup(db)
        _seed_user_and_role(db)
        op_a_id, op_b_id = _seed_operations(db)

    client = TestClient(app)
    token = _login(client)
    headers = _auth_headers(token)

    checks: list[Check] = []

    # 1) Complete without claim -> 403
    complete_without_claim = client.post(
        f"/api/v1/operations/{op_a_id}/complete",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    checks.append(
        Check(
            name="1) Complete without claim",
            passed=complete_without_claim.status_code == 403,
            detail=f"status={complete_without_claim.status_code}",
        )
    )

    # 2) Complete when status != IN_PROGRESS -> 409
    claim_a = client.post(
        f"/api/v1/station/queue/{op_a_id}/claim",
        headers=headers,
        json={},
    )
    complete_pending = client.post(
        f"/api/v1/operations/{op_a_id}/complete",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    checks.append(
        Check(
            name="2) Complete when status != IN_PROGRESS",
            passed=claim_a.status_code == 200 and complete_pending.status_code == 409,
            detail=f"claim_status={claim_a.status_code}, complete_status={complete_pending.status_code}",
        )
    )

    # 3) Clock On -> Clock Off -> OP_COMPLETED created and status COMPLETED
    start_a = client.post(
        f"/api/v1/operations/{op_a_id}/start",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    complete_a = client.post(
        f"/api/v1/operations/{op_a_id}/complete",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    with SessionLocal() as db:
        completed_events_after_first = _count_completed_events(db, op_a_id)
    complete_a_status = (
        complete_a.json().get("status") if complete_a.status_code == 200 else "-"
    )
    checks.append(
        Check(
            name="3) Clock On -> Clock Off",
            passed=(
                start_a.status_code == 200
                and complete_a.status_code == 200
                and complete_a_status == "COMPLETED"
                and completed_events_after_first == 1
            ),
            detail=(
                f"start_status={start_a.status_code}, complete_status={complete_a.status_code}, "
                f"operation_status={complete_a_status}, completed_events={completed_events_after_first}"
            ),
        )
    )

    # 4) Double Clock Off -> 409 and no duplicate OP_COMPLETED
    complete_again_a = client.post(
        f"/api/v1/operations/{op_a_id}/complete",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    with SessionLocal() as db:
        completed_events_after_second = _count_completed_events(db, op_a_id)
    checks.append(
        Check(
            name="4) Double Clock Off",
            passed=complete_again_a.status_code == 409
            and completed_events_after_second == 1,
            detail=(
                f"second_complete_status={complete_again_a.status_code}, "
                f"completed_events={completed_events_after_second}"
            ),
        )
    )

    # 5) Clock On OP A -> Clock Off OP A -> Clock On OP B (same station) -> PASS
    claim_b = client.post(
        f"/api/v1/station/queue/{op_b_id}/claim",
        headers=headers,
        json={},
    )
    start_b = client.post(
        f"/api/v1/operations/{op_b_id}/start",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    start_b_status = start_b.json().get("status") if start_b.status_code == 200 else "-"
    checks.append(
        Check(
            name="5) Start OP B after Clock Off OP A",
            passed=claim_b.status_code == 200
            and start_b.status_code == 200
            and start_b_status == "IN_PROGRESS",
            detail=(
                f"claim_b_status={claim_b.status_code}, start_b_status={start_b.status_code}, "
                f"operation_status={start_b_status}"
            ),
        )
    )

    _print_results(checks)

    failed = [c for c in checks if not c.passed]

    with SessionLocal() as db:
        _cleanup(db)

    if failed:
        print(f"\nFAILED: {len(failed)}/{len(checks)} checks")
        raise SystemExit(1)

    print(f"\nAll {len(checks)} checks passed.")


if __name__ == "__main__":
    main()

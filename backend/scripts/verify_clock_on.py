"""
Operator Clock On verification script (StationSession guard version).

Checks:
1) Start without active station session -> 409 STATION_SESSION_REQUIRED
2) Open station session + start -> PASS
3) Start again same OP -> 409
4) Start OP A, then start OP B at same station -> 409
5) Complete OP A, then start OP B -> PASS
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import app
from app.models.execution import ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, RoleScope, Scope, UserRole, UserRoleAssignment
from app.models.station_session import StationSession
from app.models.user import User
from app.security.auth import pwd_context

TENANT_ID = "default"
PASSWORD = "password123"
_SUFFIX = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")

USER_ID = f"verify-clock-opr-{_SUFFIX}"
USERNAME = f"verify_clock_opr_{_SUFFIX}"
PO_NUMBER = f"PH6-CLOCK-PO-{_SUFFIX}"
WO_NUMBER = f"PH6-CLOCK-WO-{_SUFFIX}"
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
        route_id="PH6-CLOCK-R01",
        product_name="Clock On Verify Product",
        quantity=20,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 6, 1, 8, 0, 0),
        planned_end=datetime(2099, 6, 1, 12, 0, 0),
        tenant_id=TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=WO_NUMBER,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 6, 1, 8, 0, 0),
        planned_end=datetime(2099, 6, 1, 12, 0, 0),
        tenant_id=TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op_a = Operation(
        operation_number=f"PH6-CLOCK-OPA-{_SUFFIX}",
        work_order_id=wo.id,
        sequence=10,
        name="Clock On A",
        status=StatusEnum.planned.value,
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
        operation_number=f"PH6-CLOCK-OPB-{_SUFFIX}",
        work_order_id=wo.id,
        sequence=20,
        name="Clock On B",
        status=StatusEnum.planned.value,
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
                Operation.operation_number.like(f"PH6-CLOCK-%-{_SUFFIX}")
            )
        )
    )
    if operation_ids:
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

    db.execute(delete(StationSession).where(StationSession.tenant_id == TENANT_ID, StationSession.station_id == STATION_SCOPE))

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


def _open_station_session(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/station/sessions",
        headers=headers,
        json={"station_id": STATION_SCOPE, "operator_user_id": USER_ID},
    )
    return response.status_code


def _print_results(results: list[Check]) -> None:
    print("\nClock On Verification")
    print("---------------------")
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

    # 1) Start without active station session -> 409
    start_without_session = client.post(
        f"/api/v1/operations/{op_a_id}/start",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    checks.append(
        Check(
            name="1) Start without station session",
            passed=start_without_session.status_code == 409
            and "STATION_SESSION_REQUIRED" in start_without_session.text,
            detail=f"status={start_without_session.status_code}, body={start_without_session.text}",
        )
    )

    session_open_status = _open_station_session(client, headers)

    # 2) Open station session + start -> PASS
    start_a = client.post(
        f"/api/v1/operations/{op_a_id}/start",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    start_a_status = start_a.json().get("status") if start_a.status_code == 200 else "-"
    checks.append(
        Check(
            name="2) Open session + start",
            passed=session_open_status == 200
            and start_a.status_code == 200
            and start_a_status == "IN_PROGRESS",
            detail=(
                f"session_status={session_open_status}, start_status={start_a.status_code}, "
                f"operation_status={start_a_status}"
            ),
        )
    )

    # 3) Start again same OP -> 409
    start_again_a = client.post(
        f"/api/v1/operations/{op_a_id}/start",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    checks.append(
        Check(
            name="3) Start again same OP",
            passed=start_again_a.status_code == 409,
            detail=f"status={start_again_a.status_code}",
        )
    )

    # 4) Start OP A, then start OP B at same station -> 409
    start_b_while_a_running = client.post(
        f"/api/v1/operations/{op_b_id}/start",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    checks.append(
        Check(
            name="4) Start OP A then OP B same station",
            passed=start_b_while_a_running.status_code == 409,
            detail=f"start_status={start_b_while_a_running.status_code}",
        )
    )

    # 5) Complete OP A, then start OP B -> PASS
    complete_a = client.post(
        f"/api/v1/operations/{op_a_id}/complete",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    start_b_after_complete = client.post(
        f"/api/v1/operations/{op_b_id}/start",
        headers=headers,
        json={"operator_id": USER_ID},
    )
    start_b_status = (
        start_b_after_complete.json().get("status")
        if start_b_after_complete.status_code == 200
        else "-"
    )
    checks.append(
        Check(
            name="5) Complete OP A then start OP B",
            passed=complete_a.status_code == 200
            and start_b_after_complete.status_code == 200
            and start_b_status == "IN_PROGRESS",
            detail=(
                f"complete_status={complete_a.status_code}, start_status={start_b_after_complete.status_code}, "
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

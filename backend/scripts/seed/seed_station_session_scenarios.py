#!/usr/bin/env python3
"""
Seed data for Station Session Diagnostic scenarios (dev/manual testing in Docker).

Tạo 4 kịch bản (scenarios) phục vụ kiểm thử thủ công:

  SS-1  Station chưa có session  — 3 operations PLANNED đang chờ ở STATION-SS1
  SS-2  Session đang OPEN        — 1 op IN_PROGRESS, 1 op PLANNED ở STATION-SS2
  SS-3  Session đã CLOSED        — lịch sử session + 1 op PLANNED ở STATION-SS3
  SS-4  Multi-tenant isolation   — Tenant B có session nhưng Tenant A không có,
                                   kiểm tra không bị nhầm lẫn giữa 2 tenant.

Idempotent: mỗi lần chạy sẽ xóa dữ liệu cũ và tạo lại.

Usage:
    cd backend
    .venv\\Scripts\\python scripts/seed/seed_station_session_scenarios.py
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import (
    ClosureStatusEnum,
    Operation,
    ProductionOrder,
    StatusEnum,
    WorkOrder,
)
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_session import StationSession
from app.models.tenant import TENANT_STATUS_ACTIVE, Tenant
from app.models.user import User
from app.schemas.operation import OperationStartRequest
from app.security.dependencies import RequestIdentity
from app.services.operation_service import start_operation
from app.services.station_session_service import (
    close_station_session,
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)
from app.services.user_service import get_or_create_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PREFIX = "SS-DEMO"
_TENANT_A = "default"
_TENANT_B = "tenant-b-demo"

_STATIONS = {
    "SS1": f"{_PREFIX}-STATION-SS1",
    "SS2": f"{_PREFIX}-STATION-SS2",
    "SS3": f"{_PREFIX}-STATION-SS3",
    "SS4A": f"{_PREFIX}-STATION-SS4",
    "SS4B": f"{_PREFIX}-STATION-SS4",  # same station name, different tenant
}

# Tenant A dùng account demo đã có sẵn (opr-001 / operator / password123)
_TENANT_A_OPERATOR_ID = "opr-001"
_TENANT_A_OPERATOR_USERNAME = "operator"

# Tenant B cần user riêng vì user_id là unique toàn hệ thống
_TENANT_B_OPERATOR_ID = "opr-tenantb-001"
_TENANT_B_OPERATOR_USERNAME = "operator-b"
_TENANT_B_OPERATOR_PASSWORD = "password123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _identity(user_id: str, tenant_id: str = _TENANT_A) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username=user_id,
        email=None,
        tenant_id=tenant_id,
        role_code="OPR",
        acting_role_code=None,
        is_authenticated=True,
    )


def _ensure_role(db: Session, code: str, name: str) -> Role:
    role = db.scalar(select(Role).where(Role.code == code))
    if role is None:
        role = Role(code=code, name=name, role_type="system", is_system=True)
        db.add(role)
        db.flush()
    return role


def _ensure_tenant_b_operator(db: Session) -> User:
    """Tạo hoặc lấy user cho Tenant B (không tồn tại trong demo mặc định)."""
    # Đảm bảo Tenant row tồn tại — bắt buộc để login được
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == _TENANT_B))
    if tenant is None:
        tenant = Tenant(
            tenant_id=_TENANT_B,
            tenant_code="TENANT-B",
            tenant_name="Tenant B Demo",
            lifecycle_status=TENANT_STATUS_ACTIVE,
            is_active=True,
        )
        db.add(tenant)
        db.flush()

    user = get_or_create_user(
        db,
        user_id=_TENANT_B_OPERATOR_ID,
        username=_TENANT_B_OPERATOR_USERNAME,
        password=_TENANT_B_OPERATOR_PASSWORD,
        email="operator-b@tenant-b-demo.local",
        tenant_id=_TENANT_B,
    )
    db.flush()
    return user


def _ensure_scope(db: Session, tenant_id: str, station_id: str) -> Scope:
    scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == tenant_id,
            Scope.scope_type == "station",
            Scope.scope_value == station_id,
        )
    )
    if scope is None:
        scope = Scope(
            tenant_id=tenant_id,
            scope_type="station",
            scope_value=station_id,
        )
        db.add(scope)
        db.flush()
    return scope


def _ensure_role_assignment(
    db: Session, user_id: str, role: Role, scope: Scope
) -> None:
    existing = db.scalar(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.role_id == role.id,
            UserRoleAssignment.scope_id == scope.id,
        )
    )
    if existing is None:
        db.add(
            UserRoleAssignment(
                user_id=user_id,
                role_id=role.id,
                scope_id=scope.id,
                is_primary=True,
                is_active=True,
            )
        )
        db.flush()


def _create_operation(
    db: Session,
    *,
    suffix: str,
    station_id: str,
    tenant_id: str,
    sequence: int,
    status: str = StatusEnum.planned.value,
    wo_id: int,
) -> Operation:
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name=f"Demo Operation {suffix}",
        sequence=sequence,
        work_order_id=wo_id,
        tenant_id=tenant_id,
        status=status,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value=station_id,
        quantity=10,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=False,
        planned_start=datetime(2099, 12, 1, min(8 + sequence - 1, 22), 0, 0),
        planned_end=datetime(2099, 12, 1, min(9 + sequence - 1, 23), 0, 0),
    )
    db.add(op)
    db.flush()
    return op


def _create_po_and_wo(
    db: Session,
    *,
    scenario_code: str,
    tenant_id: str,
) -> tuple[ProductionOrder, WorkOrder]:
    po_num = f"{_PREFIX}-PO-{scenario_code}"
    po = db.scalar(select(ProductionOrder).where(ProductionOrder.order_number == po_num))
    if po is None:
        po = ProductionOrder(
            order_number=po_num,
            route_id=f"{_PREFIX}-ROUTE-{scenario_code}",
            product_name=f"Demo Product {scenario_code}",
            quantity=30,
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 12, 1, 6, 0, 0),
            planned_end=datetime(2099, 12, 1, 20, 0, 0),
            tenant_id=tenant_id,
        )
        db.add(po)
        db.flush()

    wo_num = f"{_PREFIX}-WO-{scenario_code}"
    wo = db.scalar(select(WorkOrder).where(WorkOrder.work_order_number == wo_num))
    if wo is None:
        wo = WorkOrder(
            production_order_id=po.id,
            work_order_number=wo_num,
            status=StatusEnum.planned.value,
            tenant_id=tenant_id,
        )
        db.add(wo)
        db.flush()

    return po, wo


# ---------------------------------------------------------------------------
# Purge
# ---------------------------------------------------------------------------


def _purge(db: Session) -> None:
    """Xóa toàn bộ dữ liệu do script này tạo."""
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
            op_ids = list(
                db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids)))
            )
            if op_ids:
                db.execute(
                    delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids))
                )
                db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))

    all_station_ids = list(_STATIONS.values())
    db.execute(
        delete(StationSession).where(
            StationSession.station_id.in_(all_station_ids),
            StationSession.tenant_id.in_([_TENANT_A, _TENANT_B]),
        )
    )

    # Chỉ xóa scope cho các station do script này tạo (không xóa scope của opr-001)
    db.execute(
        delete(UserRoleAssignment).where(
            UserRoleAssignment.user_id == _TENANT_B_OPERATOR_ID
        )
    )
    db.execute(
        delete(Scope).where(
            Scope.scope_value.in_(list(_STATIONS.values())),
            Scope.tenant_id == _TENANT_B,
        )
    )
    # Xóa scope SS-DEMO của Tenant A (không xóa STATION_01 của opr-001)
    db.execute(
        delete(UserRoleAssignment).where(
            UserRoleAssignment.user_id == _TENANT_A_OPERATOR_ID,
            UserRoleAssignment.scope_id.in_(
                select(Scope.id).where(
                    Scope.scope_value.in_(list(_STATIONS.values())),
                    Scope.tenant_id == _TENANT_A,
                )
            ),
        )
    )
    db.execute(
        delete(Scope).where(
            Scope.scope_value.in_(list(_STATIONS.values())),
            Scope.tenant_id == _TENANT_A,
        )
    )
    # Xóa Tenant B user nếu đã tạo
    db.execute(delete(User).where(User.user_id == _TENANT_B_OPERATOR_ID))
    db.commit()
    print("✓ Purged existing SS-DEMO data")


# ---------------------------------------------------------------------------
# Scenario SS-1: Station chưa có session
# ---------------------------------------------------------------------------


def seed_ss1(db: Session) -> None:
    """
    SS-1: No Active Session

    - Station: STATION-SS1  (Tenant A)
    - 3 operations PLANNED đang chờ trong queue
    - Không có StationSession nào → diagnostic = NO_ACTIVE_SESSION
    - Dùng để kiểm tra màn hình station queue khi chưa mở ca
    - Login: username=operator / password=password123
    """
    print("\n=== SS-1: No Active Session ===")
    opr_role = _ensure_role(db, "OPR", "Operator")
    station = _STATIONS["SS1"]
    scope = _ensure_scope(db, _TENANT_A, station)
    _ensure_role_assignment(db, _TENANT_A_OPERATOR_ID, opr_role, scope)

    _, wo = _create_po_and_wo(db, scenario_code="SS1", tenant_id=_TENANT_A)
    for seq in range(1, 4):
        _create_operation(
            db,
            suffix=f"SS1-{seq:02d}",
            station_id=station,
            tenant_id=_TENANT_A,
            sequence=seq,
            wo_id=wo.id,
        )
    db.commit()
    print(f"  Station : {station}")
    print(f"  Tenant  : {_TENANT_A}")
    print("  Ops     : SS1-01, SS1-02, SS1-03  (all PLANNED)")
    print("  Session : none  → diagnostic = NO_ACTIVE_SESSION")
    print("  Login   : username=operator / password=password123")


# ---------------------------------------------------------------------------
# Scenario SS-2: Session đang OPEN
# ---------------------------------------------------------------------------


def seed_ss2(db: Session) -> None:
    """
    SS-2: Open Session with In-Progress Operation

    - Station: STATION-SS2  (Tenant A)
    - Op 1: IN_PROGRESS (operator đang làm)
    - Op 2: PLANNED (chờ tiếp theo)
    - StationSession OPEN → diagnostic = OPEN
    - Login: username=operator / password=password123
    """
    print("\n=== SS-2: Open Session + In-Progress Op ===")
    opr_role = _ensure_role(db, "OPR", "Operator")
    station = _STATIONS["SS2"]
    scope = _ensure_scope(db, _TENANT_A, station)
    _ensure_role_assignment(db, _TENANT_A_OPERATOR_ID, opr_role, scope)

    _, wo = _create_po_and_wo(db, scenario_code="SS2", tenant_id=_TENANT_A)
    op1 = _create_operation(
        db, suffix="SS2-01", station_id=station, tenant_id=_TENANT_A, sequence=10, wo_id=wo.id
    )
    _create_operation(
        db, suffix="SS2-02", station_id=station, tenant_id=_TENANT_A, sequence=20, wo_id=wo.id
    )
    db.commit()

    identity = _identity(_TENANT_A_OPERATOR_ID)
    session = get_current_station_session(db, identity, station_id=station)
    if session is None:
        session = open_station_session(db, identity, station_id=station)
    if session.operator_user_id != _TENANT_A_OPERATOR_ID:
        session = identify_operator_at_station(
            db, identity, session_id=session.session_id, operator_user_id=_TENANT_A_OPERATOR_ID
        )

    # Start op 1
    from app.repositories.operation_repository import get_operation_by_id
    op1_loaded = get_operation_by_id(db, op1.id)
    assert op1_loaded is not None
    start_operation(
        db,
        op1_loaded,
        OperationStartRequest(operator_id=_TENANT_A_OPERATOR_ID),
        tenant_id=_TENANT_A,
    )

    print(f"  Station : {station}")
    print(f"  Tenant  : {_TENANT_A}")
    print(f"  Op SS2-01: IN_PROGRESS (operator: {_TENANT_A_OPERATOR_ID})")
    print("  Op SS2-02: PLANNED")
    print("  Session : OPEN  → diagnostic = OPEN")
    print("  Login   : username=operator / password=password123")


# ---------------------------------------------------------------------------
# Scenario SS-3: Session đã CLOSED (lịch sử)
# ---------------------------------------------------------------------------


def seed_ss3(db: Session) -> None:
    """
    SS-3: Closed Session (Historical)

    - Station: STATION-SS3  (Tenant A)
    - 1 op PLANNED chờ tiếp
    - StationSession đã CLOSED → diagnostic = NO_ACTIVE_SESSION
    - Dùng kiểm tra guard khi ca trước đã đóng, ca mới chưa mở
    - Login: username=operator / password=password123
    """
    print("\n=== SS-3: Closed Session ===")
    opr_role = _ensure_role(db, "OPR", "Operator")
    station = _STATIONS["SS3"]
    scope = _ensure_scope(db, _TENANT_A, station)
    _ensure_role_assignment(db, _TENANT_A_OPERATOR_ID, opr_role, scope)

    _, wo = _create_po_and_wo(db, scenario_code="SS3", tenant_id=_TENANT_A)
    _create_operation(
        db, suffix="SS3-01", station_id=station, tenant_id=_TENANT_A, sequence=10, wo_id=wo.id
    )
    db.commit()

    identity = _identity(_TENANT_A_OPERATOR_ID)
    session = get_current_station_session(db, identity, station_id=station)
    if session is None:
        session = open_station_session(db, identity, station_id=station)

    close_station_session(db, identity, session_id=session.session_id)

    print(f"  Station : {station}")
    print(f"  Tenant  : {_TENANT_A}")
    print("  Op SS3-01: PLANNED")
    print("  Session : CLOSED  → diagnostic = NO_ACTIVE_SESSION")
    print(f"  Session ID: {session.session_id}")
    print("  Login   : username=operator / password=password123")


# ---------------------------------------------------------------------------
# Scenario SS-4: Multi-tenant isolation
# ---------------------------------------------------------------------------


def seed_ss4(db: Session) -> None:
    """
    SS-4: Multi-Tenant Isolation

    - Cùng station_id nhưng 2 tenant khác nhau:
      - Tenant A: STATION-SS4 — KHÔNG có session → diagnostic = NO_ACTIVE_SESSION
        Login: username=operator / password=password123  (tenant=default)
      - Tenant B: STATION-SS4 — CÓ session OPEN  → diagnostic = OPEN
        Login: username=operator-b / password=password123  (tenant=tenant-b-demo)
    - Kiểm tra guard không bị nhầm cross-tenant
    """
    print("\n=== SS-4: Multi-Tenant Isolation ===")
    opr_role = _ensure_role(db, "OPR", "Operator")
    station = _STATIONS["SS4A"]  # same value for both tenants

    # Tenant A: scope + user but NO session
    scope_a = _ensure_scope(db, _TENANT_A, station)
    _ensure_role_assignment(db, _TENANT_A_OPERATOR_ID, opr_role, scope_a)
    _, wo_a = _create_po_and_wo(db, scenario_code="SS4A", tenant_id=_TENANT_A)
    _create_operation(
        db, suffix="SS4A-01", station_id=station, tenant_id=_TENANT_A, sequence=10, wo_id=wo_a.id
    )
    db.commit()

    # Tenant B: tạo user mới vì không có demo account cho tenant này
    _ensure_tenant_b_operator(db)
    scope_b = _ensure_scope(db, _TENANT_B, station)
    _ensure_role_assignment(db, _TENANT_B_OPERATOR_ID, opr_role, scope_b)
    _, wo_b = _create_po_and_wo(db, scenario_code="SS4B", tenant_id=_TENANT_B)
    _create_operation(
        db, suffix="SS4B-01", station_id=station, tenant_id=_TENANT_B, sequence=10, wo_id=wo_b.id
    )
    db.commit()

    identity_b = _identity(_TENANT_B_OPERATOR_ID, tenant_id=_TENANT_B)
    session_b = get_current_station_session(db, identity_b, station_id=station)
    if session_b is None:
        session_b = open_station_session(db, identity_b, station_id=station)
    if session_b.operator_user_id != _TENANT_B_OPERATOR_ID:
        session_b = identify_operator_at_station(
            db, identity_b, session_id=session_b.session_id, operator_user_id=_TENANT_B_OPERATOR_ID
        )

    print(f"  Station : {station}")
    print(f"  Tenant A ({_TENANT_A}): op SS4A-01 PLANNED, NO session  → NO_ACTIVE_SESSION")
    print(f"  Tenant B ({_TENANT_B}): op SS4B-01 PLANNED, session OPEN → OPEN")
    print(f"  Session B ID: {session_b.session_id}")
    print("  Login A : username=operator       / password=password123  (tenant=default)")
    print("  Login B : username=operator-b     / password=password123  (tenant=tenant-b-demo)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        _purge(db)
        seed_ss1(db)
        seed_ss2(db)
        seed_ss3(db)
        seed_ss4(db)
        db.commit()
        print("\n=== Seed hoàn tất ===")
        print(f"  Prefix  : {_PREFIX}")
        print(f"  Tenant A: {_TENANT_A}")
        print(f"  Tenant B: {_TENANT_B}")
        print("\nKịch bản + account đăng nhập:")
        print("  SS-1  STATION-SS1  No session    — 3 ops PLANNED")
        print("         → username=operator / password=password123")
        print("  SS-2  STATION-SS2  Session OPEN  — op IN_PROGRESS + op PLANNED")
        print("         → username=operator / password=password123")
        print("  SS-3  STATION-SS3  Session CLOSED — 1 op PLANNED")
        print("         → username=operator / password=password123")
        print("  SS-4  STATION-SS4  Tenant isolation — B OPEN / A no session")
        print("         → Tenant A: username=operator   / password=password123")
        print("         → Tenant B: username=operator-b / password=password123")
    finally:
        db.close()


if __name__ == "__main__":
    main()

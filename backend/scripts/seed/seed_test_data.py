#!/usr/bin/env python3
"""
Seed test data for manual testing in Docker environment.
Data is PERSISTED in Docker database for interactive exploration.

Usage:
  cd backend
    .venv\\Scripts\\python scripts/seed/seed_test_data.py

Database: localhost:5432/mes (Docker postgres_data volume)
"""

from datetime import datetime
from sqlalchemy import select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.master import (
    Operation,
    ProductionOrder,
    StatusEnum,
    WorkOrder,
)
from app.models.rbac import Role, Scope, UserRoleAssignment


TENANT_ID = "default"


def _ensure_roles(db):
    """Ensure OPR, SUP roles exist."""
    for code, name in [("OPR", "Operator"), ("SUP", "Supervisor")]:
        role = db.scalar(select(Role).where(Role.code == code))
        if not role:
            role = Role(code=code, name=name, role_type="system", is_system=True)
            db.add(role)
            print(f"✓ Created role: {code}")
    db.flush()


def _create_or_get_scope(db, scope_value: str) -> Scope:
    """Create or get a station scope."""
    scope = db.scalar(
        select(Scope).where(
            Scope.scope_value == scope_value, Scope.tenant_id == TENANT_ID
        )
    )
    if scope:
        return scope

    scope = Scope(
        tenant_id=TENANT_ID,
        scope_type="station",
        scope_value=scope_value,
    )
    db.add(scope)
    db.flush()
    print(f"✓ Created scope: {scope_value}")
    return scope


def _create_or_get_user_role(db, user_id: str, username: str, role_code: str, scope: Scope):
    """Create user role assignment."""
    role = db.scalar(select(Role).where(Role.code == role_code))
    if not role:
        raise ValueError(f"Role {role_code} not found")

    existing = db.scalar(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.role_id == role.id,
            UserRoleAssignment.scope_id == scope.id,
        )
    )
    if existing:
        return existing

    assignment = UserRoleAssignment(
        user_id=user_id,
        role_id=role.id,
        scope_id=scope.id,
        is_primary=True,
        is_active=True,
    )
    db.add(assignment)
    db.flush()
    print(f"✓ Created role assignment: {username} ({role_code}) → {scope.scope_value}")
    return assignment


def seed_test_dataset_1():
    """
    Scenario 1: Simple station queue with 3 operations (no execution).

    Structure:
    - ProductionOrder: TEST-DEMO-S1-PO
      - WorkOrder: TEST-DEMO-S1-WO
        - Operation 1: TEST-DEMO-S1-OP-001 (PLANNED)
        - Operation 2: TEST-DEMO-S1-OP-002 (PLANNED)
        - Operation 3: TEST-DEMO-S1-OP-003 (PLANNED)
    - Users: alice (OPR), bob (OPR) @ STATION-A
    """
    db = SessionLocal()
    try:
        print("\n=== SCENARIO 1: Station Queue (3 Operations) ===")

        init_db()
        _ensure_roles(db)

        # Create scope
        scope_a = _create_or_get_scope(db, "STATION-A")

        # Create users
        _create_or_get_user_role(db, "alice", "alice", "OPR", scope_a)
        _create_or_get_user_role(db, "bob", "bob", "OPR", scope_a)

        # Create production order
        po = db.scalar(
            select(ProductionOrder).where(
                ProductionOrder.order_number == "TEST-DEMO-S1-PO"
            )
        )
        if not po:
            po = ProductionOrder(
                order_number="TEST-DEMO-S1-PO",
                route_id="TEST-DEMO-S1-ROUTE",
                product_name="Test Product S1",
                quantity=100,
                status=StatusEnum.planned.value,
                planned_start=datetime(2099, 6, 1, 8, 0, 0),
                planned_end=datetime(2099, 6, 1, 17, 0, 0),
                tenant_id=TENANT_ID,
            )
            db.add(po)
            db.flush()
            print(f"✓ Created ProductionOrder: {po.order_number}")

        # Create work order
        wo = db.scalar(
            select(WorkOrder).where(
                WorkOrder.work_order_number == "TEST-DEMO-S1-WO"
            )
        )
        if not wo:
            wo = WorkOrder(
                production_order_id=po.id,
                work_order_number="TEST-DEMO-S1-WO",
                status=StatusEnum.planned.value,
                planned_start=datetime(2099, 6, 1, 8, 0, 0),
                planned_end=datetime(2099, 6, 1, 17, 0, 0),
                tenant_id=TENANT_ID,
            )
            db.add(wo)
            db.flush()
            print(f"✓ Created WorkOrder: {wo.work_order_number}")

        # Create 3 operations
        for i in range(1, 4):
            op_num = f"TEST-DEMO-S1-OP-{i:03d}"
            existing = db.scalar(
                select(Operation).where(Operation.operation_number == op_num)
            )
            if not existing:
                op = Operation(
                    operation_number=op_num,
                    work_order_id=wo.id,
                    sequence=i,
                    name=f"Test Operation {i}",
                    status=StatusEnum.planned.value,
                    planned_start=datetime(2099, 6, 1, 8 + i, 0, 0),
                    planned_end=datetime(2099, 6, 1, 9 + i, 0, 0),
                    quantity=10,
                    completed_qty=0,
                    good_qty=0,
                    scrap_qty=0,
                    qc_required=False,
                    station_scope_value="STATION-A",
                    tenant_id=TENANT_ID,
                )
                db.add(op)
                db.flush()
                print(f"✓ Created Operation: {op_num}")

        db.commit()
        print("✓ Committed all changes\n")

    finally:
        db.close()


def seed_test_dataset_2():
    """
    Scenario 2: Operation in progress with claim.

    Structure:
    - ProductionOrder: TEST-DEMO-S2-PO
      - WorkOrder: TEST-DEMO-S2-WO
        - Operation 1: TEST-DEMO-S2-OP-001 (IN_PROGRESS) + claim by alice
        - Operation 2: TEST-DEMO-S2-OP-002 (PLANNED)
    - Users: alice (OPR), supervisor (SUP) @ STATION-B
    """
    db = SessionLocal()
    try:
        print("=== SCENARIO 2: Operation In-Progress with Claim ===")

        init_db()
        _ensure_roles(db)

        # Create scope
        scope_b = _create_or_get_scope(db, "STATION-B")

        # Create users
        _create_or_get_user_role(db, "alice-b", "alice-b", "OPR", scope_b)
        _create_or_get_user_role(db, "supervisor", "supervisor", "SUP", scope_b)

        # Create production order
        po = db.scalar(
            select(ProductionOrder).where(
                ProductionOrder.order_number == "TEST-DEMO-S2-PO"
            )
        )
        if not po:
            po = ProductionOrder(
                order_number="TEST-DEMO-S2-PO",
                route_id="TEST-DEMO-S2-ROUTE",
                product_name="Test Product S2",
                quantity=50,
                status=StatusEnum.in_progress.value,
                planned_start=datetime(2099, 6, 2, 8, 0, 0),
                planned_end=datetime(2099, 6, 2, 17, 0, 0),
                tenant_id=TENANT_ID,
            )
            db.add(po)
            db.flush()
            print(f"✓ Created ProductionOrder: {po.order_number}")

        # Create work order
        wo = db.scalar(
            select(WorkOrder).where(
                WorkOrder.work_order_number == "TEST-DEMO-S2-WO"
            )
        )
        if not wo:
            wo = WorkOrder(
                production_order_id=po.id,
                work_order_number="TEST-DEMO-S2-WO",
                status=StatusEnum.in_progress.value,
                planned_start=datetime(2099, 6, 2, 8, 0, 0),
                planned_end=datetime(2099, 6, 2, 17, 0, 0),
                tenant_id=TENANT_ID,
            )
            db.add(wo)
            db.flush()
            print(f"✓ Created WorkOrder: {wo.work_order_number}")

        # Create 2 operations
        for i in range(1, 3):
            op_num = f"TEST-DEMO-S2-OP-{i:03d}"
            existing = db.scalar(
                select(Operation).where(Operation.operation_number == op_num)
            )
            if not existing:
                status = StatusEnum.in_progress.value if i == 1 else StatusEnum.planned.value
                op = Operation(
                    operation_number=op_num,
                    work_order_id=wo.id,
                    sequence=i,
                    name=f"Test Operation S2-{i}",
                    status=status,
                    planned_start=datetime(2099, 6, 2, 8 + i, 0, 0),
                    planned_end=datetime(2099, 6, 2, 10 + i, 0, 0),
                    quantity=25,
                    completed_qty=5 if i == 1 else 0,
                    good_qty=5 if i == 1 else 0,
                    scrap_qty=0,
                    qc_required=False,
                    station_scope_value="STATION-B",
                    tenant_id=TENANT_ID,
                )
                db.add(op)
                db.flush()
                print(f"✓ Created Operation: {op_num} ({status})")

        db.commit()
        print("✓ Committed all changes\n")

    finally:
        db.close()


def seed_test_dataset_3():
    """
    Scenario 3: Cross-station operations (multi-station).

    Structure:
    - ProductionOrder: TEST-DEMO-S3-PO
      - WorkOrder: TEST-DEMO-S3-WO
        - Operation 1: @ STATION-A (PLANNED)
        - Operation 2: @ STATION-B (PLANNED)
        - Operation 3: @ STATION-C (PLANNED)
    - Multiple users per station
    """
    db = SessionLocal()
    try:
        print("=== SCENARIO 3: Cross-Station Operations ===")

        init_db()
        _ensure_roles(db)

        # Create scopes
        scope_a = _create_or_get_scope(db, "STATION-A")
        scope_b = _create_or_get_scope(db, "STATION-B")
        scope_c = _create_or_get_scope(db, "STATION-C")

        # Create users for each station
        for station, scope in [("A", scope_a), ("B", scope_b), ("C", scope_c)]:
            _create_or_get_user_role(
                db, f"operator-{station}", f"operator-{station}", "OPR", scope
            )

        # Create production order
        po = db.scalar(
            select(ProductionOrder).where(
                ProductionOrder.order_number == "TEST-DEMO-S3-PO"
            )
        )
        if not po:
            po = ProductionOrder(
                order_number="TEST-DEMO-S3-PO",
                route_id="TEST-DEMO-S3-ROUTE",
                product_name="Test Product S3 (Multi-Station)",
                quantity=75,
                status=StatusEnum.planned.value,
                planned_start=datetime(2099, 6, 3, 8, 0, 0),
                planned_end=datetime(2099, 6, 3, 17, 0, 0),
                tenant_id=TENANT_ID,
            )
            db.add(po)
            db.flush()
            print(f"✓ Created ProductionOrder: {po.order_number}")

        # Create work order
        wo = db.scalar(
            select(WorkOrder).where(
                WorkOrder.work_order_number == "TEST-DEMO-S3-WO"
            )
        )
        if not wo:
            wo = WorkOrder(
                production_order_id=po.id,
                work_order_number="TEST-DEMO-S3-WO",
                status=StatusEnum.planned.value,
                planned_start=datetime(2099, 6, 3, 8, 0, 0),
                planned_end=datetime(2099, 6, 3, 17, 0, 0),
                tenant_id=TENANT_ID,
            )
            db.add(wo)
            db.flush()
            print(f"✓ Created WorkOrder: {wo.work_order_number}")

        # Create 3 operations across stations
        stations = ["STATION-A", "STATION-B", "STATION-C"]
        for i in range(1, 4):
            op_num = f"TEST-DEMO-S3-OP-{i:03d}"
            existing = db.scalar(
                select(Operation).where(Operation.operation_number == op_num)
            )
            if not existing:
                op = Operation(
                    operation_number=op_num,
                    work_order_id=wo.id,
                    sequence=i,
                    name=f"Test Operation S3-{i}",
                    status=StatusEnum.planned.value,
                    planned_start=datetime(2099, 6, 3, 8 + i, 0, 0),
                    planned_end=datetime(2099, 6, 3, 10 + i, 0, 0),
                    quantity=25,
                    completed_qty=0,
                    good_qty=0,
                    scrap_qty=0,
                    qc_required=False,
                    station_scope_value=stations[i - 1],
                    tenant_id=TENANT_ID,
                )
                db.add(op)
                db.flush()
                print(f"✓ Created Operation: {op_num} @ {stations[i-1]}")

        db.commit()
        print("✓ Committed all changes\n")

    finally:
        db.close()


def main():
    """Run all seed scenarios."""
    print("\n" + "=" * 60)
    print("SEED TEST DATA FOR DOCKER DATABASE")
    print("=" * 60)

    seed_test_dataset_1()
    seed_test_dataset_2()
    seed_test_dataset_3()

    print("=" * 60)
    print("✓ ALL SCENARIOS SEEDED SUCCESSFULLY")
    print("=" * 60)
    print("\nDatabase: localhost:5432/mes (Docker postgres_data volume)")
    print("\nData Summary:")
    print("- Scenario 1: 3 operations in queue @ STATION-A")
    print("- Scenario 2: 2 operations (1 in-progress) @ STATION-B")
    print("- Scenario 3: 3 operations across 3 stations (A, B, C)")
    print("\nTo explore:")
    print("  psql -h localhost -U mes -d mes -W")
    print("  password: mes")
    print("\nOr use UI:")
    print("  http://localhost    (Frontend)")
    print("  http://localhost:8010/docs (Backend API docs)")
    print()


if __name__ == "__main__":
    main()

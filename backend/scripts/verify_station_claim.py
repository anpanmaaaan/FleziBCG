"""
Station Execution v2 verification script.

Checks:
- Queue endpoint returns operations for OPR with station scope.
- OPR without station scope gets 400 on queue.
- Execution actions require active claim by caller.
- Claim conflict/release behavior works as expected.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from sqlalchemy import update

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import app
from app.models.rbac import Role, RoleScope, Scope, UserRole, UserRoleAssignment
from app.models.station_claim import OperationClaim
from app.models.user import User
from app.security.auth import pwd_context

TENANT_ID = "default"
PASSWORD = "password123"
_SUFFIX = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
OPR_A_USER_ID = f"verify-opr-a-{_SUFFIX}"
OPR_A_USERNAME = f"verify_opr_a_{_SUFFIX}"
OPR_B_USER_ID = f"verify-opr-b-{_SUFFIX}"
OPR_B_USERNAME = f"verify_opr_b_{_SUFFIX}"
OPR_NO_SCOPE_USER_ID = f"verify-opr-noscope-{_SUFFIX}"
OPR_NO_SCOPE_USERNAME = f"verify_opr_noscope_{_SUFFIX}"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _create_user(db, *, user_id: str, username: str) -> None:
    db.add(
        User(
            user_id=user_id,
            username=username,
            email=f"{username}@example.com",
            password_hash=pwd_context.hash(PASSWORD),
            tenant_id=TENANT_ID,
            is_active=True,
        )
    )


def _ensure_station_scope(db) -> Scope:
    station_scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == TENANT_ID,
            Scope.scope_type == "station",
            Scope.scope_value == "STATION_01",
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
        scope_value="STATION_01",
        parent_scope_id=line_scope.id,
    )
    db.add(station_scope)
    db.flush()
    return station_scope


def _create_opr_fixture_user(db, *, user_id: str, username: str, with_station_scope: bool) -> None:
    role = db.scalar(select(Role).where(Role.code == "OPR"))
    if role is None:
        raise RuntimeError("Role OPR not found")

    _create_user(db, user_id=user_id, username=username)

    user_role = UserRole(
        user_id=user_id,
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

    if with_station_scope:
        station_scope = _ensure_station_scope(db)
        db.add(
            UserRoleAssignment(
                user_id=user_id,
                role_id=role.id,
                scope_id=station_scope.id,
                is_primary=True,
                is_active=True,
            )
        )


def _cleanup(db) -> None:
    ids = [OPR_A_USER_ID, OPR_B_USER_ID, OPR_NO_SCOPE_USER_ID]

    # Release orphaned operation claims from current and prior test runs
    db.execute(
        update(OperationClaim)
        .where(
            OperationClaim.claimed_by_user_id.like("verify-opr-%"),
            OperationClaim.released_at.is_(None),
        )
        .values(released_at=datetime.now(timezone.utc), release_reason="verify_cleanup")
    )

    db.execute(delete(UserRoleAssignment).where(UserRoleAssignment.user_id.in_(ids)))

    user_roles = list(db.scalars(select(UserRole).where(UserRole.user_id.in_(ids))))
    if user_roles:
        ur_ids = [item.id for item in user_roles]
        db.execute(delete(RoleScope).where(RoleScope.user_role_id.in_(ur_ids)))

    db.execute(delete(UserRole).where(UserRole.user_id.in_(ids)))
    db.execute(delete(User).where(User.user_id.in_(ids)))

    # Also clean up user records from prior runs (different timestamp suffixes)
    db.execute(
        delete(User).where(
            User.user_id.like("verify-opr-%"),
            User.tenant_id == TENANT_ID,
        )
    )
    db.commit()


def _login(client: TestClient, username: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Login failed for {username}: {response.status_code} {response.text}")
    body = response.json()
    return body["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID,
    }


def _print_results(results: list[Check]) -> None:
    print("\nStation Claim Verification")
    print("--------------------------")
    for check in results:
        state = "PASS" if check.passed else "FAIL"
        print(f"[{state}] {check.name}: {check.detail}")


def main() -> None:
    init_db()

    with SessionLocal() as db:
        _cleanup(db)
        _create_opr_fixture_user(db, user_id=OPR_A_USER_ID, username=OPR_A_USERNAME, with_station_scope=True)
        _create_opr_fixture_user(db, user_id=OPR_B_USER_ID, username=OPR_B_USERNAME, with_station_scope=True)
        _create_opr_fixture_user(
            db,
            user_id=OPR_NO_SCOPE_USER_ID,
            username=OPR_NO_SCOPE_USERNAME,
            with_station_scope=False,
        )
        db.commit()

    client = TestClient(app)

    token_a = _login(client, OPR_A_USERNAME)
    token_b = _login(client, OPR_B_USERNAME)
    token_no_scope = _login(client, OPR_NO_SCOPE_USERNAME)

    checks: list[Check] = []

    queue_a = client.get("/api/v1/station/queue", headers=_auth_headers(token_a))
    queue_items = []
    if queue_a.status_code == 200:
        queue_items = queue_a.json().get("items", [])
    checks.append(
        Check(
            name="Queue for OPR with station scope",
            passed=queue_a.status_code == 200 and len(queue_items) >= 1,
            detail=f"status={queue_a.status_code}, items={len(queue_items)}",
        )
    )

    queue_no_scope = client.get("/api/v1/station/queue", headers=_auth_headers(token_no_scope))
    checks.append(
        Check(
            name="Queue rejects OPR without station scope",
            passed=queue_no_scope.status_code == 400 and "No station scope assigned" in queue_no_scope.text,
            detail=f"status={queue_no_scope.status_code}, body={queue_no_scope.text}",
        )
    )

    if not queue_items:
        _print_results(checks)
        raise SystemExit(1)

    # Pick an unclaimed operation to avoid conflicts with non-test claims
    target_operation_id = None
    for item in queue_items:
        claim_state = (item.get("claim") or {}).get("state", "none")
        if claim_state == "none":
            target_operation_id = int(item["operation_id"])
            break

    if target_operation_id is None:
        target_operation_id = int(queue_items[0]["operation_id"])

    start_without_claim = client.post(
        f"/api/v1/operations/{target_operation_id}/start",
        headers=_auth_headers(token_a),
        json={"operator_id": None},
    )
    checks.append(
        Check(
            name="Execution start blocked without claim",
            passed=start_without_claim.status_code == 403
            and "Operation must be claimed by you before execution actions." in start_without_claim.text,
            detail=f"status={start_without_claim.status_code}, body={start_without_claim.text}",
        )
    )

    claim_a = client.post(
        f"/api/v1/station/queue/{target_operation_id}/claim",
        headers=_auth_headers(token_a),
        json={},
    )
    checks.append(
        Check(
            name="Operator A can claim",
            passed=claim_a.status_code == 200,
            detail=f"status={claim_a.status_code}",
        )
    )

    start_with_claim = client.post(
        f"/api/v1/operations/{target_operation_id}/start",
        headers=_auth_headers(token_a),
        json={"operator_id": None},
    )
    checks.append(
        Check(
            name="Execution start allowed with own claim",
            passed=start_with_claim.status_code != 403,
            detail=f"status={start_with_claim.status_code}, body={start_with_claim.text}",
        )
    )

    claim_b_conflict = client.post(
        f"/api/v1/station/queue/{target_operation_id}/claim",
        headers=_auth_headers(token_b),
        json={},
    )
    checks.append(
        Check(
            name="Claim conflict for second operator",
            passed=claim_b_conflict.status_code == 409,
            detail=f"status={claim_b_conflict.status_code}, body={claim_b_conflict.text}",
        )
    )

    release_a = client.post(
        f"/api/v1/station/queue/{target_operation_id}/release",
        headers=_auth_headers(token_a),
        json={"reason": "verify_release"},
    )
    checks.append(
        Check(
            name="Operator A can release",
            passed=release_a.status_code == 200,
            detail=f"status={release_a.status_code}",
        )
    )

    claim_b_after_release = client.post(
        f"/api/v1/station/queue/{target_operation_id}/claim",
        headers=_auth_headers(token_b),
        json={},
    )
    checks.append(
        Check(
            name="Operator B can claim after release",
            passed=claim_b_after_release.status_code == 200,
            detail=f"status={claim_b_after_release.status_code}",
        )
    )

    _print_results(checks)

    failures = [c for c in checks if not c.passed]
    if failures:
        raise SystemExit(1)

    print("\nAll station claim checks passed.")


if __name__ == "__main__":
    main()

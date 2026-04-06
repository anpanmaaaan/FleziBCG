"""
Station Queue + Mandatory Claim verification.

Checks end-to-end behavior expected by frontend:
1) Queue returns claim summary for OPR.
2) Claim/release updates are reflected immediately in queue projection.
3) Claim conflict is enforced.
4) Execution write actions enforce mandatory claim ownership.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import app
from app.models.rbac import Role, RoleScope, Scope, UserRole, UserRoleAssignment
from app.models.user import User
from app.security.auth import pwd_context
from scripts.seed.seed_station_execution_opr import seed_station_execution_for_opr

TENANT_ID = "default"
PASSWORD = "password123"
OPERATOR_A_USERNAME = "operator"
OPERATOR_A_USER_ID = "opr-001"
OPERATOR_B_USERNAME = "operator2"
OPERATOR_B_USER_ID = "opr-002"


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


def _login(client: TestClient, username: str, password: str = PASSWORD) -> tuple[str, dict]:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Login failed for {username}: {response.status_code} {response.text}")

    body = response.json()
    return body["access_token"], body["user"]


def _ensure_operator_b_with_same_station_scope_as_a() -> None:
    with SessionLocal() as db:
        # Operator A and its station scope assignment are expected in demo seed.
        operator_a = db.scalar(
            select(User).where(
                User.user_id == OPERATOR_A_USER_ID,
                User.tenant_id == TENANT_ID,
            )
        )
        if operator_a is None:
            raise RuntimeError("Missing operator A user opr-001. Run init/seed first.")

        assignment_a = db.scalar(
            select(UserRoleAssignment)
            .join(Role, Role.id == UserRoleAssignment.role_id)
            .join(Scope, Scope.id == UserRoleAssignment.scope_id)
            .where(
                UserRoleAssignment.user_id == OPERATOR_A_USER_ID,
                UserRoleAssignment.is_active.is_(True),
                Role.code == "OPR",
                Scope.tenant_id == TENANT_ID,
                Scope.scope_type == "station",
            )
            .order_by(UserRoleAssignment.is_primary.desc(), UserRoleAssignment.id.asc())
        )
        if assignment_a is None:
            raise RuntimeError("Operator A has no active OPR station scope assignment.")

        opr_role = db.scalar(select(Role).where(Role.code == "OPR"))
        if opr_role is None:
            raise RuntimeError("Role OPR not found")

        operator_b = db.scalar(
            select(User).where(
                User.user_id == OPERATOR_B_USER_ID,
                User.tenant_id == TENANT_ID,
            )
        )

        # Prevent username collision on another user id.
        username_owner = db.scalar(
            select(User).where(
                User.username == OPERATOR_B_USERNAME,
                User.tenant_id == TENANT_ID,
            )
        )
        if username_owner is not None and username_owner.user_id != OPERATOR_B_USER_ID:
            raise RuntimeError(
                f"Username '{OPERATOR_B_USERNAME}' already belongs to user_id={username_owner.user_id}."
            )

        if operator_b is None:
            operator_b = User(
                user_id=OPERATOR_B_USER_ID,
                username=OPERATOR_B_USERNAME,
                email="operator2@example.com",
                password_hash=pwd_context.hash(PASSWORD),
                tenant_id=TENANT_ID,
                is_active=True,
            )
            db.add(operator_b)
            db.flush()

        user_role = db.scalar(
            select(UserRole).where(
                UserRole.user_id == OPERATOR_B_USER_ID,
                UserRole.role_id == opr_role.id,
                UserRole.tenant_id == TENANT_ID,
            )
        )
        if user_role is None:
            user_role = UserRole(
                user_id=OPERATOR_B_USER_ID,
                role_id=opr_role.id,
                tenant_id=TENANT_ID,
                is_active=True,
            )
            db.add(user_role)
            db.flush()

        tenant_scope_link = db.scalar(
            select(RoleScope).where(
                RoleScope.user_role_id == user_role.id,
                RoleScope.scope_type == "tenant",
                RoleScope.scope_value == TENANT_ID,
            )
        )
        if tenant_scope_link is None:
            db.add(
                RoleScope(
                    user_role_id=user_role.id,
                    scope_type="tenant",
                    scope_value=TENANT_ID,
                )
            )

        assignment_b = db.scalar(
            select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == OPERATOR_B_USER_ID,
                UserRoleAssignment.role_id == assignment_a.role_id,
                UserRoleAssignment.scope_id == assignment_a.scope_id,
            )
        )
        if assignment_b is None:
            db.add(
                UserRoleAssignment(
                    user_id=OPERATOR_B_USER_ID,
                    role_id=assignment_a.role_id,
                    scope_id=assignment_a.scope_id,
                    is_primary=True,
                    is_active=True,
                )
            )

        db.commit()


def _get_queue_items(client: TestClient, token: str) -> list[dict]:
    response = client.get("/api/v1/station/queue", headers=_auth_headers(token))
    if response.status_code != 200:
        raise RuntimeError(f"Queue request failed: {response.status_code} {response.text}")
    return response.json().get("items", [])


def _find_item(items: list[dict], operation_id: int) -> dict:
    for item in items:
        raw_operation_id = item.get("operation_id")
        if raw_operation_id is None:
            continue

        item_operation_id_text = str(raw_operation_id).strip()
        if not item_operation_id_text.isdigit():
            continue

        if int(item_operation_id_text) == operation_id:
            return item
    raise RuntimeError(f"Operation {operation_id} not found in station queue")


def _print_results(results: list[Check]) -> None:
    print("\nStation Queue + Mandatory Claim Verification")
    print("--------------------------------------------")
    for check in results:
        state = "PASS" if check.passed else "FAIL"
        print(f"[{state}] {check.name}: {check.detail}")


def main() -> None:
    init_db()
    _ensure_operator_b_with_same_station_scope_as_a()

    client = TestClient(app)
    checks: list[Check] = []

    # 1) Login operator A
    token_a, user_a = _login(client, OPERATOR_A_USERNAME)
    operator_a_user_id = user_a["user_id"]
    checks.append(
        Check(
            name="Step 1 - Login operator A",
            passed=operator_a_user_id == OPERATOR_A_USER_ID,
            detail=f"status=200, user_id={operator_a_user_id}",
        )
    )

    # 2) Queue and pick operation
    queue_resp = client.get("/api/v1/station/queue", headers=_auth_headers(token_a))
    queue_items = queue_resp.json().get("items", []) if queue_resp.status_code == 200 else []

    # Ensure deterministic queue test data exists if environment has none.
    if queue_resp.status_code == 200 and len(queue_items) == 0:
        seed_station_execution_for_opr()
        token_a, user_a = _login(client, OPERATOR_A_USERNAME)
        queue_resp = client.get("/api/v1/station/queue", headers=_auth_headers(token_a))
        queue_items = queue_resp.json().get("items", []) if queue_resp.status_code == 200 else []

    has_items = queue_resp.status_code == 200 and len(queue_items) > 0
    checks.append(
        Check(
            name="Step 2 - Queue returns items",
            passed=has_items,
            detail=f"status={queue_resp.status_code}, items={len(queue_items)}",
        )
    )

    if not has_items:
        _print_results(checks)
        raise SystemExit(1)

    target_item = next(
        (
            item
            for item in queue_items
            if str(item.get("claim", {}).get("state")) in {"none", "mine"}
        ),
        None,
    )
    if target_item is None:
        seed_station_execution_for_opr()
        token_a, user_a = _login(client, OPERATOR_A_USERNAME)
        queue_resp = client.get("/api/v1/station/queue", headers=_auth_headers(token_a))
        queue_items = queue_resp.json().get("items", []) if queue_resp.status_code == 200 else []
        target_item = next(
            (
                item
                for item in queue_items
                if str(item.get("claim", {}).get("state")) in {"none", "mine"}
            ),
            None,
        )

    if target_item is None:
        checks.append(
            Check(
                name="Step 2b - Initial claim state shape",
                passed=False,
                detail="No claimable queue item found (all items are claimed by other operators).",
            )
        )
        _print_results(checks)
        raise SystemExit(1)

    op_id = int(target_item["operation_id"])
    initial_claim_state = str(target_item.get("claim", {}).get("state"))
    checks.append(
        Check(
            name="Step 2b - Initial claim state shape",
            passed=initial_claim_state in {"none", "mine"},
            detail=f"operation_id={op_id}, claim.state={initial_claim_state}",
        )
    )

    # Normalize to no claim owner for deterministic next checks.
    if initial_claim_state == "mine":
        rel = client.post(
            f"/api/v1/station/queue/{op_id}/release",
            headers=_auth_headers(token_a),
            json={"reason": "normalize_before_verify"},
        )
        if rel.status_code != 200:
            checks.append(
                Check(
                    name="Step 2c - Normalize pre-existing mine claim",
                    passed=False,
                    detail=f"status={rel.status_code}, body={rel.text}",
                )
            )
            _print_results(checks)
            raise SystemExit(1)

    # 3) Claim by operator A
    claim_a = client.post(
        f"/api/v1/station/queue/{op_id}/claim",
        headers=_auth_headers(token_a),
        json={},
    )
    checks.append(
        Check(
            name="Step 3 - Claim operation by operator A",
            passed=claim_a.status_code == 200,
            detail=f"status={claim_a.status_code}",
        )
    )

    # 4) Queue reflects claim as mine with claimed_by_user_id
    queue_after_claim = _get_queue_items(client, token_a)
    item_after_claim = _find_item(queue_after_claim, op_id)
    claim_summary_after_claim = item_after_claim.get("claim", {})
    state_after_claim = claim_summary_after_claim.get("state")
    claimed_by_after_claim = claim_summary_after_claim.get("claimed_by_user_id")
    checks.append(
        Check(
            name="Step 4 - Queue reflects claim state=mine",
            passed=state_after_claim == "mine" and claimed_by_after_claim == operator_a_user_id,
            detail=(
                f"state={state_after_claim}, claimed_by_user_id={claimed_by_after_claim}, "
                f"expected={operator_a_user_id}"
            ),
        )
    )

    # 5) Ensure operator B exists with same station scope
    _ensure_operator_b_with_same_station_scope_as_a()
    checks.append(
        Check(
            name="Step 5 - Operator B fixture present",
            passed=True,
            detail=f"user_id={OPERATOR_B_USER_ID}, username={OPERATOR_B_USERNAME}",
        )
    )

    # 6) Login operator B
    token_b, user_b = _login(client, OPERATOR_B_USERNAME)
    checks.append(
        Check(
            name="Step 6 - Login operator B",
            passed=user_b["user_id"] == OPERATOR_B_USER_ID,
            detail=f"status=200, user_id={user_b['user_id']}",
        )
    )

    # 7) Operator B claim conflict
    claim_b_conflict = client.post(
        f"/api/v1/station/queue/{op_id}/claim",
        headers=_auth_headers(token_b),
        json={},
    )
    checks.append(
        Check(
            name="Step 7 - Claim conflict for operator B",
            passed=claim_b_conflict.status_code == 409,
            detail=f"status={claim_b_conflict.status_code}, body={claim_b_conflict.text}",
        )
    )

    # 8) Release by operator A
    release_a = client.post(
        f"/api/v1/station/queue/{op_id}/release",
        headers=_auth_headers(token_a),
        json={"reason": "verify_release"},
    )
    checks.append(
        Check(
            name="Step 8 - Release by operator A",
            passed=release_a.status_code == 200,
            detail=f"status={release_a.status_code}",
        )
    )

    # 9) Queue reflects released state=none
    queue_after_release = _get_queue_items(client, token_a)
    item_after_release = _find_item(queue_after_release, op_id)
    state_after_release = item_after_release.get("claim", {}).get("state")
    checks.append(
        Check(
            name="Step 9 - Queue reflects released state=none",
            passed=state_after_release == "none",
            detail=f"state={state_after_release}",
        )
    )

    # 10) Mandatory claim enforcement
    start_without_claim_b = client.post(
        f"/api/v1/operations/{op_id}/start",
        headers=_auth_headers(token_b),
        json={},
    )
    checks.append(
        Check(
            name="Step 10a - Start denied without claim (operator B)",
            passed=start_without_claim_b.status_code == 403,
            detail=f"status={start_without_claim_b.status_code}, body={start_without_claim_b.text}",
        )
    )

    reclaim_a = client.post(
        f"/api/v1/station/queue/{op_id}/claim",
        headers=_auth_headers(token_a),
        json={},
    )
    checks.append(
        Check(
            name="Step 10b - Operator A re-claim",
            passed=reclaim_a.status_code == 200,
            detail=f"status={reclaim_a.status_code}",
        )
    )

    start_with_claim_a = client.post(
        f"/api/v1/operations/{op_id}/start",
        headers=_auth_headers(token_a),
        json={},
    )
    checks.append(
        Check(
            name="Step 10c - Start allowed when claim owned by operator A",
            passed=start_with_claim_a.status_code != 403,
            detail=f"status={start_with_claim_a.status_code}, body={start_with_claim_a.text}",
        )
    )

    cleanup_release = client.post(
        f"/api/v1/station/queue/{op_id}/release",
        headers=_auth_headers(token_a),
        json={"reason": "verify_cleanup"},
    )
    checks.append(
        Check(
            name="Cleanup - Release active claim",
            passed=cleanup_release.status_code == 200,
            detail=f"status={cleanup_release.status_code}",
        )
    )

    _print_results(checks)

    failed = [c for c in checks if not c.passed]
    if failed:
        print(f"\nFAILED: {len(failed)}/{len(checks)} checks")
        raise SystemExit(1)

    print(f"\nAll {len(checks)} checks passed.")


if __name__ == "__main__":
    main()

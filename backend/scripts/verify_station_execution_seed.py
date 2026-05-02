"""
PH6 station-execution seed verification.

Checks the dedicated PH6-STATION demo dataset still exposes the minimum
interactive coverage required by the station cockpit:

- at least one PLANNED operation visible to the OPR queue
- at least one IN_PROGRESS operation visible to the OPR queue
- station-session start guard can be satisfied for the station/operator context
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import app
from app.models.station_session import StationSession
from app.security.dependencies import RequestIdentity
from app.services.operation_service import ensure_open_station_session_for_command
from app.services.station_session_service import open_station_session

TENANT_ID = "default"
STATION_SCOPE = "STATION_01"
OPERATOR_USER_ID = "opr-001"
OPERATOR_USERNAME = "operator"
OPERATOR_PASSWORD = "password123"
SEED_PREFIX = "PH6-STATION-OP-"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _identity() -> RequestIdentity:
    return RequestIdentity(
        user_id=OPERATOR_USER_ID,
        username=OPERATOR_USERNAME,
        email=None,
        tenant_id=TENANT_ID,
        role_code="OPR",
        acting_role_code="OPR",
        is_authenticated=True,
    )


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": TENANT_ID,
    }


def _print_results(results: list[Check]) -> None:
    print("\nStation Execution Seed Verification")
    print("-----------------------------------")
    for check in results:
        state = "PASS" if check.passed else "FAIL"
        print(f"[{state}] {check.name}: {check.detail}")


def _clear_test_session(db) -> None:
    db.execute(
        StationSession.__table__.delete().where(
            StationSession.tenant_id == TENANT_ID,
            StationSession.station_id == STATION_SCOPE,
            StationSession.operator_user_id == OPERATOR_USER_ID,
        )
    )
    db.commit()


def _login(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": OPERATOR_USERNAME, "password": OPERATOR_PASSWORD},
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Login failed for seed verifier: {response.status_code} {response.text}"
        )
    return response.json()["access_token"]


def main() -> None:
    init_db()

    checks: list[Check] = []
    client = TestClient(app)

    token = _login(client)
    queue_response = client.get("/api/v1/station/queue", headers=_auth_headers(token))
    queue_items = queue_response.json().get("items", []) if queue_response.status_code == 200 else []

    seed_items = [
        item
        for item in queue_items
        if str(item.get("operation_number", "")).startswith(SEED_PREFIX)
    ]
    planned_items = [item for item in seed_items if item.get("status") == "PLANNED"]
    in_progress_items = [item for item in seed_items if item.get("status") == "IN_PROGRESS"]

    checks.append(
        Check(
            name="PH6-STATION queue readable for OPR",
            passed=queue_response.status_code == 200,
            detail=f"status={queue_response.status_code}",
        )
    )
    checks.append(
        Check(
            name="PH6-STATION items visible in station queue",
            passed=len(seed_items) >= 1,
            detail=f"seed_items={len(seed_items)}",
        )
    )
    checks.append(
        Check(
            name="PH6-STATION includes PLANNED queue item",
            passed=len(planned_items) >= 1,
            detail=f"planned_count={len(planned_items)}",
        )
    )
    checks.append(
        Check(
            name="PH6-STATION includes IN_PROGRESS queue item",
            passed=len(in_progress_items) >= 1,
            detail=f"in_progress_count={len(in_progress_items)}",
        )
    )

    session_guard_ok = False
    session_guard_error = None

    with SessionLocal() as db:
        try:
            _clear_test_session(db)
            open_station_session(
                db,
                _identity(),
                station_id=STATION_SCOPE,
            )
            ensure_open_station_session_for_command(
                db,
                tenant_id=TENANT_ID,
                station_id=STATION_SCOPE,
                operator_user_id=OPERATOR_USER_ID,
                command_name="start_operation",
            )
            session_guard_ok = True
        except Exception as exc:
            session_guard_error = str(exc)
        finally:
            _clear_test_session(db)

    checks.append(
        Check(
            name="StationSession start guard satisfiable for operator/station",
            passed=session_guard_ok,
            detail="guard passed" if session_guard_ok else f"error={session_guard_error}",
        )
    )

    _print_results(checks)

    failures = [check for check in checks if not check.passed]
    if failures:
        raise SystemExit(1)

    print("\nPH6-STATION seed contract checks passed.")


if __name__ == "__main__":
    main()

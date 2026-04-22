"""
PH6 station-execution seed verification.

Checks the dedicated PH6-STATION demo dataset still exposes the minimum
interactive coverage required by the station cockpit:

- at least one PLANNED operation visible to the OPR queue
- at least one IN_PROGRESS operation visible to the OPR queue
- at least one PLANNED operation that passes backend claim validation

This script is read-only. It does not mutate claims or execution state.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.security.dependencies import RequestIdentity
from app.services.station_claim_service import (
    _validate_operation_for_station,
    get_station_queue,
    resolve_station_scope,
)

TENANT_ID = "default"
STATION_SCOPE = "STATION_01"
OPERATOR_USER_ID = "opr-001"
OPERATOR_USERNAME = "operator"
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


def _print_results(results: list[Check]) -> None:
    print("\nStation Execution Seed Verification")
    print("-----------------------------------")
    for check in results:
        state = "PASS" if check.passed else "FAIL"
        print(f"[{state}] {check.name}: {check.detail}")


def main() -> None:
    init_db()

    identity = _identity()
    checks: list[Check] = []

    with SessionLocal() as db:
        try:
            station_scope = resolve_station_scope(db, identity)
            checks.append(
                Check(
                    name="OPR station scope resolves",
                    passed=station_scope.scope_value == STATION_SCOPE,
                    detail=(
                        f"resolved={station_scope.scope_value}, expected={STATION_SCOPE}"
                    ),
                )
            )
        except Exception as exc:
            checks.append(
                Check(
                    name="OPR station scope resolves",
                    passed=False,
                    detail=str(exc),
                )
            )
            _print_results(checks)
            raise SystemExit(1)

        station_scope_value, queue_items = get_station_queue(db, identity)
        seed_items = [
            item
            for item in queue_items
            if str(item.get("operation_number", "")).startswith(SEED_PREFIX)
        ]

        planned_items = [item for item in seed_items if item.get("status") == "PLANNED"]
        in_progress_items = [
            item for item in seed_items if item.get("status") == "IN_PROGRESS"
        ]

        checks.append(
            Check(
                name="PH6-STATION items visible in station queue",
                passed=len(seed_items) >= 1,
                detail=(
                    f"station_scope={station_scope_value}, seed_items={len(seed_items)}"
                ),
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

        claimable_operation_number = None
        claimable_operation_id = None
        claimable_error = None
        for item in planned_items:
            operation_id = int(item["operation_id"])
            try:
                operation = _validate_operation_for_station(
                    db,
                    identity=identity,
                    station_scope=station_scope,
                    operation_id=operation_id,
                )
                claimable_operation_number = operation.operation_number
                claimable_operation_id = operation.id
                break
            except Exception as exc:
                claimable_error = str(exc)

        checks.append(
            Check(
                name="PH6-STATION has claimable PLANNED operation",
                passed=claimable_operation_id is not None,
                detail=(
                    f"operation_id={claimable_operation_id}, "
                    f"operation_number={claimable_operation_number}"
                    if claimable_operation_id is not None
                    else f"validation_error={claimable_error or 'none'}"
                ),
            )
        )

    _print_results(checks)

    failures = [check for check in checks if not check.passed]
    if failures:
        raise SystemExit(1)

    print("\nPH6-STATION seed contract checks passed.")


if __name__ == "__main__":
    main()
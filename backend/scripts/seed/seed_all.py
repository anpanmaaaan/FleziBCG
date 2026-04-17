from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.master import StatusEnum, WorkOrder
from app.services.global_operation_service import build_work_order_operation_summaries
from app.services.work_order_execution_service import (
    build_work_order_summary_projection,
)

from .common import SEED_PREFIX, reset_seed_dataset
from .scenario_s1_normal_completion import seed as seed_s1
from .scenario_s2_completed_late import seed as seed_s2
from .scenario_s3_in_progress_block import seed as seed_s3
from .scenario_s4_repeat_variance import seed as seed_s4


@dataclass
class VerificationResult:
    name: str
    passed: bool
    details: str


def _coerce_projection_int(value: object, *, field: str) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    raise TypeError(
        f"Expected int-compatible value for '{field}', got {type(value).__name__}"
    )


def _fetch_work_order_by_number(db, wo_number: str) -> WorkOrder:
    work_order = db.scalar(
        select(WorkOrder).where(WorkOrder.work_order_number == wo_number)
    )
    if work_order is None:
        raise ValueError(f"Work order not found: {wo_number}")
    return work_order


def _verify_s1_s2(db, s1_wo_number: str, s2_wo_number: str) -> list[VerificationResult]:
    results: list[VerificationResult] = []

    s1_wo = _fetch_work_order_by_number(db, s1_wo_number)
    s1_projection = build_work_order_summary_projection(s1_wo)
    s1_pass = (
        s1_wo.status == StatusEnum.completed.value
        and s1_projection["completed_operations"] == s1_projection["operations_count"]
    )
    results.append(
        VerificationResult(
            name="S1 normal completion",
            passed=s1_pass,
            details=(
                f"status={s1_wo.status}, completed={s1_projection['completed_operations']}, "
                f"total={s1_projection['operations_count']}"
            ),
        )
    )

    s2_wo = _fetch_work_order_by_number(db, s2_wo_number)
    s2_projection = build_work_order_summary_projection(s2_wo)
    s2_pass = (
        s2_wo.status == StatusEnum.completed_late.value
        and s2_projection["completed_operations"] == s2_projection["operations_count"]
    )
    results.append(
        VerificationResult(
            name="S2 completed late",
            passed=s2_pass,
            details=(
                f"status={s2_wo.status}, completed={s2_projection['completed_operations']}, "
                f"total={s2_projection['operations_count']}"
            ),
        )
    )

    return results


def _verify_s3_supervisor(db, s3_wo_id: int) -> VerificationResult:
    rows = build_work_order_operation_summaries(db, s3_wo_id)
    has_blocked = any(row.supervisor_bucket == "BLOCKED" for row in rows)
    return VerificationResult(
        name="S3 supervisor blocked incident",
        passed=has_blocked,
        details=f"blocked_rows={sum(1 for row in rows if row.supervisor_bucket == 'BLOCKED')}",
    )


def _verify_s4_ie(db, s4_wo_id: int) -> VerificationResult:
    rows = build_work_order_operation_summaries(db, s4_wo_id)
    has_repeat = any(row.repeat_flag for row in rows)
    has_variance = any(row.high_variance_flag for row in rows)
    return VerificationResult(
        name="S4 IE repeat & variance",
        passed=has_repeat and has_variance,
        details=(
            f"repeat_rows={sum(1 for row in rows if row.repeat_flag)}, "
            f"high_variance_rows={sum(1 for row in rows if row.high_variance_flag)}"
        ),
    )


def _verify_non_regression(db) -> list[VerificationResult]:
    results: list[VerificationResult] = []

    all_seed_wos = list(
        db.scalars(
            select(WorkOrder).where(
                WorkOrder.work_order_number.like(f"{SEED_PREFIX}-%")
            )
        )
    )

    stuck_late = []
    zero_of_total = []
    for work_order in all_seed_wos:
        projection = build_work_order_summary_projection(work_order)
        completed = _coerce_projection_int(
            projection.get("completed_operations"),
            field="completed_operations",
        )
        total = _coerce_projection_int(
            projection.get("operations_count"),
            field="operations_count",
        )
        status = str(work_order.status)

        if total > 0 and completed == total and status == StatusEnum.late.value:
            stuck_late.append(work_order.work_order_number)

        if total > 0 and completed == total and completed == 0:
            zero_of_total.append(work_order.work_order_number)

    results.append(
        VerificationResult(
            name="No WO stuck in LATE after completion",
            passed=len(stuck_late) == 0,
            details=f"stuck={stuck_late}",
        )
    )
    results.append(
        VerificationResult(
            name="No completed WO shows 0/3 anomaly",
            passed=len(zero_of_total) == 0,
            details=f"anomalies={zero_of_total}",
        )
    )

    return results


def _print_results(results: list[VerificationResult]) -> None:
    print("\nVerification Results")
    print("--------------------")
    for result in results:
        state = "PASS" if result.passed else "FAIL"
        print(f"[{state}] {result.name}: {result.details}")


def main() -> None:
    init_db()

    with SessionLocal() as db:
        reset_seed_dataset(db)

        s1 = seed_s1(db)
        s2 = seed_s2(db)
        s3 = seed_s3(db)
        s4_contexts = seed_s4(db)

        results: list[VerificationResult] = []
        results.extend(
            _verify_s1_s2(
                db, s1.work_order.work_order_number, s2.work_order.work_order_number
            )
        )
        results.append(_verify_s3_supervisor(db, s3.work_order.id))
        results.append(_verify_s4_ie(db, s4_contexts[-1].work_order.id))
        results.extend(_verify_non_regression(db))

        _print_results(results)

        failed = [result for result in results if not result.passed]
        if failed:
            raise SystemExit(1)

        print("\nAll seed scenarios and checks passed.")


if __name__ == "__main__":
    main()

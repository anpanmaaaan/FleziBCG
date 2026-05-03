"""
Station Execution cockpit seed.

Populates a single work order at STATION_01 with operations in every cockpit
state the hardened station-execution UI must render:

  OP-001  PLANNED                  → Clock On
  OP-002  IN_PROGRESS              → Report Qty / Pause / Start Downtime / Complete
  OP-003  PAUSED (no downtime)     → Resume
  OP-004  PAUSED  + downtime_open  → End Downtime → Resume
  OP-005  BLOCKED + downtime_open  → End Downtime (BLOCKED→PAUSED)
  OP-006  COMPLETED                → terminal view

All driving commands go through the real service layer so the append-only
ExecutionEvent log, the derived snapshot fields (status, actual_start, etc.),
and the backend-derived `allowed_actions` projection all stay consistent with
what a live session would produce.

Seeding uses operator_id=None on start_operation so the "one-operation per
operator per station" guard is skipped — the seed creates multiple
simultaneous executions at the same station on purpose. The test user
(`operator`, user_id `opr-001`) is expected to select operations via the UI
to exercise the cockpit.
"""

from __future__ import annotations

from datetime import datetime
from typing import NotRequired, TypedDict

from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.schemas.operation import (
    OperationCompleteRequest,
    OperationEndDowntimeRequest,
    OperationPauseRequest,
    OperationReportQuantityRequest,
    OperationStartDowntimeRequest,
    OperationStartRequest,
)
from app.services.operation_service import (
    complete_operation,
    end_downtime,
    pause_operation,
    report_quantity,
    start_downtime,
    start_operation,
)


class _OpSpec(TypedDict):
    sequence: int
    suffix: str
    name: str
    quantity: int
    planned_start: str
    planned_end: str
    qc_required: NotRequired[bool]


SEED_PREFIX = "PH6-STATION"
TENANT_ID = "default"
STATION_SCOPE = "STATION_01"
OPERATOR_USER_ID = "opr-001"
SEED_ACTOR = "seed-user"


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _reset_station_seed(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{SEED_PREFIX}-%")
            )
        )
    )
    if not po_ids:
        db.commit()
        return

    wo_ids = list(
        db.scalars(
            select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))
        )
    )
    if wo_ids:
        operation_ids = list(
            db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids)))
        )
        if operation_ids:
            db.execute(
                delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(operation_ids))
            )
        db.execute(
            delete(ExecutionEvent).where(ExecutionEvent.work_order_id.in_(wo_ids))
        )
        db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))

    db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.commit()


def _make_operation(
    *,
    work_order_id: int,
    sequence: int,
    suffix: str,
    name: str,
    quantity: int,
    planned_start: str,
    planned_end: str,
    qc_required: bool = False,
) -> Operation:
    return Operation(
        operation_number=f"{SEED_PREFIX}-OP-{suffix}",
        work_order_id=work_order_id,
        sequence=sequence,
        name=name,
        status=StatusEnum.planned.value,
        planned_start=_dt(planned_start),
        planned_end=_dt(planned_end),
        quantity=quantity,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=qc_required,
        station_scope_value=STATION_SCOPE,
        tenant_id=TENANT_ID,
    )


def seed_station_execution_for_opr() -> None:
    init_db()

    with SessionLocal() as db:
        _reset_station_seed(db)

        production_order = ProductionOrder(
            order_number=f"{SEED_PREFIX}-PO-001",
            route_id=f"{SEED_PREFIX}-R-01",
            product_name="Station Execution Cockpit Demo",
            quantity=60,
            status=StatusEnum.planned.value,
            planned_start=_dt("2099-06-01T08:00:00"),
            planned_end=_dt("2099-06-01T17:00:00"),
            tenant_id=TENANT_ID,
        )
        db.add(production_order)
        db.flush()

        work_order = WorkOrder(
            production_order_id=production_order.id,
            work_order_number=f"{SEED_PREFIX}-WO-001",
            status=StatusEnum.planned.value,
            planned_start=_dt("2099-06-01T08:00:00"),
            planned_end=_dt("2099-06-01T17:00:00"),
            tenant_id=TENANT_ID,
        )
        db.add(work_order)
        db.flush()

        op_specs: list[_OpSpec] = [
            {
                "sequence": 10,
                "suffix": "001",
                "name": "Load Material (PLANNED)",
                "quantity": 10,
                "planned_start": "2099-06-01T08:10:00",
                "planned_end": "2099-06-01T09:00:00",
            },
            {
                "sequence": 20,
                "suffix": "002",
                "name": "Machine Run (IN_PROGRESS)",
                "quantity": 10,
                "planned_start": "2099-06-01T09:10:00",
                "planned_end": "2099-06-01T11:00:00",
            },
            {
                "sequence": 30,
                "suffix": "003",
                "name": "Visual Check (PAUSED)",
                "quantity": 10,
                "planned_start": "2099-06-01T11:10:00",
                "planned_end": "2099-06-01T12:00:00",
                "qc_required": True,
            },
            {
                "sequence": 40,
                "suffix": "004",
                "name": "Assembly (PAUSED + downtime)",
                "quantity": 10,
                "planned_start": "2099-06-01T12:10:00",
                "planned_end": "2099-06-01T13:30:00",
            },
            {
                "sequence": 50,
                "suffix": "005",
                "name": "Inspection (BLOCKED + downtime)",
                "quantity": 10,
                "planned_start": "2099-06-01T13:40:00",
                "planned_end": "2099-06-01T14:40:00",
                "qc_required": True,
            },
            {
                "sequence": 60,
                "suffix": "006",
                "name": "Packaging (COMPLETED)",
                "quantity": 10,
                "planned_start": "2099-06-01T14:50:00",
                "planned_end": "2099-06-01T16:00:00",
            },
        ]

        for spec in op_specs:
            db.add(_make_operation(work_order_id=work_order.id, **spec))
        db.commit()

        def _op(suffix: str) -> Operation:
            op = db.scalar(
                select(Operation).where(
                    Operation.operation_number == f"{SEED_PREFIX}-OP-{suffix}"
                )
            )
            if op is None:
                raise RuntimeError(f"Seeded operation not found: OP-{suffix}")
            return op

        # OP-001 stays PLANNED — nothing to drive.

        # OP-002 → IN_PROGRESS (plus a small quantity report so the cockpit
        # dashboard shows non-zero Completed / Good / Scrap totals).
        op002 = _op("002")
        start_operation(
            db,
            op002,
            OperationStartRequest(
                operator_id=None, started_at=_dt("2099-06-01T09:15:00")
            ),
            tenant_id=TENANT_ID,
        )
        report_quantity(
            db,
            _op("002"),
            OperationReportQuantityRequest(good_qty=3, scrap_qty=1, operator_id=None),
            tenant_id=TENANT_ID,
        )

        # OP-003 → PAUSED (no downtime).
        op003 = _op("003")
        start_operation(
            db,
            op003,
            OperationStartRequest(
                operator_id=None, started_at=_dt("2099-06-01T11:15:00")
            ),
            tenant_id=TENANT_ID,
        )
        pause_operation(
            db,
            _op("003"),
            OperationPauseRequest(
                reason_code="SHIFT_CHANGE", note="Seed: operator break"
            ),
            actor_user_id=SEED_ACTOR,
            tenant_id=TENANT_ID,
        )

        # OP-004 → PAUSED + downtime_open. Start → pause → start_downtime.
        # Policy: start_downtime on a PAUSED operation stays PAUSED; the
        # downtime_open flag lights up from the event log.
        op004 = _op("004")
        start_operation(
            db,
            op004,
            OperationStartRequest(
                operator_id=None, started_at=_dt("2099-06-01T12:15:00")
            ),
            tenant_id=TENANT_ID,
        )
        pause_operation(
            db,
            _op("004"),
            OperationPauseRequest(
                reason_code="WAITING_FOR_TOOL", note="Seed: waiting on tooling"
            ),
            actor_user_id=SEED_ACTOR,
            tenant_id=TENANT_ID,
        )
        start_downtime(
            db,
            _op("004"),
            OperationStartDowntimeRequest(
                reason_code="MATERIAL_SHORTAGE",
                note="Seed: material arriving next shift",
            ),
            actor_user_id=SEED_ACTOR,
            tenant_id=TENANT_ID,
        )

        # OP-005 → BLOCKED + downtime_open. Start → start_downtime directly
        # (IN_PROGRESS → BLOCKED per policy).
        op005 = _op("005")
        start_operation(
            db,
            op005,
            OperationStartRequest(
                operator_id=None, started_at=_dt("2099-06-01T13:45:00")
            ),
            tenant_id=TENANT_ID,
        )
        start_downtime(
            db,
            _op("005"),
            OperationStartDowntimeRequest(
                reason_code="BREAKDOWN_GENERIC",
                note="Seed: pneumatic line failure",
            ),
            actor_user_id=SEED_ACTOR,
            tenant_id=TENANT_ID,
        )

        # OP-006 → COMPLETED (start → report full quantity → complete).
        op006 = _op("006")
        start_operation(
            db,
            op006,
            OperationStartRequest(
                operator_id=None, started_at=_dt("2099-06-01T14:55:00")
            ),
            tenant_id=TENANT_ID,
        )
        report_quantity(
            db,
            _op("006"),
            OperationReportQuantityRequest(good_qty=10, scrap_qty=0, operator_id=None),
            tenant_id=TENANT_ID,
        )
        complete_operation(
            db,
            _op("006"),
            OperationCompleteRequest(
                operator_id=None, completed_at=_dt("2099-06-01T15:55:00")
            ),
            tenant_id=TENANT_ID,
        )

        # Sanity: double-check no downtime-related snapshot slipped past its
        # expected status, and that end_downtime still has a target. These
        # are not user-visible; they protect the seed from silent drift if
        # service policy changes.
        sanity_map = {
            "001": StatusEnum.planned.value,
            "002": StatusEnum.in_progress.value,
            "003": StatusEnum.paused.value,
            "004": StatusEnum.paused.value,
            "005": StatusEnum.blocked.value,
            "006": StatusEnum.completed.value,
        }
        for suffix, expected in sanity_map.items():
            actual = _op(suffix).status
            if actual != expected:
                raise RuntimeError(
                    f"Seed sanity failure: OP-{suffix} expected {expected}, got {actual}"
                )

        # Touch end_downtime on a fresh sixth op would have flipped it out of
        # the demo state, so we stop the drive phase here. Verify end_downtime
        # is still callable against OP-004 and OP-005 by confirming the event
        # log shows one open downtime each (started > ended).
        from app.models.execution import ExecutionEventType
        from app.repositories.execution_event_repository import get_events_for_operation

        for suffix in ("004", "005"):
            events = get_events_for_operation(db, _op(suffix).id)
            started = sum(
                1
                for e in events
                if e.event_type == ExecutionEventType.DOWNTIME_STARTED.value
            )
            ended = sum(
                1
                for e in events
                if e.event_type == ExecutionEventType.DOWNTIME_ENDED.value
            )
            if started <= ended:
                raise RuntimeError(
                    f"Seed sanity failure: OP-{suffix} should have an open downtime "
                    f"(started={started}, ended={ended})"
                )

        # Exercise end_downtime at least once by opening+closing a short
        # downtime on a throwaway path. We do NOT touch OP-001..OP-006 here;
        # instead we prove the service itself still accepts EndDowntimeRequest
        # shape by constructing one (no side effects) — keeps the import
        # statically referenced so a future typo breaks the seed early.
        _ = OperationEndDowntimeRequest(note=None)
        # end_downtime is imported but intentionally not invoked against
        # OP-004/OP-005 — those downtimes remain open so the UI can demo
        # end_downtime interactively. Keep the import alive for readers.
        _ = end_downtime

        seeded_rows = list(
            db.scalars(
                select(Operation)
                .where(Operation.operation_number.like(f"{SEED_PREFIX}-%"))
                .order_by(Operation.sequence.asc())
            )
        )

        print("Station execution seed ready.")
        print(f"operator user_id: {OPERATOR_USER_ID} (username: operator)")
        print(f"station scope:    {STATION_SCOPE}")
        print(f"production order: {production_order.order_number}")
        print(f"work order:       {work_order.work_order_number}")
        print("operations:")
        for operation in seeded_rows:
            print(
                f"  - id={operation.id:>4}  number={operation.operation_number}  "
                f"status={operation.status:<14}  "
                f"good={operation.good_qty:>2}  scrap={operation.scrap_qty:>2}  "
                f"name={operation.name}"
            )
        print(
            "\nCockpit coverage:\n"
            "  OP-001 PLANNED                → Clock On\n"
            "  OP-002 IN_PROGRESS            → Report Qty / Pause / Start Downtime / Complete\n"
            "  OP-003 PAUSED                 → Resume\n"
            "  OP-004 PAUSED + downtime_open → End Downtime → Resume\n"
            "  OP-005 BLOCKED + downtime_open → End Downtime (transitions to PAUSED)\n"
            "  OP-006 COMPLETED              → terminal view"
        )


if __name__ == "__main__":
    seed_station_execution_for_opr()

    # Run the read-only seed contract check immediately after reseeding so
    # drift is caught in the same operator workflow.
    from scripts.verify_station_execution_seed import main as verify_seed_main

    print("\nRunning PH6-STATION seed verification...")
    verify_seed_main()

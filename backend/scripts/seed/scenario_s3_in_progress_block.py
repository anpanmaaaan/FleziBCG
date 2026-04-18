from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from .common import ScenarioContext, create_scenario_context, mark_blocked_for_incident_seed, run_complete, run_start


def seed(db: Session) -> ScenarioContext:
    """
    S3: In-Progress + Blocked Incident
    
    Validates:
    - WO with multiple operations: one blocked, one in-progress
    - WO status resolves to BLOCKED (at least one op blocked, none in progress OR some in progress with blocked)
    - Supervisor lens identifies blocked operations
    - Demonstrates incident/delay handling scenario
    
    Note: Currently uses mark_blocked_for_incident_seed() which sets status directly.
    Future: Should create proper OP_BLOCKED execution event when blocking is implemented.
    """
    context = create_scenario_context(
        db,
        scenario_code="S3",
        wo_planned_start="2020-02-10T08:00:00",
        wo_planned_end="2020-02-10T12:00:00",
        operation_name_prefix="S3 Assembly",
        operation_plans=[
            (10, "2020-02-10T08:00:00", "2020-02-10T09:00:00", "Prep", False),
            (20, "2020-02-10T09:00:00", "2020-02-10T10:30:00", "Process", True),
            (30, "2020-02-10T10:30:00", "2020-02-10T12:00:00", "Inspect", True),
        ],
    )

    first_op = context.operations[0]
    second_op = context.operations[1]

    # First operation: Start then block due to material shortage
    run_start(db, first_op.id, started_at=first_op.planned_start, operator_id="seed-s3-op1")
    mark_blocked_for_incident_seed(db, first_op.id, reason_code="MATERIAL_SHORTAGE")

    # Second operation: Leave in-progress (started but not completed)
    run_start(db, second_op.id, started_at=second_op.planned_start, operator_id="seed-s3-op2")
    
    # Third operation: Leave pending (not started)
    # This demonstrates a mixed WO state where some ops are blocked, some in-progress, some pending

    return context

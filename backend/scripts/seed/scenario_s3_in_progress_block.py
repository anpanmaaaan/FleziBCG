from __future__ import annotations

from sqlalchemy.orm import Session

from .common import ScenarioContext, create_scenario_context, mark_blocked_for_incident_seed, run_start


def seed(db: Session) -> ScenarioContext:
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

    run_start(db, first_op.id)
    mark_blocked_for_incident_seed(db, first_op.id, reason_code="MATERIAL_SHORTAGE")

    run_start(db, second_op.id)

    return context

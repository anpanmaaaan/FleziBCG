from __future__ import annotations

from sqlalchemy.orm import Session

from .common import ScenarioContext, create_scenario_context, run_complete, run_start


def seed(db: Session) -> ScenarioContext:
    context = create_scenario_context(
        db,
        scenario_code="S1",
        wo_planned_start="2099-01-10T08:00:00",
        wo_planned_end="2099-01-10T18:00:00",
        operation_name_prefix="S1 Assembly",
        operation_plans=[
            (10, "2099-01-10T08:00:00", "2099-01-10T11:00:00", "Prep", False),
            (20, "2099-01-10T11:05:00", "2099-01-10T14:00:00", "Machine", True),
            (30, "2099-01-10T14:10:00", "2099-01-10T18:00:00", "Inspect", True),
        ],
    )

    for operation in context.operations:
        run_start(db, operation.id)
        run_complete(db, operation.id)

    return context

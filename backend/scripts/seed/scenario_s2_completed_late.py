from __future__ import annotations

from sqlalchemy.orm import Session

from .common import ScenarioContext, create_scenario_context, run_complete, run_start


def seed(db: Session) -> ScenarioContext:
    context = create_scenario_context(
        db,
        scenario_code="S2",
        wo_planned_start="2020-01-10T08:00:00",
        wo_planned_end="2020-01-10T09:00:00",
        operation_name_prefix="S2 HeatTreat",
        operation_plans=[
            (10, "2020-01-10T08:00:00", "2020-01-10T08:20:00", "Prep", False),
            (20, "2020-01-10T08:20:00", "2020-01-10T08:40:00", "Process", True),
            (30, "2020-01-10T08:40:00", "2020-01-10T09:00:00", "QC", True),
        ],
    )

    for operation in context.operations:
        run_start(db, operation.id)
        run_complete(db, operation.id)

    return context

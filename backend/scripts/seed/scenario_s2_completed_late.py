from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from .common import ScenarioContext, create_scenario_context, run_complete, run_start


def seed(db: Session) -> ScenarioContext:
    """
    S2: Completed Late
    
    Validates:
    - All operations complete after their planned_end times
    - WO status resolves to COMPLETED_LATE
    - Delay is correctly calculated
    - Timing logic: actual_end > planned_end = LATE
    """
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
        # Start at planned time
        run_start(db, operation.id, started_at=operation.planned_start)
        # Complete AFTER planned_end to trigger COMPLETED_LATE status
        # Add 30 minutes delay to ensure actual_end > planned_end
        completion_time = datetime.fromisoformat(operation.planned_end.isoformat())
        completion_time = completion_time.replace(hour=completion_time.hour + 1)  # 1 hour late
        run_complete(db, operation.id, completed_at=completion_time)

    return context

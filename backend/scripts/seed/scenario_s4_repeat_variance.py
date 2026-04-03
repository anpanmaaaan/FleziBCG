from __future__ import annotations

from sqlalchemy.orm import Session

from .common import ScenarioContext, create_scenario_context, run_complete, run_start


def seed(db: Session) -> list[ScenarioContext]:
    contexts: list[ScenarioContext] = []

    # Historical delayed samples for repeated process-step analysis.
    delayed_windows = [
        ("2020-03-10T08:00:00", "2020-03-10T08:05:00"),
        ("2020-03-11T08:00:00", "2020-03-11T09:00:00"),
        ("2020-03-12T08:00:00", "2020-03-12T10:00:00"),
    ]

    for index, (wo_start, wo_end) in enumerate(delayed_windows, start=1):
        scenario_code = f"S4H{index}"
        context = create_scenario_context(
            db,
            scenario_code=scenario_code,
            wo_planned_start=wo_start,
            wo_planned_end=wo_end,
            operation_name_prefix="S4 RepeatStep",
            operation_plans=[
                (10, wo_start, wo_end, "Core", True),
            ],
        )
        op = context.operations[0]
        run_start(db, op.id)
        run_complete(db, op.id)
        contexts.append(context)

    # Main scenario work order used for current IE investigation row.
    main_context = create_scenario_context(
        db,
        scenario_code="S4",
        wo_planned_start="2020-04-10T08:00:00",
        wo_planned_end="2020-04-10T09:00:00",
        operation_name_prefix="S4 RepeatStep",
        operation_plans=[
            (10, "2020-04-10T08:00:00", "2020-04-10T08:20:00", "Core", True),
            (20, "2020-04-10T08:20:00", "2020-04-10T09:00:00", "Secondary", False),
            (30, "2020-04-10T09:00:00", "2020-04-10T09:40:00", "Final", False),
        ],
    )

    # Complete first operation only to keep WO active but analytical flags visible.
    run_start(db, main_context.operations[0].id)
    run_complete(db, main_context.operations[0].id)

    contexts.append(main_context)
    return contexts

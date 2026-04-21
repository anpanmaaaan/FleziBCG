from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .common import ScenarioContext, create_scenario_context, run_complete, run_start


def seed(db: Session) -> list[ScenarioContext]:
    """
    S4: Repeat Variance Analysis

    Validates:
    - Process variance detection (same operation run multiple times with different cycle times)
    - IE/Process lens shows repeat_flag and high_variance_flag
    - Historical data for analysis (same operation_name in different WOs)
    - Variance calculated from cycle_time differences

    Creates:
    1. Three historical executions (S4H1, S4H2, S4H3) with varying cycle times
    2. Main scenario (S4) demonstrating current variance state
    """
    contexts: list[ScenarioContext] = []

    # Historical delayed samples showing variance in cycle times for same process step.
    # These runs show increasing delays:
    # - S4H1: 5 min cycle (quick)
    # - S4H2: 60 min cycle (normal, 12x slower)
    # - S4H3: 120 min cycle (slow, variance detected)
    historical_windows = [
        ("2020-03-10T08:00:00", "2020-03-10T08:05:00", 5),  # 5 minute cycle
        (
            "2020-03-11T08:00:00",
            "2020-03-11T09:00:00",
            60,
        ),  # 60 minute cycle (variance!)
        (
            "2020-03-12T08:00:00",
            "2020-03-12T10:00:00",
            120,
        ),  # 120 minute cycle (high variance!)
    ]

    for index, (wo_start, wo_end, cycle_minutes) in enumerate(
        historical_windows, start=1
    ):
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

        # Start at planned time
        start_time = datetime.fromisoformat(wo_start)
        run_start(db, op.id, started_at=start_time)

        # Complete with calculated cycle time
        completion_time = start_time + timedelta(minutes=cycle_minutes)
        run_complete(db, op.id, completed_at=completion_time)

        contexts.append(context)

    # Main scenario work order used for current IE investigation row.
    # Shows variance in progress (incomplete).
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

    # Complete first operation (matches historical "Core" operation for variance analysis)
    first_op = main_context.operations[0]
    run_start(
        db,
        first_op.id,
        started_at=datetime.fromisoformat(first_op.planned_start.isoformat()),
    )
    # Complete with 15-minute cycle (falls within variance of historical data)
    completion = datetime.fromisoformat(first_op.planned_start.isoformat()) + timedelta(
        minutes=15
    )
    run_complete(db, first_op.id, completed_at=completion)

    # Leave second and third operations in pending state
    # This demonstrates a work-in-progress scenario while variance analysis is ongoing

    contexts.append(main_context)
    return contexts

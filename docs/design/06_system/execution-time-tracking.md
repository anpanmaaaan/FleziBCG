# Execution Time Tracking (v4)

## Definitions
- total_time = end - start
- productive_time = RUNNING duration
- downtime = PAUSED (machine)
- idle_time = PAUSED (operator)

## Event Driven
duration = next_event - current_event

## States
RUNNING → productive
PAUSED(machine) → downtime
PAUSED(operator) → idle

## Rule
- No overlap
- Full coverage timeline

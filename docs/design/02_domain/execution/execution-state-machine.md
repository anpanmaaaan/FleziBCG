# Execution State Machine

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Clarified state shell vs ownership semantics. |

Status: Runtime/closure state-shell note for Station Execution.

## Runtime

`PLANNED -> IN_PROGRESS -> PAUSED -> IN_PROGRESS -> COMPLETED`

Additional derived runtime branch:
- `BLOCKED` when downtime/other blockers are active
- `ABORTED` where implementation/policy supports it

## Closure

`OPEN -> CLOSED -> OPEN`

## Rules

- no transition without event
- `COMPLETED` does not silently go back to `IN_PROGRESS`
- `CLOSED` blocks all mutations except authorized reopen
- ownership/session semantics are separate from runtime state names

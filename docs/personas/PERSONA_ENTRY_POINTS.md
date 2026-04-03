# PERSONA_ENTRY_POINTS

## Purpose
Define canonical entry points by persona using business intent, not UI mechanics.

## Scope
- Decision entry points
- Monitoring entry points
- Execution entry points

## Key Decisions (LOCKED)
- Operator execution entry: Work Order execution flow ending at Station Execution write surface.
- Supervisor monitoring entry: Work Orders and Global Operations read-only monitoring surfaces.
- Manager decision entry: Dashboard summary/health APIs and dashboard decision surface.
- Production Order acts as planning/filter context only.

## Explicitly Out Of Scope
- Any persona entry that bypasses backend source-of-truth
- Dashboard or monitoring entry points that perform execution writes

## Future (FUTURE)
- Additional persona-tailored entry routes if they preserve current execution boundaries.

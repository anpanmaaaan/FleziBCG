# EXECUTION_MODEL

## Purpose
Describe execution-state ownership and derivation responsibilities.

## Scope
- Work Order-centric execution lifecycle
- Operation runtime state
- Station Execution write actions
- Event-derived state in backend

## Key Decisions (LOCKED)
- Execution lifecycle actions are backend-authorized and event-recorded.
- Operation state is derived from append-only events.
- Frontend never becomes source-of-truth for execution state.
- Monitoring and dashboard surfaces consume derived read models only.

## Explicitly Out Of Scope
- UI-side status correction
- Direct DB mutation from frontend
- Alternative execution control channels outside current APIs

## Future (FUTURE)
- Additional derived read models from the same event lineage.

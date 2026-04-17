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
- **Two-Dimension Status Model (v1.1):** Execution lifecycle (PLANNED/IN_PROGRESS/COMPLETED/ABORTED) is orthogonal to readiness/dispatch status (PENDING/BLOCKED). See [mes-business-logic-v1.md §3](../system/mes-business-logic-v1.md) and [ADR-0001](../adr/ADR-0001-two-dimension-status-model.md).

## Explicitly Out Of Scope
- UI-side status correction
- Direct DB mutation from frontend
- Alternative execution control channels outside current APIs

## Future (FUTURE)
- Additional derived read models from the same event lineage.

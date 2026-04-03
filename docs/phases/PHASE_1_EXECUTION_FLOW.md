# PHASE_1_EXECUTION_FLOW

## Purpose
Document the locked execution flow used by runtime operations.

## Scope
- Work Order execution entry
- Operation-level runtime state
- Station Execution write actions
- Read-only execution context views supporting operator and supervisor awareness

## Key Decisions (LOCKED)
- Canonical flow:
  - `/work-orders`
  - `/work-orders/:woId/operations`
  - `/operations/:operationId/detail`
  - `/station-execution?operationId=...`
- Write actions (start/report/complete) are restricted to Station Execution.
- Execution state is derived from append-only backend execution events.
- Production Order may provide planning context but is not execution root.

## Explicitly Out Of Scope
- Global cross-order monitoring as a write surface
- Dashboard-level execution controls
- Frontend-based status derivation or correction

## Future (FUTURE)
- None in this document; phase is locked for execution semantics.

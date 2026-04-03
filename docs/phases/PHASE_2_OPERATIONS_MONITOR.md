# PHASE_2_OPERATIONS_MONITOR

## Purpose
Define the Global Operations monitoring capability as a read-only operational visibility surface.

## Scope
- Global operation list for monitoring and triage
- Filtering by status and planning context (including Production Order)
- Drill-down to operation detail read-only context

## Key Decisions (LOCKED)
- Global Operations is read-only.
- No execution lifecycle actions are allowed from monitoring screens.
- Backend state is displayed via API adapters and enum/code mappings only.
- Monitoring can drill down to detail, but does not own execution control.

## Explicitly Out Of Scope
- Start/complete/report actions from Global Operations
- Business-rule inference in frontend
- Dashboard substitution by operation-level views

## Future (FUTURE)
- Additional read-only monitoring dimensions if exposed by backend APIs.

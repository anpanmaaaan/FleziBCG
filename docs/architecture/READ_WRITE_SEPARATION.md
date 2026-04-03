# READ_WRITE_SEPARATION

## Purpose
Formalize read vs write boundaries across execution, monitoring, and dashboard surfaces.

## Scope
- Write surface: Station Execution
- Read surfaces: Work Order/Operation monitoring, Global Operations, Dashboard
- API-level constraints

## Key Decisions (LOCKED)
- Station Execution is the only execution write surface.
- Global Operations is read-only.
- Dashboard APIs are read-only and decision-level.
- No write action is permitted from dashboard or monitoring endpoints.
- Drill-down from dashboard is Work Order context only.

## Explicitly Out Of Scope
- Mixed read/write dashboards
- Hidden side-effect endpoints in read APIs
- Frontend business-rule-based execution actions

## Future (FUTURE)
- Additional read-only projections and filters with unchanged write ownership.

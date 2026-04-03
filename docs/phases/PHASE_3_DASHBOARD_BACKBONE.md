# PHASE_3_DASHBOARD_BACKBONE

## Purpose
Define dashboard APIs and usage as decision-level, persona-safe read-only services.

## Scope
- `/api/v1/dashboard/summary`
- `/api/v1/dashboard/health`
- High-level KPI and risk/bottleneck indicators
- Drill-down intent toward Work Order context

## Key Decisions (LOCKED)
- Dashboard is read-only.
- Dashboard does not expose operation-level lists or execution events.
- KPI and health derivation is backend service-layer responsibility.
- API responses use enums/codes, not translated business prose.
- Tenant-scoped aggregation is mandatory.

## Explicitly Out Of Scope
- Dashboard-triggered execution actions
- Direct links to operation execution write surfaces
- Auth/RBAC redesign in this phase

## Future (FUTURE)
- Additional summary/health metrics if implemented in backend and tenant-scoped.

---
name: "FleziBCG Execution Domain"
description: "Use when working on FleziBCG execution, station execution, station session, operation lifecycle, quantity reporting, downtime, completion, reopen, execution timeline, allowed actions, execution projections, or execution-related specs and plans."
applyTo: ["backend/app/api/v1/operations.py", "backend/app/api/v1/station.py", "backend/app/api/v1/station_sessions.py", "backend/app/api/v1/execution_timeline.py", "backend/app/services/operation_service.py", "backend/app/services/global_operation_service.py", "backend/app/services/work_order_execution_service.py", "backend/app/services/station_session_service.py", "backend/app/services/execution_timeline_service.py", "backend/app/models/execution.py", "backend/app/models/station_session.py", "frontend/src/app/api/operationApi.ts", "frontend/src/app/api/stationApi.ts", "frontend/src/app/api/operationMonitorApi.ts", "frontend/src/app/api/mappers/executionMapper.ts", "frontend/src/app/pages/StationExecution.tsx", "frontend/src/app/pages/StationSession.tsx", "frontend/src/app/pages/OperationExecutionOverview.tsx", "frontend/src/app/pages/OperationExecutionDetail.tsx", "frontend/src/app/pages/OperationTimeline.tsx", "frontend/src/app/components/station-execution/**"]
---
# Execution Domain Guidance

Primary truth:

- `docs/design/02_domain/execution/business-truth-station-execution-v4.md`
- `docs/design/02_domain/execution/domain-contracts-execution.md`
- `docs/design/02_domain/execution/station-execution-state-matrix-v4.md`
- `docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md`

## Load This When

- The task changes execution behavior, allowed actions, station/session ownership, quantity reporting, downtime, completion, closure, reopen, or execution read models.
- The task writes execution specs, implementation plans, or reviews.

## Non-Negotiables

- Backend is source of truth.
- Execution truth is append-only event history where eventing is used.
- Runtime status is derived, not manually decided by UI.
- Station Execution is session-owned in target truth.
- Authenticated user, identified operator, and equipment/resource context are separate concerns.
- Claim-centric behavior is migration debt, not target design truth.
- Frontend sends intent only and must not derive effective execution actor, resource, or allowed actions.
- `BLOCKED` is derived from runtime facts; do not hardcode it as a UI-only state.

## Required Modeling Rules

- Start, pause, resume, report production, downtime start/end, complete, close, and reopen must respect current runtime guards and ownership path.
- Open downtime blocks resume and complete at minimum.
- Quantity reporting remains discrete-first and delta-based in current scope.
- Good and scrap remain distinct quantities.
- Reopen is exceptional and must return to controlled non-running behavior.
- Allowed actions must come from backend-derived state and policy, not frontend heuristics.

## Hard Mode Trigger

- Treat execution work as Hard Mode MOM v3 by default when behavior, state transitions, event writing, projections, or authorization paths change.
- Before coding under v3, produce Design Evidence Extract, Event Map, Invariant Map, State Transition Map, Test Matrix, and Verdict.

## Implementation Boundaries

- Keep routes thin; business branching belongs in services.
- Do not put execution truth in frontend screen state.
- Do not treat projections or overview cards as authoritative.
- Do not delete claim compatibility paths unless the migration slice explicitly covers continuity and all consumers.

## Validation Focus

- Prefer behavior tests around the changed command or transition.
- Verify allowed actions and returned status from backend results.
- If contracts or route shapes change, treat that as intentional contract work and document it.

# FE-6 P0-C Execution UI Readiness Audit

Date: 2026-04-29
Owner: Frontend audit (no backend/db/route/screen implementation changes)
Scope: Execution-related frontend readiness for session-owned execution target (P0-C)

## Routing
- Selected brain: MOM Brain (flezibcg-ai-brain-v6-auto-execution)
- Selected mode: Architecture + QA audit mode
- Hard Mode MOM: Applied as design-governed execution audit context; no implementation coding under v3 gate
- Reason: Task touches execution/station/operator ownership model and operational truth boundaries

## Source Inputs Read
- .github/copilot-instructions.md
- .github/agent/AGENT.md
- docs/ai-skills/stitch-design-md-ui-ux/SKILL.md
- docs/ai-skills/hard-mode-mom-v3/SKILL.md
- docs/design/DESIGN.md
- docs/design/INDEX.md
- docs/design/AUTHORITATIVE_FILE_MAP.md
- docs/governance/CODING_RULES.md
- docs/governance/ENGINEERING_DECISIONS.md
- docs/governance/SOURCE_STRUCTURE.md
- docs/design/02_domain/execution/business-truth-station-execution-v4.md
- docs/design/02_domain/execution/execution-domain-overview.md
- docs/design/02_domain/execution/station-execution-state-matrix-v4.md
- docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md
- docs/design/02_domain/execution/station-execution-authorization-matrix-v4.md
- docs/design/02_domain/execution/station-execution-policy-and-master-data-v4.md
- docs/design/02_domain/execution/station-execution-operational-sop-v4.md
- docs/audit/frontend-source-alignment-snapshot.md
- frontend/src/app/pages/StationExecution.tsx
- frontend/src/app/pages/OperationExecutionDetail.tsx
- frontend/src/app/pages/DispatchQueue.tsx
- frontend/src/app/pages/OperationExecutionOverview.tsx
- frontend/src/app/pages/GlobalOperationList.tsx
- frontend/src/app/api/operationApi.ts
- frontend/src/app/api/stationApi.ts
- frontend/src/app/api/productionOrderApi.ts
- frontend/src/app/api/operationMonitorApi.ts
- frontend/src/app/screenStatus.ts

## Executive Verdict
Current execution UI is usable for compatibility-claim flow, but not yet aligned to session-owned execution semantics. The highest migration pressure is concentrated in Station Execution ownership and queue semantics. Monitoring/Gantt surfaces are largely preservable. Dispatch is still mock and should remain deferred until backend dispatch/session APIs stabilize.

## Current Execution UI Maturity

| Screen | Current maturity | Data source | Readiness for P0-C |
|---|---|---|---|
| StationExecution | PARTIAL | BACKEND_API (+ claim model) | Medium: preserve layout and action UX, rewrite ownership flow |
| OperationExecutionOverview | CONNECTED | BACKEND_API | High: preserve with contract-alignment updates |
| GlobalOperationList | CONNECTED | BACKEND_API | High: preserve with endpoint consolidation/perf hardening |
| OperationExecutionDetail | PARTIAL | MIXED | Medium-low: preserve header shell, replace mock tabs progressively |
| DispatchQueue | MOCK | MOCK_FIXTURE | Low: defer until backend dispatch/session-owned queue truth is available |

Evidence notes:
- screenStatus already flags StationExecution as compatibility claim model and PARTIAL.
- OperationExecutionDetail still contains readOnly placeholder arrays for QC/materials/timeline.
- DispatchQueue still runs entirely from in-file mockDispatchQueue and toast-only actions.

## Claim-Model Compatibility Areas (what currently works)
1. Backend-derived action gating exists in StationExecution via allowed_actions checks.
2. Operation lifecycle actions are backend-called (start/pause/resume/report/downtime/complete/close/reopen) and error-handled.
3. Work-order execution timeline rendering is backend-derived in OperationExecutionOverview.
4. Global operation monitor is backend-connected and persona-lens aware.
5. Closure status and reopen metadata are already surfaced in StationExecution and compatible with v4 closure truth.

## Session-Owned Target Gaps

### Gap A: Ownership primitive still claim-centric in StationExecution
- Current UI mode switching depends on claim.state and canExecuteByClaim.
- Claim/release buttons and queue-lock behavior are centered on stationApi claim endpoints.
- Target design deprecates claim as long-term ownership primitive and requires station session + operator identification + equipment context.

Impact:
- Main operator flow (Mode A/Mode B split) needs ownership gating rewrite to session context.

### Gap B: Missing station session UX/state carrier
- No frontend contract for open_station_session, identify_operator, bind_equipment, close_station_session.
- No persistent session summary panel in execution surfaces.

Impact:
- Cannot enforce/communicate session-required write preconditions from backend truth.

### Gap C: Queue schema is claim-shaped, not session-shaped
- stationApi queue type includes claim summary and claim state.
- Target model requires session ownership context indicators and should remove claim dependency from primary execution affordance.

Impact:
- Queue badges, filters, and lock semantics require contract update.

### Gap D: OperationExecutionDetail tabs remain mock
- QC/material/timeline/doc sections are placeholder arrays and not authoritative execution/quality/material truth.

Impact:
- Detail screen is not production-truth ready for P0-C governance expectations.

### Gap E: Dispatch remains non-authoritative
- No backend dispatch API integration.

Impact:
- Should not be used for operational truth during P0-C rollout.

## Backend API Dependencies for P0-C FE Readiness

### Required/updated frontend dependencies
1. Station session endpoints and read model
- open_station_session
- identify_operator
- bind_equipment
- close_station_session
- current active session summary endpoint for UI hydration/restore

2. Station queue/detail contracts
- Replace claim-centric fields with session-owned context (active session, identified operator, bound equipment where required)
- Maintain downtime_open/status/closure_status/allowed_actions in detail response

3. Operation command rejects aligned to v4 families
- SESSION_REQUIRED
- OPERATOR_IDENTIFICATION_REQUIRED
- EQUIPMENT_BINDING_REQUIRED
- STATE_INVALID_TRANSITION
- STATE_CLOSED_RECORD
- REASON_CODE_INVALID
- FORBIDDEN

4. Dispatch/read contracts (if/when enabled)
- Backend queue ordering and station dispatch status; no toast-only pseudo actions

### Existing APIs that remain useful
- operationApi lifecycle endpoints can remain surface-level stable if backend semantics shift to session-owned guards.
- work-order execution timeline endpoint can remain primary source for overview Gantt.
- monitor APIs remain useful for cross-order prioritization views.

## Screens to Preserve
1. OperationExecutionOverview
- Preserve Gantt-centric execution timeline view and drill-in pattern.
- Preserve backend-derived stats and operation click navigation.

2. GlobalOperationList
- Preserve monitoring lens concept and grouped operational triage UX.
- Preserve status mapping from backend monitor data.

3. StationExecution visual shell
- Preserve industrial touch-first layout, KPI cluster, action zone, downtime modal UX, closure/reopen panel.
- Preserve backend-first allowed_actions discipline.

## Screens to Defer
1. DispatchQueue
- Defer from operational truth path until backend dispatch/session contracts are available.
- Keep clearly labeled as MOCK in status registry until connected.

2. OperationExecutionDetail secondary tabs (QC/material/timeline/documents)
- Defer full truth claims for these tabs until backend endpoints are available.

## Screens Needing Rewrite After P0-C Backend Is Green
1. StationExecution ownership and selection flow (high priority rewrite)
- Replace claim-required execution mode logic with session-owned context logic.
- Replace claim/release actions with station session open/identify/bind/close lifecycle controls.
- Rework queue filter/lock semantics from claim-state to session-state truth.

2. Station API client layer
- Replace claim endpoints/types in stationApi with session-oriented contracts.
- Keep thin wrappers and preserve frontend/backend truth boundary.

3. OperationExecutionDetail tab data sections (incremental rewrite)
- Replace readOnly arrays with backend-backed queries when APIs are ready.

## Do-Not-Fake Rules (P0-C execution guardrails)
1. Do not infer execution ownership from frontend local state when backend session state is absent.
2. Do not treat visible buttons as permission truth.
3. Do not simulate start/pause/resume/downtime/complete success in UI without backend confirmation.
4. Do not fake operator identification or equipment binding state.
5. Do not derive or hardcode downtime reasons; use backend master data only.
6. Do not derive closure/reopen authority in frontend; backend authorization remains source of truth.
7. Do not present mock QC/material/timeline data as live execution truth.
8. Do not use dispatch mock list for real production decisions.

## Recommended First FE Execution Slice After P0-C Backend Is Green
Slice name: FE-EXE-P0C-1 Station Session Header + Guarded Action Enablement

Goal:
- Introduce session context strip at StationExecution top-level using backend session read endpoint.
- Gate execution action affordances by backend session-derived prerequisites (session open, operator identified, equipment bound where required) plus allowed_actions.
- Remove claim-only gating dependency from primary execution actions.

Why this first:
- Highest risk reduction for operational correctness.
- Minimal route impact (no route changes required).
- Preserves current StationExecution shell while moving truth boundary to session-owned model.

Acceptance signals:
- No action button enabled when backend reports missing session/operator/equipment prerequisites.
- Backend reject families are surfaced with explicit, non-fake user guidance.
- Existing build/lint/route checks remain green.

## Notes on Snapshot Consistency
The broad snapshot historically described StationExecution as fully connected, while current screenStatus marks it PARTIAL due claim-compatibility debt. For P0-C planning, treat screenStatus and current source code as the more precise readiness indicator.

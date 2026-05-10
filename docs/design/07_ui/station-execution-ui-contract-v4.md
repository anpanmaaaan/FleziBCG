# Station Execution UI Contract v4

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-10 | v1.0 | Initial v4 UI contract for Station Setup -> Station Queue -> Station Cockpit flow, runtime visibility, and interrupted-mode boundaries. |

## Routing
- Selected brain: MOM Brain
- Selected mode: Product / Architecture / UI contract mode
- Hard Mode MOM: v3 ON
- Reason: Contract governs execution-adjacent Station UI behavior, state visibility, and backend-truth boundaries.

## Slice ID

- `DOC-SE-UI-CONTRACT-05`

## Status

Authoritative UI contract for Station Execution frontend behavior and boundaries.

## 1. Purpose

Define the canonical Station UI v4 contract for the three-screen operator journey:

1. Station Setup
2. Station Queue
3. Station Cockpit

This contract aligns UI composition with backend-owned execution truth, command legality, and session ownership.

## 2. Non-Negotiable Truth Boundaries

1. Backend is source of truth for execution state, closure state, and authorization.
2. Frontend sends intent only; frontend never derives command legality from status text.
3. Frontend renders backend-derived `allowed_actions` and ownership/session context.
4. Frontend never decides close/reopen legality.
5. Frontend never fakes quality pass/fail, ERP posting, backflush completion, or AI deterministic outcomes.

## 3. Scope

In scope:

- Screen-level behavior for Setup, Queue, Cockpit.
- Runtime visibility stage expectations for in-progress, paused, blocked, and downtime-interrupted states.
- Component ownership boundaries for v4 Station UI composition.
- Accessibility and responsive requirements for operator use.

Out of scope:

- Backend command/state/API changes.
- New authorization rules.
- New event schema or projection behavior.
- Quality workflow implementation beyond existing backend flags.

## 4. Canonical Screen Contract

### 4.1 Station Setup

Purpose:

- Confirm minimum execution context readiness.

Required UI responsibilities:

- Show station/session/operator/equipment context tokens.
- Surface open/close session intent.
- Provide routes to operator identification and equipment binding.
- Provide explicit handoff to Queue.

Rules:

- Setup readiness UX is advisory only.
- Backend revalidates session/operator/equipment on mutation commands.

### 4.2 Station Queue

Purpose:

- Show selectable work list under station context.

Required UI responsibilities:

- Show queue summary metrics and filters.
- Show operation list with runtime and ownership hints.
- Allow selection and route into Cockpit.
- Show session-handoff strip as compact context guidance.

Rules:

- Queue card behavior is projection-derived and non-authoritative.
- Queue UI must not infer command legality.

### 4.3 Station Cockpit

Purpose:

- Execute selected operation using backend-derived truth.

Required UI responsibilities:

- Show operation identity, runtime status, closure status, and key totals.
- Show guidance and command zone driven by `allowed_actions` plus session-control prerequisites.
- Show quantity reporting, downtime controls, completion summary, and closure/reopen panel.
- Keep Back to Queue and Queue overlay access available.

Rules:

- Cockpit action visibility is backend-derived.
- Frontend must handle command rejects as expected runtime outcomes.

## 5. Runtime Visibility and Interrupted Mode Contract

### 5.1 Stage Mapping

- `STX_005_ACTIVE_OPERATION`: selected operation active cockpit context.
- `STX_006_RUNTIME_VISIBILITY`: paused/blocked/downtime-interrupted execution visibility state.
- `STX_007_COMPLETION`: completed operation summary and next-step guidance.

### 5.2 Interrupted Mode Definition

Interrupted mode is a cockpit visualization mode, not a backend state mutation.

Interrupted mode triggers when either condition holds:

1. `status = PAUSED`
2. `status = BLOCKED` or `downtime_open = true`

Interrupted mode responsibilities:

- Promote blocker/interruption context near the top of cockpit body.
- Reduce non-actionable affordances.
- Keep only safe next actions visible (for example resume or end downtime depending on backend state).
- Preserve read visibility for quantity/timer/identity context.

Interrupted mode must not:

- Invent status.
- Invent actions not present in `allowed_actions`.
- Auto-transition runtime state.

## 6. Component Ownership Contract (v4)

### 6.1 Shared shell/context components

- `StationWorkflowShell`: stage rail + context tokens + recovery slot.
- `StationEntryHandoff`: setup/queue/cockpit readiness strip and route affordances.

### 6.2 Queue surfaces

- `StationQueuePanel`
- `QueueFilterBar`
- `QueueOperationCard`

### 6.3 Cockpit surfaces

- `StationExecutionHeader`
- `ExecutionStateHero`
- `QuantitySummaryPanel`
- `AllowedActionZone`
- `ClosureStatePanel`
- `CompletionSummaryPanel`
- `StartDowntimeDialog`
- `ReopenOperationModal`

### 6.4 Boundaries

- Components do not own backend truth.
- Components receive derived data/permissions from page-level orchestration.
- Components do not maintain parallel command legality models.

## 7. Responsive and A11y Contract

1. Operator-primary command buttons: minimum 56px target height.
2. Secondary execution actions: minimum 48px target height.
3. Narrow width behavior (<640px): paired runtime actions stack single-column.
4. Queue-mode CTA strips must wrap under narrow widths.
5. Modal/dialog flows must preserve focus management, Escape close, and semantic labeling.

## 8. Route and Navigation Contract

Required route surfaces:

- `/station-session`
- `/operator-identification`
- `/equipment-binding`
- `/station` (and `/station-execution` alias)

Rules:

- Route registration and auth layout nesting must remain valid.
- Persona visibility is UX routing only, not authorization truth.

## 9. Acceptance Criteria

1. Setup, Queue, and Cockpit remain explicit and non-overlapping in responsibilities.
2. Cockpit command zone is always backend-derived (`allowed_actions` + session guard context).
3. Runtime interrupted context is visible when paused/blocked/downtime-open.
4. Stage semantics represent runtime visibility (`STX_006`) distinctly from active operation (`STX_005`).
5. Responsive and a11y rules pass lint/build/route/i18n gates.

## 10. Related Slices

- `DOC-SE-ANDON-PROPOSAL-06`
- `FE-SE-V4-COMPONENTS-05`
- `FE-SE-COCKPIT-REWORK-07`
- `FE-SE-INTERRUPTED-MODE-08`

## 11. Verification Gate (docs slice)

This slice is docs-only.

Minimum checks:

1. File exists and links are consistent with current route/component names.
2. Contract does not introduce backend/API behavior claims outside current authoritative docs.

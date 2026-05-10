# Station Execution Andon Proposal v1

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-10 | v1.0 | Initial Station Execution Andon proposal for operator/supervisor visibility and escalation UX. |

## Routing
- Selected brain: MOM Brain
- Selected mode: Product / UI proposal mode
- Hard Mode MOM: v3 ON
- Reason: Proposal touches execution-adjacent visibility and escalation semantics and must preserve backend truth boundaries.

## Slice ID

- `DOC-SE-ANDON-PROPOSAL-06`

## Status

PROPOSAL-ONLY.

No backend, API, or command behavior changes are defined or implied by this document.

## 1. Objective

Define a practical Andon UX proposal for Station screens that:

1. Improves runtime interruption awareness.
2. Clarifies when operator action is sufficient versus supervisor support is needed.
3. Preserves backend-owned truth and command legality.

## 2. Guardrails

1. Frontend does not create Andon truth.
2. Frontend displays backend-derived conditions and errors.
3. Andon UI cannot authorize, unblock, or transition execution state by itself.
4. Any escalation action remains intent-only unless backend contract exists.

## 3. Andon Signal Taxonomy (UI Layer)

### 3.1 Informational Andon

Examples:

- Session not yet open.
- Operator not identified.
- Equipment context optional/unknown.

UI treatment:

- Blue advisory panel with next-step guidance.

### 3.2 Warning Andon

Examples:

- Required equipment missing.
- Operation paused with no resumed action yet.
- Queue selection mismatch with active session ownership expectations.

UI treatment:

- Amber warning panel with clear remediation route.

### 3.3 Blocking Andon

Examples:

- `status = BLOCKED`.
- `downtime_open = true` and progression commands are unavailable.
- Backend reject codes for session/operator/equipment mismatch.

UI treatment:

- Red interruption panel with explicit safe-next-action guidance.

## 4. Screen Placement Proposal

### 4.1 Setup

- Show informational/warning Andon in handoff strip context.
- No blocking red panel unless backend returns hard reject on session actions.

### 4.2 Queue

- Show queue-level warning/bocking chips per operation card.
- Add compact summary count for warning/blocking conditions in queue summary row.

### 4.3 Cockpit

- Primary Andon region directly below handoff strip and above action zone.
- In interrupted mode, Andon panel becomes dominant and collapses non-essential helper text.

## 5. Trigger Inputs (Backend-Derived)

Candidate input signals:

1. `operation.status`
2. `operation.closure_status`
3. `operation.downtime_open`
4. `operation.quality_hold_open`
5. `operation.allowed_actions`
6. session ownership projection (`owner_state`, `has_open_session`, `operator_user_id`, `equipment_id`)
7. normalized command error codes

No client-invented signals are allowed.

## 6. Escalation UX Proposal

### 6.1 Operator flow

- Operator sees next safe action first.
- If no operator-safe action exists, show supervised escalation hint.

### 6.2 Supervisor flow

- Supervisor-only context remains visually marked and non-primary in operator shell.
- Supervisor route affordance may be shown as secondary link only.

### 6.3 Proposed CTA language

- `Resolve in Cockpit`
- `End Downtime`
- `Resume When Safe`
- `Open Session Context`
- `Request Supervisor Review` (intent-only placeholder unless backend route exists)

## 7. Visual Contract

1. Severity-based icon + text + border color, never color-only.
2. Single primary message plus one optional recovery line.
3. Action area supports one dominant CTA and optional secondary route links.
4. Persistent Andon states should remain visible until backend state changes.

## 8. Accessibility Contract

1. Andon panel uses `role="alert"` only for newly raised blocking/warning conditions.
2. Static advisory panels use standard region semantics.
3. Buttons remain minimum touch target size per responsive contract.
4. Messaging keys are i18n-backed and EN/JA synchronized.

## 9. Deferred Decisions

1. Audible/stack-light/hardware Andon integration.
2. Push notifications to supervisor consoles.
3. SLA timers and escalation thresholds.
4. Cross-station Andon aggregation dashboard.

These require backend event/projection and policy work outside this proposal.

## 10. Acceptance Criteria (Proposal)

1. Proposal clearly separates UI severity from backend truth ownership.
2. Proposal identifies practical screen placement and trigger inputs.
3. Proposal avoids introducing fake escalation authority in frontend.
4. Proposal is implementation-ready for class-level UI work in later slices.

## 11. Follow-on Implementation Slices

- `FE-SE-V4-COMPONENTS-05`
- `FE-SE-COCKPIT-REWORK-07`
- `FE-SE-INTERRUPTED-MODE-08`

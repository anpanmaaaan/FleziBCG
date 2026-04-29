# FE Execution P0-C UI Slice Contract

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial FE-EXE-P0C-0 contract. Converted FE-6 audit into prioritized frontend execution backlog and implementation contract. No runtime UI implementation changes. |
| 2026-04-29 | v1.1 | Corrected allowed_actions dependency status to PARTIAL for session-owned P0-C readiness and added explicit caution note. |

## 1. Purpose

Define a frontend-only execution migration contract for P0-C that converts FE-6 audit findings into:
- prioritized backlog slices
- backend dependency gating
- non-fake implementation boundaries
- verification and acceptance criteria

This document is planning and governance output only.

Out of scope in this slice:
- backend changes
- database changes
- migration changes
- StationExecution rewrite
- new execution screens
- route changes

## 2. Current UI Reality

Current execution UI state (source-aligned):

1. StationExecution is backend-connected but claim-compatible and not session-owned.
2. OperationExecutionOverview is backend-connected and suitable for preservation.
3. GlobalOperationList is backend-connected and suitable for preservation.
4. OperationExecutionDetail is mixed: backend operation header plus placeholder tabs for quality/materials/timeline/documents.
5. DispatchQueue remains mock/fixture-only and is non-authoritative.

Operational truth posture:
- backend-derived allowed_actions is already used in StationExecution and must remain authoritative.
- command success/failure remains backend-determined.
- current ownership semantics in StationExecution are still claim-centric and represent migration debt relative to v4 session-owned design.

## 3. Backend Dependency Matrix

Status legend:
- AVAILABLE: capability is already consumable from current frontend-visible backend contract.
- PARTIAL: some usable contract exists, but not in v4 session-owned target shape.
- MISSING: required capability has no current consumable contract for FE.
- UNKNOWN: capability may exist internally but is not confirmed consumable for FE.

Current allowed_actions visibility is useful as a pattern, but FE must not treat it as P0-C-ready until backend provides the canonical session-owned allowed_actions payload and reject-code examples.

| Required backend capability | Current FE evidence | Status | Notes for FE coding gate |
|---|---|---|---|
| station session open | no session endpoint in stationApi | MISSING | required before session-owned StationExecution migration |
| station session close | no session endpoint in stationApi | MISSING | required before session lifecycle UI controls |
| operator identification | no identify-operator endpoint in stationApi | MISSING | required to satisfy v4 operator/session separation |
| equipment binding | no bind-equipment endpoint in stationApi | MISSING | required where station policy mandates explicit binding |
| current operation context | stationApi.getOperationDetail + queue context exists | PARTIAL | operation context exists, but no backend session summary/operator/equipment context payload |
| allowed_actions | operation detail includes allowed_actions and FE consumes it | PARTIAL | current payload is useful, but P0-C requires canonical session-owned allowed_actions derived from station session, operator identity, equipment binding, operation state, blocked reason, and authorization/scope |
| start | operationApi.start exists and is used | PARTIAL | command exists; target P0-C requires session reject family parity |
| pause | operationApi.pause exists and is used | PARTIAL | command exists; target P0-C requires session reject family parity |
| resume | operationApi.resume exists and is used | PARTIAL | command exists; target P0-C requires session + downtime guard parity |
| report quantity | operationApi.reportQuantity exists and is used | PARTIAL | command exists; target P0-C requires session-owned guard parity |
| downtime start/end | operationApi.startDowntime/endDowntime exists and is used | PARTIAL | command exists; target P0-C requires reason/session contract parity |
| complete | operationApi.complete exists and is used | PARTIAL | command exists; target P0-C requires session + invalid-transition parity |
| close/reopen | operationApi.close/reopen exists and is used | PARTIAL | command exists; keep backend authorization and closure guards authoritative |
| event timeline | work-order execution timeline endpoint consumed by OperationExecutionOverview | AVAILABLE | preserve as authoritative read surface |
| blocked reason projection | monitor payload has optional blockReasonCode/flags; station detail lacks canonical blocked-reason projection | PARTIAL | requires explicit canonical projection contract for StationExecution guidance UI |

## 4. Screen Preservation Strategy

| Screen / surface | Classification | Contract direction |
|---|---|---|
| StationExecution shell and layout primitives | REWRITE_AFTER_BACKEND | preserve visual shell and action-zone ergonomics; replace claim ownership flow only after backend session contracts are verified |
| OperationExecutionOverview | PRESERVE | keep current backend timeline wiring and drill-down flow; adjust only if backend timeline contract evolves |
| GlobalOperationList | PRESERVE | keep backend monitor lens and triage flow; align optional fields as contracts harden |
| OperationExecutionDetail | EXTEND | retain route/screen shell; replace placeholder tabs incrementally only when backend read contracts are verified |
| DispatchQueue | DEFER | keep non-authoritative state clearly marked until backend dispatch/session queue truth is available |
| claim-centric StationExecution affordances (claim/release-specific ownership UI path) | REMOVE_LATER | remove only after session-owned replacement is backend-ready and verified |

## 5. First Safe FE Slice After Backend P0-C

Slice: FE-EXE-P0C-1 (future implementation only)

Scope:
1. session header
2. backend-derived current state
3. backend-derived allowed actions
4. no command mutation unless endpoint is verified

Implementation contract:
- introduce a StationExecution session header area that renders backend session summary only.
- gate action enablement by backend response only (session/operator/equipment prerequisites + allowed_actions).
- keep all existing command buttons disabled when required session prerequisites are missing in backend response.
- do not introduce optimistic or inferred ownership states in frontend.

Explicit non-goals for FE-EXE-P0C-1:
- no new route
- no new standalone screen
- no StationExecution full rewrite
- no frontend-side fallback ownership derivation

## 6. Do-Not-Fake Rules

Mandatory rules:
1. no frontend-derived execution state
2. no frontend-derived allowed_actions
3. no fake session ownership
4. no fake operator/equipment binding
5. no fake command success
6. no fake QC/material/timeline truth

Additional enforcement:
- do not present visibility of a button as authorization truth.
- do not simulate backend reject families in frontend without backend response.
- do not backfill missing backend fields with fabricated operational values.

## 7. Acceptance Criteria

A. Contract completeness
1. all required dependency capabilities are statused (AVAILABLE/PARTIAL/MISSING/UNKNOWN).
2. each status has a concrete evidence note and FE implication.

B. Slice safety
1. first implementation slice is FE-EXE-P0C-1 only.
2. FE-EXE-P0C-1 excludes route/screen expansion and StationExecution rewrite.

C. Non-fake compliance
1. do-not-fake rules are explicit and testable.
2. allowed_actions and execution state remain backend-authoritative.

D. Preservation/defer strategy
1. each target screen has one clear preservation classification and rationale.
2. DispatchQueue remains deferred until backend truth is present.

## 8. Required Backend Contract Before Coding

Frontend execution migration must not start coding until backend confirms consumable contracts for:

1. station session read/open/close
2. operator identification in session context
3. equipment binding in session context where policy requires
4. station operation detail including:
   - current ownership/session summary
   - current operator summary
   - bound equipment summary when applicable
   - allowed_actions
   - downtime_open
   - closure_status
   - blocked reason projection
5. command reject family parity for FE guidance:
   - SESSION_REQUIRED
   - OPERATOR_IDENTIFICATION_REQUIRED
   - EQUIPMENT_BINDING_REQUIRED
   - STATE_INVALID_TRANSITION
   - STATE_CLOSED_RECORD
   - REASON_CODE_INVALID
   - FORBIDDEN

Minimum backend/FE handshake artifact required before coding:
- endpoint list + payload examples + reject code examples for each command/read contract in scope.

## 9. Test / Verification Plan

Required verification gates for future FE implementation slices:

1. build
- run frontend build and require pass.

2. lint
- run frontend lint and require pass.

3. check:routes
- run route smoke checks and require pass.

4. route accessibility gate
- verify route registration, layout nesting, auth behavior, persona/menu alignment, and screenStatus alignment for any touched route path.

5. manual station route smoke
- direct URL and in-app navigation smoke for StationExecution path(s).
- confirm no route regression from execution slice changes.

6. command button disabled/enabled validation based on backend response only
- verify each command affordance state is driven exclusively by backend session/context + allowed_actions payload.
- verify missing backend prerequisites keep actions disabled.
- verify frontend does not enable actions via local inference.

## 10. Recommended Sequencing

Recommended FE sequencing after backend readiness:

1. FE-EXE-P0C-1
- session header + backend-derived action gating in StationExecution shell

2. FE-EXE-P0C-2
- station queue/detail schema alignment from claim-shaped fields to session-shaped ownership indicators

3. FE-EXE-P0C-3
- OperationExecutionDetail tab truth replacement (quality/material/timeline/documents) as backend endpoints become available

4. FE-EXE-P0C-4
- DispatchQueue migration from mock to backend dispatch/session truth (only when backend contract is stable)

Coordination rule:
- do not advance to the next FE slice until prior slice has passing verification gates and backend contract sign-off for the next dependency set.
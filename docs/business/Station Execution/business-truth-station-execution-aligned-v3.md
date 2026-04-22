# Business Truth — Station Execution
## Current implemented baseline alignment note

Status: **Authoritative business truth for the current implemented backend baseline**  
Baseline scope: **Station Execution Core / Pre-QC / Pre-Review**

This version reconciles the business-truth document with what is actually implemented now. It preserves the canonical target direction, but it does **not** claim full canonical Station Execution v1 parity.

## 1. Scope

### 1.1 In scope now
The current implemented backend baseline covers:

- operation claim in station context
- start / pause / resume / report / start downtime / end downtime / complete
- queue/detail truth alignment on derived runtime status
- `closure_status` as a separate dimension
- `close_operation` foundation
- `reopen_operation` foundation
- reopen metadata
- reopen claim-continuity protection
- closure-aware allowed actions
- closed-record invariant on execution writes
- single-active-claim safe default in the same station context

### 1.2 Designed but deferred
The following remain part of broader canonical direction, but are **not implemented in the current backend baseline**:

- station session entity and open/close station session commands
- `quality_status` dimension
- `review_status` dimension
- QC measurement submission and backend QC evaluation
- exception raising
- disposition decision flow
- approved-effects lifecycle
- full dispatch-status model parity
- full policy-gated close/reopen variants

## 2. Foundational principles

### BT-CORE-001 — Backend is the source of truth
Frontend renders backend-derived projections and sends commands. It does not decide execution truth.

### BT-CORE-002 — Execution truth is event history
Important execution facts are append-only business events.

### BT-CORE-003 — Status is derived
Runtime status is derived from event history. Snapshot/projection fields are support data, not truth.

### BT-CORE-004 — Persona is not permission
Role names and visible buttons do not grant write authority. Authorization is checked on backend per command.

### BT-CORE-005 — AI is advisory only
AI may explain or recommend, but must not mutate execution truth by default.

### BT-CORE-006 — Corrections must stay auditable
The current baseline does not permit silent destructive correction of execution history.

## 3. Current aggregate boundary

The implemented execution-core aggregate is still effectively centered on **operation execution at station context**, even though some broader canonical dimensions remain deferred.

Queue, cockpit, and detail must read the same backend-derived execution truth.

## 4. Role intent in the current baseline

### 4.1 OPR
Implemented as the primary execution actor for:
- claim
- start
- pause
- resume
- report quantity
- start/end downtime
- complete

Not allowed in the current baseline to:
- reopen closed execution
- use `close_operation` directly under the current hardened phase rule

### 4.2 SUP
Implemented as the current phase owner for:
- `close_operation` (narrow phase rule at API boundary)
- `reopen_operation`

This is stricter than the broader canonical future target and is intentional for the current pre-QC baseline.

### 4.3 QCI/QAL
Quality-owned roles remain part of the canonical target model, but the current backend baseline does not yet implement quality/disposition command paths.

### 4.4 ADM / OTS
Not normal shopfloor actors. No broad production execution shortcut is implied by support/admin existence.

## 5. State dimensions

### 5.1 Runtime execution status (implemented carrier)
Current implemented runtime carrier still uses the flattened execution status family:

- `PLANNED`
- `IN_PROGRESS`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`
- `ABORTED` (implementation enum support where applicable)

This is an interim execution-core carrier, not the final full canonical orthogonal state model.

### 5.2 Closure status (implemented orthogonal dimension)
Implemented values:
- `OPEN`
- `CLOSED`

Current implemented rule:
- `CLOSED` records reject execution write commands
- `close_operation` sets `closure_status = CLOSED`
- `reopen_operation` sets `closure_status = OPEN`

### 5.3 Deferred orthogonal dimensions
Not yet implemented as persisted operational dimensions in the current backend baseline:
- `quality_status`
- `review_status`
- full `dispatch_status`

## 6. Claim truth

### BT-CLAIM-001 — Single active unreleased claim per operator per station context (default v1)
Current safe default:
- one operator may hold at most one unreleased claim at a time in the same station context
- second-claim attempts are rejected
- queue visibility is broader than claimability

### BT-CLAIM-002 — Claim continuity across active non-terminal states
Current implemented baseline preserves claim continuity across:
- `IN_PROGRESS`
- `PAUSED`
- `BLOCKED`

Ordinary release is not the mechanism for active-work switching in these states.

### BT-CLAIM-003 — Reopen preserves resumability path
Current implemented reopen foundation preserves or safely restores claim continuity when a prior valid ownership path exists, so reopened work is not stranded.

## 7. Core execution lifecycle truth

### BT-EX-001 — Claim
Claim is station-owned in the current baseline.

### BT-EX-002 — Start execution
Implemented start requires current backend start guards and valid claim ownership.

### BT-EX-003 — Pause execution
Implemented.

### BT-EX-004 — Resume execution
Implemented. Current baseline resume remains claim-gated and blocked by open downtime. Future quality/review blockers remain deferred.

### BT-EX-005 — Blocked is derived
Current implementation derives `BLOCKED` from runtime facts. In the current execution-core baseline, the primary shipped blocked path is downtime-related. Broader quality/review-driven block semantics remain deferred.

### BT-EX-006 — Report production
Implemented as delta reporting.

**Current implemented rule:** reporting is accepted only in `IN_PROGRESS`.  
The broader canonical possibility of reporting while paused remains deferred and is **not** current baseline truth.

### BT-EX-007 — Start / End downtime
Implemented.
- open downtime is represented as explicit start/end events
- end downtime does **not** auto-resume
- current flow returns to non-running state and requires explicit resume

### BT-EX-008 — Complete execution
Implemented.

**Current implemented rule:** completion is accepted from `IN_PROGRESS` in the current baseline.  
Broader canonical completion-from-`PAUSED` parity and quality/review/approved-effect gates remain deferred.

### BT-EX-009 — Close operation
Implemented as post-execution business closure.

Current implemented phase rule:
- close is allowed only on completed open records
- close authorization is intentionally hardened to `SUP` at API boundary for this pre-QC baseline

### BT-EX-010 — Reopen operation
Implemented as exceptional post-close action.

Current implemented baseline:
- requires `closure_status = CLOSED`
- requires reopen reason
- uses current narrowed authorization policy
- reopens to `OPEN` + controlled non-running runtime behavior
- current reopened runtime projection is `PAUSED`

## 8. Quantity truth

### BT-QTY-001 — Quantity is event-driven and delta-based
Implemented.

### BT-QTY-002 — Good and scrap are distinct
Implemented in the current baseline.

### BT-QTY-003 — Negative free-form correction is not allowed
Current baseline does not allow arbitrary negative corrective deltas.

### BT-QTY-004 — Accepted-good derivation
The richer canonical split between reported good and accepted good remains **designed but not implemented** in the current execution-core baseline.

## 9. Downtime truth

### BT-DT-001 — Downtime is an interval event pair
Implemented.

### BT-DT-002 — Downtime requires reason classification
Implemented in the current baseline path.

### BT-DT-003 — Open downtime blocks progression
Implemented now for:
- `resume_execution`
- `complete_execution`

### BT-DT-004 — Pause and downtime are different
Implemented behavior keeps them distinct.

## 10. Close / reopen truth

### BT-CL-001 — Close is not the same as complete
Implemented. `COMPLETED` and `CLOSED` are distinct.

### BT-CL-002 — Reopen is not a closure status
Implemented reopen representation uses:
- event `operation_reopened`
- `reopen_count`
- `last_reopened_at`
- `last_reopened_by`

### BT-CL-003 — Reopened records are controlled non-running
Implemented current behavior after reopen:
- `closure_status = OPEN`
- runtime behavior projects to `PAUSED`
- resume still requires a valid ownership path

## 11. Current read-model expectations

The current implemented backend baseline should expose at least:
- active operation / WO / PO context
- runtime status
- `closure_status`
- good/scrap totals
- remaining quantity
- downtime-open signal
- backend-derived `allowed_actions`
- reopen metadata
- close/reopen timestamps/actors where available

## 12. Must exist now vs later

### 12.1 Must exist now for the current implemented baseline
- claim / start / pause / resume / report / downtime / complete
- closure_status
- close / reopen foundation
- role/scope authorization
- auditability
- derived allowed actions
- single-active-claim safe default

### 12.2 Explicitly deferred from the current implemented baseline
- station session
- QC measurement / QC hold lifecycle
- exception/disposition lifecycle
- quality_status / review_status parity
- full dispatch parity
- full approved-effects model
- full canonical close/reopen policy matrix parity

## 13. Final implementation note

This document describes the **current implemented backend baseline**, not the full future canonical Station Execution domain.

The approved implementation strategy remains:
- keep execution-core stable
- add orthogonal dimensions incrementally
- do not reintroduce contradictory truths between code and docs

# Business Truth — Station Execution

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-22 | v3.1 | Previous current-implementation baseline. |
| 2026-04-23 | v4.0 | Approved transition design: deprecate claim target, introduce station-session ownership, and align to mode-neutral platform. |

Status: Authoritative business truth for the **approved next-step Station Execution design**.

## 1. Scope and interpretation

This document now describes the approved next-step design for Station Execution.
It also records key current-code divergence where needed.

### 1.1 Station Execution role in the platform
Station Execution is the current **discrete-first execution application**.
It is not the universal execution model for all manufacturing modes.

### 1.2 Current implementation divergence note
Current code still carries claim-centric behavior and does not yet implement first-class station session commands.
That is transition debt, not target truth.

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
The system must not permit silent destructive correction of execution history.

## 3. Aggregate boundary and ownership model

### BT-AGG-001 — Station Execution is session-owned
Station Execution write paths are owned by active execution session context, not by standalone claim.

### BT-AGG-002 — Execution session binds three different concerns
A valid active station execution session binds:
- authenticated user
- identified operator
- station context
- bound equipment/resource context where required

### BT-AGG-003 — Authenticated user is not identical to operator by default
The security principal and production actor must be modeled separately.

### BT-AGG-004 — Equipment is context, not identity
Equipment/resource context must never be treated as user identity.

## 4. Role intent in Station Execution

### OPR
Normal execution actor for:
- identify operator within allowed policy
- bind/select equipment where required
- start / pause / resume
- report production
- start/end downtime
- complete

### SUP
Supervisor-oriented owner for:
- close/reopen foundation under current phase policy
- monitoring and controlled intervention where later policy allows

### QCI / QAL
Remain quality-owned roles, not default execution mutation owners.

### ADM / OTS
Not normal shopfloor actors.
No broad production execution shortcut is implied by support/admin existence.

## 5. State dimensions

### 5.1 Runtime execution status
Current carrier vocabulary for Station Execution remains:
- `PLANNED`
- `IN_PROGRESS`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`
- `ABORTED`

This is still a discrete-first carrier, not the full universal cross-mode state shell.

### 5.2 Closure status
Orthogonal dimension:
- `OPEN`
- `CLOSED`

`CLOSED` blocks execution writes except authorized reopen flow.

### 5.3 Deferred orthogonal dimensions
- `quality_status`
- `review_status`
- fuller `dispatch_status`

## 6. Claim deprecation truth

### BT-CLAIM-001 — Claim is deprecated from the target model
Station Execution target design no longer uses `claim` as the long-term ownership primitive.

### BT-CLAIM-002 — Claim may exist only as transition compatibility
If current implementation still carries claim, it exists only as migration debt during the move to session-owned execution.

### BT-CLAIM-003 — Reopen/resume continuity must move to session-owned semantics
The target design preserves resumability through valid session/operator ownership paths rather than claim restoration.

## 7. Station session truth

### BT-SESSION-001 — Active execution write requires active station session
Target Station Execution writes require a valid active station session.

### BT-SESSION-002 — Operator identification is part of execution truth
The backend must know which operator is acting in the current station context.

### BT-SESSION-003 — Equipment binding is required where plant policy requires it
For single-machine/fixed-resource stations, equipment may be resolved by configuration.
For multi-resource stations, equipment binding must be explicit.

### BT-SESSION-004 — Backend derives effective execution actor/resource
Frontend does not authoritatively choose the effective execution actor/resource for mutation commands.
Backend resolves them from the active session.

## 8. Core execution lifecycle truth

### BT-EX-001 — Start execution
Start requires:
- valid active station session
- valid identified operator
- valid equipment context where required
- valid runtime/state guards
- no competing running execution under the governing station/resource policy

### BT-EX-002 — Pause execution
Implemented/target semantics remain supported.
Target ownership guard is session-owned rather than claim-owned.

### BT-EX-003 — Resume execution
Resume remains blocked by open downtime and later by quality/review gates where those dimensions exist.
Ownership is session-owned.

### BT-EX-004 — Blocked is derived
`BLOCKED` is derived from runtime facts.
Current strongest discrete path is downtime-related, but broader block semantics remain possible later.

### BT-EX-005 — Report production
Station Execution remains delta-based in the current app design.
Current target rule remains discrete-first:
- non-negative deltas only
- at least one positive delta required
- reporting during `IN_PROGRESS` by default

### BT-EX-006 — Start / End downtime
Downtime is represented as an interval event pair.
End downtime does not auto-resume.
Current flow returns to non-running state and requires explicit resume.

### BT-EX-007 — Complete execution
Completion requires valid execution session ownership, valid runtime state, and no open downtime.
Future quality/review gates remain orthogonal.

### BT-EX-008 — Close operation
Close remains post-execution business closure.
Current phase rule may remain supervisor-owned until broader policy context exists.

### BT-EX-009 — Reopen operation
Reopen is an exceptional post-close action.
Reopened records return to controlled non-running behavior and require valid ownership path to resume.

## 9. Quantity truth

### BT-QTY-001 — Quantity is event-driven and delta-based in Station Execution
Discrete-first Station Execution uses delta reporting.

### BT-QTY-002 — Good and scrap are distinct
Implemented and retained.

### BT-QTY-003 — Accepted-good derivation remains deferred in execution core
The richer canonical split between reported good and accepted good remains orthogonal and quality-adjacent.

### BT-QTY-004 — Platform neutrality warning
The broader platform must not assume count-only quantity forever.
Station Execution may remain count-oriented while platform abstractions later include UoM-aware, consumption/yield/byproduct-capable models.

## 10. Downtime truth

### BT-DT-001 — Downtime is an interval event pair
Implemented and retained.

### BT-DT-002 — Downtime requires backend master-data reason selection
Frontend must not derive or hardcode downtime reasons.
Backend master data is the source of truth.

### BT-DT-003 — Open downtime blocks progression
At minimum it blocks resume and complete in the current Station Execution design.

### BT-DT-004 — Pause and downtime are different
They remain distinct concepts.

## 11. Current read-model expectations

Station Execution reads should expose at least:
- active operation / WO / OP context
- runtime status
- closure_status
- good/scrap totals
- remaining quantity
- downtime-open signal
- backend-derived allowed_actions
- station session summary
- identified operator summary
- equipment/resource summary when relevant
- reopen metadata

## 12. Must exist now vs later

### 12.1 Must exist now for the approved next-step direction
- station session concept
- operator identification
- equipment binding where policy requires it
- start / pause / resume / report / downtime / complete
- closure_status
- close / reopen foundation
- role/scope authorization
- auditability
- derived allowed actions

### 12.2 Designed now, implemented progressively
- quality_status / review_status parity
- exception/disposition lifecycle
- accepted-good derivation
- full dispatch parity
- support-mode operational intervention flows
- process/batch execution applications on the shared core

# Station Execution Module Specification (vCurrent, Locked)

## 1) Purpose & Scope
Station Execution is the operator-facing execution module for deterministic, real-time control of operation execution at station scope.

Station Execution is responsible for:
- selecting work from station-scoped queue
- enforcing claim-before-execution behavior in operator flow
- triggering Clock On (start), quantity report, Pause/Resume, downtime start/end, and Clock Off (complete)
- surfacing closure-aware close/reopen foundation using backend-derived affordances
- reflecting backend-derived execution status after each action

Station Execution explicitly does not own:
- planning or scheduling decisions
- QC workflow decisions
- labor tracking
- routing orchestration beyond current execution updates

This specification is authoritative for vCurrent. Any future extension MUST conform to this contract.

## 2) User Roles & Responsibilities
### Operator
The operator is the only execution actor in Station Execution.

Operator responsibilities:
- claim an operation before execution actions
- Clock On to begin execution
- report produced quantities during execution
- pause/resume and downtime actions during execution
- Clock Off to finalize execution

### Supervisor (read-only reference)
Supervisor responsibilities are outside Station Execution write control. Supervisors monitor execution state from other views and do not replace operator-triggered Clock On/Clock Off semantics.

### QC (not part of execution)
QC is not part of Station Execution transitions in vCurrent. QC authority is handled outside this module and MUST NOT gate base execution transitions in this phase.

## 3) Execution Lifecycle Overview
Execution lifecycle is locked and event-driven:

PLANNED (UI label: Pending)
  -> Clock On
IN_PROGRESS
  -> Pause / Resume / Downtime controls (backend-guarded runtime transitions)
  -> Clock Off
COMPLETED / ABORTED

Event mapping:
- Clock On -> OP_STARTED
- Clock Off -> OP_COMPLETED

Lifecycle truth is backend-derived from immutable execution events. UI renders state and triggers intents only.

## 4) Station Execution UI Behavior (Operator View)
### Claim
Visibility:
- claim action is shown when selected queue item is not currently claimed by operator

Enable/disable rules:
- claim action is enabled when operation is claimable at station scope
- release action is enabled when claim owner is current operator

Payload semantics:
- claim uses station claim API with optional reason/duration defaults handled server-side
- release includes explicit operator release reason

Expected UI transitions:
- queue claim state updates to mine/other/none from backend response
- execution actions become available only when claim state is mine

### Clock On
Visibility:
- Clock On is visible when operation is execution-pending (backend PLANNED; UI may also accept PENDING compatibility in client)

Enable/disable rules:
- enabled only when claim state is mine
- disabled when claim state is not mine

Payload semantics:
- operator_id = authenticated user id
- started_at may be backend default if omitted

Expected UI transitions:
- operation transitions to IN_PROGRESS after successful response
- queue and detail pane refresh from backend
- next available execution controls become visible

### Report Quantity
Visibility:
- visible only when operation status is IN_PROGRESS

Enable/disable rules:
- enabled only when claim state is mine
- disabled when claim state is not mine

Payload semantics:
- good_qty and scrap_qty are operator-entered execution values
- operator_id may be included by client contract

Expected UI transitions:
- backend records quantity report event
- derived quantities and progress refresh from backend

### Clock Off
Visibility:
- visible only when operation status is IN_PROGRESS

Enable/disable rules:
- enabled only when claim state is mine
- disabled when claim state is not mine

Payload semantics:
- operator_id = authenticated user id
- completed_at = client timestamp or backend default when omitted

Expected UI transitions:
- operation transitions to COMPLETED on success
- Clock Off disappears because operation is no longer IN_PROGRESS
- completed operation leaves station queue view (queue is execution-active scope)
- downstream views (including Gantt) reflect completion from backend-derived state

## 5) Backend Interaction Semantics
Station Execution uses backend endpoints as execution command surfaces.

Conceptual responsibilities:
- read operation detail and station queue projections
- enforce claim ownership for execution actions
- apply status guards for start/report/complete
- append immutable execution events and update projection fields

Source-of-truth rules:
- backend is the single source of truth
- event history is authoritative for lifecycle semantics
- snapshot status/quantities are projections derived and maintained by backend services

Deterministic guards:
- claim ownership required for execution write actions
- Clock On valid only from PLANNED execution-pending state
- Clock Off valid only from IN_PROGRESS
- one running operation per station/operator
- idempotency enforced for repeated start/complete attempts

## 6) Error Handling Rules
HTTP 403 semantics:
- means authorization/ownership failure for execution action (typically claim ownership missing)
- operator sees claim-required feedback and must claim before retry

HTTP 409 semantics:
- means lifecycle conflict with current operation state
- examples: start from non-pending state, complete from non-in-progress state, repeat complete
- operator sees explicit conflict feedback and must refresh/continue with valid next action

Why explicit rejection is required:
- prevents silent state drift
- preserves deterministic lifecycle guarantees
- preserves audit-grade execution trail integrity

## 7) Invariants & Guardrails
The following invariants are mandatory:
- execution write actions require claim ownership
- Clock On and Clock Off are explicit operator actions
- no feature may bypass or auto-trigger Clock On/Clock Off
- lifecycle transitions remain PLANNED -> IN_PROGRESS -> COMPLETED/ABORTED
- one running operation per station/operator is enforced by backend
- repeated completion attempts do not create duplicate OP_COMPLETED events
- backend enforcement takes precedence over any UI state

## 8) Explicit Non-Goals
Station Execution intentionally excludes:
- QC gating within execution transitions
- labor time accounting
- APS or scheduling logic
- advanced routing progression control beyond current behavior

The following are implemented as foundation but remain partial versus full canonical target:
- close_operation / reopen_operation with closure-aware FE support
- current phase-close authorization is intentionally narrow (SUP-only at API boundary)

## 9) Extension Guidance (Forward-Looking)
QC v1 layering guidance:
- QC can consume execution state and events but MUST NOT redefine Clock On/Clock Off lifecycle semantics
- QC rules must be added as separate domain behavior, not by mutating core execution state machine

Analytics/OEE guidance:
- analytics should consume execution events and projections as read models
- analytics MUST NOT write back lifecycle transitions or override execution guards

Extension warning:
- all extensions must adapt to locked execution semantics
- changing execution semantics requires a new versioned lifecycle contract and explicit approval

## 10) Relationship to Other Modules
Gantt:
- Gantt reflects backend-derived execution status and timing outcomes
- Gantt does not own execution authority in this module

Planning / Work Order management:
- planning and work order modules are upstream context providers
- Station Execution consumes released work context; it does not perform planning decisions

QC:
- QC is downstream or adjacent to execution in this phase
- QC workflows may observe execution completion but are not embedded in Clock On/Clock Off logic

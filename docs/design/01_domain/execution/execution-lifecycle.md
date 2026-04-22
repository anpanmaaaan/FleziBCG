# MES Execution Lifecycle (Locked)

## 1) Purpose
This document freezes the MES execution lifecycle behavior for vCurrent.

This lifecycle is LOCKED. Changes to lifecycle semantics are not allowed in this phase.

## 2) Execution Lifecycle Overview
Lifecycle transitions (textual state diagram):

PLANNED (UI: Pending)
  -> Clock On
IN_PROGRESS
  -> Pause
PAUSED
  -> Resume
IN_PROGRESS
  -> Start Downtime
BLOCKED
  -> End Downtime
PAUSED
  -> Resume
IN_PROGRESS
  -> Clock Off
COMPLETED / ABORTED

Note: “Pending” is a UI representation for operators; backend enum remains PLANNED.

Execution transitions are event-driven. Clock On records OP_STARTED and Clock Off records OP_COMPLETED. Pause/Resume and Downtime start/end are also implemented runtime controls in the current core baseline. Lifecycle state is derived from execution events and enforced by backend guards.

Close/Reopen are implemented as post-execution closure controls in the current core baseline:
- `close_operation` transitions `closure_status` to `CLOSED` on completed records
- `reopen_operation` transitions `closure_status` back to `OPEN` and re-enters controlled non-running runtime behavior (`PAUSED` projection)

## 3) Operator Responsibilities
Operator responsibilities in vCurrent are strictly:
- Claim operation
- Clock On
- Execute work
- Pause / Resume execution
- Start / End downtime
- Clock Off

Operators do not have QC decision authority at this stage.

Close/Reopen are post-execution business closure actions and are not ordinary runtime operator controls.

## 4) Backend Source of Truth
Backend is the single source of truth.

Execution state is derived from immutable execution events. Persisted database status fields are projections and must remain consistent with event history. Backend enforcement always governs validity of execution actions.

## 5) Guardrails (Strict)
The following guardrails are mandatory and locked:
- Claim ownership is required for Clock On.
- Claim ownership is required for runtime execution writes (Clock Off, Pause/Resume, Report, Downtime).
- Only one running operation per station/operator is allowed.
- Clock On is valid only from PLANNED.
- Clock Off is valid only from IN_PROGRESS.
- Resume is valid only from PAUSED and when blockers allow.
- End Downtime does not auto-resume execution.
- Idempotency is enforced: duplicate OP_STARTED or OP_COMPLETED side effects are not allowed.
- `closure_status = CLOSED` blocks execution writes until a valid reopen path succeeds.

## 6) Explicit Non-Goals
The execution lifecycle does not include:
- QC gating inside execution transitions
- Labor accounting
- Automatic routing advancement beyond existing behavior
- APS or scheduling logic inside execution transitions

Still deferred for this pre-QC / pre-review core baseline:
- quality_status / review_status command blocking parity
- submit_qc_measurement workflow and disposition lifecycle
- full canonical close/reopen approval matrix parity

## 7) Extension Policy
Future features (for example QC, Pause, Analytics) are allowed only as layered extensions.

Future features must not:
- Change the meaning of Clock On or Clock Off
- Change the execution state machine semantics

Any change to execution semantics requires:
- A new lifecycle change document
- Versioning
- Explicit approval before implementation

## DO NOT BREAK EXECUTION RULES
The following rules are a contractual guardrail for all future development:
- Clock On and Clock Off semantics are FINAL for vCurrent.
- Execution lifecycle transitions MUST remain: PLANNED -> IN_PROGRESS -> COMPLETED / ABORTED.
- Quality, labor, analytics, and scheduling are layered on top of execution, not inside execution.
- No feature is allowed to bypass Clock On or Clock Off.
- No feature is allowed to auto-trigger Clock On or Clock Off.
- Backend enforcement always takes precedence over UI behavior.

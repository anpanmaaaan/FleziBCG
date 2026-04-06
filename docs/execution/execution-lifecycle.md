# MES Execution Lifecycle (Locked)

## 1) Purpose
This document freezes the MES execution lifecycle behavior for vCurrent.

This lifecycle is LOCKED. Changes to lifecycle semantics are not allowed in this phase.

## 2) Execution Lifecycle Overview
Lifecycle transitions (textual state diagram):

PLANNED (UI: Pending)
  -> Clock On
IN_PROGRESS
  -> Clock Off
COMPLETED / ABORTED

Execution transitions are event-driven. Clock On records OP_STARTED and Clock Off records OP_COMPLETED. Lifecycle state is derived from execution events and enforced by backend guards.

## 3) Operator Responsibilities
Operator responsibilities in vCurrent are strictly:
- Claim operation
- Clock On
- Execute work
- Clock Off

Operators do not have QC decision authority at this stage.

## 4) Backend Source of Truth
Backend is the single source of truth.

Execution state is derived from immutable execution events. Persisted database status fields are projections and must remain consistent with event history. Backend enforcement always governs validity of execution actions.

## 5) Guardrails (Strict)
The following guardrails are mandatory and locked:
- Claim ownership is required for Clock On.
- Claim ownership is required for Clock Off.
- Only one running operation per station/operator is allowed.
- Clock On is valid only from PLANNED.
- Clock Off is valid only from IN_PROGRESS.
- Idempotency is enforced: duplicate OP_STARTED or OP_COMPLETED side effects are not allowed.

## 6) Explicit Non-Goals
The execution lifecycle does not include:
- Pause / Resume
- QC gating inside execution transitions
- Labor accounting
- Automatic routing advancement beyond existing behavior
- APS or scheduling logic inside execution transitions

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

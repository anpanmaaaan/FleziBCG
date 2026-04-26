# Approval and Separation of Duties Model

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Clarified that execution/session changes do not weaken approval/SoD. |

Status: Canonical approval/SoD note.

## 1. Core rule

Requester must never equal decider, including under impersonation.

## 2. Valid governed action rule

A governed action is valid only if:
- RBAC allows the action
- approval policy allows the acting role
- SoD remains satisfied

## 3. Execution implication

Introducing operator identification and execution sessions does not bypass approval or SoD.
Where a later workflow requires governed intervention, operator/session context is additional audit context, not a substitute for governance.

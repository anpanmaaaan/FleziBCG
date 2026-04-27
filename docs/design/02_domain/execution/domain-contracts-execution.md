# Domain Contract — Execution

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Replaced claim-centric contract with unified execution/session-oriented contract. |

Status: Canonical execution domain contract.

## 1. Purpose

This document defines canonical execution domain vocabulary and invariants at platform level.

## 2. Core entities

- `production_request`
- `execution_run`
- `execution_step`
- `execution_session`
- `resource_context`
- `personnel_context`
- `quantity_record`
- `downtime_interval`

## 3. Station Execution specialization

Station Execution is a discrete-first specialization that maps:
- production request -> WO/PO context
- execution step -> operation context
- execution session -> station session

## 4. Canonical dimensions

### Runtime status
- `PLANNED`
- `IN_PROGRESS`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`
- `ABORTED`

### Closure status
- `OPEN`
- `CLOSED`

## 5. Canonical event intent

- `execution_session_opened`
- `operator_identified`
- `equipment_bound`
- `execution_started`
- `execution_paused`
- `execution_resumed`
- `production_reported`
- `downtime_started`
- `downtime_ended`
- `execution_completed`
- `operation_closed`
- `operation_reopened`

## 6. Invariants

- execution facts are append-only
- closed records cannot mutate except through authorized reopen flow
- execution write paths require valid execution ownership context
- backend derives effective execution actor/resource context
- claim is not a target-state invariant

# Station Execution Command and Event Contracts
## Current implemented backend baseline

Status: **Implementation-aligned contract note for the current backend baseline**  
Scope: **Station Execution Core / Pre-QC / Pre-Review**

This file distinguishes:
- canonical names we want to keep stable
- what is actually implemented now
- what remains deferred

## 1. Implemented command set now

Implemented backend command paths:
- `claim_operation`
- `start_execution`
- `pause_execution`
- `resume_execution`
- `report_production`
- `start_downtime`
- `end_downtime`
- `complete_execution`
- `close_operation`
- `reopen_operation`

## 2. Deferred command set
Not implemented in the current backend baseline:
- `open_station_session`
- `close_station_session`
- `submit_qc_measurement`
- `raise_exception`
- `record_disposition_decision`

## 3. Implemented event intent now

Canonical event intent for implemented flows:
- `operation_claimed`
- `execution_started`
- `execution_paused`
- `execution_resumed`
- `production_reported`
- `downtime_started`
- `downtime_ended`
- `execution_completed`
- `operation_closed_at_station`
- `operation_reopened`

### Implementation-phase note
Current backend still carries mixed legacy/internal event names for some execution events. This is a known contract debt. Canonical names above remain the business-facing target vocabulary.

## 4. Current payload / contract truths

### 4.1 `report_production`
Current implemented behavior:
- delta only
- non-negative values only
- at least one positive delta required
- current baseline accepts reporting only while runtime status is effectively `IN_PROGRESS`

### 4.2 `close_operation`
Current implemented behavior:
- optional note payload
- closes only completed open record
- current phase authorization is hardened at API boundary to `SUP`

### 4.3 `reopen_operation`
Current implemented behavior:
- reopen reason required
- increments/stamps reopen metadata server-side
- reopens into controlled non-running runtime behavior (`PAUSED` projection)

## 5. Reopen metadata
Server-derived facts:
- `reopen_count`
- `last_reopened_at`
- `last_reopened_by`

## 6. Error-family note
Current implementation already uses machine-readable `STATE_*` style conflicts for many core execution guards, including `STATE_CLOSED_RECORD`.

## 7. Deferred contract areas
Still deferred from the current baseline:
- full command/event envelope standardization
- idempotency envelope parity for every command
- optimistic concurrency envelope parity for every command
- QC and disposition contracts
- approved-effects event/output parity

# Station Execution Command and Event Contracts

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Reworked contracts for session-owned execution and claim deprecation. |

Status: Canonical Station Execution command/event contract for the approved next-step design.

## 1. Target command set

### Session/context commands
- `open_station_session`
- `identify_operator`
- `bind_equipment`
- `close_station_session`

### Execution commands
- `start_execution`
- `pause_execution`
- `resume_execution`
- `report_production`
- `start_downtime`
- `end_downtime`
- `complete_execution`
- `close_operation`
- `reopen_operation`

## 2. Transition note

`claim_operation` and related claim semantics are deprecated from the target model.
They may continue to exist temporarily in current code as compatibility debt during migration.

## 3. Canonical event intent

- `station_session_opened`
- `operator_identified_at_station`
- `equipment_bound_to_station_session`
- `execution_started`
- `execution_paused`
- `execution_resumed`
- `production_reported`
- `downtime_started`
- `downtime_ended`
- `execution_completed`
- `operation_closed_at_station`
- `operation_reopened`
- `station_session_closed`

## 4. Payload/contract truths

### `start_execution`
Backend resolves effective operator/resource context from the active station session.

### `report_production`
Body remains discrete-first for Station Execution:
- `good_delta`
- `scrap_delta`
- optional note/comment under policy

### `start_downtime`
Body:
- `reason_code`
- optional comment when policy requires

### `reopen_operation`
Body:
- `reason`

## 5. Error-family expectations

- `STATE_INVALID_TRANSITION`
- `STATE_CLOSED_RECORD`
- `SESSION_REQUIRED`
- `OPERATOR_IDENTIFICATION_REQUIRED`
- `EQUIPMENT_BINDING_REQUIRED`
- `FORBIDDEN`
- `REASON_CODE_INVALID`

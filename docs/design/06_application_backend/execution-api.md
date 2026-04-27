# Execution API

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Reworked API design for session-owned execution and claim deprecation. |

Status: Domain API design aligned to the approved next-step Station Execution design.

## 1. Purpose

This document specifies the execution session/context APIs and execution mutation/read APIs.

## 2. Session/context endpoints

### POST /execution/stations/{station_id}/session/open
Effects:
- validates station/resource access
- creates or restores active session context

### POST /execution/stations/{station_id}/session/identify-operator
Body:
- operator_code or equivalent identifier
Effects:
- validates operator and linkage policy
- updates active station session

### POST /execution/stations/{station_id}/session/bind-equipment
Body:
- equipment_id or equipment_code
Effects:
- validates equipment/resource policy
- updates active station session

### POST /execution/stations/{station_id}/session/close
Effects:
- closes session when no active work would be orphaned

### GET /execution/stations/{station_id}/session
Returns:
- active session summary
- identified operator summary
- bound equipment/resource summary where relevant

## 3. Execution command endpoints

### POST /execution/operations/{operation_id}/start
Effects:
- validates active station session and start guards
- appends `execution_started`

### POST /execution/operations/{operation_id}/pause
Effects:
- validates active station session and pause guards
- appends `execution_paused`

### POST /execution/operations/{operation_id}/resume
Effects:
- validates no open downtime and active session ownership path
- appends `execution_resumed`

### POST /execution/operations/{operation_id}/report-production
Body:
- `good_delta`
- `scrap_delta`
- optional note/comment as policy allows

### POST /execution/operations/{operation_id}/start-downtime
Body:
- `reason_code`
- optional comment when policy requires

### POST /execution/operations/{operation_id}/end-downtime

### POST /execution/operations/{operation_id}/complete

### POST /execution/operations/{operation_id}/close
Current phase note:
- SUP-owned path in the current next-step design unless later policy broadens it

### POST /execution/operations/{operation_id}/reopen
Body:
- `reason`

## 4. Read endpoints

- `GET /execution/stations/{station_id}/queue`
- `GET /execution/operations/{operation_id}`
- `GET /execution/operations/{operation_id}/history`
- `GET /execution/downtime-reasons`

## 5. Response expectations

Execution reads should include where relevant:
- runtime status
- closure_status
- quantity totals
- open downtime signal
- allowed_actions
- station session summary
- identified operator summary
- equipment/resource summary
- reopen metadata

## 6. Key error families

- `OPERATION_NOT_FOUND`
- `STATE_INVALID_TRANSITION`
- `STATE_CLOSED_RECORD`
- `SESSION_REQUIRED`
- `OPERATOR_IDENTIFICATION_REQUIRED`
- `EQUIPMENT_BINDING_REQUIRED`
- `DOWNTIME_ALREADY_OPEN`
- `DOWNTIME_NOT_OPEN`
- `REASON_CODE_INVALID`
- `FORBIDDEN`

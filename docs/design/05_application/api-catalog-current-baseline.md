# API Catalog — Current Baseline and Approved Next Additions

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Split current baseline from approved next execution/session additions. |

Status: Transition API inventory note.

## 1. Foundation API families

### Auth/session
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/logout-all`
- `GET /auth/me`
- `GET /auth/sessions`
- `POST /auth/sessions/{session_id}/revoke`

### Users/access
- `GET /users`
- `POST /users/invite`
- `POST /users/{user_id}/activate`
- `POST /users/{user_id}/deactivate`
- `POST /users/{user_id}/lock`
- `POST /users/{user_id}/unlock`
- `POST /access/role-assignments`
- `POST /access/scope-assignments`
- `POST /approvals`
- `POST /approvals/{approval_id}/decide`

## 2. Execution API families

### Current code-oriented baseline families
- `POST /execution/operations/{operation_id}/start`
- `POST /execution/operations/{operation_id}/pause`
- `POST /execution/operations/{operation_id}/resume`
- `POST /execution/operations/{operation_id}/report-production`
- `POST /execution/operations/{operation_id}/start-downtime`
- `POST /execution/operations/{operation_id}/end-downtime`
- `POST /execution/operations/{operation_id}/complete`
- `POST /execution/operations/{operation_id}/close`
- `POST /execution/operations/{operation_id}/reopen`
- `GET /execution/stations/{station_id}/queue`
- `GET /execution/operations/{operation_id}`
- `GET /execution/operations/{operation_id}/history`
- `GET /execution/downtime-reasons`

### Approved next additions for cutover
- `POST /execution/stations/{station_id}/session/open`
- `POST /execution/stations/{station_id}/session/identify-operator`
- `POST /execution/stations/{station_id}/session/bind-equipment`
- `POST /execution/stations/{station_id}/session/close`
- `GET /execution/stations/{station_id}/session`

## 3. Quality API families
- `GET /quality/operations/{operation_id}/requirements`
- `GET /quality/operations/{operation_id}/template`
- `POST /quality/operations/{operation_id}/measurements`
- `GET /quality/operations/{operation_id}/result`
- `POST /quality/reviews/{review_id}/disposition` later

## 4. Important transition note

Historical claim routes may still exist during migration, but claim is deprecated from the target design.
Keep this file aligned to the actual public surface as the cutover proceeds.

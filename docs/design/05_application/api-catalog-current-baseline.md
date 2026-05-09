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
- `GET /quality/gates/definitions`
- `POST /quality/gates/definitions`
- `POST /quality/gates/instances/open`
- `POST /quality/measurements`
- `GET /quality/holds`
- `GET /quality/deviations`
- `POST /quality/holds/{hold_id}/deviations`
- `POST /quality/deviations/{deviation_request_id}/resolve`
- `GET /quality/nonconformances`
- `POST /quality/nonconformances`
- `POST /quality/reviews/{review_id}/disposition`

## 3.1 Quality-to-execution progression gate baseline

- Active quality hold blocks execution progression commands:
	- resume
	- complete
- Allowed-actions projection must suppress blocked commands when hold is active.
- `REQUIRE_RECHECK` does not count as hold release:
	- active hold remains in effect
	- execution progression remains blocked until a release-like disposition resolves the hold

## 3.2 Quality quantity-effect response baseline

- `POST /quality/measurements` evaluates submitted values against backend-owned requirement/template items and spec limits:
	- request measurement rows are operator-observed facts only (`item_code`, `measured_value`)
	- unsupported `item_code` values are rejected server-side
	- client-supplied threshold overrides do not control pass/fail and are rejected by the request contract
	- strict completeness: all required template items must be present in a submit request
- `POST /quality/measurements` response includes backend-derived quantity effects:
	- `accepted_good_release_qty`
	- `held_pending_good_qty`
- `POST /quality/reviews/{review_id}/disposition` response includes backend-derived quantity effects:
	- `accepted_good_release_qty`
	- `held_pending_good_qty`
- Quantity effects are derived server-side from quality outcome/disposition and current reported-good context.

## 3.3 Quality gate/admin baseline

- Gate definition create currently accepts `gate_type=PRE_ACCEPTANCE`.
- Gate open, deviation resolve, and disposition decision are approval-governed actions (`APPROVE` permission).
- Frontend quality admin pages must send intent only; backend remains source of truth for gate validity, hold lifecycle, and quality outcome.

## 4. Important transition note

Historical claim routes may still exist during migration, but claim is deprecated from the target design.
Keep this file aligned to the actual public surface as the cutover proceeds.

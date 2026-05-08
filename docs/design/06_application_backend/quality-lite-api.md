# Quality Lite API

## History

| Date | Version | Change |
|---|---|---|
| 2026-05-08 | v2.1 | Synced endpoint inventory to live `/api/v1/quality/*` routes and current quality governance boundaries. |
| 2026-04-23 | v2.0 | Minor alignment to session-owned execution context. |

Status: Backend application API note.

## Scope
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

## Alignment note

Quality endpoints use operation/execution context and must remain compatible with session-owned execution and later broader batch/lot contexts.

## Contract notes (current baseline)

- Backend owns quality truth (evaluation outcome, hold behavior, accepted-good release semantics).
- `POST /quality/measurements` accepts operator-observed facts only (`item_code`, `measured_value`) and rejects threshold override fields.
- Strict completeness is active for required template items during measurement submit.
- `REQUIRE_RECHECK` is not a hold-release action and does not unblock execution progression.
- Gate definition create currently accepts `gate_type=PRE_ACCEPTANCE` only.

## Authz notes (current baseline)

- Authenticated identity required:
	- requirements read
	- holds/deviations/nonconformance list
	- measurement submit
	- nonconformance create
	- deviation request create
- `APPROVE` permission required:
	- gate definition create
	- gate instance open
	- deviation resolve
	- disposition decision

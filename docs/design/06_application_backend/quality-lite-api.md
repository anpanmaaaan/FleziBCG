# Quality Lite API

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Minor alignment to session-owned execution context. |

Status: Backend application API note.

## Scope
- `GET /quality/operations/{operation_id}/requirements`
- `GET /quality/operations/{operation_id}/template`
- `POST /quality/operations/{operation_id}/measurements`
- `GET /quality/operations/{operation_id}/result`

## Alignment note

Quality endpoints should use the operation/execution context but must remain compatible with session-owned execution and later broader batch/lot contexts.

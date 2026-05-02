# Canonical Error Code Registry

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.2 | Removed CLAIM_API_DISABLED after legacy claim routes were deleted in H14B/H08I-B cleanup. |
| 2026-05-02 | v1.1 | Added CLAIM_API_DISABLED for P0-C-08H12B claim API runtime disablement. |
| 2026-05-01 | v1.0 | Added approved StationSession command-guard error set for P0-C-08C controlled batch. |

## Scope

This registry records machine-readable backend error codes that are approved for governed runtime use.

Error-code format rule:
- `UPPER_SNAKE_CASE`

## StationSession Command Guard Errors

Status for this slice:
- `APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD`

These codes are approved for P0-C-08C execution command guard enforcement.
They may be promoted to broader cross-slice canonical platform status in a later registry pass.

| Error Code | HTTP Status | Meaning | Status |
|---|---:|---|---|
| `STATION_SESSION_REQUIRED` | 409 | No StationSession exists for the resolved tenant + station command context. | APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD |
| `STATION_SESSION_CLOSED` | 409 | A StationSession exists for the resolved tenant + station, but it is not OPEN. | APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD |
| `STATION_SESSION_STATION_MISMATCH` | 409 | The resolved OPEN StationSession context does not match the operation station context. | APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD |
| `STATION_SESSION_OPERATOR_MISMATCH` | 403 | The resolved OPEN StationSession operator does not match the command actor/operator context. | APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD |
| `STATION_SESSION_TENANT_MISMATCH` | 404 | The resolved StationSession context is outside the caller tenant boundary. | APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD |

## Notes

- `STATION_SESSION_NOT_AUTHORIZED` is not approved in P0-C-08C because the current command-guard slice can express the required behavior with the five approved codes above.
- `STATION_SESSION_TENANT_MISMATCH` must preserve non-leaking cross-tenant behavior. Current approved HTTP mapping for this slice is `404`.
- Success response shapes are unchanged by this registry entry.

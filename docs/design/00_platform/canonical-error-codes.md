# Canonical Error Codes

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.2 | Removed CLAIM_API_DISABLED after legacy claim routes were deleted in H14B/H08I-B cleanup. |
| 2026-05-02 | v1.1 | Added CLAIM_API_DISABLED for P0-C-08H12B claim API runtime disablement. |
| 2026-05-01 | v1.0 | Added approved StationSession command-guard error codes for P0-C-08C. |

## StationSession Guard Codes

### `STATION_SESSION_REQUIRED`
- Status: `APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD`
- HTTP status: `409`
- Meaning: the command requires an OPEN StationSession for the resolved tenant + station context, but none exists.

### `STATION_SESSION_CLOSED`
- Status: `APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD`
- HTTP status: `409`
- Meaning: a StationSession exists for the resolved tenant + station context, but it is CLOSED or otherwise non-OPEN.

### `STATION_SESSION_STATION_MISMATCH`
- Status: `APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD`
- HTTP status: `409`
- Meaning: the operator has an OPEN StationSession, but it is bound to a different station than the target operation.

### `STATION_SESSION_OPERATOR_MISMATCH`
- Status: `APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD`
- HTTP status: `403`
- Meaning: the StationSession at the target station is OPEN, but its operator context does not match the command actor/operator context.

### `STATION_SESSION_TENANT_MISMATCH`
- Status: `APPROVED_FOR_P0_C_08_STATION_SESSION_GUARD`
- HTTP status: `404`
- Meaning: a StationSession exists at the target station but outside the caller tenant boundary; the runtime must not leak cross-tenant existence details.

## Slice Boundary

- `STATION_SESSION_*` codes approved only for P0-C-08C subset command guard enforcement.
- No event rename, success payload change, or projection redesign is implied by these codes.

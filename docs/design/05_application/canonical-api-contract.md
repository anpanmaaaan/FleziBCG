# Canonical API Contract

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Added target-state contract principles for execution session APIs. |

Status: Canonical API contract note.

## Rules
- request/response contracts use explicit schemas
- backend returns codes, not translated business labels
- datetimes use ISO 8601
- public contract changes require architecture/contract handling
- execution mutation contracts must make session/context requirements explicit where relevant

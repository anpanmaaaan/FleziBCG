# Integration API Boundary

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Minor strengthening of canonical-boundary language. |

Status: Integration API boundary note.

## Rule

Integration-facing APIs/adapters must normalize external semantics into canonical backend contracts.
They must not push ERP/PLC/historian semantics directly into frontend-owned business truth.

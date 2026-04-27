# Hardening Baseline Summary — FleziBCG

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-27 | v1.0 | Rebuilt latest hardening baseline summary for downloadable design pack. |

## Status

**Baseline summary.**

The authoritative baseline after review is:

```text
Latest consolidated design package 2026-04-26
+ Hardening v1
+ Hardening Housekeeping v1.1
+ Source Code Audit Response
+ CODING_RULES.md v2.0
```

## Decisions Preserved

- Backend is source of truth.
- Frontend is UX/navigation only.
- Persona is not permission.
- JWT proves identity only.
- AI is advisory by default.
- Digital Twin is derived state.
- ERP is not replaced by FleziBCG.
- Acceptance Gate is canonical; LAT/Pre-LAT are display labels only.
- Backflush is cross-domain.
- Station Execution target is session-owned; claim is migration debt.

## Hardening Decisions

| Area | Decision |
|---|---|
| API/error | `/api/v1` + RFC 9457-compatible Problem Details with FleziBCG `code` and `correlation_id`. |
| Event boundary | Internal event schema remains FleziBCG canonical; external/brokered events CloudEvents-compatible later. |
| Tenant isolation | Repository tenant filtering mandatory; schema RLS-ready; PostgreSQL RLS P1 hardening unless approved earlier. |
| Timezone | UTC persisted instants; plant timezone for shift/calendar/reporting; i18n keys for UI text. |
| OEE | Deterministic formula before AI explanations. |
| AI | Observe/explain/predict/recommend only; no autonomous mutation. |
| Cache/broker | DB/projection-first P0; Redis/Kafka optional later. |
| Backend stack | Current sync stack preserved for P0-A; async migration requires separate ADR. |
| Migration | Alembic is canonical; no `create_all()` for production schema management. |

## Next Step

Proceed with P0-A Foundation Database implementation prompt.

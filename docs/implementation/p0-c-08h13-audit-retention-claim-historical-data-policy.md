# P0-C-08H13 Audit Retention Decision / Claim Historical Data Policy

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Defined retention and removal policy for legacy claim model, tables, and audit history after claim API runtime disablement. |

---

## 1. Executive Summary

As of H12B, the three legacy claim-only API endpoints (`POST .../claim`, `POST .../release`, `GET .../claim`) return HTTP 410 `CLAIM_API_DISABLED`. The claim service, `OperationClaim` model, `OperationClaimAuditLog` model, and their underlying PostgreSQL tables (`operation_claims`, `operation_claim_audit_logs`) remain intact. No historical audit rows have been deleted.

This H13 document:

1. Maps all claim data artifacts and their current role.
2. Evaluates audit retention options.
3. Establishes the environment/data assumption for this project.
4. Recommends the retention and removal policy.
5. Proposes the exact H14–H17 removal sequence.
6. Defines stop conditions for destructive table drop.

**Final verdict:** `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED`

---

## 2. Scope Reviewed

### Source files inspected

| File | Purpose |
|---|---|
| `backend/app/models/station_claim.py` | `OperationClaim` and `OperationClaimAuditLog` ORM models |
| `backend/app/services/station_claim_service.py` | Full claim lifecycle service — all functions intact |
| `backend/app/api/v1/station.py` | 3 claim routes disabled with `_raise_claim_api_disabled()` |
| `backend/app/schemas/station.py` | `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` schemas |
| `backend/scripts/migrations/0009_station_claims.sql` | Original DDL for `operation_claims` and `operation_claim_audit_logs` |
| `backend/alembic/versions/` | 3 Alembic files: `0001_baseline`, `0002_add_refresh_tokens`, `0003_routing_operation_extended_fields` |
| `frontend/src/app/api/stationApi.ts` | Deprecated `claim()`, `release()`, `getClaim()` stubs + `ClaimSummary`, `QueueClaimState`, `ClaimResponse` types |
| `frontend/src/app/api/index.ts` | Re-exports `QueueClaimState`, `ClaimSummary`, `ClaimResponse` |
| `backend/tests/test_claim_api_deprecation_lock.py` | 5 tests — 3 assert 410+`CLAIM_API_DISABLED`, 2 assert non-deprecated paths |
| `backend/tests/test_claim_single_active_per_operator.py` | 6 service-level tests — directly call `claim_operation()` |
| `backend/tests/test_release_claim_active_states.py` | 14 service-level tests — directly call `release_operation_claim()`, `get_operation_claim_status()` |
| `backend/tests/test_execution_route_claim_guard_removal.py` | 12 tests — teardown uses `OperationClaim`, `OperationClaimAuditLog` |
| `backend/tests/test_operation_detail_allowed_actions.py` | Large suite — teardown uses `OperationClaim`, `OperationClaimAuditLog` |
| `backend/tests/test_operation_status_projection_reconcile.py` | Uses `OperationClaim`, `OperationClaimAuditLog` in teardown |
| `backend/tests/test_reopen_resumability_claim_continuity.py` | Tests reopen without claim restoration |
| `backend/tests/test_reopen_resume_station_session_continuity.py` | Tests StationSession continuity over reopen |
| `backend/tests/test_reopen_operation_claim_continuity_hardening.py` | 13 tests — hardening |

### Prior implementation reports reviewed

- `docs/implementation/p0-c-08h12b-claim-api-runtime-disablement-implementation-report.md`
- `docs/implementation/p0-c-08h11b-reopen-claim-compatibility-retirement-implementation-report.md`
- `docs/implementation/p0-c-08h10-backend-queue-claim-payload-null-only-implementation-report.md`

---

## 3. Hard Mode Gate Evidence

### Design Evidence Extract

| Fact | Evidence | Confirmed |
|---|---|---|
| StationSession is target ownership truth | `station-session-ownership-contract.md` | ✅ |
| Claim APIs are runtime-disabled (HTTP 410) | H12B — `_raise_claim_api_disabled()` in `station.py` | ✅ |
| Queue claim payload is null-only | H10 — `"claim": None` always returned | ✅ |
| Reopen no longer restores claim | H11B — `_restore_claim_continuity_for_reopen` deleted | ✅ |
| Claim service/model/table are legacy remnants | No active route calls service functions after H12B | ✅ |
| `CLAIM_EXPIRED` still produced via queue loop | `_expire_claim_if_needed()` still active in `get_station_queue` | ✅ |
| Historical audit data must not be silently deleted | Governance policy — doc-tracked removal required | ✅ |
| H13 is governance/policy only — no code | Task scope is review/contract only | ✅ |
| User goal is clean hard-removal of claim tables/code | Explicit user statement | ✅ |
| DB migration/drop requires explicit retention verdict | This document provides that verdict | ✅ |
| Project is dev/pre-production baseline | Evidence: no migration file drops tables; Alembic head = `0003`; SQL migrations 0001–0017 only add; test data is disposable | ✅ |

### Verdict

```text
ALLOW_GOVERNANCE_POLICY_REVIEW
```

---

## 4. Claim Data Inventory

| Artifact | File / Location | Type | Current Role After H12B | Removal Candidate? | Risk |
|---|---|---|---|---|---|
| `OperationClaim` (ORM) | `backend/app/models/station_claim.py` | MODEL | DEAD_RUNTIME_CODE (no active route calls service) | YES — H15 | LOW |
| `OperationClaimAuditLog` (ORM) | `backend/app/models/station_claim.py` | MODEL | HISTORICAL_AUDIT (stores expired/released/created events) | YES — H15 (after table drop) | LOW |
| `operation_claims` (table) | `backend/scripts/migrations/0009_station_claims.sql` | TABLE | LEGACY_DISABLED_API (no new rows; lazy expiry still writes) | YES — H16 | LOW |
| `operation_claim_audit_logs` (table) | `backend/scripts/migrations/0009_station_claims.sql` | TABLE | HISTORICAL_AUDIT (static after H12B; CLAIM_EXPIRED may still write via queue loop) | YES — H16 (after `operation_claims`) | LOW |
| `claim_operation()` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | DEAD_RUNTIME_CODE (no active caller after H12B) | YES — H15 | LOW |
| `release_operation_claim()` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | DEAD_RUNTIME_CODE | YES — H15 | LOW |
| `get_operation_claim_status()` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | DEAD_RUNTIME_CODE | YES — H15 | LOW |
| `_expire_claim_if_needed()` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | LEGACY_DISABLED_API (still active in `get_station_queue` queue loop; still writes `CLAIM_EXPIRED` rows) | YES — H14 queue cleanup | MEDIUM |
| `ensure_operator_context()` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | DEAD_RUNTIME_CODE (still called by `get_station_queue` and `resolve_station_scope` — not claim-specific) | NO — retained for queue | LOW |
| `resolve_station_scope()` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | ACTIVE (used by `get_station_queue`) | NO — retained for queue | NONE |
| `get_station_queue()` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | ACTIVE (still used by station queue route) | NO — retained for queue | NONE |
| `get_station_scoped_operation()` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | ACTIVE (used by station detail route) | NO — retained for queue | NONE |
| `ClaimConflictError` | `backend/app/services/station_claim_service.py` | SERVICE_FUNCTION | DEAD_RUNTIME_CODE | YES — H15 | LOW |
| `ClaimRequest` | `backend/app/schemas/station.py` | SCHEMA | LEGACY_DISABLED_API (kept as route type annotation) | YES — H15 | LOW |
| `ReleaseClaimRequest` | `backend/app/schemas/station.py` | SCHEMA | LEGACY_DISABLED_API | YES — H15 | LOW |
| `ClaimResponse` | `backend/app/schemas/station.py` | SCHEMA | LEGACY_DISABLED_API | YES — H15 | LOW |
| `POST .../claim` route | `backend/app/api/v1/station.py` | API_ROUTE | LEGACY_DISABLED_API (returns 410) | YES — H14 | LOW |
| `POST .../release` route | `backend/app/api/v1/station.py` | API_ROUTE | LEGACY_DISABLED_API (returns 410) | YES — H14 | LOW |
| `GET .../claim` route | `backend/app/api/v1/station.py` | API_ROUTE | LEGACY_DISABLED_API (returns 410) | YES — H14 | LOW |
| `stationApi.claim()` | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | LEGACY_DISABLED_API (deprecated stub, no active callers) | YES — H14 | LOW |
| `stationApi.release()` | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | LEGACY_DISABLED_API | YES — H14 | LOW |
| `stationApi.getClaim()` | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | LEGACY_DISABLED_API | YES — H14 | LOW |
| `ClaimSummary` type | `frontend/src/app/api/stationApi.ts` | SCHEMA | LEGACY_DISABLED_API (field `claim` is null-only in queue) | YES — H14 | LOW |
| `QueueClaimState` type | `frontend/src/app/api/stationApi.ts` | SCHEMA | LEGACY_DISABLED_API | YES — H14 | LOW |
| `ClaimResponse` type | `frontend/src/app/api/stationApi.ts` | SCHEMA | LEGACY_DISABLED_API | YES — H14 | LOW |
| `StationQueueItem.claim` field | `frontend/src/app/api/stationApi.ts` | SCHEMA | LEGACY_DISABLED_API (null-only per H10) | YES — H14 | LOW |
| `test_claim_api_deprecation_lock.py` | `backend/tests/` | TEST | TEST_LOCK (asserts 410 + disabled behavior) | TRANSFORM — H14/H15 | LOW |
| `test_claim_single_active_per_operator.py` | `backend/tests/` | TEST | TEST_LOCK (asserts service-level claim behavior) | DELETE — H15 | LOW |
| `test_release_claim_active_states.py` | `backend/tests/` | TEST | TEST_LOCK (asserts service-level release behavior) | DELETE — H15 | LOW |
| `test_execution_route_claim_guard_removal.py` (teardown) | `backend/tests/` | TEST | TEST_LOCK (teardown uses OperationClaim/AuditLog) | UPDATE teardown — H16 | LOW |
| `test_operation_detail_allowed_actions.py` (teardown) | `backend/tests/` | TEST | TEST_LOCK (teardown deletes OperationClaim/AuditLog rows) | UPDATE teardown — H16 | LOW |
| `test_operation_status_projection_reconcile.py` (teardown) | `backend/tests/` | TEST | TEST_LOCK (teardown) | UPDATE teardown — H16 | LOW |
| `0009_station_claims.sql` | `backend/scripts/migrations/` | MIGRATION | DOC_HISTORY (creates claim tables) | RETAIN as history doc | NONE |
| `CLAIM_CREATED` event | `operation_claim_audit_logs.event_type` | AUDIT_EVENT | HISTORICAL_AUDIT (rows written before H12B) | DROP with table — H16 | LOW |
| `CLAIM_RELEASED` event | `operation_claim_audit_logs.event_type` | AUDIT_EVENT | HISTORICAL_AUDIT | DROP with table — H16 | LOW |
| `CLAIM_EXPIRED` event | `operation_claim_audit_logs.event_type` | AUDIT_EVENT | HISTORICAL_AUDIT + may still produce until H14 queue cleanup | DROP with table — H16 | LOW |
| `CLAIM_RESTORED_ON_REOPEN` event | `operation_claim_audit_logs.event_type` | AUDIT_EVENT | HISTORICAL_AUDIT (retired since H11B) | DROP with table — H16 | LOW |
| H8–H12 implementation reports | `docs/implementation/` | DOC | DOC_HISTORY | RETAIN permanently | NONE |
| `p0-c-04-claim-compatibility-deprecation-lock.md` | `docs/implementation/` | DOC | DOC_HISTORY | RETAIN permanently | NONE |

---

## 5. Audit / History Map

| Data / Event | Source Table / Model | Producer Before Retirement | Producer Now | Audit Value | H13 Decision |
|---|---|---|---|---|---|
| `OperationClaim` row | `operation_claims` | `claim_operation()` via POST /claim | NONE (route returns 410) | LOW — temporary execution lock; already superseded by StationSession | DROP approved |
| `OperationClaimAuditLog` row | `operation_claim_audit_logs` | `_log_claim_event()` via claim/release/expire functions | Still written by `_expire_claim_if_needed()` via queue loop | LOW — dev baseline data; not legal e-record | DROP approved after H14 queue cleanup |
| `CLAIM_CREATED` | `operation_claim_audit_logs.event_type` | `claim_operation()` | NONE since H12B | LOW | DROP with table |
| `CLAIM_RELEASED` | `operation_claim_audit_logs.event_type` | `release_operation_claim()` | NONE since H12B | LOW | DROP with table |
| `CLAIM_EXPIRED` | `operation_claim_audit_logs.event_type` | `_expire_claim_if_needed()` in queue loop | STILL ACTIVE in queue loop | LOW | Stop writing first (H14), then DROP table (H16) |
| `CLAIM_RESTORED_ON_REOPEN` | `operation_claim_audit_logs.event_type` | `_restore_claim_continuity_for_reopen()` | NONE since H11B | LOW (retired) | DROP with table |
| Disabled API attempt | `operation_claim_audit_logs` | N/A | NOT recorded (410 returns before any service call) | N/A | N/A |
| StationSession lifecycle events | `security_event_logs` | `station_session_service` | ACTIVE | HIGH — target ownership events | RETAIN; NOT in scope for removal |

---

## 6. Data Retention Risk Map

| Data Object | Risk If Dropped | Severity | Mitigation | Decision |
|---|---|---|---|---|
| `operation_claims` rows | Loss of historical claim lock records | LOW — no production legal obligation; dev/test data only | Document drop in migration | APPROVED FOR DROP — H16 |
| `operation_claim_audit_logs` rows | Loss of `CLAIM_CREATED/RELEASED/EXPIRED/RESTORED` history | LOW — claim events are execution debug data; not business-critical after StationSession | Document drop in migration | APPROVED FOR DROP — H16 |
| Historical audit rows (CLAIM_EXPIRED via queue) | Still being written until H14; dropped in H16 | LOW | Stop writing first (H14), then drop table (H16) | APPROVED — requires H14 queue cleanup first |
| Migration rollback | Cannot recover claim tables from Alembic downgrade if data was present | MEDIUM | Downgrade script drops added column/table only; re-seed is required for test data | ACCEPTABLE — dev only; no production rollback risk |
| Test fixtures | Tests that create `OperationClaim` rows in teardown will fail after H16 | LOW | Tests must be updated before migration runs | REQUIRED PRECONDITION |
| Generated docs/history references | H8–H12 reports reference claim tables | NONE — docs are read-only history | Retain docs permanently | RETAIN |

---

## 7. Migration Impact Map

| Object | Current Dependency | Drop / Archive Impact | Required Before Removal |
|---|---|---|---|
| `OperationClaim` model | `test_claim_single_active_per_operator.py`, `test_release_claim_active_states.py`, teardown in 3 other test files | Teardown breaks; service tests fail | Remove model-dependent tests (H15); update teardown in other suites (H16) |
| `OperationClaimAuditLog` model | Teardown in same 3+ files | Teardown breaks | Update teardown before dropping table |
| `station_claim_service.py` (claim functions) | `test_claim_single_active_per_operator.py`, `test_release_claim_active_states.py` | Service tests fail | Delete service tests first (H15) |
| `station.py` claim routes | `test_claim_api_deprecation_lock.py` | 3 tests assert 410; after routes are removed, tests must be rewritten/removed | Update or delete route-level tests (H14) |
| `stationApi.ts` claim functions/types | No active callers; re-exported in `index.ts` | `index.ts` export must be removed | Remove exports from `index.ts` and types from `stationApi.ts` (H14) |
| `0009_station_claims.sql` | History only — not executed by Alembic | No impact; retain as history doc | RETAIN |
| `operation_claim_audit_logs` FK → `operation_claims.id` | FK `claim_id` references parent | Must drop `operation_claim_audit_logs` BEFORE `operation_claims` (FK constraint) | H16 migration: drop child table first |
| `operation_claims` FK → `operations.id` | FK `operation_id` references `operations` | Standard FK; no cascade impact | H16 migration: drop after child table |
| `operation_claims` FK → `scopes.id` | FK `station_scope_id` references `scopes` | Standard FK | H16 migration: drop after child table |
| `_expire_claim_if_needed()` in queue loop | Still active in `get_station_queue()`; writes `CLAIM_EXPIRED` to `operation_claim_audit_logs` | If table is dropped while function writes → runtime error | MUST remove from queue loop BEFORE dropping table (H14) |
| Backend tests (teardown) | `test_execution_route_claim_guard_removal.py`, `test_operation_detail_allowed_actions.py`, `test_operation_status_projection_reconcile.py` | Teardown `delete(OperationClaim)` / `delete(OperationClaimAuditLog)` will fail after H16 | Update teardown to remove claim deletes before H16 migration |
| Alembic head | Currently `0003` | H16 must add `0018` (or next) drop migration | New Alembic revision required — H16 |

---

## 8. Audit Retention Options

| Option | Pros | Cons | Risk | Fits User Goal? | Recommendation |
|---|---|---|---|---|---|
| **A — Dev/Test Hard Drop** | Clean; satisfies user goal; minimal complexity; no archive work | Irreversible; no recovery without re-seed | LOW (dev only) | ✅ YES | **RECOMMENDED** |
| **B — Archive Then Drop** | Preserves audit history; production-safe | Extra work; extra table; extra migration | MEDIUM | ❌ Over-engineering for dev | NOT recommended |
| **C — Retain Audit Table, Drop Runtime Table** | Keeps `CLAIM_CREATED/RELEASED` rows queryable | `operation_claim_audit_logs` FK blocks `operation_claims` drop anyway; still leaves partial tables | MEDIUM | Partial — still not clean | NOT recommended |
| **D — Retain Both Tables, Remove Runtime Code** | Safest; zero data loss | Does not satisfy "xóa sạch table/code"; tables remain forever | LOW | ❌ NO | NOT recommended |
| **E — Big-bang Drop Without Policy** | Fast | Skips this governance document; unsafe; blocks if tests still reference tables | HIGH | ❌ | **REJECTED** |

---

## 9. Environment / Data Assumption

| Assumption | Evidence | Confidence | Policy Impact |
|---|---|---|---|
| Project is pre-production / dev baseline | Alembic head is `0003`; SQL scripts 0001–0017 are additive only; no drop/truncate migrations exist; README confirms Docker-based local dev; H1–H12B all describe dev baseline increments | HIGH | Hard drop is safe |
| Claim tables contain only dev/test generated data | No production connection strings in config; `docker-compose.yml` is local only; seed scripts generate test data only | HIGH | Drop without archive approved |
| No legal/compliance data retention requirement for claim events | Claim events are internal execution debug data, not financial or regulatory events; no retention policy document exists | HIGH | Drop approved |
| Alembic can safely add a drop migration | Current head `0003` has no FK cycle or circular deps; `operation_claim_audit_logs` FK to `operation_claims` is child FK (drop child first) | HIGH | H16 migration is safe |
| `_expire_claim_if_needed()` still writes rows | Confirmed by source review: called in `get_station_queue()` for lazy claim expiry | CONFIRMED | Must be removed in H14 before table drop |
| FK constraint blocks drop order | `operation_claim_audit_logs.claim_id → operation_claims.id` | CONFIRMED | H16 must drop `operation_claim_audit_logs` first, then `operation_claims` |

**Environment verdict:** `DEV_PRE_PRODUCTION — HARD_DROP_SAFE`

---

## 10. Recommended H13 Policy

```text
CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED
```

**Conditions for this policy to remain valid:**

1. System is confirmed dev/pre-production with no production data in `operation_claims` or `operation_claim_audit_logs`.
2. `_expire_claim_if_needed()` is removed from `get_station_queue()` before table drop (H14 must complete before H16).
3. All test teardown code that deletes `OperationClaim` / `OperationClaimAuditLog` rows must be removed before migration runs.
4. `operation_claim_audit_logs` must be dropped BEFORE `operation_claims` in the H16 migration (FK constraint).
5. Alembic downgrade for H16 migration must restore both tables correctly.
6. Historical implementation reports (H8–H13) are retained permanently in `docs/implementation/`.

**Warning:** This policy cannot be reversed once tables are dropped. If this system transitions to production before H16, the policy must be re-reviewed and Option B (Archive Then Drop) substituted.

---

## 11. Removal Sequence After H13

### Recommended staged sequence (hard-drop approved path)

| Slice | Goal | Code? | Migration? | Preconditions | Stop Conditions |
|---|---|---|---|---|---|
| **H14** | Claim Route / Frontend Client / Queue-Loop Removal | YES (backend + frontend) | NO | H13 policy `APPROVED`; tests identified | Any active frontend caller of `stationApi.claim/release/getClaim` found |
| **H15** | Claim Service / Schema / Model Removal | YES (backend) | NO | H14 complete; route definitions removed; frontend types removed | Any non-disabled route still calls claim service; `test_claim_single_active_per_operator` and `test_release_claim_active_states` must be deleted first |
| **H16** | Claim Table Drop Migration | NO code; YES migration | YES | H15 complete; OperationClaim/AuditLog models removed; all teardown code updated; no active DB writes to claim tables | `_expire_claim_if_needed` still active in queue; teardown code still references claim models |
| **H17 / H-I** | Post-Removal Regression Closeout | YES (test + sweep) | NO | H16 complete | Any claim term found in active source by `rg` sweep |

### Detailed slice scope

#### H14 — Claim Route / Frontend Client / Queue-Loop Removal

**Backend:**
- Remove 3 disabled claim route definitions from `station.py` (entire route bodies + `@router.post/get` decorators)
- Remove `_raise_claim_api_disabled()` helper and `_CLAIM_DISABLED_HEADERS` from `station.py`
- Remove `add_claim_api_deprecation_headers()` from `station.py`
- Remove `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` imports from `station.py`
- Remove `_expire_claim_if_needed()` call and supporting logic from `get_station_queue()` in `station_claim_service.py` (remove `claims` dict, claim loop, `_to_claim_state()` call)
- Remove `OperationClaim` import from `station_claim_service.py` (after removing queue claim loop)
- Note: `get_station_queue()` itself is retained; only the claim-querying block inside it is removed

**Frontend:**
- Remove `claim()`, `release()`, `getClaim()` methods from `stationApi`
- Remove `ClaimSummary`, `QueueClaimState`, `ClaimResponse` interfaces from `stationApi.ts`
- Remove `StationQueueItem.claim` field from `stationApi.ts`
- Remove `claim: ClaimSummary | null` references from `index.ts` re-exports
- Remove `QueueClaimState`, `ClaimSummary`, `ClaimResponse` from `index.ts` exports

**Test updates:**
- Delete or transform `test_claim_api_deprecation_lock.py` (3 of 5 tests now assert 410; after route removal, those 3 tests would get 404; decide: delete file or transform to 404 assertions)
- Update teardown in `test_execution_route_claim_guard_removal.py`, `test_operation_detail_allowed_actions.py`, `test_operation_status_projection_reconcile.py` to remove claim-row deletion stmts (now safe since no new rows written)

#### H15 — Claim Service / Schema / Model Removal

**Backend:**
- Delete `claim_operation()`, `release_operation_claim()`, `get_operation_claim_status()`, `_log_claim_event()`, `_get_unreleased_claim_for_update()`, `_get_operator_unreleased_claims_for_station_for_update()`, `_to_claim_state()`, `_validate_operation_for_station()`, `_validate_operation_for_active_claim_context()`, `ClaimConflictError` from `station_claim_service.py`
- Remove `OperationClaim`, `OperationClaimAuditLog` imports from `station_claim_service.py`
- Remove `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` from `backend/app/schemas/station.py`
- Delete `backend/app/models/station_claim.py` (entire file)
- Remove `station_claim` model from `backend/app/db/base.py` imports if present

**Tests:**
- Delete `backend/tests/test_claim_single_active_per_operator.py` (entire file)
- Delete `backend/tests/test_release_claim_active_states.py` (entire file)

**Precondition:** H14 complete; claim routes removed; no active code path imports `OperationClaim` or `OperationClaimAuditLog`.

#### H16 — Claim Table Drop Migration

**Alembic migration** (new revision, e.g. `0004_drop_claim_tables`):
```sql
-- upgrade
DROP TABLE IF EXISTS operation_claim_audit_logs;  -- child FK first
DROP TABLE IF EXISTS operation_claims;

-- downgrade (for rollback safety)
CREATE TABLE operation_claims (...);
CREATE TABLE operation_claim_audit_logs (...);
```

**Preconditions:**
- H15 complete (no Python code references ORM models)
- `_expire_claim_if_needed()` is removed from queue loop (H14)
- Test teardown code no longer deletes from claim tables (H14)
- DB confirmed dev/test only — no production data

**FK drop order:** `operation_claim_audit_logs` first (FK `claim_id → operation_claims.id`), then `operation_claims`.

#### H-I / H17 — Post-Removal Regression Closeout

- Run `rg` sweep for claim terms across backend source
- Run full backend suite — 391 → expect lower test count (service tests deleted)
- Run frontend lint/build/routes
- Update trackers
- Verify no remaining `operation_claims` or `operation_claim_audit_logs` references in active code

---

## 12. Stop Conditions for Destructive Removal

| Stop Condition | Why It Blocks | Required Resolution |
|---|---|---|
| `_expire_claim_if_needed()` still active in queue loop | Will write `CLAIM_EXPIRED` rows to `operation_claim_audit_logs` after table drop → runtime crash | Must be removed from `get_station_queue()` in H14 before H16 migration |
| Test teardown still deletes `OperationClaim` / `OperationClaimAuditLog` rows | After table drop, teardown raises `ProgrammingError: table does not exist` | Must update teardown in H14/H15 before H16 migration |
| `OperationClaim` or `OperationClaimAuditLog` ORM models still imported anywhere | SQLAlchemy will fail to map table on startup if model exists but table is gone | Must delete model file (H15) before running H16 migration |
| Frontend still exports `ClaimSummary`, `QueueClaimState`, `ClaimResponse` as public types | Other files may import these; TypeScript compilation fails | Must remove from `stationApi.ts` and `index.ts` in H14 |
| `test_claim_single_active_per_operator.py` or `test_release_claim_active_states.py` still present | Will fail immediately when claim service functions are removed | Must delete both test files in H15 |
| Alembic migration creates FK cycle | `operation_claim_audit_logs.claim_id → operation_claims.id` — if dropped in wrong order | H16 migration must drop child (`operation_claim_audit_logs`) before parent (`operation_claims`) |
| Production data detected in claim tables | Would mean audit records cannot be discarded | Re-review retention policy; switch to Option B (Archive Then Drop) |
| New feature imports claim model after H12B | If any post-H12B slice accidentally introduces a claim dependency | Full `rg` sweep of source must show zero matches before H16 |
| Docs declare claim as active compatibility feature | If any design doc or API doc still lists claim as supported | Update or tombstone docs before H16 |
| Migration rollback unclear | Downgrade must restore tables or be explicitly marked non-reversible | H16 migration downgrade must include CREATE TABLE stmts or be marked `irreversible = True` |

---

## 13. Test Strategy for Removal Slices

| Future Slice | Tests Required | Expected Claim State After Slice |
|---|---|---|
| **H14** | Frontend lint + build + route smoke; Backend: `test_claim_api_deprecation_lock.py` updated/deleted; teardown stmts removed; `rg` for `_expire_claim_if_needed` = 0 in queue service | Route defs removed; FE types/methods removed; queue loop no longer writes claim rows |
| **H15** | Backend: delete `test_claim_single_active_per_operator.py` + `test_release_claim_active_states.py`; `rg OperationClaim\|OperationClaimAuditLog` in backend source = 0; full backend suite passes | ORM model file deleted; service functions deleted; schema types deleted |
| **H16** | Run `alembic upgrade head`; confirm `operation_claims` table does not exist in DB; confirm `operation_claim_audit_logs` table does not exist in DB; `alembic downgrade -1` + re-upgrade round-trip; full backend suite passes | Both tables dropped from DB; alembic head incremented |
| **H-I / H17** | `rg` sweep backend+frontend for `claim\|OperationClaim\|ClaimSummary\|QueueClaimState\|CLAIM_CREATED\|CLAIM_RELEASED\|CLAIM_EXPIRED` — must return zero hits in active source (docs/reports excluded); frontend lint/build; full backend suite | Clean repository; no claim references in active code or tests |

---

## 14. Risk Register

| Risk | Probability | Severity | Mitigation |
|---|---|---|---|
| `_expire_claim_if_needed` still writing after H14 slip | LOW (explicit precondition) | HIGH — table drop would crash queue | H16 gate: verify function removed from `get_station_queue` before migration |
| FK order mistake in H16 migration | LOW | MEDIUM — migration fails on child FK constraint | Explicitly: `DROP operation_claim_audit_logs` first |
| Test teardown not updated before H16 | LOW | MEDIUM — teardown errors after drop | H14 scope explicitly includes teardown cleanup |
| Frontend types removed before backend (null claim field still served) | VERY LOW | LOW — field is already null-only; FE already ignores it | H14 removes FE types after backend claim routes are gone |
| Policy applies to production environment in future | POSSIBLE | HIGH | Warning documented in Section 10; policy must be re-reviewed before production rollout |
| `rg` sweep misses a claim reference in dynamic code | LOW | LOW | Pattern-based sweep + full test suite as final gate |

---

## 15. Recommendation

1. **Adopt:** `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED`
2. **Proceed to H14** — Claim Route / Frontend Client / Queue-Loop Removal (implementation).
3. **Do NOT proceed to H16** until H14 and H15 are both complete and all stop conditions are verified.
4. **Retain** all implementation reports (H8–H13) in `docs/implementation/` permanently.
5. **Retain** `backend/scripts/migrations/0009_station_claims.sql` as historical reference (do not delete).
6. **Do NOT archive** `operation_claim_audit_logs` data — it is dev/test data with no legal retention requirement.

---

## 16. Final Verdict

```text
CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED
```

| Decision | Verdict |
|---|---|
| Retention policy | DEV_HARD_DROP_APPROVED |
| Hard drop approved for current baseline | YES |
| Archive required | NO |
| Audit table separate retention | NO |
| Environment assumption | DEV_PRE_PRODUCTION |
| Production data at risk | NO |
| FK order enforced | YES — audit_logs first, then claims |
| H14 precondition | Remove `_expire_claim_if_needed` from queue loop + remove route defs + remove FE types |
| H15 precondition | H14 complete; delete service tests; delete model file |
| H16 precondition | H15 complete; all teardown updated; `rg` sweep clean |
| Claim tables removal readiness | NOT YET — H14 and H15 must complete first |
| Remaining blockers | `_expire_claim_if_needed` in queue loop; ORM models still imported in tests; teardown code references claim models |
| Recommended next slice | P0-C-08H14 — Claim Route / Frontend Client / Queue-Loop Removal |

---

## Verification Results (H13 Baseline Smoke)

| Check | Result |
|---|---|
| Backend compat smoke (claim disable + queue + execution guard) | `27 passed`, `H13_COMPAT_SMOKE_EXIT:0` |
| Backend reopen smoke | `22 passed`, `H13_REOPEN_SMOKE_EXIT:0` |
| Frontend lint | `H13_FRONTEND_LINT_EXIT:0` |
| Frontend build | `H13_FRONTEND_BUILD_EXIT:0` |
| Frontend route smoke | `H13_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 77/78 covered) |

Note: First run of reopen smoke encountered transient DB-lock errors (`1 passed, 21 errors`) due to test session overlap. Second run confirmed `22 passed` — this is a known transient issue in multi-suite combined runs; individual suite runs are reliable.

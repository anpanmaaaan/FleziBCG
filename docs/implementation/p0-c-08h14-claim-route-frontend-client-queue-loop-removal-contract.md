# P0-C-08H14 Claim Route / Frontend Client / Queue-Loop Removal Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Defined first hard-removal implementation scope for claim routes, frontend clients, and queue-loop remnants after audit hard-drop approval (H13). |

---

## Routing

- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only Review
- Hard Mode MOM: v3
- Reason: Task touches claim API route removal, frontend API client removal, queue-loop cleanup, audit event retirement, execution ownership truth, legacy operational data boundary, and staged hard-removal sequencing — all v3 trigger zones.

---

## 1. Executive Summary

As of H13, `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED` has been issued. This H14 contract defines the precise scope and boundary for the first hard-removal implementation slice:

**H14B** — Claim API Route Removal + Frontend Client/Type Removal + Queue-Loop Expiration Removal

Key findings from source inspection:

1. The 3 disabled claim API routes in `station.py` have no runtime consumers. They are safe to remove entirely.
2. The frontend `stationApi.claim()`, `stationApi.release()`, `stationApi.getClaim()` stubs have zero active callers across all frontend source files. They are safe to remove.
3. The `ClaimSummary`, `QueueClaimState`, `ClaimResponse` types have **zero consumers** outside `stationApi.ts` and `index.ts` (the `station.claim.*` i18n strings used in components are NOT dependent on these types — they're just translation keys).
4. `StationQueueItem.claim` field (`claim: ClaimSummary | null`) has **zero consumers** in component code — the field arrives null from backend since H10, and no component reads it.
5. The `_expire_claim_if_needed()` call inside `get_station_queue()` is still active — it queries `OperationClaim` rows, writes `CLAIM_EXPIRED` to `operation_claim_audit_logs`, and calls `db.commit()`. This is a **blocker for H16 table drop** and must be removed in H14B.
6. The `_to_claim_state()` function is only called inside the queue claim loop — it becomes dead code after queue-loop removal.
7. `ensure_operation_claim_owned_by_identity()` has **zero callers** in production code — it was the old execution route claim guard removed in H4. It is dead code.
8. `add_claim_api_deprecation_headers()` in `station.py` is defined but **never called** in any route — the routes use `_CLAIM_DISABLED_HEADERS` directly via `HTTPException.headers`. It is dead code.
9. `db/init_db.py` imports `OperationClaim, OperationClaimAuditLog` for SQLAlchemy table registration — this must **remain until H16** (model/table drop).
10. Backend test `test_claim_api_deprecation_lock.py`: 3 of 5 tests assert HTTP 410 on the 3 claim routes. After route removal, these 3 tests would receive 404/405 instead. The file must be rewritten or deleted in H14B.
11. `test_execution_route_claim_guard_removal.py` inserts live `OperationClaim` rows in `_insert_active_claim()` helper and teardown. This test must remain (it validates StationSession guard behavior) but the claim insertion helper and teardown must be removed from it.

**No code changes in this document.** Contract-only.

---

## 2. Scope Reviewed

### Source files inspected

| File | Purpose |
|---|---|
| `backend/app/api/v1/station.py` | 3 disabled claim routes + `_raise_claim_api_disabled()` + `add_claim_api_deprecation_headers()` + `_CLAIM_DISABLED_HEADERS` |
| `backend/app/services/station_claim_service.py` | Full claim service; `get_station_queue()` with embedded claim expiry loop; dead service functions |
| `backend/app/models/station_claim.py` | `OperationClaim`, `OperationClaimAuditLog` ORM models |
| `backend/app/db/init_db.py` | Imports claim models for Alembic/SQLAlchemy table registration |
| `backend/app/schemas/station.py` | `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` schema types |
| `frontend/src/app/api/stationApi.ts` | `claim()`, `release()`, `getClaim()` deprecated stubs; `ClaimSummary`, `QueueClaimState`, `ClaimResponse`, `StationQueueItem.claim` field |
| `frontend/src/app/api/index.ts` | Re-exports `QueueClaimState`, `ClaimSummary`, `ClaimResponse` |
| `frontend/src/app/pages/StationExecution.tsx` | Uses `station.claim.*` i18n keys — NOT the claim type |
| `frontend/src/app/components/station-execution/QueueOperationCard.tsx` | Uses `station.claim.ownedBadge` i18n key — NOT the claim type |
| `frontend/src/app/components/station-execution/StationExecutionHeader.tsx` | Uses `station.claim.ownedBadge` i18n key — NOT the claim type |
| `backend/tests/test_claim_api_deprecation_lock.py` | 5 tests: 3 assert 410, 2 assert non-deprecated behavior |
| `backend/tests/test_claim_single_active_per_operator.py` | 6 service-level tests calling `claim_operation()` |
| `backend/tests/test_release_claim_active_states.py` | 14 service-level tests calling `release_operation_claim()` |
| `backend/tests/test_execution_route_claim_guard_removal.py` | 12 tests; inserts `OperationClaim` rows; teardown deletes claim rows |
| `backend/tests/test_operation_detail_allowed_actions.py` | Teardown deletes `OperationClaim`/`OperationClaimAuditLog` rows |
| `backend/tests/test_operation_status_projection_reconcile.py` | Teardown deletes `OperationClaim`/`OperationClaimAuditLog` rows |
| `backend/scripts/verify_station_claim.py` | References `OperationClaim` for claim release in teardown |
| `backend/scripts/verify_station_queue_claim.py` | References `OperationClaim` for claim release in teardown |
| `backend/scripts/verify_clock_on.py` | Teardown deletes `OperationClaim`/`OperationClaimAuditLog` rows |
| `backend/scripts/verify_clock_off.py` | Teardown deletes `OperationClaim`/`OperationClaimAuditLog` rows |
| `backend/scripts/seed/seed_station_execution_opr.py` | Imports `OperationClaim`, `OperationClaimAuditLog` |

### Prior implementation reports reviewed

- `docs/implementation/p0-c-08h13-audit-retention-claim-historical-data-policy.md`
- `docs/implementation/p0-c-08h12b-claim-api-runtime-disablement-implementation-report.md`
- `docs/implementation/p0-c-08h11b-reopen-claim-compatibility-retirement-implementation-report.md`
- `docs/implementation/p0-c-08h10-backend-queue-claim-payload-null-only-implementation-report.md`

---

## 3. Hard Mode Gate Evidence

### Design Evidence Extract

| Fact | Evidence | Confirmed |
|---|---|---|
| StationSession is target ownership truth | `station-session-ownership-contract.md`; `get_station_queue()` returns `ownership` block from active session | ✅ |
| Claim API is runtime-disabled; no active public surface | H12B — `_raise_claim_api_disabled()` on all 3 routes; HTTP 410 `CLAIM_API_DISABLED` | ✅ |
| Queue claim payload is null-only | H10 — `get_station_queue()` returns `"claim": None`; no component reads `item.claim` | ✅ |
| Reopen claim restoration removed | H11B — `_restore_claim_continuity_for_reopen` deleted | ✅ |
| H13 approved `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED` | H13 policy document | ✅ |
| Historical claim audit deletion requires staged migration | H13 — table drop deferred to H16 Alembic migration | ✅ |
| `_expire_claim_if_needed` still active in queue loop | Source: `station_claim_service.py` lines 376–381; still queries `OperationClaim` and writes `CLAIM_EXPIRED` | ✅ (BLOCKER) |
| Frontend `station.claim.*` i18n keys are NOT claim type dependencies | Grep confirms: `StationExecution.tsx`, `QueueOperationCard.tsx`, `StationExecutionHeader.tsx` use i18n strings only — no import of `ClaimSummary`/`QueueClaimState`/`ClaimResponse` | ✅ |
| `stationApi.claim/release/getClaim` have zero active callers | Full grep of `frontend/src/**` — functions only defined in `stationApi.ts`, never called elsewhere | ✅ |
| `ensure_operation_claim_owned_by_identity()` has zero callers | Grep of `backend/app/**` — defined in `station_claim_service.py`; no import or call site found | ✅ |
| `add_claim_api_deprecation_headers()` is never called | Defined in `station.py` line 23; never referenced in any route (routes use `_CLAIM_DISABLED_HEADERS` dict directly) | ✅ |
| H14 is contract-only; no runtime code change | Task scope is review/contract only | ✅ |

### Verdict

```text
ALLOW_CONTRACT_REVIEW
```

---

## 4. Repo-Wide Claim Reference Inventory

| Reference | File | Category | Active Runtime? | H14B Action |
|---|---|---|---|---|
| `OperationClaim` (ORM model) | `backend/app/models/station_claim.py` | MODEL | YES — still registered in `init_db.py`, referenced in service queue loop | DEFER to H15 |
| `OperationClaimAuditLog` (ORM model) | `backend/app/models/station_claim.py` | MODEL | YES — still registered in `init_db.py`, referenced in queue loop `_log_claim_event` | DEFER to H15 |
| `OperationClaim` import | `backend/app/db/init_db.py` | MODEL | YES — required for SQLAlchemy table registration | DEFER to H15 |
| `OperationClaim` import | `backend/app/services/station_claim_service.py` | MODEL | YES — used in queue loop + dead service functions | REMOVE queue loop in H14B; full import removal in H15 |
| `OperationClaimAuditLog` import | `backend/app/services/station_claim_service.py` | MODEL | YES — used by `_log_claim_event()` which is called from queue loop | REMOVE from queue loop in H14B; full removal in H15 |
| `ClaimRequest` | `backend/app/schemas/station.py` | SCHEMA | YES — imported in `station.py` as route type annotation | REMOVE import from `station.py` in H14B; schema type defer to H15 |
| `ReleaseClaimRequest` | `backend/app/schemas/station.py` | SCHEMA | YES — imported in `station.py` | REMOVE import from `station.py` in H14B; defer to H15 |
| `ClaimResponse` | `backend/app/schemas/station.py` | SCHEMA | YES — imported in `station.py` | REMOVE import from `station.py` in H14B; defer to H15 |
| `POST .../claim` route | `backend/app/api/v1/station.py` | ROUTE | NO — returns 410; no runtime consumers | REMOVE in H14B |
| `POST .../release` route | `backend/app/api/v1/station.py` | ROUTE | NO — returns 410; no runtime consumers | REMOVE in H14B |
| `GET .../claim` route | `backend/app/api/v1/station.py` | ROUTE | NO — returns 410; no runtime consumers | REMOVE in H14B |
| `add_claim_api_deprecation_headers()` | `backend/app/api/v1/station.py` | ROUTE | NO — defined but never called in any route | REMOVE in H14B |
| `_CLAIM_DISABLED_HEADERS` | `backend/app/api/v1/station.py` | ROUTE | NO — only used by `_raise_claim_api_disabled()` which is only called from removed routes | REMOVE with routes in H14B |
| `_raise_claim_api_disabled()` | `backend/app/api/v1/station.py` | ROUTE | NO — only called from claim routes being removed | REMOVE with routes in H14B |
| `get_station_claim_status` function name | `backend/app/api/v1/station.py` | ROUTE | NO — disabled route, returns 410 | REMOVE in H14B (part of route removal) |
| `claim_operation()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — dead code since H12B; no route callers | DEFER to H15 |
| `release_operation_claim()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — dead code | DEFER to H15 |
| `get_operation_claim_status()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — dead code | DEFER to H15 |
| `_expire_claim_if_needed()` | `backend/app/services/station_claim_service.py` | SERVICE | YES — called inside `get_station_queue()` queue loop; still writes `CLAIM_EXPIRED` rows | REMOVE from queue loop in H14B |
| `_log_claim_event()` | `backend/app/services/station_claim_service.py` | SERVICE | YES — called by `_expire_claim_if_needed()` from queue loop | REMOVE from queue loop in H14B; function remains until H15 |
| `_get_unreleased_claim_for_update()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — only called by dead `claim_operation()`, `release_operation_claim()`, `get_operation_claim_status()`, `ensure_operation_claim_owned_by_identity()` | DEFER to H15 |
| `_get_operator_unreleased_claims_for_station_for_update()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — only called by dead `claim_operation()` | DEFER to H15 |
| `_to_claim_state()` | `backend/app/services/station_claim_service.py` | SERVICE | YES — called inside queue loop (maps claim to "mine"/"other"/"none") | REMOVE from queue loop in H14B; dead code after; defer full removal to H15 |
| `_validate_operation_for_station()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — only called by `claim_operation()` | DEFER to H15 |
| `_validate_operation_for_active_claim_context()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — only called by `release_operation_claim()`, `get_operation_claim_status()` | DEFER to H15 |
| `_has_admin_support_override()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — only called by `release_operation_claim()` | DEFER to H15 |
| `ensure_operation_claim_owned_by_identity()` | `backend/app/services/station_claim_service.py` | SERVICE | NO — zero callers in production code (execution route claim guard removed in H4) | DEFER to H15 |
| `ClaimConflictError` | `backend/app/services/station_claim_service.py` | SERVICE | NO — only referenced by `claim_operation()` and `test_claim_single_active_per_operator.py` | DEFER to H15 |
| `active_operation_ids` claim query | `backend/app/services/station_claim_service.py` (queue loop) | SERVICE | YES — queries `OperationClaim` rows inside `get_station_queue()` | REMOVE in H14B |
| `claims` dict construction | `backend/app/services/station_claim_service.py` (queue loop) | SERVICE | YES — builds claim map from queried rows | REMOVE in H14B |
| `operation_claims` table | `backend/scripts/migrations/0009_station_claims.sql` | TABLE | YES — SQLAlchemy still maps it via model | DEFER to H16 |
| `operation_claim_audit_logs` table | `backend/scripts/migrations/0009_station_claims.sql` | TABLE | YES — SQLAlchemy still maps it via model | DEFER to H16 |
| `CLAIM_CREATED` event | `operation_claim_audit_logs.event_type` | AUDIT_EVENT | NO — no writer since H12B | DEFER to H16 (DROP with table) |
| `CLAIM_RELEASED` event | `operation_claim_audit_logs.event_type` | AUDIT_EVENT | NO — no writer since H12B | DEFER to H16 |
| `CLAIM_EXPIRED` event | `operation_claim_audit_logs.event_type` | AUDIT_EVENT | YES — still written by `_expire_claim_if_needed()` in queue loop | STOP writing in H14B (remove queue loop); DROP in H16 |
| `CLAIM_API_DISABLED` error detail | `backend/app/api/v1/station.py` | ERROR_CODE | YES — returned by 3 disabled routes; routes being removed | RETIRE with routes in H14B |
| `CLAIM_API_DISABLED` in canonical error docs | `docs/` | DOC | NO — runtime error detail string; not a formal error code in canonical error registry | RETAIN as historical reference in docs; note as retired |
| `QueueClaimState` type | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | NO — zero consumers outside stationApi.ts and index.ts | REMOVE in H14B |
| `ClaimSummary` interface | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | NO — zero consumers outside stationApi.ts and index.ts | REMOVE in H14B |
| `ClaimResponse` interface | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | NO — zero consumers outside stationApi.ts and index.ts | REMOVE in H14B |
| `StationQueueItem.claim` field | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | NO — field arrives null-only from backend; zero components read it | REMOVE in H14B |
| `stationApi.claim()` | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | NO — zero callers in frontend source | REMOVE in H14B |
| `stationApi.release()` | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | NO — zero callers | REMOVE in H14B |
| `stationApi.getClaim()` | `frontend/src/app/api/stationApi.ts` | FRONTEND_CLIENT | NO — zero callers | REMOVE in H14B |
| `QueueClaimState` re-export | `frontend/src/app/api/index.ts` | FRONTEND_CLIENT | NO — nothing imports it from index.ts | REMOVE in H14B |
| `ClaimSummary` re-export | `frontend/src/app/api/index.ts` | FRONTEND_CLIENT | NO — nothing imports it from index.ts | REMOVE in H14B |
| `ClaimResponse` re-export | `frontend/src/app/api/index.ts` | FRONTEND_CLIENT | NO — nothing imports it from index.ts | REMOVE in H14B |
| `station.claim.*` i18n keys (en.ts, ja.ts) | `frontend/src/app/i18n/registry/` | DOC | YES — used as display strings in StationExecution.tsx, QueueOperationCard.tsx, StationExecutionHeader.tsx | RETAIN — these are UI text keys, NOT claim API dependencies |
| `test_claim_api_deprecation_lock.py` | `backend/tests/` | TEST | YES — 3 tests assert HTTP 410; 2 assert non-deprecated paths | DELETE/REWRITE in H14B |
| `test_claim_single_active_per_operator.py` | `backend/tests/` | TEST | YES — calls `claim_operation()` directly | DEFER DELETE to H15 (needs service functions) |
| `test_release_claim_active_states.py` | `backend/tests/` | TEST | YES — calls `release_operation_claim()` | DEFER DELETE to H15 |
| `test_execution_route_claim_guard_removal.py` | `backend/tests/` | TEST | YES — inserts `OperationClaim` rows; teardown deletes claim rows | RETAIN test body; REMOVE `_insert_active_claim()` helper + teardown claim deletes in H14B |
| `test_operation_detail_allowed_actions.py` teardown | `backend/tests/` | TEST | YES — teardown deletes `OperationClaim`/`OperationClaimAuditLog` rows | UPDATE teardown in H14B |
| `test_operation_status_projection_reconcile.py` teardown | `backend/tests/` | TEST | YES — teardown deletes claim rows | UPDATE teardown in H14B |
| `verify_station_claim.py` | `backend/scripts/` | SCRIPT | NO — standalone verification script | DEFER to H15/H-I (scripts cleanup) |
| `verify_station_queue_claim.py` | `backend/scripts/` | SCRIPT | NO — standalone verification script | DEFER to H15/H-I |
| `verify_clock_on.py` | `backend/scripts/` | SCRIPT | NO — teardown uses `OperationClaim` | DEFER to H16 |
| `verify_clock_off.py` | `backend/scripts/` | SCRIPT | NO — teardown uses `OperationClaim` | DEFER to H16 |
| `seed_station_execution_opr.py` | `backend/scripts/seed/` | SCRIPT | NO — seed script references claim models | DEFER to H15 |
| `0009_station_claims.sql` | `backend/scripts/migrations/` | MIGRATION | NO — history doc only; not executed by Alembic | RETAIN permanently |

---

## 5. Runtime Surface Map

| Surface | Current File | Current State After H13 | H14B Candidate? | Risk |
|---|---|---|---|---|
| `POST /queue/{id}/claim` route | `station.py` | Returns HTTP 410 `CLAIM_API_DISABLED`; no active consumer | YES — remove entirely | LOW |
| `POST /queue/{id}/release` route | `station.py` | Returns HTTP 410; no active consumer | YES — remove entirely | LOW |
| `GET /queue/{id}/claim` route | `station.py` | Returns HTTP 410; no active consumer | YES — remove entirely | LOW |
| `_raise_claim_api_disabled()` | `station.py` | Only called by the 3 claim routes being removed | YES — remove with routes | LOW |
| `_CLAIM_DISABLED_HEADERS` | `station.py` | Only used by `_raise_claim_api_disabled()` | YES — remove with helper | LOW |
| `add_claim_api_deprecation_headers()` | `station.py` | Defined but **never called** — dead code | YES — remove in H14B | LOW |
| `CLAIM_API_DISABLED` detail string | `station.py` | Returned via `_raise_claim_api_disabled()`; gone with routes | YES — retired with routes | NONE |
| `ClaimRequest` schema import | `station.py` | Used only as route type annotation for removed routes | YES — remove import | LOW |
| `ReleaseClaimRequest` schema import | `station.py` | Used only as route type annotation | YES — remove import | LOW |
| `ClaimResponse` schema import | `station.py` | Used only as route type annotation | YES — remove import | LOW |
| Queue claim query (`OperationClaim` select) | `station_claim_service.py` | Inside `get_station_queue()` — queries `OperationClaim`, feeds `_expire_claim_if_needed()` | YES — remove this block in H14B | MEDIUM (must keep `get_station_queue()`) |
| `_expire_claim_if_needed()` call in queue | `station_claim_service.py` | Still writes `CLAIM_EXPIRED` rows; only caller after H12B is queue loop | YES — remove call and surrounding loop in H14B | MEDIUM (BLOCKER for H16) |
| `claims` dict in queue | `station_claim_service.py` | Populated from `OperationClaim` query; result always `None` after expiry | YES — remove dict | LOW |
| `_to_claim_state()` function | `station_claim_service.py` | Only called in queue loop claim block | Remove call in H14B; defer function deletion to H15 | LOW |
| `"claim": None` in queue item dict | `station_claim_service.py` | Null-only hardcoded since H10; stable response | RETAIN until queue response contract is updated | LOW |
| `OperationClaim` import in service | `station_claim_service.py` | Used by queue loop + dead service functions | Remove from queue loop block; full import removal deferred to H15 | MEDIUM |
| `claim_operation()` | `station_claim_service.py` | Dead code (no route caller) | DEFER to H15 | NONE |
| `release_operation_claim()` | `station_claim_service.py` | Dead code | DEFER to H15 | NONE |
| `get_operation_claim_status()` | `station_claim_service.py` | Dead code | DEFER to H15 | NONE |
| `ensure_operation_claim_owned_by_identity()` | `station_claim_service.py` | Zero callers | DEFER to H15 | NONE |
| `stationApi.claim()` | `stationApi.ts` | Deprecated stub; zero callers in frontend source | YES — remove in H14B | LOW |
| `stationApi.release()` | `stationApi.ts` | Deprecated stub; zero callers | YES — remove in H14B | LOW |
| `stationApi.getClaim()` | `stationApi.ts` | Deprecated stub; zero callers | YES — remove in H14B | LOW |
| `ClaimSummary` interface | `stationApi.ts` | Zero consumers; only referenced in own file and index.ts re-export | YES — remove in H14B | LOW |
| `QueueClaimState` type | `stationApi.ts` | Zero consumers outside stationApi.ts | YES — remove in H14B | LOW |
| `ClaimResponse` interface | `stationApi.ts` | Zero consumers outside stationApi.ts | YES — remove in H14B | LOW |
| `StationQueueItem.claim` field | `stationApi.ts` | Null-only; zero component consumers | YES — remove field in H14B | LOW |
| `QueueClaimState/ClaimSummary/ClaimResponse` re-exports | `index.ts` | Zero downstream imports | YES — remove in H14B | LOW |
| `OperationClaim` model | `models/station_claim.py` | Registered in `init_db.py`; still backs DB table | DEFER to H15 | NONE |
| `OperationClaimAuditLog` model | `models/station_claim.py` | Same as above | DEFER to H15 | NONE |
| `operation_claims` table | DB | SQLAlchemy-mapped; no new rows after queue loop removal | DEFER to H16 | NONE |
| `operation_claim_audit_logs` table | DB | Same; `CLAIM_EXPIRED` stops after H14B queue loop removal | DEFER to H16 | NONE |

---

## 6. API / Client Removal Impact Map

| API / Client Artifact | Current Consumer | Remove in H14B? | Required Test Change | Risk |
|---|---|---|---|---|
| `POST /queue/{id}/claim` (HTTP 410) | None (no active client; `test_claim_api_deprecation_lock.py` only) | YES | Delete/rewrite `test_claim_api_deprecation_lock.py` — 3 tests assert 410 become 404 after removal; OR delete file | LOW |
| `POST /queue/{id}/release` (HTTP 410) | None | YES | Same test file | LOW |
| `GET /queue/{id}/claim` (HTTP 410) | None | YES | Same test file | LOW |
| `stationApi.claim()` | Zero frontend callers | YES | None needed; no test mocks the function | LOW |
| `stationApi.release()` | Zero frontend callers | YES | None | LOW |
| `stationApi.getClaim()` | Zero frontend callers | YES | None | LOW |
| `ClaimSummary` interface | Only used by `StationQueueItem.claim` field (being removed) and `index.ts` re-export (being removed) | YES | None | LOW |
| `QueueClaimState` type | Only used in `ClaimSummary`, `ClaimResponse`, and `getClaim` return type (all being removed) | YES | None | LOW |
| `ClaimResponse` interface | Only used in `claim()` and `release()` stubs (being removed) | YES | None | LOW |
| `StationQueueItem.claim` field | Zero component consumers; backend delivers null-only | YES | None (no component reads the field) | LOW |
| `QueueClaimState/ClaimSummary/ClaimResponse` in `index.ts` | Zero downstream imports confirmed by grep | YES | None | LOW |
| `CLAIM_API_DISABLED` in canonical error docs | Historical docs only; not referenced in active code | RETAIN in docs | None; note in docs as retired | NONE |
| Deprecation headers (`Deprecation`, `X-FleziBCG-Deprecation-Status`, `X-FleziBCG-Replacement`) | `test_claim_api_deprecation_lock.py` assertions | RETIRE with routes | Update/delete test file | LOW |

**CRITICAL FINDING — `test_claim_api_deprecation_lock.py`:**

| Test | Current Assertion | After H14B Route Removal | H14B Action |
|---|---|---|---|
| `test_claim_endpoint_returns_disabled_error` | POST → 410 + `CLAIM_API_DISABLED` | POST → 404 (route not registered) OR 405 (method not allowed) | DELETE or update to assert 404 |
| `test_release_endpoint_returns_disabled_error` | POST → 410 + `CLAIM_API_DISABLED` | POST → 404 | DELETE or update |
| `test_claim_status_endpoint_returns_disabled_error` | GET → 410 + `CLAIM_API_DISABLED` | GET → 404 | DELETE or update |
| `test_station_queue_endpoint_remains_non_deprecated_with_compat_claim_payload` | GET /queue → 200 + claim=none + no deprecation headers | GET /queue → 200 + claim still in payload (null) | RETAIN (queue still works) **BUT update mock** — monkeypatch includes `claim: {...}` dict in mock response; after H14B queue loop removal, queue items still have `"claim": None` hardcoded in service, so this test remains valid. However, the `claim_payload=true` description is misleading post-removal. |
| `test_station_session_endpoint_does_not_receive_claim_deprecation_headers` | GET /sessions/current → 200 + no deprecation headers | Still valid (session endpoint unchanged) | RETAIN — fully valid test |

**Recommendation:** Delete entire `test_claim_api_deprecation_lock.py` in H14B. The 2 retained tests (`test_station_queue_endpoint...` and `test_station_session_endpoint...`) are edge-case compat tests that either test moot behavior (queue now always null) or are better expressed as broader session endpoint tests. The 3 deprecated-route tests become meaningless after removal.

**Alternative:** Rewrite only the 2 valid tests and delete the file, moving them to `test_station_queue_active_states.py` or `test_station_queue_session_aware_migration.py` if the session endpoint assertion is not already covered.

---

## 7. Queue-Loop / Service Dependency Map

| Function / Block | Current Caller | Runtime Role After H12B | Remove in H14B? | Defer? | Risk |
|---|---|---|---|---|---|
| Queue claim query (select `OperationClaim`) | `get_station_queue()` | Queries active claims → feeds expiry → builds `claims` dict | YES — remove block | — | MEDIUM (must keep surrounding queue logic) |
| `_expire_claim_if_needed()` call | `get_station_queue()` (queue loop) | Writes `CLAIM_EXPIRED` to `operation_claim_audit_logs`; mutates claim row | YES — remove call | — | **HIGH (BLOCKER for H16)** |
| `claims` dict | `get_station_queue()` | Populated from queried claims; always results in `None` after expiry | YES — remove | — | LOW |
| `_to_claim_state()` call | Inside queue loop block | Maps claim to "mine"/"other"/"none"; result was never exposed in queue payload since H10 | YES — remove call | Function body defer to H15 | LOW |
| `get_station_queue()` (whole function) | `station.py` route `/queue` | **ACTIVE — must remain intact** | NO | — | NONE |
| `"claim": None` hardcoded in queue item | `get_station_queue()` return | Null-only response stability; `StationQueueResponse` still includes `claim` field in Pydantic schema | RETAIN until schema/response contract is revised | H15 schema cleanup | LOW |
| `claim_operation()` | No active caller | Dead service code | NO | H15 | NONE |
| `release_operation_claim()` | No active caller | Dead service code | NO | H15 | NONE |
| `get_operation_claim_status()` | No active caller | Dead service code | NO | H15 | NONE |
| `_log_claim_event()` | `_expire_claim_if_needed()` from queue loop + dead service functions | Writes audit event rows | Remove from queue loop path in H14B; defer function deletion to H15 | H15 | LOW |
| `_get_unreleased_claim_for_update()` | Dead service functions only | No active caller after H12B | NO | H15 | NONE |
| `_get_operator_unreleased_claims_for_station_for_update()` | Dead `claim_operation()` | No active caller | NO | H15 | NONE |
| `_validate_operation_for_station()` | Dead `claim_operation()` | No active caller | NO | H15 | NONE |
| `_validate_operation_for_active_claim_context()` | Dead `release_operation_claim()`, `get_operation_claim_status()` | No active caller | NO | H15 | NONE |
| `_has_admin_support_override()` | Dead `release_operation_claim()` | No active caller | NO | H15 | NONE |
| `ensure_operation_claim_owned_by_identity()` | Zero callers anywhere | Was execution route claim guard (H4 removed) | NO | H15 | NONE |
| `ClaimConflictError` | Dead `claim_operation()`; `test_claim_single_active_per_operator.py` | No active runtime caller | NO | H15 | NONE |
| `_to_claim_state()` function body | Queue loop (call removed in H14B) | Dead function after H14B | Remove call in H14B; defer function deletion to H15 | H15 | LOW |
| `ensure_operator_context()` | `get_station_queue()`, `get_station_scoped_operation()`, `claim_operation()` et al | **ACTIVE** — still guards queue and scoped operation routes | RETAIN | — | NONE |
| `resolve_station_scope()` | `get_station_queue()`, `get_station_scoped_operation()`, claim functions (dead) | **ACTIVE** — still resolves station scope for queue | RETAIN | — | NONE |
| `get_station_scoped_operation()` | `station.py` route `/detail` | **ACTIVE** | RETAIN | — | NONE |
| `StationScopeContext` dataclass | `get_station_queue()`, `resolve_station_scope()` | **ACTIVE** | RETAIN | — | NONE |
| `_normalize_role()` | `_effective_role()` | **ACTIVE** | RETAIN | — | NONE |
| `_effective_role()` | `ensure_operator_context()` | **ACTIVE** | RETAIN | — | NONE |
| `_to_session_owner_state()` | `get_station_queue()` ownership block | **ACTIVE** | RETAIN | — | NONE |

### Queue-Loop Surgical Removal Boundary

The removal target inside `get_station_queue()` is precisely this block:

```python
# REMOVE THIS BLOCK IN H14B (lines ~352–381 of station_claim_service.py)
active_operation_ids = [operation.id for operation, _wo, _po in active_rows]
claims = {}
if active_operation_ids:
    claim_rows = list(
        db.scalars(
            select(OperationClaim).where(
                OperationClaim.tenant_id == identity.tenant_id,
                OperationClaim.operation_id.in_(active_operation_ids),
                OperationClaim.released_at.is_(None),
            )
        )
    )
    for claim in claim_rows:
        claims[claim.operation_id] = _expire_claim_if_needed(
            db, claim, identity=identity
        )
```

After removal, `db.commit()` below this block must be verified — it was committing expiry mutations. Since no mutations remain, it may be simplified or kept (safe either way — empty commit is a no-op).

The `"claim": None` line in the item dict must be **kept** for response stability (Pydantic still validates it).

The `claims[operation.id]` lookup in the item loop (if present) must also be removed:
```python
# REMOVE: any "claim": _to_claim_state(identity, claims.get(operation.id)) or similar
# KEEP: "claim": None
```

After checking the source, the item construction at line ~384–418 already uses `"claim": None` hardcoded (not `claims.get(...)`). The `claims` dict is never used in the item construction — this was already cleaned to null in H10. So queue-loop removal is **clean**: remove only the claim query block; item dict is unaffected.

**The `db.commit()` after the query block** — after claim expiry removal, the commit is only needed if other mutations exist. In the current code, `db.commit()` commits any expiry mutations written by `_expire_claim_if_needed()`. After removal, `db.commit()` is a no-op in the queue read path. It is safe to keep but may optionally be removed to avoid unnecessary transactions. **Recommendation: keep it** to minimize diff surface.

---

## 8. Data / Migration Boundary Map

| Data Object | Current Runtime Caller | Can Remove in H14B? | Future Slice |
|---|---|---|---|
| `OperationClaim` model (Python ORM) | `station_claim_service.py` (queue loop — BEING REMOVED in H14B; dead service functions); `init_db.py` (SQLAlchemy table registration) | NO — still registered; `init_db.py` import must remain | H15 |
| `OperationClaimAuditLog` model (Python ORM) | Same as above | NO | H15 |
| `operation_claims` table (PostgreSQL) | SQLAlchemy-mapped; no new rows after H14B queue loop removal | NO — requires Alembic migration | H16 |
| `operation_claim_audit_logs` table | Same | NO | H16 (after H15) |
| `0009_station_claims.sql` | History doc — never executed by Alembic | RETAIN permanently | — |
| Alembic versions (0001–0003) | Active DB schema state | Not touched | H16 (new revision `0004_drop_claim_tables`) |
| Test fixtures creating `OperationClaim` rows | `test_execution_route_claim_guard_removal.py` — `_insert_active_claim()` helper; teardown in 3 test suites | `_insert_active_claim()` in guard test ONLY — REMOVE in H14B (see note below) | Others defer to H16 |
| Test teardown deleting `OperationClaim` rows | `test_execution_route_claim_guard_removal.py`, `test_operation_detail_allowed_actions.py`, `test_operation_status_projection_reconcile.py` | See teardown analysis below | UPDATE teardown in H14B |

### Teardown Analysis

**`test_execution_route_claim_guard_removal.py`:**
- The `_insert_active_claim()` helper creates `OperationClaim` rows to test the old claim-based guard.
- After H4, the claim guard was removed — `test_valid_station_session_without_claim_succeeds_for_h4_commands` and `test_active_claim_cannot_bypass_missing_station_session` and `test_conflicting_claim_no_longer_blocks_valid_station_session` may still use this helper.
- **These specific tests** (`test_active_claim_cannot_bypass_missing_station_session`, `test_conflicting_claim_no_longer_blocks_valid_station_session`) still insert `OperationClaim` rows to prove that a **conflicting claim no longer blocks a valid session**. This is still a valuable negative test.
- **Recommendation:** Retain these specific tests until H16 (they prove `OperationClaim` does not affect session-gated routes). Remove teardown claim-delete stmts in **all** test files in H14B — since H12B claims are no longer created by production routes, the teardown deletes are already no-ops.
- After H16 table drop, all `_insert_active_claim()` calls and teardown stmts must be removed.

**`test_operation_detail_allowed_actions.py` teardown:** Claim delete in teardown is a no-op since no claim rows are created by these tests' production path. Remove teardown claim delete stmts in H14B.

**`test_operation_status_projection_reconcile.py` teardown:** Same — remove teardown stmts in H14B.

**Caution:** Removing teardown stmts now is safe because:
1. No production path creates new claim rows after H12B.
2. The only remaining writer (`_expire_claim_if_needed` in queue loop) is being removed in H14B.
3. Test isolation is maintained via `db_session` fixture which rollbacks after each test in most suites.

---

## 9. Claim Route Removal Decision

| Route | Current Behavior | Remove in H14B? | Replacement Behavior | Test Strategy |
|---|---|---|---|---|
| `POST /queue/{id}/claim` | HTTP 410 + `CLAIM_API_DISABLED` + deprecation headers | YES | Route removed → HTTP 404 or 405 on unregistered path | Delete 3 tests in `test_claim_api_deprecation_lock.py` that asserted 410 |
| `POST /queue/{id}/release` | HTTP 410 + `CLAIM_API_DISABLED` | YES | Same as above | Same |
| `GET /queue/{id}/claim` | HTTP 410 + `CLAIM_API_DISABLED` | YES | Same | Same |

**Decision: REMOVE all 3 routes in H14B.**

Rationale:
- No active consumer has called these routes since H12B.
- They are pure dead code returning a static error.
- Removing them eliminates future confusion and the `CLAIM_API_DISABLED` response code from live API surface.
- No rollback risk — no system depends on the 410 response; the 404 is an equally clear signal.
- `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` imports from `station.py` can all be removed since they are ONLY used as type annotations for the 3 disabled routes.

**What remains active in `station.py` after route removal:**
- `GET /queue` — untouched
- `GET /queue/{id}/detail` — untouched
- `get_station_queue` and `get_station_scoped_operation` imports from service — retained
- `get_db` — retained
- `StationQueueItem`, `StationQueueResponse` — retained (used by `/queue` route)

---

## 10. Frontend Client Removal Decision

| Frontend Artifact | Current Usage | Remove in H14B? | Risk |
|---|---|---|---|
| `stationApi.claim()` | Zero callers in `frontend/src/**` | YES | LOW |
| `stationApi.release()` | Zero callers | YES | LOW |
| `stationApi.getClaim()` | Zero callers | YES | LOW |
| `ClaimSummary` interface | Only referenced in: `StationQueueItem.claim` (being removed) and `index.ts` re-export (being removed) | YES | LOW |
| `QueueClaimState` type | Only referenced in `ClaimSummary`, `ClaimResponse`, `getClaim` return — all being removed | YES | LOW |
| `ClaimResponse` interface | Only in `claim()` and `release()` stubs (being removed) | YES | LOW |
| `StationQueueItem.claim` field | Backend always delivers `null`; zero component reads confirmed by grep | YES | LOW |
| `QueueClaimState` re-export in `index.ts` | No downstream imports in frontend source | YES | LOW |
| `ClaimSummary` re-export in `index.ts` | No downstream imports | YES | LOW |
| `ClaimResponse` re-export in `index.ts` | No downstream imports | YES | LOW |
| `station.claim.*` i18n keys (en.ts, ja.ts) | Used in `StationExecution.tsx`, `QueueOperationCard.tsx`, `StationExecutionHeader.tsx` as translated UI strings | NO — these are i18n display keys, NOT claim type dependencies | RETAIN |

**IMPORTANT FINDING — `station.claim.*` i18n keys:**
These keys (`station.claim.required`, `station.claim.ownedBadge`, `station.claim.takenWarning`, `station.claim.singleActiveHint`) were originally labelled "claim" because they described the claim UX. After H2+, the components driving these strings switched to **ownership-based logic** — they use `item.ownership?.owner_state`, not `item.claim`. The keys remain valid as UX feedback strings (e.g., "owned badge" now means "you have an active session at this station"). Renaming them is cosmetic work, out of scope for H14B.

**Decision: REMOVE all frontend claim API artifacts in H14B. RETAIN i18n keys.**

**TypeScript compile safety:** After removing `StationQueueItem.claim`, any code reading `item.claim` would fail to compile. Grep confirms zero such consumers → build remains valid.

---

## 11. Queue-Loop Cleanup Decision

| Queue Code Path | Current Behavior | Remove in H14B? | Risk |
|---|---|---|---|
| `active_operation_ids` list comprehension (feeds claim query) | Built from `active_rows`; only used for claim query | YES — remove the entire block from `if active_operation_ids:` | LOW (the same list is built again implicitly in item loop below; remove only this pre-fetch) |
| `claim_rows` query (`select OperationClaim...`) | Queries `OperationClaim` table for active claims | YES | LOW |
| `claims` dict construction | Populated from `claim_rows`; feeds `_expire_claim_if_needed` | YES | LOW |
| `_expire_claim_if_needed(db, claim, identity=identity)` call | Mutates claim row; writes `CLAIM_EXPIRED` audit event; calls `_log_claim_event()` | YES — HIGHEST PRIORITY REMOVAL | **HIGH (BLOCKER for H16)** |
| `claims[claim.operation_id] = ...` assignment | Stores `None` or expiry result back in dict | YES (removed with block) | LOW |
| `db.commit()` after claim block | Commits expiry mutations; after removal → no-op | KEEP — safe no-op, minimize diff | NONE |
| `"claim": None` in item dict | Hardcoded null; response stability | RETAIN | NONE |
| `active_operation_ids` variable name reuse in item loop | None — the list is not reused; the loop uses `active_rows` directly | N/A | NONE |
| `_to_claim_state()` call (if any in item construction) | Not present in item dict — already removed in H10; dict uses `"claim": None` | NONE — already clean | NONE |

**Decision: REMOVE queue claim expiration block in H14B. Retain `"claim": None` in item dict and `db.commit()`.**

**Exact surgical boundary:** Remove lines from `active_operation_ids = [...]` before the claim query through `db.commit()` after the claim expiry loop, keeping the `db.commit()` itself. Wait — re-reading the code:

```python
# Lines in get_station_queue():
active_operation_ids = [operation.id for operation, _wo, _po in active_rows]  # KEEP? REMOVE?
claims = {}                                                                    # REMOVE
if active_operation_ids:                                                       # REMOVE
    claim_rows = list(db.scalars(...))                                         # REMOVE
    for claim in claim_rows:                                                   # REMOVE
        claims[claim.operation_id] = _expire_claim_if_needed(...)             # REMOVE

db.commit()   # KEEP (safe no-op after removal)
```

The `active_operation_ids` variable is **only** used for the claim query. It is not referenced anywhere else in `get_station_queue()`. → **Remove `active_operation_ids` variable too.**

After removal, `OperationClaim` import in `station_claim_service.py` becomes used only by dead service functions (`claim_operation`, `release_operation_claim`, etc.). The import itself can remain until H15 when the dead functions are deleted. However, if linting catches the import as potentially unused (due to removal of the queue block), it should be noted that the dead service functions still reference the symbol. **No linting issue expected** — dead functions still import it.

---

## 12. Claim Service / Model / Table Deferral Decision

| Artifact | Remove in H14B? | Reason | Future Slice |
|---|---|---|---|
| `claim_operation()` function | NO | Dead code but service tests (`test_claim_single_active_per_operator.py`) still import it | H15 |
| `release_operation_claim()` function | NO | Same | H15 |
| `get_operation_claim_status()` function | NO | Same | H15 |
| `_log_claim_event()` function | NO | Still called by `claim_operation()` etc (defer with parent); queue call removed in H14B | H15 |
| `_get_unreleased_claim_for_update()` | NO | Dead; defer with parent functions | H15 |
| `_get_operator_unreleased_claims_for_station_for_update()` | NO | Same | H15 |
| `_to_claim_state()` | Queue call removed in H14B; function body remains | Defer function deletion | H15 |
| `_validate_operation_for_station()` | NO | Dead | H15 |
| `_validate_operation_for_active_claim_context()` | NO | Dead | H15 |
| `_has_admin_support_override()` | NO | Dead | H15 |
| `ensure_operation_claim_owned_by_identity()` | NO | Zero callers but defer for clean slice | H15 |
| `ClaimConflictError` | NO | Test file still imports it | H15 |
| `ClaimRequest` schema | NO | Schema type only; import removed from `station.py` in H14B | H15 |
| `ReleaseClaimRequest` schema | NO | Same | H15 |
| `ClaimResponse` schema | NO | Same | H15 |
| `OperationClaim` ORM model + file | NO | `init_db.py` import + dead service functions still reference | H15 |
| `OperationClaimAuditLog` ORM model | NO | Same | H15 |
| `station_claim.py` model file | NO | Delete entire file in H15 | H15 |
| `operation_claims` table | NO | Requires Alembic migration | H16 |
| `operation_claim_audit_logs` table | NO | Requires Alembic migration; FK child → drop before parent | H16 |
| `test_claim_single_active_per_operator.py` | NO | Needs `claim_operation()` service to exist | H15 (delete with service) |
| `test_release_claim_active_states.py` | NO | Same | H15 |

---

## 13. H14B Implementation Scope Proposal

**Slice name:** `P0-C-08H14B Claim Route / Frontend Client / Queue-Loop Removal Implementation`

### H14B In Scope

| H14B Candidate Action | Files | Tests Required | Risk |
|---|---|---|---|
| Remove `POST .../claim` route definition and signature | `backend/app/api/v1/station.py` | `test_claim_api_deprecation_lock.py` → delete file | LOW |
| Remove `POST .../release` route definition and signature | `backend/app/api/v1/station.py` | Same | LOW |
| Remove `GET .../claim` route definition and signature | `backend/app/api/v1/station.py` | Same | LOW |
| Remove `_raise_claim_api_disabled()` helper | `backend/app/api/v1/station.py` | None | LOW |
| Remove `_CLAIM_DISABLED_HEADERS` dict | `backend/app/api/v1/station.py` | None | LOW |
| Remove `add_claim_api_deprecation_headers()` (dead, never called) | `backend/app/api/v1/station.py` | None | LOW |
| Remove `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` imports | `backend/app/api/v1/station.py` | None | LOW |
| Remove `Response` import from FastAPI if no longer used | `backend/app/api/v1/station.py` | None | LOW — verify it's only used by claim routes |
| Remove queue claim query block from `get_station_queue()` | `backend/app/services/station_claim_service.py` | Queue tests must pass; run `test_station_queue_active_states.py` | MEDIUM |
| Remove `_expire_claim_if_needed()` call from queue loop | `backend/app/services/station_claim_service.py` | Queue tests | HIGH — BLOCKER removed |
| Remove `claims` dict and `active_operation_ids` variable from queue | `backend/app/services/station_claim_service.py` | Queue tests | LOW |
| Delete `test_claim_api_deprecation_lock.py` | `backend/tests/` | N/A | LOW |
| Remove teardown claim delete stmts from `test_execution_route_claim_guard_removal.py` | `backend/tests/` | Run the test suite | LOW |
| Remove teardown claim delete stmts from `test_operation_detail_allowed_actions.py` | `backend/tests/` | Run the test suite | LOW |
| Remove teardown claim delete stmts from `test_operation_status_projection_reconcile.py` | `backend/tests/` | Run the test suite | LOW |
| Remove `stationApi.claim()`, `stationApi.release()`, `stationApi.getClaim()` | `frontend/src/app/api/stationApi.ts` | Frontend lint + build | LOW |
| Remove `ClaimSummary`, `QueueClaimState`, `ClaimResponse` interfaces | `frontend/src/app/api/stationApi.ts` | Frontend lint + build | LOW |
| Remove `StationQueueItem.claim` field | `frontend/src/app/api/stationApi.ts` | Frontend build (TypeScript compile) | LOW |
| Remove `QueueClaimState`, `ClaimSummary`, `ClaimResponse` from `index.ts` exports | `frontend/src/app/api/index.ts` | Frontend build | LOW |
| Update trackers and create implementation report | `docs/implementation/` | N/A | NONE |

### H14B Out of Scope

| Item | Reason | Future Slice |
|---|---|---|
| `OperationClaim` ORM model deletion | `init_db.py` import; dead service functions still reference | H15 |
| `OperationClaimAuditLog` ORM model deletion | Same | H15 |
| `models/station_claim.py` file deletion | Entire model file deferred | H15 |
| `claim_operation()`, `release_operation_claim()`, `get_operation_claim_status()` deletion | Service tests still import them | H15 |
| `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` schema types in `schemas/station.py` | Schema types retained until service removal | H15 |
| `test_claim_single_active_per_operator.py` deletion | Needs service functions to exist | H15 |
| `test_release_claim_active_states.py` deletion | Same | H15 |
| `test_execution_route_claim_guard_removal.py` full deletion | Tests still valid (prove claim no longer blocks session) | H16 |
| `operation_claims` table drop | Alembic migration required | H16 |
| `operation_claim_audit_logs` table drop | Same; FK order required | H16 |
| Audit row deletion | Included in table drop migration | H16 |
| `verify_station_claim.py`, `verify_station_queue_claim.py` script cleanup | Deferred | H-I |
| `verify_clock_on.py`, `verify_clock_off.py` claim teardown | Deferred | H16 |
| `station.claim.*` i18n key rename/removal | Cosmetic; not a claim API dependency | Out of scope (H-I or later) |
| StationSession behavior changes | Not touched | N/A |
| Frontend UI changes | Not needed | N/A |
| DB migration creation | Deferred | H16 |

### H14B Verification Plan

After implementation:

1. `pytest -q tests/test_station_queue_active_states.py tests/test_station_queue_session_aware_migration.py` — queue tests must pass; claim field arrives null
2. `pytest -q tests/test_execution_route_claim_guard_removal.py` — guard tests must pass (claim rows still insertable for negative tests)
3. `pytest -q tests/test_operation_detail_allowed_actions.py tests/test_operation_status_projection_reconcile.py` — updated teardown must not fail
4. `pytest -q tests/test_reopen_resume_station_session_continuity.py tests/test_reopen_resumability_claim_continuity.py tests/test_reopen_operation_claim_continuity_hardening.py` — reopen tests unaffected
5. Full backend suite: confirm claim-disabled tests are gone; service tests still pass
6. Frontend: `npm run lint && npm run build && npm run check:routes` — all must exit 0

---

## 14. H15 / H16 Roadmap

| Slice | Goal | Code? | Migration? | Preconditions | Stop Conditions |
|---|---|---|---|---|---|
| **H15** P0-C-08H15 Claim Service / Schema / Model Removal | Delete all dead claim service functions, schemas, model file, and service-level tests | YES | NO | H14B complete; routes removed; FE types removed; queue loop clean | Any non-disabled route still calls claim service; `test_claim_single_active_per_operator.py` must be deleted first |
| **H16** P0-C-08H16 Claim Table Drop Migration | Alembic migration `0004_drop_claim_tables`; drop both tables | NO code (Alembic migration only) | YES | H15 complete; ORM models deleted; all teardown updated; `_expire_claim_if_needed` removed (H14B); no active DB writes to claim tables | ORM model file still exists; any test imports `OperationClaim`/`OperationClaimAuditLog`; any active writer to claim tables remains |
| **H17 / H-I** P0-C-08I Claim Retirement Closeout | Repo sweep; delete verify scripts; final regression; update docs | YES (minor) | NO | H16 complete | `rg` sweep finds claim terms in active source |

### H15 Detailed Scope

- Delete `claim_operation()`, `release_operation_claim()`, `get_operation_claim_status()`, `_log_claim_event()`, `_get_unreleased_claim_for_update()`, `_get_operator_unreleased_claims_for_station_for_update()`, `_to_claim_state()`, `_validate_operation_for_station()`, `_validate_operation_for_active_claim_context()`, `_has_admin_support_override()`, `ensure_operation_claim_owned_by_identity()`, `ClaimConflictError` from `station_claim_service.py`
- Remove `OperationClaim`, `OperationClaimAuditLog` imports from `station_claim_service.py`
- Delete `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` from `backend/app/schemas/station.py`
- Delete `backend/app/models/station_claim.py`
- Remove `OperationClaim`, `OperationClaimAuditLog` import from `backend/app/db/init_db.py`
- Delete `backend/tests/test_claim_single_active_per_operator.py`
- Delete `backend/tests/test_release_claim_active_states.py`
- Delete `backend/scripts/seed/seed_station_execution_opr.py` claim imports or update
- Run `rg OperationClaim|OperationClaimAuditLog` across `backend/app/**` → must return 0 results

### H16 Detailed Scope

- New Alembic revision: `0004_drop_claim_tables`
- Upgrade:
  ```sql
  DROP TABLE IF EXISTS operation_claim_audit_logs;  -- FK child first
  DROP TABLE IF EXISTS operation_claims;
  ```
- Downgrade (for rollback safety):
  ```sql
  CREATE TABLE operation_claims (...);
  CREATE TABLE operation_claim_audit_logs (...);
  -- Add FKs back
  ```
- Update `test_execution_route_claim_guard_removal.py`: remove `_insert_active_claim()` helper and all claim teardown
- Update `backend/scripts/verify_clock_on.py` and `verify_clock_off.py`: remove claim delete teardown
- Run: `alembic upgrade head` → confirm tables do not exist in DB
- Run: `alembic downgrade -1` + `alembic upgrade head` round-trip

---

## 15. Test Strategy

| Test File | Current Claim Dependency | H14B Expected Action | H15 | H16 |
|---|---|---|---|---|
| `test_claim_api_deprecation_lock.py` | 3 tests assert 410 + `CLAIM_API_DISABLED`; 2 test non-deprecated endpoints | DELETE entire file in H14B | — | — |
| `test_station_queue_active_states.py` | Queue tests; no direct claim assert; tests verify `claim` field present but null | RETAIN; verify queue response still includes `"claim": null` | — | — |
| `test_station_queue_session_aware_migration.py` | Queue migration tests | RETAIN unmodified | — | — |
| `test_execution_route_claim_guard_removal.py` | Inserts `OperationClaim` rows; teardown deletes claim rows | RETAIN body; REMOVE teardown claim deletes (now no-op); RETAIN `_insert_active_claim()` until H16 — these tests prove claim no longer blocks valid session | — | REMOVE `_insert_active_claim()` + teardown |
| `test_operation_detail_allowed_actions.py` | Teardown deletes claim rows (no-op since H12B) | REMOVE teardown claim delete stmts | — | — |
| `test_operation_status_projection_reconcile.py` | Same | REMOVE teardown claim delete stmts | — | — |
| `test_claim_single_active_per_operator.py` | 6 tests call `claim_operation()` directly | DEFER — do not touch | DELETE | — |
| `test_release_claim_active_states.py` | 14 tests call `release_operation_claim()` | DEFER — do not touch | DELETE | — |
| `test_reopen_resume_station_session_continuity.py` | No claim dependency | RETAIN unmodified | — | — |
| `test_reopen_resumability_claim_continuity.py` | No claim dependency | RETAIN unmodified | — | — |
| `test_reopen_operation_claim_continuity_hardening.py` | No claim dependency | RETAIN unmodified | — | — |
| `test_close_operation_auth.py` et al | No claim dependency | RETAIN unmodified | — | — |
| Frontend lint | Build smoke | PASS after removal | — | — |
| Frontend build | TypeScript compile | PASS after removal (zero consumers of removed types) | — | — |
| Frontend check:routes | Route coverage | PASS unchanged | — | — |
| `pytest -q` (full suite) | Full suite minus deleted files | Pass — count decreases by: 5 (`test_claim_api_deprecation_lock.py` deleted) | Decreases by 6+14 | — |

---

## 16. Risk Register

| Risk | Probability | Severity | Mitigation |
|---|---|---|---|
| Queue route breaks if claim block removal takes adjacent code | LOW | HIGH | Surgical removal — exact lines specified above; queue test suite run immediately after |
| `Response` import still needed after removing claim routes | LOW | LOW | Verify — `Response` used only as parameter type in claim route signatures; remove if unused |
| `station.claim.*` i18n key references mistakenly removed | LOW | MEDIUM | Explicitly noted: i18n keys are NOT removed in H14B |
| `StationQueueItem.claim` removal causes TypeScript error in unconventional import | VERY LOW | MEDIUM | Grep confirms zero consumers; build + TypeScript strict mode confirms |
| `test_execution_route_claim_guard_removal.py` teardown removal breaks isolation | LOW | MEDIUM | Teardown deletes were already no-ops; test isolation via `db_session` fixture rollback |
| `db.commit()` inside queue kept causes confusion | VERY LOW | NONE | Kept as explicit decision; comment to be added noting it's a no-op after claim loop removal |
| `ensure_operation_claim_owned_by_identity()` is secretly called somewhere not found by grep | VERY LOW | HIGH | Backend grep of `backend/app/**` shows 1 match (definition only); no callers in app code |
| Frontend `index.ts` re-export removal breaks external consumer | VERY LOW | LOW | Confirmed zero downstream imports; TypeScript build catches any remaining consumer |
| H14B touches the `StationQueueResponse` Pydantic schema | NONE | N/A | Queue response schema is not touched in H14B; `claim: ClaimSummary \| null` field remains in schema until H15 |

---

## 17. Recommendation

**Proceed with `P0-C-08H14B` as defined in Section 13.**

Priority order for implementation:

1. **FIRST:** Remove `_expire_claim_if_needed()` call and surrounding claim query block from `get_station_queue()` — this is the BLOCKER for H16 and must go first.
2. Remove 3 claim API route definitions from `station.py` + `_raise_claim_api_disabled()` + `_CLAIM_DISABLED_HEADERS` + `add_claim_api_deprecation_headers()`.
3. Remove schema imports (`ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse`) from `station.py`.
4. Remove `stationApi.claim/release/getClaim` + claim types from `stationApi.ts`.
5. Remove claim re-exports from `index.ts`.
6. Delete `test_claim_api_deprecation_lock.py`.
7. Update teardown in 3 test files.

**Should CLAIM_API_DISABLED remain in canonical error docs?**
The `CLAIM_API_DISABLED` string is a runtime error detail (not a registered canonical error code in the error code registry). It was used only by the disabled routes being removed. After route removal, `CLAIM_API_DISABLED` no longer appears in any API response. Recommendation: retain in docs as a historical note (annotate as "retired in H14B") rather than deleting the documentation, since H-series reports reference it.

**Queue-Loop verdict:** Evidence shows queue-loop claim expiration can be removed cleanly in H14B. The `_expire_claim_if_needed()` function is only called from the queue loop; no other active caller exists. The `claims` dict result was never used in item construction (already null-only since H10). This is a `READY_FOR_P0_C_08H14B_ROUTE_CLIENT_QUEUE_LOOP_REMOVAL_IMPLEMENTATION` verdict.

---

## 18. Final Verdict

```text
READY_FOR_P0_C_08H14B_ROUTE_CLIENT_QUEUE_LOOP_REMOVAL_IMPLEMENTATION
```

| Decision Point | Answer |
|---|---|
| Claim route removal ready? | YES — all 3 routes; no active consumers |
| Frontend client removal ready? | YES — all 3 functions + 3 types + `claim` field; zero consumers confirmed |
| Queue-loop expiration removal ready? | YES — `_expire_claim_if_needed()` call and surrounding block; zero active consumers of result |
| Model/table/migration boundary held? | YES — model, table, Alembic migration deferred to H15/H16 |
| Service function removal (non-queue) deferred? | YES — `claim_operation`, `release_operation_claim`, `get_operation_claim_status` deferred to H15 |
| `ensure_operation_claim_owned_by_identity()` deferred? | YES — dead code but clean slice boundary |
| Schema types (`ClaimRequest` et al) deferred? | YES — import removed from `station.py` in H14B; type definitions deferred to H15 |
| `test_claim_api_deprecation_lock.py` action? | DELETE entire file in H14B |
| Teardown cleanup in 3 test files? | UPDATE in H14B (no-op removal) |
| `test_execution_route_claim_guard_removal.py` action? | RETAIN body; remove teardown claim deletes; retain `_insert_active_claim()` until H16 |
| `test_claim_single_active_per_operator.py` / `test_release_claim_active_states.py` action? | DEFER DELETE to H15 |
| `station.claim.*` i18n keys? | RETAIN — not claim API dependencies |
| `db.commit()` after claim removal? | RETAIN as no-op (safe; minimal diff) |
| `"claim": None` in queue item dict? | RETAIN for response stability |
| Next slice? | P0-C-08H14B Implementation |

---

## Verification Results (H14 Contract Baseline Smoke)

| Check | Result |
|---|---|
| Backend compat smoke (`test_claim_api_deprecation_lock.py` + guard + queue) | `27 passed`, `H14_COMPAT_SMOKE_EXIT:0` |
| Backend reopen smoke | `22 passed`, `H14_REOPEN_SMOKE_EXIT:0` |
| Frontend lint | `H14_FRONTEND_LINT_EXIT:0` |
| Frontend build | `H14_FRONTEND_BUILD_EXIT:0` |
| Frontend route smoke | `H14_FRONTEND_ROUTE_SMOKE_EXIT:0` |

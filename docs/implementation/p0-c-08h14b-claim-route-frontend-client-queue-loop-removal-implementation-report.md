# P0-C-08H14B Claim Route / Frontend Client / Queue-Loop Removal Implementation

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Removed disabled claim API routes, frontend claim client surface, and queue-loop claim expiration remnants. Model/table/service deferred. |

---

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Implementation
- Hard Mode MOM: v3
- Reason: Legacy claim API route removal, frontend API client removal, queue-loop `CLAIM_EXPIRED` emission removal, execution ownership truth, staged hard-removal of legacy operational data path — all v3 trigger zones.

---

## 1. Executive Summary

H14B implements the first hard-removal slice approved by H13 policy and H14 contract. All 3 disabled claim API routes have been removed from `station.py`, the frontend claim API client surface has been eliminated from `stationApi.ts` and `index.ts`, and the queue-loop claim expiration block (the critical H16 blocker) has been surgically removed from `get_station_queue()`.

No model, table, migration, service function, or audit row was touched. StationSession ownership projection, queue behavior, and all execution commands are unaffected.

---

## 2. Scope and Non-Scope

### In Scope — Completed

| Item | Status |
|---|---|
| Remove 3 disabled claim API route definitions from `station.py` | ✅ DONE |
| Remove `_raise_claim_api_disabled()` helper | ✅ DONE |
| Remove `_CLAIM_DISABLED_HEADERS` dict | ✅ DONE |
| Remove `add_claim_api_deprecation_headers()` dead function | ✅ DONE |
| Remove `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` imports from `station.py` | ✅ DONE |
| Remove `Response` import from `station.py` | ✅ DONE |
| Remove queue claim expiry block from `get_station_queue()` | ✅ DONE |
| Remove `_expire_claim_if_needed()` call from queue (BLOCKER for H16) | ✅ DONE |
| Remove `active_operation_ids` and `claims` dict from queue loop | ✅ DONE |
| Remove `stationApi.claim()`, `stationApi.release()`, `stationApi.getClaim()` | ✅ DONE |
| Remove `QueueClaimState`, `ClaimSummary`, `ClaimResponse` types from `stationApi.ts` | ✅ DONE |
| Remove `StationQueueItem.claim` field | ✅ DONE |
| Remove claim type re-exports from `frontend/src/app/api/index.ts` | ✅ DONE |
| Delete `test_claim_api_deprecation_lock.py` | ✅ DONE |
| Remove teardown claim delete stmts from `test_operation_detail_allowed_actions.py` | ✅ DONE |
| Remove teardown claim delete stmts from `test_operation_status_projection_reconcile.py` | ✅ DONE |
| Remove unused `OperationClaim/OperationClaimAuditLog` imports from those 2 test files | ✅ DONE |

### Out of Scope — Deferred

| Item | Deferred To |
|---|---|
| `OperationClaim` ORM model | H15 |
| `OperationClaimAuditLog` ORM model | H15 |
| `claim_operation()`, `release_operation_claim()`, `get_operation_claim_status()` | H15 |
| `_expire_claim_if_needed()` function body | H15 |
| `_log_claim_event()`, `_to_claim_state()`, claim helpers | H15 |
| `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse` schema types | H15 |
| `test_claim_single_active_per_operator.py` | H15 |
| `test_release_claim_active_states.py` | H15 |
| `_insert_active_claim()` in test_execution_route_claim_guard_removal.py | H16 |
| `operation_claims` table | H16 |
| `operation_claim_audit_logs` table | H16 |
| Alembic migration `0004_drop_claim_tables` | H16 |
| Verify scripts: `verify_station_claim.py`, `verify_station_queue_claim.py` | H-I |
| Seed scripts referencing claim models | H15 |

---

## 3. Hard Mode Gate Evidence

### Design Evidence Extract

| Fact | Source | Confirmed |
|---|---|---|
| StationSession is ownership truth | `station-session-ownership-contract.md`; queue `ownership` block | ✅ |
| Claim API was runtime-disabled HTTP 410 since H12B | H12B report; `_raise_claim_api_disabled()` removed in H14B | ✅ |
| Queue claim payload null-only since H10 | H10 report; `"claim": None` hardcoded in item dict; RETAINED | ✅ |
| Reopen claim restoration removed since H11B | H11B report | ✅ |
| H13 `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED` | H13 policy document | ✅ |
| H14 `READY_FOR_P0_C_08H14B_ROUTE_CLIENT_QUEUE_LOOP_REMOVAL_IMPLEMENTATION` | H14 contract | ✅ |
| `_expire_claim_if_needed()` was BLOCKER for H16 | H14 contract § 7; source confirmed | ✅ RESOLVED |
| Frontend claim functions zero callers | H14 contract grep results | ✅ |
| H14B does NOT remove model/table/migration | H14 contract § 2, § 8 | ✅ HELD |

---

## 4. Source Usage Inventory

### Backend Changes

| File | What Changed |
|---|---|
| `backend/app/api/v1/station.py` | Removed `Response` import; removed 3 claim schema imports; removed `add_claim_api_deprecation_headers()`, `_CLAIM_DISABLED_HEADERS`, `_raise_claim_api_disabled()`; removed 3 claim route definitions |
| `backend/app/services/station_claim_service.py` | Removed queue claim expiry block: `active_operation_ids` list + `claims = {}` + `if active_operation_ids: ...` + `_expire_claim_if_needed()` call |

### Frontend Changes

| File | What Changed |
|---|---|
| `frontend/src/app/api/stationApi.ts` | Removed `QueueClaimState`, `ClaimSummary`, `ClaimResponse` types; removed `StationQueueItem.claim` field; removed `stationApi.claim()`, `stationApi.release()`, `stationApi.getClaim()` methods; removed unused `STATION_BASE_PATH` (kept for `getOperationDetail`) |
| `frontend/src/app/api/index.ts` | Removed `QueueClaimState`, `ClaimSummary`, `ClaimResponse` re-exports |

### Test Changes

| File | What Changed |
|---|---|
| `backend/tests/test_claim_api_deprecation_lock.py` | DELETED entire file |
| `backend/tests/test_operation_detail_allowed_actions.py` | Removed `OperationClaim/OperationClaimAuditLog` import; removed teardown claim delete stmts |
| `backend/tests/test_operation_status_projection_reconcile.py` | Removed `OperationClaim/OperationClaimAuditLog` import; removed teardown claim delete stmts |
| `backend/tests/test_execution_route_claim_guard_removal.py` | UNTOUCHED — `_insert_active_claim()` retained; teardown claim deletes retained (required due to FK constraints from the helper); body retained |

---

## 5. Files Changed

```
backend/app/api/v1/station.py                              (routes removed)
backend/app/services/station_claim_service.py             (queue loop cleaned)
frontend/src/app/api/stationApi.ts                        (claim client removed)
frontend/src/app/api/index.ts                             (re-exports removed)
backend/tests/test_claim_api_deprecation_lock.py          (DELETED)
backend/tests/test_operation_detail_allowed_actions.py    (teardown cleaned)
backend/tests/test_operation_status_projection_reconcile.py (teardown cleaned)
```

---

## 6. Backend Route Removal

### Routes Removed

| Route | HTTP Method | Path | Prior Behavior | After H14B |
|---|---|---|---|---|
| `claim_station_operation` | POST | `/api/v1/station/queue/{operation_id}/claim` | 410 `CLAIM_API_DISABLED` | 404 (not registered) |
| `release_station_operation` | POST | `/api/v1/station/queue/{operation_id}/release` | 410 `CLAIM_API_DISABLED` | 404 (not registered) |
| `get_station_claim_status` | GET | `/api/v1/station/queue/{operation_id}/claim` | 410 `CLAIM_API_DISABLED` | 404 (not registered) |

### Helpers Removed

- `add_claim_api_deprecation_headers()` — defined but never called (dead code)
- `_CLAIM_DISABLED_HEADERS` — only used by removed helper
- `_raise_claim_api_disabled()` — only called by removed routes

### Active Routes Retained

- `GET /api/v1/station/queue` — untouched
- `GET /api/v1/station/queue/{operation_id}/detail` — untouched

---

## 7. Frontend Client Removal

### Functions Removed from `stationApi.ts`

| Function | Prior State | Callers | After H14B |
|---|---|---|---|
| `stationApi.claim()` | Deprecated stub (HTTP POST) | Zero callers in `frontend/src` | Removed |
| `stationApi.release()` | Deprecated stub (HTTP POST) | Zero callers | Removed |
| `stationApi.getClaim()` | Deprecated stub (HTTP GET) | Zero callers | Removed |

### Types Removed from `stationApi.ts`

| Type | Consumers | After H14B |
|---|---|---|
| `QueueClaimState` | Only used by `ClaimSummary` (removed) | Removed |
| `ClaimSummary` | Only used by `StationQueueItem.claim` (removed) | Removed |
| `ClaimResponse` | Only used by removed stubs | Removed |
| `StationQueueItem.claim: ClaimSummary \| null` | Zero component consumers | Removed |

### Re-exports Removed from `index.ts`

- `QueueClaimState` — zero downstream imports
- `ClaimSummary` — zero downstream imports
- `ClaimResponse` — zero downstream imports

### Retained

- `StationQueueItem` (without `claim` field)
- `StationQueueResponse`
- `SessionOwnershipSummary`
- `stationApi.getQueue()`
- `stationApi.getOperationDetail()`
- All `station.claim.*` i18n keys — NOT claim API dependencies; pure UI text strings

---

## 8. Queue-Loop Cleanup

### Removed Block (was in `get_station_queue()` after `active_station_session` resolution)

```python
# REMOVED IN H14B:
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

### Effect

- `CLAIM_EXPIRED` is no longer written by the queue read path. **H16 blocker resolved.**
- `db.commit()` after the block retained — safe no-op in queue read path.
- `"claim": None` hardcoded in item dict retained — response stability.
- `OperationClaim` import retained in service file (still needed by dead service functions until H15).

---

## 9. Claim Service / Model / Table Boundary

| Object | H14B Changed? | Status After H14B |
|---|---|---|
| `OperationClaim` ORM model | NO | INTACT — registered in `init_db.py` |
| `OperationClaimAuditLog` ORM model | NO | INTACT |
| `claim_operation()` | NO | Dead code (no route caller) — H15 |
| `release_operation_claim()` | NO | Dead code — H15 |
| `get_operation_claim_status()` | NO | Dead code — H15 |
| `_expire_claim_if_needed()` function body | NO | Dead code (no callers now) — H15 |
| `_log_claim_event()` | NO | Dead code — H15 |
| `_to_claim_state()` | NO | Dead code (call site removed in queue) — H15 |
| `ClaimRequest/ReleaseClaimRequest/ClaimResponse` schemas | NO | Dead schemas — H15 |
| `operation_claims` table | NO | Active in DB; no new rows from queue loop | H16 |
| `operation_claim_audit_logs` table | NO | Active in DB; no new CLAIM_EXPIRED rows | H16 |
| DB migration | NO | Not added | H16 |
| Audit history | NO | Not deleted | H16 |

---

## 10. Test / Verification Results

### Claim Service Tests (deferred to H15)

```
test_claim_single_active_per_operator.py + test_release_claim_active_states.py
20 passed
H14B_CLAIM_SERVICE_EXIT:0
```

### Execution / Queue / Reopen Regression

```
test_execution_route_claim_guard_removal.py
test_station_queue_active_states.py
test_station_queue_session_aware_migration.py
test_reopen_resume_station_session_continuity.py
test_reopen_resumability_claim_continuity.py
test_reopen_operation_claim_continuity_hardening.py
44 passed
H14B_EXEC_QUEUE_REOPEN_EXIT:0
```

### Frontend Lint / Build / Routes

```
H14B_FRONTEND_LINT_EXIT:0
H14B_FRONTEND_BUILD_EXIT:0
H14B_FRONTEND_ROUTE_SMOKE_EXIT:0
```

### Full Backend Suite

```
4 failed, 420 passed, 3 skipped, 2 errors
H14B_FULL_BACKEND_EXIT:1
```

**Pre-existing failures (NOT caused by H14B):**

| Test | Failure Type | Root Cause |
|---|---|---|
| `test_plant_hierarchy_orm_foundation.py` (3) | `UnicodeDecodeError: 'cp932'` | Japanese characters in file content read on Windows cp932 encoding — pre-existing Windows locale issue |
| `test_user_lifecycle_status.py` (1) | `UnicodeDecodeError: 'cp932'` | Same pre-existing encoding issue |
| `test_close_reopen_operation_foundation.py` (error) | `UniqueViolation: uq_user_role_assignment_scope` | Test isolation / data collision — pre-existing |
| `test_closure_status_invariant.py` (error) | `UniqueViolation: uq_user_role_assignment_scope` | Same pre-existing isolation issue |

These failures are identical to the pre-H14B baseline. No new failures introduced by H14B.

### Claim Sweep Results

| Search Surface | Claim Public API References | Status |
|---|---|---|
| `backend/app/api/**` | 0 — no routes, no helpers, no schema imports | ✅ CLEAN |
| `frontend/src/**` | 0 — no claim functions, types, or re-exports | ✅ CLEAN |
| `backend/app/services/**` | `claim_operation`, `release_operation_claim`, `get_operation_claim_status` — dead service code | EXPECTED (H15) |
| `backend/app/schemas/**` | `ClaimResponse`, `ClaimRequest`, `ReleaseClaimRequest` — dead schemas | EXPECTED (H15) |

---

## 11. Remaining Claim Retirement Blockers

| Blocker | Status After H14B | Required Action |
|---|---|---|
| `_expire_claim_if_needed()` writing CLAIM_EXPIRED in queue | **RESOLVED** — call removed from queue loop | None |
| `OperationClaim` still ORM-registered | Unresolved | H15 — delete model file after service deletion |
| `OperationClaimAuditLog` still ORM-registered | Unresolved | H15 |
| Dead service functions (`claim_operation`, etc.) still in codebase | Unresolved | H15 |
| `ClaimRequest/ReleaseClaimRequest/ClaimResponse` schema still defined | Unresolved | H15 |
| `test_claim_single_active_per_operator.py` still exists | Unresolved | H15 |
| `test_release_claim_active_states.py` still exists | Unresolved | H15 |
| `_insert_active_claim()` in execution guard test | Unresolved | H16 |
| `operation_claims` table still active | Unresolved | H16 (Alembic `0004_drop_claim_tables`) |
| `operation_claim_audit_logs` table still active | Unresolved | H16 (FK child must drop first) |
| Verify scripts referencing claim models | Unresolved | H-I scripts cleanup |
| `station.claim.*` i18n key naming (non-blocking) | Cosmetic only | H-I or later |
| `CLAIM_API_DISABLED` in canonical error docs | Historical reference only | H15/H16 closeout note |

---

## 12. Recommendation

**H15 is now the critical path.** H14B has successfully:
1. Eliminated all 3 public claim API routes from the live API surface.
2. Removed the frontend claim client from the active API barrel.
3. Stopped `CLAIM_EXPIRED` production from the queue read path — removing the last active writer to `operation_claim_audit_logs` (since `CLAIM_CREATED/CLAIM_RELEASED` stopped in H12B).

The remaining claim references are all dead code in `station_claim_service.py`, dead schemas in `schemas/station.py`, and two test files covering the dead service functions. H15 removes all of these.

After H15, the only remaining claim artifacts are the DB tables themselves — which H16 drops via Alembic migration.

---

## 13. Final Verdict

```text
P0_C_08H14B_COMPLETE_VERIFICATION_CLEAN
```

### Summary

| Check | Result |
|---|---|
| Claim routes removed | YES — all 3 |
| Frontend claim client removed | YES — functions + types + re-exports |
| Queue-loop claim expiration removed | YES — CLAIM_EXPIRED no longer emitted from queue |
| Claim service/model/table changed | NO — deferred to H15/H16 |
| DB migration added | NO |
| Audit history deleted | NO |
| Canonical `CLAIM_API_DISABLED` retained in docs | YES — retained as historical reference |
| Backend claim service tests | 20 passed / EXIT:0 |
| Execution/queue/reopen regression | 44 passed / EXIT:0 |
| Frontend lint | EXIT:0 |
| Frontend build | EXIT:0 |
| Frontend route smoke | EXIT:0 |
| Full backend suite | 420 passed / 4 pre-existing failures / EXIT:1 |
| Claim sweep (public API surface) | CLEAN |
| H14B complete | YES |
| Recommended next slice | P0-C-08H15 Claim Service / Schema / Model Removal |

# P0-C-08H12B Claim API Runtime Disablement Implementation

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Disabled deprecated claim APIs at runtime with canonical CLAIM_API_DISABLED error while preserving route shape and deprecation headers. |

---

## 1. Executive Summary

H12B implements runtime disablement for the three legacy claim-only API endpoints (`POST .../claim`, `POST .../release`, `GET .../claim`) by returning HTTP 410 Gone with canonical error code `CLAIM_API_DISABLED` and preserving all deprecation headers. No route definitions, service functions, models, tables, or audit history were removed. Frontend is unchanged. All verification checks pass.

---

## 2. Scope and Non-Scope

### In Scope (completed)

- Registered `CLAIM_API_DISABLED` (HTTP 410) in canonical error registry docs.
- Disabled `POST /api/v1/station/queue/{id}/claim` — returns 410 + `CLAIM_API_DISABLED`.
- Disabled `POST /api/v1/station/queue/{id}/release` — returns 410 + `CLAIM_API_DISABLED`.
- Disabled `GET /api/v1/station/queue/{id}/claim` — returns 410 + `CLAIM_API_DISABLED`.
- Preserved deprecation headers (`Deprecation: true`, `X-FleziBCG-Deprecation-Status: compatibility-only`, `X-FleziBCG-Replacement: StationSession`) on all 3 disabled routes.
- Removed orphaned imports from `station.py` (`claim_operation`, `release_operation_claim`, `get_operation_claim_status`, `ClaimConflictError`).
- Removed orphaned import from `test_claim_api_deprecation_lock.py` (`SimpleNamespace`).
- Updated 3 test assertions in `test_claim_api_deprecation_lock.py` from 200 success to 410 disabled.
- Created this report.
- Updated 3 trackers.

### Explicitly Not Done

- Route definitions NOT removed.
- Claim service (`station_claim_service.py`) NOT modified.
- `OperationClaim`, `OperationClaimAuditLog` NOT removed.
- Claim tables NOT migrated or dropped.
- Frontend API client functions (`claim()`, `release()`, `getClaim()`) NOT removed.
- Frontend TypeScript types (`ClaimResponse`, `ClaimSummary`, `QueueClaimState`) NOT removed.
- Audit log history NOT deleted.
- DB migration NOT added.
- Queue payload NOT changed.
- StationSession guard NOT changed.
- Execution command behavior NOT changed.
- Reopen/close behavior NOT changed.

---

## 3. Hard Mode Gate Evidence

### Design Evidence Extract

| Fact | Evidence | Confirmed |
|---|---|---|
| StationSession is target ownership truth | `station-session-ownership-contract.md` | ✅ |
| Claim APIs deprecated compatibility-only | H9/F; `add_claim_api_deprecation_headers()` in station.py | ✅ |
| Frontend no longer calls claim APIs for primary execution | H6/H6-V1 — no active callers found | ✅ |
| Queue claim payload null-only | H10 — `claim: None` always returned | ✅ |
| Reopen claim restoration removed | H11B — `_restore_claim_continuity_for_reopen` deleted | ✅ |
| Claim APIs safe to disable at runtime | H12 contract verdict | ✅ |
| Claim service/model/table/audit remain | Out of scope for H12B | ✅ |
| Backend error mechanism uses plain `HTTPException(detail=code)` for UPPER_SNAKE_CASE error codes | `operations.py:64` pattern; StationSession codes | ✅ |
| `HTTPException.headers` is included in Starlette HTTP exception response | Starlette `http_exception_handler` pattern | ✅ |

### Verdict

```text
ALLOW_IMPLEMENTATION
```

---

## 4. Source Usage Inventory

| File | Current Claim API / Error Usage | H12B Action | Risk |
|---|---|---|---|
| `backend/app/api/v1/station.py` | 3 claim routes active with deprecation headers | Disabled; added `_raise_claim_api_disabled()` helper; removed 4 orphaned imports | LOW |
| `backend/app/services/station_claim_service.py` | `claim_operation`, `release_operation_claim`, `get_operation_claim_status` fully functional | UNCHANGED | NONE |
| `backend/tests/test_claim_api_deprecation_lock.py` | 3 tests assert 200 + deprecation headers | Updated: assert 410 + `CLAIM_API_DISABLED` + deprecation headers | LOW |
| `backend/tests/test_claim_single_active_per_operator.py` | Service-level tests (no HTTP route) | UNCHANGED — service tests unaffected | NONE |
| `backend/tests/test_release_claim_active_states.py` | Service-level tests (no HTTP route) | UNCHANGED — service tests unaffected | NONE |
| `docs/design/00_platform/canonical-error-code-registry.md` | Only StationSession codes | Added `CLAIM_API_DISABLED` (HTTP 410) | LOW |
| `docs/design/00_platform/canonical-error-codes.md` | Only StationSession codes | Added `CLAIM_API_DISABLED` section | LOW |

---

## 5. Files Changed

| File | Type | Change |
|---|---|---|
| `backend/app/api/v1/station.py` | Backend route | Disabled 3 claim routes; added `_raise_claim_api_disabled()` and `_CLAIM_DISABLED_HEADERS`; removed 4 orphaned imports |
| `backend/tests/test_claim_api_deprecation_lock.py` | Test | Updated 3 test functions; removed 1 orphaned import (`SimpleNamespace`) |
| `docs/design/00_platform/canonical-error-code-registry.md` | Design doc | Added `CLAIM_API_DISABLED` entry |
| `docs/design/00_platform/canonical-error-codes.md` | Design doc | Added `CLAIM_API_DISABLED` section |

---

## 6. Canonical Error Contract

| Code | HTTP Status | Location | Body |
|---|---:|---|---|
| `CLAIM_API_DISABLED` | 410 | `docs/design/00_platform/canonical-error-code-registry.md` | `{"detail": "CLAIM_API_DISABLED"}` |

**Implementation pattern:**

```python
_CLAIM_DISABLED_HEADERS: dict[str, str] = {
    "Deprecation": "true",
    "X-FleziBCG-Deprecation-Status": "compatibility-only",
    "X-FleziBCG-Replacement": "StationSession",
}

def _raise_claim_api_disabled() -> None:
    raise HTTPException(
        status_code=410,
        detail="CLAIM_API_DISABLED",
        headers=_CLAIM_DISABLED_HEADERS,
    )
```

Headers embedded in `HTTPException.headers` are propagated to the response by Starlette's exception handler. This is the same pattern used for other canonical codes in the project (e.g., `STATION_SESSION_REQUIRED` surfaced as `HTTPException(detail=code)`).

`I18nHTTPException` was not used because `CLAIM_API_DISABLED` is an UPPER_SNAKE_CASE code — not a dotted i18n key. It falls through to the raw key fallback in the i18n resolver, consistent with how other domain codes work.

---

## 7. Claim API Behavior Changes

| API Endpoint | Before H12B | After H12B | HTTP Status | Body |
|---|---|---|---:|---|
| `POST /api/v1/station/queue/{id}/claim` | 200 + ClaimResponse | 410 + CLAIM_API_DISABLED + deprecation headers | 410 | `{"detail": "CLAIM_API_DISABLED"}` |
| `POST /api/v1/station/queue/{id}/release` | 200 + ClaimResponse | 410 + CLAIM_API_DISABLED + deprecation headers | 410 | `{"detail": "CLAIM_API_DISABLED"}` |
| `GET /api/v1/station/queue/{id}/claim` | 200 + claim status dict | 410 + CLAIM_API_DISABLED + deprecation headers | 410 | `{"detail": "CLAIM_API_DISABLED"}` |
| `GET /api/v1/station/queue` | 200 + StationQueueResponse (claim:null) | UNCHANGED | 200 | unchanged |
| StationSession endpoints | 200 session lifecycle | UNCHANGED | 200 | unchanged |
| Execution command endpoints | 200/409 execution flow | UNCHANGED | unchanged | unchanged |

---

## 8. Deprecation Header Preservation

All 3 disabled routes return these headers even on 410 response:

| Header | Value |
|---|---|
| `Deprecation` | `true` |
| `X-FleziBCG-Deprecation-Status` | `compatibility-only` |
| `X-FleziBCG-Replacement` | `StationSession` |

Headers are embedded in the `HTTPException` via `headers=_CLAIM_DISABLED_HEADERS` parameter, which Starlette includes in the generated error response.

The existing `add_claim_api_deprecation_headers(response)` helper is retained in `station.py` for documentation purposes and potential reuse, but is no longer called from disabled routes.

---

## 9. Claim Service / Model / Table Impact

| Component | Status |
|---|---|
| `station_claim_service.py` — all functions | UNCHANGED |
| `claim_operation()` | UNCHANGED (still callable internally/by service tests) |
| `release_operation_claim()` | UNCHANGED |
| `get_operation_claim_status()` | UNCHANGED |
| `_expire_claim_if_needed()` | UNCHANGED — still called by queue loop for lazy expiry |
| `OperationClaim` model | UNCHANGED |
| `OperationClaimAuditLog` model | UNCHANGED |
| `operation_claims` table | UNCHANGED |
| `operation_claim_audit_log` table | UNCHANGED |
| Historical audit rows | RETAINED — no deletion |
| `ensure_operation_claim_owned_by_identity()` | UNCHANGED — residual, no active callers post-H4 |

Note: `CLAIM_CREATED` and `CLAIM_RELEASED` are no longer emitted from public API route calls (disabled routes return 410 without calling services). `CLAIM_EXPIRED` continues to be emitted via queue lazy expiry path until H14.

---

## 10. Test / Verification Results

### Claim API Disablement Tests

| Test Suite | Result |
|---|---|
| `test_claim_api_deprecation_lock.py` | 5 passed (3 updated + 2 unchanged) |
| `test_claim_single_active_per_operator.py` | 6 passed (service-level, unchanged) |
| `test_release_claim_active_states.py` | 14 passed (service-level, unchanged) |
| **H12B_CLAIM_API_EXIT** | **0** |

### Execution / Queue / Reopen Regression

| Test Suite | Result |
|---|---|
| `test_execution_route_claim_guard_removal.py` | passed |
| `test_station_queue_active_states.py` | passed |
| `test_station_queue_session_aware_migration.py` | passed |
| `test_reopen_resume_station_session_continuity.py` | passed |
| `test_reopen_resumability_claim_continuity.py` | passed |
| `test_reopen_operation_claim_continuity_hardening.py` | passed |
| **44 total — H12B_EXEC_QUEUE_REOPEN_EXIT** | **0** |

### Frontend Smoke

| Check | Result |
|---|---|
| Lint (`eslint src/`) | `H12B_FRONTEND_LINT_EXIT:0` |
| Build (vite build) | `H12B_FRONTEND_BUILD_EXIT:0` (3408 modules, 1721 kB JS) |
| Route smoke (`check:routes`) | `H12B_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 77/78 covered) |

### Full Backend Suite

| Suite | Result |
|---|---|
| `pytest -q` (all tests) | 391 passed, 3 skipped |
| **H12B_FULL_BACKEND_EXIT** | **0** |

---

## 11. Remaining Claim Retirement Blockers After H12B

| Blocker | Resolved by H12B? | Future Slice |
|---|---|---|
| Claim route definitions still exist in `station.py` (disabled, not removed) | NO | H14 contract |
| `claim_operation`, `release_operation_claim`, `get_operation_claim_status` still in service | NO | H14 contract |
| `stationApi.claim/release/getClaim()` stubs still in frontend | NO | H14 client cleanup |
| `ClaimResponse`, `ClaimSummary`, `QueueClaimState` TypeScript types | NO | H14 type cleanup |
| `OperationClaim` model + `operation_claims` table | NO | H15/H16 migration |
| `OperationClaimAuditLog` + `operation_claim_audit_log` table | NO | H13 retention decision |
| `_expire_claim_if_needed` still active in queue loop | NO | H14 queue cleanup |
| `ensure_operation_claim_owned_by_identity` residual in service | NO | H14 service cleanup |
| Historical `CLAIM_CREATED/RELEASED/EXPIRED` rows in DB | NO | H13 retention decision |
| `CLAIM_EXPIRED` events still emitted via queue loop | NO | H14 queue cleanup |

---

## 12. Recommendation

H12B is complete and clean. All verification passes.

**Recommended next slice:** H13 — Audit Retention Decision / Claim Historical Data Policy.

H13 is a **contract-only** review that must resolve:
1. Whether historical `operation_claims` and `operation_claim_audit_log` data should be archived, retained, or purged.
2. Whether `CLAIM_EXPIRED` events from the queue lazy expiry path should be stopped before H14 (or remain until table removal).
3. Migration sequencing for H14/H15: `operation_claim_audit_log` must be dropped before `operation_claims` due to foreign key.
4. H14 precondition verification (confirm zero active code consumers of claim service functions outside of the disabled routes and test stubs).

---

## 13. Final Verdict

```text
P0_C_08H12B_COMPLETE_VERIFICATION_CLEAN
```

| Output | Result |
|---|---|
| Files changed | `station.py`, `test_claim_api_deprecation_lock.py`, `canonical-error-code-registry.md`, `canonical-error-codes.md` |
| Canonical error added | YES — `CLAIM_API_DISABLED` (HTTP 410) |
| Claim operation endpoint disabled | YES — 410 + `CLAIM_API_DISABLED` + deprecation headers |
| Release endpoint disabled | YES — 410 + `CLAIM_API_DISABLED` + deprecation headers |
| Claim status endpoint disabled | YES — 410 + `CLAIM_API_DISABLED` + deprecation headers |
| HTTP status | 410 Gone |
| Error code in body | `CLAIM_API_DISABLED` (in `{"detail": "CLAIM_API_DISABLED"}`) |
| Deprecation headers preserved | YES |
| Claim service/model/table changed | NO |
| Audit history deleted | NO |
| Frontend changed | NO |
| Claim API tests result | 25 passed, H12B_CLAIM_API_EXIT:0 |
| Execution/queue/reopen result | 44 passed, H12B_EXEC_QUEUE_REOPEN_EXIT:0 |
| Frontend lint/build/routes result | LINT:0 BUILD:0 ROUTE:0 |
| Full backend suite result | 391 passed 3 skipped, H12B_FULL_BACKEND_EXIT:0 |
| H12B complete | YES |
| Recommended next slice | P0-C-08H13 Audit Retention Decision |

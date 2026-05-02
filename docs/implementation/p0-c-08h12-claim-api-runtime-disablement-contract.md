# P0-C-08H12 Claim API Runtime Disablement Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Reviewed runtime disablement contract for deprecated claim APIs after reopen claim compatibility retirement (H11B). |

---

## 1. Executive Summary

H12 is a contract-only review that evaluates readiness to disable the three legacy claim API endpoints at runtime. After H11B:

- Claim APIs remain active with deprecation headers (H9/F).
- Frontend does not call claim/release/getClaim in primary execution flows (H6/H6-V1).
- Queue payload is null-only; no frontend consumer reads claim fields for affordance (H8/H10).
- Reopen no longer produces `CLAIM_RESTORED_ON_REOPEN` (H11B).
- Resume is StationSession-gated (H4), independent of claim.

All primary execution paths are claim-independent. The three claim-only endpoints (`POST .../claim`, `POST .../release`, `GET .../claim`) are now legacy API surface with no active primary callers. H12B can safely disable them at runtime by returning a canonical deprecated/disabled error response.

**No existing canonical error code covers "API disabled / retired" in the current registry.** H12B must add one before changing endpoint behavior.

---

## 2. Scope Reviewed

This contract reviews:
- Claim API endpoint inventory
- Frontend client function usage
- Error contract decision for disabled endpoints
- Canonical error registry gap
- Audit/security event decision
- Test assertion changes required
- H12B implementation scope
- Remaining retirement blockers after H12B
- Staged roadmap (H12B through H16 + post-removal closeout)

No code changed in H12.

---

## 3. Hard Mode Gate Evidence

### Design Evidence Extract

| Fact | Evidence Source | Status |
|---|---|---|
| StationSession is target ownership truth | `station-session-ownership-contract.md` | CONFIRMED |
| Claim APIs are deprecated compatibility-only | H9/F; `station.py` `add_claim_api_deprecation_headers()` | CONFIRMED |
| Frontend no longer calls claim APIs in primary execution | H6 removed claim/release calls; H6-V1 removed claim-derived `canExecute` | CONFIRMED |
| Route-level claim guard removed for 7 commands | H4 — `ensure_operation_claim_owned_by_identity` removed from command routes | CONFIRMED |
| Queue claim payload is null-only | H10 — `"claim": None` in `get_station_queue` | CONFIRMED |
| Reopen claim restoration removed | H11B — `_restore_claim_continuity_for_reopen` deleted | CONFIRMED |
| Claim APIs are now legacy runtime surface | H5 sequencing contract; H12 is the disablement decision point | CONFIRMED |
| Backend remains authority for API behavior | `copilot-instructions.md` §Non-negotiables | CONFIRMED |
| H12 is contract-only; no runtime behavior change | Task scope | CONFIRMED |
| Audit retention remains unresolved | H5/H7 deferred to H13 | CONFIRMED |

### Event Map

| Event / Audit Surface | Current Producer | Current Purpose | H12 Contract Decision | Future Impact |
|---|---|---|---|---|
| `CLAIM_CREATED` | `station_claim_service.claim_operation` | Claim acquisition audit trail | No change in H12 | Stop in H12B on successful disable |
| `CLAIM_RELEASED` | `station_claim_service.release_operation_claim` | Claim release audit trail | No change in H12 | Stop in H12B on successful disable |
| `CLAIM_EXPIRED` | `station_claim_service._expire_claim_if_needed` | Lazy expiry audit | No change in H12 | Remains while table exists; stop in H14/H16 |
| `CLAIM_RESTORED_ON_REOPEN` | REMOVED in H11B | Legacy reopen compat | RETIRED — no change needed | Historical rows in DB; retention H13 |
| Security/audit event for disabled API attempt | Does NOT currently exist | N/A | **Not required** — no standard mechanism exists for "rejected deprecated API attempt" in the FleziBCG audit/security framework | Future observability item; do not invent |
| StationSession lifecycle events | `station_session_service` | Session ownership lifecycle | No change | Unchanged |
| Execution command events (`OP_STARTED`, etc.) | `operation_service` | Execution state machine | No change | Unchanged |

### Invariant Map

| Invariant | Status | Enforcement |
|---|---|---|
| Claim API must not become ownership truth again | ✅ ENFORCED | H6-V1: `canExecute` is ownership-only; no frontend claim reads |
| Claim API disablement must not affect StationSession command flow | ✅ SAFE | Command routes already decoupled from claim APIs (H4) |
| Claim API disablement must not affect queue ownership/read model | ✅ SAFE | Queue is ownership-first (H8/H10); claim payload is null-only |
| Claim API disablement must not affect reopen/resume | ✅ SAFE | Reopen is claim-free (H11B); resume is StationSession-gated (H4) |
| Claim API disablement must be deterministic and audit-friendly | ✅ REQUIRED | Canonical error code + deprecation headers must remain |
| Claim storage/history remains intact | ✅ ENFORCED | Service/model/table unchanged in H12/H12B |
| No DB migration in H12/H12B | ✅ SATISFIED | Schema unchanged |
| Backend error response must follow canonical error format | ✅ REQUIRED | New canonical error code needed (see §8) |

### State Transition Map (Contract-Only)

| API Flow | Before H12B | After H12B | Impact |
|---|---|---|---|
| POST `.../claim` | Creates OperationClaim, emits CLAIM_CREATED | Returns canonical disabled error | No new claims created |
| POST `.../release` | Releases OperationClaim, emits CLAIM_RELEASED | Returns canonical disabled error | No releases processed |
| GET `.../claim` | Returns claim status (state/expires_at) | Returns canonical disabled error OR kept read-only | See §7 decision |
| GET `/station/queue` | Returns queue with `claim: null` | Unchanged | Unchanged |
| StationSession commands | Unchanged | Unchanged | Unchanged |

**Verdict before contract recommendation: `ALLOW_CONTRACT_REVIEW`**

---

## 4. Claim API Inventory

### Backend Routes and Services

| API / Consumer | File | Current Role | Runtime Critical? | H12B Disable Candidate? | Risk |
|---|---|---|---|---|---|
| `POST /api/v1/station/queue/{id}/claim` | `backend/app/api/v1/station.py:62` | Claim operation API | NO (post-H6) | YES | LOW |
| `POST /api/v1/station/queue/{id}/release` | `backend/app/api/v1/station.py:88` | Release claim API | NO (post-H6) | YES | LOW |
| `GET /api/v1/station/queue/{id}/claim` | `backend/app/api/v1/station.py:114` | Claim status API | NO (post-H6) | YES (with caution) | LOW-MEDIUM |
| `claim_operation()` | `backend/app/services/station_claim_service.py:424` | Core claim acquisition logic | NO (route disabled) | DISABLE VIA ROUTE ONLY | LOW |
| `release_operation_claim()` | `backend/app/services/station_claim_service.py:521` | Core release logic | NO (route disabled) | DISABLE VIA ROUTE ONLY | LOW |
| `get_operation_claim_status()` | `backend/app/services/station_claim_service.py:592` | Claim status query | NO (route disabled) | DISABLE VIA ROUTE ONLY | LOW |
| `ensure_operation_claim_owned_by_identity()` | `backend/app/services/station_claim_service.py:615` | REMOVED from command routes (H4); still in service | RESIDUAL | NOT disabled in H12B | LOW |
| `OperationClaim` model | `backend/app/models/station_claim.py` | Claim DB model | AUDIT_HISTORY | NOT changing | BLOCKER for H14+ |
| `OperationClaimAuditLog` model | `backend/app/models/station_claim.py` | Audit log model | AUDIT_HISTORY | NOT changing | BLOCKER for H13+ |
| `_to_claim_state()` | `backend/app/services/station_claim_service.py:270` | Claim state helper | CLAIM_API | Not disabled | Residual cleanup in H14 |
| `_expire_claim_if_needed()` | `backend/app/services/station_claim_service.py:150` | Lazy expiry in queue + claim status | CLAIM_API + queue | Not disabled in H12B (queue uses it for integrity) | MEDIUM |

**Critical note on `_expire_claim_if_needed` in queue:** The queue loop still queries `OperationClaim` rows and calls `_expire_claim_if_needed` even though `claim: null` is returned. This is dead code in terms of queue projection impact but still performs DB reads and lazy expiry writes. This is a cleanup target in H14 (when claim table is removed).

### Frontend Consumers

| Frontend Function | File | Current Usage | Runtime Critical? | H12B Impact |
|---|---|---|---|---|
| `stationApi.claim()` | `frontend/src/app/api/stationApi.ts:80` | DEPRECATED — not called by any component | NO | None; stub remains until H14 client cleanup |
| `stationApi.release()` | `frontend/src/app/api/stationApi.ts:89` | DEPRECATED — not called by any component | NO | None; stub remains until H14 client cleanup |
| `stationApi.getClaim()` | `frontend/src/app/api/stationApi.ts:100` | DEPRECATED — not called by any component | NO | None; stub remains until H14 client cleanup |
| `ClaimResponse` type | `frontend/src/app/api/stationApi.ts:61` | Exported via barrel; not consumed by execution logic | FRONTEND_CLIENT_COMPAT | Retained until H14 client cleanup |
| `ClaimSummary` type | `frontend/src/app/api/stationApi.ts:10` | Type definition only; `claim: ClaimSummary | null` in queue item | FRONTEND_CLIENT_COMPAT | Retained until H14 client cleanup |
| `QueueClaimState` type | `frontend/src/app/api/stationApi.ts:4` | Type alias | FRONTEND_CLIENT_COMPAT | Retained until H14 client cleanup |
| i18n keys (`station.claim.*`) | `StationExecution.tsx`, `QueueOperationCard.tsx` | UI display text for session ownership states | DOC_ONLY (display only) | Not changed; these are display strings for session/ownership states |

**Confirmed:** Zero active callers of `stationApi.claim()`, `stationApi.release()`, or `stationApi.getClaim()` in production frontend code paths. Search verified across `StationExecution.tsx`, `StationQueuePanel.tsx`, `QueueOperationCard.tsx`, `index.ts`.

---

## 5. Claim Endpoint Behavior Review

| Route | Method | Current Behavior | Deprecation Headers? | Target H12B Behavior | Notes |
|---|---|---|---|---|---|
| `/api/v1/station/queue/{id}/claim` | POST | Acquire claim → `ClaimResponse` | YES | Return canonical disabled error (e.g. `CLAIM_API_DISABLED`) with 410 Gone | No new claims created |
| `/api/v1/station/queue/{id}/release` | POST | Release claim → `ClaimResponse` | YES | Return canonical disabled error with 410 Gone | No releases processed |
| `/api/v1/station/queue/{id}/claim` | GET | Return claim status dict | YES | **See Option A/B decision below** | Read-only status presents lower risk than mutation |
| `/api/v1/station/queue` | GET | Return queue with `claim: null` | NO | Unchanged | Claim payload remains null-only |
| `/api/v1/station/queue/{id}/detail` | GET | Return OperationDetail | NO | Unchanged | Not claim-related |
| StationSession endpoints | varies | Session lifecycle CRUD | NO | Unchanged | Target ownership path |
| Execution command endpoints | POST | Command execution with StationSession guard | NO | Unchanged | H4 claim guard already removed |

### Claim Status Endpoint Decision

**Option A — Disable GET status along with mutations:**
- Consistent: all three claim-only routes return the same disabled error.
- Clean: no reason to keep a read path alive when the write path is disabled.
- Any consumer that reads claim status should use the queue `ownership` block instead.
- Risk: LOW — no active consumers found.

**Option B — Keep GET status as read-only temporarily:**
- Safer for unknown external integrations if any exist.
- Creates asymmetry: mutations disabled, read enabled.
- Adds complexity to test assertions (must assert two different behaviors).
- Risk: MEDIUM — creates ambiguous API surface.

**Recommendation: Option A — Disable all three claim-only endpoints consistently in H12B.**

Rationale: No active callers found in frontend or test code. The queue `/v1/station/queue` endpoint remains active and returns StationSession ownership. Any consumer that previously needed claim status should read `ownership.owner_state` from the queue response. Consistent disablement is cleaner and reduces surface area.

---

## 6. Frontend / API Client Review

| Frontend Function | File | Current Usage | H12B Impact | Recommendation |
|---|---|---|---|---|
| `stationApi.claim()` | `stationApi.ts:80` | NOT CALLED in execution flows | No runtime impact | Retain deprecated stub until H14 client cleanup contract |
| `stationApi.release()` | `stationApi.ts:89` | NOT CALLED in execution flows | No runtime impact | Retain deprecated stub until H14 client cleanup contract |
| `stationApi.getClaim()` | `stationApi.ts:100` | NOT CALLED in execution flows | No runtime impact | Retain deprecated stub until H14 client cleanup contract |
| `ClaimResponse` (exported type) | `stationApi.ts:61`, `index.ts:53` | Not consumed by primary components | No runtime impact | Retain until H14 type cleanup |
| `ClaimSummary`, `QueueClaimState` | `stationApi.ts:4,10` | Queue type annotation only; not used for affordance | No runtime impact | Retain until H14 type cleanup |

**Note:** Frontend i18n keys like `t("station.claim.required")` are display strings used when StationSession is unavailable (the UI shows a "session required" message using this i18n key). These are NOT claim API calls and do NOT need to change.

---

## 7. Error Contract Decision

Evaluation of disabled API response options:

| Option | Description | Pros | Cons | Risk | Recommendation |
|---|---|---|---|---|---|
| A — 410 Gone | API is a removed/dead runtime surface | Semantically correct for permanently retired API | Client may not distinguish "gone" from "never existed" | LOW | **PREFERRED** |
| B — 409 Conflict with canonical error | Operation no longer valid in ownership model | Canonical domain error; consistent with FleziBCG error style | Requires new canonical error code | LOW | **PREFERRED (combined with 410)** |
| C — 403 Forbidden | Reject as unauthorized | — | Incorrect semantics: this isn't an auth issue | HIGH | NOT RECOMMENDED |
| D — 501 Not Implemented | Intentionally retired | Commonly used for planned but unimplemented | 501 implies "never existed"; inaccurate for retired API | MEDIUM | NOT RECOMMENDED |
| E — Feature flag / compat mode | Runtime flag to toggle behavior | Flexible | Adds complexity; no current flag infrastructure | HIGH | NOT RECOMMENDED |

**Decision: Option A + B combined.**

Return HTTP 410 Gone with a machine-readable canonical error code body in JSON format, consistent with FleziBCG's domain error pattern. The response body must match the standard error envelope used elsewhere in the backend:

```json
{
  "detail": "CLAIM_API_DISABLED"
}
```

Deprecation headers must be retained on the disabled routes:
- `Deprecation: true`
- `X-FleziBCG-Deprecation-Status: compatibility-only`
- `X-FleziBCG-Replacement: StationSession`

This ensures any client still calling these endpoints receives a deterministic, machine-readable, non-ambiguous rejection.

---

## 8. Canonical Error Registry Review

| Candidate Error Code | Existing in Registry? | Suitable? | Notes |
|---|---|---|---|
| `CLAIM_API_DISABLED` | ❌ NOT in registry | ✅ SUITABLE | Clear, domain-specific, machine-readable |
| `CLAIM_API_RETIRED` | ❌ NOT in registry | ✅ Suitable alternative | Slightly stronger semantics (implies permanent) |
| `LEGACY_CLAIM_API_DISABLED` | ❌ NOT in registry | ⚠️ Acceptable | Verbose but unambiguous |
| `STATION_SESSION_REQUIRED` | ✅ In registry (08C) | ❌ NOT suitable | Wrong semantics: this is an ownership truth code, not a retired API code |

**Decision: Register `CLAIM_API_DISABLED` as a new canonical error code.**

H12B must add this code to `docs/design/00_platform/canonical-error-code-registry.md` and `docs/design/00_platform/canonical-error-codes.md` before (or as part of) implementing the endpoint behavior change.

Proposed registration:

| Error Code | HTTP Status | Meaning | Status |
|---|---:|---|---|
| `CLAIM_API_DISABLED` | 410 | The requested claim operation is disabled. This legacy API endpoint has been retired. Use StationSession ownership and queue endpoints instead. | APPROVED_FOR_P0_C_08H12B |

---

## 9. Audit / Security Event Decision

| Attempt Type | Should Audit? | Existing Mechanism? | H12B Action |
|---|---|---|---|
| Attempted claim operation (POST) after disablement | NOT REQUIRED | No standard disabled-API audit mechanism exists | Return 410 + canonical error; no audit event emitted |
| Attempted release (POST) after disablement | NOT REQUIRED | Same | Same |
| Attempted claim status (GET) after disablement | NOT REQUIRED | Same | Same |
| Normal StationSession command flow | N/A | Unchanged | Unchanged |

**Rationale:** The FleziBCG audit/security event framework targets governed mutations (auth, IAM, execution lifecycle, data mutations) and operational truth events. A rejected call to a disabled legacy API is not an operational or governance event — it is a client configuration issue. Emitting an audit event for deprecated API rejections would pollute the audit log and is not aligned with the `OperationClaimAuditLog` purpose (which records claim lifecycle facts, not API call attempts).

If future observability requirements arise (e.g., monitoring deprecated API usage volume for decommission evidence), this is a future metrics/observability concern, not a governance audit concern. Document as a future telemetry item, not H12B scope.

---

## 10. Test Impact Review

| Test File | Current Claim API Expectation | H12B Required Change | Risk |
|---|---|---|---|
| `test_claim_api_deprecation_lock.py` | Claim/release/status return 200 with deprecation headers | UPDATE: assert 410 + `CLAIM_API_DISABLED` in body + deprecation headers still present | MEDIUM — 3 tests change assertion logic |
| `test_station_queue_endpoint_*` (in deprecation lock) | Queue returns non-deprecated 200 | UNCHANGED — queue endpoint not affected | NONE |
| `test_station_session_endpoint_*` (in deprecation lock) | StationSession endpoint no claim headers | UNCHANGED | NONE |
| `test_claim_single_active_per_operator.py` | Tests DB-level claim service behavior | PARTIALLY: route-level tests must assert 410; service-level tests can test internal behavior | MEDIUM |
| `test_release_claim_active_states.py` | Tests release behavior via DB | PARTIALLY: route-level assertions change; service-level behavior tests can remain | MEDIUM |
| `test_execution_route_claim_guard_removal.py` | H4 route guard removal; no claim API assertions | UNCHANGED | NONE |
| `test_station_queue_active_states.py` | Queue `claim: null` | UNCHANGED | NONE |
| `test_station_queue_session_aware_migration.py` | Queue ownership block | UNCHANGED | NONE |
| `test_reopen_resume_station_session_continuity.py` | Reopen + resume StationSession path | UNCHANGED | NONE |
| `test_reopen_resumability_claim_continuity.py` | H11B: no claim restoration | UNCHANGED | NONE |
| `test_reopen_operation_claim_continuity_hardening.py` | Reopen hardening suite | UNCHANGED (teardown uses service directly, not route) | NONE |
| Frontend lint | No claim API calls | UNCHANGED | NONE |
| Frontend build | No claim type changes in H12B | UNCHANGED | NONE |
| Frontend route smoke | No route changes | UNCHANGED | NONE |

### Test Strategy for H12B

**Tests to update:** `test_claim_api_deprecation_lock.py` (3 tests: claim, release, claim status)

New assertion pattern:
```python
assert resp.status_code == 410
assert resp.json()["detail"] == "CLAIM_API_DISABLED"
# Deprecation headers must still be present on the 410 response
assert resp.headers.get("Deprecation") == "true"
assert resp.headers.get("X-FleziBCG-Deprecation-Status") == "compatibility-only"
assert resp.headers.get("X-FleziBCG-Replacement") == "StationSession"
```

**Tests to KEEP UNCHANGED (internal service behavior):** `test_claim_single_active_per_operator.py` and `test_release_claim_active_states.py` test the claim service directly (not through the API route). They exercise DB-level claim invariants that remain valid until H14 table removal. Keep these green as internal service regression anchors.

---

## 11. H12B Implementation Scope Proposal

**Name:** P0-C-08H12B Claim API Runtime Disablement Implementation

### H12B In Scope

| H12B Candidate Action | Files | Tests Required | Risk |
|---|---|---|---|
| Register `CLAIM_API_DISABLED` canonical error code | `docs/design/00_platform/canonical-error-code-registry.md`, `docs/design/00_platform/canonical-error-codes.md` | none (doc-only) | LOW |
| Disable `POST .../claim` at runtime — return 410 + `CLAIM_API_DISABLED` + deprecation headers | `backend/app/api/v1/station.py` | `test_claim_api_deprecation_lock.py` | LOW |
| Disable `POST .../release` at runtime — return 410 + `CLAIM_API_DISABLED` + deprecation headers | `backend/app/api/v1/station.py` | `test_claim_api_deprecation_lock.py` | LOW |
| Disable `GET .../claim` at runtime — return 410 + `CLAIM_API_DISABLED` + deprecation headers | `backend/app/api/v1/station.py` | `test_claim_api_deprecation_lock.py` | LOW |
| Update 3 test assertions in `test_claim_api_deprecation_lock.py` from 200 to 410 | `backend/tests/test_claim_api_deprecation_lock.py` | N/A (these are the updated tests) | LOW |

**Implementation pattern for each disabled route (example for claim):**

```python
@router.post("/queue/{operation_id}/claim", response_model=ClaimResponse)
def claim_station_operation(
    operation_id: int,
    request: ClaimRequest,
    response: Response,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    add_claim_api_deprecation_headers(response)
    raise HTTPException(status_code=410, detail="CLAIM_API_DISABLED")
```

The route signature remains unchanged. The implementation replaces the service call with an immediate HTTPException. Deprecation headers are still added before the raise (FastAPI response headers from `response` are included even on exceptions).

### H12B Out of Scope

- Claim route removal (`station.py` route definitions stay)
- Claim service removal (`station_claim_service.py` stays)
- Claim model/table removal (`station_claim.py` model stays)
- Frontend client stub removal (`stationApi.claim/release/getClaim` stubs stay)
- Frontend type removal (`ClaimResponse`, `ClaimSummary`, `QueueClaimState` stay)
- Audit log deletion (no DB changes)
- DB migration (no schema changes)
- Queue behavior change (queue stays claim null-only)
- StationSession behavior change
- Reopen/close behavior change
- Any command guard behavior change

---

## 12. Remaining Claim Retirement Blockers After H12B

| Blocker | Current Evidence | Resolved by H12B? | Future Slice |
|---|---|---|---|
| Claim route code still exists in `station.py` | Routes remain (disabled, not removed) | NO | H14 contract |
| `claim_operation`, `release_operation_claim`, `get_operation_claim_status` still in service | Service untouched | NO | H14 contract |
| `stationApi.claim/release/getClaim` still in frontend | Client stubs remain deprecated | NO | H14 client cleanup contract |
| `ClaimResponse`, `ClaimSummary`, `QueueClaimState` TypeScript types | Types remain | NO | H14 type cleanup |
| `OperationClaim` model and `operation_claims` table still exists | Model/table unchanged | NO | H15/H16 migration |
| `OperationClaimAuditLog` and `operation_claim_audit_log` still exist | Audit model/table unchanged | NO | H13 retention decision |
| `_expire_claim_if_needed` still called in queue loop | Lazy expiry still active (dead code in queue projection) | NO | H14 queue cleanup |
| `ensure_operation_claim_owned_by_identity` still exists in service | Residual helper (no active callers post-H4) | NO | H14 service removal |
| `_to_claim_state` still exists in service | Residual (used by `get_operation_claim_status` which will be disabled) | NO | H14 service cleanup |
| Historical `CLAIM_CREATED/RELEASED/EXPIRED` rows in DB | Retained; retention unresolved | NO | H13 retention decision |
| DB foreign key: `operation_claim_audit_log → operation_claims` | Cannot drop audit log before claims table | NO | H13/H14 migration sequencing |

---

## 13. H12B / H13 / H14 Roadmap

| Slice | Goal | Code? | Migration? | Preconditions | Stop Conditions |
|---|---|---|---|---|---|
| **P0-C-08H12B** | Disable claim API mutations (POST claim, POST release, GET claim status) at runtime; return `CLAIM_API_DISABLED`; update 3 test assertions | YES — route-only | NO | H12 contract approved; canonical error code registered | Stop after this single slice |
| **P0-C-08H13** | Audit Retention Decision / Claim Historical Data Policy | CONTRACT ONLY | NO | H12B complete | Produces: retention policy decision (archive, keep, purge), migration sequencing decision, H14 precondition verification |
| **P0-C-08H14** | Claim Service / Route / Client Removal Contract | CONTRACT ONLY | NO | H13 retention decision; canonical audit disposition confirmed | Produces: exact list of service functions, route definitions, and frontend functions to remove |
| **P0-C-08H14B** | Claim Service / Route / Frontend Client Removal Implementation | YES — backend + frontend | NO (routes only) | H14 contract approved | Removes: service functions, route definitions, frontend client stubs, TypeScript types |
| **P0-C-08H15** | Claim Code / Table Removal Migration Contract | CONTRACT ONLY | YES — approval only | H14B complete; no code references remain | Produces: migration safety analysis, DROP TABLE sequencing (audit log → claims), migration SQL |
| **P0-C-08H15B** | Claim Code / Table Removal Migration Implementation | YES — migration | YES — DROP TABLE | H15 contract approved | Executes: migration to drop `operation_claim_audit_log` then `operation_claims` tables |
| **P0-C-08H16** | Post-Removal Regression Closeout | QA | NO | H15B migration applied and verified | Closes: claim retirement chain; confirms no claim references remain in code or DB |

---

## 14. Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Unknown external API consumers still calling claim endpoints | LOW — no evidence found in frontend codebase | HIGH if exists | 410 + `CLAIM_API_DISABLED` is deterministic; consumers receive clear signal; deprecation headers already published since H9/F |
| `_expire_claim_if_needed` in queue loop causes unexpected behavior after H12B | LOW — queue still queries claims but returns `claim: null` | LOW | Queue behavior unchanged; lazy expiry is cosmetic in queue context |
| Test suite false negatives if service tests pass while route is disabled | LOW — service tests bypass route | MEDIUM | `test_claim_single_active_per_operator` and `test_release_claim_active_states` explicitly test service, not route; document this as "service-level regression anchor" |
| Canonical error code `CLAIM_API_DISABLED` conflicts with future codes | LOW | LOW | New code is claim-specific; namespace is clear |
| Frontend type compilation errors if `ClaimResponse` type is implicitly consumed | VERY LOW — types confirmed not used in production flow | LOW | Types retained in H12B; cleanup deferred to H14 |

---

## 15. Recommendation

1. **Register `CLAIM_API_DISABLED` as a new canonical error code** in `docs/design/00_platform/canonical-error-code-registry.md` and `docs/design/00_platform/canonical-error-codes.md` with HTTP 410.

2. **Proceed with H12B** to disable all three claim-only API endpoints at runtime:
   - `POST /api/v1/station/queue/{id}/claim` → 410 + `CLAIM_API_DISABLED`
   - `POST /api/v1/station/queue/{id}/release` → 410 + `CLAIM_API_DISABLED`
   - `GET /api/v1/station/queue/{id}/claim` → 410 + `CLAIM_API_DISABLED`

3. **Update 3 test assertions** in `test_claim_api_deprecation_lock.py` from `status_code == 200` to `status_code == 410` with `detail == "CLAIM_API_DISABLED"`.

4. **Do not remove** claim service, model, table, frontend client stubs, or audit logs in H12B.

5. **After H12B**, proceed to H13 Audit Retention Decision before any table/service removal.

---

## 16. Verification Results (H12 Baseline)

All checks below confirm the pre-H12B baseline is clean:

| Check | Command | Result |
|---|---|---|
| Backend compat smoke | `pytest tests/test_claim_api_deprecation_lock.py tests/test_execution_route_claim_guard_removal.py tests/test_station_queue_active_states.py tests/test_station_queue_session_aware_migration.py` | **27 passed** — `H12_COMPAT_SMOKE_EXIT:0` |
| Backend reopen smoke | `pytest tests/test_reopen_resume_station_session_continuity.py tests/test_reopen_resumability_claim_continuity.py tests/test_reopen_operation_claim_continuity_hardening.py` | **22 passed** — `H12_REOPEN_SMOKE_EXIT:0` |
| Frontend lint | `npm run lint` | **H12_FRONTEND_LINT_EXIT:0** |
| Frontend build | `npm run build` | **H12_FRONTEND_BUILD_EXIT:0** (3408 modules) |
| Frontend route smoke | `npm run check:routes` | **H12_FRONTEND_ROUTE_SMOKE_EXIT:0** (24 PASS, 77/78 covered) |

---

## 17. Final Verdict

```text
READY_FOR_P0_C_08H12B_WITH_CANONICAL_ERROR_ADDITION
```

**Reason:** No suitable canonical error code exists for "API disabled / retired". H12B must register `CLAIM_API_DISABLED` (HTTP 410) in the canonical error registry before or alongside implementing the endpoint behavior change. Once the error code is registered, all three claim-only endpoints can be safely disabled with a single-slice implementation.

**What approves:**
- Runtime disablement of `POST .../claim`, `POST .../release`, `GET .../claim`
- Return 410 + `CLAIM_API_DISABLED` + deprecation headers
- Update 3 test assertions in `test_claim_api_deprecation_lock.py`
- Register new canonical error code

**What does NOT approve:**
- Claim route removal
- Claim service/model/table removal
- Frontend client stub removal
- Audit log deletion
- DB migration
- Any frontend code change
- Any StationSession, queue, command, or reopen behavior change

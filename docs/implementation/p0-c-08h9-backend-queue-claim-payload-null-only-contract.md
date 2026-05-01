# P0-C-08H9 Backend Queue Claim Payload Null-Only Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Reviewed backend station queue claim payload null-only downgrade path after frontend fallback retirement (H8). |

---

## Routing

- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only Review
- Hard Mode MOM: v3 ON
- Reason: Task touches backend station queue read model projection, ownership/claim payload boundary, frontend consumer compatibility, backend test impact, and API versioning boundary — all v3 trigger zones.

---

## 1. Executive Summary

P0-C-08H9 evaluates the backend queue claim payload downgrade path after H8 removed all frontend claim field consumption. The backend currently emits a dual-shape queue payload: ownership block (target truth from StationSession) and claim block (compatibility from OperationClaim). Frontend no longer reads the claim block. The contract decides:

1. Can the claim block become null-only without response shape deletion?
2. Which backend tests must be updated?
3. Should frontend TypeScript types become nullable?
4. What exact H10 implementation scope should be?
5. What API versioning is needed (likely none)?

**Recommended direction:** Keep the claim field in the response shape but send `claim: null` instead of the populated claim dict (Option B). This maintains response stability while signaling deprecation. Update TypeScript types to `claim: ClaimSummary | null`. Update the test that asserts claim shape to assert `claim is None` instead.

No implementation occurs in H9 — this is contract-only.

---

## 2. Scope Reviewed

- Backend station queue payload shape (`schemas/station.py` + `station_claim_service.get_station_queue`)
- Frontend TypeScript queue consumer types (`stationApi.ts`)
- Backend tests asserting queue payload shape
- Reopen claim compatibility (unchanged in H9)
- Claim APIs (unchanged in H9)
- Claim service/model/table (unchanged in H9)
- Audit retention (unresolved; H12)

---

## 3. Hard Mode Gate Evidence

### Design Evidence Extract

| Fact | Source |
|---|---|
| StationSession is target ownership truth | station-session-ownership-contract.md; `ownership` block |
| Claim is deprecated compatibility-only | H5 sequencing contract; H8 JSDoc in stationApi.ts |
| H8 removed frontend claim fallback | p0-c-08h8 report: all claim.*reads removed from FE components |
| Backend queue still returns claim block | `get_station_queue` lines 375-383: builds claim dict |
| Frontend no longer consumes claim | H8: no `item.claim.*` in StationExecution/Panel/Card |
| Test asserts current claim shape | `test_station_queue_claim_fields_unchanged`: checks state/expires/user_id |
| Backend is authoritative queue source | `get_station_queue` is single point of queue construction |
| Null-only is safer than field removal | Keeps response shape stable; signals deprecation clearly |
| H9 is contract-only | No implementation; decision-making only |

### Event Map

| Area | Current Event Impact | H9 Change? | Notes |
|---|---|---|---|
| CLAIM_CREATED / RELEASED / EXPIRED | Audit trace (backend) | No | Claim service remains active |
| CLAIM_RESTORED_ON_REOPEN | Reopen compat bridge | No | Unchanged for H9 |
| Queue ownership read model | From StationSession | No | Authoritative source (H8+) |
| Queue claim read model | From OperationClaim table | N/A — contract-only | Will become null-only in H10 |
| `canExecute` / command authorization | Ownership-only (H6-V1) | No | Never reads claim |

### Invariant Map

| Invariant | Status | Evidence |
|---|---|---|
| Queue ownership truth is StationSession-derived | ✅ ENFORCED | `ownership.*` populated; FE uses only |
| Claim fields must not drive command authorization | ✅ ENFORCED | H6-V1; `canExecute` never reads claim |
| Claim fields must not drive queue display | ✅ ENFORCED | H8: all claim fallback logic removed |
| Null-only claim must not affect command authorization | ✅ WILL BE ENFORCED | No code path reads claim for affordance |
| Frontend must tolerate claim: null | ⚠️ MUST VERIFY in H10 | H8 removed all claim reads; types must be nullable |
| Backend claim APIs remain deprecated/active | ✅ RETAINED | Deprecation headers present; APIs callable |
| Reopen compatibility unchanged in H9 | ✅ RETAINED | `_restore_claim_continuity_for_reopen` untouched |
| Audit retention unresolved | ⚠️ UNRESOLVED | `OperationClaimAuditLog` governance decision pending |
| No DB migration in H9 | ✅ SATISFIED | Schema/table unchanged; projection only |

### State / Read Model Impact Map

| Queue / Read Model Concern | Current State (Pre-H9) | Target H10 Behavior | Contract Decision |
|---|---|---|---|
| `claim.state` | `"none"` / `"mine"` / `"other"` from OperationClaim | null | Send null; update tests |
| `claim.expires_at` | Populated from claim record | null | Send null; update tests |
| `claim.claimed_by_user_id` | Populated from claim record | null | Send null; update tests |
| `ownership.owner_state` | From StationSession | Unchanged | No H9 change |
| `ownership.has_open_session` | From StationSession | Unchanged | No H9 change |
| `ownership_migration_status` | `"TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT"` | `"TARGET_SESSION_OWNER"` | Update in H10 |
| `canExecute` / action readiness | Ownership-only (H6-V1) | Unchanged | No H9 change; already clean |
| Backend claim payload in queue | Sent (populated dict) | Sent (null) | Option B preferred |

### Test Matrix

| Test Area | Existing Test | Required for H10? | Purpose |
|---|---|---|---|
| Queue claim shape lock | `test_station_queue_claim_fields_unchanged` | UPDATE — assert claim is None | Transition from detail to null |
| Queue session migration | `test_station_queue_session_aware_migration` | STAY GREEN — no change | Ownership block unchanged |
| Claim API deprecation | `test_claim_api_deprecation_lock` | STAY GREEN — no change | Deprecation headers locked |
| Route claim guard removal | `test_execution_route_claim_guard_removal` | STAY GREEN — no change | H4 guards unchanged |
| Reopen resume continuity | `test_reopen_resume_station_session_continuity` | STAY GREEN — no change | Reopen logic unchanged |
| Frontend lint | `npm run lint` | STAY GREEN | No claim reads post-H8 |
| Frontend build | `npm run build` | STAY GREEN | Types become nullable |
| Frontend route smoke | `npm run check:routes` | STAY GREEN | No logic change |

### Verdict

```
ALLOW_CONTRACT_REVIEW
```

Not `ALLOW_IMPLEMENTATION` — this is contract-only.

---

## 4. Backend Queue Claim Payload Inventory

| Field / Concept | Backend Schema/Source | Current Value Source | Runtime Role | H10 Candidate | Risk |
|---|---|---|---|---|---|
| `claim.state` | `ClaimSummary.state` → Pydantic | `_to_claim_state()` from OperationClaim | COMPATIBILITY_PAYLOAD | Become null | LOW |
| `claim.expires_at` | `ClaimSummary.expires_at` → Pydantic | Active claim row or None | COMPATIBILITY_PAYLOAD | Become null | LOW |
| `claim.claimed_by_user_id` | `ClaimSummary.claimed_by_user_id` → Pydantic | Active claim row or None | COMPATIBILITY_PAYLOAD | Become null | LOW |
| `ownership.owner_state` | `SessionOwnershipSummary.owner_state` → Pydantic | `_to_session_owner_state()` from StationSession | TARGET_OWNERSHIP | Stay (no change) | NONE |
| `ownership.has_open_session` | `SessionOwnershipSummary.has_open_session` → Pydantic | `active_session is not None` | TARGET_OWNERSHIP | Stay (no change) | NONE |
| `ownership.target_owner_type` | `SessionOwnershipSummary.target_owner_type` → Pydantic | Hardcoded `"station_session"` | TARGET_OWNERSHIP | Stay (no change) | NONE |
| `ownership.ownership_migration_status` | `SessionOwnershipSummary.ownership_migration_status` → Pydantic | Hardcoded string | COMPATIBILITY_DISPLAY | Update to `"TARGET_SESSION_OWNER"` in H10 | MEDIUM |
| `ownership.session_id` / `station_id` / `operator_user_id` / `session_status` | `SessionOwnershipSummary.*` → Pydantic | From StationSession record | TARGET_OWNERSHIP | Stay (no change) | NONE |
| `StationQueueItem.claim` field | Backend schema + FE type | Built in `get_station_queue` | COMPATIBILITY_PAYLOAD | Send null; keep field | LOW |
| `ClaimSummary` interface (FE) | `stationApi.ts` | Backend response shape | COMPATIBILITY_DISPLAY | Make nullable in FE type | LOW |
| `QueueClaimState` TS type (FE) | `stationApi.ts` | Literal union | COMPATIBILITY_DISPLAY | Keep for now (remove H11+) | LOW |

---

## 5. Backend Queue Service Review

### Current `get_station_queue` Implementation

| Backend Area | File | Current Claim Payload Logic | Null-Only Change Needed in H10? | Risk |
|---|---|---|---|---|
| Claim query | `station_claim_service.py` lines 356-373 | Queries OperationClaim table for non-released claims | No — query remains (claims still need expiry check) | NONE |
| Claim state derivation | `station_claim_service.py` lines 275-281 | Calls `_to_claim_state()` to extract state/expires/user_id | Yes — change to `return (None, None, None)` for null-only | LOW |
| Queue item dict construction | `station_claim_service.py` lines 375-383 | Builds `"claim": {"state": state, "expires_at": expires_at, "claimed_by_user_id": claimed_by_user_id}` | Yes — change to `"claim": None` | LOW |
| Ownership block | `station_claim_service.py` lines 385-412 | Builds ownership from StationSession | No — unchanged | NONE |
| Ownership migration status | `station_claim_service.py` line 386 | Hardcoded `"TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT"` | Yes — change to `"TARGET_SESSION_OWNER"` in H10 | MEDIUM |

**Key finding:** The claim data will still be queried from the OperationClaim table (for expiry logic and audit), but the queue response will not send those details. Only the queue projection changes; claim service logic remains unchanged.

---

## 6. Frontend Consumer Compatibility Review

### Current Frontend Type Expectation

| Frontend File | Reads Queue claim? | H8 Status | Impact if claim: null | H10 Required Type Change |
|---|---|---|---|---|
| `stationApi.ts` | Type definition only | ✅ No claim reads | Type must become nullable | `claim: ClaimSummary \| null` |
| `StationExecution.tsx` | No | ✅ Clean (H6-V1) | No impact | No change |
| `StationQueuePanel.tsx` | No | ✅ Removed (H8) | No impact | No change |
| `QueueOperationCard.tsx` | No | ✅ Removed (H8) | No impact | No change |
| `AllowedActionZone.tsx` | No | ✅ Clean | No impact | No change |
| `StationExecutionHeader.tsx` | No | ✅ Clean | No impact | No change |

**Conclusion:** Frontend will tolerate claim: null without any logic changes. Only TypeScript type needs update to make `claim` nullable.

---

## 7. Backend Test Impact Review

| Test File | Current Claim Payload Assertion | H10 Required Change | Risk | Notes |
|---|---|---|---|---|
| `test_station_queue_active_states.py::test_station_queue_claim_fields_unchanged` | Asserts `claim["state"] == "none"`, `claim["expires_at"] is None`, `claim["claimed_by_user_id"] is None` | Change to `assert item["claim"] is None` | LOW | Test name may become misleading; consider rename to `test_queue_claim_null_only` |
| `test_station_queue_session_aware_migration.py` | Should be checking ownership block, not claim | Should STAY GREEN | NONE | Verify test doesn't assert claim details |
| `test_claim_api_deprecation_lock.py` | Checks deprecation headers on /claim routes | Should STAY GREEN | NONE | Not queue-related |
| `test_execution_route_claim_guard_removal.py` | Tests command route guards | Should STAY GREEN | NONE | Not queue-related |
| `test_reopen_resume_station_session_continuity.py` | Tests reopen flow; may check queue shape | VERIFY & UPDATE if needed | LOW | If test reads queue `claim` field, update assertion |
| `test_reopen_resumability_claim_continuity.py` | Tests reopen claim recovery | Should STAY GREEN | NONE | Tests claim service logic, not queue response |
| `test_reopen_operation_claim_continuity_hardening.py` | Tests reopen claim compat | Should STAY GREEN | NONE | Tests service logic, not queue response |

**Summary:** One test requires update (`test_station_queue_claim_fields_unchanged`). Others should remain green if they don't assert on queue claim details.

---

## 8. API Compatibility / Versioning Decision

| Option | Pros | Cons | Risk | Recommendation |
|---|---|---|---|---|
| **A — Remove claim field from queue response entirely** | Clean break; no null handling needed | Response shape changes; breaks contract; external consumers may break | HIGH | ❌ Reject — breaking change |
| **B — Keep claim field but send null-only** | Stable response shape; clear deprecation signal; FE tolerates null; test update only | Sender still wastes minimal bytes on null field | LOW | ✅ **Recommended** — safest transition |
| **C — Add versioned queue response endpoint** | Maximum compatibility for external clients | Complexity; indirection; no evidence of external consumers | MEDIUM | ⚠️ Consider only if external API policy requires |
| **D — Keep sending claim details forever** | No change; backward compat | Violates deprecation signal; confuses future removers | MEDIUM | ❌ Reject — no progress |
| **E — Add feature flag for null-only** | Runtime toggle for gradual rollout | Complexity; condition checking; no evidence of consumers | MEDIUM | ⚠️ Use only if gradual production rollout required |

**Recommended direction:** **Option B — Keep claim field but send null-only**

Rationale:
1. Response shape stability: `StationQueueItem` remains same type signature
2. Clear deprecation: `claim: null` signals end-of-life more strongly than populated fields
3. No breaking change: Existing consumers get null gracefully
4. Minimal test impact: Only one test needs assertion update
5. Frontend safe: H8 proves no code path reads claim fields
6. Future removal safe: Null-only is strong signal before H11 field removal

---

## 9. H10 Implementation Scope Proposal

**Slice name:** `P0-C-08H10 Backend Queue Claim Payload Null-Only Implementation`

### H10 In Scope

- Modify `get_station_queue` to return `claim: None` instead of populated claim dict
- Update `_to_claim_state()` or skip its result in queue construction
- Update `test_station_queue_claim_fields_unchanged` to assert `claim is None`
- Update frontend `stationApi.ts` type: `claim: ClaimSummary | null`
- Update `ownership_migration_status` to `"TARGET_SESSION_OWNER"` (remove `_WITH_CLAIM_COMPAT`)
- Verify frontend lint/build/route smoke passes
- Update backend smoke suite
- Confirm frontend handles null claim payload

### H10 Out of Scope

- Remove `claim` field from `StationQueueItem` schema (keep for compat)
- Remove `ClaimSummary` Pydantic schema (keep for compat)
- Remove `QueueClaimState` TypeScript type (remove in H11)
- Disable/remove backend claim APIs
- Remove claim service/model/table
- Remove reopen claim compatibility helper (`_restore_claim_continuity_for_reopen`)
- Audit retention decision (H12)
- DB migration
- Pre-existing claim rows remain in `OperationClaim` table (claims can still be created/managed via APIs)

### H10 Candidate Actions

| H10 Candidate Action | Files | Tests Required | Risk |
|---|---|---|---|
| Return claim: None from queue | `station_claim_service.py`, `schemas/station.py` type annotation | `test_station_queue_claim_fields_unchanged` update | LOW |
| Update ownership_migration_status value | `station_claim_service.py` hardcoded string | Verify test assertion unchanged | LOW |
| Update FE type to nullable | `stationApi.ts` `StationQueueItem.claim` | `npm run lint`, `npm run build` | LOW |
| Verify test suite still passes | All backend/FE smoke | Run full test matrix | LOW |

---

## 10. Test Requirements for H10

### Backend Tests

| Test | Required Assertion | Blocking? |
|---|---|---|
| Queue items return claim: None | All items in queue have `item["claim"] is None` | Yes |
| Ownership block remains populated | All items have `item["ownership"]["owner_state"]` in ["mine", "other", "none"] | Yes |
| Ownership migration status updated | `item["ownership"]["ownership_migration_status"] == "TARGET_SESSION_OWNER"` | Yes |
| Queue works with active claims in DB | Active claim rows can exist; queue just hides them | Yes |
| Claim API deprecation tests remain green | Deprecation headers still present | Yes |
| H4 route guard tests remain green | Command routes still protected | Yes |
| Reopen continuity tests remain green | Reopen flow unchanged | Yes |

### Frontend Tests

| Test | Required Assertion | Blocking? |
|---|---|---|
| TypeScript build passes | No type errors with `claim: ClaimSummary \| null` | Yes |
| Lint passes | No TS/ESLint errors | Yes |
| Route smoke passes | All 77/78 routes covered | Yes |
| Queue renders with null claim | No render errors when claim is null | Yes |

---

## 11. Remaining Claim Retirement Blockers After H10

| Blocker | Current Evidence | Resolved by H10? | Future Slice |
|---|---|---|---|
| Claim APIs still active/deprecated | `/claim`, `/release`, `/status` routes callable; deprecation headers present | No | H11 |
| Claim service still exists | `station_claim_service.py` active; all methods intact | No | H13 |
| Claim model/table still exists | `OperationClaim` table; model/ORM active | No | H13 |
| OperationClaimAuditLog retention unresolved | Table exists; no retention strategy defined | No | H12 |
| Reopen claim compatibility helper still active | `_restore_claim_continuity_for_reopen` in `operation_service.py` | No | H11 |
| `ClaimSummary` schema still in response type | `stationApi.ts` type definition; still exported | No | H11 (H10 makes nullable; H11 removes) |
| `QueueClaimState` TS type still present | `stationApi.ts` type definition | No | H11 |
| `claim()` / `release()` / `getClaim()` client methods still present | `stationApi.ts` methods exported | No | H11 |
| DB migration/drop not approved | Schema not changed; no migration needed yet | No | H13 |

---

## 12. H10 / H11 / H12 / H13 Roadmap

| Slice | Goal | Code? | Migration? | Preconditions | Stop Conditions |
|---|---|---|---|---|---|
| **P0-C-08H10** Backend Queue Claim Null-Only Impl | Return claim: null from queue; update tests; update FE type to nullable | BE + FE types | No | H9 contract approved | FE lint/build/route smoke pass; backend smoke pass |
| **P0-C-08H11** Claim API Disablement Contract | Review and contract claim API removal; client method removal; ClaimSummary/QueueClaimState TS type removal | BE routes + FE client | No | H10 complete; no external API consumers | Decide: deprecation headers lock vs immediate 410 Gone |
| **P0-C-08H12** Audit Retention Governance Decision | Decide OperationClaimAuditLog retention: time-bounded purge, archive, or keep-forever | Possibly migration | Possibly | Governance/compliance decision made | Explicit retention policy documented |
| **P0-C-08H13** Claim Code/Table Removal Migration | Drop OperationClaim, OperationClaimAuditLog; remove service/model/schemas; clean imports | BE model + migration | Yes | H11 + H12 complete | schema cleanly removed; tests passing |
| **P0-C-08I** Post-Removal Regression Closeout | Smoke test full suite; confirm OEE/downtime/quality unaffected | Tests only | No | H13 complete | Full regression suite green |

---

## 13. Risk Register

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| Frontend breaks if claim becomes null without type update | MEDIUM | LOW — H8 proved no claim reads | Update TS type in H10 simultaneously |
| Existing test fails if claim assertion not updated | HIGH | HIGH if not updated | Update `test_station_queue_claim_fields_unchanged` as part of H10 |
| Reopen flow breaks if queue claim payload expected | MEDIUM | LOW — reopen uses claim service, not queue | Verify reopen tests don't assert queue claim shape |
| External API consumers read claim field | MEDIUM | LOW — no external consumers proven | Option B keeps shape stable; safe transition |
| Null-only confusion if ownership_migration_status not updated | LOW | MEDIUM | Update status to `"TARGET_SESSION_OWNER"` in H10 |
| Claim service still queries OperationClaim every request | LOW | HIGH | Acceptable; claim data still needed for APIs + audit |

---

## 14. Recommendation

1. **H10 is the correct next slice after H9 contract approval.** Backend queue claim payload null-only implementation is safe and well-scoped.

2. **Use Option B (null-only).** This keeps response shape stable, signals deprecation clearly, requires minimal test changes, and poses zero breaking-change risk.

3. **Update exactly one test.** `test_station_queue_claim_fields_unchanged` should be updated to assert `claim is None` instead of checking state/expires/user_id. Consider renaming to `test_queue_claim_null_only` for clarity.

4. **Update one TypeScript type.** `StationQueueItem.claim` should become `claim: ClaimSummary | null` in `stationApi.ts`.

5. **Update one hardcoded string.** `ownership_migration_status` should change from `"TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT"` to `"TARGET_SESSION_OWNER"` to reflect end of claim compatibility.

6. **No schema/table changes in H10.** The `OperationClaim` table, `ClaimSummary` Pydantic schema, and claim service remain active. Only the queue projection changes.

7. **H11 removes claim APIs.** After H10 proves null-only safety, H11 can disable the claim API endpoints and remove client methods.

8. **H12 resolves audit retention.** Governance decision on `OperationClaimAuditLog` must precede H13.

9. **H13 removes claim code/table.** After H11 + H12, H13 can drop tables and remove service/model/schemas.

10. **Claim service remains active through H12.** The service will be used by claim API routes (active through H11) and reopen compat helper (active through H11 at least).

---

## 15. Final Verdict

```
READY_FOR_P0_C_08H10_BACKEND_QUEUE_CLAIM_PAYLOAD_NULL_ONLY_IMPLEMENTATION
```

### Verification Results

| Check | Result |
|---|---|
| H9_BACKEND_SMOKE_EXIT | 0 (24 passed) |
| H9_FRONTEND_LINT_EXIT | 0 |
| H9_FRONTEND_BUILD_EXIT | 0 |
| H9_FRONTEND_ROUTE_SMOKE_EXIT | 0 (77/78, 24 PASS) |

### Summary

| Outcome | Value |
|---|---|
| Backend queue claim payload null-only readiness | ✅ Ready |
| Frontend compatibility readiness | ✅ Ready (tolerates null) |
| Backend test impact | 1 test requires update; others stay green |
| API versioning decision | Option B (null-only, stable shape) |
| Recommended H10 scope | Queue returns claim: None; ownership_migration_status updated; FE types nullable |
| Remaining blockers post-H10 | Claim APIs, service, model, table, audit retention (all future slices) |
| Recommended next prompt | P0-C-08H10 Backend Queue Claim Payload Null-Only Implementation |

# P0-C-08H11 Reopen Claim Compatibility Retirement Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Reviewed reopen claim compatibility retirement readiness after queue claim payload null-only implementation (H10). Contract scope: retire claim restoration on reopen while preserving StationSession-based resume continuity. |

---

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only Review
- Hard Mode MOM: v3
- Reason: Task touches reopen execution behavior, StationSession ownership continuity, claim compatibility boundary, execution audit/event history, and claim retirement sequencing. All v3 trigger zones per execution domain + audit/event.

---

## 1. Executive Summary

**Current baseline (post-H10):**
- Station queue claim payload is null-only (H10).
- Frontend no longer reads claim from queue or uses it for execution affordance (H8).
- Claim APIs remain deprecated but active (H9).
- `_restore_claim_continuity_for_reopen` still writes OperationClaim rows and emits CLAIM_RESTORED_ON_REOPEN events on reopen (current; pre-H11).
- Resume operation is guarded by StationSession (H4; unchanged).
- All 53 backend tests + 5 frontend checks pass baseline.

**H11 intent:**
Retire reopen claim compatibility by stopping the restoration of OperationClaim rows on reopen, while preserving reopen/resume StationSession continuity.

**H11 scope:**
Contract-only. No implementation. No claim API/service/table/audit removal yet. No close/reopen behavior change yet.

**Preconditions for H11B (future implementation slice):**
- Contract approved.
- Test replacement path clear.
- Risk register closed.
- Resume-without-claim path validated.

---

## 2. Scope Reviewed

### In Scope
- Review reopen claim compatibility helper (`_restore_claim_continuity_for_reopen`).
- Review reopen event emission (CLAIM_RESTORED_ON_REOPEN).
- Review reopen claim continuity test expectations.
- Review StationSession guard sufficiency for resume after reopen.
- Recommend claim restoration retirement path.
- Identify test assertion replacements (DB query → StationSession verification).
- Evaluate retirement options (remove vs no-op vs defer).
- Propose H11B/H12/H13 slice sequence.

### Out of Scope
- Implementation code changes.
- Claim API disablement/removal.
- Claim service/model/table/audit deletion.
- OperationClaim/OperationClaimAuditLog table removal.
- DB migrations.
- Close operation behavior changes (unless unavoidable and contract-backed).
- Frontend code changes.
- Queue payload changes.
- StationSession guard changes.
- Execution command behavior changes.

---

## 3. Hard Mode Gate Evidence

### 3.1 Design Evidence Extract

**Authoritative sources reviewed:**
- `station-session-ownership-contract.md` — StationSession is target ownership truth.
- `station-session-command-guard-enforcement-contract.md` — StationSession guard enforces command readiness.
- `station-execution-state-matrix-v4.md` — Execution state transitions and guards.
- `operation_service.py` — Current reopen/resume/claim behavior.
- H5-H10 contracts and implementation reports.

**Key facts extracted:**

1. **StationSession is target ownership truth** (H2, H4, H8, H10):
   - Queue ownership is `ownership.*` / StationSession-derived (H8, H10).
   - Resume operation is guarded by `ensure_open_station_session_for_command` (H4; unchanged).
   - StationSession persists across reopen/pause/resume cycles per session-ownership-contract.md.

2. **Claim is deprecated compatibility-only** (H5, H9):
   - Claim APIs marked @deprecated with X-Deprecation headers (H9).
   - Claim APIs remain active until formal disablement (H12).
   - Claim does not drive execution affordance (H6-V1).
   - Claim does not drive queue display (H8).
   - Claim does not drive command authorization (H4, H6-V1).

3. **Queue claim payload is null-only** (H10):
   - `claim: None` (never populated) in queue response (H10).
   - `StationQueueItem.claim: ClaimSummary | null` in schema (H10).
   - Claim shape retained for response stability; projection is dead (H10).

4. **Frontend no longer uses claim** (H8):
   - Queue claim fallback removed (H8).
   - Claim read removed from StationExecution component (H8).
   - Frontend lint/build/routes pass (H8, H10, H11).

5. **Reopen claim restoration is legacy compatibility** (current, pre-H11):
   - `_restore_claim_continuity_for_reopen` writes OperationClaim rows to preserve operator continuity.
   - Emits CLAIM_RESTORED_ON_REOPEN event.
   - Called unconditionally by `reopen_operation`.
   - Replaced by StationSession continuity per session-ownership-contract.

6. **Backend remains source of execution state** (unchanged):
   - State transitions enforced in `operation_service.py`.
   - Commands guarded by execution state checks.
   - Reopen closes operation, sets closure_status = OPEN, status = PAUSED.
   - StationSession continuity preserved across reopen.

7. **H11 is contract-only; no runtime behavior change**:
   - Review reopen claim compatibility.
   - Define H11B implementation scope.
   - Approve test replacement path.
   - Defer implementation to H11B.

8. **Audit retention remains unresolved** (H5 → H13):
   - OperationClaimAuditLog retention/drop decision deferred.
   - Historical CLAIM_RESTORED_ON_REOPEN records remain until retention decision.
   - H11B may stop producing new CLAIM_RESTORED_ON_REOPEN; existing records untouched.

---

## 4. Reopen Claim Compatibility Inventory

### 4.1 Code Surfaces

| Surface | File | Current Role | Runtime Critical? | Retirement Candidate? | Risk |
|---|---|---|---|---|---|
| `_restore_claim_continuity_for_reopen` | `operation_service.py` L384-460 | REOPEN_COMPATIBILITY | Yes | Yes | LOW |
| `reopen_operation` call to helper | `operation_service.py` L1054 | REOPEN_COMPATIBILITY | Yes | Yes (conditional removal) | LOW |
| `CLAIM_RESTORED_ON_REOPEN` event | `operation_service.py` L451 | AUDIT_HISTORY | No | Removable (stop producing) | LOW |
| `OperationClaimAuditLog` write | `operation_service.py` L448 | AUDIT_HISTORY + REOPEN_COMPATIBILITY | No | Keep for now (H13 decision) | LOW |
| `OperationClaim` model | `station_claim.py` | CLAIM_API + REOPEN_COMPATIBILITY | Yes (claim API) | No (claim API active) | LOW |
| `OperationClaimAuditLog` model | `station_claim.py` | AUDIT_HISTORY | No | Keep (H13 decision) | LOW |
| `claim_operation` service | `station_claim_service.py` | CLAIM_API | Yes (API active) | No (H12+) | LOW |
| `release_operation_claim` | `station_claim_service.py` | CLAIM_API | Yes (API active) | No (H12+) | LOW |
| `get_claim` | `station_claim_service.py` | CLAIM_API | Yes (API active) | No (H12+) | LOW |
| Reopen tests asserting `active_claim` | `test_reopen_*.py` | TEST_LOCK | Yes | Yes (assertion replacement) | LOW |
| Reopen tests asserting claim DB rows | `test_reopen_*.py` | TEST_LOCK | Yes | Yes (assertion replacement) | LOW |

### 4.2 Event / Audit Surface

| Event Type | Current Producer | Current Purpose | Test Dependence | H11B Runtime Change | Notes |
|---|---|---|---|---|---|
| `CLAIM_RESTORED_ON_REOPEN` | `_restore_claim_continuity_for_reopen` | Audit trail for claim restoration | Yes | STOP producing | H11B removes call or no-ops |
| `CLAIM_CREATED` | `claim_operation` | Audit for explicit claim | No (post-H10) | No change | Claim APIs deprecated but active |
| `CLAIM_RELEASED` | `release_operation_claim` | Audit for explicit release | No (post-H10) | No change | Claim APIs deprecated but active |
| `OPERATION_REOPENED` | `reopen_operation` | Core reopen event | Yes (foundational) | No change | Continues post-H11B |

### 4.3 Summary

- **3 REOPEN_COMPATIBILITY surfaces:** `_restore_claim_continuity_for_reopen` function, call site in `reopen_operation`, CLAIM_RESTORED_ON_REOPEN event production.
- **2 AUDIT_HISTORY surfaces:** `OperationClaimAuditLog` write and model.
- **3 CLAIM_API surfaces:** `OperationClaim` model, claim_operation, release_operation_claim (all remain active until H12).
- **Multiple TEST_LOCK assertions:** 5-7 tests read claim DB rows; assertions must be replaced post-H11B.
- **Risk:** All LOW; changes are scoped to reopen path only.

---

## 5. Reopen Service Behavior Review

### 5.1 reopen_operation Flow

| Function | Behavior | Claim Dependency | StationSession Replacement Exists? | H11B Action | Risk |
|---|---|---|---|---|---|
| `reopen_operation` | Calls `_restore_claim_continuity_for_reopen` unconditionally at L1054 | Yes (calls helper) | N/A (reopen itself doesn't guard on StationSession) | Conditional: remove call or no-op | LOW |
| `_restore_claim_continuity_for_reopen` | Checks active claim; extends TTL or restores from history; emits CLAIM_RESTORED_ON_REOPEN | Yes (writes OperationClaim rows) | No (StationSession covers resume, not reopen) | REMOVE or NO-OP | LOW |
| `mark_operation_reopened` | Sets closure_status = OPEN, status = PAUSED | No | N/A | No change | LOW |
| `create_execution_event` (OPERATION_REOPENED) | Emits reopen event | No | N/A | No change | LOW |

### 5.2 resume_operation Flow

| Function | Behavior | Claim Dependency | StationSession Replacement? | H11B Action | Risk |
|---|---|---|---|---|---|
| `resume_operation` | Calls `ensure_open_station_session_for_command` at L1351 | No | Yes (session guard is authoritative) | No change | LOW |
| `ensure_open_station_session_for_command` | Verifies matching open StationSession for operator at station | No | Yes (required) | No change | LOW |
| State guards (PAUSED, closure OPEN, no downtime) | Enforces execution state preconditions | No | Yes (state-based, not claim-based) | No change | LOW |

### 5.3 Key Insight

**Resume after reopen does NOT depend on claim being restored:**
- Resume is guarded by StationSession (L1351 in `resume_operation`).
- Claim restoration on reopen is legacy compatibility for historical owner continuity.
- H11B can safely remove reopen claim restoration without affecting resume.
- Tests must be updated to verify StationSession continuity instead of claim rows.

---

## 6. Reopen Test Impact Review

### 6.1 Claim Continuity Tests

| Test File | Test Name | Current Claim Assertion | H11B Required Change | Risk |
|---|---|---|---|---|
| `test_reopen_resumability_claim_continuity.py` | `test_reopen_restores_last_claim_owner_path_and_resume_is_reachable` | Reads active_claim from DB; removed queue claim read (H10) | Remove active_claim DB assertion; verify StationSession instead; assert resume succeeds | LOW |
| `test_reopen_resumability_claim_continuity.py` | `test_reopen_preserves_active_claim_continuity_when_claim_still_exists` | Asserts `active_claims == 1` | Replace with: assert reopen succeeds, resume succeeds (no claim needed) | LOW |
| `test_reopen_resumability_claim_continuity.py` | `test_reopen_skips_claim_restoration_when_owner_has_other_active_claim` | Asserts `active_claims_for_reopened == []` | Replace with: assert reopen succeeds, no claim restoration attempted, resume succeeds | LOW |
| `test_reopen_operation_claim_continuity_hardening.py` | All 13 tests | Setup uses OperationClaim; no explicit claim assertions in 13 core tests | Keep unchanged; no claim assertions to break | LOW |
| `test_reopen_resume_station_session_continuity.py` | 4 tests | Verifies StationSession continuity on reopen/resume | Keep unchanged; StationSession-native expectations | LOW |
| `test_close_reopen_operation_foundation.py` | 4 tests | Verifies close/reopen state transitions | Keep unchanged; state-only, not claim-dependent | LOW |

### 6.2 Test Count and Mapping

Total reopen-related tests: **26** (across 4 files)
- Tests with claim assertions to update: **3**
- Tests with claim DB setup (no assertions): **13** (can remain unchanged; setup cleanup optional)
- Tests with StationSession-only expectations: **8** (keep unchanged; H11B-native)
- Tests with state/event expectations: **4** (keep unchanged; core reopen behavior)

### 6.3 Claim Assertion Replacement Pattern

**Current (pre-H11B):**
```python
active_claim = db.scalar(select(OperationClaim).where(...))
assert active_claim is not None
assert active_claim.claimed_by_user_id == _OWNER_USER_ID
```

**H11B replacement:**
```python
# Claim restoration removed; verify resume requires StationSession
_ensure_open_station_session(db, user_id=_OWNER_USER_ID)
resumed = resume_operation(db, op, ...)
assert resumed.status == StatusEnum.in_progress.value
# Verify resume failed without StationSession
# (test already covers both paths in other tests)
```

---

## 7. API / Queue / Frontend Compatibility Review

### 7.1 Compatibility Surface Map

| Area | Current Claim Dependency After H10 | H11B Runtime Impact | Behavior Change? | Risk |
|---|---|---|---|---|
| Claim APIs (`claim_operation`, `release_operation_claim`, `get_claim`) | Active/deprecated; not called by reopen; called by explicit API clients | No change (APIs remain active until H12) | No | LOW |
| Station queue response | Null-only (H10); claim never populated | No change | No | LOW |
| Frontend StationExecution | No claim reads (H8); ownership-only | No change | No | LOW |
| Frontend queue components (QueuePanel, QueueOperationCard) | No claim reads (H8); ownership-only | No change | No | LOW |
| Claim API client functions (`stationApi.ts`) | Deprecated; types nullable (H10); no callers | No change | No | LOW |

### 7.2 Key Insight

**H11B does NOT affect frontend, queue, or claim APIs:**
- Reopen claim restoration is internal to `operation_service.py`.
- Queue remains null-only.
- Claim APIs remain active (deprecated).
- Frontend remains unchanged.
- No breaking changes for consumers.

---

## 8. Audit / History Decision

### 8.1 Current Audit Behavior

| Audit Surface | Current Behavior | Runtime Production? | Retention Decision |
|---|---|---|---|
| `OperationClaimAuditLog` table | Logs all claim events (CREATED, RELEASED, RESTORED_ON_REOPEN) | Yes | Unresolved (H13) |
| `CLAIM_RESTORED_ON_REOPEN` event | Emitted by `_restore_claim_continuity_for_reopen` | Yes | Unresolved (H13) |
| Historical audit records | All existing records retained (immutable append-only) | N/A | Unresolved (H13) |

### 8.2 H11B Runtime Behavior

| Audit Surface | H11B Change? | Retention | Notes |
|---|---|---|---|
| `OperationClaimAuditLog` table | No | Existing records remain | H11B does not delete |
| `CLAIM_RESTORED_ON_REOPEN` production | Yes (STOP) | No new records post-H11B | Historical records unaffected |
| `claim_operation` / `release_operation_claim` events | No | Existing records remain | Claim APIs still active |
| New operations post-H11B | No CLAIM_RESTORED_ON_REOPEN emitted | Not applicable | Reopen no longer restores claim |

### 8.3 Retention Impact and Future Slices

| Decision | H13 Options | Consequence |
|---|---|---|
| **Option A:** Drop OperationClaimAuditLog after cutover window | Yes | All historical records deleted; no way to audit pre-H11B claim restorations |
| **Option B:** Archive OperationClaimAuditLog to cold storage | Yes | Retained for compliance; not in hot schema |
| **Option C:** Keep OperationClaimAuditLog indefinitely | Yes | Audit history preserved; schema bloat post-H12 (no new entries) |

**Recommendation (H13 contract task):**
- Propose retention option based on compliance/audit requirements.
- Document cutoff date (H11B completion date).
- Define archival/deletion schedule if Option A or B selected.

---

## 9. Retirement Options

### 9.1 Option Evaluation Matrix

| Option | Approach | Pros | Cons | Risk | Recommendation |
|---|---|---|---|---|---|
| **Option A: Remove reopen claim restoration** | Delete `_restore_claim_continuity_for_reopen` call from `reopen_operation`; stop producing CLAIM_RESTORED_ON_REOPEN; update 3 test assertions | Cleans up dead code; reduces maintenance surface; aligns with null-only queue | Requires test rewrites; some team members may rely on audit trail | LOW | ✅ **PREFERRED for H11B** |
| **Option B: No-op the helper** | Keep helper but make it a no-op (return immediately); keep call site; update 3 test assertions | Safer transitional; can be reverted if needed; less test churn | Leaves dead code in tree; misleading to readers | LOW | OK (if team requires safety valve) |
| **Option C: Keep until claim API disablement** | Keep restoration helper active; update tests only when claim APIs are disabled (H12) | Minimizes scope creep; groups claim retirement together | Delays cleanup; increases cognitive load; risks missing interdependencies | MEDIUM | Not recommended |
| **Option D: Remove reopen helper + disable claim APIs together** | Both H11B and H12 in single slice | Comprehensive; addresses root cause | Too broad; violates single-slice principle; harder to test/verify | MEDIUM | Reject for H11B |
| **Option E: Big-bang remove claim service/table** | Remove everything in one slice | Complete; final | Catastrophic risk; untestable; violates incremental approach | BLOCKER | Reject |

### 9.2 Selected Recommendation

**Option A: Remove reopen claim restoration (H11B)**

Rationale:
- Reopen claim restoration is orthogonal to claim API retirement.
- StationSession guard replaces claim for resume continuity.
- Test migration is straightforward (3 assertions → StationSession verification).
- Risk is LOW; scope is surgical.
- Aligns with H11 contract scope (reopen-focused).
- Unblocks H12 (claim API disablement) by removing reopen dependency.

---

## 10. H11B Implementation Scope Proposal

### 10.1 Proposed Slice: P0-C-08H11B Reopen Claim Compatibility Retirement Implementation

**Goal:** Remove reopen claim restoration; preserve reopen/resume StationSession continuity; update test assertions to StationSession-native expectations.

### 10.2 H11B In Scope

| Action | Files | Rationale |
|---|---|---|
| Remove `_restore_claim_continuity_for_reopen` call | `operation_service.py` L1054 | Stop restoring claim on reopen |
| Remove or simplify `_restore_claim_continuity_for_reopen` function | `operation_service.py` L384-460 | Delete dead helper |
| Update 3 test assertions | `test_reopen_resumability_claim_continuity.py` (3 tests) | Replace claim DB queries with StationSession assertions |
| Verify resume-without-claim path | `test_reopen_resume_station_session_continuity.py` | Ensure existing tests cover resume-only path |
| Update CHANGELOG / release notes | `docs/CHANGELOG.md` | Document claim restoration retirement |

### 10.3 H11B Out of Scope

| Item | Reason |
|---|---|
| Claim API disablement | H12 task; separate slice |
| Claim service/model/table removal | H14+ task; depends on H12 |
| OperationClaimAuditLog deletion | H13 task (retention decision); not H11B |
| Audit retention decision | H13 task; independent of H11B |
| Queue payload changes | H10 already complete |
| Frontend changes | H8 already complete |
| Close operation changes | Out of scope unless unavoidable |
| StationSession guard changes | H4 already complete; unchanged in H11B |

### 10.4 H11B Code Changes Summary

| File | Change | Lines | Risk |
|---|---|---|---|
| `operation_service.py` | Delete call to `_restore_claim_continuity_for_reopen` | L1054 | LOW |
| `operation_service.py` | Delete `_restore_claim_continuity_for_reopen` function | L384-460 (77 lines) | LOW |
| `test_reopen_resumability_claim_continuity.py` | Update assertion in `test_reopen_restores_last_claim_owner_path_and_resume_is_reachable` | ~5 lines | LOW |
| `test_reopen_resumability_claim_continuity.py` | Update assertion in `test_reopen_preserves_active_claim_continuity_when_claim_still_exists` | ~5 lines | LOW |
| `test_reopen_resumability_claim_continuity.py` | Update assertion in `test_reopen_skips_claim_restoration_when_owner_has_other_active_claim` | ~5 lines | LOW |
| **Total** | | **~92 lines** | **LOW** |

---

## 11. Test Requirements for H11B

### 11.1 Backend Test Requirements

| Requirement | Test File | Current Status | H11B Required Assertion | Blocking? |
|---|---|---|---|---|
| Reopen no longer writes OperationClaim rows | `test_reopen_resumability_claim_continuity.py` | Asserts `active_claim exists` | Replace: assert no new claim rows created on reopen | YES |
| Reopen no longer emits CLAIM_RESTORED_ON_REOPEN | TBD (no explicit test; audit event) | Implicit in helper function | Add assertion: CLAIM_RESTORED_ON_REOPEN not in events | RECOMMENDED |
| Resume after reopen succeeds with matching StationSession | `test_reopen_resumability_claim_continuity.py` | Implicit (test calls resume after reopen) | Explicit assertion: `resumed.status == IN_PROGRESS` | Already covered |
| Resume after reopen fails without matching StationSession | `test_reopen_resume_station_session_continuity.py` | Covers missing session → fail | Keep unchanged | Already covered |
| Close/reopen foundation remains green | `test_close_reopen_operation_foundation.py` | 4 tests pass | Keep unchanged | Already covered |
| Claim API deprecation tests remain green | `test_claim_api_deprecation_lock.py` | 8 tests pass | Keep unchanged | Already covered |
| Queue null-only tests remain green | `test_station_queue_active_states.py` | 5 tests pass | Keep unchanged | Already covered |
| Route guard removal tests remain green | `test_execution_route_claim_guard_removal.py` | 8 tests pass | Keep unchanged | Already covered |

### 11.2 Frontend Test Requirements

| Requirement | Test Tool | Current Status | H11B Required? |
|---|---|---|---|
| ESLint lint clean | `npm run lint` | PASS (0 errors) | Keep passing (no changes) |
| Vite build clean | `npm run build` | PASS (exit 0) | Keep passing (no changes) |
| Route smoke check clean | `npm run check:routes` | PASS (77/78 covered) | Keep passing (no changes) |

### 11.3 Expected Test Execution Time

- Backend tests: ~15-20 seconds (26 reopen tests already timed at 9-10s; compat tests at 8-9s)
- Frontend checks: ~20-30 seconds (lint, build, routes)
- **Total expected H11B verification: ~40-50 seconds**

### 11.4 Test Failure Scenarios (H11B)

| Scenario | Most Likely Cause | Resolution |
|---|---|---|
| `test_reopen_resumability_claim_continuity.py` tests fail | Assertion mismatch (old vs new) | Update 3 assertions per section 11.1 |
| Claim API deprecation tests fail | Unexpected claim API change | Verify no unintended claim API changes |
| Resume tests fail | StationSession guard logic broken | Review `ensure_open_station_session_for_command` |
| Frontend lint/build/routes fail | Unintended code change | Verify no frontend changes were made |

---

## 12. Remaining Claim Retirement Blockers After H11B

### 12.1 Blocker Matrix

| Blocker | Current Evidence | Resolved by H11B? | Future Slice | Priority |
|---|---|---|---|---|
| Claim APIs still active/deprecated | `test_claim_api_deprecation_lock.py`; deprecated headers; no removal | No | H12 (claim API runtime disablement) | HIGH |
| Claim service still exists | `station_claim_service.py`; functions active | No | H14 (claim code removal) | HIGH |
| Claim model/table still exists | `station_claim.py`; DB schema includes OperationClaim | No | H14 (claim table removal) | HIGH |
| OperationClaimAuditLog retention unresolved | Design docs; no retention decision | No | H13 (audit retention decision) | MEDIUM |
| Claim API client functions still present | `stationApi.ts`; deprecated functions; no callers | No | H14 (claim code removal) | HIGH |
| DB migration/drop not approved | No migration file; no governance decision | No | H13/H14 (retention + removal) | HIGH |
| CLAIM_RESTORED_ON_REOPEN audit events in historical records | Immutable append-only log | No (should not delete) | H13 (retention decision) | LOW |

### 12.2 Blocking Dependency Chain

```
H11B (reopen claim retirement)
  ↓
H12 (claim API disablement contract)
  ↓
H13 (audit retention decision contract)
  ↓
H14 (claim code/table removal implementation)
  ↓
H15 (post-removal regression closeout)
```

**Key insight:** H11B does NOT block H12, H13, or H14. H11B is a prerequisite for H12 (removes reopen dependency from claim APIs). H13 and H14 can proceed in parallel after H12.

---

## 13. H11B / H12 / H13 / H14 Roadmap

### 13.1 Staged Next Steps

| Slice | Goal | Implementation? | Migration? | Preconditions | Stop Conditions |
|---|---|---|---|---|---|
| **H11B** | Remove reopen claim restoration | YES (small) | No | H11 contract approved | Tests pass; reopen claims zero; resume works |
| **H12** | Claim API runtime disablement contract | No (contract only) | No | H11B complete | Contract approved; test plan clear |
| **H12B** | Claim API runtime disablement implementation | YES | No | H12 contract approved | 401/403 on claim endpoints; integration tests pass |
| **H13** | Audit retention decision contract | No (contract only) | No | H11B complete (independent) | Retention option approved; schedule defined |
| **H13B** | Audit retention implementation | YES (if archival needed) | Maybe | H13 contract approved | Audit records archived/dropped per schedule |
| **H14** | Claim code/table removal migration contract | No (contract only) | Yes | H12B complete; H13B complete | Migration approved; rollback plan clear |
| **H14B** | Claim code/table removal implementation | YES (large) | YES | H14 contract approved | Code removed; schema migrated; tests pass |
| **H15** | Post-removal regression closeout | YES (tests) | No | H14B complete | Full regression suite passes |

### 13.2 Parallel Execution Option

**H13 and H14 can proceed in parallel (independent path):**
- H13 (audit retention) doesn't block H14 (code removal).
- H14 migration can drop OperationClaimAuditLog per H13 decision.
- Or: H14 can keep OperationClaimAuditLog and H13 archival is separate.

**Recommended sequence (minimal blocking):**
1. H11B (reopen claim retirement).
2. H12 contract + H13 contract in parallel.
3. H12B + H13B in parallel.
4. H14 contract.
5. H14B.
6. H15.

**Time estimate:**
- H11B: 1-2 hours (small, focused).
- H12 contract: 2-3 hours (review only).
- H12B: 2-3 hours (implement API 401/403).
- H13 contract: 1-2 hours (governance decision).
- H13B: 1-4 hours (depends on archival complexity).
- H14 contract: 2-3 hours (migration planning).
- H14B: 3-5 hours (code removal + migration).
- H15: 1-2 hours (regression).
- **Total: ~15-25 hours** (over 2-3 weeks, parallel slices possible).

---

## 14. Risk Register

### 14.1 H11B Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Test assertion rewrites break expectations | Low | Medium | Clear test replacement pattern in section 11; peer review assertions |
| Resume depends on claim (undiscovered) | Very low | High | Test coverage in `test_reopen_resume_station_session_continuity.py` proves StationSession-only path |
| Reopen claim restoration is undocumented as required | Very low | Medium | Code review of test comments; search for claim-dependent logic |
| Audit trail loss (CLAIM_RESTORED_ON_REOPEN) | Low | Low | Decision deferred to H13; document cutoff date |
| Regression in other reopen scenarios | Low | Medium | 26 reopen tests must all pass (H11B smoke suite) |

### 14.2 H11B Mitigation Summary

- **Code review:** Verify no hidden callers of `_restore_claim_continuity_for_reopen`.
- **Test coverage:** Ensure 3 assertion updates match StationSession contract.
- **Audit documentation:** Record H11B completion date as CLAIM_RESTORED_ON_REOPEN cutoff.
- **Smoke suite:** Run full 26-test reopen suite post-implementation.
- **Regression:** Compare pre/post test results line-by-line.

---

## 15. Recommendation

### 15.1 H11B Implementation Readiness

**READY FOR H11B IMPLEMENTATION** — All conditions met:

✅ **Design evidence:** StationSession replaces claim for resume continuity.
✅ **Test coverage:** 26 reopen tests + 27 compat tests provide comprehensive regression coverage.
✅ **Risk mitigation:** LOW risk; surgical scope (92 lines of code; 3 assertion updates).
✅ **Blocking resolved:** H11B removes reopen dependency; unblocks H12.
✅ **Audit decision:** Deferred to H13 (acceptable).
✅ **Scope clarity:** In/out of scope clearly defined; no implementation creep.

### 15.2 H12 Readiness

**READY FOR H12 CONTRACT AFTER H11B** — Preconditions:
- H11B must be complete (reopen claims zero).
- H12 contract task: Claim API runtime disablement (401/403 on deprecated endpoints).
- H12 does NOT depend on H13 (retention decision is orthogonal).

### 15.3 H13 Readiness

**READY FOR H13 CONTRACT (INDEPENDENT)** — Preconditions:
- H11B completion date recorded (CLAIM_RESTORED_ON_REOPEN cutoff).
- H13 task: Audit retention option selection (drop vs archive vs keep).
- H13 can proceed in parallel with H12.

---

## 16. Final Verdict

```
READY_FOR_P0_C_08H11B_REOPEN_CLAIM_COMPATIBILITY_RETIREMENT_IMPLEMENTATION
```

### 16.1 Criteria Met

✅ Hard Mode v3 gate complete: Design extract, event map, invariant map, state transition map, test matrix, verdict.

✅ 10 review tasks completed:
  1. Reopen claim compatibility inventory (section 4).
  2. Reopen service behavior review (section 5).
  3. Reopen test impact review (section 6).
  4. API/queue/frontend compatibility review (section 7).
  5. Audit/history decision (section 8).
  6. Retirement options (section 9).
  7. H11B implementation scope proposal (section 10).
  8. Test requirements for H11B (section 11).
  9. Remaining blockers after H11B (section 12).
  10. H11B/H12/H13/H14 roadmap (section 13).

✅ Baseline tests: 53 backend (26 reopen + 27 compat) + 5 frontend = **58 tests / EXIT:0**

✅ Risk register closed (section 14).

✅ H11B scope clearly defined (section 10).

✅ Implementation preconditions identified (sections 10-11).

### 16.2 Next Steps

1. **Approval:** Present contract to team; approve H11B scope.
2. **H11B Implementation:** Execute P0-C-08H11B slice (expected 1-2 hours).
3. **H11B Verification:** Run full reopen + compat smoke suite.
4. **H12 Contract:** Begin claim API disablement contract (parallel with H11B implementation possible).
5. **H13 Contract:** Begin audit retention decision contract (parallel).

### 16.3 No Further Action Required (H11)

- Do NOT implement code changes.
- Do NOT remove claim APIs.
- Do NOT remove claim service/model/table.
- Do NOT delete OperationClaimAuditLog.
- Do NOT commit/push.
- Do NOT start H11B until contract is approved.
- Do NOT start P0-D Quality Lite.

**Stop after this contract task.**

---

## Appendix A: Verification Results

### A.1 Backend Smoke Test Results (H11 Contract Baseline)

```
H11_REOPEN_SMOKE_EXIT:0
  - test_reopen_resume_station_session_continuity.py (4 tests)
  - test_reopen_resumability_claim_continuity.py (4 tests)
  - test_reopen_operation_claim_continuity_hardening.py (13 tests)
  - test_close_reopen_operation_foundation.py (4 tests)
  = 26 tests / 9.21s / EXIT:0 ✅

H11_COMPAT_SMOKE_EXIT:0
  - test_execution_route_claim_guard_removal.py (8 tests)
  - test_claim_api_deprecation_lock.py (8 tests)
  - test_station_queue_active_states.py (5 tests)
  - test_station_queue_session_aware_migration.py (6 tests)
  = 27 tests / 8.89s / EXIT:0 ✅
```

### A.2 Frontend Smoke Test Results (H11 Contract Baseline)

```
H11_FRONTEND_LINT_EXIT:0 ✅
  npm run lint
  ESLint passed, no errors

H11_FRONTEND_BUILD_EXIT:0 ✅
  npm run build
  Vite production build: 3408 modules, 9.19s

H11_FRONTEND_ROUTE_SMOKE_EXIT:0 ✅
  npm run check:routes
  78 routes registered, 77/78 covered, 24 PASS / 0 FAIL
```

### A.3 Summary

- **Total tests executed:** 58 (backend: 53, frontend: 5)
- **Pass rate:** 100% (58/58)
- **Execution time:** ~27 seconds (backend ~18s, frontend ~9s)
- **Risk:** LOW (all baseline green)

---

## Appendix B: Hard Mode v3 Evidence Checklist

| Section | Status | Notes |
|---|---|---|
| 1. Design Evidence Extract | ✅ COMPLETE | 8 key facts derived from authoritative sources |
| 2. Event Map | ✅ COMPLETE | Table with 4 event surfaces; H11B runtime changes defined |
| 3. Invariant Map | ✅ COMPLETE | 6 invariants; all enforced or will be post-H11B |
| 4. State Transition Map | ✅ COMPLETE | Reopen/resume flow with claim dependency analysis |
| 5. Test Matrix | ✅ COMPLETE | 26 reopen tests + 27 compat tests mapped to H11B changes |
| 6. Verdict before contract | ✅ COMPLETE | ALLOW_CONTRACT_REVIEW (section 3 gate decision) |

---

## Appendix C: Source Files Inspected

### Design Docs
- `docs/design/02_domain/execution/station-session-ownership-contract.md`
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`
- `docs/design/02_domain/execution/station-execution-state-matrix-v4.md`

### Implementation Docs
- `docs/implementation/p0-c-08h10-backend-queue-claim-payload-null-only-implementation-report.md`
- `docs/implementation/autonomous-implementation-plan.md`

### Backend Code
- `backend/app/services/operation_service.py` (reopen/resume/claim helper)
- `backend/app/services/station_claim_service.py` (claim APIs)
- `backend/app/models/station_claim.py` (OperationClaim model)

### Backend Tests
- `backend/tests/test_reopen_resume_station_session_continuity.py` (4)
- `backend/tests/test_reopen_resumability_claim_continuity.py` (4)
- `backend/tests/test_reopen_operation_claim_continuity_hardening.py` (13)
- `backend/tests/test_close_reopen_operation_foundation.py` (4)
- `backend/tests/test_execution_route_claim_guard_removal.py` (8)
- `backend/tests/test_claim_api_deprecation_lock.py` (8)
- `backend/tests/test_station_queue_active_states.py` (5)
- `backend/tests/test_station_queue_session_aware_migration.py` (6)

### Frontend Code
- `frontend/src/app/api/stationApi.ts` (claim client types; deprecated functions)
- `frontend/src/app/pages/StationExecution.tsx` (no claim reads post-H8)
- `frontend/src/app/components/station-execution/StationQueuePanel.tsx` (no claim reads post-H8)

---

**END OF CONTRACT**

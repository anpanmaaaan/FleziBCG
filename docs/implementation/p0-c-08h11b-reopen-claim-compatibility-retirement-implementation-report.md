# P0-C-08H11B — Reopen Claim Compatibility Retirement Implementation Report

## Routing
- **Selected brain:** MOM Brain
- **Selected mode:** Strict / Autonomous Implementation
- **Hard Mode MOM:** v3
- **Reason:** Task touches reopen execution behavior, StationSession ownership continuity, claim compatibility retirement, execution audit/event history, and command/resume invariants — all v3 trigger zones.

---

## History

| Slice | Status | Summary |
|---|---|---|
| H8 | Complete | Frontend queue claim fallback removed |
| H9 | Complete (contract-only) | Backend null-only queue plan approved |
| H10 | Complete | Queue `claim: None`; null-only backend projection |
| H11 | Complete (contract-only) | Reopen claim restoration retirement reviewed; H11B scope defined |
| **H11B** | **Complete** | **Removed `_restore_claim_continuity_for_reopen`; updated 3 test assertions** |

---

## Executive Summary

H11B removes the legacy reopen claim restoration helper `_restore_claim_continuity_for_reopen` from `operation_service.py` and updates three test assertions in `test_reopen_resumability_claim_continuity.py` to reflect StationSession-native ownership expectations.

After H11B:
- Reopen does not create, restore, or extend any `OperationClaim` row.
- `CLAIM_RESTORED_ON_REOPEN` audit events are no longer produced.
- Resume after reopen continues to be governed by `ensure_open_station_session_for_command` (unchanged from H4).
- Claim APIs, service, model, table, and audit history are untouched.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Source | Evidence | Impact |
|---|---|---|
| `station-session-command-guard-enforcement-contract.md` | Resume command is in the enforced 08C subset, gated by `ensure_open_station_session_for_command` | Resume after reopen is already StationSession-guarded; claim restoration is not needed for resume continuity |
| `station-session-ownership-contract.md` | StationSession is target ownership truth; claim is compatibility-only | Reopen ownership continuity must be StationSession-derived, not claim-derived |
| `p0-c-08h11-reopen-claim-compatibility-retirement-contract.md` | H11 approved: risk LOW; 3 assertion updates; no claim API/service/table change | H11B scope confirmed |
| `operation_service.py` (line 1347) | `resume_operation` calls `ensure_open_station_session_for_command` before any state guard | Resume is StationSession-gated; claim restoration at reopen is redundant dead code |

### Event Map

| Event / Audit Surface | Before H11B | After H11B | Historical Data |
|---|---|---|---|
| `CLAIM_RESTORED_ON_REOPEN` | Produced by helper on reopen | Not produced | Historical records retained in DB |
| `CLAIM_CREATED` | Produced by claim API | Unchanged | Unchanged |
| `CLAIM_RELEASED` | Produced by claim API | Unchanged | Unchanged |
| `OPERATION_REOPENED` | Produced by `reopen_operation` | Unchanged | Unchanged |
| StationSession lifecycle events | Unchanged | Unchanged | Unchanged |

### Invariant Map

| Invariant | Status |
|---|---|
| Reopen must not restore claim ownership | ✅ ENFORCED post-H11B |
| Reopen must not create claim rows | ✅ ENFORCED post-H11B |
| Resume after reopen must rely on StationSession | ✅ ENFORCED (unchanged, H4) |
| Queue remains claim null-only | ✅ ENFORCED (H10; no change) |
| Claim APIs remain active/deprecated | ✅ RETAINED (unchanged) |
| Claim audit history retained | ✅ ENFORCED (no audit row deletion) |
| No DB migration | ✅ SATISFIED |

### State Transition Map

| Flow | Before H11B | After H11B |
|---|---|---|
| close → reopen | Helper restores/extends claim | Helper removed; no claim touched |
| reopen with previous active claim | Helper extends TTL | Existing claim untouched by reopen |
| reopen → resume with valid StationSession | StationSession guard passes | Unchanged |
| reopen → resume without StationSession | StationSession guard rejects | Unchanged |
| reopen with conflicting claim on owner | Restoration skipped | No restoration attempted at all |

### Test Matrix

| Test Suite | Required Assertion | Status |
|---|---|---|
| `test_reopen_restores_last_claim_owner_path_and_resume_is_reachable` | No new claim created; resume succeeds via StationSession | ✅ UPDATED |
| `test_reopen_preserves_active_claim_continuity_when_claim_still_exists` | Reopen succeeds; closure_status open | ✅ UPDATED |
| `test_reopen_skips_claim_restoration_when_owner_has_other_active_claim` | No active claim for reopened op | ✅ UPDATED (assertion correct, message clarified) |
| `test_reopen_operation_claim_continuity_hardening.py` | Unchanged (teardown-only) | ✅ UNCHANGED |
| Full backend suite | 391 passed, 3 skipped | ✅ CLEAN |

**Verdict: `ALLOW_IMPLEMENTATION`**

---

## Scope and Non-Scope

### In Scope (H11B)

- Remove `_restore_claim_continuity_for_reopen` function (77 lines) from `operation_service.py`
- Remove call to `_restore_claim_continuity_for_reopen` in `reopen_operation`
- Remove unused import: `from app.models.station_claim import OperationClaim, OperationClaimAuditLog`
- Remove unused import: `timedelta` from `from datetime import datetime, timedelta, timezone`
- Remove unused import: `settings` from `from app.config.settings import settings`
- Update 3 test assertions in `test_reopen_resumability_claim_continuity.py`

### Out of Scope (H11B)

- Claim API disablement (H12)
- Claim service/model/table/audit removal (H14)
- Audit retention decision (H13)
- `close_operation` StationSession enforcement
- Queue payload changes
- Frontend changes
- DB migrations
- Any reopen command guard change

---

## Source Usage Inventory

Before removal, all usages of affected symbols in `operation_service.py` were verified:

| Symbol | Usages | Scope |
|---|---|---|
| `OperationClaim` | Lines 387, 389–393, 408, 410–413, 420, 422–428, 437 | All inside `_restore_claim_continuity_for_reopen` only |
| `OperationClaimAuditLog` | Line 448 | Inside `_restore_claim_continuity_for_reopen` only |
| `timedelta` | Lines 399, 443 | Inside `_restore_claim_continuity_for_reopen` only |
| `settings` | Lines 399, 443 | Inside `_restore_claim_continuity_for_reopen` only |

All four symbols confirmed unused elsewhere in `operation_service.py` after removal. All four removed.

---

## Files Changed

| File | Change Type | Description |
|---|---|---|
| `backend/app/services/operation_service.py` | Production code | Removed `_restore_claim_continuity_for_reopen` function + call site + 4 unused imports |
| `backend/tests/test_reopen_resumability_claim_continuity.py` | Test update | Updated 3 claim DB assertions to StationSession-native expectations |

---

## Reopen Behavior Changes

### Before H11B

`reopen_operation` called `_restore_claim_continuity_for_reopen(db, operation=operation, tenant_id=tenant_id)` before creating the `OPERATION_REOPENED` event.

The helper:
1. Queried for an active (unreleased) claim on the operation.
2. If found, extended its TTL.
3. If not found, queried for the last historical claim.
4. If found and no conflicting claim, created a new `OperationClaim` row with a fresh TTL and emitted `CLAIM_RESTORED_ON_REOPEN`.

### After H11B

`reopen_operation` proceeds directly to creating the `OPERATION_REOPENED` event. No claim row is created, extended, or restored. `CLAIM_RESTORED_ON_REOPEN` is never produced.

---

## StationSession Continuity Impact

None. Resume after reopen was already guarded by `ensure_open_station_session_for_command` (H4). The StationSession guard at `resume_operation` line 1347 is unchanged. Resume succeeds if and only if a matching OPEN StationSession exists for the operation's station — claim ownership is irrelevant.

---

## Claim API / Service / Table Impact

None. `station_claim_service.py`, `station_claim.py` (model), and the claim DB table are unchanged. Claim create/release/get APIs remain active with deprecation headers (H9/F). This is exclusively a reopen path behavioral change.

---

## Audit / Event Impact

`CLAIM_RESTORED_ON_REOPEN` events will no longer be produced after H11B. Historical `CLAIM_RESTORED_ON_REOPEN` rows already in the DB are retained. The audit log table is untouched. Audit retention policy for historical claim events is deferred to H13.

---

## Test / Verification Results

### Backend Reopen + Continuity Suite

```
pytest tests/test_reopen_resume_station_session_continuity.py
      tests/test_reopen_resumability_claim_continuity.py
      tests/test_reopen_operation_claim_continuity_hardening.py
      tests/test_close_reopen_operation_foundation.py
```

Result: **26 passed** | `H11B_REOPEN_EXIT:0`

### Backend Compat Suite

```
pytest tests/test_execution_route_claim_guard_removal.py
      tests/test_claim_api_deprecation_lock.py
      tests/test_station_queue_active_states.py
      tests/test_station_queue_session_aware_migration.py
```

Result: **27 passed** | `H11B_COMPAT_EXIT:0`

### Full Backend Suite

```
pytest --tb=no -q
```

Result: **391 passed, 3 skipped** | `H11B_FULLSUITE_EXIT:0`

### Frontend Lint

Result: `H11B_FRONTEND_LINT_EXIT:0` — no errors

### Frontend Build

Result: `H11B_FRONTEND_BUILD_EXIT:0` — clean (3408 modules, 7.68s; pre-existing chunk size warning only)

### Frontend Route Accessibility Gate

Result: `H11B_FRONTEND_ROUTE_SMOKE_EXIT:0` — 24 PASS, 0 FAIL; 77/78 routes covered

---

## Remaining Claim Retirement Blockers

| Blocker | Resolved by |
|---|---|
| Claim API still active/callable | H12 runtime disablement contract + H12B implementation |
| Claim code (`station_claim_service.py`, model, repository) still present | H14 code + table removal contract |
| DB table `operation_claims`, `operation_claim_audit_log` still exists | H14 migration |
| Audit retention decision deferred | H13 contract |
| Historical `CLAIM_RESTORED_ON_REOPEN` records in DB | H13 retention decision |

---

## Recommendation

No further action required in this slice. Stop here.

Next: H12 Claim API Runtime Disablement Contract.

---

## Final Verdict

```
P0_C_08H11B_COMPLETE_VERIFICATION_CLEAN
```

- `_restore_claim_continuity_for_reopen` removed from `operation_service.py`
- Call site removed from `reopen_operation`
- 4 unused imports removed
- 3 test assertions updated to StationSession-native expectations
- 391 backend tests passing, 3 skipped
- Frontend lint, build, route gate all clean
- No regressions detected

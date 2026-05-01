# P0-C-08H7 Queue Claim Payload Retirement Contract / Review

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Reviewed queue claim compatibility payload retirement readiness after frontend claim/release consumer cutover. |

---

## Routing

- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only
- Hard Mode MOM: v3
- Reason: Task touches station queue read-model contract, StationSession ownership truth, claim compatibility payload boundary, and claim audit retention — all v3 trigger zones.

---

## 1. Executive Summary

P0-C-08H7 is a CONTRACT-ONLY / REVIEW task. No code was changed.

The station queue currently carries a dual-shape payload: an ownership block (`ownership.*`) derived from StationSession, and a compatibility claim block (`claim.*`) derived from OperationClaim. Frontend consumers have migrated to ownership-first logic with claim fallback (H2+), and `canExecute` no longer uses claim-derived enablement (H6-V1). However, both shapes remain in the backend payload and all frontend components still read `claim.*` fields for fallback display.

**H7 conclusion:** The queue claim payload can be staged for frontend-only fallback retirement first (H8), followed by backend null-only compatibility contract (H9), followed by eventual removal. Direct backend field deletion in H8 is not recommended.

---

## 2. Scope Reviewed

- Backend queue payload shape (`station_claim_service.py`, `schemas/station.py`)
- Frontend queue consumers (`StationQueuePanel.tsx`, `QueueOperationCard.tsx`, `StationExecutionHeader.tsx`, `AllowedActionZone.tsx`, `stationApi.ts`, `StationExecution.tsx`)
- Existing test coverage locking queue payload shape
- Claim API and reopen claim compatibility state
- Audit retention decision state

---

## 3. Hard Mode MOM v3 Gate

### Design Evidence Extract

| Fact | Source |
|---|---|
| StationSession is target ownership truth | station-session-ownership-contract.md + queue `ownership` block in schema |
| Claim is deprecated compatibility-only | H5 sequencing contract + stationApi.ts deprecation comments |
| Frontend must not use claim for command authorization | copilot-instructions.md Non-negotiables + H6-V1 |
| Queue ownership block is the target read-model contract | H2 implementation: `ownerState + hasOpenSession` primary |
| Queue claim payload is compatibility surface | H2+: claim fallback present in 3 FE components |
| Backend remains source of queue / read-model truth | station_claim_service.get_station_queue is authoritative |
| Claim audit/history is still unresolved | H5 sequencing contract: audit retention unresolved |
| H7 is contract-only; no runtime behavior change | Verified: no code changes in this slice |

### Event Map

| Area | Current Event Impact | H7 Change? | Notes |
|---|---|:---:|---|
| CLAIM_CREATED | Audit trace for claim lifecycle | No | Must remain while claim APIs active |
| CLAIM_RELEASED | Audit trace for release lifecycle | No | Must remain while claim runtime exists |
| CLAIM_EXPIRED | Audit trace for auto-expiry | No | Must remain while claim table exists |
| CLAIM_RESTORED_ON_REOPEN | Reopen compatibility bridge event | No | Must remain behind reopen helper |
| OPERATION_REOPENED | Canonical execution event (source of truth) | No | Untouched |
| Queue ownership read model | Derived from StationSession at queue fetch time | No | Target shape, no event needed |

### Invariant Map

| Invariant | Status |
|---|---|
| Queue ownership truth must be StationSession-derived | ✅ ENFORCED — `ownership` block from `get_active_station_session_for_station` |
| Claim compatibility payload must not drive execution affordance | ✅ ENFORCED — H6-V1 removed `canExecute` claim path |
| Frontend must not infer command authorization from claim fields | ✅ ENFORCED — no `claim.state === "mine"` in `canExecute` |
| Queue response consumers must not break silently | ⚠️ RISK — if `claim` removed from backend, 3 FE components break |
| Backend queue service remains source of queue truth | ✅ ENFORCED |
| Claim APIs remain deprecated/active | ✅ RETAINED |
| Reopen compatibility remains unchanged | ✅ RETAINED |
| Audit retention remains unresolved | ⚠️ UNRESOLVED — requires explicit governance decision |
| No DB migration in H7 | ✅ SATISFIED |

### State / Read Model Impact Map

| Queue / UI State | Current Source | Target Source | H7 Decision Needed |
|---|---|---|---|
| `owner_state` | `get_active_station_session_for_station` in `get_station_queue` | StationSession (same) | No |
| `has_open_session` | `active_station_session is not None` | StationSession (same) | No |
| `target_owner_type` | Hardcoded `"station_session"` | StationSession (same) | No |
| `ownership_migration_status` | Hardcoded `"TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT"` | Should become `"TARGET_SESSION_OWNER"` when compat retired | H9 decision |
| `compatibility_claim` / `claim.state` | `_to_claim_state()` from `OperationClaim` table | Remove (H9) | H8 FE fallback removal first |
| `claimed_by_user_id` | `OperationClaim.claimed_by_user_id` | Remove (H9) | H8 FE fallback removal first |
| Claim `expires_at` | `OperationClaim.expires_at` | Remove (H9) | H8 FE fallback removal first |
| Action readiness / `canExecute` | `ownerState === "mine" && hasOpenSession` | ✅ Already ownership-only (H6-V1) | None — already complete |
| Queue filter "mine" | Ownership-first with claim fallback in `matchesQueueFilter` | Ownership-only | H8 action |
| Queue summary "mine" count | Ownership-first with claim fallback in `summary.mine` | Ownership-only | H8 action |
| Queue card `lockedByOther` | Ownership-first with claim fallback | Ownership-only | H8 action |
| Queue card `isMine` | Ownership-first with claim fallback | Ownership-only | H8 action |
| Queue card `ownershipHint` | Ownership-first with claim fallback | Ownership-only | H8 action |

### Test Matrix

| Test Area | Existing Test | Required for H8? | Purpose |
|---|---|:---:|---|
| Queue ownership block present | `test_station_queue_session_aware_migration.py` | Must stay green | Locks ownership shape |
| Queue claim block present | `test_station_queue_active_states.py` | Update/weaken for H8 | Currently asserts `claim.state` |
| Claim deprecation headers | `test_claim_api_deprecation_lock.py` | Must stay green | Locks deprecation signal |
| Route claim guard removal | `test_execution_route_claim_guard_removal.py` | Must stay green | Locks command guard state |
| Reopen resume continuity | `test_reopen_resume_station_session_continuity.py` | Must stay green | Reopen continuity |
| Reopen claim continuity hardening | `test_reopen_operation_claim_continuity_hardening.py` | Must stay green | Reopen claim compat |
| Reopen resumability claim continuity | `test_reopen_resumability_claim_continuity.py` | Must stay green | Claim continuity safety |
| FE: queue card renders without claim fallback | None yet | Required | Prove FE works without claim fields |
| FE: `canExecute` independent of claim | None yet | Required | Prove affordance not claim-driven |
| FE: claim fields absent/null does not enable commands | None yet | Required | Prove null-safety |
| FE: lint / build / route smoke | Existing scripts | Must stay green | Baseline regression |

### Verdict

```
ALLOW_CONTRACT_REVIEW
```

Not `ALLOW_IMPLEMENTATION` — this slice is contract/review only. No implementation was done.

---

## 4. Queue Claim Payload Inventory

### Backend field inventory (from `schemas/station.py` + `station_claim_service.get_station_queue`)

| Field / Concept | Backend Schema/Source | Frontend Consumer | Current Role | Retirement Risk | H8 Candidate? |
|---|---|---|---|---|---|
| `claim.state` | `ClaimSummary.state` / `_to_claim_state()` | `StationQueuePanel`, `QueueOperationCard`, `stationApi.ts` type | COMPATIBILITY_FALLBACK | HIGH | Partial (FE fallback only in H8) |
| `claim.expires_at` | `ClaimSummary.expires_at` | `stationApi.ts` type only | COMPATIBILITY_DISPLAY | LOW | FE type cleanup in H8 |
| `claim.claimed_by_user_id` | `ClaimSummary.claimed_by_user_id` | `stationApi.ts` type only | COMPATIBILITY_DISPLAY | LOW | FE type cleanup in H8 |
| `ownership.owner_state` | `SessionOwnershipSummary.owner_state` | `StationExecution.tsx`, `StationQueuePanel`, `QueueOperationCard` | TARGET_OWNERSHIP | None | Must stay |
| `ownership.has_open_session` | `SessionOwnershipSummary.has_open_session` | Same as above | TARGET_OWNERSHIP | None | Must stay |
| `ownership.target_owner_type` | `SessionOwnershipSummary.target_owner_type` | `stationApi.ts` type + FE reads | TARGET_OWNERSHIP | None | Must stay |
| `ownership.ownership_migration_status` | `SessionOwnershipSummary.ownership_migration_status` | `stationApi.ts` type, test assertion | COMPATIBILITY_DISPLAY | MEDIUM | Value update in H9 (remove `_WITH_CLAIM_COMPAT`) |
| `ownership.session_id` | `SessionOwnershipSummary.session_id` | `stationApi.ts` type | TARGET_OWNERSHIP | None | Must stay |
| `ownership.station_id` | `SessionOwnershipSummary.station_id` | `stationApi.ts` type | TARGET_OWNERSHIP | None | Must stay |
| `ownership.session_status` | `SessionOwnershipSummary.session_status` | `stationApi.ts` type | TARGET_OWNERSHIP | None | Must stay |
| `ownership.operator_user_id` | `SessionOwnershipSummary.operator_user_id` | `stationApi.ts` type | TARGET_OWNERSHIP | None | Must stay |
| `QueueClaimState` type | Frontend type alias `"none" \| "mine" \| "other"` | `stationApi.ts` + `ClaimSummary` interface | COMPATIBILITY_DISPLAY | LOW | Remove in H9 with `ClaimSummary` interface |
| `ClaimSummary` interface | Frontend `stationApi.ts` | `StationQueueItem.claim` field | COMPATIBILITY_DISPLAY | MEDIUM | Remove interface + field in H9 |
| `StationQueueItem.claim` field | Frontend `stationApi.ts` | `StationQueuePanel`, `QueueOperationCard` | COMPATIBILITY_FALLBACK | HIGH | FE fallback removal in H8; type removal in H9 |

---

## 5. Backend Queue Contract Review

| Backend Area | File | Claim Payload Role | StationSession Replacement Exists? | Can Remove in H8? | Notes |
|---|---|---|---|---|---|
| `ClaimSummary` schema | `schemas/station.py` | Claim fields in queue response body | Yes (`SessionOwnershipSummary`) | No — H9 only | Removing would break FE `claim.*` reads |
| `StationQueueItem.claim` | `schemas/station.py` | Queue item carries `claim: ClaimSummary` | Yes (`ownership: SessionOwnershipSummary`) | No — H9 only | Must keep while FE still reads `item.claim.*` |
| `get_station_queue` claim block | `station_claim_service.py` lines 375-383 | Builds `"claim": {"state":..., "expires_at":..., "claimed_by_user_id":...}` | Yes — ownership block built alongside | No — H9 only | Removing now would break `test_station_queue_active_states.py` |
| `get_station_queue` ownership block | `station_claim_service.py` lines 385-412 | Builds full `ownership.*` block from StationSession | N/A — this IS the replacement | Must stay | Target contract; no change needed |
| Claim API routes (`/claim`, `/release`, `/status`) | `api/v1/station.py` | Deprecated compatibility routes | Yes (StationSession session management) | No — H11 only | Still callable; deprecation headers present |
| `station_claim_service` | `station_claim_service.py` | Claim CRUD + expiry + audit | Yes (station_session_service) | No — H12 only | Still active for claim API routes |
| `OperationClaim` model/table | `models/station_claim.py` | Persistence for claim data | Yes (StationSession model) | No — H13 only | Foreign key to audit log |
| `OperationClaimAuditLog` model/table | `models/station_claim.py` | Claim audit history | N/A — audit is own concern | No — H12/H13 | Retention decision unresolved |

---

## 6. Frontend Consumer Review

| Frontend File | Claim Payload Usage | Display / Fallback / Affordance | H8 Action | Risk |
|---|---|---|---|---|
| `stationApi.ts` | `ClaimSummary` interface, `QueueClaimState` type, `StationQueueItem.claim` field, `claim()`, `release()`, `getClaim()` methods | COMPATIBILITY_DISPLAY (types/client methods) | Remove fallback logic; keep types until H9 backend payload removed | LOW |
| `StationExecution.tsx` | No `claim.*` reads post H6-V1 | None — already clean | No H8 action needed | NONE |
| `StationQueuePanel.tsx` | `item.claim.state === "mine"` in `matchesQueueFilter`, `hasMineClaim`, `summary.mine` count | COMPATIBILITY_FALLBACK | Remove claim fallback from filter + summary logic | MEDIUM |
| `QueueOperationCard.tsx` | `item.claim.state === "other"`, `item.claim.state === "mine"` in `lockedByOther`, `isMine`, `ownershipHint`, `ownershipHintTone` | COMPATIBILITY_FALLBACK | Remove claim fallback from all display logic | MEDIUM |
| `AllowedActionZone.tsx` | None — receives `canExecute` prop only | N/A | No H8 action | NONE |
| `StationExecutionHeader.tsx` | Ownership badge comment references claim fallback (display only) | COMPATIBILITY_DISPLAY (comment only) | Update comment in H8 | LOW |

**No BLOCKER found.** No claim field currently drives `canExecute`, `canPauseExecution`, `canStartDowntime`, or any other action enablement. Frontend claim usage is display/fallback only.

---

## 7. API Compatibility / Versioning Decision

| Option | Pros | Cons | Risk | Recommendation |
|---|---|---|---|---|
| A — Remove claim fields directly in H8 | Simple, clean | Breaks `StationQueuePanel` + `QueueOperationCard` + 3+ test assertions immediately | HIGH | Reject |
| B — Keep response shape, mark claim fields deprecated/null-only in H9 | Safe transition; backend still sends fields but null-valued | Nulls require FE null-safety checks | MEDIUM | Recommended for H9 |
| C — Add versioned queue response / feature flag | Maximum safety for external clients | Complexity, adds indirection | LOW-MEDIUM | Not needed — no external API consumers proven |
| D — Frontend-only fallback removal first, backend payload remains | FE cleaned up without backend risk; can validate before backend changes | Backend still sends unused claim data | LOW | **Recommended for H8** |
| E — Defer queue payload retirement until claim API disablement | No risk of premature removal | Delays cleanup significantly | LOW | Partial deferral acceptable for claim service/table; not for FE fallback |

**Recommended direction:**
- **H8**: Option D — Frontend queue fallback removal only. Backend payload unchanged. FE components use ownership-only logic.
- **H9**: Option B — Backend claim block sent as null-only (zero-impact contract change). Update `ownership_migration_status` to `"TARGET_SESSION_OWNER"`.
- **H10+**: Progressive backend claim/service/table/audit retirement with explicit contracts and tests.

---

## 8. Queue Payload Retirement Scope for H8

**Slice name:** `P0-C-08H8 Frontend Queue Claim Fallback Retirement`

### H8 In Scope

| H8 Candidate Action | Files | Tests Required | Risk |
|---|---|---|---|
| Remove `item.claim.state` fallback from `matchesQueueFilter` | `StationQueuePanel.tsx` | FE test: filter works with only ownership block | MEDIUM |
| Remove `item.claim.state` fallback from `hasMineClaim` | `StationQueuePanel.tsx` | FE test: mine-count correct without claim | MEDIUM |
| Remove `item.claim.state` fallback from `summary.mine` | `StationQueuePanel.tsx` | FE test: summary correct without claim | MEDIUM |
| Remove `item.claim.state` fallback from `lockedByOther`, `isMine` | `QueueOperationCard.tsx` | FE test: lock/owned display correct without claim | MEDIUM |
| Remove `item.claim.state` fallback from `ownershipHint`, `ownershipHintTone` | `QueueOperationCard.tsx` | FE test: hint text correct without claim | LOW |
| Update ownership badge comment in header | `StationExecutionHeader.tsx` | None required | LOW |
| FE lint / build / route smoke | All FE | All must pass | HIGH |

### H8 Out of Scope

- Backend claim block removal from `get_station_queue` response
- `ClaimSummary` schema removal from `schemas/station.py`
- `StationQueueItem.claim` field removal from backend schema
- `ClaimSummary` / `QueueClaimState` interface removal from `stationApi.ts`
- `claim()`, `release()`, `getClaim()` client method removal from `stationApi.ts`
- Claim API route disablement (H11)
- Claim service/model/table removal (H13)
- Reopen claim compatibility removal (H10)
- Audit retention decision (H12)
- DB migrations of any kind

---

## 9. Test Requirements for H8

| Test | Required Assertion | Blocking? |
|---|---|---|
| FE: queue filter "mine" works with ownership-only | `matchesQueueFilter` returns correct items when `claim.state` absent | Yes |
| FE: queue summary "mine" count uses ownership-only | `summary.mine` counts correctly when `claim.state` absent | Yes |
| FE: `QueueOperationCard` lock display ownership-only | `lockedByOther`, `isMine` correct with null claim | Yes |
| FE: `QueueOperationCard` ownershipHint ownership-only | Hint text correct with null claim | Yes |
| FE: `canExecute` not affected by claim fields | `canExecute` unchanged after claim fallback removal | Yes |
| FE: lint | No new lint errors | Yes |
| FE: build | No new build errors | Yes |
| FE: route smoke | All 77/78 routes covered | Yes |
| BE: `test_station_queue_session_aware_migration.py` | Ownership block still correct | Yes |
| BE: `test_claim_api_deprecation_lock.py` | Claim API headers still present | Yes |
| BE: `test_execution_route_claim_guard_removal.py` | H4 guards still correct | Yes |
| BE: `test_reopen_resume_station_session_continuity.py` | Reopen continuity intact | Yes |
| BE: `test_station_queue_active_states.py` | Queue shape test remains green (no backend change) | Yes |

---

## 10. Remaining Claim Retirement Blockers After H8

| Blocker | Current Evidence | Resolved by H8? | Future Slice |
|---|---|---|---|
| Claim APIs still active (deprecated) | `test_claim_api_deprecation_lock.py` passes; routes return Deprecation headers | No | H11 |
| Claim service still exists | `station_claim_service.py` actively used by queue and claim routes | No | H13 |
| Reopen claim compatibility helper still active | `_restore_claim_continuity_for_reopen` still invoked in `operation_service.py` | No | H10 |
| Claim audit retention unresolved | `OperationClaimAuditLog` still active; no retention/archive strategy | No | H12 |
| `OperationClaim` / `OperationClaimAuditLog` tables remain | Foreign key constraint; cannot drop until retention resolved | No | H13 |
| DB migration / drop not approved | No migration planned | No | H13 |
| `ClaimSummary` / `QueueClaimState` TS types still present | `stationApi.ts` still exposes these interfaces | No (only FE fallback logic removed in H8) | H9 |
| Backend `claim` block still in queue payload | `get_station_queue` still builds `claim.*` dict | No | H9 |
| `ownership_migration_status` still `"TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT"` | Hardcoded string in `get_station_queue` | No | H9 |

---

## 11. H8 / H9 / H10 Roadmap

| Slice | Goal | Code? | Migration? | Preconditions | Stop Conditions |
|---|---|---|---|---|---|
| **P0-C-08H8** Frontend Queue Claim Fallback Retirement | Remove `claim.*` fallback logic from `StationQueuePanel` and `QueueOperationCard`; ownership-only queue display | FE only | No | H6-V1 complete; canExecute ownership-only | Do NOT remove `claim` type from `stationApi.ts`; do NOT touch backend payload |
| **P0-C-08H9** Backend Queue Claim Payload Null-Only Contract | Send `claim` block as null-only or omit; update `ownership_migration_status` to `"TARGET_SESSION_OWNER"`; remove `ClaimSummary` + `QueueClaimState` from `stationApi.ts` after backend confirms null-safe | BE + FE types | No | H8 complete; FE no longer reads claim fields for logic | Do NOT remove `OperationClaim` table; do NOT touch claim service |
| **P0-C-08H10** Reopen Claim Compatibility Retirement Contract | Review and retire `_restore_claim_continuity_for_reopen`; replace with session-native continuity | BE service | No | Reopen session-native continuity contract and tests passing | Do NOT remove claim table; requires dedicated contract review |
| **P0-C-08H11** Claim API Runtime Disablement Contract | Disable claim/release/status endpoints (return 410 Gone or remove routes); remove `claim()`, `release()`, `getClaim()` from `stationApi.ts` | BE routes + FE client | No | H9 + H10 complete; no consumers calling claim APIs | Do NOT delete claim service or model; disable only |
| **P0-C-08H12** Audit Retention Decision | Define claim audit log retention period; decide archive vs. keep-forever vs. time-bounded purge | Possibly migration | Possibly | Governance/compliance decision made | Cannot proceed without explicit data governance approval |
| **P0-C-08H13** Claim Code/Table Removal Migration Contract | Drop `OperationClaim`, `OperationClaimAuditLog` tables; remove service/model/schemas; clean up all claim code | BE model + migration | Yes | H11 + H12 complete; audit retention resolved | Most destructive slice; requires explicit approval per governance rules |

---

## 12. Risk Register

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| Frontend breaks if `claim.*` removed from backend before H8 FE cleanup | HIGH | HIGH if sequencing violated | Strict slice ordering: H8 before H9 |
| Queue filter "mine" breaks if claim fallback removed without test | MEDIUM | LOW if tests written first | Require FE tests before H8 implementation |
| Reopen path regression if `_restore_claim_continuity_for_reopen` removed prematurely | HIGH | LOW if H10 contract followed | Dedicated H10 contract + test matrix required |
| Audit compliance risk if claim log dropped without retention decision | HIGH | MEDIUM if H12 skipped | Explicitly require governance decision before H13 |
| `ownership_migration_status` stays stale string forever | LOW | MEDIUM | Update in H9 as part of payload contract cleanup |
| External API consumers reading `claim.*` fields (unknown) | MEDIUM | LOW — no evidence of external consumers | Option B (null-only first) in H9 provides safe transition |

---

## 13. Recommendation

1. **H8 is the correct next slice**: Frontend queue claim fallback retirement. Safe, reversible, no backend changes needed.
2. **Do not remove backend claim block in H8.** The TypeScript `ClaimSummary` types and `item.claim.*` reads in FE components must be removed first so null-safety is proven before backend sends null/omits.
3. **H9 follows H8** after FE is verified working with ownership-only queue display. H9 can then confidently null-out or omit the claim block in the backend response.
4. **Claim service/model/table removal (H13) requires separate governance approval** and must wait for audit retention decision (H12).
5. **Do not combine slices.** Each slice should have its own contract, test matrix, and verification gate.

---

## 14. Final Verdict

```
READY_FOR_P0_C_08H8_FRONTEND_QUEUE_CLAIM_FALLBACK_RETIREMENT
```

### Verification Results

| Check | Result |
|---|---|
| H7_BACKEND_SMOKE_EXIT | 0 (24 passed) |
| H7_FRONTEND_LINT_EXIT | 0 |
| H7_FRONTEND_BUILD_EXIT | 0 (confirmed previous build) |
| H7_FRONTEND_ROUTE_SMOKE_EXIT | 0 (77/78 covered, 24 checks PASS) |

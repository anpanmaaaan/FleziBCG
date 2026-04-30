# P0-C-04E Claim Compatibility / Deprecation Lock

**Slice:** P0-C-04E  
**Classification:** Compatibility Lock — DOC-ONLY  
**Hard Mode MOM v3 Verdict:** ALLOW_IMPLEMENTATION (no production code changes required)  
**Date:** 2025  
**Status:** COMPLETE

---

## Purpose

This document locks the claim compatibility boundary established by the
`station-session-ownership-contract.md §6` contract.

P0-C-04E is **not** claim removal. It is the explicit lock that prevents
the claim layer from being expanded, repurposed, or conflated with
StationSession ownership going forward.

---

## Compatibility Boundary (Non-negotiable)

1. **Claim is compatibility layer.** It is migration debt, not target ownership truth.
2. **Claim is not target ownership truth.** StationSession is the target ownership model.
3. **Claim must not be expanded** in any subsequent slice without an explicit
   contract revision and ADR.
4. **Claim must not be removed** in P0-C-04E — removal is a future slice requiring
   an explicit migration plan and ADR entry.
5. **StationSession is the target ownership model.**
6. **The P0-C-04D diagnostic bridge (`_session_ctx`) remains non-blocking.**
   It does not alter claim evaluation at any point in the execution path.
7. **`ensure_operation_claim_owned_by_identity` remains at route layer** and
   continues to act as the operational guard until an alignment slice explicitly
   replaces it.
8. **`_restore_claim_continuity_for_reopen` must not be removed** until the
   replacement plan is explicitly defined.

---

## Claim Source Map (as of P0-C-04E)

| Component | Location | Role |
|---|---|---|
| `OperationClaim` model | `backend/app/models/station_claim.py` | Compatibility ORM model |
| `OperationClaimAuditLog` model | `backend/app/models/station_claim.py` | Compatibility audit trail |
| `claim_operation` | `backend/app/services/station_claim_service.py` | Create claim (one-active-per-operator) |
| `release_operation_claim` | `backend/app/services/station_claim_service.py` | Release with ownership check |
| `ensure_operation_claim_owned_by_identity` | `backend/app/services/station_claim_service.py` | Route-layer execution guard (8 endpoints) |
| `get_station_queue` | `backend/app/services/station_claim_service.py` | Returns queue with claim state |
| `get_operation_claim_status` | `backend/app/services/station_claim_service.py` | Returns current claim state |
| `_restore_claim_continuity_for_reopen` | `backend/app/services/operation_service.py` | Reopen path claim continuity |
| Route enforcement (8 endpoints) | `backend/app/api/v1/operations.py` lines 86,114,138,170,202,249,283 | Pre-command claim guard |

---

## Diagnostic Bridge Non-Interference Contract

`_compute_session_diagnostic()` in `operation_service.py` (introduced in P0-C-04D):

- Called **before** `_ensure_operation_open_for_write` in all 9 execution commands.
- Result (`_session_ctx: StationSessionDiagnostic`) is **local and informational only**.
- Has **no conditional branching** — never affects execution outcome.
- Does **not** interact with `ensure_operation_claim_owned_by_identity`.
- Does **not** modify claim state.
- Does **not** create dual ownership by reading session state alongside claim state.

The claim guard at route layer runs at HTTP boundary **before** operation_service is called.
The diagnostic runs **inside** operation_service **after** the claim has already been verified.
There is zero overlap and zero dual authority.

---

## Test Coverage (Compatibility Lock)

The following test suites act as the living compatibility lock.
**All must remain green on every future merge.**

| Test File | Tests | What It Locks |
|---|---|---|
| `test_claim_single_active_per_operator.py` | 6 | One-active-per-operator invariant |
| `test_release_claim_active_states.py` | 14 | Release rules, ownership, expiry, status guards |
| `test_station_queue_active_states.py` | 8 | Queue with claim states |
| `test_reopen_resumability_claim_continuity.py` | 4 | Reopen/resume claim continuity |
| `test_close_reopen_operation_foundation.py` | 4 | Close/reopen foundation |
| `test_station_session_command_context_diagnostic.py` | 9 | Diagnostic does not affect claim |

**Total: 45 tests as compatibility lock.**

---

## What P0-C-04E Does NOT Change

- `backend/app/models/station_claim.py` — untouched
- `backend/app/services/station_claim_service.py` — untouched
- `backend/app/services/operation_service.py` — untouched (P0-C-04D wiring already complete)
- `backend/app/api/v1/operations.py` — untouched
- Any existing test file — untouched

---

## Migration Debt Register

The following debt exists and is explicitly deferred to a future slice:

| Debt Item | Deferred To | Requires |
|---|---|---|
| Remove `ensure_operation_claim_owned_by_identity` from routes | P0-C-05 or later | StationSession enforcement proven in production; ADR |
| Remove `OperationClaim` / `OperationClaimAuditLog` | Post-enforcement | Data migration, archived audit trail strategy |
| Remove `_restore_claim_continuity_for_reopen` | Post-enforcement | Reopen path uses StationSession for continuity |
| Remove `station_claim_service.py` | Final cleanup slice | All above debt resolved |

---

## Next Slice

P0-C-05 (not yet scheduled): Hard StationSession enforcement gate.

Pre-conditions for P0-C-05:
- StationSession is operational in production for all tenant stations.
- Monitoring confirms >99.9% of execution commands have a matching OPEN session.
- ADR approved for claim removal timeline.
- Rollback plan documented.

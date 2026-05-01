# P0-C-08G Claim Table / Code Removal Readiness Check

## History
- 2026-05-01: Review-only readiness audit completed after P0-C-08E-V2 and P0-C-08F.
- Constraints honored: no runtime code changes, no migrations, no frontend UI changes, no claim behavior changes, no StationSession guard changes, no queue behavior changes, no reopen or resume behavior changes, no close behavior changes.
- Verification executed sequentially against the current backend baseline:
  - `tests/test_claim_api_deprecation_lock.py` -> `5 passed`
  - `tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py` -> `28 passed`
  - `tests/test_station_session_command_guard_enforcement.py tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py` -> `29 passed`
  - full backend suite -> `289 passed, 1 skipped`

## 1. Executive Summary
Claim is not ready for direct runtime removal. It remains wired into three live control paths: execution command authorization compatibility, reopen continuity compatibility, and the frontend station queue and execution UX contract.

The backend replacement path exists, but it is only partial. `StationSession` is already the target ownership truth for execution commands, and queue payloads now expose additive `ownership` data, but the legacy `claim` contract is still enforced and consumed across backend routes, queue composition, tests, scripts, and frontend UI state.

The codebase is ready for `P0-C-08H` only if `08H` is explicitly scoped as a staged cutover and removal plan, not as immediate table or code deletion.

## 2. Scope Reviewed
- Backend runtime surfaces:
  - `backend/app/api/v1/station.py`
  - `backend/app/api/v1/operations.py`
  - `backend/app/services/station_claim_service.py`
  - `backend/app/services/operation_service.py`
  - `backend/app/schemas/station.py`
  - `backend/app/models/station_claim.py`
- Persistence surfaces:
  - `backend/scripts/migrations/0009_station_claims.sql`
- Frontend consumers:
  - `frontend/src/app/api/stationApi.ts`
  - `frontend/src/app/pages/StationExecution.tsx`
  - `frontend/src/app/components/station-execution/StationQueuePanel.tsx`
  - `frontend/src/app/components/station-execution/QueueOperationCard.tsx`
  - `frontend/src/app/i18n/registry/en.ts`
  - `frontend/src/app/i18n/registry/ja.ts`
- Regression and replacement coverage reviewed via existing backend tests and claim-related search inventory.

## 3. Claim Usage Inventory
| Surface | Current usage | Runtime critical | Readiness note |
| --- | --- | --- | --- |
| Claim ORM models | `OperationClaim`, `OperationClaimAuditLog` are imported by backend services, tests, scripts, and reopen continuity logic | Yes | Cannot remove models until route, reopen, and retention cutover is complete |
| Claim API routes | Claim, release, and claim-status routes remain active in `station.py`; only deprecation headers were added in 08F | Yes | Routes are still called by frontend and tests |
| Claim service | `claim_operation`, `release_operation_claim`, `get_operation_claim_status`, `get_station_queue`, `ensure_operation_claim_owned_by_identity` remain active | Yes | Service still owns queue claim projection and compatibility guard logic |
| Execution commands | Seven execution endpoints in `operations.py` still call `ensure_operation_claim_owned_by_identity` after StationSession guard | Yes | Direct removal would change authorization behavior |
| Reopen continuity | `_restore_claim_continuity_for_reopen` still restores claim rows and writes `CLAIM_RESTORED_ON_REOPEN` audit events | Yes | Reopen path still depends on claim persistence |
| Queue payload | Backend queue schema still returns both `claim` and `ownership` | Yes | Current consumers still rely on `claim` |
| Frontend API client | `stationApi` still defines `ClaimSummary`, `ClaimResponse`, and direct claim/release/getClaim calls | Yes | No frontend cutover to `ownership` yet |
| Frontend execution page | `StationExecution.tsx` derives execution affordances from `claim.state === "mine"` and calls claim APIs | Yes | Strongest consumer blocker |
| Frontend queue components | `StationQueuePanel.tsx` and `QueueOperationCard.tsx` filter and badge by `item.claim.state` | Yes | Queue UX still claim-shaped |
| Tests and scripts | Claim-focused tests and verification scripts remain widespread | No for production runtime, Yes for delivery safety | Must be replaced or retired during later stages |

## 4. Claim API Removal Readiness
| Question | Answer | Evidence | Verdict |
| --- | --- | --- | --- |
| Are claim endpoints already unused? | No | Frontend `stationApi` still calls claim, release, and claim-status routes | Not ready |
| Can claim routes be deleted without frontend breakage? | No | `StationExecution.tsx` calls `stationApi.claim()` and `stationApi.release()` directly | Not ready |
| Did 08F fully replace claim APIs? | No | 08F only added deprecation headers and preserved behavior | Not ready |
| Is queue access independent from claim APIs? | Partially | Queue list route survives, but queue consumers still depend on `claim` data in its payload | Not ready |

Direct claim API removal would break the current frontend and invalidate existing claim route tests immediately.

## 5. Claim Service Removal Readiness
| Question | Answer | Evidence | Verdict |
| --- | --- | --- | --- |
| Can `ensure_operation_claim_owned_by_identity` be removed now? | No | Seven execution endpoints still invoke it after StationSession guard | Not ready |
| Can `get_station_queue` stop returning claim today? | No | Queue schema and frontend queue rendering still consume `claim.state` | Not ready |
| Can claim mutation helpers be removed now? | No | Frontend and backend claim routes still invoke claim and release helpers | Not ready |

Claim service removal must be preceded by execution-route compatibility removal and queue contract cutover.

## 6. Claim Data / Audit Retention Readiness
| Question | Answer | Evidence | Verdict |
| --- | --- | --- | --- |
| Is claim persistence isolated to one migration? | Mostly | `0009_station_claims.sql` creates both claim and claim audit tables plus indexes | Partially ready |
| Is audit retention strategy already decided? | No | `operation_claim_audit_logs` still stores claim history with `claim_id` FK; no archival or migration decision was found in current code | Not ready |
| Can tables be dropped without handling audit lineage? | No | Audit table references `operation_claims(id)` via `claim_id` | Not ready |

The persistence layer is simple enough to stage, but not ready for deletion until audit retention is explicitly decided.

## 7. Station Queue Dependency Review
The queue is not claim-free. Backend queue assembly in `station_claim_service.py` still resolves unreleased claims, computes `claim.state`, lazily expires claim rows, and returns a legacy `claim` object alongside additive `ownership` data.

This is the key migration state:
- Backend queue contract already includes the target `ownership` object.
- Frontend queue contract still types only `claim` and ignores `ownership`.
- Queue filters and badges are still driven by `item.claim.state`.

Conclusion: queue removal readiness is blocked by contract cutover, not by missing backend source-of-truth data.

## 8. Reopen / Resume Claim Dependency Review
Reopen continuity is still claim-backed. `_restore_claim_continuity_for_reopen` in `operation_service.py` still:
- queries prior claim history,
- restores a new active claim row when compatible,
- extends active claim expiry when needed,
- writes `CLAIM_RESTORED_ON_REOPEN` audit events.

This means claim persistence is still part of reopen compatibility semantics even though reopen no longer rejects on owner-conflict in the same way.

Conclusion: claim tables and audit log cannot be removed before reopen continuity is redesigned to use a non-claim ownership path or explicitly retire this compatibility behavior.

## 9. Frontend / Consumer Dependency Review
| Question | Answer | Evidence | Verdict |
| --- | --- | --- | --- |
| Has frontend switched to `ownership`? | No | `stationApi.ts` does not type `ownership`; it still types `claim` only | Not ready |
| Does execution mode still depend on claim state? | Yes | `StationExecution.tsx` uses `claimState === "mine"` to gate execution actions and execution-mode UX | Not ready |
| Does queue selection UX still depend on claim state? | Yes | `StationQueuePanel.tsx` and `QueueOperationCard.tsx` use `item.claim.state` for filters, badges, and lock states | Not ready |
| Are claim strings still user-visible? | Yes | Claim-specific copy remains in i18n registries and screen status documentation | Not ready |

Frontend cutover is the largest visible blocker to removing claim APIs or claim-shaped queue payloads.

## 10. Test Replacement Readiness
| Question | Answer | Evidence | Verdict |
| --- | --- | --- | --- |
| Are there dedicated claim regressions today? | Yes | Claim-specific backend tests remain active and green | Ready to replace gradually |
| Does replacement-path coverage already exist? | Yes | StationSession guard, session-aware queue migration, and reopen continuity tests are already present and green | Ready to expand |
| Can claim tests be deleted now? | No | They still protect live runtime compatibility behavior | Not ready |

Recommended testing sequence for 08H:
1. Add replacement-focused tests before removing any claim compatibility path.
2. Flip frontend and queue contract assertions to `ownership`-based expectations.
3. Remove claim tests only after runtime removal is complete.

## 11. Removal Strategy Options
| Option | Description | Pros | Cons | Recommendation |
| --- | --- | --- | --- | --- |
| A | Directly delete claim APIs, service, models, and tables | Fastest on paper | Breaks frontend, queue UX, reopen compatibility, and execution-route compatibility | Reject |
| B | Backend-only removal first, frontend later | Reduces backend debt early | Breaks current consumers and queue contract immediately | Reject |
| C | Staged cutover: frontend to `ownership`, backend execution-route compatibility removal, reopen redesign, then persistence removal | Preserves behavior and allows focused verification per stage | Requires several controlled slices | Accept |

## 12. Risk Register
| Risk | Severity | Why it matters | Required mitigation |
| --- | --- | --- | --- |
| Frontend break on claim route removal | High | Current UI calls claim and release endpoints directly | Cut frontend to `ownership` and StationSession-first UX before route removal |
| Execution auth drift | High | Seven execution routes still require claim ownership compatibility after StationSession guard | Remove compatibility guard only in a dedicated slice with targeted auth regression coverage |
| Queue contract regression | High | Queue items still expose legacy `claim` contract that frontend consumes | Add frontend and API contract migration slice first |
| Reopen continuity regression | High | Reopen still restores claim rows and audit events | Redesign continuity path before removing claim persistence |
| Audit/history loss | Medium | Claim audit table still holds compatibility history with FK linkage | Decide archive, migration, or deliberate retirement policy |
| Script and test fallout | Medium | Existing verification scripts and tests still import claim models and helpers | Replace after runtime cutover, not before |

## 13. Proposed P0-C-08H Plan
`P0-C-08H` should be a staged removal plan with explicit sub-slices, not a direct deletion slice.

Recommended stages:
1. Frontend contract cutover
   - move queue and execution UX from `claim` to `ownership`
   - stop calling claim and release routes from the main station execution flow
   - retain compatibility fields temporarily behind additive backend payloads
2. Backend execution compatibility removal
   - remove `ensure_operation_claim_owned_by_identity` from the seven execution command routes only after equivalent StationSession coverage is expanded
   - keep claim API routes temporarily deprecated but non-authoritative
3. Reopen continuity redesign
   - replace `_restore_claim_continuity_for_reopen` with a StationSession-compatible continuity path or explicitly retire claim restoration behavior
4. Claim API and queue contract cleanup
   - remove claim-only endpoints
   - remove legacy `claim` payload fields from queue responses after frontend cutover is complete
5. Persistence retirement
   - finalize audit retention decision
   - add migration(s) for audit archival or schema transition
   - drop claim tables only after runtime and consumer references are gone
6. Test and script cleanup
   - replace claim-focused tests/scripts with StationSession and ownership-path assertions

## 14. Recommendation
Do not remove claim runtime, API routes, service code, models, or tables in the current state.

Proceed to `P0-C-08H` only as a staged cutover/removal plan whose first goal is consumer migration, not deletion. The first concrete target should be frontend queue and execution cutover to `ownership`, because that is the narrowest high-value blocker and the clearest discriminator for whether subsequent backend cleanup is safe.

## 15. Final Verdict
`READY_FOR_P0_C_08H_STAGED_REMOVAL_PLAN`

Interpretation: the system is not ready for direct claim removal, but it is ready for an explicitly staged `08H` plan that first removes consumer dependence, then removes backend compatibility logic, and only then retires persistence.
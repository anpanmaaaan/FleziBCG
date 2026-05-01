# P0-C-08H6-V1 Claim-Derived Execution Affordance Removal + Verification Gap Closure

Date: 2026-05-01
Scope: Small frontend fix + verification recovery only.

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: SINGLE-SLICE
- Hard Mode MOM: v3
- Reason: Frontend execution affordance had residual claim-derived enablement that conflicts with StationSession ownership truth.

## Hard Mode MOM v3 Gate

### Design Evidence Extract
- StationSession is target ownership truth.
- Claim API remains deprecated compatibility-only.
- Claim may remain display/debug compatibility only.
- Frontend must not decide authorization from claim.
- Backend command guard remains authoritative.

Sources:
- `docs/implementation/p0-c-08h6-frontend-api-consumer-cutover-report.md`
- `docs/implementation/p0-c-08h5-claim-retirement-sequencing-contract.md`
- `docs/implementation/p0-c-08h4-backend-route-claim-guard-removal-report.md`
- `docs/implementation/p0-c-08h2-frontend-queue-consumer-cutover-report.md`
- `docs/design/02_domain/execution/station-session-ownership-contract.md`
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`

### Current Source Evidence

| File | Finding | H6-V1 Action | Risk |
|---|---|---|---|
| `frontend/src/app/pages/StationExecution.tsx` | `canExecute` used claim fallback (`canExecuteByOwnership || claimState === "mine"`) | Removed claim-derived enablement | High |
| `frontend/src/app/pages/StationExecution.tsx` | No direct `stationApi.claim/release` calls in primary flow | Keep unchanged | Low |
| `frontend/src/app/components/station-execution/AllowedActionZone.tsx` | Action buttons depend on parent `canExecute` | Parent now ownership/session-only | Medium |
| `frontend/src/app/components/station-execution/StationExecutionHeader.tsx` | Display-only ownership/compatibility UI | Keep unchanged | Low |
| `frontend/src/app/components/station-execution/StationQueuePanel.tsx` | Claim fallback in queue filter/summary (compatibility) | Keep unchanged | Low |
| `frontend/src/app/components/station-execution/QueueOperationCard.tsx` | Claim fallback in lock/hint display (compatibility) | Keep unchanged | Low |
| `frontend/src/app/api/stationApi.ts` | `claim/release/getClaim` remain deprecated compatibility client methods | Keep unchanged | Low |

### Invariant Map
- claimState must not enable execution.
- claimState must not bypass missing ownership/session context.
- frontend sends command intent only.
- backend decides success/failure.
- queue claim fallback remains display/debug compatibility only.

### Test Matrix
| Test / Check | Purpose | Required? |
|---|---|---|
| `npm.cmd run lint` | Frontend lint gate | Yes |
| `npm.cmd run build` | Frontend compile/build gate | Yes |
| `npm.cmd run check:routes` | Frontend route smoke gate | Yes |
| `pytest -q tests/test_execution_route_claim_guard_removal.py tests/test_claim_api_deprecation_lock.py tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py` | Backend compatibility and guard continuity gate | Yes |
| grep audit (`claimState`, `canExecute`, `stationApi.claim`, `stationApi.release`) | Verify claim-derived affordance removal | Yes |

### Verdict before coding
`ALLOW_IMPLEMENTATION`

## Implementation

### Code change
File changed:
- `frontend/src/app/pages/StationExecution.tsx`

Change:
- Before:
  - `const canExecute = canExecuteByOwnership || claimState === "mine";`
- After:
  - `const canExecute = canExecuteByOwnership;`

Additional cleanup:
- Removed now-unused local `claimState` in `StationExecution.tsx`.

### Post-fix grep validation
- `claimState === "mine"` in `StationExecution.tsx`: none.
- `canExecuteByOwnership ||` in `StationExecution.tsx`: none.
- `stationApi.claim`/`stationApi.release` in `StationExecution.tsx` and `station-execution` components: none.

## Verification

### Frontend
- `npm.cmd run lint` -> `H6V1_FRONTEND_LINT_EXIT:0`
- `npm.cmd run build` -> `H6V1_FRONTEND_BUILD_EXIT:0`
- `npm.cmd run check:routes` -> `H6V1_FRONTEND_ROUTE_SMOKE_EXIT:0`

### Backend required smoke
- `pytest -q tests/test_execution_route_claim_guard_removal.py tests/test_claim_api_deprecation_lock.py tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py`
- Result: `24 passed`
- Exit marker: `H6V1_BACKEND_SMOKE_EXIT:0`

## Scope Guard Confirmation
- No backend runtime code change.
- No backend API shape change.
- No claim API/service/model/table/audit removal.
- No queue claim compatibility payload removal.
- No reopen compatibility/helper removal.
- No close/reopen behavior change.
- No migration added.

## Final Verdict
`P0_C_08H6_COMPLETE_VERIFICATION_CLEAN`

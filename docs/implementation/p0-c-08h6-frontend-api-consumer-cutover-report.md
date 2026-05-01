# P0-C-08H6 Frontend/API Consumer Cutover from Claim/Release Calls

Date: 2026-05-01
Scope: Single-slice frontend/API consumer cutover only.

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: SINGLE-SLICE IMPLEMENTATION
- Hard Mode MOM: v3
- Reason: Station Execution UI touched execution ownership semantics and command affordance gating, so governed MOM safety gate is required before code changes.

## Hard Mode MOM v3 Gate

### Design Evidence Extract
- `docs/implementation/p0-c-08h5-claim-retirement-sequencing-contract.md` defines H6 as consumer cutover first, with claim compatibility preserved.
- `docs/implementation/p0-c-08h2-frontend-queue-consumer-cutover-report.md` sets ownership-first queue consumption baseline and keeps claim fallback compatibility.
- `docs/implementation/p0-c-08f-claim-api-deprecation-lock-report.md` requires claim APIs remain callable/deprecated and not removed in this slice.
- `docs/design/02_domain/execution/station-session-ownership-contract.md` establishes StationSession as target ownership truth.
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md` confirms command authorization remains backend-owned.
- `docs/design/00_platform/product-business-truth-overview.md` confirms frontend must not be authorization or execution truth.

### Event Map
| Area | Event Impact | Change |
|---|---|---|
| StationExecution claim/release UI actions | No domain event introduced | No |
| Execution command API calls (start/pause/resume/report/downtime/complete) | Existing events only when backend accepts command | No |
| Claim compatibility APIs | Still active/deprecated; not called from StationExecution primary flow | No |

### Invariant Map
| Invariant | Enforcement | H6 Result |
|---|---|---|
| Backend is source of execution truth | Backend command handlers + StationSession guards | Preserved |
| Frontend does not authorize execution | `allowed_actions` + backend response handling | Preserved |
| Claim compatibility surfaces remain | Backend unchanged | Preserved |
| No backend/API shape mutation in H6 | Frontend-only edit scope | Preserved |

### State Transition Map
| UI State | Before H6 | After H6 |
|---|---|---|
| Mode A claim/release controls | Present and API-calling | Removed |
| Mode B execution gating | Mixed claim/session | Ownership/session-capable `canExecute` gate |
| Header release action | Called claim release API | Removed |

### Test Matrix
| Test ID | Verification | Result |
|---|---|---|
| H6-FE-1 | `npm.cmd run lint` | PASS (`H6_FRONTEND_LINT_EXIT:0`) |
| H6-FE-2 | `npm.cmd run build` | PASS (`H6_FRONTEND_BUILD_EXIT:0`) |
| H6-FE-3 | `npm.cmd run check:routes` | PASS (`H6_FRONTEND_ROUTE_SMOKE_EXIT:0`) |
| H6-BE-1 | `pytest -q tests/test_claim_api_deprecation_lock.py tests/test_station_queue_session_aware_migration.py tests/test_station_session_command_guard_enforcement.py` | PASS (`29 passed`, `H6_BACKEND_SMOKE_EXIT:0`) |

### Verdict before coding
`ALLOW_IMPLEMENTATION`

## Current Source Evidence

| Consumer Surface | Pre-H6 State | H6 Action | Risk |
|---|---|---|---|
| `frontend/src/app/pages/StationExecution.tsx` claim path | Direct calls to `stationApi.claim()` and `stationApi.release()` | Removed both call paths and related UI actions | Medium |
| Mode A claim CTA | Claim-acquire panel shown and API-triggered | Removed; selection remains queue-driven | Medium |
| Mode B header release CTA | Release button exposed command path | Removed from header and parent wiring | Medium |
| Action affordance gate | Mixed logic with `canExecuteByClaim` dependency | Unified to `canExecute` for ownership/session-capable behavior | High (fixed) |
| Claim compatibility typing | Present in station API client | Retained unchanged (compatibility-only) | Low |

## Files Changed
- `frontend/src/app/pages/StationExecution.tsx`
- `frontend/src/app/components/station-execution/StationExecutionHeader.tsx`
- `frontend/src/app/components/station-execution/AllowedActionZone.tsx`

## Behavior Contract After H6
- StationExecution no longer invokes claim/release APIs.
- Queue/ownership consumption remains ownership-first with claim fallback compatibility.
- Execution commands remain unchanged and backend-authoritative.
- Claim API routes, service, and data model remain untouched.

## Scope Guard Confirmation
- No backend code change.
- No migration/schema change.
- No claim API deletion.
- No queue payload shape change.
- No close/reopen policy change.

## Final Verdict
`P0-C-08H6_COMPLETE_VERIFICATION_CLEAN`

## H6-V1 Recovery Addendum (2026-05-01)

Gap found after H6 implementation audit:

- `frontend/src/app/pages/StationExecution.tsx` still had claim-derived enablement:
	- `const canExecute = canExecuteByOwnership || claimState === "mine";`

H6-V1 correction:

- Removed claim-derived execution affordance from `StationExecution.tsx`.
- Final gate is now ownership/session-only:
	- `const canExecute = canExecuteByOwnership;`
- Removed now-unused `claimState` local in `StationExecution.tsx`.

Post-fix checks:

- `claimState === "mine"` in `StationExecution.tsx`: none.
- `canExecuteByOwnership ||` in `StationExecution.tsx`: none.
- `stationApi.claim` and `stationApi.release` usage in `StationExecution.tsx` and `station-execution` components: none.

H6-V1 verification:

- `npm.cmd run lint` -> `H6V1_FRONTEND_LINT_EXIT:0`
- `npm.cmd run build` -> `H6V1_FRONTEND_BUILD_EXIT:0`
- `npm.cmd run check:routes` -> `H6V1_FRONTEND_ROUTE_SMOKE_EXIT:0`
- `pytest -q tests/test_execution_route_claim_guard_removal.py tests/test_claim_api_deprecation_lock.py tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py` -> `24 passed`, `H6V1_BACKEND_SMOKE_EXIT:0`

H6-V1 scope guard confirmation:

- No backend runtime code changed.
- No backend API shape changed.
- No claim API/service/model/table/audit removal.
- No queue compatibility payload removal.
- No reopen continuity helper removal.
- No close/reopen behavior change.
- No migration.

H6-V1 verdict:

`P0_C_08H6_COMPLETE_VERIFICATION_CLEAN`

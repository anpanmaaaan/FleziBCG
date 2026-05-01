# P0-C-08F Claim API Deprecation Lock Report

## Routing
- Selected brain: docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- Selected mode: SINGLE-SLICE IMPLEMENTATION
- Hard Mode MOM: docs/ai-skills/hard-mode-mom-v3/SKILL.md
- Reason: lock claim APIs as compatibility-only deprecation surface while preserving StationSession ownership direction and runtime compatibility.

# Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
- Design and source evidence are explicit that claim remains compatibility debt in this phase.
- Route-level deprecation headers on claim-only endpoints are safe, additive, and non-breaking.
- No schema/event/state-machine changes are required for 08F scope.

## Design Evidence Extract

### Source docs read
| Doc | Why used |
|---|---|
| docs/design/02_domain/execution/station-session-ownership-contract.md | Establishes StationSession as target ownership and claim as compatibility debt |
| docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md | Confirms 08C seven-command StationSession guard and claim compatibility boundary |
| docs/design/02_registry/station-session-event-registry.md | Confirms StationSession lifecycle event baseline unchanged |
| docs/design/00_platform/canonical-error-code-registry.md | Confirms 08C guard error semantics baseline |
| docs/design/00_platform/canonical-error-codes.md | Confirms approved StationSession guard HTTP mappings |
| docs/implementation/p0-c-08c-station-session-command-guard-enforcement-report.md | Confirms 08C scope and deferred items |
| docs/implementation/p0-c-08d-station-queue-session-aware-migration-report.md | Confirms queue is session-aware additively and claim payload retained |
| docs/implementation/p0-c-08e-reopen-resume-continuity-replacement-report.md | Confirms reopen/resume continuity boundaries and compatibility path |
| docs/implementation/p0-c-08e-v2-db-fixture-deadlock-stabilization-report.md | Confirms stable baseline before 08F |
| docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md | Defines non-negotiable claim compatibility lock |
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | Confirms target execution ownership/session requirements and closure boundaries |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | Confirms claim deprecation from target model |
| docs/design/02_domain/execution/station-execution-policy-and-master-data-v4.md | Confirms start does not require claim in target semantics |
| docs/design/02_domain/execution/execution-state-machine.md | Confirms no state-machine mutation allowed in this slice |

### Required design conclusions
- StationSession is target ownership truth.
- Claim remains compatibility/migration debt.
- 08C command guard enforcement active for seven commands.
- 08D queue already session-aware additively.
- 08E reopen/resume continuity replacement is complete.
- Claim API still active.
- Claim removal is not approved in this slice.

## Current Source Evidence

| Source Area | File | Current Claim Role | Deprecation Impact |
|---|---|---|---|
| Claim routes and queue routes | backend/app/api/v1/station.py | Exposes claim/release/status APIs and queue/detail endpoints | Claim-only routes can be marked deprecated via headers; queue/detail must remain non-deprecated |
| Execution command routes | backend/app/api/v1/operations.py | Uses ensure_operation_claim_owned_by_identity as compatibility guard on enforced commands | No header changes applied here to avoid broad endpoint deprecation semantics |
| Claim service | backend/app/services/station_claim_service.py | Provides claim acquisition/release/status and queue claim compatibility payload | Behavior unchanged; compatibility surface retained |
| Reopen continuity helper | backend/app/services/operation_service.py | _restore_claim_continuity_for_reopen compatibility behavior | Unchanged in 08F |
| Claim ORM models | backend/app/models/station_claim.py | OperationClaim and OperationClaimAuditLog persistence/audit | Unchanged in 08F |
| Queue schema | backend/app/schemas/station.py | claim + ownership additive payload shape | Unchanged schema; queue remains non-deprecated |
| Claim lock tests | backend/tests/test_claim_single_active_per_operator.py | Locks single-active claim behavior | Must remain green |
| Claim release tests | backend/tests/test_release_claim_active_states.py | Locks release behavior and restrictions | Must remain green |
| Queue compatibility tests | backend/tests/test_station_queue_active_states.py | Locks queue claim compatibility behavior | Must remain green |
| Reopen continuity tests | backend/tests/test_reopen_resumability_claim_continuity.py | Locks claim continuity compatibility path | Must remain green |
| Close/reopen foundation tests | backend/tests/test_close_reopen_operation_foundation.py | Locks close/reopen baseline | Must remain green |
| StationSession guard tests | backend/tests/test_station_session_command_guard_enforcement.py | Locks target guard ownership behavior | Must remain green |

## Claim API Inventory

| API / Route | Current Purpose | Runtime Critical? | Target Replacement | 08F Action |
|---|---|---:|---|---|
| POST /api/v1/station/queue/{operation_id}/claim | Acquire operation claim | YES | StationSession ownership flow | MARK_DEPRECATED_COMPATIBILITY |
| POST /api/v1/station/queue/{operation_id}/release | Release operation claim | YES | StationSession ownership flow | MARK_DEPRECATED_COMPATIBILITY |
| GET /api/v1/station/queue/{operation_id}/claim | Read claim status | YES | StationSession ownership/status view | MARK_DEPRECATED_COMPATIBILITY |
| GET /api/v1/station/queue | Read queue with claim compatibility and session ownership block | YES | Session-aware queue (already active) | LEAVE_UNCHANGED_WITH_DOC_NOTE |
| Route uses of ensure_operation_claim_owned_by_identity in operations endpoints | Transitional compatibility guard on execution writes | YES | Pure StationSession guard-only path in later slice | KEEP_INTERNAL_COMPATIBILITY_ONLY |

## Deprecation Model

Selected model: Option A (claim-only endpoint deprecation headers) + Option C behavior for queue endpoint.

Headers added to claim-only endpoints:
- Deprecation: true
- X-FleziBCG-Deprecation-Status: compatibility-only
- X-FleziBCG-Replacement: StationSession

Why this model:
- Additive, response-shape-safe, and client-nonbreaking.
- Precisely marks only legacy claim APIs.
- Avoids incorrectly deprecating the station queue endpoint, which remains valid and includes active session ownership context.

## Claim Compatibility Boundary

| Claim Function | 08F Status | Reason | Future Removal Slice |
|---|---|---|---|
| claim_operation | Deprecated API surface, behavior retained | Existing clients and compatibility workflows depend on it | P0-C-08H |
| release_operation_claim | Deprecated API surface, behavior retained | Existing release semantics retained during migration window | P0-C-08H |
| ensure_operation_claim_owned_by_identity | Internal compatibility guard retained | 08C/08E transition boundary still active | P0-C-08G/H |
| get_operation_claim_status | Deprecated API surface, behavior retained | Status endpoint still used by compatibility clients | P0-C-08H |
| get_station_queue | Non-deprecated endpoint with compatibility claim block retained | Queue remains active with additive session ownership | P0-C-08H |
| _restore_claim_continuity_for_reopen | Compatibility-only helper retained | Reopen continuity boundary preserved from 08E | P0-C-08G/H |

## Event Map

| Area | Event Impact | Change? |
|---|---|---:|
| Claim API deprecation headers | No event changes | No |
| Claim audit behavior | Existing claim audit events remain when claim APIs are used | No |
| StationSession lifecycle events | Unchanged | No |
| Execution command events | Unchanged | No |

## Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| StationSession is target ownership truth | session | design + service contract | no | yes | station-session-ownership-contract |
| Claim API is deprecated compatibility surface only | migration_boundary | route headers + docs | no | yes | p0-c-04 lock + 08F tests |
| Claim cannot override StationSession guard | authorization | operations route/service chain | no | yes | 08C contract/tests |
| Command guard behavior unchanged | state_machine | existing command services/routes | no | yes | command hardening tests |
| Queue session-aware output unchanged | projection_consistency | queue service/schema | no | yes | 08D queue tests |
| Reopen/resume behavior unchanged | state_machine | operation_service | no | yes | 08E tests |
| Close behavior unchanged | state_machine | operation_service | no | yes | close tests |
| Claim audit/history retained | auditability | claim service/models | no | yes | claim regression tests |
| Frontend cannot infer target truth from claim | integration_boundary | backend-owned semantics + deprecation marker | no | yes | API tests/docs |
| Tenant isolation preserved | tenant | existing authz + service checks | no | yes | existing regressions |

## State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Claim API surface | active compatibility routes | add deprecation headers | yes | none_required | same runtime behavior | test_claim_api_deprecation_lock | 08F scope |
| Station queue endpoint | active queue route | no deprecation header | yes | none_required | unchanged queue contract | test_claim_api_deprecation_lock | 08D/08F boundary |
| Execution command guards | existing 08C state | no behavior change | yes | unchanged command events | unchanged | command hardening regressions | 08C contract |

## Behavior Contract (08F)
- Claim endpoints remain callable.
- Claim/service/model/audit are retained.
- Claim endpoints are explicitly marked compatibility-only deprecated.
- No command success/failure behavior changes.
- No StationSession guard behavior changes.
- No queue contract change (except documentation/deprecation interpretation).
- No schema migration.
- No event rename/new domain event.

## Implementation Summary
- Updated backend/app/api/v1/station.py
  - Added add_claim_api_deprecation_headers(response)
  - Applied headers to:
    - POST /station/queue/{operation_id}/claim
    - POST /station/queue/{operation_id}/release
    - GET /station/queue/{operation_id}/claim
- Added test suite: backend/tests/test_claim_api_deprecation_lock.py
  - Verifies claim endpoint deprecation headers
  - Verifies queue endpoint remains non-deprecated and still exposes claim compatibility context
  - Verifies StationSession endpoint remains non-deprecated

## Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| 08F-T1 | Claim endpoint has deprecation headers | regression | authenticated identity + mocked claim service | POST claim | 200 + required deprecation headers | none_required | claim deprecated compatibility-only |
| 08F-T2 | Release endpoint has deprecation headers | regression | authenticated identity + mocked release service | POST release | 200 + required deprecation headers | none_required | claim deprecated compatibility-only |
| 08F-T3 | Claim status endpoint has deprecation headers | regression | authenticated identity + mocked status service | GET claim status | 200 + required deprecation headers | none_required | claim deprecated compatibility-only |
| 08F-T4 | Queue endpoint is not globally deprecated | regression | authenticated identity + mocked queue service | GET queue | 200 + no deprecation headers | none_required | queue remains active while claim block retained |
| 08F-T5 | StationSession endpoint is not deprecated | regression | authenticated identity + mocked session service | GET station session current | 200 + no deprecation headers | none_required | StationSession is target, not deprecated |

## Verification Runs
1. Focused 08F tests:
- `pytest -q tests/test_claim_api_deprecation_lock.py`
- Result: `5 passed`
- Exit: `T08F_EXIT:0`

2. Claim regression:
- `pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py`
- Result: `28 passed`
- Exit: `T_CLAIM_REG_EXIT:0`

3. StationSession / 08C guard regression:
- `pytest -q tests/test_station_session_command_guard_enforcement.py tests/test_station_session_lifecycle.py tests/test_station_session_diagnostic_bridge.py tests/test_station_session_command_context_diagnostic.py`
- Result: `47 passed`
- Exit: `T_08C_REG_EXIT:0`

4. 08D / 08E regression:
- `pytest -q tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py tests/test_reopen_resumability_claim_continuity.py tests/test_reopen_operation_claim_continuity_hardening.py tests/test_close_reopen_operation_foundation.py`
- Result: `28 passed`
- Exit: `T_08D08E_REG_EXIT:0`

5. Command hardening regression:
- `pytest -q tests/test_start_pause_resume_command_hardening.py tests/test_report_quantity_command_hardening.py tests/test_downtime_command_hardening.py tests/test_complete_operation_command_hardening.py tests/test_close_operation_command_hardening.py`
- Result: `58 passed`
- Exit: `T_CMD_HARDEN_REG_EXIT:0`

6. Full backend suite (sequential):
- `pytest -q`
- Result: `289 passed, 1 skipped in 52.11s`
- Exit: `T_FULL_EXIT:0`

## Scope Guard Confirmation
- No claim removal.
- No claim table/code removal.
- No claim route removal.
- No schema migration.
- No close/reopen StationSession enforcement expansion.
- No queue rewrite.
- No command behavior change.
- No FE/UI changes.

## Final Verdict
ALLOW_IMPLEMENTATION_COMPLETE

P0-C-08F status: IMPLEMENTATION_COMPLETE_VERIFICATION_CLEAN

## Next Slice Recommendation
P0-C-08G Claim Table / Code Removal Readiness Check (readiness audit only; no removal yet).

# Autonomous Implementation Plan

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: NON-STOP SLICE EXECUTION
- Hard Mode MOM: v3 for governed foundation and execution-adjacent slices
- Reason: Continue vertical-slice implementation in phase order with backend-authoritative behavior and per-slice verification.

## Phase Status

### P0-A Foundation Database Slice

Status: Complete except deferred ADR work.

Completed slices:
- Runtime config hardening
- Alembic foundation
- Remove production create_all path
- Tenant foundation
- IAM user lifecycle baseline
- Session / refresh token transitional foundation
- Role / action / scope foundation
- Plant hierarchy foundation
- Audit / security event foundation
- Governed audit/security-event emission wiring for auth and admin mutations
- Backend CI minimum baseline
- Backend CI/test hardening: explicit backend import check + workflow config regression test
- Backend CI governance hardening: required Hard Mode v3 report artifacts enforced in workflow
- Audit/security event foundation hardening: admin read-only security-events endpoint

Deferred / blocked inside P0-A:
- Advanced refresh-token rotation / reuse detection policy
  - Status: DEFERRED / NEEDS ADR
  - Reason: User explicitly deferred advanced rotation policy; current refresh endpoint remains transitional baseline.

### P0-B Manufacturing Master Data Minimum

Status: In progress with Product Foundation, Routing Foundation, and Resource Requirement Mapping completed.

Completed slices:
- Reason/reference data foundation baseline via governed downtime-reason admin management
- Product foundation backend slice (P0-B-01) implemented from approved executable contract
- Routing foundation backend slice (P0-B-02) implemented with tenant-scoped routing lifecycle and operation-sequence governance
- Resource Requirement Mapping backend slice (P0-B-03) implemented with tenant-scoped operation linkage, lifecycle-governed mutation, and candidate domain events

Blocked / deferred slices:
1. Higher-scope manufacturing flows (outside P0-B minimum)
  - Status: DEFERRED
  - Reason: Explicitly out of scope for P0-B-03 (dispatch, execution queue, APS, BOM, Backflush, ERP integration).

### P0-C Station Execution Baseline

Status: In progress. Entry audit complete. Slices P0-C-01 through P0-C-07C complete.

Completed slices:
- P0-C-01 Work Order / Operation Foundation Alignment
  - Tests added for PENDING/LATE status in _derive_allowed_actions projection contract
  - Tests added for tenant isolation at service layer (start, close, report_quantity)
  - Tests added for WO→PO→Operation hierarchy read consistency
  - Design gap documented: ProductionOrder.route_id has no FK to Routing.routing_id
  - Backend suite: 148 passed, 1 skipped, exit 0
- P0-C-02 Execution State Machine Guard Alignment
  - Bug fixed: `_derive_status` dead-code for OP_COMPLETED/OP_ABORTED causing wrong status in reopen→resume→complete sequence
  - Added `last_runtime_event = event.event_type` to OP_COMPLETED and OP_ABORTED elif branches
  - Removed dead code: OP_COMPLETED and OP_ABORTED from final elif in `_derive_status`
  - 7 new pure-unit regression tests added to test_operation_detail_allowed_actions.py
  - Projection consistency between `_derive_status` (single-op) and bulk reconciler now guaranteed
  - Backend suite: 153 passed, 1 skipped, exit 0
- P0-C-03 Execution Event Log / Projection Consistency
  - Added detail-vs-bulk projection parity tests for core event sequences (reopen/resume/complete, aborted, downtime open, downtime ended)
  - Added reconcile-command parity regression test ensuring post-apply detail and bulk projection alignment
  - Hardened event repository ordering for operation detail projection: `created_at, id` deterministic ordering
  - No event contract change, no command expansion, no schema migration, no claim/session migration
  - Backend suite: 159 passed, 1 skipped, exit 0
- P0-C-04A Station Session Ownership Contract (DOC-ONLY)
- P0-C-04B StationSession Model + Lifecycle Foundation
  - StationSession ORM model, SQL migration 0017, repository, service, API routes
  - 9 lifecycle tests (test-first), all passing
  - Station session event registry (v1.1 CANONICAL)
  - Backend suite: 168 passed, 1 skipped, exit 0
- P0-C-04B Hardening: Event registry canonicalization
  - `_CANDIDATE_EVENT_STATUS` renamed to `_CANONICAL_EVENT_STATUS`
  - All 4 station session events at `CANONICAL_FOR_P0_C_STATION_SESSION`
- P0-C-04C Diagnostic Session Context Bridge
  - Pure read-only `get_station_session_diagnostic()` helper; `StationSessionDiagnostic` + `SessionReadiness` enum
  - Non-blocking: missing session is a diagnostic signal only, not a command rejection
  - 7 test-first tests (BRIDGE-T1 through BRIDGE-T7 class), all passing
  - Backend suite: 175 passed, 1 skipped, exit 0
- P0-C-04D Command Context Diagnostic Integration / Guard Readiness
  - `_compute_session_diagnostic()` private helper wired into all 9 execution commands after tenant check
  - Diagnostic result stored as local `_session_ctx` — informational only, never used for rejection
  - 9 test-first tests in test_station_session_command_context_diagnostic.py, all passing
  - API response shape (OperationDetail) unchanged
  - Backend suite: 184 passed, 1 skipped, exit 0
- P0-C-05 Start / Pause / Resume Command Hardening
  - New focused hardening suite: `backend/tests/test_start_pause_resume_command_hardening.py` (12 tests)
  - Guard legality verified for PLANNED/IN_PROGRESS/PAUSED and CLOSED-record rejection
  - Event emission verified: `OP_STARTED`, `execution_paused`, `execution_resumed`
  - Projection and `allowed_actions` verified after start/pause/resume transitions
  - StationSession diagnostic non-blocking behavior re-verified (session and no-session paths)
  - Backend suite: 196 passed, 1 skipped, exit 0
- P0-C-06A Production Reporting Command Hardening
  - New focused hardening suite: `backend/tests/test_report_quantity_command_hardening.py` (12 tests)
  - State guard, quantity invariants, closed-record rejection, event emission verified
  - Projection accumulation across multiple `QTY_REPORTED` events verified
  - `allowed_actions` after report verified: `["report_production", "pause_execution", "complete_execution", "start_downtime"]`
  - StationSession diagnostic non-blocking behavior re-verified (no-session and open-session paths)
  - Backend suite: 208 passed, 1 skipped, exit 0
- P0-C-06B Downtime Start / End Command Hardening
  - New focused hardening suite: `backend/tests/test_downtime_command_hardening.py` (14 tests)
  - State guards verified: `start_downtime` from IN_PROGRESS/PAUSED only; PLANNED rejected
  - Duplicate open downtime rejection (DOWNTIME_ALREADY_OPEN) verified via event-count guard
  - Invalid/inactive reason code rejection verified
  - Closed-record rejection verified for both commands
  - Event emission verified: `downtime_started`, `downtime_ended`
  - IN_PROGRESS→BLOCKED transition after `start_downtime` verified (event-derived projection)
  - BLOCKED→PAUSED transition after `end_downtime` verified; no auto-resume confirmed
  - `resume_operation` blocked while downtime open (STATE_DOWNTIME_OPEN)
  - StationSession diagnostic non-blocking behavior re-verified
  - Backend suite: 222 passed, 1 skipped, exit 0
- P0-C-07A Complete Operation Command Hardening
  - New focused hardening suite: `backend/tests/test_complete_operation_command_hardening.py` (10 tests)
  - State legality verified for `complete_operation` from IN_PROGRESS and invalid-state rejection paths
  - Closed-record and tenant-mismatch rejection verified
  - Completion event emission verified: `OP_COMPLETED`
  - Projection and `allowed_actions` after complete verified (`status=completed`, `allowed_actions=["close_operation"]`)
  - StationSession diagnostic non-blocking behavior re-verified (no-session and matching OPEN-session parity)
  - Backend suite: 232 passed, 1 skipped, exit 0
- P0-C-07B Close Operation Guard Hardening
  - New focused hardening suite: `backend/tests/test_close_operation_command_hardening.py` (10 tests)
  - State legality verified for `close_operation` from completed states and invalid-state rejection paths
  - Already-closed and tenant-mismatch rejection verified
  - Close event emission verified: `operation_closed_at_station`
  - `closure_status` after close verified (`OPEN -> CLOSED`)
  - Projection/detail and `allowed_actions` after close verified (`["reopen_operation"]`)
  - StationSession diagnostic non-blocking behavior re-verified (no-session and matching OPEN-session parity)
  - Backend suite: 242 passed, 1 skipped, exit 0

Pending slices (in recommended order):
- P0-C-07C Reopen Operation / Claim Continuity Hardening (Complete)

### P0-C-08C Controlled Batch: StationSession Guard Enforcement

Status: Complete.

Completed scope:
- Canonical StationSession guard error registry finalized for the 08C subset.
- Service-layer StationSession command guard added for exactly seven commands:
  - `start_operation`
  - `pause_operation`
  - `resume_operation`
  - `report_quantity`
  - `start_downtime`
  - `end_downtime`
  - `complete_operation`
- Route-layer explicit `StationSessionGuardError` to HTTP translation added with compatibility-preserving claim guard retention.
- Repository lookup helpers added for latest station and operator session resolution.
- Focused guard-enforcement suite added and adjacent regression suites updated to the approved 08C contract.

Explicitly deferred from this controlled batch:
- `close_operation` and `reopen_operation` StationSession enforcement
- claim removal or continuity replacement
- queue migration or read-model redesign
- UI changes

Verification summary:
- Focused 08C slice: 70 passed
- Adjacent regression subset: 61 passed
- Full backend suite: 277 passed, 1 skipped

### P0-C-08H15B Claim Service / Schema Dead-Code Removal Implementation

Status: Complete.

Completed scope:
- Removed dead claim service functions/helpers from `backend/app/services/station_claim_service.py` while preserving queue/detail active paths.
- Removed dead route-only claim schemas (`ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse`) from `backend/app/schemas/station.py`.
- Deleted claim-service-only tests:
  - `backend/tests/test_claim_single_active_per_operator.py`
  - `backend/tests/test_release_claim_active_states.py`
- Updated `backend/tests/test_reopen_resumability_claim_continuity.py` to seed claim rows directly via ORM fixtures (no removed service API calls).

Explicitly deferred from H15B:
- Claim model deletion (`backend/app/models/station_claim.py`)
- DB init model registration changes
- Table-drop migration

Verification summary:
- Backend queue/session/reopen regression: 43 passed
- Backend projection/downtime regression: 46 passed
- Dead-code sweep for removed symbols: 0 matches
- Frontend lint/build/route smoke: all passed
- Implementation report: `docs/implementation/p0-c-08h15b-claim-service-schema-dead-code-removal-implementation-report.md`

### P0-C-08H16 Claim Model / Table Drop Migration Contract

Status: Complete (contract-only).

Completed scope:
- Produced migration-readiness contract after H15B service/schema cleanup.
- Built repo-wide dependency inventory for claim model/table references.
- Confirmed unresolved test/script dependencies block immediate model/table drop.
- Defined controlled split path: H16B dependency burn-down, then H17 migration implementation.

Contract artifact:
- `docs/implementation/p0-c-08h16-claim-model-table-drop-migration-contract.md`

Contract verdict:
- `READY_FOR_P0_C_08H16B_CLAIM_MODEL_TEST_DEPENDENCY_BURN_DOWN`

### P0-C-08H16B Claim Model/Test Dependency Burn-Down

Status: Complete.

Completed scope:
- Removed claim model/table dependencies from required H16B test files.
- Removed claim fixture inserts and claim teardown cleanup statements in targeted tests.
- Rewrote reopen/guard tests to StationSession-native assertions where claim fixtures were previously used.
- Preserved runtime boundaries: no migration, no table drop, no model deletion, no queue shape change.

Verification summary:
- Execution/queue/reopen subset: `42 passed` (`H16B_EXEC_QUEUE_REOPEN_EXIT:0`)
- Dependency burn-down subset: `51 passed` (`H16B_DEPENDENCY_BURN_DOWN_EXIT:0`)
- Claim dependency sweep: `H16B_CLAIM_DEPENDENCY_SWEEP_EXIT:0` (targeted tests clean)
- Frontend lint/build/route smoke: all exit 0

Implementation report:
- [docs/implementation/p0-c-08h16b-claim-model-test-dependency-burn-down-report.md](docs/implementation/p0-c-08h16b-claim-model-test-dependency-burn-down-report.md)

Verdict:
- `P0_C_08H16B_COMPLETE_WITH_MODEL_REFERENCES_DEFERRED`

## Current Slice Ledger

### Completed Slices

1. Governed audit/security-event emission wiring
   - Scope:
     - Session login/logout/logout-all/admin-revoke security-event emission
     - Refresh route security-event emission
     - Admin user lifecycle actor-aware security-event emission
     - Access assignment actor-aware security-event emission
   - Verification summary:
     - Targeted new slice tests passed
     - Backend import check passed
     - Foundation regression subset passed: 22 passed, 1 skipped

2. Reason/reference data foundation baseline
   - Scope:
     - Admin upsert route for downtime reasons
     - Admin deactivate route for downtime reasons
     - Tenant-scoped audit/security-event emission for downtime reason mutations
     - Existing active-only read catalog preserved
   - Changed backend surfaces:
     - app/api/v1/downtime_reasons.py
     - app/services/downtime_reason_service.py
     - app/repositories/downtime_reason_repository.py
     - app/schemas/downtime_reason.py
   - Verification summary:
     - Direct slice tests passed: 2 passed
     - Broader regression revalidated prior audit/governance slice: 22 passed, 1 skipped

3. P0-A backend CI/test hardening
   - Scope:
     - Added explicit backend import verification gate to PR workflow
     - Added deterministic workflow config regression test
     - Extended deterministic backend CI subset to include workflow and new endpoint tests
   - Changed surfaces:
     - .github/workflows/pr-gate.yml
     - backend/tests/test_pr_gate_workflow_config.py
   - Verification summary:
     - Test-first failure captured (missing import-check step)
     - Targeted slice test passed after patch: 2 passed

4. P0-A audit/security-event read visibility hardening
   - Scope:
     - Added admin-gated read-only endpoint for tenant-scoped security events
     - Added schema contract for security event API payload
   - Changed surfaces:
     - backend/app/api/v1/security_events.py
     - backend/app/schemas/security_event.py
     - backend/app/api/v1/router.py
     - backend/tests/test_security_events_endpoint.py
   - Verification summary:
     - Targeted endpoint tests passed: 2 passed
     - Focused governance regression subset passed: 18 passed
     - Backend import check passed

5. P0-A backend CI governance artifact enforcement
   - Scope:
     - Added PR gate enforcement for required Hard Mode v3 implementation artifacts
     - Added workflow regression assertion for required report checks
   - Changed surfaces:
     - .github/workflows/pr-gate.yml
     - backend/tests/test_pr_gate_workflow_config.py
   - Verification summary:
     - Test-first failure captured (missing report checks)
     - Targeted workflow config tests passed after patch: 3 passed
     - Focused regression subset passed: 5 passed

6. P0-B-01 Product Foundation backend implementation
   - Scope:
     - Product model/table with tenant-scoped unique code invariant
     - Product schemas, repository, service, and API routes
     - Lifecycle transitions DRAFT/RELEASED/RETIRED with transition guards
     - Tenant isolation and cross-tenant detail 404 behavior
     - Security-event emission for governed product mutations
   - Changed backend surfaces:
     - backend/app/models/product.py
     - backend/app/schemas/product.py
     - backend/app/repositories/product_repository.py
     - backend/app/services/product_service.py
     - backend/app/api/v1/products.py
     - backend/app/api/v1/router.py
     - backend/app/db/init_db.py
     - backend/scripts/migrations/0014_products.sql
     - backend/tests/test_product_foundation_service.py
     - backend/tests/test_product_foundation_api.py
   - Verification summary:
     - Backend import check passed
     - Focused product tests passed: 8 passed
     - Requested regression subset passed: 8 passed

  ### P0-C-08F Claim API Deprecation Lock

  Status: Complete.

  Completed scope:
  - Claim API surface inventory and compatibility boundary lock finalized.
  - Added compatibility-only deprecation headers on claim-only routes:
    - `POST /api/v1/station/queue/{operation_id}/claim`
    - `POST /api/v1/station/queue/{operation_id}/release`
    - `GET /api/v1/station/queue/{operation_id}/claim`
  - Kept station queue endpoint non-deprecated and behavior unchanged.
  - Kept StationSession endpoints non-deprecated.
  - Added focused deprecation lock tests: `backend/tests/test_claim_api_deprecation_lock.py`.

  Explicitly out of scope and preserved:
  - claim removal/table removal/code removal
  - command guard behavior changes
  - close/reopen StationSession enforcement expansion
  - queue rewrite
  - schema migration
  - FE/UI changes

  Verification summary:
  - Focused 08F tests: `5 passed` (`T08F_EXIT:0`)
  - Claim regression subset: `28 passed` (`T_CLAIM_REG_EXIT:0`)
  - StationSession/08C guard regression: `47 passed` (`T_08C_REG_EXIT:0`)
  - 08D/08E regression: `28 passed` (`T_08D08E_REG_EXIT:0`)
  - Command hardening regression: `58 passed` (`T_CMD_HARDEN_REG_EXIT:0`)
  - Full backend suite: `289 passed, 1 skipped` (`T_FULL_EXIT:0`)

  Verdict:
  - `ALLOW_IMPLEMENTATION_COMPLETE`
  - P0-C-08F complete and clean.

7. P0-B-02 Routing Foundation backend implementation
   - Scope:
     - Routing aggregate and routing operation sequence models
     - Routing schemas, repository, service, and API routes
     - Lifecycle transitions DRAFT/RELEASED/RETIRED with RELEASED structural immutability
     - Tenant isolation and cross-tenant routing detail 404 behavior
     - Product-linkage invariants including retired-product new-link rejection
     - Security-event emission using candidate routing event names pending registry finalization
   - Changed backend surfaces:
     - backend/app/models/routing.py
     - backend/app/schemas/routing.py
     - backend/app/repositories/routing_repository.py
     - backend/app/services/routing_service.py
     - backend/app/api/v1/routings.py
     - backend/app/api/v1/router.py
     - backend/app/db/init_db.py
     - backend/tests/test_routing_foundation_service.py
     - backend/tests/test_routing_foundation_api.py
   - Verification summary:
     - Backend import check passed
     - Focused routing tests passed: 8 passed
     - Product + execution regression subset passed: 18 passed
     - Full backend suite passed: 134 passed, 1 skipped

8. P0-B-03 Resource Requirement Mapping backend implementation
   - Scope:
     - Resource requirement model/table linked to routing and routing operation
     - Resource requirement schemas, repository, service, and nested routing-operation API routes
     - Tenant isolation and same-tenant routing/operation linkage validation
     - Parent routing lifecycle guards (DRAFT-only mutation)
  - Canonical domain-event naming for requirement create/update/remove
   - Changed backend surfaces:
     - backend/app/models/resource_requirement.py
     - backend/app/schemas/resource_requirement.py
     - backend/app/repositories/resource_requirement_repository.py
     - backend/app/services/resource_requirement_service.py
     - backend/app/api/v1/routings.py
     - backend/app/db/init_db.py
     - backend/scripts/migrations/0016_resource_requirements.sql
     - backend/tests/test_resource_requirement_service.py
     - backend/tests/test_resource_requirement_api.py
   - Verification summary:
     - Backend import check passed
     - Focused P0-B-03 tests passed: 7 passed
     - Requested product+routing regression subset passed: 16 passed
     - Full backend suite passed: 141 passed, 1 skipped

### Next Slice Selection

Name: STOP_AFTER_P0_B_01 (explicit user instruction)

Entry hypothesis:
- P0-B-01 is complete and verified against the approved product foundation contract.
- Product event names are canonical for P0-B and tracked as `CANONICAL_FOR_P0_B`.

Stop conditions before implementation:
- STOP triggered by user request to stop after this slice

### 15. P0-C-04B StationSession Model + Lifecycle Foundation

Status: Complete.

Scope implemented:
- StationSession persistence model and SQL migration foundation
- StationSession schemas, repository, service, and API routes under `/station/sessions`
- Candidate station-session lifecycle events emitted through transitional security-event infrastructure
- Lifecycle tests added (test-first) and executed

Non-scope preserved:
- No claim removal/refactor
- No execution command behavior change
- No dual-mode queue
- No FE/UI changes

Files introduced for this slice:
- backend/app/models/station_session.py
- backend/app/schemas/station_session.py
- backend/app/repositories/station_session_repository.py
- backend/app/services/station_session_service.py
- backend/app/api/v1/station_sessions.py
- backend/scripts/migrations/0017_station_sessions.sql
- backend/tests/test_station_session_lifecycle.py
- docs/design/02_registry/station-session-event-registry.md

Verification target for this slice:
- Focused lifecycle tests
- Claim regression subset
- Full backend suite

### 16. P0-C-04C Diagnostic Session Context Bridge

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:
- `station_session_diagnostic.py` — pure read-only service helper returning `StationSessionDiagnostic`
- `SessionReadiness` enum: `OPEN` / `NO_ACTIVE_SESSION`
- 7 test-first tests covering: detection of open session, detection of missing session, ignoring closed session, tenant isolation (no false positive), command-unchanged with no session (BRIDGE-T1), command-unchanged with open session (BRIDGE-T2), operator context when identified
- Behavior contract: missing session is a diagnostic signal only — not a command rejection

Non-scope preserved:
- No claim removal/refactor
- No execution command behavior change (`start_operation` / any command guard unchanged)
- No new domain events
- No schema migration
- No FE/UI changes

Files introduced for this slice:
- backend/app/services/station_session_diagnostic.py
- backend/tests/test_station_session_diagnostic_bridge.py

Verification summary:
- Diagnostic bridge tests: 7 passed
- Station session lifecycle regression: 9 passed
- Claim regression subset: 45 passed
- Full backend suite: 175 passed, 1 skipped, exit 0

### 17. P0-C-04D Command Context Diagnostic Integration / Guard Readiness
### 18. P0-C-04E Claim Compatibility / Deprecation Lock

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:
- Compatibility lock document: `docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md`
- 8 non-negotiable compatibility boundary invariants codified
- Claim source map documented (8 guard call-sites via `ensure_operation_claim_owned_by_identity`)
- Diagnostic bridge non-interference contract documented
- Test compatibility lock: 45 claim tests + 16 session/diagnostic bridge tests + 9 command context tests
- Migration debt register and next-slice pre-conditions documented

Non-scope preserved:
- No claim model/service/test changes
- No execution command behavior change
- No API response change
- No schema migration
- No new domain events
- No FE/UI changes

Files introduced:
- docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md

Verification summary:
- Claim suite (isolation run): 36 passed, exit 0
- Full backend suite: 184 passed, 1 skipped, exit 0

---

### 17. P0-C-04D Command Context Diagnostic Integration / Guard Readiness

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:
- `_compute_session_diagnostic(db, operation, tenant_id)` private helper in `operation_service.py`
- Wired into all 9 execution commands: start_operation, report_quantity, complete_operation, pause_operation, resume_operation, start_downtime, end_downtime, close_operation, reopen_operation
- Each command calls helper AFTER the tenant_id guard, BEFORE existing state machine guards
- Result stored as local `_session_ctx` — informational only, never used for rejection or any conditional
- Integration point is now in place for P0-C-04E hard enforcement

Non-scope preserved:
- No command rejection behavior change
- No API response change (OperationDetail schema unchanged)
- No claim removal/refactor
- No new domain events
- No schema migration
- No FE/UI changes

Files changed for this slice:
- backend/app/services/operation_service.py (import + helper + 9 invocations)

Files introduced for this slice:
- backend/tests/test_station_session_command_context_diagnostic.py

Verification summary:
- Command context diagnostic tests: 9 passed
- Diagnostic bridge tests: 7 passed (unchanged)
- Session lifecycle + claim regression subset: 86 passed
- Full backend suite: 184 passed, 1 skipped, exit 0

### 19. P0-C-05 Start / Pause / Resume Command Hardening

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:
- Focused start/pause/resume hardening suite added: `backend/tests/test_start_pause_resume_command_hardening.py`
- 12 tests added to verify legal transitions, illegal transitions, closed-record rejection, event emission, projection status, and allowed-actions derivation
- StationSession non-blocking contract re-verified for start/pause/resume with and without OPEN session
- Claim compatibility regression re-verified unchanged

Non-scope preserved:
- No StationSession hard enforcement
- No claim removal or claim behavior change
- No event name changes
- No schema migration
- No FE/UI changes

Files introduced for this slice:
- backend/tests/test_start_pause_resume_command_hardening.py

Production code changes:
- none (tests-only hardening slice)

Verification summary:
- P0-C-05 focused tests: 12 passed
- Station session lifecycle/diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 196 passed, 1 skipped, exit 0

### 20. P0-C-06A Production Reporting Command Hardening

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:
- Focused `report_quantity` hardening suite added: `backend/tests/test_report_quantity_command_hardening.py`
- 12 tests added to verify: happy path (good-qty-only, mixed qty), state guards (PLANNED reject, PAUSED reject), closed-record rejection, negative qty rejection, zero-sum rejection, cumulative projection across two reports, allowed-actions after report, no-session parity, open-session parity
- `QTY_REPORTED` event emission verified
- Projection accumulation across multiple `QTY_REPORTED` events verified (good_qty and scrap_qty cumulate)
- StationSession diagnostic non-blocking contract re-verified for report_quantity
- Claim compatibility regression re-verified unchanged

Non-scope preserved:
- No StationSession hard enforcement
- No claim removal or claim behavior change
- No event name changes
- No schema migration
- No downtime command hardening
- No complete/close/reopen hardening
- No FE/UI changes

Files introduced for this slice:
- backend/tests/test_report_quantity_command_hardening.py

Production code changes:
- none (tests-only hardening slice)

Verification summary:
- P0-C-06A focused tests: 12 passed
- P0-C-05 regression: 12 passed
- Station session lifecycle/diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 208 passed, 1 skipped, exit 0

### 21. P0-C-06B Downtime Start / End Command Hardening

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:

### P0-C-08D Station Queue Session-Aware Migration

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION_COMPLETE

Scope implemented:
- Additive queue payload migration in backend read model only.
- Added `ownership` object on each station queue item with session-aware ownership metadata:
  - `target_owner_type=station_session`
  - `ownership_migration_status=TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT`
  - `session_id`, `station_id`, `session_status`, `operator_user_id`, `owner_state`, `has_open_session`
- Existing `claim` payload shape and claim behavior preserved as compatibility contract.
- No execution command-path behavior changes.

Files changed:
- `backend/app/services/station_claim_service.py`
- `backend/app/schemas/station.py`
- `backend/tests/test_station_queue_active_states.py`
- `backend/tests/test_station_queue_session_aware_migration.py`

Verification summary:
- Focused queue migration regression:
  - `test_station_queue_session_aware_migration.py` + `test_station_queue_active_states.py`
  - Result: `10 passed`, `exit 0`
- Command hardening regression batch:
  - Result: `70 passed`, `exit 0`
- StationSession/claim/queue/reopen regression batch:
  - Result: `63 passed`, `exit 0`
- Full backend suite:
  - Result: `279 passed, 1 skipped`, `exit 0`

Scope guard confirmation:
- No claim removal or claim endpoint deprecation.
- No close/reopen StationSession guard expansion.
- No new domain events.
- No schema migration.
- No FE/UI changes.
- Focused `start_downtime`/`end_downtime` hardening suite added: `backend/tests/test_downtime_command_hardening.py`
- 14 tests added to verify: state guards, event-count-based open-downtime guard, duplicate rejection, invalid reason code rejection, closed-record rejection, snapshot/projection transitions (IN_PROGRESS→BLOCKED, BLOCKED→PAUSED), no-auto-resume invariant, resume-blocked-while-open, no-session and open-session parity
- `downtime_started` / `downtime_ended` event emission verified
- BLOCKED→PAUSED transition after `end_downtime` verified; no auto-resume confirmed
- `resume_operation` blocked while downtime open confirmed (STATE_DOWNTIME_OPEN)
- Design clarification noted: `_derive_status` returns BLOCKED when downtime_started > downtime_ended, even when snapshot is PAUSED — event-derived projection is authoritative
- StationSession diagnostic non-blocking contract re-verified
- Claim compatibility regression re-verified unchanged

Non-scope preserved:
- No StationSession hard enforcement
- No claim removal or claim behavior change
- No event name changes
- No schema migration
- No complete/close/reopen hardening
- No FE/UI changes

Files introduced for this slice:
- backend/tests/test_downtime_command_hardening.py

Production code changes:
- none (tests-only hardening slice)

Verification summary:
- P0-C-06B focused tests: 14 passed
- P0-C-06A + P0-C-05 regression: 24 passed
- Station session lifecycle/diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 222 passed, 1 skipped, exit 0

### 22. P0-C-07A Complete Operation Command Hardening

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:
- Focused `complete_operation` hardening suite added: `backend/tests/test_complete_operation_command_hardening.py`
- 10 tests added to verify: happy path from IN_PROGRESS, invalid runtime state rejection, already-completed rejection, CLOSED-record rejection, tenant mismatch rejection, completion event emission, projection status after complete, allowed-actions after complete, no-session parity, matching OPEN-session parity
- `OP_COMPLETED` event emission verified
- Projection after complete verified as event-derived `completed`
- `allowed_actions` after complete verified as backend-derived `["close_operation"]`
- StationSession diagnostic non-blocking contract re-verified for `complete_operation`
- Claim compatibility regression re-verified unchanged

Non-scope preserved:
- No StationSession hard enforcement
- No claim removal or claim behavior change
- No event name changes
- No schema migration
- No close/reopen hardening changes
- No FE/UI changes

Files introduced for this slice:
- backend/tests/test_complete_operation_command_hardening.py

Production code changes:
- none (tests-only hardening slice)

Verification summary:
- P0-C-07A focused tests: 10 passed
- Recent command hardening regression: 38 passed
- Station session lifecycle/diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 232 passed, 1 skipped, exit 0

### 23. P0-C-07B Close Operation Guard Hardening

Status: Complete.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:
- Focused `close_operation` hardening suite added: `backend/tests/test_close_operation_command_hardening.py`
- 10 tests added to verify: happy path from COMPLETED, invalid runtime state rejection, already-closed rejection, tenant mismatch rejection, close event emission, closure_status transition to CLOSED, projection/detail consistency after close, allowed-actions after close, no-session parity, matching OPEN-session parity
- `operation_closed_at_station` event emission verified
- Post-close detail projection verified: `closure_status=closed`, `allowed_actions=["reopen_operation"]`
- StationSession diagnostic non-blocking contract re-verified for `close_operation`
- Claim compatibility regression and close/reopen baseline regression re-verified unchanged

Non-scope preserved:
- No StationSession hard enforcement
- No claim removal or claim behavior change
- No event name changes
- No schema migration
- No reopen hardening changes
- No FE/UI changes

Files introduced for this slice:
- backend/tests/test_close_operation_command_hardening.py

Production code changes:
- none (tests-only hardening slice)

Verification summary:
- P0-C-07B focused tests: 10 passed
- Recent command hardening regression: 48 passed
- Station session lifecycle/diagnostic suites: 25 passed
- Claim regression subset (includes close/reopen baseline): 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 242 passed, 1 skipped, exit 0

### 24. P0-C-07C Reopen Operation / Claim Continuity Hardening

Classification: Tests-only hardening slice

Production code changed: No

Scope:
- New focused hardening test suite: `backend/tests/test_reopen_operation_claim_continuity_hardening.py`
- 13 tests covering reopen guards, event emission, projection/detail, allowed_actions,
  claim continuity, and StationSession diagnostic non-interference
- Verified T4 (None reason) is schema-level Pydantic guard (documented correctly)
- All prior claim/reopen/close regression suites remain green
- StationSession diagnostic confirmed non-blocking for reopen path (T10, T11)
- `_restore_claim_continuity_for_reopen` preserved and confirmed compatible
- Claim compatibility lock baseline unchanged

Out of scope preserved:
- No claim removal
- No StationSession hard enforcement
- No close_operation changes
- No schema migration
- No FE/UI changes

Files introduced for this slice:
- backend/tests/test_reopen_operation_claim_continuity_hardening.py

Production code changes:
- none (tests-only hardening slice)

Verification summary:
- P0-C-07C focused tests: 13 passed
- Close/complete hardening regression: 20 passed
- Recent command hardening regression: 38 passed
- StationSession lifecycle/diagnostic suites: 25 passed
- Claim regression subset (includes close/reopen baseline): 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 255 passed, 1 skipped, exit 0

### 25. P0-C-08E Reopen / Resume Continuity Replacement

Status: Implementation complete; verification recorded with full-suite instability.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

Scope implemented:
- Narrow production change in `backend/app/services/operation_service.py`:
  - `_restore_claim_continuity_for_reopen(...)` now skips restoration (non-blocking) when historical owner already has another active claim in same station scope.
- Reopen flow remains non-StationSession-enforced in 08E.
- Resume-after-reopen remains governed by existing StationSession command guard behavior.
- Added focused 08E continuity suite:
  - `backend/tests/test_reopen_resume_station_session_continuity.py`
- Updated claim-continuity expectation:
  - `backend/tests/test_reopen_resumability_claim_continuity.py`

Non-scope preserved:
- No claim removal.
- No close_operation StationSession enforcement.
- No additional queue migration.
- No new domain events.
- No schema migration.

Verification summary (sequential, required matrix):
- `test_reopen_resume_station_session_continuity.py`: `5 passed`, exit `0`
- `test_reopen_resumability_claim_continuity.py` + `test_reopen_operation_claim_continuity_hardening.py` + `test_close_reopen_operation_foundation.py`: `21 passed`, exit `0`
- `test_station_session_command_guard_enforcement.py`: `22 passed`, exit `0`
- `test_station_queue_session_aware_migration.py` + `test_station_queue_active_states.py`: `10 passed`, exit `0`
- command hardening batch (`start/pause/resume`, `report_quantity`, `downtime`, `complete`, `close`): `58 passed`, exit `0`
- StationSession/diagnostic/claim batch: `45 passed`, exit `0`
- full backend suite: `164 passed, 1 skipped, 6 errors`, interrupted (KeyboardInterrupt), exit `2`

Slice closure note:
- 08E implementation scope is complete.
- Full-suite verification in this run is not clean due DB deadlock/transaction contamination under teardown overlap.

  ### P0-C-08G Claim Removal Readiness Check

  Status: Complete (review-only, no implementation).

  Verdict: READY_FOR_P0_C_08H_STAGED_REMOVAL_PLAN

  ### P0-C-08H1 Claim Consumer / Queue Contract Cutover Plan

  Status: Complete (plan-only, no implementation).

  Verdict: READY_FOR_P0_C_08H2_FRONTEND_QUEUE_CONSUMER_CUTOVER

  ### P0-C-08H2 Frontend Queue Consumer Cutover to StationSession Ownership Contract

  Status: Complete.

  Completed scope:
  - Frontend ownership-first logic implemented across 6 key files
  - Claim APIs marked deprecated; retained for backward compatibility
  - Claim compat fallback in place for defensive programming
  - Queue filtering now ownership-driven
  - Execution readiness now ownership-driven
  - No backend behavior modifications
  - No database migrations
  - Frontend does not call claim APIs in primary execution flow

  Verification summary:
  - Backend claim API deprecation: 5 passed
  - Backend queue session-aware migration: 2 passed
  - Backend command guard enforcement: 22 passed
  - Backend regression total: 29 passed (6.98s)
  - Full backend suite (08F baseline): 289 passed, 1 skipped

  Verdict:
  - `ALLOW_IMPLEMENTATION_COMPLETE`
  - P0-C-08H2 complete and passing.

  ### P0-C-08H3 Backend Execution Route Claim Guard Removal Contract

  Status: Complete (contract-only, no implementation).

  Verdict: READY_FOR_P0_C_08H4_ROUTE_GUARD_REMOVAL_SUBSET

  ### P0-C-08H4 Backend Execution Route Claim Guard Removal for StationSession-Enforced Commands

  Status: Complete.

  Completed scope:
  - Removed route-level claim guard from approved seven command routes only:
    - start
    - pause
    - resume
    - report-quantity
    - start-downtime
    - end-downtime
    - complete
  - Added route-level H4 contract regression suite:
    - `backend/tests/test_execution_route_claim_guard_removal.py`
  - Kept close/reopen unchanged.
  - Kept claim API/service/model/table/audit unchanged.
  - Kept queue behavior unchanged.
  - No frontend changes.
  - No migrations.

  Verification summary:
  - H4 route test: `12 passed`, `H4_ROUTE_TEST_EXIT:0`
  - StationSession guard regression: `22 passed`, `H4_STATION_SESSION_REG_EXIT:0`
  - Claim compatibility regression: `25 passed`, `H4_CLAIM_COMPAT_REG_EXIT:0`
  - Queue regression: `10 passed`, `H4_QUEUE_REG_EXIT:0`
  - Close/reopen regression: `36 passed`, `H4_CLOSE_REOPEN_REG_EXIT:0`
  - Command hardening regression: `48 passed`, `H4_CMD_HARDEN_REG_EXIT:0`
  - Full backend suite rerun after cleanup: `301 passed, 1 skipped`, `H4_FULL_BACKEND_EXIT:0`

  Verdict:
  - `P0-C-08H4_COMPLETE_VERIFICATION_CLEAN`
  - Stop after this single slice.

### P0-C-08H6 Frontend/API Consumer Cutover from Claim/Release Calls

Status: Complete.

Completed scope:
- Removed StationExecution claim/release API consumer calls from primary UI flow.
- Removed Mode A claim acquire action panel.
- Removed Mode B header release action and related props/wiring.
- Normalized action affordance gate to ownership/session-capable `canExecute`.
- Preserved claim compatibility typing and fallback read behavior.

Out-of-scope preserved:
- No backend code changes.
- No claim API/service/model/table removal.
- No queue payload/API shape changes.
- No migration/schema changes.

Verification summary:
- Frontend lint: `H6_FRONTEND_LINT_EXIT:0`
- Frontend build: `H6_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H6_FRONTEND_ROUTE_SMOKE_EXIT:0`
- Backend smoke: `29 passed`, `H6_BACKEND_SMOKE_EXIT:0`

Verdict:
- `P0-C-08H6_COMPLETE_VERIFICATION_CLEAN`
- Stop after this single slice.

### P0-C-08H6-V1 Claim-Derived Execution Affordance Removal + Verification Gap Closure

Status: Complete.

Completed scope:
- Removed `|| claimState === "mine"` from `canExecute` in `StationExecution.tsx`.
- `canExecute` is now exclusively `canExecuteByOwnership` (StationSession/ownership-derived).
- Verified no `claimState` references remain in StationExecution.tsx.
- Verified no direct `stationApi.claim` / `stationApi.release` calls in StationExecution or station-execution components.
- Queue claim fallback retained in `StationQueuePanel` and `QueueOperationCard` (display/debug only).

Out-of-scope preserved:
- No backend code changes.
- No claim API/service/model/table removal.
- No queue payload/API shape changes.
- No migration/schema changes.

Verification summary:
- Frontend lint: `H6V1_FRONTEND_LINT_EXIT:0`
- Frontend build: `H6V1_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H6V1_FRONTEND_ROUTE_SMOKE_EXIT:0` (77/78 covered)
- Backend smoke (4 files, 24 tests): `H6V1_BACKEND_SMOKE_EXIT:0`

Verdict:
- `P0_C_08H6_COMPLETE_VERIFICATION_CLEAN`
- Stop after this single slice.

### P0-C-08H7 Queue Claim Payload Retirement Contract / Review

Status: Complete (contract-only, no implementation).

Completed scope:
- Full queue claim payload inventory: backend schema + frontend consumers.
- Backend queue contract review: `get_station_queue` builds dual-shape payload; claim block fully present.
- Frontend consumer review: 3 components (`StationQueuePanel`, `QueueOperationCard`, `StationExecutionHeader`) still read `claim.*` for display/fallback; no claim data reaches `canExecute`.
- API compatibility / versioning decision made: Option D (FE-only fallback removal first) for H8, Option B (null-only backend) for H9.
- Staged retirement roadmap proposed: H8–H13.
- No code changes.

Out-of-scope preserved:
- No backend claim block removal.
- No frontend type removal.
- No claim API/service/model/table removal.
- No reopen compatibility removal.
- No migration/schema changes.

Verification summary:
- Backend smoke: `H7_BACKEND_SMOKE_EXIT:0` (24 passed)
- Frontend lint: `H7_FRONTEND_LINT_EXIT:0`
- Frontend route smoke: `H7_FRONTEND_ROUTE_SMOKE_EXIT:0` (77/78 covered, 24 checks PASS)

Verdict:
- `READY_FOR_P0_C_08H8_FRONTEND_QUEUE_CLAIM_FALLBACK_RETIREMENT`
- Stop after this single contract slice.

### P0-C-08H8 Frontend Queue Claim Fallback Retirement

Status: Complete (frontend implementation only).

Completed scope:
- Removed `item.claim.state === "mine"` fallback from `matchesQueueFilter` case "mine" (StationQueuePanel).
- Removed `item.claim.state === "mine"` fallback from `hasMineClaim` (StationQueuePanel).
- Removed `item.claim.state === "mine"` fallback from `summary.mine` accumulator (StationQueuePanel).
- Removed `item.claim.state === "other"` fallback from `lockedByOther` (QueueOperationCard).
- Removed `item.claim.state === "mine"` fallback from `isMine` (QueueOperationCard).
- Removed claim state fallback branches from `ownershipHint` (QueueOperationCard).
- Removed claim state fallback branches from `ownershipHintTone` (QueueOperationCard).
- Added compatibility deprecation comment to `ClaimSummary` interface + `StationQueueItem.claim` field (stationApi.ts).
- Updated stale `canReleaseClaim` JSDoc reference in StationExecutionHeader.tsx.

Out-of-scope preserved:
- Backend queue payload unchanged; claim block still sent by server.
- `ClaimSummary` / `QueueClaimState` TypeScript types retained until H9.
- `StationQueueItem.claim` frontend type field retained until H9.
- Deprecated `claim()` / `release()` / `getClaim()` client methods retained until H11.
- Backend claim APIs remain active/deprecated.
- No reopen compatibility removal.
- No claim service/model/table removal.
- No migration/schema changes.

Verification summary:
- Frontend lint: `H8_FRONTEND_LINT_EXIT:0`
- Frontend build: `H8_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H8_FRONTEND_ROUTE_SMOKE_EXIT:0` (77/78 covered, 24 checks PASS)
- Backend smoke (4 files, 24 tests): `H8_BACKEND_SMOKE_EXIT:0`

Verdict:
- `P0_C_08H8_COMPLETE_VERIFICATION_CLEAN`
- Stop after this single implementation slice.

### P0-C-08H9 Backend Queue Claim Payload Null-Only Contract

Status: Complete (contract-only, no implementation).

Completed scope:
- Backend queue claim payload null-only downgrade path reviewed after H8 frontend fallback removal.
- Backend queue service contract review: `get_station_queue` builds dual-shape payload; both ownership (target) and claim (compat) blocks present.
- Frontend consumer compatibility review: Frontend tolerates claim: null without code changes.
- Backend test impact review: One test (`test_station_queue_claim_fields_unchanged`) requires update to assert claim is None.
- API compatibility / versioning decision: Option B (keep claim field but send null-only) recommended as safest transition.
- H10 implementation scope proposed: Return claim: null from queue; update ownership_migration_status; update FE type to nullable; update test.
- No code changes in H9 (contract-only).

Out-of-scope preserved:
- No backend queue payload change.
- No frontend code change.
- No claim API/service/model/table removal.
- No reopen compatibility removal.
- No audit retention decision.
- No migration/schema changes.

Verification summary:
- Backend smoke: `H9_BACKEND_SMOKE_EXIT:0` (24 passed)
- Frontend lint: `H9_FRONTEND_LINT_EXIT:0`
- Frontend build: `H9_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H9_FRONTEND_ROUTE_SMOKE_EXIT:0` (77/78 covered, 24 checks PASS)

Verdict:
- `READY_FOR_P0_C_08H10_BACKEND_QUEUE_CLAIM_PAYLOAD_NULL_ONLY_IMPLEMENTATION`
- Stop after this single contract slice.

### P0-C-08H10 Backend Queue Claim Payload Null-Only Implementation

**Purpose:** Remove claim detail projection from queue items; `claim` field is always `null`. Dual-pane ownership-only queue is now complete end-to-end.

**Changes made:**
- `station_claim_service.get_station_queue`: Removed `_to_claim_state()` call; set `"claim": None`; updated `ownership_migration_status` to `"TARGET_SESSION_OWNER"`.
- `schemas/station.py`: Changed `claim: ClaimSummary` → `claim: ClaimSummary | None = None`.
- `test_station_queue_active_states.py`: Renamed test; updated assertions to `claim is None` and `ownership_migration_status == "TARGET_SESSION_OWNER"`.
- `test_station_queue_session_aware_migration.py`: Updated `ownership_migration_status` assertion to `"TARGET_SESSION_OWNER"`.
- `frontend/src/app/api/stationApi.ts`: Changed `claim: ClaimSummary` → `claim: ClaimSummary | null`.

**Verification:**
- Frontend lint: `H10_FRONTEND_LINT_EXIT:0`
- Frontend build: `H10_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H10_FRONTEND_ROUTE_SMOKE_EXIT:0` (78 routes, 77/78 covered, 24 PASS, 0 FAIL)
- Backend queue tests: `H10_BACKEND_QUEUE_EXIT:0` (10 tests passed)
- Backend smoke tests: `H10_BACKEND_SMOKE_EXIT:0` (22 tests passed)
- Backend reopen tests: `H10_REOPEN_COMPAT_EXIT:0` (17 tests passed)

**Test adjustment:** One assertion in `test_reopen_resumability_claim_continuity.py` was updated to remove queue claim payload read (now null-only per H10) — test assertion corrected per contract.

**Residuals:**
- Claims DB query in `get_station_queue` is now queue-projection-dead. Retained per H10 contract for claim API path compatibility. Remove in H11.
- Backend DB-backed tests verified clean via Docker recovery.

Verdict:
- `P0_C_08H10_COMPLETE_VERIFICATION_CLEAN`
- Stop after this slice. Do NOT start P0-D Quality Lite or H11 until released.

### P0-C-08H11 Reopen Claim Compatibility Retirement Contract

**Purpose:** Review reopen claim compatibility retirement readiness. Contract-only slice; no implementation.

**Scope:**
- Review `_restore_claim_continuity_for_reopen` helper (claim restoration on reopen).
- Review CLAIM_RESTORED_ON_REOPEN event emission.
- Review reopen test claim continuity expectations.
- Evaluate retirement options (remove vs no-op).
- Propose H11B implementation scope.
- Identify test assertion replacements (claim DB → StationSession verification).

**Key findings:**
- Reopen claim restoration is legacy compatibility; StationSession guard replaces it for resume continuity.
- Resume is already guarded by StationSession (H4); doesn't depend on claim restoration.
- 3 test assertions must be updated to StationSession-native expectations (LOW risk).
- 92 lines of code change (remove helper + 3 assertion updates).
- All 53 backend + 5 frontend baseline tests pass (EXIT:0).

**Verification:**
- Backend reopen smoke: `H11_REOPEN_SMOKE_EXIT:0` (26 tests)
- Backend compat smoke: `H11_COMPAT_SMOKE_EXIT:0` (27 tests)
- Frontend lint: `H11_FRONTEND_LINT_EXIT:0`
- Frontend build: `H11_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H11_FRONTEND_ROUTE_SMOKE_EXIT:0` (78 routes, 77/78 covered)

**Verdict:**
- `READY_FOR_P0_C_08H11B_REOPEN_CLAIM_COMPATIBILITY_RETIREMENT_IMPLEMENTATION`
- H11B scope: Remove reopen claim restoration; update 3 test assertions.
- Preconditions: Contract approved; test replacement path clear; risk register closed.
- Stop after this contract task.

### P0-C-08H11B Reopen Claim Compatibility Retirement Implementation

**Purpose:** Remove `_restore_claim_continuity_for_reopen` helper from `operation_service.py`. Reopen no longer creates, restores, or extends any `OperationClaim` row. `CLAIM_RESTORED_ON_REOPEN` audit events no longer produced.

**Changes made:**
- `operation_service.py`: Removed entire `_restore_claim_continuity_for_reopen` function (77 lines).
- `operation_service.py`: Removed call site `_restore_claim_continuity_for_reopen(db, operation=operation, tenant_id=tenant_id)` in `reopen_operation`.
- `operation_service.py`: Removed unused imports: `OperationClaim`, `OperationClaimAuditLog`, `timedelta`, `settings` (all exclusively used by removed helper).
- `test_reopen_resumability_claim_continuity.py`: Updated `test_reopen_restores_last_claim_owner_path_and_resume_is_reachable` — removed `active_claim is not None` DB assertion; added assertion no new claim created; retained resume success assertion.
- `test_reopen_resumability_claim_continuity.py`: Updated `test_reopen_preserves_active_claim_continuity_when_claim_still_exists` — removed `len(active_claims) == 1` assertion; asserted reopen succeeds with correct closure_status.
- `test_reopen_resumability_claim_continuity.py`: Updated `test_reopen_skips_claim_restoration_when_owner_has_other_active_claim` — retained `active_claims_for_reopened == []` assertion (correct post-H11B); added clarifying message.

**Explicitly out of scope and preserved:**
- Claim APIs remain active with deprecation headers.
- Claim service/model/table/audit unchanged.
- Queue claim null-only (H10) unchanged.
- No StationSession enforcement change.
- No DB migration.
- No frontend changes.

**Verification:**
- Reopen + continuity suite: `26 passed`, `H11B_REOPEN_EXIT:0`
- Compat suite: `27 passed`, `H11B_COMPAT_EXIT:0`
- Full backend suite: `391 passed, 3 skipped`, `H11B_FULLSUITE_EXIT:0`
- Frontend lint: `H11B_FRONTEND_LINT_EXIT:0`
- Frontend build: `H11B_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H11B_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 77/78 covered)

**Verdict:**
- `P0_C_08H11B_COMPLETE_VERIFICATION_CLEAN`
- Stop after this single implementation slice.

---

### P0-C-08H12 Claim API Runtime Disablement Contract

**Goal:** Contract-only review. Determine how to disable claim APIs at runtime, what error code to use, what tests change, and what H12B implementation must do.

**Hard Mode MOM:** v3 (touches claim ownership, audit event path, execution surface, tenant/auth boundary)

**Source Files Reviewed:**
- `backend/app/api/v1/station.py` — 3 claim routes with deprecation headers; queue route unchanged
- `backend/app/services/station_claim_service.py` — full claim lifecycle; `_expire_claim_if_needed` still active in queue loop
- `backend/tests/test_claim_api_deprecation_lock.py` — 5 tests; currently assert 200 + deprecation headers
- `frontend/src/app/api/stationApi.ts` — deprecated stubs; no active callers in production code
- `docs/design/00_platform/canonical-error-code-registry.md` + `canonical-error-codes.md` — NO existing disabled/retired API code

**Key Findings:**
- No active frontend callers of claim, release, or getClaim APIs.
- No canonical error code exists for "API disabled / retired" — H12B must add `CLAIM_API_DISABLED` (HTTP 410) to the registry first.
- `_expire_claim_if_needed` in queue loop still active but is dead code in queue projection (claim returned as null per H10); cleanup deferred to H14.
- All 3 claim-only endpoints can be safely disabled without affecting execution, session, queue, or reopen flows.

**Baseline Verification:**
- Compat smoke: `27 passed`, `H12_COMPAT_SMOKE_EXIT:0`
- Reopen smoke: `22 passed`, `H12_REOPEN_SMOKE_EXIT:0`
- Frontend lint: `H12_FRONTEND_LINT_EXIT:0`
- Frontend build: `H12_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H12_FRONTEND_ROUTE_SMOKE_EXIT:0`

**Contract Document:** `docs/implementation/p0-c-08h12-claim-api-runtime-disablement-contract.md`

**Verdict:**
- `READY_FOR_P0_C_08H12B_WITH_CANONICAL_ERROR_ADDITION`
- H12B must: (1) register `CLAIM_API_DISABLED` canonical error code (HTTP 410); (2) disable 3 claim-only endpoints to return 410; (3) update 3 test assertions in `test_claim_api_deprecation_lock.py`.
- After H12B: proceed to H13 Audit Retention Decision before any service/table removal.

---

### P0-C-08H12B Claim API Runtime Disablement Implementation

**Goal:** Single-slice backend implementation. Disable 3 legacy claim-only endpoints at runtime; return HTTP 410 + `CLAIM_API_DISABLED` + deprecation headers. No route definitions, service functions, models, tables, or audit history removed.

**Files Changed:**
- `backend/app/api/v1/station.py` — Added `_CLAIM_DISABLED_HEADERS` + `_raise_claim_api_disabled()` helper; disabled 3 route bodies (claim, release, claim-status); removed 4 orphaned imports (`claim_operation`, `release_operation_claim`, `get_operation_claim_status`, `ClaimConflictError`).
- `backend/tests/test_claim_api_deprecation_lock.py` — Updated 3 test functions to assert 410 + `CLAIM_API_DISABLED` + deprecation headers; removed orphaned `SimpleNamespace` import.
- `docs/design/00_platform/canonical-error-code-registry.md` — Added `CLAIM_API_DISABLED` (HTTP 410, `APPROVED_FOR_P0_C_08H12B`).
- `docs/design/00_platform/canonical-error-codes.md` — Added `CLAIM_API_DISABLED` section with full documentation.

**Behavior After H12B:**

| Endpoint | Before | After | Status |
|---|---|---|---:|
| `POST .../queue/{id}/claim` | 200 + ClaimResponse | 410 + CLAIM_API_DISABLED + headers | 410 |
| `POST .../queue/{id}/release` | 200 + ClaimResponse | 410 + CLAIM_API_DISABLED + headers | 410 |
| `GET .../queue/{id}/claim` | 200 + status dict | 410 + CLAIM_API_DISABLED + headers | 410 |
| Queue, sessions, exec commands | unchanged | unchanged | — |

**Explicitly Not Done:**
- Route definitions NOT removed.
- Claim service NOT modified.
- `OperationClaim` / audit model / tables NOT removed.
- Frontend NOT changed.
- DB migration NOT added.

**Verification:**
- Claim API suite: `25 passed`, `H12B_CLAIM_API_EXIT:0`
- Execution/queue/reopen regression: `44 passed`, `H12B_EXEC_QUEUE_REOPEN_EXIT:0`
- Frontend lint: `H12B_FRONTEND_LINT_EXIT:0`
- Frontend build: `H12B_FRONTEND_BUILD_EXIT:0` (3408 modules)
- Frontend route smoke: `H12B_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 77/78 covered)
- Full backend suite: `391 passed, 3 skipped`, `H12B_FULL_BACKEND_EXIT:0`

**Verdict:**
- `P0_C_08H12B_COMPLETE_VERIFICATION_CLEAN`
- Recommended next slice: P0-C-08H13 Audit Retention Decision.

---

### P0-C-08H13 Audit Retention Decision / Claim Historical Data Policy

**Goal:** Contract-only governance review. Establish retention and removal policy for legacy claim model, tables, and audit history. No code changes.

**Sources reviewed:**
- H8–H12B implementation reports; `station_claim.py` model; `station_claim_service.py`; `0009_station_claims.sql`; frontend `stationApi.ts`; all backend tests referencing `OperationClaim`/`OperationClaimAuditLog`

**Key Findings:**
- `operation_claims` and `operation_claim_audit_logs` contain dev/test data only; no production retention requirement.
- `_expire_claim_if_needed()` still active in `get_station_queue()` — writes `CLAIM_EXPIRED` rows until H14 queue cleanup.
- FK constraint: `operation_claim_audit_logs.claim_id → operation_claims.id` — child must be dropped before parent.
- 3 test suites use `OperationClaim`/`OperationClaimAuditLog` in teardown; must be updated before H16 migration.
- Service-level tests `test_claim_single_active_per_operator.py` and `test_release_claim_active_states.py` must be deleted in H15.
- Frontend: `ClaimSummary`, `QueueClaimState`, `ClaimResponse`, `claim()`, `release()`, `getClaim()` — all deprecated stubs; no active callers.

**Verification (baseline smoke):**
- Compat smoke: `27 passed`, `H13_COMPAT_SMOKE_EXIT:0`
- Reopen smoke: `22 passed`, `H13_REOPEN_SMOKE_EXIT:0`
- Frontend lint: `H13_FRONTEND_LINT_EXIT:0`
- Frontend build: `H13_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H13_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 77/78 covered)

**Policy document:** `docs/implementation/p0-c-08h13-audit-retention-claim-historical-data-policy.md`

**Retention Policy Selected:** `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED`

**Removal sequence approved:**
- H14: Claim routes + FE client + `_expire_claim_if_needed` removal from queue loop
- H15: Claim service functions + schemas + model file deletion
- H16: Alembic migration — DROP `operation_claim_audit_logs`, then DROP `operation_claims`
- H-I: Post-removal regression closeout + `rg` sweep

**Stop conditions before H16:**
- `_expire_claim_if_needed` must be removed from `get_station_queue()` (H14)
- All test teardown claim-delete stmts removed (H14)
- `OperationClaim`/`OperationClaimAuditLog` ORM models deleted (H15)
- `rg` sweep of active source = 0 claim references

**Verdict:**
- `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED`
- Recommended next slice: P0-C-08H14 Claim Route / Frontend Client / Queue-Loop Removal.

---

### P0-C-08H14 Claim Route / Frontend Client / Queue-Loop Removal Contract

**Goal:** Contract-only review. Define exact scope and boundary for first hard-removal implementation slice after H13 policy approval.

**Sources inspected:**
- `backend/app/api/v1/station.py`, `backend/app/services/station_claim_service.py`, `backend/app/models/station_claim.py`
- `frontend/src/app/api/stationApi.ts`, `frontend/src/app/api/index.ts`
- All frontend components referencing `ClaimSummary/QueueClaimState/ClaimResponse/station.claim.*`
- All backend tests referencing claim models or claim service functions
- `backend/scripts/verify_station_claim.py`, `verify_station_queue_claim.py`, `verify_clock_on.py`, `verify_clock_off.py`
- Prior H8–H13 implementation reports

**Key Findings:**
- All 3 claim API routes return HTTP 410; zero active consumers; safe to remove entirely.
- `stationApi.claim()`, `stationApi.release()`, `stationApi.getClaim()` have zero callers in frontend source; safe to remove.
- `ClaimSummary`, `QueueClaimState`, `ClaimResponse`, `StationQueueItem.claim` have zero consumers outside `stationApi.ts`/`index.ts`.
- `station.claim.*` i18n keys are UI display strings — NOT claim type dependencies; RETAIN.
- `_expire_claim_if_needed()` call in `get_station_queue()` is still active — writes `CLAIM_EXPIRED` rows; BLOCKER for H16; MUST be removed in H14B.
- `claims` dict and `active_operation_ids` variable in queue loop are only used for claim expiration — safe to remove with the expiry block.
- `ensure_operation_claim_owned_by_identity()` has zero callers in production code — defer to H15.
- `add_claim_api_deprecation_headers()` in station.py is defined but never called — dead code; remove in H14B.
- `test_claim_api_deprecation_lock.py`: DELETE entire file in H14B (3 tests assert 410 on removed routes; 2 remaining tests are covered elsewhere or are moot).
- Teardown claim deletes in 3 test suites are already no-ops since H12B; remove stmts in H14B.
- `test_execution_route_claim_guard_removal.py`: RETAIN body; remove teardown claim deletes only.

**H14B In Scope:**
- Remove 3 claim API routes from `station.py` + `_raise_claim_api_disabled()` + `_CLAIM_DISABLED_HEADERS` + `add_claim_api_deprecation_headers()` + schema imports
- Remove queue claim expiry block from `get_station_queue()` (queue loop claim query + `_expire_claim_if_needed()` call + `claims` dict + `active_operation_ids` variable)
- Remove `stationApi.claim/release/getClaim` + `ClaimSummary`/`QueueClaimState`/`ClaimResponse` interfaces + `StationQueueItem.claim` field from `stationApi.ts`
- Remove claim type re-exports from `index.ts`
- Delete `test_claim_api_deprecation_lock.py`
- Remove teardown claim delete stmts from `test_execution_route_claim_guard_removal.py`, `test_operation_detail_allowed_actions.py`, `test_operation_status_projection_reconcile.py`

**H14B Out of Scope:**
- Service function deletion (H15)
- ORM model/file deletion (H15)
- Schema type deletion in `schemas/station.py` (H15)
- `test_claim_single_active_per_operator.py` / `test_release_claim_active_states.py` deletion (H15)
- Table drop migration (H16)
- Audit row deletion (H16)
- `station.claim.*` i18n key rename/removal (H-I or later)
- StationSession or execution command behavior changes

**Verification (baseline smoke):**
- Backend compat smoke: `27 passed`, `H14_COMPAT_SMOKE_EXIT:0`
- Backend reopen smoke: `22 passed`, `H14_REOPEN_SMOKE_EXIT:0`
- Frontend lint: `H14_FRONTEND_LINT_EXIT:0`
- Frontend build: `H14_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H14_FRONTEND_ROUTE_SMOKE_EXIT:0`

**Contract document:** `docs/implementation/p0-c-08h14-claim-route-frontend-client-queue-loop-removal-contract.md`

**Verdict:**
- `READY_FOR_P0_C_08H14B_ROUTE_CLIENT_QUEUE_LOOP_REMOVAL_IMPLEMENTATION`
- Recommended next slice: P0-C-08H14B Claim Route / Frontend Client / Queue-Loop Removal Implementation.

---

### P0-C-08H14B Claim Route / Frontend Client / Queue-Loop Removal Implementation

**Goal:** First hard-removal slice. Remove disabled claim API routes, frontend claim client surface, and queue-loop claim expiration block.

**Files changed:**
- `backend/app/api/v1/station.py` — 3 claim routes removed; `_raise_claim_api_disabled()`, `_CLAIM_DISABLED_HEADERS`, `add_claim_api_deprecation_headers()` removed; claim schema imports removed; `Response` import removed
- `backend/app/services/station_claim_service.py` — queue claim expiry block removed (`active_operation_ids`, `claims` dict, `_expire_claim_if_needed()` call); `CLAIM_EXPIRED` no longer emitted from queue read path
- `frontend/src/app/api/stationApi.ts` — `stationApi.claim/release/getClaim` removed; `QueueClaimState`, `ClaimSummary`, `ClaimResponse` types removed; `StationQueueItem.claim` field removed
- `frontend/src/app/api/index.ts` — `QueueClaimState`, `ClaimSummary`, `ClaimResponse` re-exports removed
- `backend/tests/test_claim_api_deprecation_lock.py` — DELETED
- `backend/tests/test_operation_detail_allowed_actions.py` — teardown claim delete stmts + import removed
- `backend/tests/test_operation_status_projection_reconcile.py` — teardown claim delete stmts + import removed

**Key decisions:**
- `test_execution_route_claim_guard_removal.py` UNTOUCHED — `_insert_active_claim()` retained until H16; teardown deletes retained (FK constraint requirement)
- `"claim": None` in queue item dict RETAINED for response stability
- `station.claim.*` i18n keys RETAINED — UI text strings, not claim API dependencies
- `CLAIM_API_DISABLED` retained in canonical docs as historical reference

**Verification:**
- Claim service tests: `20 passed`, `H14B_CLAIM_SERVICE_EXIT:0`
- Execution/queue/reopen regression: `44 passed`, `H14B_EXEC_QUEUE_REOPEN_EXIT:0`
- Frontend lint: `H14B_FRONTEND_LINT_EXIT:0`
- Frontend build: `H14B_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H14B_FRONTEND_ROUTE_SMOKE_EXIT:0`
- Full backend suite: `420 passed`, 4 pre-existing failures (Unicode/FK), `H14B_FULL_BACKEND_EXIT:1`
- Claim sweep (public API surface): CLEAN — zero claim references in `backend/app/api/**` and `frontend/src/**`

**Implementation report:** `docs/implementation/p0-c-08h14b-claim-route-frontend-client-queue-loop-removal-implementation-report.md`

**Verdict:**
- `P0_C_08H14B_COMPLETE_VERIFICATION_CLEAN`
- Recommended next slice: P0-C-08H15 Claim Service / Schema / Model Removal

---

### P0-C-08H15 Claim Service / Schema / Model Removal Contract

**Goal:** Contract-only readiness review for dead claim service/schema/model retirement boundaries after H14B.

**Contract outputs:**
- Dead claim service functions confirmed: `claim_operation`, `release_operation_claim`, `get_operation_claim_status`, `_expire_claim_if_needed`, `_log_claim_event`, `_to_claim_state`, plus claim-only helper set.
- Dead route schemas confirmed: `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse`.
- Queue compatibility boundary confirmed: keep `StationQueueItem.claim` nullable while backend still emits `claim: None`.
- Model/table boundary confirmed: model deletion is not minimal-safe in H15B unless dependent tests/scripts/db-init imports are handled in-slice; table migration remains H16/H17 only.
- Additional dependency risk discovered: claim model usage is broader than original H15 note (multiple tests/scripts beyond the initial shortlist).

**Verification (contract-time):**
- Claim service smoke: `20 passed`, `H15_CLAIM_SERVICE_SMOKE_EXIT:0`
- Execution/queue/reopen regression: `44 passed`, `H15_EXEC_QUEUE_REOPEN_EXIT:0`
- Frontend lint: `H15_FRONTEND_LINT_EXIT:0`
- Frontend build: `H15_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H15_FRONTEND_ROUTE_SMOKE_EXIT:0`

**Contract document:** `docs/implementation/p0-c-08h15-claim-service-schema-model-removal-contract.md`

**Verdict:**
- `READY_FOR_P0_C_08H15B_WITH_MODEL_DEFERRED_TO_MIGRATION`
- Recommended next slice: P0-C-08H15B Claim Service / Schema Dead-Code Removal Implementation

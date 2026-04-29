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

Status: In progress. Entry audit complete. Slices P0-C-01 through P0-C-03 complete.

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

Pending slices (in recommended order):
- P0-C-04 Station Session Ownership Alignment
- P0-C-05 Start / Pause / Resume Command Hardening
- P0-C-06 Production Reporting + Downtime Commands
- P0-C-07 Complete / Close / Reopen Guard Alignment

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

# P0-C Execution Entry Audit

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial P0-C entry audit after P0-B closeout debt cleanup. Audit-only, no execution logic changes. |
| 2026-04-29 | v1.1 | P0-C-01 implemented. PENDING/LATE allowed_actions coverage added. Tenant isolation tests added. WO/PO hierarchy read test added. Design gap DG-P0C01-ROUTING-FK-001 documented. |
| 2026-04-29 | v1.2 | P0-C-02 implemented. Bug fixed: `_derive_status` dead-code for OP_COMPLETED/OP_ABORTED causing wrong status in reopen→resume→complete scenario. 7 pure-unit regression tests added. Backend suite: 153 passed, 1 skipped, exit 0. |
| 2026-04-29 | v1.3 | P0-C-03 implemented. Added detail-vs-bulk projection parity tests for core sequences and reconcile apply path. Hardened operation event read ordering to `created_at, id` for deterministic projection parity. Backend suite: 159 passed, 1 skipped, exit 0. |

## Executive Summary

Execution foundation is already substantial in backend source: operation lifecycle commands, downtime, closure/reopen, status projection reconciliation, station queue, and claim ownership guardrails are implemented and tested.

Current source remains claim-owned for execution write paths, while canonical target design is session-owned execution. This is the primary controlled debt entering P0-C.

P0-C should proceed with narrow, sequence-safe slices. First slice should align operation/work order execution foundations and guard semantics before introducing session ownership changes.

## Current Source Execution Surface

Primary execution surfaces in source:
- Models: execution events, operation/work order/prod order, operation claims
- Services: operation command handlers, claim lifecycle, projection reconciliation, execution timeline projection, global operation summaries
- APIs: operation execution endpoints, station queue/claim endpoints, execution timeline read endpoint
- Tests: closure/reopen, claim continuity, active-state queue behavior, projection reconciliation, allowed-actions projection, auth gates

Core evidence files reviewed:
- docs/design/02_domain/execution/station-execution-state-matrix-v4.md
- docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md
- docs/design/02_domain/execution/station-execution-policy-and-master-data-v4.md
- docs/design/02_domain/execution/station-execution-exception-and-approval-matrix-v4.md
- docs/design/02_domain/execution/execution-state-machine.md
- docs/implementation/p0-b-mmd-closeout-review.md
- backend/app/models/master.py
- backend/app/models/execution.py
- backend/app/models/station_claim.py
- backend/app/services/operation_service.py
- backend/app/services/station_claim_service.py
- backend/app/services/work_order_execution_service.py
- backend/app/services/execution_timeline_service.py
- backend/app/services/global_operation_service.py
- backend/app/api/v1/operations.py
- backend/app/api/v1/station.py
- backend/app/api/v1/execution_timeline.py
- backend/tests/test_operation_detail_allowed_actions.py
- backend/tests/test_closure_status_invariant.py
- backend/tests/test_close_reopen_operation_foundation.py
- backend/tests/test_close_operation_auth.py
- backend/tests/test_operation_status_projection_reconcile.py
- backend/tests/test_status_projection_reconcile_command.py
- backend/tests/test_claim_single_active_per_operator.py
- backend/tests/test_release_claim_active_states.py
- backend/tests/test_reopen_resumability_claim_continuity.py
- backend/tests/test_station_queue_active_states.py
- backend/tests/test_start_downtime_auth.py

Note:
- docs/design/02_domain/execution/execution-lifecycle.md is not present in repository.
- Requested v3 files are migration stubs that explicitly point to v4 canonical files.

## Existing Execution Models

Implemented execution-relevant models:
- ExecutionEvent log: append-only event store used for runtime derivation (backend/app/models/execution.py)
- Operation aggregate with runtime status, closure_status, quantity projections, reopen metadata (backend/app/models/master.py)
- WorkOrder and ProductionOrder status/progress carriers (backend/app/models/master.py)
- OperationClaim and OperationClaimAuditLog for station-claim ownership model (backend/app/models/station_claim.py)

Observed model-level truths:
- Runtime status and closure status are orthogonal in source
- Event log is used as execution truth; operation snapshot fields are projection caches
- Claim tables remain active and integrated with execution flows

## Existing Execution Services

Implemented services:
- operation_service.py:
  - start, pause, resume, report quantity, start/end downtime, complete, abort, close, reopen
  - runtime status derivation from events
  - allowed_actions projection
  - projection mismatch detection and repair helpers
- station_claim_service.py:
  - station queue projection
  - claim/release/status operations
  - claim continuity restoration on reopen
- work_order_execution_service.py:
  - recompute work-order status from operation snapshots
- execution_timeline_service.py:
  - event-backed timeline projection
- global_operation_service.py:
  - operation list projections and supervisor buckets

## Existing Execution APIs

Execution write/read APIs:
- /api/v1/operations/{id}
- /api/v1/operations/{id}/start
- /api/v1/operations/{id}/pause
- /api/v1/operations/{id}/resume
- /api/v1/operations/{id}/report-quantity
- /api/v1/operations/{id}/start-downtime
- /api/v1/operations/{id}/end-downtime
- /api/v1/operations/{id}/complete
- /api/v1/operations/{id}/abort
- /api/v1/operations/{id}/close
- /api/v1/operations/{id}/reopen

Station ownership APIs (claim-centric):
- /api/v1/station/queue
- /api/v1/station/queue/{operation_id}/claim
- /api/v1/station/queue/{operation_id}/release
- /api/v1/station/queue/{operation_id}/claim (status)
- /api/v1/station/queue/{operation_id}/detail

Execution timeline read API:
- /api/v1/work-orders/{work_order_id}/execution-timeline

## Existing Execution Tests

High-value coverage present:
- Closure invariants and closed-record write rejection
- Close/Reopen behavior and role/action auth gates
- Allowed-actions matrix and event round-trip semantics
- Downtime lifecycle and non-auto-resume behavior
- Runtime projection reconciliation and reconcile command
- Station queue active-state inclusion and terminal exclusion
- Single-active-claim and release restrictions for active states
- Reopen claim-continuity restoration and conflict guard

## Design vs Source Alignment

Aligned areas:
- Closed-record invariant enforced for execution writes
- Open-downtime guard enforced for resume/complete semantics
- Append-only event truth and projection derivation pattern exists
- Closure OPEN/CLOSED orthogonal to runtime status in source

Partial/misaligned areas:
- Target design is session-owned execution; source remains claim-owned for write command authorization
- Session/context command family is absent in source:
  - open_station_session
  - identify_operator
  - bind_equipment
  - close_station_session
- Event namespace is mixed legacy/canonical in source enum:
  - legacy upper snake values remain (OP_STARTED, OP_COMPLETED, etc.)
  - newer lower-snake values exist for pause/resume/downtime/close/reopen
- Requested v3 design documents are now stubs, so v4 must be treated as canonical for P0-C planning

## State Machine Coverage

Implemented/covered runtime states in source:
- PLANNED
- IN_PROGRESS
- PAUSED
- BLOCKED
- COMPLETED
- ABORTED

Implemented closure dimension:
- OPEN
- CLOSED

State-transition coverage is strong for current claim-compatible model:
- start, pause, resume, downtime start/end, complete, abort, close, reopen
- reopen returns runtime to PAUSED
- end_downtime does not auto-resume

## Command/Event Coverage

Covered command/event families in source:
- start_execution -> OP_STARTED
- pause_execution -> execution_paused
- resume_execution -> execution_resumed
- report_production -> QTY_REPORTED
- start_downtime -> downtime_started
- end_downtime -> downtime_ended
- complete_execution -> OP_COMPLETED
- close_operation -> operation_closed_at_station
- reopen_operation -> operation_reopened

Gaps versus v4 target command/event contract:
- No implemented station session commands/events
- Mixed event naming conventions create normalization debt before broader P0-C hardening

## Projection Coverage

Projection/read-model behavior already present:
- derive_operation_runtime_projection_for_ids in operation_service
- detect/reconcile mismatch helpers in operation_service
- dedicated reconcile command script in scripts/reconcile_operation_status_projection.py with test coverage
- station queue status now derives from event truth instead of stale snapshot-only assumptions
- work-order status recomputation from child operations implemented

## Tenant/Scope/Auth Coverage

Tenant and auth coverage is present but split across patterns:
- Tenant checks in operation endpoints and services are explicit
- Action-based auth dependencies used in operation routes
- Station queue/claim uses role and station scope resolution from RBAC assignment
- Claim ownership enforcement currently gates execution writes
- Close/Reopen include explicit SUP role gate checks

## Claim vs Session-Owned Target Debt

Primary P0-C entry debt:
- Source enforces claim ownership before execution writes
- Target design deprecates claim as ownership truth in favor of station session context

Controlled transition requirement:
- Keep current claim behavior stable while introducing session-owned alignment slices incrementally
- Avoid broad station refactor in first slice

## Risks Before P0-C Implementation

- Risk 1: Introducing session ownership too early without preserving current command legality could regress active station flows
- Risk 2: Mixed event naming conventions may complicate projections/integration if normalized and business changes are coupled
- Risk 3: Claim and session semantics can conflict if migration phases are not explicitly bounded
- Risk 4: Missing execution-lifecycle design file path in repo can cause audit/tooling confusion if not documented as absent

## Recommended P0-C Slice Order

Conservative order:
1. P0-C-01 Work Order / Operation Foundation Alignment — **COMPLETE**
2. P0-C-02 Execution State Machine Guard Alignment — **COMPLETE**
3. P0-C-03 Execution Event Log / Projection Consistency — **COMPLETE**
4. P0-C-04 Station Session Ownership Alignment
5. P0-C-05 Start / Pause / Resume Command Hardening
6. P0-C-06 Production Reporting + Downtime Commands
7. P0-C-07 Complete / Close / Reopen Guard Alignment

## First Safe Implementation Slice

Recommended first slice:
- P0-C-01 Work Order / Operation Foundation Alignment

Why first:
- Lowest migration risk while strengthening execution base invariants
- Improves status/projection consistency before ownership model transition
- Avoids immediate broad station execution refactor

## Stop Conditions

Stop and re-evaluate before coding if any occur:
- Any proposed change introduces dispatch, APS, BOM, Backflush, ERP, Acceptance Gate, or frontend scope
- Any proposed change requires schema migration in first slice
- Session-owned changes require deleting/bypassing claim behavior without equivalent guarded transition path
- Event/projection modifications cannot preserve existing passing execution regression tests
- Tenant/scope/auth checks become less strict in route or service layer
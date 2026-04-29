# P0-C-04 Station Session Ownership Alignment Review

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Design review of claim-owned source vs session-owned target. PROPOSE-ONLY. No implementation changes. |

## Executive Summary

Current backend execution is **claim-owned** (OperationClaim model, station_claim_service). Target design is **session-owned** (per station-execution-state-matrix-v4.md and station-execution-command-event-contracts-v4.md).

This is the primary controlled debt entering P0-C-04.

**Key finding:** Claim model is a compatibility layer, not the target truth. Migration strategy must decide whether to:
- **Option A (Big-Bang):** Remove claim directly, replace with session (HIGH RISK, not recommended for first slice).
- **Option B (Compatibility Bridge):** Keep claim as compatibility during gradual session introduction (RECOMMENDED).
- **Option C (Claim-Only Hardening):** Harden claim temporarily, plan session as future work (ACCEPTABLE if session contract is immature).

**Verdict:** READY FOR IMPLEMENTATION under Option B (Compatibility Bridge) strategy with narrow, test-first slices.

---

## 1. Scope and Non-Scope

### Scope for P0-C-04 Design Review

- Current claim ownership model and behavior
- Target session ownership model from design docs
- Gap analysis between current and target
- Event contract implications
- Invariant impact
- API/test implications
- Safe migration paths
- Proposed implementation sequence

### NOT in Scope

- Implementing session ownership changes
- Removing claim code
- Adding DB migrations
- Changing API behavior
- Implementing dispatch, APS, BOM, Backflush, ERP
- Frontend execution UI changes
- Breaking current test suite

---

## 2. Design Evidence

### Target Design Sources (Canonical)

**From docs/design/02_domain/execution/station-execution-state-matrix-v4.md (v4.0):**

> "This matrix replaces claim-owned target semantics with session-owned target semantics.
> Any remaining claim-owned behavior in current code is migration debt, not target matrix truth."

Session/context transitions required:
- `open_station_session` → `station_session_opened` event
- `identify_operator` → `operator_identified_at_station` event
- `bind_equipment` (conditional) → `equipment_bound_to_station_session` event
- `close_station_session` → `station_session_closed` event

Execution transitions guarded by:
- Valid station session context required
- Operator identified in session required
- Equipment bound (when policy requires)

**From docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md (v4.0):**

Target commands include:
- Session/context: `open_station_session`, `identify_operator`, `bind_equipment`, `close_station_session`
- Execution: `start_execution`, `pause_execution`, `resume_execution`, `report_production`, `start_downtime`, `end_downtime`, `complete_execution`

Canonical event intents:
- `station_session_opened`
- `operator_identified_at_station`
- `equipment_bound_to_station_session`
- `execution_started` (requires valid session context)
- `execution_paused`
- `execution_resumed`
- `production_reported`
- `downtime_started`
- `downtime_ended`
- `execution_completed`
- `operation_closed_at_station`
- `operation_reopened`
- `station_session_closed`

> "claim_operation and related claim semantics are deprecated from the target model.
> They may continue to exist temporarily in current code as compatibility debt during migration."

**From docs/design/02_domain/execution/station-execution-policy-and-master-data-v4.md (v4.0):**

Target policy truths:
- `require_station_session_for_execution = true`
- `require_operator_identification = true`
- `allow_start_without_claim = true` (claim is deprecated)
- Ownership resolved through active station session, not claim
- Claim-related implementation policy is compatibility debt

### Current Source Behavior (As Observed)

**Current claim-owned model:**
- `OperationClaim` aggregate in backend/app/models/station_claim.py
  - `claimed_by_user_id` identifies the operator holding the claim
  - `claimed_at` timestamp
  - `expires_at` for auto-release TTL
  - `released_at` for explicit release
  - `release_reason` optional note
- `OperationClaimAuditLog` for audit trail
- `station_claim_service` provides:
  - `claim_operation(db, identity, operation_id, reason, duration_minutes)`
  - `release_operation_claim(db, identity, operation_id, reason)`
  - `get_station_queue(db, identity)` — filters operations by station scope and claim status
  - `get_operation_claim_status(operation_id)` — returns claim state ("mine", "other", "none")
  - Implicit: single active claim per operation constraint enforced in service
- Station API endpoints:
  - `GET /station/queue` — returns scoped operation queue
  - `POST /station/queue/{operation_id}/claim` — creates claim
  - `POST /station/queue/{operation_id}/release` — releases claim
  - `GET /station/queue/{operation_id}/claim` — checks claim status
- Execution commands (operation_service.py):
  - `start_operation`, `pause_operation`, `resume_operation`, `report_quantity`, `start_downtime`, `end_downtime`, `complete_operation`
  - Do NOT currently require valid claim as guard (claim is informational, not required)
  - Guards include: operation status, closed-record reject, downtime checks, tenant isolation, authorization checks

**Current event behavior:**
- ExecutionEvent log used for event truth
- Events recorded:
  - OP_STARTED, OP_COMPLETED, OP_ABORTED (legacy naming)
  - execution_paused, execution_resumed (lower_snake naming)
  - downtime_started, downtime_ended
  - operation_closed_at_station
  - operation_reopened
  - QTY_REPORTED
  - No claim-related events (claim is not appended as event truth)
- Mixed event naming convention (legacy upper_snake and canonical lower_snake)

**Current tests that lock claim behavior:**
- test_claim_single_active_per_operator.py — single-active claim constraint
- test_release_claim_active_states.py — claim release under different states
- test_station_queue_active_states.py — queue filters active/terminal states
- test_reopen_resumability_claim_continuity.py — claim continuity on reopen
- No tests currently validate `allow_start_without_claim` semantics (claim not required guard)

**No StationSession model exists currently.**

---

## 3. Claim vs Session Gap Matrix

| Area | Target Design | Current Source | Gap Type | Severity | Proposed Handling |
|---|---|---|---|---|---|
| **Ownership Model** | Session-owned (open/identify/bind/close lifecycle) | Claim-owned (claim/release per operation) | DESIGN_GAP | HIGH | Introduce session model alongside claim; don't remove claim yet |
| **Execution Guard** | Requires active station session context | No session requirement (claim optional) | SOURCE_DEBT | HIGH | Add session context validation to execution commands (non-breaking) |
| **Operator Context** | Identified in session, persisted across operations | Identified per claim, implicit in claimed_by_user_id | SOURCE_DEBT | MEDIUM | Introduce operator identification API + model; map claim.claimed_by_user_id to session context |
| **Equipment Binding** | Explicit binding when policy requires | No equipment model in current code | DESIGN_GAP | MEDIUM | Add equipment binding API (conditional on policy); not required for MVP |
| **Event Contract** | Explicit session events (opened/closed/operator_identified) | No session events yet | TEST_GAP | MEDIUM | Define and emit session events before execution events required |
| **Claim Semantics** | Deprecated, will be removed | Active, tested, relied upon | COMPATIBILITY_DEBT | HIGH | Preserve claim behavior; add session as parallel model until safe to deprecate |
| **API Surface** | Session endpoints + execution endpoints | Claim endpoints + execution endpoints | COMPATIBILITY_DEBT | MEDIUM | Keep claim endpoints for backward compat; add session endpoints alongside |
| **Station Queue** | Queue derived from session ownership | Queue derived from claim status | SOURCE_DEBT | MEDIUM | Support both claim and session query paths during migration |
| **Frontend Dependency** | Session context in UI | Claims in UI (StationExecution.tsx) | COMPATIBILITY_DEBT | MEDIUM | Don't remove FE claim support until session is proven |
| **Reopen Continuity** | Session context restored on reopen | Claim continuity restored on reopen (test_reopen_resumability_claim_continuity.py) | NO_GAP | LOW | Verify session continuity pattern matches current claim continuity |
| **Tenant Isolation** | Maintained via session ownership | Maintained via claim + operation tenant_id checks | NO_GAP | LOW | Ensure session model includes tenant_id; no change needed |
| **Station Scope Isolation** | Maintained via session station binding | Maintained via claim + UserRoleAssignment scope checks | NO_GAP | LOW | Ensure session model includes station scope; no change needed |
| **Closed Record Invariant** | Still applies (closure_status = CLOSED) | Already enforced in operation_service | NO_GAP | LOW | No change needed; applies to both models |
| **Downtime Guard** | Still applies (open downtime blocks resume/complete) | Already enforced | NO_GAP | LOW | No change needed |
| **Projection Truth** | Event-derived, not snapshot | Event-derived, operation snapshots are caches | NO_GAP | LOW | No change needed |

---

## 4. Current APIs and Consumers

### Station API (Claim-Centric)

Current endpoints:
- `GET /api/v1/station/queue` — depends on claim context
- `POST /api/v1/station/queue/{operation_id}/claim` — creates claim
- `POST /api/v1/station/queue/{operation_id}/release` — releases claim
- `GET /api/v1/station/queue/{operation_id}/claim` — check claim status
- `GET /api/v1/station/queue/{operation_id}/detail` — operation detail in queue context

Consumers:
- FE StationExecution.tsx — calls claim/release, displays queue
- FE DispatchQueue.tsx (mock, not connected)

### Operation API (Claim-Agnostic)

Current endpoints (execution commands):
- `POST /api/v1/operations/{id}/start` — no current claim guard
- `POST /api/v1/operations/{id}/pause`
- `POST /api/v1/operations/{id}/resume`
- `POST /api/v1/operations/{id}/report-quantity`
- `POST /api/v1/operations/{id}/start-downtime`
- `POST /api/v1/operations/{id}/end-downtime`
- `POST /api/v1/operations/{id}/complete`
- `POST /api/v1/operations/{id}/close`
- `POST /api/v1/operations/{id}/reopen`

Consumers:
- FE StationExecution.tsx (via operationApi)
- Integration tests
- Backend tests

**Note:** Current implementation does NOT require claim to execute operations. Claim is informational (for queue visibility/coordination), not a permission guard.

---

## 5. Current Tests That Lock Claim Behavior

### Test Files Directly Testing Claim

| Test File | Purpose | Locked Behavior | Risk if Removed |
|---|---|---|---|
| test_claim_single_active_per_operator.py | Single active claim constraint | One claim per operation, same or different users over time | MEDIUM — if removed without session equivalent, claim behavior undefined |
| test_release_claim_active_states.py | Release behavior across operation states | Release allowed on terminal states, restricted on active states | MEDIUM — station queue filtering depends on this |
| test_station_queue_active_states.py | Queue filtering based on operation + claim status | Queue includes non-claimed PLANNED/IN_PROGRESS, excludes PAUSED/COMPLETED/CLOSED | MEDIUM — FE queue display relies on this |
| test_reopen_resumability_claim_continuity.py | Claim restoration on reopen | Claim is restored after reopen so operator can resume | MEDIUM — operator continuity assumes claim exists |
| test_close_reopen_operation_foundation.py | Close/reopen state machine | No explicit claim checks, but uses claim context in setup | LOW — tests operation state, not claim directly |

### Test Files Indirectly Depending on Claim Behavior

| Test File | Dependency | Risk |
|---|---|---|
| test_operation_detail_allowed_actions.py | Creates claim setup fixture (setup/teardown includes claim cleanup) | LOW — tests allowed_actions, not claim logic |
| test_station_queue_active_states.py | Queue function uses claim state internally | MEDIUM — if queue function changes, test breaks |
| Integration test suites | Claim implicit in station queue setup | LOW — integration scope, not claim-specific |

---

## 6. Current Event Recording and Projection

### Events Currently Recorded

ExecutionEvent log includes:
- `OP_STARTED` (legacy upper_snake)
- `OP_COMPLETED` (legacy upper_snake)
- `OP_ABORTED` (legacy upper_snake)
- `execution_paused` (canonical lower_snake)
- `execution_resumed` (canonical lower_snake)
- `downtime_started` (canonical lower_snake)
- `downtime_ended` (canonical lower_snake)
- `operation_closed_at_station` (canonical lower_snake)
- `operation_reopened` (canonical lower_snake)
- `QTY_REPORTED` (legacy upper_snake)

**Claim is NOT recorded as events.** Claim is a mutable record (released_at field), not append-only events.

### Projection Consumer

operation_service.py:
- `_derive_status(events)` — derives runtime status from event log
- `_derive_allowed_actions(operation, events)` — derives allowed actions from state + events
- `derive_operation_detail(operation)` — returns full operation detail with projections

**No projection dependency on claim currently.**

---

## 7. Invariant Impact

### Invariants Currently Enforced (No Change Needed)

| Invariant | Current Enforcement | Impact on Session Migration |
|---|---|---|
| INV-001: Closed records reject execution writes | operation_service guard on closure_status | PRESERVED — session model doesn't change this |
| INV-002: One running execution per governing station | Single-active-claim + queue filtering | REIMPLEMENT — will be enforced by session ownership instead |
| INV-003: Open downtime blocks resume/complete | operation_service guard on downtime_open | PRESERVED — unchanged |
| Tenant isolation | operation + claim + endpoint scope checks | PRESERVED — session model must include tenant_id |
| Station scope isolation | UserRoleAssignment + claim filters | PRESERVED — session model must include station scope |

### Invariants Requiring New Enforcement (Session Model)

| Invariant | Target Semantics | Current Source | Gap |
|---|---|---|---|
| One active station session per station | Only one open session per station at a time | N/A (no session model) | Need session model + uniqueness constraint |
| Active station session required for execution writes | Session must be open before any execution command | No current guard | Need session validation gate in all execution commands |
| Operator identified in session context | Operator identity tied to session lifetime | Implicit in claim.claimed_by_user_id, not persisted | Need operator_id in session model |
| Equipment bound when required | Equipment context tied to session (configurable by policy) | No current equipment model | Need conditional equipment binding API |

---

## 8. Event Contract Impact

### Target Events Not Yet Implemented

From station-execution-command-event-contracts-v4.md:

| Event Name | Purpose | When Emitted | Payload Minimum |
|---|---|---|---|
| `station_session_opened` | Session started | open_station_session command | tenant_id, actor_user_id, station_id, session_id, occurred_at |
| `operator_identified_at_station` | Operator identified in session | identify_operator command | tenant_id, actor_user_id, session_id, operator_id, occurred_at |
| `equipment_bound_to_station_session` | Equipment bound (conditional) | bind_equipment command | tenant_id, actor_user_id, session_id, equipment_id, occurred_at |
| `execution_started` | Execution started (requires session) | start_execution command | tenant_id, actor_user_id, operation_id, session_id, occurred_at |
| `station_session_closed` | Session closed | close_station_session command | tenant_id, actor_user_id, session_id, occurred_at |

**Current status:** None of these are implemented. ExecutionEvent log has no session-related events.

### Impact on Projection Consistency

Current projection logic (operation_service._derive_status) will continue to work because:
- Execution state derivation is event-based (from ExecutionEvent log)
- Session ownership is a **parallel** concern, not part of runtime status projection
- Adding session events does NOT break current status projection

However, will need NEW projections:
- `session_status` — is session open, operator identified, equipment bound?
- This is **parallel** to operation runtime status, not replacing it

---

## 9. Migration Strategy Options

### Option A: Big-Bang Claim Removal (NOT RECOMMENDED)

Description:
- Remove OperationClaim table and all claim-related service/API code
- Implement StationSession model immediately
- Update all execution commands to require session validation
- Update all tests to use session context instead of claim

Pros:
- Clean final state (no migration debt)
- No dual-model confusion

Cons:
- **Extremely high risk** for first slice
- Breaks current claim tests without equivalent session test coverage
- Breaks FE StationExecution.tsx claim endpoints
- Breaks any existing integrations expecting claim endpoints
- Requires extensive refactoring across service layer, tests, and FE
- If session contract is incomplete, blocking the slice

Recommendation:
**REJECT** for P0-C-04 first slice. Defer to later phase after session is proven separately.

---

### Option B: Compatibility Bridge (RECOMMENDED)

Description:
- Introduce StationSession model + APIs alongside OperationClaim
- Implement session lifecycle (open/identify/bind/close) as new feature
- Add execution command guards for session context WITHOUT requiring session yet (warn/soft-check)
- Keep claim functionality unchanged and tested
- Gradually transition execution commands to prefer session over claim
- Define deprecation plan for claim removal (future phase)

Pros:
- **Low breaking risk** for current code
- Can implement incrementally in sub-slices
- Current claim tests remain green
- FE can be migrated independently
- Clear migration path visible to stakeholders
- Allows session design to mature in real code before full migration

Cons:
- Temporary dual-model complexity
- Requires clear deprecation messaging
- Longer total path to final state

Recommendation:
**ACCEPT** — Enables safe P0-C-04 implementation in phases.

---

### Option C: Claim-Only Hardening (ACCEPTABLE ALTERNATIVE)

Description:
- Harden current claim model with additional tests
- Document session-owned target as future work
- Do NOT introduce session model yet
- Plan P0-C-04 as design-only, with implementation deferred to P0-C-05

Pros:
- Minimal code change
- No new complexity
- Can focus on claim reliability before migration
- Safer for extremely low-risk preference

Cons:
- Doesn't move toward target design
- Defers addressing core architecture tension
- May accumulate more claim-dependent code before migration

Recommendation:
**ACCEPTABLE** only if hard deadline prevents session implementation. Otherwise, Option B preferred.

---

## 10. Recommended Strategy: Option B (Compatibility Bridge)

### Principles

1. **No claim code removal yet** — Keep claim tests green
2. **Session introduced as parallel** — Doesn't replace claim immediately
3. **Incremental validation** — Execution commands gradually require session context
4. **Test-first** — New session tests added before command changes
5. **FE decoupled** — FE can use either claim or session endpoints (backwards compatible)
6. **Clear deprecation** — Document claim as migration debt, session as future truth

### Implementation Boundary

P0-C-04 will:
- ✓ Introduce StationSession model and persistence
- ✓ Implement open_station_session, identify_operator, close_station_session APIs
- ✓ Add test coverage for session lifecycle
- ✓ Add soft validation in execution commands (session context checked but not required)
- ✓ Preserve all claim functionality
- ✓ Preserve all existing execution command behavior
- ✗ NOT require claim removal
- ✗ NOT require execution command refactor (guards can be soft initially)
- ✗ NOT change FE behavior
- ✗ NOT implement dispatch or APS

---

## 11. Proposed P0-C-04 Implementation Slices

### P0-C-04A: Station Session Contract Finalization (Doc-Only)

**Purpose:** Ensure station session data model is complete before coding

**Outputs:**
- docs/design/02_domain/execution/station-session-ownership-contract.md
  - Session model fields
  - Session lifecycle semantics (open → identify → bind → close)
  - Session scope boundaries (per-station, per-operator, per-session-id)
  - Session TTL/expiration rules
  - Session validation requirements for execution commands

**Inputs:**
- station-execution-state-matrix-v4.md (state transitions)
- station-execution-command-event-contracts-v4.md (command families)
- Current OperationClaim model (for reference on scope fields)

**Tests:** None (doc-only)

**Acceptance:**
- Contract includes model fields, lifecycle, invariants, validation rules
- Aligned with target design docs
- Clear boundary between required and optional fields
- No implementation code

---

### P0-C-04B: Station Session Model & Readiness (Test-First Implementation)

**Purpose:** Implement session model and basic lifecycle without breaking claim

**Outputs:**
- backend/app/models/station_session.py
  - StationSession aggregate
  - Fields: session_id (uuid), station_id, operator_id, tenant_id, opened_at, closed_at, equipment_id (nullable)
- backend/app/repositories/station_session_repository.py
  - get_active_session_for_station(station_id, tenant_id)
  - create_session, close_session, identify_operator, bind_equipment
- backend/app/services/station_session_service.py
  - open_station_session(identity, station_id)
  - identify_operator_in_session(identity, session_id, operator_id)
  - bind_equipment_to_session(identity, session_id, equipment_id)
  - close_station_session(identity, session_id)
- backend/tests/test_station_session_lifecycle.py
  - Test open → identify → bind → close sequence
  - Test single-active-session constraint per station
  - Test tenant isolation
  - Test operator identification guard

**Inputs:**
- P0-C-04A contract

**Tests:**
- Happy path: open session, identify operator, close session
- Error cases: duplicate open, identify invalid operator, close active session
- Tenant isolation: cross-tenant session queries rejected
- Station scope: session tied to specific station

**Acceptance:**
- Model can be persisted
- Lifecycle API calls succeed in happy path
- Invariants enforced (single active per station, tenant isolation)
- All tests pass
- Claim functionality unchanged, all claim tests still pass

**DB Migration:**
- Add station_sessions table
- No changes to operation_claims table

---

### P0-C-04C: Execution Command Session Validation (Soft Guards)

**Purpose:** Add session validation to execution commands without breaking claim

**Outputs:**
- backend/app/services/operation_service.py (modified)
  - add_session_context_validation to start, pause, resume, report, downtime, complete
  - Validation is **soft** — checks if session exists and is valid, but does NOT reject command if session invalid
  - Emits warning/log if session context is missing
- backend/tests/test_operation_session_validation.py
  - Test execution with valid session context
  - Test execution with missing session (should still succeed but log warning)
  - Test execution with invalid session (should log error but not reject)

**Inputs:**
- P0-C-04B (session model + API)

**Tests:**
- start_execution with active session succeeds and proceeds normally
- start_execution without session still succeeds (backward compat)
- resume_execution with closed session logs warning but proceeds
- Execution events recorded normally (session context separate from event truth)

**Acceptance:**
- All execution commands execute normally with or without session
- Session context is optional (soft check)
- All claim tests still pass
- Warnings logged for missing/invalid session in logs
- No breaking API changes

---

### P0-C-04D: Station Queue Dual-Mode Support

**Purpose:** Station queue can derive from either claim or session context

**Outputs:**
- backend/app/services/station_claim_service.py (modified)
  - get_station_queue updated to support session-based filtering as alternative path
  - Query can use session ownership (if active session with identified operator) OR claim ownership (current)
  - Prefer session if available, fall back to claim
- backend/tests/test_station_queue_dual_mode.py
  - Test queue filtered by active claim (current behavior)
  - Test queue filtered by active session (new behavior)
  - Test queue transition from claim to session

**Inputs:**
- P0-C-04C (soft session validation)

**Tests:**
- Queue returns operations claimed by current user
- Queue returns operations claimed by current user's session
- Both claim and session filtering produce consistent results

**Acceptance:**
- Queue can be filtered by session when session is active
- Queue still works with claim (backward compat)
- No breaking changes to queue API

---

### P0-C-04E: Claim Deprecation Tests & Documentation

**Purpose:** Lock in claim behavior as compatibility layer, document deprecation plan

**Outputs:**
- backend/tests/test_claim_compatibility.py (new, consolidates claim guarantee tests)
  - Single-active claim behavior verified
  - Claim release under different states verified
  - Claim continuity on reopen verified
  - All marked as "compatibility layer, plan to replace with session"
- docs/implementation/p0-c-04-claim-deprecation-plan.md
  - Claim model is compatibility debt
  - Session is target ownership model
  - Timeline for claim removal (post-P0-C, TBD)
  - Migration path for dependent code
  - FE migration requirements documented

**Inputs:**
- All prior slices (A-D)

**Tests:**
- All claim tests remain green
- Claim tests marked as "deprecating in X phase"

**Acceptance:**
- Claim behavior locked in as compatibility
- Clear deprecation messaging in code/docs
- Session is identified as target truth
- Migration path visible to team

---

## 12. Tests Required Before Implementation

### Unit Tests (Session Model)

Required before P0-C-04B:
- `test_station_session_creation` — happy path
- `test_single_active_session_per_station` — constraint enforced
- `test_operator_identification_in_session` — operator linked to session
- `test_equipment_binding_in_session` — equipment linked (optional)
- `test_session_closure` — closes active session
- `test_tenant_isolation_session_queries` — cross-tenant rejected
- `test_session_expiration` — TTL enforcement if applicable

### Integration Tests (Session Lifecycle)

Required before P0-C-04B:
- `test_open_identify_bind_close_sequence` — full happy path
- `test_operator_identification_requires_valid_operator` — guard enforced
- `test_cannot_identify_same_operator_twice` — constraint
- `test_cannot_close_session_with_active_work` (TBD) — if design requires
- `test_reopen_restores_session_context` (TBD) — if applicable

### Soft Validation Tests (Execution Commands)

Required before P0-C-04C:
- `test_start_execution_with_valid_session` — logs success, proceeds
- `test_start_execution_without_session` — logs warning, still succeeds
- `test_start_execution_with_invalid_session` — logs error, still succeeds
- `test_execution_preserves_current_behavior_without_session` — no breaking changes

### Dual-Mode Queue Tests

Required before P0-C-04D:
- `test_station_queue_with_active_claim` — claim-based filtering works
- `test_station_queue_with_active_session` — session-based filtering works
- `test_station_queue_claim_and_session_equivalent` — both paths produce same result

### Regression Tests (All Phases)

Must pass throughout:
- `test_claim_single_active_per_operator.py` — claim behavior unchanged
- `test_release_claim_active_states.py` — claim release behavior unchanged
- `test_station_queue_active_states.py` — queue filtering unchanged
- `test_reopen_resumability_claim_continuity.py` — reopen continuity unchanged
- `test_close_reopen_operation_foundation.py` — close/reopen state machine unchanged
- `test_operation_detail_allowed_actions.py` — allowed actions unchanged
- Full backend test suite — all 159 passed, 1 skipped maintained

---

## 13. Stop Conditions

**DO NOT IMPLEMENT P0-C-04 if any of these occur:**

1. **Station Session Contract Not Stable**
   - If P0-C-04A reveals ambiguity in session model design
   - If design docs conflict on session semantics
   - Stop: Escalate to design review, resolve contract first

2. **Claim Tests Failing**
   - If any existing claim tests fail after P0-C-04B model introduction
   - Stop: Revert, isolate issue, fix before proceeding

3. **Backward Compat Broken**
   - If any execution command behavior changes unexpectedly
   - If FE integration tests fail due to API changes
   - Stop: Revert slice, refactor in isolation

4. **Full Suite Not Green**
   - If full backend test suite falls below 159 passed after any slice
   - Stop: Debug, fix, rerun before proceeding to next slice

5. **Session Validation Too Aggressive**
   - If soft validation (P0-C-04C) causes unexpected rejections
   - If claim+session dual ownership creates ambiguity
   - Stop: Revert to strictly soft validation, debug

6. **DB Migration Issues**
   - If schema migration fails
   - If existing data cannot be migrated
   - Stop: Rollback migration, redesign model

---

## 14. Verification Commands

**Before proceeding with implementation, run:**

```bash
# Verify current baseline
cd backend
.venv\Scripts\python -m pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py tests/test_reopen_resumability_claim_continuity.py tests/test_close_reopen_operation_foundation.py

# Expected: All pass (locked claim behavior)
# Exit code: 0

# Full suite baseline
.venv\Scripts\python -m pytest -q

# Expected: 159 passed, 1 skipped
# Exit code: 0
```

**After P0-C-04A (doc-only):**
- No code changes, no test runs required

**After P0-C-04B (session model):**
```bash
# New tests must pass
.venv\Scripts\python -m pytest -q tests/test_station_session_lifecycle.py

# Claim tests must still pass
.venv\Scripts\python -m pytest -q tests/test_claim_single_active_per_operator.py

# Full suite must not regress
.venv\Scripts\python -m pytest -q
# Expected: >= 159 passed (new tests added, claim tests preserved)
```

**After P0-C-04C (soft validation):**
```bash
# New tests must pass
.venv\Scripts\python -m pytest -q tests/test_operation_session_validation.py

# Full suite must not regress
.venv\Scripts\python -m pytest -q
# Expected: >= 159 + test_operation_session_validation.py passed
```

**After P0-C-04D (dual-mode queue):**
```bash
# New tests must pass
.venv\Scripts\python -m pytest -q tests/test_station_queue_dual_mode.py

# Full suite must not regress
.venv\Scripts\python -m pytest -q
```

**After P0-C-04E (deprecation docs):**
```bash
# Full suite must remain at baseline
.venv\Scripts\python -m pytest -q
# Expected: >= 159 passed, all claim tests green
```

---

## 15. Final Verdict

### Can Implementation Proceed?

**YES** — under these conditions:

1. ✓ Use Option B (Compatibility Bridge) strategy
2. ✓ Implement in sub-slices (A → B → C → D → E)
3. ✓ Keep claim code and tests unchanged through all slices
4. ✓ Add session model as parallel ownership concern
5. ✓ Use soft session validation initially (warnings, no rejections)
6. ✓ Maintain 159+ test pass rate
7. ✓ Document claim as compatibility debt, session as target
8. ✓ Do NOT remove claim code in P0-C-04
9. ✓ Do NOT break FE claim dependencies
10. ✓ Do NOT implement dispatch, APS, BOM, ERP

### Key Constraints for Implementer

- **MUST preserve claim behavior** — All claim tests must pass throughout
- **MUST NOT require session for execution** — Execution succeeds with or without session (soft check)
- **MUST maintain backward compat** — Existing APIs unchanged
- **MUST test-first** — Tests written before each code change
- **MUST document deprecation** — Mark claim as compatibility, session as target
- **MUST stop at first blocker** — Don't force through failing tests or breaking changes

### Risk Assessment

- **Technical Risk:** MEDIUM (new model + dual ownership, but isolation is good)
- **Breaking Risk:** LOW (compatibility bridge design minimizes breaking changes)
- **Test Risk:** LOW (claim tests preserved, new tests added)
- **Schedule Risk:** MEDIUM (5 sub-slices, each requires verification)

### Recommended Next Action

**Present this review to team/stakeholders for approval, then:**

1. Get sign-off on Option B (Compatibility Bridge) strategy
2. Confirm P0-C-04A contract scope with domain expert
3. Proceed with P0-C-04B model implementation (test-first)
4. Execute sub-slices B → C → D → E in sequence, with full regression verification after each

---

## 16. Appendix: Current Test Baseline (Verified)

**Date:** 2026-04-29 (After P0-C-03)
**Command:** `pytest -q`
**Result:** 159 passed, 1 skipped
**Exit Code:** 0

**Claim tests included in baseline:**
- test_claim_single_active_per_operator.py — ALL PASS
- test_release_claim_active_states.py — ALL PASS
- test_station_queue_active_states.py — ALL PASS
- test_reopen_resumability_claim_continuity.py — ALL PASS

**Execution tests included in baseline:**
- test_operation_detail_allowed_actions.py — ALL PASS
- test_close_reopen_operation_foundation.py — ALL PASS
- test_operation_status_projection_reconcile.py — ALL PASS (P0-C-03 added)
- test_status_projection_reconcile_command.py — ALL PASS (P0-C-03 added)

This baseline must be maintained or exceeded after each P0-C-04 sub-slice.

---

*End of P0-C-04 Station Session Ownership Alignment Review — PROPOSE-ONLY, no implementation changes made.*

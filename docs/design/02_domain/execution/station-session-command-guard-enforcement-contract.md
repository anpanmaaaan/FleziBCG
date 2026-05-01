# StationSession Command Guard Enforcement Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Defined StationSession-based command guard enforcement contract before replacing claim-based execution guard. |
| 2026-05-01 | v1.1 | Finalized P0-C-08B executable guard contract from P0-C-08 readiness evidence and current source boundaries. |

## 1. Purpose

This contract defines the enforcement semantics required before P0-C-08C can migrate execution command ownership from claim compatibility guardrails to StationSession ownership guardrails.

Non-negotiable scope for P0-C-08B:
- StationSession is target execution ownership context.
- Claim is compatibility layer / migration debt.
- P0-C-08B does not remove claim.
- P0-C-08B does not implement enforcement.
- P0-C-08B is the contract gate for P0-C-08C.

## 2. Current State Summary

Current source baseline:
- Execution commands have StationSession diagnostic integration (`_compute_session_diagnostic`) in service layer.
- Diagnostic remains non-blocking; command allow/deny does not branch on StationSession yet.
- Route-layer claim guard (`ensure_operation_claim_owned_by_identity`) remains active on 7 execution mutation endpoints.
- Claim still provides station queue ownership state and reopen continuity support.
- Full backend suite baseline remains green (255 passed, 1 skipped).

## 3. Target Enforcement Principle

Target principle:
- An execution command may proceed only when backend resolves a valid OPEN StationSession matching:
  - tenant_id
  - station_id (from operation.station_scope_value)
  - operator context expected by command

Boundary rules:
- Frontend cannot assert ownership truth.
- JWT identity alone is not sufficient ownership proof.
- Claim is not target ownership truth.
- StationSession guard must be backend-derived from authoritative runtime/context data.

## 4. Ownership Context Definitions

StationSession context (required):
- session_id
- tenant_id
- station_id
- operator_user_id
- status = OPEN

StationSession context (optional / policy):
- equipment_id
- current_operation_id

Command context source-of-truth:
- tenant_id: authenticated backend request identity
- station_id: backend operation.station_scope_value
- operator identity input:
  - start_operation, report_quantity: request.operator_id when present, else actor_user_id
  - pause_operation, resume_operation, start_downtime, end_downtime, complete_operation: actor_user_id
  - close_operation, reopen_operation: supervisor actor_user_id (role-gated)

Compatibility claim context:
- claim remains compatibility-only
- claim is not target guard
- claim may remain as secondary compatibility check during migration
- claim cannot override failed StationSession guard

## 5. Command Guard Applicability Matrix

| Command | Requires StationSession in Target? | Context Source | Enforce in P0-C-08C? | Claim Guard During Migration | Notes |
|---|---|---|---:|---|---|
| start_operation | YES | tenant + operation.station_scope_value + operator/actor | YES | KEEP temporary | Core execution write; high priority |
| pause_operation | YES | tenant + operation.station_scope_value + actor | YES | KEEP temporary | Core execution write |
| resume_operation | YES | tenant + operation.station_scope_value + actor | YES | KEEP temporary | Core execution write |
| report_quantity | YES | tenant + operation.station_scope_value + operator/actor | YES | KEEP temporary | Core execution write |
| start_downtime | YES | tenant + operation.station_scope_value + actor | YES | KEEP temporary | Core execution write |
| end_downtime | YES | tenant + operation.station_scope_value + actor | YES | KEEP temporary | Core execution write |
| complete_operation | YES | tenant + operation.station_scope_value + actor | YES | KEEP temporary | Core execution write |
| close_operation | EVENTUAL_YES (policy-dependent) | tenant + operation.station_scope_value + supervisor actor | NO (defer) | N/A (no claim guard today) | Supervisor closure action currently independent of claim |
| reopen_operation | EVENTUAL_YES (after continuity contract) | tenant + operation.station_scope_value + supervisor actor | NO (defer) | N/A (no claim guard today) | Defer until P0-C-08E continuity replacement |

P0-C-08C scope recommendation:
- Enforce first subset on 7 execution mutation commands currently claim-guarded.
- Exclude close/reopen from first enforcement subset to avoid unresolved continuity and supervisor-ownership semantic conflicts.

## 6. StationSession Validation Rules

Mandatory validation order for P0-C-08C guard implementation:
1. Load operation by operation_id.
2. Validate operation tenant matches request tenant context.
3. Resolve station_id from backend operation.station_scope_value.
4. Resolve command actor/operator context from authenticated backend identity and command payload.
5. Query active OPEN StationSession for tenant_id + station_id.
6. Validate session exists; else reject STATION_SESSION_REQUIRED.
7. Validate session.status == OPEN; else reject STATION_SESSION_CLOSED.
8. Validate session.tenant_id == operation.tenant_id; else reject STATION_SESSION_TENANT_MISMATCH.
9. Validate session.station_id == operation.station_scope_value; else reject STATION_SESSION_STATION_MISMATCH.
10. Validate session.operator_user_id matches expected command actor/operator; else reject STATION_SESSION_OPERATOR_MISMATCH.
11. Proceed to existing command state machine guards.

Guard-order decision:
- Tenant/resource existence guard must run first (avoid cross-tenant leakage).
- StationSession ownership guard runs before mutation/state transition checks.
- Preserve existing state guard semantics once ownership is valid.

## 7. Claim Compatibility Boundary

P0-C-08C compatibility contract:
- Claim is not removed.
- Claim route guards may remain temporarily.
- Claim cannot override failed StationSession guard.
- Claim must not be expanded.
- Claim audit logs remain.
- Claim queue behavior remains until P0-C-08D.
- `_restore_claim_continuity_for_reopen` remains until P0-C-08E.
- Claim tests remain green until replacement tests and migration gates are complete.

| Claim Function | Keep in P0-C-08C? | Reason | Future Removal Slice |
|---|---:|---|---|
| claim_operation | YES | Station queue and compatibility ownership still claim-based | P0-C-08H |
| release_operation_claim | YES | Compatibility release path still required | P0-C-08H |
| ensure_operation_claim_owned_by_identity | YES (temporary) | Existing route compatibility guard remains during staged migration | P0-C-08C->08F |
| get_station_queue | YES | Queue rewrite deferred | P0-C-08D/08H |
| get_operation_claim_status | YES | Claim API deprecation deferred | P0-C-08F/08H |
| _restore_claim_continuity_for_reopen | YES | Reopen continuity replacement deferred | P0-C-08E/08H |

## 8. Route Guard Migration Rules

Service-layer ownership validation is canonical target.
Route layer remains thin and delegates to service guard helper.

Transitional rule for 7 currently claim-guarded routes:
- Apply StationSession guard first (authoritative ownership).
- Keep existing claim guard as compatibility second check during transition.
- This avoids claim passing when session is invalid.

| Route / Endpoint | Current Guard | Target Guard | P0-C-08C Action | Compatibility Rule |
|---|---|---|---|---|
| POST /operations/{id}/start | claim guard | StationSession service guard | Add service guard path | Keep claim guard after session guard during transition |
| POST /operations/{id}/pause | claim guard | StationSession service guard | Add service guard path | Keep claim guard after session guard during transition |
| POST /operations/{id}/resume | claim guard | StationSession service guard | Add service guard path | Keep claim guard after session guard during transition |
| POST /operations/{id}/report-quantity | claim guard | StationSession service guard | Add service guard path | Keep claim guard after session guard during transition |
| POST /operations/{id}/start-downtime | claim guard | StationSession service guard | Add service guard path | Keep claim guard after session guard during transition |
| POST /operations/{id}/end-downtime | claim guard | StationSession service guard | Add service guard path | Keep claim guard after session guard during transition |
| POST /operations/{id}/complete | claim guard | StationSession service guard | Add service guard path | Keep claim guard after session guard during transition |
| POST /operations/{id}/close | role gate only | policy pending | No enforcement in 08C subset | Preserve existing SUP behavior |
| POST /operations/{id}/reopen | role gate only + claim continuity helper | policy pending | No enforcement in 08C subset | Preserve existing reopen behavior |

## 9. Error Contract

Error family for StationSession guard outcomes in P0-C-08C:

| Error Code | HTTP Status | Meaning | Example Trigger | Notes |
|---|---:|---|---|---|
| STATION_SESSION_REQUIRED | 409 | No active StationSession for tenant+station | command at station without open session | CANDIDATE_FOR_P0_C_08_STATION_SESSION_GUARD; NEEDS_ERROR_REGISTRY_FINALIZATION |
| STATION_SESSION_CLOSED | 409 | Session exists but not OPEN | closed session row selected or stale context | CANDIDATE_FOR_P0_C_08_STATION_SESSION_GUARD; NEEDS_ERROR_REGISTRY_FINALIZATION |
| STATION_SESSION_STATION_MISMATCH | 409 | Session station != operation station | wrong station context | CANDIDATE_FOR_P0_C_08_STATION_SESSION_GUARD; NEEDS_ERROR_REGISTRY_FINALIZATION |
| STATION_SESSION_OPERATOR_MISMATCH | 403 | Session operator does not match command actor/operator | actor differs from session operator | CANDIDATE_FOR_P0_C_08_STATION_SESSION_GUARD; NEEDS_ERROR_REGISTRY_FINALIZATION |
| STATION_SESSION_TENANT_MISMATCH | 404/403 | Session tenant conflict/cross-tenant safety | tenant mismatch | Do not leak cross-tenant existence; CANDIDATE_FOR_P0_C_08_STATION_SESSION_GUARD |
| STATION_SESSION_NOT_AUTHORIZED | 403 | Authenticated user cannot use station session context | missing scope/ownership rights | Optional alias if policy needs explicit auth distinction |

Registry status:
- No dedicated finalized error registry entry for these codes in current source/docs.
- Treat all as candidate codes pending registry finalization.

## 10. API Behavior Contract

P0-C-08C API behavior constraints:
- Success response bodies for execution commands remain unchanged.
- OperationDetail response shape remains unchanged.
- New failure path may return StationSession guard error code/status per Section 9.
- No diagnostic context field is exposed as permission truth.
- Frontend must continue treating backend response as sole authorization/ownership truth.

## 11. Event Impact

Event contract for P0-C-08C:
- StationSession guard enforcement emits no new execution domain event on guard failure.
- Failed guard must not append command execution events.
- Existing StationSession lifecycle events remain unchanged.
- Claim audit events remain unchanged during compatibility period.
- No event renames in P0-C-08C.

## 12. Projection / allowed_actions Impact

P0-C-08C constraints:
- Do not modify `_derive_status` logic.
- Do not modify `_derive_allowed_actions` semantics in P0-C-08C.
- Keep allowed_actions state-derived and backend-generated as today.
- Ownership-aware allowed_actions overlay is a future decision, not part of P0-C-08C.

## 13. Reopen / Resume Continuity Boundary

P0-C-08C boundaries:
- Must not remove `_restore_claim_continuity_for_reopen`.
- Must not rewrite reopen continuity semantics.
- Continuity replacement is delegated to P0-C-08E.

Decision for first enforcement subset:
- Reopen excluded from P0-C-08C enforcement.
- Close excluded from P0-C-08C enforcement due supervisor closure policy and no existing claim guard coupling.

Justification:
- Reopen has highest migration risk because continuity is currently claim-backed.
- Enforcing reopen before continuity contract risks regressions in resumability and conflict semantics.

## 14. Station Queue Boundary

Queue boundary for P0-C-08C:
- Do not rewrite station queue.
- Session-aware queue migration belongs to P0-C-08D.
- Claim-based queue fields may remain temporarily.
- Avoid dual authoritative ownership display by preserving current queue contract until explicit queue migration slice.

## 15. Test Matrix for P0-C-08C

Required tests before/for P0-C-08C implementation:

StationSession required tests (per enforced command):
- reject when no OPEN StationSession exists
- reject when StationSession is CLOSED
- reject on station mismatch
- reject on operator mismatch
- reject on tenant mismatch
- succeed with matching OPEN StationSession

Per-command tests for enforcement scope (7 commands):
- no session rejected
- matching session succeeds
- existing state guard behavior unchanged
- command event emitted only on success
- failed guard emits no command event

Compatibility tests:
- claim regression suites remain green
- transitional route claim guard behavior remains compatible
- command hardening suites updated for StationSession required behavior only in scope
- StationSession lifecycle + diagnostic suites remain green
- reopen continuity suites remain green (reopen excluded from enforcement subset)

Full regression:
- full backend suite sequential run with explicit summary + exit code captured

## 16. Implementation Rules for P0-C-08C

Implementation guardrails:
- smallest possible implementation scope
- add one service-level helper (example): ensure_open_station_session_for_command(...)
- helper must be backend-derived only
- no frontend input promoted to ownership truth
- no claim removal
- no queue rewrite
- no reopen continuity rewrite
- no schema migration unless explicitly approved in separate slice
- no API shape changes for success responses

## 17. Stop Conditions

Stop P0-C-08C implementation immediately if:
1. Guard requires frontend-provided ownership truth.
2. Guard semantics conflict with transitional claim guard ordering.
3. Reopen continuity semantics become ambiguous.
4. Queue ownership semantics become ambiguous.
5. Test changes require broad unrelated rewrites.
6. API error contract cannot be aligned or candidate-coded safely.
7. Full suite fails with real regression caused by guard migration.

## 18. Final Contract Verdict

READY_FOR_P0_C_08C_SUBSET_IMPLEMENTATION

Scope for this verdict:
- Proceed with P0-C-08C subset enforcement on 7 currently claim-guarded execution mutation endpoints.
- Defer close/reopen enforcement to later slice after continuity and policy contracts are explicit.

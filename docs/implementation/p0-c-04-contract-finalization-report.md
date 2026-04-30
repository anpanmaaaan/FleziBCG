# P0-C-04A Contract Finalization Report

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial P0-C-04A finalization report. DOC-ONLY, PROPOSE-ONLY. |
| 2026-04-29 | v1.1 | P0-C-04B lifecycle implementation execution aligned to this contract (model/repository/service/routes/migration/tests). |

## Routing
- Selected brain: MOM Brain
- Selected mode: Architecture
- Hard Mode MOM: v3
- Reason: Station/session ownership contract touches execution governance, ownership invariants, and migration safety gates.

## Hard Mode MOM v3 Gate

## Verdict before coding
ALLOW_IMPLEMENTATION

## Reason
Design evidence across canonical execution v4 docs is sufficient to finalize P0-C-04A contract and define safe boundaries for P0-C-04B onward. This slice is documentation only and does not modify runtime behavior.

## Design Evidence Extract

### Source docs read

| Doc | Why used |
|---|---|
| .github/copilot-instructions.md | Required routing and Hard Mode policy enforcement |
| .github/agent/AGENT.md | Caution/surgical execution principles |
| docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md | Brain/mode routing and required output format |
| docs/ai-skills/hard-mode-mom-v3/SKILL.md | Mandatory v3 gate structure |
| docs/design/INDEX.md | Authoritative reading order |
| docs/design/AUTHORITATIVE_FILE_MAP.md | Execution truth mapping |
| docs/governance/CODING_RULES.md | Backend truth, event/projection invariants, service boundaries |
| docs/governance/ENGINEERING_DECISIONS.md | Claim deprecation and session-owned target confirmation |
| docs/governance/SOURCE_STRUCTURE.md | API/backend folder boundary context |
| docs/implementation/p0-c-execution-entry-audit.md | P0-C entry baseline, risks, stop conditions |
| docs/implementation/p0-c-04-station-session-ownership-alignment-review.md | Gap analysis and option recommendation baseline |
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | Session/context + execution transition truth |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | Command/event target contract |
| docs/design/02_domain/execution/station-execution-policy-and-master-data-v4.md | Session-required and claim-deprecated policy truths |
| docs/design/02_domain/execution/station-execution-exception-and-approval-matrix-v4.md | Exception alignment constraints |
| docs/design/02_domain/execution/execution-state-machine.md | Runtime/closure shell rules and event requirement |

### Commands/actions found

| Command/Action | Domain | Source doc | Evidence |
|---|---|---|---|
| open_station_session | Station session ownership | station-execution-state-matrix-v4.md | Session transition SS-OPEN-001 |
| identify_operator | Station session ownership | station-execution-state-matrix-v4.md | Session transition OP-ID-001 |
| bind_equipment | Station session ownership | station-execution-state-matrix-v4.md | Session transition EQ-BIND-001 |
| close_station_session | Station session ownership | station-execution-state-matrix-v4.md | Session transition SS-CLOSE-001 |
| start_execution | Execution | station-execution-state-matrix-v4.md | START-001 requires valid session context |
| pause_execution | Execution | station-execution-state-matrix-v4.md | PAUSE-001 requires valid ownership session |
| resume_execution | Execution | station-execution-state-matrix-v4.md | RESUME-001 requires valid session |
| report_production | Execution | station-execution-state-matrix-v4.md | PROD-REP-001 requires valid session |
| start_downtime/end_downtime | Execution | station-execution-state-matrix-v4.md | DT-START/DT-END require valid session |
| complete_execution | Execution | station-execution-state-matrix-v4.md | COMPLETE-001 requires valid session |
| close_operation/reopen_operation | Closure | station-execution-state-matrix-v4.md | CLOSE-001 / REOPEN-001 |

### Events found

| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| station_session_opened | open_station_session | station-execution-command-event-contracts-v4.md | Canonical event intent |
| operator_identified_at_station | identify_operator | station-execution-command-event-contracts-v4.md | Canonical event intent |
| equipment_bound_to_station_session | bind_equipment | station-execution-command-event-contracts-v4.md | Canonical event intent |
| station_session_closed | close_station_session | station-execution-command-event-contracts-v4.md | Canonical event intent |

### States found

| State | Entity | Source doc | Evidence |
|---|---|---|---|
| PLANNED, IN_PROGRESS, PAUSED, BLOCKED, COMPLETED, ABORTED | Runtime execution | station-execution-state-matrix-v4.md | Runtime status carrier |
| OPEN, CLOSED | Closure | station-execution-state-matrix-v4.md | Orthogonal closure dimension |
| active session / no active session | Session context | station-execution-state-matrix-v4.md | Session transition matrix |

### Invariants found

| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| Closed records reject execution writes | state machine | station-execution-state-matrix-v4.md | INV-001 |
| One running execution per station/resource context | station/session | station-execution-state-matrix-v4.md | INV-002 |
| Open downtime blocks resume and completion | state machine | station-execution-state-matrix-v4.md | INV-003 |
| Active execution mutation requires valid station session context | session | station-execution-state-matrix-v4.md | INV-004 |
| Backend is source of truth | governance | CODING_RULES.md | Principle 2.1 |
| Claim deprecated from target model | migration/ownership | station-execution-command-event-contracts-v4.md | Transition note |

### Explicit exclusions

| Exclusion | Source doc | Reason |
|---|---|---|
| No claim removal in this slice | p0-c-04-station-session-ownership-alignment-review.md | Compatibility bridge recommendation |
| No command behavior change in this slice | p0-c-04-station-session-ownership-alignment-review.md | DOC-ONLY boundary |
| Exception/disposition lifecycle implementation deferred | station-execution-exception-and-approval-matrix-v4.md | Deferred feature |

## Auto-generated Event Map

| Command/Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| open_station_session | STATION_SESSION.OPENED | domain_event | session_id, tenant_id, station_id, actor_user_id, opened_at | session ownership projection (future) | station-execution-state-matrix-v4.md |
| identify_operator_at_station | STATION_SESSION.OPERATOR_IDENTIFIED | domain_event | session_id, tenant_id, station_id, operator_user_id, occurred_at | session operator context projection (future) | station-execution-state-matrix-v4.md |
| bind_equipment_to_station_session | STATION_SESSION.EQUIPMENT_BOUND | domain_event | session_id, tenant_id, station_id, equipment_id, occurred_at | session equipment projection (future) | station-execution-state-matrix-v4.md |
| close_station_session | STATION_SESSION.CLOSED | domain_event | session_id, tenant_id, station_id, actor_user_id, closed_at | session active-context projection (future) | station-execution-state-matrix-v4.md |

Event status for this slice (finalized in P0-C-04B hardening):
- CANONICAL_FOR_P0_C_STATION_SESSION

## Auto-generated Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| Tenant isolation on station session operations | tenant | route + service + repository | Yes | Yes | CODING_RULES.md, state-matrix-v4 |
| Station scope isolation | scope | service + repository | Yes | Yes | p0-c entry audit, state-matrix-v4 |
| Single active session per station | station/session | service + DB uniqueness strategy | Yes | Yes | state-matrix-v4 INV-004 context |
| Explicit operator context per session | operator/session | service validation | Optional | Yes | state-matrix-v4 OP-ID-001 |
| Closed session rejects new ownership mutations | state_machine | service validation | No | Yes | state-matrix-v4 SS-CLOSE-001 |
| Claim/session cannot be dual authoritative truth | projection_consistency | service contract boundary | No | Yes | p0-c-04 alignment review |
| No command rejection behavior change in 04A/04B | migration_boundary | implementation gate | No | Yes | user slice constraints + alignment review |

## Auto-generated State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| StationSession | no active session | open_station_session | Yes | STATION_SESSION.OPENED (candidate) | active session | duplicate open rejected | state-matrix-v4 SS-OPEN-001 |
| StationSession | active without operator | identify_operator_at_station | Yes | STATION_SESSION.OPERATOR_IDENTIFIED (candidate) | active with operator | invalid/inactive operator rejected | state-matrix-v4 OP-ID-001 |
| StationSession | active session | bind_equipment_to_station_session | Yes (policy optional) | STATION_SESSION.EQUIPMENT_BOUND (candidate) | active with equipment | out-of-scope equipment rejected | state-matrix-v4 EQ-BIND-001 |
| StationSession | active session | close_station_session | Yes | STATION_SESSION.CLOSED (candidate) | no active session | close with orphaned running work rejected | state-matrix-v4 SS-CLOSE-001 |

## Auto-generated Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion | Source |
|---|---|---|---|---|---|---|---|---|
| SS-TEST-001 | Open session happy path | happy_path | authorized actor, no active session | open session | session OPEN | OPENED emitted (candidate) | single active context established | state-matrix-v4 |
| SS-TEST-002 | Single active per station | db_invariant | one active session exists | open second session | reject | no new lifecycle event | one active station session invariant | state-matrix-v4 |
| SS-TEST-003 | Tenant mismatch rejected | wrong_tenant | actor tenant A, station tenant B | open/identify/bind/close | reject | no lifecycle event | tenant isolation | CODING_RULES + state-matrix-v4 |
| SS-TEST-004 | Station mismatch rejected | wrong_scope | session station A | mutate as station B context | reject | no lifecycle event | station scope isolation | p0-c entry audit |
| SS-TEST-005 | Identify operator | happy_path | active session without operator | identify operator | operator context set | OPERATOR_IDENTIFIED emitted | explicit operator context | state-matrix-v4 |
| SS-TEST-006 | Close session | happy_path | active session | close | status CLOSED | CLOSED emitted | closed session transition | state-matrix-v4 |
| SS-TEST-007 | Closed session cannot be used | invalid_state | CLOSED session | execute ownership mutation | reject | no mutation event | closed sessions non-active | state-matrix-v4 |
| SS-TEST-008 | Claim suite remains green | regression | existing claim tests | run claim tests | unchanged pass | none required | compatibility boundary preserved | p0-c alignment review |
| SS-TEST-009 | No command behavior change in 04B | regression | existing execution commands | run existing command tests | behavior unchanged | none required | migration gate honored | user constraints |
| SS-TEST-010 | Diagnostic bridge does not reject yet | regression | missing session context in compatibility path | run command path | no hard reject in bridge slice | diagnostic only | no premature behavior change | p0-c alignment review |
| SS-TEST-011 | Lifecycle event emission | event_payload | lifecycle command success | inspect event payload | required fields present | event payload complete | append-only lifecycle facts | contracts-v4 |

## API Surface Proposal (Propose Only)

Candidate routes:
- POST /station-sessions
- GET /station-sessions/current
- POST /station-sessions/{session_id}/identify-operator
- POST /station-sessions/{session_id}/bind-equipment
- POST /station-sessions/{session_id}/close

Namespace recommendation:
- Prefer /station/sessions over /station-sessions

Reason:
- Existing station bounded workflows already group under /station/*.
- Station session ownership is a station-execution concern and aligns with current route topology.
- Reduces surface fragmentation and improves discoverability for station UI clients.

## Claim Compatibility Decision

Decision: KEEP claim as compatibility layer for P0-C-04A through P0-C-04D.

Rules affirmed:
- claim is migration debt, not target truth
- do not remove claim in P0-C-04A
- do not expand claim scope
- do not create dual authoritative ownership
- do not regress existing claim tests

## Stop Conditions

Stop future implementation if:
1. claim tests fail
2. session introduces dual ownership ambiguity
3. command behavior changes without explicit approval
4. station/session event contract remains unclear
5. migration requires unspecified data transformation
6. frontend becomes ownership truth

## Final Verdict

READY_FOR_P0_C_04B_MODEL_IMPLEMENTATION

## Deliverables Produced

- docs/design/02_domain/execution/station-session-ownership-contract.md
- docs/implementation/p0-c-04-contract-finalization-report.md

## Verification Plan

Run audit-safe tests:

cd backend
.venv\Scripts\python -m pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py tests/test_reopen_resumability_claim_continuity.py tests/test_close_reopen_operation_foundation.py

Then run full backend suite:

.venv\Scripts\python -m pytest -q

Result capture fields to fill after run:
- audit-safe suite exit code: 0
- audit-safe suite summary: 36 passed in 11.31s
- full backend suite exit code: 0
- full backend suite summary: 168 passed, 1 skipped in 21.98s

## Verification Results (Executed)

Audit-safe command executed:
- cd backend
- .venv\\Scripts\\python -m pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py tests/test_reopen_resumability_claim_continuity.py tests/test_close_reopen_operation_foundation.py

Observed output:
- 36 passed in 11.31s
- exit code: 0

Full backend suite command executed:
- Set-Location "g:\\Work\\FleziBCG\\backend"; ..\\.venv\\Scripts\\python -m pytest -q

Observed output:
- 168 passed, 1 skipped in 21.98s
- exit code: 0

## P0-C-04B Handoff Status

Contract application result:
- StationSession aggregate implemented with required contract fields.
- Lifecycle commands implemented: open, identify operator, bind equipment, close.
- Event names implemented and promoted to CANONICAL_FOR_P0_C_STATION_SESSION in P0-C-04B hardening.
- API surface implemented under `/station/sessions`.
- Claim compatibility boundary preserved (no claim removal/refactor).
- Execution command behavior unchanged in this slice.

P0-C-04B readiness verdict:
- PRODUCTION_READY_FOR_FOUNDATION_SCOPE
- Event registry finalized: CANONICAL_FOR_P0_C_STATION_SESSION.
- Recommended next: P0-C-04C diagnostic session context bridge.

---

## P0-C-04C: Diagnostic Session Context Bridge

Slice purpose: Implement a non-blocking, read-only diagnostic helper that detects whether an OPEN StationSession exists for tenant/station context. Missing session is a diagnostic signal only — never a command rejection.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

### Files introduced
- `backend/app/services/station_session_diagnostic.py` — `get_station_session_diagnostic()` + `StationSessionDiagnostic` + `SessionReadiness`
- `backend/tests/test_station_session_diagnostic_bridge.py` — 7 test-first tests

### Behavior contract confirmed
- `get_station_session_diagnostic(db, tenant_id=..., station_id=...)` always returns `StationSessionDiagnostic`; never raises
- `SessionReadiness.OPEN` — active OPEN session found
- `SessionReadiness.NO_ACTIVE_SESSION` — no session, CLOSED session, or different tenant
- CLOSED sessions are transparent (repository returns OPEN-only via partial index)
- Tenant isolation: every lookup filtered by tenant_id
- Execution command `start_operation` (and all others) behavior unchanged — no injection into command path in this slice

### Invariant confirmations
- No new domain events emitted
- No claim model/service changes
- No execution command guard changes
- No schema migration

### Verification summary
- Diagnostic bridge tests: 7 passed
- Station session lifecycle regression: 9 passed
- Claim regression subset: 45 passed
- Full backend suite: 175 passed, 1 skipped, exit 0

### P0-C-04C readiness verdict
- COMPLETE — Non-blocking diagnostic bridge operational and production-ready
- Recommended next: P0-C-04D (command context guard alignment — execution commands begin requiring valid StationSession)

---

## P0-C-04D: Command Context Diagnostic Integration / Guard Readiness

Slice purpose: Wire the diagnostic helper into all 9 execution command service functions so the backend can observe StationSession readiness during command execution, without changing command allow/deny behavior.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

### Integration design

A private helper `_compute_session_diagnostic(db, operation, tenant_id)` calls `get_station_session_diagnostic` using the verified tenant_id and the server-side `operation.station_scope_value`. This helper is called in each command after the tenant guard passes. The result is stored as `_session_ctx` — a local variable that is informational only and never used in any conditional in this slice.

All 9 commands wired:
- `start_operation`, `report_quantity`, `complete_operation`
- `pause_operation`, `resume_operation`
- `start_downtime`, `end_downtime`
- `close_operation`, `reopen_operation`

### Behavior contract confirmed
- All existing command outcomes unchanged
- OperationDetail API response shape unchanged
- Diagnostic is backend-derived (station_scope_value from server-side operation object)
- Tenant isolation guaranteed (tenant_id is verified before diagnostic lookup)
- Integration point is now in place for P0-C-04E (hard enforcement: missing session → reject)

### Invariant confirmations
- No new domain events emitted
- No claim model/service changes
- No execution command guard changes
- No schema migration

### Files changed
- `backend/app/services/operation_service.py` — import `get_station_session_diagnostic` + `_compute_session_diagnostic` helper + 9 invocations

### Files introduced
- `backend/tests/test_station_session_command_context_diagnostic.py` — 9 test-first tests

### Verification summary
- Command context diagnostic tests: 9 passed
- Diagnostic bridge tests: 7 passed (unchanged)
- Session lifecycle + claim regression: 86 passed
- Full backend suite: 184 passed, 1 skipped, exit 0

### P0-C-04D readiness verdict
- COMPLETE — Diagnostic integration operational in all 9 execution commands
- Recommended next: P0-C-04E (Claim compatibility / deprecation lock — wire session as required guard, deprecate claim as execution context)
- Recommended next: P0-C-04E (Claim compatibility / deprecation lock — wire session as required guard, deprecate claim as execution context)

---

## P0-C-04E: Claim Compatibility / Deprecation Lock

Slice purpose: Codify the compatibility boundary for the OperationClaim migration debt layer. Lock claim behavior, document the source map, establish the migration debt register, and confirm that the diagnostic bridge does not interfere with the claim lifecycle.

Hard Mode MOM v3 verdict: ALLOW_IMPLEMENTATION

### Scope
- DOC-ONLY slice. No production code changes.
- Compatibility lock document: `docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md`
- 8 non-negotiable boundary invariants codified.
- Claim source map: `ensure_operation_claim_owned_by_identity` called at 8 route-layer guard sites in `operations.py`.
- Diagnostic bridge non-interference contract confirmed: `_compute_session_diagnostic` / `_session_ctx` never touches claim lifecycle.
- Test compatibility lock: 45 claim tests + 16 session/diagnostic bridge tests + 9 command context tests = 70 total lock tests.
- Migration debt register created.
- Next-slice pre-conditions documented.

### Compatibility boundary (8 non-negotiables)
1. OperationClaim model must not be modified in this slice.
2. `station_claim_service.py` must not be modified in this slice.
3. `ensure_operation_claim_owned_by_identity` must remain the sole route-layer execution guard.
4. All 8 route guard call-sites must remain unchanged.
5. Claim test suite (≥36 tests) must remain green.
6. Claim must not be expanded in any subsequent slice without an explicit contract revision and ADR.
7. Claim must not be removed without an explicit migration plan and ADR entry.
8. Diagnostic bridge must not influence claim lifecycle in any way.

### Invariant confirmations
- OperationClaim model/service/tests unchanged.
- Execution command behavior unchanged.
- OperationDetail API response shape unchanged.
- No new domain events emitted.
- No schema migration.

### Verification summary
- Claim suite (isolation run): 36 passed, exit code 0
- Full backend suite: 184 passed, 1 skipped, exit code 0

### P0-C-04E readiness verdict
- COMPLETE — Claim compatibility boundary locked; migration debt register established
- Recommended next: P0-C-05 (Start / Pause / Resume Command Hardening)

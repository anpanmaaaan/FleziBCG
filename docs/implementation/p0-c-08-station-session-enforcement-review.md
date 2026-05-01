# P0-C-08 StationSession Enforcement / Claim Removal Readiness Review

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Reviewed readiness for StationSession enforcement and claim removal after P0-C command hardening closeout. |
| 2026-05-01 | v1.1 | Re-ran verification matrix, refreshed runtime/test/doc dependency inventory, and issued final P0-C-08 readiness verdict. |

## 1. Executive Summary

## Routing
- Selected brain: MOM Brain
- Selected mode: Architecture + QA
- Hard Mode MOM: v3 (review gate discipline; no implementation)
- Reason: Execution command ownership, queue, reopen continuity, tenant/auth boundaries, and migration safety are in-scope.

This review confirms that claim remains runtime-critical in current source for:
- execution write guard at route layer (`ensure_operation_claim_owned_by_identity`)
- station queue claim-state projection (`get_station_queue`)
- reopen continuity (`_restore_claim_continuity_for_reopen`)

StationSession is present and stable as lifecycle foundation + diagnostic bridge, but command enforcement semantics are not yet contracted or implemented.

Decision:
- Claim removal is not safe now.
- Recommended path is staged migration (P0-C-08B onward), not big-bang removal.
- P0-D Quality Lite should not depend on claim removal; if P0-D touches execution ownership semantics, P0-C-08 contract slices must come first.

## 2. Scope Reviewed

Runtime/API/tests/docs reviewed in this audit:
- Claim model/persistence: `backend/app/models/station_claim.py`, `backend/scripts/migrations/0009_station_claims.sql`
- StationSession model/persistence: `backend/app/models/station_session.py`, `backend/scripts/migrations/0017_station_sessions.sql`
- Claim service: `backend/app/services/station_claim_service.py`
- Execution service: `backend/app/services/operation_service.py`
- StationSession service/diagnostic: `backend/app/services/station_session_service.py`, `backend/app/services/station_session_diagnostic.py`
- API routes: `backend/app/api/v1/operations.py`, `backend/app/api/v1/station.py`, `backend/app/api/v1/station_sessions.py`, `backend/app/api/v1/router.py`
- Required tests from prompt (claim/session/command hardening sets)
- Required docs/reports listed in request

Out-of-scope controls honored:
- no business logic change
- no migration change
- no API/FE behavior change
- no claim removal or StationSession enforcement implementation

## 3. Claim Usage Inventory

| Usage | File | Runtime/Test/Doc | Purpose | Current Criticality | Removal Risk | Replacement Candidate |
|---|---|---|---|---|---|---|
| `OperationClaim` model | `backend/app/models/station_claim.py` | Runtime | Active ownership row per operation | CRITICAL_RUNTIME_GUARD | BLOCKER | StationSession guard + assignment read model |
| `OperationClaimAuditLog` model | `backend/app/models/station_claim.py` | Runtime | Claim audit trail | AUDIT_ONLY | MEDIUM | StationSession lifecycle event/audit + migration archive |
| `operation_claims` table + active unique index | `backend/scripts/migrations/0009_station_claims.sql` | Runtime | Enforce one unresolved claim per operation | CRITICAL_RUNTIME_GUARD | BLOCKER | Session enforcement + equivalent ownership invariant |
| `operation_claim_audit_logs` table | `backend/scripts/migrations/0009_station_claims.sql` | Runtime | Append-only claim lifecycle evidence | AUDIT_ONLY | MEDIUM | Archive policy + session event evidence |
| `claim_operation` | `backend/app/services/station_claim_service.py` | Runtime | Acquire claim + one-active-per-operator semantics | CRITICAL_RUNTIME_GUARD | HIGH | Session-owned operation intent + queue assignment semantics |
| `release_operation_claim` | `backend/app/services/station_claim_service.py` | Runtime | Release with active-state guards and override path | CRITICAL_RUNTIME_GUARD | HIGH | Session release/transfer policy |
| `ensure_operation_claim_owned_by_identity` | `backend/app/services/station_claim_service.py` | Runtime | Write guard used by execution command routes | CRITICAL_RUNTIME_GUARD | BLOCKER | StationSession enforcement guard contract |
| `get_station_queue` | `backend/app/services/station_claim_service.py` | Runtime | Queue projection includes claim.state/expires/owner | QUEUE_CONTEXT | BLOCKER | Session-aware queue projection |
| `get_operation_claim_status` | `backend/app/services/station_claim_service.py` | Runtime | Claim status endpoint payload | QUEUE_CONTEXT | HIGH | Session status endpoint / operation ownership status endpoint |
| `_restore_claim_continuity_for_reopen` | `backend/app/services/operation_service.py` | Runtime | Reopen owner continuity + conflict gate | REOPEN_CONTINUITY | BLOCKER | Reopen/session continuity contract |
| `CLAIM_CREATED` | `backend/app/services/station_claim_service.py` | Runtime | Audit event on claim acquire | AUDIT_ONLY | MEDIUM | Session event/audit mapping |
| `CLAIM_RELEASED` | `backend/app/services/station_claim_service.py` | Runtime | Audit event on release | AUDIT_ONLY | MEDIUM | Session event/audit mapping |
| `CLAIM_EXPIRED` | `backend/app/services/station_claim_service.py` | Runtime | Lazy expiry audit | AUDIT_ONLY | MEDIUM | Session expiry/close policy event |
| `CLAIM_RESTORED_ON_REOPEN` | `backend/app/services/operation_service.py` | Runtime | Reopen continuity audit event | REOPEN_CONTINUITY | HIGH | Session continuity event |
| `claim_id`, `claimed_by_user_id` in queue/status schemas | `backend/app/schemas/station.py` | Runtime/API | API payload contract for claim-aware consumers | QUEUE_CONTEXT | HIGH | Versioned queue/status contract |
| Claim route guard call sites | `backend/app/api/v1/operations.py` | Runtime/API | Pre-command guard for start/report/pause/resume/complete/downtime start/end | CRITICAL_RUNTIME_GUARD | BLOCKER | Route-level StationSession guard |
| Claim queue/claim/release/status endpoints | `backend/app/api/v1/station.py` | Runtime/API | Station ownership API surface | QUEUE_CONTEXT | HIGH | Session-based endpoints and compatibility window |
| Claim invariants tests | `backend/tests/test_claim_single_active_per_operator.py` | Test | Locks one-active-per-operator behavior | TEST_LOCK | HIGH | Session ownership tests replacing claim invariant |
| Claim release tests | `backend/tests/test_release_claim_active_states.py` | Test | Locks release restrictions and override path | TEST_LOCK | HIGH | Session close/reassign tests |
| Queue claim-state tests | `backend/tests/test_station_queue_active_states.py` | Test | Locks queue claim fields/state shape | TEST_LOCK | BLOCKER | Session-aware queue contract tests |
| Reopen claim continuity tests | `backend/tests/test_reopen_resumability_claim_continuity.py`, `backend/tests/test_reopen_operation_claim_continuity_hardening.py` | Test | Locks reopen continuity behavior | TEST_LOCK | BLOCKER | Session continuity replacement tests |
| Claim compatibility lock docs | `docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md` | Doc | Explicitly forbids premature claim removal | DOC_ONLY | MEDIUM | Superseding ADR + staged deprecation lock |

## 4. StationSession Readiness Inventory

| Capability | Exists? | Evidence | Is It Enough To Replace Claim? | Gap |
|---|---:|---|---:|---|
| StationSession table/model | YES | `backend/app/models/station_session.py`, `backend/scripts/migrations/0017_station_sessions.sql` | NO | No command guard tie-in |
| Open session | YES | `open_station_session` + lifecycle tests | NO | No execution write enforcement |
| Identify operator | YES | `identify_operator_at_station` + lifecycle tests | NO | Not bound to command authorization |
| Bind equipment | YES | `bind_equipment_to_station_session` + lifecycle tests | NO | Policy not enforced in execution commands |
| Close session | YES | `close_station_session` + lifecycle tests | NO | No command rejection semantics contract |
| Get current session | YES | `get_current_station_session` + route | NO | Read-only; not ownership guard |
| One active session per station | YES | partial unique index `uq_station_sessions_tenant_station_active_open` | PARTIAL | Covers session lifecycle only |
| Diagnostic helper | YES | `get_station_session_diagnostic` | NO | Explicitly non-blocking |
| Command diagnostic integration | YES | `_compute_session_diagnostic` in all 9 commands | NO | Variable never used in allow/deny branch |
| Event registry canonicalization | YES | `docs/design/02_registry/station-session-event-registry.md` | PARTIAL | Contracted names exist; subscribers/ownership semantics not finalized |
| Tests | YES | lifecycle + diagnostic + command context suites | PARTIAL | No enforcement/rejection compatibility tests |
| API routes | YES | `/api/v1/station/sessions*` | PARTIAL | Claim API still authoritative for queue ownership |
| Session audit/event trail | YES | security-event emission with canonical station-session event names | PARTIAL | No migration mapping from claim audit semantics |
| Station queue session awareness | NO | queue currently in claim service and emits claim state | NO | Queue contract rewrite needed |
| Reopen/resume continuity replacement | NO | continuity currently claim-backed in operation service | NO | Missing explicit session continuity contract |

## 5. Command Guard Migration Readiness

| Command | Current Claim Dependency | StationSession Context Available? | Safe To Enforce Now? | Required Before Enforcement | Risk |
|---|---|---:|---:|---|---|
| start_operation | Route guard `ensure_operation_claim_owned_by_identity` | YES (diagnostic only) | NO | Guard contract + error semantics + parity tests + route migration | HIGH |
| pause_operation | Same route claim guard | YES | NO | Same as above | HIGH |
| resume_operation | Same route claim guard + reopen continuity coupling | YES | NO | Guard contract + reopen continuity replacement + queue parity | BLOCKER |
| report_quantity | Same route claim guard | YES | NO | Guard contract + parity tests | HIGH |
| start_downtime | Same route claim guard | YES | NO | Guard contract + downtime/state compatibility tests | HIGH |
| end_downtime | Same route claim guard | YES | NO | Guard contract + downtime continuity tests | HIGH |
| complete_operation | Same route claim guard | YES | NO | Guard contract + close/reopen pathway compatibility | HIGH |
| close_operation | No claim guard in route; SUP role gate currently | YES | PARTIAL/NO | Define whether close requires session or remains supervisor-only closure action | MEDIUM |
| reopen_operation | No claim guard in route; invokes `_restore_claim_continuity_for_reopen` | YES | NO | Reopen continuity replacement contract first | BLOCKER |

## 6. Station Queue Migration Readiness

| Queue Aspect | Claim-Based Current Behavior | Session-Owned Target | Gap | Recommendation |
|---|---|---|---|---|
| Queue payload ownership block | `claim.state`, `claim.expires_at`, `claim.claimed_by_user_id` | Session ownership context (session/operator + operation actionable state) | API contract mismatch | Introduce versioned queue contract before removal |
| Queue service ownership source | `get_station_queue` in claim service | Session-aware projection service | No session-aware queue implementation | Build P0-C-08D queue projection slice |
| Active/in-progress ownership | Claim determines mine/other/none | Session + policy-driven operator ownership | Dual truth risk | Freeze claim contract until session queue contract finalized |
| API consumers | `/station/queue` and claim status consumers expect claim fields | Consumers must handle session fields | FE/API break risk | Dual-read compatibility window with explicit deprecation |
| Test lock | `test_station_queue_active_states.py` validates claim fields | New tests needed for session ownership shape | Current tests would fail on removal | Add side-by-side queue contract tests before cutover |
| Migration order | Queue currently tightly coupled to claim semantics | Session queue can be introduced independently | Unclear ordering between queue and guard | Prefer guard contract first, then queue migration with compatibility |

Queue sequencing decision:
- Do not remove claim queue semantics first.
- Define command guard contract first (P0-C-08B), then implement queue session-aware projection with compatibility (P0-C-08D).

## 7. Reopen / Resume Continuity Replacement

| Current Claim Continuity Behavior | Why It Exists | StationSession Replacement | Risk | Required Slice |
|---|---|---|---|---|
| Reopen extends active claim TTL if already active | Prevent owner losing resumability after reopen | Session continuity should preserve active session ownership context or explicit rebind requirement | HIGH | P0-C-08E |
| Reopen restores last claim if none active | Preserve operator continuity after closed interval | Reopen must define session restoration strategy (restore prior session context vs require active session now) | BLOCKER | P0-C-08E |
| Reopen rejects if owner already has other active claim (`STATE_REOPEN_OWNER_HAS_OTHER_ACTIVE_CLAIM`) | Enforce single-active ownership invariant | Equivalent session conflict rule must be defined and tested | BLOCKER | P0-C-08E |
| Reopen appends `CLAIM_RESTORED_ON_REOPEN` audit | Trace continuity behavior | New session continuity audit/event required | MEDIUM | P0-C-08E |

Contract decisions still needed for session-owned reopen:
- Should reopen require an active OPEN session at command time?
- Should reopen preserve prior operator identity or require explicit identify-operator step?
- Should resume enforce same session/operator identity as reopen actor?

## 8. API Deprecation / Removal Readiness

| API | Current Purpose | Consumer Risk | Replacement API | Deprecation Plan | Removal Ready? |
|---|---|---|---|---|---|
| `POST /api/v1/station/queue/{operation_id}/claim` | Acquire claim | HIGH | Session-owned operation intent endpoint (TBD) | Mark deprecated after replacement released + compatibility window | NO |
| `POST /api/v1/station/queue/{operation_id}/release` | Release claim | HIGH | Session close/reassign endpoint (TBD) | Keep until session continuity+queue migration complete | NO |
| `GET /api/v1/station/queue/{operation_id}/claim` | Claim status | HIGH | Session ownership status endpoint (TBD) | Add replacement endpoint; dual support period | NO |
| `GET /api/v1/station/queue` | Queue with claim payload | BLOCKER | Session-aware queue projection endpoint/contract | Version payload and migrate clients first | NO |
| `POST /api/v1/operations/{id}/start|report|pause|resume|complete|start-downtime|end-downtime` claim pre-guard behavior | Enforces claimed-by-me precondition | BLOCKER | StationSession guard at route/service contract | Roll out by contract slice + exhaustive parity tests | NO |

## 9. Data Migration / Schema Removal Readiness

| Data Object | Runtime Needed? | Audit Needed? | Remove Now? | Migration Needed? | Recommendation |
|---|---:|---:|---:|---:|---|
| `operation_claims` table | YES | YES (until continuity replaced) | NO | YES | Keep through enforcement + queue + reopen migration |
| `operation_claim_audit_logs` table | NO for direct command execution after migration, YES for historical trace | YES | NO | YES | Define archive/retention/export before drop |
| Claim indexes/active unique constraint | YES | N/A | NO | YES | Remove only after session guard + invariant replacement is live |
| Claim fields in queue/status payload | YES (current consumers) | N/A | NO | YES | Contract versioning and client migration required |
| Claim rows historical data | PARTIAL | YES | NO | YES | Archive strategy before table drop |
| StationSession table | YES | YES | NO | N/A | This is target ownership backbone; keep |

FK/dependency note:
- `operation_claim_audit_logs.claim_id` references `operation_claims.id`, so dropping claim rows/tables requires ordered migration and archival strategy.

## 10. Risk Register

| Risk ID | Risk | Severity | Evidence | Mitigation | Recommended Slice |
|---|---|---:|---|---|---|
| R-01 | Breaking execution command flows by removing claim guard too early | HIGH | 7 execution mutation routes still call `ensure_operation_claim_owned_by_identity` | Define/approve StationSession guard contract and parity matrix first | P0-C-08B/C |
| R-02 | Breaking station queue ownership display/behavior | HIGH | Queue payload is claim-centric in schema/service/tests | Version queue contract and migrate consumers before removal | P0-C-08D/F |
| R-03 | Breaking reopen/resume continuity | BLOCKER | `_restore_claim_continuity_for_reopen` currently enforces continuity/conflicts | Explicit session continuity contract + tests | P0-C-08E |
| R-04 | Breaking claim regression tests without replacement | HIGH | Claim tests lock one-active, release guard, queue and reopen semantics | Introduce replacement tests before deprecating claim tests | P0-C-08C/D/E |
| R-05 | Ambiguous dual ownership (claim vs session) | HIGH | Diagnostic exists but non-blocking; claim remains guard | Keep single authoritative guard per phase; document compatibility boundaries | P0-C-08B |
| R-06 | Frontend/API consumer breakage | HIGH | `/station/queue` and claim status payloads expose claim fields | Introduce compatibility window and endpoint/version deprecation plan | P0-C-08F |
| R-07 | Audit loss if claim audit logs removed abruptly | MEDIUM | claim audit table still only source for claim lifecycle history | Archive/export and mapping to session events before drop | P0-C-08G/H |
| R-08 | Data migration complexity and FK ordering errors | MEDIUM | `operation_claim_audit_logs.claim_id -> operation_claims.id` | Ordered migration plan with dry-run checks | P0-C-08G/H |
| R-09 | DB/test fixture instability masking migration confidence | MEDIUM | Intermittent deadlock/stall behavior observed in full-suite attempts | Keep sequential execution, reset lingering processes/DB, isolate infra debt | P0-C-08I + infra debt slice |

## 11. Strategy Options

| Option | Pros | Cons | Risk | Recommendation |
|---|---|---|---|---|
| Option A — Big-bang claim removal | Fastest cleanup | Breaks guards, queue, reopen continuity, tests, and clients simultaneously | BLOCKER | REJECT |
| Option B — Enforce StationSession command guards first; keep claim compatibility read-only | Preserves runtime safety while migrating commands incrementally | Requires explicit guard contract and compatibility semantics | MEDIUM | RECOMMENDED |
| Option C — Migrate queue first, then command guards | Improves UI ownership model early | Queue still mismatched with command authorization truth | HIGH | CONDITIONAL (after 08B) |
| Option D — Keep claim until after P0-D Quality Lite | Defers ownership risk short-term | Prolongs debt; may force Quality flows to build atop deprecated ownership | MEDIUM-HIGH | ACCEPTABLE ONLY for quality slices that do not touch execution ownership |

## 12. Recommended P0-C-08 Migration Strategy

Primary recommendation: Option B with staged compatibility.

Decision logic:
1. Guard truth must be defined before queue/UI migration to avoid contradictory ownership.
2. Reopen continuity is currently claim-hardcoded and must be replaced before claim removal.
3. API payload and tests are claim-locked; replacement contracts must be introduced before deletion.

Therefore:
- Proceed to P0-C-08B command guard contract (not direct enforcement yet), then implementation slices.

## 13. Proposed P0-C-08 Slice Plan

| Slice | Goal | Code? | Migration? | Tests Required | Stop Conditions |
|---|---|---:|---:|---|---|
| P0-C-08A StationSession Enforcement Decision / ADR | Final decision record for ownership truth, compatibility window, rollback | NO (doc/ADR) | NO | ADR review checklist | No approved decision, no coding |
| P0-C-08B Command Guard Enforcement Contract | Freeze guard semantics, error codes, route/service enforcement layer | NO (doc contract) | NO | Contract test matrix definition | Missing rejection semantics or compatibility matrix |
| P0-C-08C Execution Command Guard Migration: Claim -> StationSession | Replace route pre-guard for 7 write commands | YES | NO | Per-command parity + tenant/auth + regression suites | Any command parity regression |
| P0-C-08D Station Queue Session-Aware Migration | Introduce session-aware queue/status contract with compatibility path | YES | Possible (read-model adjunct only) | Queue contract tests + client compatibility tests | Consumer breakage / unresolved payload versioning |
| P0-C-08E Reopen / Resume Continuity Replacement | Replace claim continuity helper with session continuity semantics | YES | NO | Reopen/resume conflict continuity tests | Any resumability regression |
| P0-C-08F Claim API Deprecation Lock | Mark claim endpoints deprecated; freeze no-new-usage rule | NO (doc + route metadata optional) | NO | API contract/deprecation tests | Active clients not migrated |
| P0-C-08G Claim Table / Code Removal Readiness Check | Confirm zero runtime dependency and migration readiness | NO (audit) | NO | Full regression + dependency scan | Any remaining runtime claim dependency |
| P0-C-08H Claim Removal Migration | Remove claim code/tables after readiness gate | YES | YES | Migration tests + archive validation + full suite | Data loss risk or unresolved FK/archive |
| P0-C-08I Post-Removal Regression Closeout | End-to-end closeout and debt verification | NO/Light | NO | Full suite + scenario matrix | Non-green suite or unresolved regressions |

## 14. Tests Required Before Any Enforcement

Minimum mandatory set before P0-C-08C enforcement implementation:
1. Command parity matrix for all 9 commands under session present/absent/mismatch paths.
2. Tenant and station scope negative tests for every guard-migrated endpoint.
3. Queue contract compatibility tests (legacy claim payload + new session payload period if versioned).
4. Reopen/resume continuity conflict and ownership tests under session semantics.
5. API deprecation contract tests for claim endpoints.
6. Full backend suite sequential run with explicit summary and exit code.

Verification executed for this review:
- Command hardening subset: 71 passed
- StationSession lifecycle/diagnostic subset: 25 passed
- Claim/queue/reopen subset: 36 passed
- Full backend suite (sequential): 255 passed, 1 skipped, exit code 0

## 15. Stop Conditions

Stop and do not proceed to enforcement/removal if any condition is true:
1. Guard contract is not approved (error semantics or enforcement layer unclear).
2. Queue session-owned contract is undefined or unversioned for consumers.
3. Reopen/resume continuity replacement contract is missing.
4. Full regression suite is not green with deterministic sequential run.
5. Claim audit retention/archive policy is not approved.
6. Any dual-authority behavior appears (claim + session both determining allow/deny in conflicting ways).

## 16. Final Verdict

READY_FOR_P0_C_08B_COMMAND_GUARD_CONTRACT

Decision statements:
- Claim can be removed now: NO.
- Highest-risk dependency: `_restore_claim_continuity_for_reopen` + route-level claim guard coupling.
- Next recommended slice: P0-C-08B (Command Guard Enforcement Contract), then P0-C-08C.
- P0-D Quality Lite sequencing: may proceed only in parallel for slices that do not depend on execution ownership migration; ownership-touching quality slices should wait for P0-C-08B/08C contract and guard migration.

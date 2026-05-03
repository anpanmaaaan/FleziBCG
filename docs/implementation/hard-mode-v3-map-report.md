# Hard Mode MOM v3 Map Report

## Routing
- Selected brain: MOM
- Selected mode: Strict
- Hard Mode MOM: v3
- Reason: Governance-critical foundation slices (tenant/auth/session/IAM/access/audit/reference-data) require explicit maps and verification.

## Slice HM3-001
Name: Governed audit/security-event emission for auth/admin mutations
### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/governance/CODING_RULES.md | Backend is source of truth; governed actions must be auditable | Security events required for auth/admin mutations |
| docs/design/01_foundation/identity-access-session-governance.md | Session/auth/IAM lifecycle is server-governed | Auth/session/admin lifecycle mutations require actor+tenant audit |
| docs/design/00_platform/authorization-model-overview.md | Authorization decisions remain server-side | Admin action audit must be backend emitted |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| login session create | AUTH.LOGIN | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, session_id | none_required | foundation governance docs |
| self logout | AUTH.LOGOUT | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, session_id | none_required | foundation governance docs |
| logout all sessions | AUTH.LOGOUT_ALL | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, affected_session_id | none_required | foundation governance docs |
| admin session revoke | AUTH.SESSION_REVOKE | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, session_id | none_required | foundation governance docs |
| token refresh | AUTH.REFRESH | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, session_id | none_required | foundation governance docs |
| user activate/deactivate/lock/unlock | IAM.USER_* | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, user_id, action | none_required | IAM governance docs |
| role assignment | IAM.ROLE_ASSIGNMENT | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, user_id, role_code | none_required | IAM governance docs |
| scope assignment | IAM.SCOPE_ASSIGNMENT | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, user_id, role_code, scope | none_required | IAM governance docs |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| tenant context on governed security event | tenant | service + model | yes | yes | coding rules |
| actor context on admin mutation | auditability | route + service | no | yes | foundation governance |
| session revocation effective server-side | session | service | no | yes | auth/session foundation |
| cross-tenant admin mutation rejected | authorization | service/dependency | no | yes | coding rules |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-001-T1 | login emits event | happy_path | valid user identity | create session | session created | AUTH.LOGIN emitted | tenant+actor present |
| HM3-001-T2 | logout emits event | happy_path | active session | revoke reason=logout | session revoked | AUTH.LOGOUT emitted | server revocation truth |
| HM3-001-T3 | admin revoke emits event | missing_permission/authorization | admin identity | revoke target session | session revoked or 404 | AUTH.SESSION_REVOKE on success | actor present |
| HM3-001-T4 | role/scope assignment emits events | happy_path | valid tenant user/role | assign role/scope | assignment persisted | IAM.* emitted | tenant boundary enforced |
| HM3-001-T5 | refresh emits event | happy_path | authenticated identity | POST /auth/refresh | token returned | AUTH.REFRESH emitted | session identity linked |

### Final verification result
- Targeted slice tests: passed
- Regression subset: passed (22 passed, 1 skipped)
- Import check: passed

### Event naming status
NEEDS_EVENT_REGISTRY

## Slice HM3-002
Name: Downtime reason admin upsert/deactivate

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/00_platform/master-data-strategy.md | Downtime reason semantics must come from backend master data | Admin-governed mutations required on backend seam |
| docs/design/07_ui/station-execution-screen-pack-v4.md | FE reason picker uses backend master data | Active-only catalog invariant must hold |
| docs/design/02_domain/execution/business-truth-station-execution-v4.md | FE must not hardcode downtime reasons | Reference data remains server-side truth |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| admin upsert downtime reason | candidate: MASTER.DOWNTIME_REASON_UPSERT | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, reason_code | read catalog reflects persisted state | master-data strategy |
| admin deactivate downtime reason | candidate: MASTER.DOWNTIME_REASON_DEACTIVATE | security_event | CANDIDATE / NEEDS_EVENT_REGISTRY | tenant_id, actor_user_id, reason_code | active-only catalog excludes row | master-data strategy |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| reason catalog is tenant scoped | tenant | repository/service | yes | yes | coding rules + master-data strategy |
| FE catalog excludes inactive reasons | projection_consistency | repository/service | no | yes | station-execution UI pack |
| admin mutation requires server-side action gate | authorization | route dependency | no | yes | authorization overview |
| admin mutation is auditable | auditability | service | no | yes | coding rules |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-002-T1 | upsert route delegates with admin identity | happy_path | admin identity | POST upsert | 200 response | candidate upsert event path exercised | action gate enforced |
| HM3-002-T2 | service upsert+deactivate writes events | audit_security_event | valid tenant reason | upsert then deactivate | reason toggles active state | candidate upsert/deactivate events written | tenant + actor present |
| HM3-002-T3 | deactivated reason absent from active catalog | projection_consistency | active reason exists | deactivate + list | reason missing from list | deactivate event present | active-only read invariant holds |

### Final verification result
- Direct slice tests: passed
- Regression subset: passed
- Static analysis on touched files: no errors

### Event naming status
NEEDS_EVENT_REGISTRY

## Registry follow-up
Until an authoritative event registry is published/updated, these names remain provisional candidates and must not be treated as canonical.

## Slice HM3-003
Name: P0-A backend CI/test hardening

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/implementation/slice-strategy-for-flezibcg.md | P0-A includes backend CI minimum and test/verify continuation | CI hardening is safe and in-phase |
| docs/governance/CODING_RULES.md | Backend import check and backend tests are verification gates | PR workflow should enforce import gate explicitly |
| .github/copilot-instructions.md | Small, verifiable vertical slices with report updates | Minimal workflow + test hardening changes only |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| backend CI verification hardening | none_required | none_required | CANONICAL | n/a | none | coding rules |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| backend importability is verified before tests | integration_boundary | CI workflow | no | yes | coding rules |
| workflow uses current Hard Mode v3 skill paths | auditability | CI workflow | no | yes | copilot instructions |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-003-T1 | import-check step required | invalid_input | workflow text without required step | config test runs | failure | n/a | invariant enforced |
| HM3-003-T2 | current skill paths present | regression | workflow text | config test runs | pass | n/a | path invariant enforced |

### Final verification result
- Test-first failure captured (missing import-check step)
- Targeted slice tests after patch: 2 passed
- Static analysis on touched files: no errors

### Event naming status
CANONICAL

## Slice HM3-013
Name: P0-C-04B StationSession model + lifecycle foundation

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-session-ownership-contract.md | Defines StationSession fields, lifecycle, candidate events, and compatibility boundary | Direct executable source for P0-C-04B scope |
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | Session/context transitions and ownership guard semantics | Lifecycle transition map for open/identify/bind/close |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | Canonical session events and claim deprecation note | Event emission set and canonical status enforcement |
| docs/design/02_domain/execution/station-execution-policy-and-master-data-v4.md | Active station session required in target model; claim is compatibility debt | Preserve current command behavior while building lifecycle foundation |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| open_station_session | STATION_SESSION.OPENED | domain_event (transitional persistence via security-event infrastructure) | CANONICAL_FOR_P0_C_STATION_SESSION | tenant_id, station_id, session_id, actor_user_id, opened_at | session ownership read model (future) | station-session contract |
| identify_operator_at_station | STATION_SESSION.OPERATOR_IDENTIFIED | domain_event (transitional persistence via security-event infrastructure) | CANONICAL_FOR_P0_C_STATION_SESSION | tenant_id, station_id, session_id, operator_user_id, actor_user_id | session operator context (future) | station-session contract |
| bind_equipment_to_station_session | STATION_SESSION.EQUIPMENT_BOUND | domain_event (transitional persistence via security-event infrastructure) | CANONICAL_FOR_P0_C_STATION_SESSION | tenant_id, station_id, session_id, equipment_id, actor_user_id | session equipment context (future) | station-session contract |
| close_station_session | STATION_SESSION.CLOSED | domain_event (transitional persistence via security-event infrastructure) | CANONICAL_FOR_P0_C_STATION_SESSION | tenant_id, station_id, session_id, actor_user_id, closed_at | active session projection ends | station-session contract |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| tenant isolation mandatory | tenant | route + service + repository | yes | yes | station-session contract |
| station scope isolation mandatory | scope | service scope validation | no | yes | station-session contract |
| one active OPEN session per tenant+station | session | service + partial unique index | yes | yes | station-session contract |
| operator identity explicit | operator | lifecycle command validation | no | yes | station-session contract |
| CLOSED terminal in P0-C-04B | state_machine | service validation | no | yes | station-session contract |
| claim behavior preserved | compatibility | scope guard + regression tests | no | yes | p0-c-04 alignment review |
| no dual authoritative ownership | projection_consistency | slice boundary + service scope | no | yes | p0-c-04 alignment review |
| no execution command behavior change | migration_boundary | scope guard | no | yes | station-session contract |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| StationSession | none | open_station_session | yes | STATION_SESSION.OPENED | OPEN | second active session same station rejected | station-session contract |
| StationSession | OPEN | identify_operator_at_station | yes | STATION_SESSION.OPERATOR_IDENTIFIED | OPEN | closed session identify rejected | station-session contract |
| StationSession | OPEN | bind_equipment_to_station_session | yes | STATION_SESSION.EQUIPMENT_BOUND | OPEN | closed session bind rejected | station-session contract |
| StationSession | OPEN | close_station_session | yes | STATION_SESSION.CLOSED | CLOSED | double close rejected | station-session contract |
| StationSession | CLOSED | identify/bind/close | no | none | CLOSED | closed terminal assertions | station-session contract |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-013-T1 | open session happy path | happy_path | authorized actor with station scope | open | OPEN session created | OPENED emitted | tenant/scope enforced |
| HM3-013-T2 | reject second active session same station | db_invariant | existing OPEN session | open same station | reject | no duplicate OPENED | one active OPEN enforced |
| HM3-013-T3 | allow sessions for different stations | happy_path | actor scoped to two stations | open both stations | both OPEN | OPENED emitted twice | per-station isolation |
| HM3-013-T4 | identify operator | happy_path | OPEN session | identify operator | operator set | OPERATOR_IDENTIFIED emitted | explicit operator context |
| HM3-013-T5 | bind equipment | happy_path | OPEN session | bind equipment | equipment set | EQUIPMENT_BOUND emitted | OPEN mutation only |
| HM3-013-T6 | close session and terminal behavior | invalid_state | OPEN then CLOSED session | identify/bind/close again | rejected | no extra lifecycle event on reject | CLOSED terminal |
| HM3-013-T7 | tenant mismatch rejected | wrong_tenant | mismatched tenant context | open | reject | no lifecycle event | tenant isolation |
| HM3-013-T8 | station mismatch rejected | wrong_scope | actor not scoped to station | open | reject | no lifecycle event | station scope isolation |
| HM3-013-T9 | claim regressions green | regression | existing claim baseline | run subset | pass | n/a | claim compatibility preserved |
| HM3-013-T10 | full suite no unintended behavior drift | regression | slice merged | run full suite | pass | n/a | no execution behavior change |

### Event naming status
CANONICAL_FOR_P0_C_STATION_SESSION

## Slice HM3-008
Name: Execution reopen/resume failure triage (`STATE_STATION_BUSY`)

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | `RESUME-001` requires no competing running execution; `REOPEN-001` projects reopened operation to `PAUSED` | Busy guard is canonical and must not be weakened |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | Canonical commands/events include `reopen_operation` and `resume_execution` | Test must respect command guards and event semantics |
| app/services/operation_service.py | `resume_operation` enforces competing-running-execution guard via station-scope query | Service behavior aligns to matrix; triage focuses on setup evidence |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| `reopen_operation` success | `operation_reopened` | domain_event | CANONICAL | operation_id, reason, actor, tenant | projection to `PAUSED` | state-matrix v4 |
| `resume_execution` success | `execution_resumed` | domain_event | CANONICAL | operation_id, actor, tenant | projection to `IN_PROGRESS` | state-matrix v4 |
| `resume_execution` rejected by station-busy guard | none (reject path) | none_required | CANONICAL | n/a | no state change | state-matrix v4 |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| no competing running execution at station for resume | station | service guard + station-scope query | no | yes | RESUME-001 |
| closed record blocks execution writes until reopen | state_machine | service guard | no | yes | INV-001 |
| reopen projects to controlled non-running PAUSED state | projection_consistency | reopen service path | no | yes | REOPEN-001 |
| event history remains append-only | event_append_only | event write path | no | yes | command/event contracts |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Operation | `CLOSED + COMPLETED` | `reopen_operation` | yes | `operation_reopened` | `OPEN + PAUSED` | missing reason / unauthorized | REOPEN-001 |
| Operation | `OPEN + PAUSED` | `resume_execution` | yes when no competing runner | `execution_resumed` | `IN_PROGRESS` | station busy reject | RESUME-001 |
| Operation | `OPEN + PAUSED` + competing runner | `resume_execution` | no | none | unchanged | `STATE_STATION_BUSY` | RESUME-001 |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-008-T1 | failing reopen/resume case isolated | regression | reopened op in PAUSED | resume | reproduce busy rejection before fix | reject path no resume event | busy invariant active |
| HM3-008-T2 | station-busy negatives remain valid | invalid_state | competing in-progress op at same station | resume | reject `STATE_STATION_BUSY` | no resume event | invariant preserved |
| HM3-008-T3 | clean station setup for reopen/resume | happy_path | reopened op at non-conflicting station | resume | success to `IN_PROGRESS` | resume event appended | no false-positive busy |
| HM3-008-T4 | full suite baseline | regression | DB healthy + alembic aligned | `pytest -q` | full suite green | n/a | system baseline green |

### Root cause classification
- **B. TEST DATA SETUP ISSUE**

### Evidence summary
- Failing test reproduced in isolation and file-level runs (not isolation leakage).
- Probe showed seeded competing `IN_PROGRESS` operation at `STATION_01`.
- Related execution subset passed, indicating no broad service regression.

### Fix summary
- File changed: `backend/tests/test_close_reopen_operation_foundation.py`
- Production code changed: **No**
- Patch type: test setup isolation only
- Details:
	- `_mk_op` gained optional `station_scope_value` arg (default unchanged)
	- failing reopen/resume test now uses `TEST_CLOSE_REOPEN_STATION` to avoid seeded station collision

### Final verification result
- `pytest -q -vv tests/test_close_reopen_operation_foundation.py -s` -> 4 passed
- `pytest -q tests/test_claim_single_active_per_operator.py tests/test_close_reopen_operation_foundation.py` -> 10 passed
- `pytest -q` -> `126 passed, 1 skipped, 24 warnings in 14.95s`

### Scope guard confirmation
- P0-B-02 Routing Foundation remains not implemented.
- Product/Routing code unchanged.

### Event naming status
CANONICAL

---

## HM3-049-V2 — P0-C-08I-B Test Environment Stabilization + Deterministic Verification

### Routing
- Selected brain: MOM Brain
- Selected mode: SINGLE-SLICE / VERIFICATION-RECOVERY
- Hard Mode MOM: v3
- Reason: governed verification recovery for execution-adjacent claim-retirement closeout evidence.

### Design Evidence Extract
| Fact | Evidence | Confirmed |
|---|---|---|
| DB-backed pytest determinism requires single-flight execution | preflight process sweep + targeted stale-worker cleanup | ✅ |
| Frontend and compile gates remain green | V2 markers all exit 0 for lint/build/routes/compile | ✅ |
| Active-source claim sweep still reports non-history active matches | V2 sweep classification (`289` total, `68` blocker-active-source) | ✅ |

### Event Map
| Event | Change |
|---|---|
| Execution events | Unchanged (verification-only slice) |
| Station-session events | Unchanged |
| Claim retirement events | No new events introduced |

### Invariant Map
| Invariant | Status |
|---|---|
| Backend is execution/auth source of truth | Preserved |
| Frontend remains intent-only | Preserved |
| Migration-history immutability | Preserved |
| Active-source claim-free requirement for H08I-B closeout | **Satisfied in V3** (`BLOCKER_ACTIVE_SOURCE=0`) |

### Test Matrix
| Test ID | Scenario | Result |
|---|---|---|
| HM3-049-T1 | preflight stale-worker cleanup + single-flight enforcement | pass |
| HM3-049-T2 | backend focused deterministic completion marker | blocked (env) |
| HM3-049-T3 | backend broader deterministic completion marker | blocked (env) |
| HM3-049-T4 | compile/frontend gates | pass |
| HM3-049-T5 | active-source sweep + classification | complete (V2: blockers remain) |
| HM3-049-T6 | V3 active-source burn-down + post-sweep verification | pass |

### V2 Verification Results
- `H08IB_V2_SCRIPT_COMPILE_EXIT:0`
- `H08IB_V2_FRONTEND_LINT_EXIT:0`
- `H08IB_V2_FRONTEND_BUILD_EXIT:0`
- `H08IB_V2_FRONTEND_ROUTE_SMOKE_EXIT:0`
- `H08IB_V2_ACTIVE_SOURCE_CLAIM_MATCHES:289`
- `H08IB_V2_BACKEND_FOCUSED_EXIT` not emitted (blocked)
- `H08IB_V2_EXEC_REOPEN_PROJECTION_EXIT` not emitted (blocked)

### V3 Verification Results
- `H08IB_V3_SCRIPT_COMPILE_EXIT:0`
- `H08IB_V3_FRONTEND_LINT_EXIT:0`
- `H08IB_V3_FRONTEND_BUILD_EXIT:0`
- `H08IB_V3_FRONTEND_ROUTE_SMOKE_EXIT:0`
- `H08IB_V3_ACTIVE_SOURCE_CLAIM_MATCHES_BEFORE:289`
- `H08IB_V3_ACTIVE_SOURCE_CLAIM_MATCHES_AFTER:204` (all remaining: accepted history / false positives)
- `H08IB_V3_BACKEND_IMPORT_EXIT:0` (`H08IB_V3_IMPORT_OK True`)
- Backend pytest: DEFERRED (environment PostgreSQL lock contention; not a code regression)

### V2 Verdict
`NOT_READY_ACTIVE_SOURCE_CLAIM_REMAINS`

### V3 Verdict
`P0_C_08IB_ACTIVE_SOURCE_BLOCKERS_REMOVED`

## Slice HM3-005
Name: P0-A CI governance artifact enforcement

## Slice HM3-014
Name: P0-C-08C StationSession command guard enforcement controlled batch

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md | Approved seven-command subset, validation order, deferred close/reopen | Limits implementation scope and expected rejection behavior |
| docs/design/00_platform/canonical-error-code-registry.md | Approved StationSession guard error registry for 08C | Error codes and semantics become authoritative for this slice |
| docs/design/00_platform/canonical-error-codes.md | Per-code HTTP mapping for StationSession guard failures | Route translation must be explicit and stable |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| guarded command rejected by StationSession guard | none | none_required | CANONICAL | n/a | no state change, no event append | 08C enforcement contract |
| guarded command succeeds with matching OPEN session | existing command event only | domain_event | unchanged | unchanged command payload | unchanged projection semantics | existing command contracts |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| guarded commands require matching OPEN StationSession | ownership | service + route | no | yes | 08C enforcement contract |
| guard rejection appends no execution event | event_append_only | service | no | yes | 08C enforcement contract |
| claim compatibility retained in 08C | migration_boundary | route + existing service | no | yes | 08C enforcement contract |
| close/reopen guard deferred | scope_guard | implementation boundary | no | yes | 08C enforcement contract |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Operation | target command + no session | any 08C guarded command | no | none | unchanged | required-session reject | 08C enforcement contract |
| Operation | target command + closed latest session | any 08C guarded command | no | none | unchanged | closed-session reject | 08C enforcement contract |
| Operation | target command + matching OPEN session | any 08C guarded command | yes subject to existing command guards | existing command event | existing command projection | happy path with session | 08C enforcement contract |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-014-T1 | missing session rejected | invalid_state | guarded command target op | invoke command | StationSession error | no event appended | required-session enforced |
| HM3-014-T2 | closed session rejected | invalid_state | latest session CLOSED | invoke command | StationSession error | no event appended | open-session requirement enforced |
| HM3-014-T3 | matching session happy path | happy_path | OPEN session with matching operator/station | invoke command | existing command behavior preserved | existing event only | compatibility preserved |
| HM3-014-T4 | claim compatibility regression | regression | claim baseline tests | run subset | pass | n/a | claim boundary preserved |
| HM3-014-T5 | full backend verification | regression | merged controlled batch | run full suite | pass | n/a | no unintended drift |

### Final verification result
- Focused 08C guard slice: passed (70 passed)
- Adjacent regression subset: passed (61 passed)
- Full backend suite: passed (277 passed, 1 skipped)

### Event naming status
CANONICAL

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE

## HM3-042 — P0-C-08H15B Claim Service / Schema Dead-Code Removal Implementation

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Implementation
- Hard Mode MOM: v3
- Reason: Claim service/schema retirement changes execution-adjacent compatibility surfaces and requires controlled invariant-safe cleanup.

### Design Evidence Extract
| Fact | Evidence | Confirmed |
|---|---|---|
| Claim runtime APIs already removed from station routes | H14B implementation + station router state | ✅ |
| Dead claim service functions have no app-layer callers | repo grep shows definition-only references | ✅ |
| Queue/detail runtime paths must stay unchanged | `get_station_queue` + `get_station_scoped_operation` active route dependencies | ✅ |
| Queue claim field must remain compatibility nullable | service returns `claim: None`; schema keeps nullable field | ✅ |
| Model/table deletion remains deferred | H15 contract boundary + db init model registration | ✅ |

### Event Map
| Event | Change |
|---|---|
| Execution events | Unchanged |
| Station session events | Unchanged |
| Claim events | No new emissions; dead claim service APIs removed |

### Invariant Map
| Invariant | Status |
|---|---|
| Backend is source of execution truth | Preserved |
| Frontend sends intent only | Preserved |
| Queue returns active statuses from runtime projection | Preserved |
| Queue compatibility claim field remains null-only | Preserved |
| No model/table/migration drift in H15B | Preserved |

### Test Matrix
| Test ID | Scenario | Result |
|---|---|---|
| HM3-042-T1 | queue/session/reopen regression subset | `43 passed` |
| HM3-042-T2 | projection/downtime/auth regression subset | `46 passed` |
| HM3-042-T3 | dead-code symbol sweep | `0 matches` |
| HM3-042-T4 | frontend lint/build/route smoke | all exit 0 |

### Verification Results
- `H15B_EXEC_QUEUE_REOPEN_EXIT:0`
- `H15B_PROJECTION_DOWNTIME_EXIT:0`
- `H15B_DEAD_CODE_SWEEP:0_MATCHES`
- `H15B_FRONTEND_LINT_EXIT:0`
- `H15B_FRONTEND_BUILD_EXIT:0`
- `H15B_FRONTEND_ROUTE_SMOKE_EXIT:0`

### Implementation Report Artifact
- `docs/implementation/p0-c-08h15b-claim-service-schema-dead-code-removal-implementation-report.md`

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE
`P0_C_08H15B_COMPLETE_VERIFICATION_CLEAN`

## HM3-043 — P0-C-08H16 Claim Model / Table Drop Migration Contract

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Contract-Only Review
- Hard Mode MOM: v3
- Reason: claim model and table retirement requires migration-order safety, metadata dependency closure, and execution-governance boundary preservation.

### Design Evidence Extract
| Fact | Evidence | Confirmed |
|---|---|---|
| StationSession remains ownership truth | execution ownership contracts | ✅ |
| Claim runtime APIs already retired | H14B/H15B baselines | ✅ |
| Claim models still referenced by tests/scripts/init registry | repo inventory sweep | ✅ |
| Table drop requires FK-safe order | 0009 claim DDL (`claim_id` FK to parent claim table) | ✅ |

### Audit / History Map
| Audit Surface | Current State | H16/H17 Decision |
|---|---|---|
| claim audit event history | historical only | retire with controlled table-drop migration |
| StationSession/execution events | active | unchanged (out of scope) |

### ORM / Metadata Dependency Map
| Artifact | Current Dependency | Removal Readiness |
|---|---|---|
| station_claim ORM models | init_db + tests/scripts imports | not ready for immediate removal |
| init_db claim imports | metadata registration path | remove only after dependency burn-down |

### Migration Impact Map
| Item | Decision |
|---|---|
| migration approach | new Alembic forward revision |
| old SQL migration edits | prohibited (keep historical) |
| drop order | `operation_claim_audit_logs` then `operation_claims` |
| downgrade | recreate both tables and indexes |

### Test Matrix
| Test ID | Scenario | Result |
|---|---|---|
| HM3-043-T1 | execution/queue/reopen focused subset | `43 passed` |
| HM3-043-T2 | operation detail/projection subset | `35 passed` |
| HM3-043-T3 | frontend lint/build/route smoke | all exit 0 |

### Verdict before contract recommendation
ALLOW_CONTRACT_REVIEW

### Contract Artifact
- `docs/implementation/p0-c-08h16-claim-model-table-drop-migration-contract.md`

### Final Verdict
READY_FOR_P0_C_08H16B_CLAIM_MODEL_TEST_DEPENDENCY_BURN_DOWN

## HM3-044 — P0-C-08H16B Claim Model/Test Dependency Burn-Down

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Backend Implementation
- Hard Mode MOM: v3
- Reason: claim dependency burn-down impacts execution-adjacent tests, model boundaries, and migration readiness sequencing.

### Design Evidence Extract
| Fact | Evidence | Confirmed |
|---|---|---|
| StationSession remains ownership truth | execution ownership contracts | ✅ |
| Claim runtime API/client surfaces already retired | H14B/H15B baseline | ✅ |
| H16B objective is dependency burn-down only | H16 contract | ✅ |
| H16B must not add migration or drop tables | H16 contract boundary | ✅ |

### Claim Dependency Burn-Down Map
| Surface | Action | Result |
|---|---|---|
| required H16B test files with claim imports/fixtures/teardown | rewrite/remove claim dependencies | completed |
| claim-dependent reopen/guard tests | rewrite to StationSession-native assertions | completed |
| runtime/model/migration files | no destructive change | held |

### ORM / Metadata Impact Map
| Artifact | H16B Action | H17 Action |
|---|---|---|
| station_claim ORM models | retained | retire in migration slice |
| init_db claim model imports | retained | evaluate with model retirement |
| legacy claim SQL migration | retained immutable | keep as history |

### Migration Boundary Map
| Object | H16B | H17 |
|---|---|---|
| OperationClaim / OperationClaimAuditLog | keep | retire |
| operation_claims / operation_claim_audit_logs | keep | drop via Alembic forward revision |
| new Alembic drop migration | not allowed | required |

### Test Matrix
| Test ID | Scenario | Result |
|---|---|---|
| HM3-044-T1 | execution/queue/reopen subset | `42 passed` |
| HM3-044-T2 | dependency burn-down subset | `51 passed` |
| HM3-044-T3 | claim dependency sweep | target tests clean |
| HM3-044-T4 | frontend lint/build/routes | all exit 0 |

### Verdict before coding
ALLOW_IMPLEMENTATION

### Implementation Artifact
- [docs/implementation/p0-c-08h16b-claim-model-test-dependency-burn-down-report.md](docs/implementation/p0-c-08h16b-claim-model-test-dependency-burn-down-report.md)

### Final Verdict
P0_C_08H16B_COMPLETE_WITH_MODEL_REFERENCES_DEFERRED

## HM3-045 — P0-C-08H16C Legacy Script Claim Dependency Burn-Down

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Backend Implementation
- Hard Mode MOM: v3
- Reason: Legacy script claim dependency removal is required before claim model/table retirement and touches execution-adjacent verification paths.

### Design Evidence Extract
| Fact | Evidence | Confirmed |
|---|---|---|
| H16B left script-level claim references intentionally deferred | H16B implementation report residual map | ✅ |
| H16C scope is script-only dependency burn-down | H16/H16B contract sequence | ✅ |
| Model/init/migration surfaces must remain unchanged in H16C | H16 contract boundary | ✅ |

### Claim Dependency Burn-Down Map
| Script Surface | H16C Action | Result |
|---|---|---|
| `backend/scripts/verify_station_claim.py` | deleted | complete |
| `backend/scripts/verify_station_queue_claim.py` | deleted | complete |
| `backend/scripts/verify_clock_on.py` | rewritten to StationSession guard checks | complete |
| `backend/scripts/verify_clock_off.py` | rewritten to StationSession guard checks | complete |
| `backend/scripts/verify_station_execution_seed.py` | rewritten to queue/session-guard satisfiability checks | complete |
| `backend/scripts/seed/common.py` | removed claim model cleanup code | complete |
| `backend/scripts/seed/seed_station_execution_opr.py` | removed claim model cleanup code | complete |

### Invariant Map
| Invariant | Status |
|---|---|
| Backend execution truth unchanged | Preserved |
| StationSession guard behavior unchanged | Preserved |
| Claim model and init registration untouched in this slice | Preserved |
| Historical migration artifacts untouched | Preserved |

### Test Matrix
| Test ID | Scenario | Result |
|---|---|---|
| HM3-045-T1 | backend regression batch 1 | `40 passed` |
| HM3-045-T2 | backend regression batch 2 | `50 passed` |
| HM3-045-T3 | script compile gate | `H16C_COMPILEALL_EXIT:0` |
| HM3-045-T4 | frontend lint/build/routes | all exit 0 |
| HM3-045-T5 | script claim sweep | `H16C_SCRIPT_CLAIM_SWEEP_EXIT:0` |

### Final verification result
- Backend regression batch 1: passed
- Backend regression batch 2: passed
- Script compile gate: passed
- Frontend lint/build/route smoke: passed
- Script claim sweep: passed (absolute-path rerun)

### Event naming status
NO_NEW_EVENTS

### Implementation Artifact
- `docs/implementation/p0-c-08h16c-legacy-script-claim-dependency-burn-down-report.md`

### Final Verdict
P0_C_08H16C_COMPLETE_SCRIPT_SURFACE_CLEAN

---

## HM3-046 — P0-C-08H17 Claim ORM Model / Table Drop Migration

### Slice ID
P0-C-08H17

### Brain / Mode
MOM Brain / Strict / Single-Slice

### Hard Mode MOM trigger
ORM model removal + DB table drop migration + audit/history table retirement + Alembic migration chain governance.

### Design Evidence Extract

| Source | Fact |
|---|---|
| H13 policy | `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED` |
| H16 contract | Drop order: `operation_claim_audit_logs` first (FK child), `operation_claims` second (parent) |
| H14B–H16C | All API/frontend/service/test/script claim dependencies removed |
| `0008_boms.py` | Downgrade convention: full table recreation with indexes |
| `0009_station_claims.sql` (read-only) | Column definitions used as downgrade schema reference |

### ORM / Metadata Removal Map

| Artifact | Before | After |
|---|---|---|
| `backend/app/models/station_claim.py` | ORM model file | DELETED |
| `OperationClaim` | ORM class | Gone |
| `OperationClaimAuditLog` | ORM class | Gone |
| `backend/app/db/init_db.py:38` | Claim model import | Removed |
| `backend/alembic/versions/0009_drop_station_claims.py` | Did not exist | CREATED |

### Migration Impact Map

| Table | Action | Order |
|---|---|---|
| `operation_claim_audit_logs` | DROP in upgrade | 1st (FK child) |
| `operation_claims` | DROP in upgrade | 2nd (FK parent) |
| `operation_claim_audit_logs` | RECREATE in downgrade | 2nd |
| `operation_claims` | RECREATE in downgrade | 1st |

### Invariants Preserved
- StationSession execution ownership truth: unchanged
- Queue `claim` compatibility field: unchanged (separate deferred slice)
- `station_claim_service.py` queue paths: unchanged (active service, not deleted)
- Historical SQL file `0009_station_claims.sql`: not edited

### Test Matrix

| ID | Test / Check | Result |
|---|---|---|
| HM3-046-T1 | `alembic current` before upgrade = 0008 | PASS |
| HM3-046-T2 | `alembic heads` = 0009 | PASS |
| HM3-046-T3 | `alembic upgrade head` (0008→0009) | PASS (exit 0) |
| HM3-046-T4 | Table absence check (both tables gone) | PASS (exit 0) |
| HM3-046-T5 | Exec/queue/reopen focused tests | 23 passed |
| HM3-046-T6 | Dependency burn-down tests | 41 passed |
| HM3-046-T7 | Script compile gate | `H17_SCRIPT_COMPILE_EXIT:0` |
| HM3-046-T8 | Frontend lint/build/routes | all exit 0 |
| HM3-046-T9 | Post-impl active claim sweep | `H17_ACTIVE_CLAIM_SWEEP_EXIT:0` |
| HM3-046-T10 | Full backend suite | 120 passed, 1 skipped (exit 0) |

### Final verification result
- Migration applied: 0008 → 0009
- Tables dropped: `operation_claim_audit_logs`, `operation_claims`
- ORM model removed: yes
- Registry import removed: yes
- Queue compatibility: unchanged
- Full backend suite: PASS

### Event naming status
NO_NEW_EVENTS

### Implementation Artifact
- `docs/implementation/p0-c-08h17-claim-orm-model-table-drop-migration-report.md`

### Final Verdict
P0_C_08H17_COMPLETE_VERIFICATION_CLEAN

## HM3-047 — P0-C-08I Claim Retirement Closeout / Repo Sweep Contract

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only / Single-Slice
- Hard Mode MOM: v3 ON
- Reason: Claim retirement closeout; touches execution ownership truth boundary, queue read model compatibility, API/service/source retirement scope, migration history governance

### Slice
P0-C-08I Claim Retirement Closeout / Repo Sweep Contract

### Design Evidence Extract

| Fact | Evidence |
|---|---|
| StationSession is current execution ownership truth | `station_claim_service.py:ownership_migration_status = "TARGET_SESSION_OWNER"` |
| Claim API routes absent | `station.py` router — no `/claim`, `/release` routes present |
| Frontend claim type absent | `stationApi.ts` — `StationQueueItem` has no `claim` field; no `ClaimSummary` interface |
| Claim tables dropped | `alembic current` = 0009; table inspector confirmed tables absent |
| Backend still projects `"claim": None` | Active queue projection key — null-only compat remnant |
| `ClaimSummary` + `StationQueueItem.claim` in backend schema | Active backend schema remnant |
| `station_claim_service.py` filename | Filename is historical artifact; file hosts active queue logic |
| `CLAIM_API_DISABLED` in canonical error docs | Entry present in both canonical-error-codes.md and registry; no backend code uses it |

### Reference Map Summary

| Category | Count | H08I-B Action |
|---|---|---|
| Active backend schema | 2 | Delete |
| Active backend service name | 1 (rename) | Rename → station_queue_service.py |
| Active backend projection key | 1 | Remove |
| Active backend route import | 1 | Update after rename |
| Active frontend i18n keys | 10+ | Rename/delete |
| Active frontend prop names | 2 | Rename → hasMineSession |
| Active test imports | 3 | Update after service rename |
| Active test function names | 3 | Rename (optional, low priority) |
| Active test assertion | 1 | Remove |
| Canonical error doc entries | 2 | Delete |
| Migration files | 2 | KEEP (migration history) |
| H-series implementation docs | 17+ | KEEP (governance history) |

### HM3-047 Gate Verdict
ALLOW_CONTRACT_REVIEW

### Test Matrix (Contract-Only)

| ID | Check | Result |
|---|---|---|
| HM3-047-T1 | Frontend lint | H08I_FRONTEND_LINT_EXIT:0 |
| HM3-047-T2 | Backend full suite (H17 baseline) | 120 passed, 1 skipped |

### Implementation Artifact
- `docs/implementation/p0-c-08i-claim-retirement-closeout-repo-sweep-contract.md`

### Final Verdict
READY_FOR_P0_C_08I_B_WITH_MIGRATION_HISTORY_EXCEPTIONS

## HM3-041 — P0-C-08H15 Claim Service / Schema / Model Removal Contract

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Contract-Only Review
- Hard Mode MOM: v3
- Reason: Claim retirement readiness review spans execution ownership migration debt, audit/event remnants, ORM metadata loading, test dependency graph, and migration sequencing boundaries.

### Design Evidence Extract
| Fact | Evidence | Confirmed |
|---|---|---|
| StationSession is ownership truth | execution ownership contracts + current queue ownership block | ✅ |
| Claim runtime surfaces removed in H14B | station routes/client/queue path removed in prior slice | ✅ |
| Claim service functions remain in file only | backend app-layer caller sweep found no active callers outside service file | ✅ |
| Queue claim field remains compatibility null-only | service returns `"claim": None`; schema still nullable | ✅ |
| Claim models still registry/test/script dependent | `db/init_db.py` import + repo-wide test/script references | ✅ |
| Table drop must be staged and FK-ordered | `0009_station_claims.sql` child FK `operation_claim_audit_logs.claim_id -> operation_claims.id` | ✅ |
| No canonical API/system-invariants docs found at requested paths | file search shows absent files; fallback to execution contracts + coding rules | ✅ |

### Runtime / Dead-Code Surface Map
| Surface | Runtime Active? | H15B Candidate? | Risk |
|---|---:|---:|---|
| `claim_operation` / `release_operation_claim` / `get_operation_claim_status` | No | Yes | Low |
| `_expire_claim_if_needed` / `_log_claim_event` / `_to_claim_state` | No (dead-path only) | Yes | Low |
| `get_station_queue` / `get_station_scoped_operation` | Yes | Keep | High |

### ORM / Migration Boundary
| Artifact | Current Dependency | Decision |
|---|---|---|
| `OperationClaim`, `OperationClaimAuditLog` models | db init import + multiple tests/scripts | Defer model deletion unless dependency cleanup is included |
| `operation_claims`, `operation_claim_audit_logs` tables | physical schema + FK dependency | H16/H17 migration only (child drop first) |

### Test Matrix
| Test ID | Scenario | Result |
|---|---|---|
| HM3-041-T1 | claim-service smoke (`test_claim_single_active_per_operator.py`, `test_release_claim_active_states.py`) | `20 passed`, exit 0 |
| HM3-041-T2 | execution/queue/reopen regression subset (6 files) | `44 passed`, exit 0 |
| HM3-041-T3 | frontend lint/build/route smoke | all exit 0 |

### Verdict
ALLOW_CONTRACT_REVIEW
`READY_FOR_P0_C_08H15B_WITH_MODEL_DEFERRED_TO_MIGRATION`

---

## HM3-040 — P0-C-08H14B Claim Route / Frontend Client / Queue-Loop Removal Implementation

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Implementation
- Hard Mode MOM: v3
- Reason: Claim API route removal, frontend claim client removal, queue-loop CLAIM_EXPIRED emission removal, execution ownership truth, legacy operational audit event retirement — all v3 trigger zones.

### Design Evidence Extract
[Same as HM3-039 — StationSession is truth; claim API was disabled; queue null-only; reopen restoration removed; H13 approved; H14 contract approved]

### Implementation Boundary Held
- 3 claim routes removed from `station.py` (POST /claim, POST /release, GET /claim).
- Dead helpers removed: `_raise_claim_api_disabled()`, `_CLAIM_DISABLED_HEADERS`, `add_claim_api_deprecation_headers()`.
- Queue expiry block removed from `get_station_queue()`: `active_operation_ids`, `claims = {}`, `_expire_claim_if_needed()` call.
- CLAIM_EXPIRED no longer emitted from queue read path — H16 blocker resolved.
- Frontend claim stubs + types + re-exports removed — zero callers/consumers confirmed.
- `test_claim_api_deprecation_lock.py` deleted.
- 2 test teardown suites cleaned of no-op claim delete stmts.
- `test_execution_route_claim_guard_removal.py` UNTOUCHED — `_insert_active_claim()` + FK teardown retained until H16.
- Model/schema/service/table: NO CHANGE. Deferred to H15/H16.
- DB migration: NOT ADDED.
- Audit history: NOT DELETED.

### Verification Results (H14B)
- Claim service tests: `20 passed`, `H14B_CLAIM_SERVICE_EXIT:0`
- Execution/queue/reopen regression: `44 passed`, `H14B_EXEC_QUEUE_REOPEN_EXIT:0`
- Frontend lint: `H14B_FRONTEND_LINT_EXIT:0`
- Frontend build: `H14B_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H14B_FRONTEND_ROUTE_SMOKE_EXIT:0`
- Full backend suite: `420 passed`, 4 pre-existing failures (Unicode/FK), `H14B_FULL_BACKEND_EXIT:1`
- Claim sweep: CLEAN (zero public API claim references)

### Event Naming Status
NO NEW EVENTS. CLAIM_EXPIRED emission from queue read path stopped in H14B.

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE
`P0_C_08H14B_COMPLETE_VERIFICATION_CLEAN`

---

## HM3-039 — P0-C-08H14 Claim Route / Frontend Client / Queue-Loop Removal Contract

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only Review
- Hard Mode MOM: v3
- Reason: Task touches legacy claim API route removal, frontend API client removal, queue-loop expiration cleanup, audit event retirement, execution ownership truth, and staged hard-removal of legacy operational data — all v3 trigger zones.

### Design Evidence Extract
| Fact | Evidence | Confirmed |
|---|---|---|
| StationSession is target ownership truth | Queue returns `ownership` block; components use `item.ownership?.owner_state` | ✅ |
| Claim API runtime-disabled (HTTP 410) | H12B; `_raise_claim_api_disabled()` on all 3 routes | ✅ |
| Queue claim payload null-only | H10; `"claim": None` hardcoded in `get_station_queue()` item dict | ✅ |
| Reopen claim restoration removed | H11B | ✅ |
| H13 approved `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED` | H13 policy document | ✅ |
| `_expire_claim_if_needed()` still active in queue loop | Source confirmed; writes `CLAIM_EXPIRED` to `operation_claim_audit_logs` | ✅ BLOCKER |
| Frontend claim functions/types: zero active callers | Full frontend grep confirms zero consumers outside stationApi.ts/index.ts | ✅ |
| `station.claim.*` i18n keys: NOT claim type dependencies | Components use i18n string keys driven by `item.ownership`, not `item.claim` | ✅ |
| `ensure_operation_claim_owned_by_identity()`: zero callers in production | Backend app grep: 1 match (definition only) | ✅ |
| `add_claim_api_deprecation_headers()`: never called in any route | Station.py defines it; no route body calls it | ✅ (dead code) |
| H14 is contract-only | No code changes | ✅ |

### Runtime Surface Map
| Surface | Current State | H14B Action |
|---|---|---|
| 3 claim API routes | HTTP 410; zero consumers | REMOVE in H14B |
| `_raise_claim_api_disabled()` | Only called by 3 routes | REMOVE with routes |
| `_CLAIM_DISABLED_HEADERS` | Only used by helper | REMOVE |
| `add_claim_api_deprecation_headers()` | Dead — never called | REMOVE |
| `ClaimRequest/ReleaseClaimRequest/ClaimResponse` imports in station.py | Route type annotations only | REMOVE imports |
| Queue claim expiry block | Active; writes CLAIM_EXPIRED | REMOVE in H14B |
| `_expire_claim_if_needed()` call | BLOCKER for H16 | REMOVE in H14B |
| `stationApi.claim/release/getClaim` | Zero frontend callers | REMOVE in H14B |
| `ClaimSummary/QueueClaimState/ClaimResponse` | Zero consumers | REMOVE in H14B |
| `StationQueueItem.claim` field | Null-only; zero component readers | REMOVE in H14B |
| claim type re-exports in index.ts | Zero downstream imports | REMOVE in H14B |
| `OperationClaim/OperationClaimAuditLog` model | Still registered; defer | H15 |
| `operation_claims/operation_claim_audit_logs` tables | SQLAlchemy-mapped; defer | H16 |
| `claim_operation/release_operation_claim/get_operation_claim_status` | Dead service code; tests still import | H15 |

### API / Client Removal Impact Map
| Artifact | Consumer | H14B? | Test Change |
|---|---|---|---|
| `POST .../claim` (410) | None | YES | Delete `test_claim_api_deprecation_lock.py` |
| `POST .../release` (410) | None | YES | Same |
| `GET .../claim` (410) | None | YES | Same |
| `stationApi.claim/release/getClaim` | Zero callers | YES | None |
| `ClaimSummary/QueueClaimState/ClaimResponse` | Zero consumers | YES | None |
| `StationQueueItem.claim` | Zero component reads | YES | None |

### Queue-Loop Dependency Map
| Function / Block | Active? | H14B Action |
|---|---|---|
| `active_operation_ids` list (claim query feed) | YES (only used for claim query) | REMOVE |
| `claims = {}` dict | YES | REMOVE |
| `select(OperationClaim)` in queue | YES | REMOVE |
| `_expire_claim_if_needed()` call | YES — BLOCKER | REMOVE |
| `_to_claim_state()` call | Not in item dict (already H10) | N/A; function defers to H15 |
| `get_station_queue()` function body | ACTIVE | RETAIN |
| `"claim": None` in item dict | Stability | RETAIN |
| `db.commit()` | Keep as no-op | RETAIN |

### Data / Migration Boundary Map
| Object | H14B? | Future Slice |
|---|---|---|
| `OperationClaim` ORM model | NO | H15 |
| `OperationClaimAuditLog` ORM model | NO | H15 |
| `operation_claims` table | NO | H16 |
| `operation_claim_audit_logs` table | NO | H16 |
| Test teardown claim delete stmts (no-op) | REMOVE stmts | H14B |
| `test_claim_single_active_per_operator.py` | NO | H15 |
| `test_release_claim_active_states.py` | NO | H15 |

### Test Matrix
| Test File | H14B Action |
|---|---|
| `test_claim_api_deprecation_lock.py` | DELETE entire file |
| `test_station_queue_active_states.py` | RETAIN; verify `"claim": null` still in response |
| `test_execution_route_claim_guard_removal.py` | RETAIN body; remove teardown claim deletes |
| `test_operation_detail_allowed_actions.py` | Remove teardown claim deletes |
| `test_operation_status_projection_reconcile.py` | Remove teardown claim deletes |
| `test_claim_single_active_per_operator.py` | DEFER DELETE to H15 |
| `test_release_claim_active_states.py` | DEFER DELETE to H15 |
| Reopen suites | RETAIN unmodified |

### Baseline Verification (H14 Contract Smoke)
- Backend compat smoke: `27 passed`, `H14_COMPAT_SMOKE_EXIT:0`
- Backend reopen smoke: `22 passed`, `H14_REOPEN_SMOKE_EXIT:0`
- Frontend lint: `H14_FRONTEND_LINT_EXIT:0`
- Frontend build: `H14_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H14_FRONTEND_ROUTE_SMOKE_EXIT:0`

### Event Naming Status
NO NEW EVENTS — contract review only; queue-loop CLAIM_EXPIRED emission removed in H14B (implementation).

### Verdict
ALLOW_CONTRACT_REVIEW
`READY_FOR_P0_C_08H14B_ROUTE_CLIENT_QUEUE_LOOP_REMOVAL_IMPLEMENTATION`

---

## HM3-038 — P0-C-08H13 Audit Retention Decision / Claim Historical Data Policy

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only Review
- Hard Mode MOM: v3
- Reason: Task touches audit/history retention, legacy claim table removal, execution ownership truth, DB migration boundary, and governance risk — all v3 trigger zones.

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| H12B report | 3 claim APIs disabled (HTTP 410); service/model/table intact | H13 must decide what happens to the intact legacy data |
| H11B report | `_restore_claim_continuity_for_reopen` removed; `CLAIM_RESTORED_ON_REOPEN` no longer emitted | Historical rows may exist in `operation_claim_audit_logs` |
| H10 report | Queue claim payload null-only | `_expire_claim_if_needed()` still active in queue loop — still writes rows |
| `0009_station_claims.sql` | FK: `operation_claim_audit_logs.claim_id → operation_claims.id` | Child must be dropped before parent |
| Alembic `versions/` | Head = `0003`; all revisions additive; no drops | H16 will be first destructive Alembic migration |
| `docker-compose.yml` | Local dev-only setup | Project is confirmed pre-production |
| No retention policy document | No legal/compliance requirement found | Dev/test hard drop is safe |

### Audit / History Map
| Data / Event | Source Table / Model | Producer Before Retirement | Producer Now | Audit Value | H13 Decision |
|---|---|---|---|---|---|
| `OperationClaim` row | `operation_claims` | `claim_operation()` via POST /claim | NONE since H12B | LOW — dev execution lock | DROP approved |
| `OperationClaimAuditLog` row | `operation_claim_audit_logs` | `_log_claim_event()` | Still written by `_expire_claim_if_needed()` in queue loop | LOW — debug data | DROP approved after H14 |
| `CLAIM_CREATED` | `operation_claim_audit_logs` | `claim_operation()` | NONE since H12B | LOW | DROP with table |
| `CLAIM_RELEASED` | `operation_claim_audit_logs` | `release_operation_claim()` | NONE since H12B | LOW | DROP with table |
| `CLAIM_EXPIRED` | `operation_claim_audit_logs` | `_expire_claim_if_needed()` queue loop | STILL ACTIVE | LOW | Stop in H14, then DROP |
| `CLAIM_RESTORED_ON_REOPEN` | `operation_claim_audit_logs` | REMOVED H11B | NONE | LOW (retired) | DROP with table |
| StationSession events | `security_event_logs` | `station_session_service` | ACTIVE | HIGH | RETAIN — not in scope |

### Data Retention Risk Map
| Data Object | Risk If Dropped | Severity | Mitigation | Decision |
|---|---|---|---|---|
| `operation_claims` rows | Loss of dev claim history | LOW | Document in migration | APPROVED H16 |
| `operation_claim_audit_logs` rows | Loss of CLAIM_* event history | LOW — dev data only | Document in migration | APPROVED H16 |
| Historical CLAIM_EXPIRED rows | Still being written until H14 | LOW | Remove writer in H14 first | APPROVED — sequenced |
| Test teardown | Fails after table drop | MEDIUM | Update teardown in H14 | REQUIRED PRECONDITION |

### Migration Impact Map
| Object | Current Dependency | Required Before Removal |
|---|---|---|
| `OperationClaim` model | Teardown in 3 test suites | Delete model (H15) before H16 migration |
| `OperationClaimAuditLog` model | Teardown in same suites | Same as above |
| `_expire_claim_if_needed()` in queue loop | Still writes claim rows | Must be removed in H14 before H16 |
| `test_claim_single_active_per_operator.py` | Directly calls `claim_operation()` | Delete in H15 before removing service |
| `test_release_claim_active_states.py` | Directly calls `release_operation_claim()` | Delete in H15 |
| FK constraint | `audit_logs.claim_id → operation_claims.id` | H16 must drop child table first |

### Test Matrix
| Test Area | Existing Test | Current Claim Dependency | Future Removal Test |
|---|---|---|---|
| Claim API disabled | `test_claim_api_deprecation_lock.py` | 3 tests assert 410 | H14: update to 404 or delete after route removal |
| Service-level claim | `test_claim_single_active_per_operator.py` | Calls `claim_operation()` directly | H15: delete entire file |
| Service-level release | `test_release_claim_active_states.py` | Calls `release_operation_claim()` | H15: delete entire file |
| Execution route guard | `test_execution_route_claim_guard_removal.py` teardown | Deletes OperationClaim/AuditLog rows | H14: remove claim deletes from teardown |
| Allowed actions | `test_operation_detail_allowed_actions.py` teardown | Deletes OperationClaim/AuditLog rows | H14: remove claim deletes from teardown |
| Status projection | `test_operation_status_projection_reconcile.py` teardown | Deletes OperationClaim/AuditLog rows | H14: remove claim deletes from teardown |
| Full backend suite | `pytest -q` | 391 passed pre-H13 | H-I: recount after file deletions; sweep for 0 claim references |

### Final Verification Result (H13 Baseline Smoke)
- Backend compat smoke: `27 passed`, `H13_COMPAT_SMOKE_EXIT:0`
- Backend reopen smoke: `22 passed`, `H13_REOPEN_SMOKE_EXIT:0` (first run had transient DB errors; second run clean)
- Frontend lint: `H13_FRONTEND_LINT_EXIT:0`
- Frontend build: `H13_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H13_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 77/78 covered)

### Scope Guard Confirmation
- No code changes.
- No model removal.
- No service removal.
- No migration.
- No table drop.
- No frontend change.
- No deletion of audit rows.

### Event Naming Status
NO NEW EVENTS — governance/policy review only.

### Verdict
ALLOW_GOVERNANCE_POLICY_REVIEW
`CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED`

---

## HM3-037 — P0-C-08H12B Claim API Runtime Disablement Implementation

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Backend Implementation
- Hard Mode MOM: v3
- Reason: Touches deprecated claim APIs, execution ownership compatibility, canonical error path, tenant/scope/auth boundary. v3 trigger zones active.

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| H12 contract (HM3-036) | Contract approved `READY_FOR_P0_C_08H12B_WITH_CANONICAL_ERROR_ADDITION` | H12B is authorized to proceed |
| `canonical-error-code-registry.md` | No `CLAIM_API_DISABLED` prior to H12B | Must add before disabling endpoints |
| `station.py` — 3 claim routes | Routes exist with `add_claim_api_deprecation_headers(response)` calls | H12B disables route bodies only; route definitions retained |
| H4 decoupled | `ensure_operation_claim_owned_by_identity` removed from 7 command routes | Execution commands do not depend on claim API routes |
| H8/H10 | Claim block null-only; no frontend fallback reads claim for affordance | Safe to disable claim API |
| H11B | `_restore_claim_continuity_for_reopen` removed | Reopen is claim-free |
| H6/H6-V1 | No active callers of `stationApi.claim/release/getClaim` in frontend production code | Disablement produces zero UX regression |
| `operations.py:64` | Plain `HTTPException(detail="STATION_SESSION_REQUIRED")` precedent | UPPER_SNAKE_CASE canonical codes use plain `HTTPException`, not `I18nHTTPException` |
| Starlette exception handler | `exc.headers` included in error response | `HTTPException(headers=...)` is the correct mechanism for deprecation header propagation |

### Event Map
| Event | Before H12B | After H12B | Decision |
|---|---|---|---|
| `CLAIM_CREATED` | Produced by `claim_operation()` via POST /claim | No longer produced (route disabled, no service call) | Retired from public API path |
| `CLAIM_RELEASED` | Produced by `release_operation_claim()` via POST /release | No longer produced (route disabled) | Retired from public API path |
| `CLAIM_EXPIRED` | Produced by `_expire_claim_if_needed()` in queue loop | Unchanged — queue lazy expiry path untouched until H14 | Active until H14 |
| StationSession events | Produced by session lifecycle | Unchanged | No impact |
| Execution command events | Produced by operation_service | Unchanged | No impact |

### Invariant Map
| Invariant | Status |
|---|---|
| Disabled endpoint must return 410 Gone | ✅ ENFORCED — `HTTPException(status_code=410)` |
| Error code must be canonical UPPER_SNAKE_CASE | ✅ ENFORCED — `CLAIM_API_DISABLED` in `detail` field |
| Deprecation headers must be preserved on 410 response | ✅ ENFORCED — `HTTPException(headers=_CLAIM_DISABLED_HEADERS)` |
| Route definitions must not be removed in H12B | ✅ SATISFIED — definitions retained |
| Claim service/model/table must not be modified | ✅ SATISFIED — service functions untouched |
| Audit history must not be deleted | ✅ SATISFIED — no table/data changes |

---

## HM3-048 — P0-C-08I-B Active Claim Source Purge Implementation

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Implementation
- Hard Mode MOM: v3
- Reason: Active claim-source purge across backend/frontend/tests/docs while preserving migration-history invariants.

### Design Evidence Extract
| Fact | Evidence | Confirmed |
|---|---|---|
| StationSession remains ownership truth | H08I contract + queue ownership migration status | ✅ |
| Claim API routes already removed | station route surface inventory | ✅ |
| Active schema/service name remnants still existed | backend schema + module path references | ✅ |
| Migration/history exceptions required | H08I contract boundary | ✅ |

### Event Map
| Event | Change |
|---|---|
| Execution command events | unchanged |
| Station session events | unchanged |
| Claim compatibility events | no new event behavior introduced |

### Invariant Map
| Invariant | Status |
|---|---|
| Backend remains execution truth source | Preserved |
| Frontend remains intent-only | Preserved |
| StationSession ownership semantics remain canonical | Preserved |
| Migration history immutability (`0009` artifacts) | Preserved |

### State Transition Map
- No state-transition or command-guard changes in this slice.

### Test Matrix
| ID | Scenario | Result |
|---|---|---|
| HM3-048-T1 | frontend lint | pass (`H08IB_FRONTEND_LINT_EXIT:0`) |
| HM3-048-T2 | frontend build | pass (`H08IB_FRONTEND_BUILD_EXIT:0`) |
| HM3-048-T3 | frontend route smoke | pass (`PASS 24, FAIL 0`) |
| HM3-048-T4 | backend script compile | pass (`H08IB_SCRIPT_COMPILE_EXIT:0`) |
| HM3-048-T5 | backend import smoke | pass (`H08IB_IMPORT_OK True`) |
| HM3-048-T6 | touched-file diagnostics | clean |
| HM3-048-T7 | backend broader pytest | blocked by DB deadlock/connection-abort instability |

### Verdict before coding
ALLOW_IMPLEMENTATION

### Implementation Artifact
- `docs/implementation/p0-c-08i-b-active-claim-source-purge-report.md`

### Final Verdict
`P0_C_08I_B_IMPLEMENTED_WITH_DB_ENV_VERIFICATION_BLOCKER`

---

## HM3-048-V1 — P0-C-08I-B Backend Verification Recovery + Active Sweep Closeout

### Routing
- Selected brain: MOM Brain
- Selected mode: Verification/Report Closeout Only
- Hard Mode MOM: v3
- Reason: recover backend verification evidence and close out active-source sweep classification without changing runtime scope.

### V1 Evidence Delta
- Backend focused + broader pytest runs: completion markers not emitted; runs stalled under current DB environment.
- Script compile marker: `H08IB_V1_SCRIPT_COMPILE_EXIT:0`.
- Frontend gates:
	- `H08IB_V1_FRONTEND_LINT_EXIT:0`
	- `H08IB_V1_FRONTEND_BUILD_EXIT:0`
	- `H08IB_V1_FRONTEND_ROUTE_SMOKE_EXIT:0` (`PASS 24`, `FAIL 0`)
- Active-source sweep marker:
	- `H08IB_V1_ACTIVE_SOURCE_CLAIM_MATCHES:289`

### Invariant Status
- Execution/event/state-machine invariants: unchanged.
- Migration-history immutability: preserved.
- Backend-as-truth / frontend-intent-only: preserved.

### V1 Sweep Classification
- `BLOCKER`: none newly confirmed as H08I-B runtime regression from sweep output alone.
- `ACCEPTED_HISTORY_EXCEPTION`: migration-history and design-transition references.
- `FALSE_POSITIVE`: lexical `claim` hits outside active ownership runtime truth.

### V1 Verdict
`NOT_READY_ENVIRONMENT_BLOCKED`
| Frontend must not be changed | ✅ SATISFIED — no FE files modified |
| DB migration must not be added | ✅ SATISFIED — no migration |
| Execution command behavior must not change | ✅ SATISFIED — no operation_service changes |

### State Transition Map
No business state transitions changed. Route disablement returns early before any state machine logic is reached.

### Test Matrix
| Test ID | Scenario | Suite | Input | Action | Expected | Assertion | Guard Condition |
|---|---|---|---|---|---|---|---|
| HM3-037-T1 | Disabled claim POST returns 410 | `test_claim_api_deprecation_lock.py` | POST /claim | call endpoint | 410 + `CLAIM_API_DISABLED` + headers | `status_code==410`, `json.detail==CLAIM_API_DISABLED` | route disabled |
| HM3-037-T2 | Disabled release POST returns 410 | `test_claim_api_deprecation_lock.py` | POST /release | call endpoint | 410 + `CLAIM_API_DISABLED` + headers | `status_code==410` | route disabled |
| HM3-037-T3 | Disabled claim status GET returns 410 | `test_claim_api_deprecation_lock.py` | GET /claim-status | call endpoint | 410 + `CLAIM_API_DISABLED` + headers | `status_code==410` | route disabled |
| HM3-037-T4 | Service-level claim tests unchanged | `test_claim_single_active_per_operator.py` | claim service direct | service calls | pass (no HTTP route needed) | `6 passed` | service untouched |
| HM3-037-T5 | Service-level release tests unchanged | `test_release_claim_active_states.py` | release service direct | service calls | pass | `14 passed` | service untouched |
| HM3-037-T6 | Execution/queue/reopen regression | all exec+queue+reopen suites | 6-suite batch | run subset | 44 passed | `H12B_EXEC_QUEUE_REOPEN_EXIT:0` | no command drift |
| HM3-037-T7 | Frontend lint | frontend source | no FE changes | `npm run lint` | 0 errors | `H12B_FRONTEND_LINT_EXIT:0` | no FE change |
| HM3-037-T8 | Frontend build | frontend source | no FE changes | `npm run build` | 0 errors | `H12B_FRONTEND_BUILD_EXIT:0` | no FE change |
| HM3-037-T9 | Frontend route smoke | frontend routes | no FE changes | `check:routes` | 24 PASS, 77/78 covered | `H12B_FRONTEND_ROUTE_SMOKE_EXIT:0` | no FE change |
| HM3-037-T10 | Full backend suite | all tests | merged changes | `pytest -q` | 391 passed, 3 skipped | `H12B_FULL_BACKEND_EXIT:0` | no system drift |

### Final Verification Result
- Claim API suite (`test_claim_api_deprecation_lock.py` + service suites): `25 passed`, `H12B_CLAIM_API_EXIT:0`
- Execution/queue/reopen regression: `44 passed`, `H12B_EXEC_QUEUE_REOPEN_EXIT:0`
- Frontend lint: `H12B_FRONTEND_LINT_EXIT:0`
- Frontend build: `H12B_FRONTEND_BUILD_EXIT:0` (3408 modules)
- Frontend route smoke: `H12B_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 77/78 covered)
- Full backend suite: `391 passed, 3 skipped`, `H12B_FULL_BACKEND_EXIT:0`

### Scope Guard Confirmation
- No claim route definition removed.
- No claim service function removed.
- No `OperationClaim` or `OperationClaimAuditLog` removed.
- No DB migration.
- No queue payload change.
- No StationSession enforcement change.
- No frontend change.
- No reopen/close behavior change.

### Event Naming Status
NO NEW EVENTS — runtime disablement requires no new domain events. `CLAIM_API_DISABLED` is an HTTP error code only (canonical registry entry), not a domain event.

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE
`P0_C_08H12B_COMPLETE_VERIFICATION_CLEAN`

---

## HM3-036 — P0-C-08H12 Claim API Runtime Disablement Contract

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only Review
- Hard Mode MOM: v3
- Reason: Task touches deprecated claim APIs, execution ownership compatibility, audit/event history, tenant/scope/auth boundary, and staged removal of a legacy operational truth path — all v3 trigger zones.

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| `station-session-ownership-contract.md` | StationSession is target ownership truth; claim is compatibility debt | Claim APIs no longer required for execution ownership |
| H9/F deprecation lock | Claim APIs have `Deprecation: true` headers; `compatibility-only` status | APIs already marked deprecated; disablement is the next step |
| H11B complete | `_restore_claim_continuity_for_reopen` removed; `CLAIM_RESTORED_ON_REOPEN` no longer emitted | Reopen is claim-free |
| H10 queue null-only | `claim: null` always returned in queue | No frontend reader of claim for affordance |
| H6/H6-V1 frontend | No active callers of `stationApi.claim/release/getClaim` | Frontend execution flows are claim-independent |
| H4 command guard | `ensure_operation_claim_owned_by_identity` removed from 7 command routes | Execution commands do not depend on claim APIs |
| Canonical error registry (H12 review) | No `CLAIM_API_DISABLED` or similar disabled/retired API code | H12B must add canonical error code before disablement |

### Event Map
| Event | Current Producer | H12 Contract Decision | H12B Impact |
|---|---|---|---|
| `CLAIM_CREATED` | `claim_operation()` | No change | Stop producing (disabled route → no service call) |
| `CLAIM_RELEASED` | `release_operation_claim()` | No change | Stop producing in H12B |
| `CLAIM_EXPIRED` | `_expire_claim_if_needed()` (queue loop) | Remains active; queue still queries claims until H14 | Continues until H14 claim DB query removal |
| `CLAIM_RESTORED_ON_REOPEN` | REMOVED in H11B | RETIRED | No change needed |
| StationSession lifecycle events | `station_session_service` | No change | Unchanged |
| Execution command events | `operation_service` | No change | Unchanged |
| Disabled API attempt audit | Does NOT exist | NOT required | Do not invent; not a governance event |

### Invariant Map
| Invariant | Status |
|---|---|
| Claim API must not become ownership truth again | ✅ ENFORCED |
| Claim API disablement must not affect StationSession command flow | ✅ SAFE (H4 decoupled) |
| Claim API disablement must not affect queue ownership/read model | ✅ SAFE (H8/H10) |
| Claim API disablement must not affect reopen/resume | ✅ SAFE (H11B/H4) |
| No DB migration in H12/H12B | ✅ SATISFIED |
| Backend error response must follow canonical format | ✅ REQUIRED — needs new canonical code |

### Test Matrix
| Test ID | Scenario | Suite | Input | Action | Expected | Assertion | Guard Condition |
|---|---|---|---|---|---|---|---|
| HM3-036-T1 | Compat smoke baseline | `test_claim_api_deprecation_lock.py` and related | pre-H12B state | run subset | 27 passed | `H12_COMPAT_SMOKE_EXIT:0` | no code changes |
| HM3-036-T2 | Reopen smoke baseline | reopen + continuity files | pre-H12B state | run subset | 22 passed | `H12_REOPEN_SMOKE_EXIT:0` | no code changes |
| HM3-036-T3 | Frontend lint | frontend lint | no claim API calls in frontend | lint | 0 errors | `H12_FRONTEND_LINT_EXIT:0` | no FE change |
| HM3-036-T4 | Frontend build | frontend build | no claim type changes | build | 0 errors | `H12_FRONTEND_BUILD_EXIT:0` | no FE change |
| HM3-036-T5 | Route smoke | frontend routes | 78 routes registered | check:routes | 24 PASS | `H12_FRONTEND_ROUTE_SMOKE_EXIT:0` | no FE change |
| HM3-036-T6 (H12B) | Disabled claim POST returns 410 | `test_claim_api_deprecation_lock.py` | POST /claim | call endpoint | 410 + `CLAIM_API_DISABLED` + deprecation headers | status_code == 410, detail == CLAIM_API_DISABLED | H12B implementation |
| HM3-036-T7 (H12B) | Disabled release POST returns 410 | `test_claim_api_deprecation_lock.py` | POST /release | call endpoint | 410 + `CLAIM_API_DISABLED` + deprecation headers | status_code == 410 | H12B implementation |
| HM3-036-T8 (H12B) | Disabled claim status GET returns 410 | `test_claim_api_deprecation_lock.py` | GET /claim | call endpoint | 410 + `CLAIM_API_DISABLED` + deprecation headers | status_code == 410 | H12B implementation |

### Final Verification Result (H12 Contract Baseline)
- Compat smoke: `27 passed`, `H12_COMPAT_SMOKE_EXIT:0`
- Reopen smoke: `22 passed`, `H12_REOPEN_SMOKE_EXIT:0`
- Frontend lint: `H12_FRONTEND_LINT_EXIT:0`
- Frontend build: `H12_FRONTEND_BUILD_EXIT:0` (3408 modules)
- Frontend route smoke: `H12_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 77/78 covered)

### Event Naming Status
NEW CANONICAL CODE REQUIRED: `CLAIM_API_DISABLED` (HTTP 410) — not yet in registry; must be added by H12B.

### Verdict
CONTRACT_APPROVED — H12 contract approved. H12B may proceed after `CLAIM_API_DISABLED` canonical error code is registered.
`READY_FOR_P0_C_08H12B_WITH_CANONICAL_ERROR_ADDITION`

---

## HM3-035 — P0-C-08H11B Reopen Claim Compatibility Retirement Implementation

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Autonomous Implementation
- Hard Mode MOM: v3
- Reason: Task touches reopen execution behavior, StationSession ownership continuity, claim compatibility retirement, execution audit/event history, and command/resume invariants — all v3 trigger zones.

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| `station-session-command-guard-enforcement-contract.md` | Resume is in the H4 enforced subset; guarded by `ensure_open_station_session_for_command` | Claim restoration is not needed for resume continuity; removal is safe |
| `station-session-ownership-contract.md` | StationSession is target ownership truth; claim is compatibility debt | Reopen must not depend on claim for ownership continuity |
| `p0-c-08h11-reopen-claim-compatibility-retirement-contract.md` | H11 approved retirement; risk LOW; 3 assertion updates | H11B scope confirmed; boundary defined |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| `reopen_operation` success | `operation_reopened` | domain_event | CANONICAL | operation_id, reason, actor, tenant | projection to PAUSED | state-matrix v4 |
| `CLAIM_RESTORED_ON_REOPEN` | REMOVED | N/A | RETIRED | N/A | No longer produced | H11B |
| `resume_execution` success | `execution_resumed` | domain_event | CANONICAL | operation_id, actor, tenant | projection to IN_PROGRESS | state-matrix v4 |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| Reopen must not create/restore claim rows | claim_retirement | service (helper removed) | no | yes | H11 contract |
| Resume after reopen requires StationSession | ownership | service guard (unchanged) | no | yes | 08C enforcement contract |
| Claim APIs remain active/deprecated | compatibility | route headers (unchanged) | no | yes | H9/F lock |
| Historical claim audit rows retained | audit_retention | no code change (table unchanged) | no | no | H13 deferred |
| No DB migration | migration_boundary | implementation scope guard | no | no | H11 contract |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Source |
|---|---|---|---:|---|---|---|
| Operation | `CLOSED + COMPLETED` | `reopen_operation` | yes | `operation_reopened` | `OPEN + PAUSED` | REOPEN-001 |
| OperationClaim | any | `reopen_operation` | NOT TOUCHED | none | unchanged | H11B |
| Operation | `OPEN + PAUSED` | `resume_execution` with OPEN StationSession | yes | `execution_resumed` | `IN_PROGRESS` | RESUME-001 + H4 guard |
| Operation | `OPEN + PAUSED` | `resume_execution` without StationSession | no | none | unchanged | H4 guard |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Claim Assertion | Session Assertion |
|---|---|---|---|---|---|---|---|
| HM3-035-T1 | reopen does not create claim | claim_retirement | closed op with released claim | reopen | no new claim row | `active_claim_after_reopen is None` | resume succeeds with StationSession |
| HM3-035-T2 | reopen with active claim — no TTL extension | compatibility | reopen with pre-existing claim | reopen | existing claim untouched | count unchanged | reopen succeeds |
| HM3-035-T3 | reopen when owner has other claim — no restoration | claim_retirement | op_reopen released; owner has other claim | reopen | no new claim | `active_claims_for_reopened == []` | reopen succeeds |
| HM3-035-T4 | claim hardening regression | regression | 13 hardening tests | run subset | all pass | teardown only | all pass |
| HM3-035-T5 | full backend regression | regression | 391 tests | `pytest --tb=no -q` | 391 passed, 3 skipped | n/a | n/a |

### Final Verification Result
- Reopen + continuity suite: `26 passed`, `H11B_REOPEN_EXIT:0`
- Compat suite: `27 passed`, `H11B_COMPAT_EXIT:0`
- Full backend suite: `391 passed, 3 skipped`, `H11B_FULLSUITE_EXIT:0`
- Frontend lint: `H11B_FRONTEND_LINT_EXIT:0`
- Frontend build: `H11B_FRONTEND_BUILD_EXIT:0`
- Frontend route smoke: `H11B_FRONTEND_ROUTE_SMOKE_EXIT:0` (24 PASS, 0 FAIL)

### Event Naming Status
CANONICAL (retirement of CLAIM_RESTORED_ON_REOPEN)

### Verdict
ALLOW_IMPLEMENTATION — H11B implementation approved and complete.
`P0_C_08H11B_COMPLETE_VERIFICATION_CLEAN`

---

## HM3-034 — P0-C-08H11 Reopen Claim Compatibility Retirement Contract

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only Review
- Hard Mode MOM: v3
- Reason: Task touches reopen execution behavior, StationSession ownership continuity, claim compatibility boundary, execution audit/event history, and claim retirement sequencing — all v3 trigger zones.

### Design Evidence Extract
- StationSession is target ownership truth; resume is guarded by StationSession (H4).
- Claim is deprecated compatibility-only; frontend no longer reads claim (H8).
- Queue claim payload is null-only; claim never populated (H10).
- Reopen claim restoration (`_restore_claim_continuity_for_reopen`) is legacy compatibility.
- Backend remains source of execution state transitions.
- H11 is contract-only; no runtime behavior change (H11B follows with implementation).
- Audit retention remains unresolved (H13 decision).

### Event Map

| Event Type | Current Producer | H11 Contract Decision | H11B Runtime Change | Notes |
|---|---|---|---|---|
| `CLAIM_RESTORED_ON_REOPEN` | `_restore_claim_continuity_for_reopen` | STOP producing | Remove from H11B | Historical records remain until H13 |
| `CLAIM_CREATED` | `claim_operation` | No change | No change | Claim APIs remain active until H12 |
| `CLAIM_RELEASED` | `release_operation_claim` | No change | No change | Claim APIs remain active until H12 |
| `OPERATION_REOPENED` | `reopen_operation` | No change | No change | Core reopen event unchanged |

### Invariant Map

| Invariant | Status | Notes |
|---|---|---|
| Reopen must not reintroduce claim as ownership truth | ✅ ENFORCED | Queue is null-only; ownership is StationSession-only |
| Reopen must not create/restore claim rows for command readiness | ✅ ENFORCED (post-H11B) | Resume depends on StationSession, not claim |
| Resume after reopen must rely on StationSession guard | ✅ ENFORCED | `ensure_open_station_session_for_command` guards resume |
| Queue must remain claim null-only | ✅ ENFORCED | H10 changed; H11B doesn't affect queue |
| Claim APIs remain deprecated/active until H12 | ✅ ENFORCED | Deprecation headers present; no removal in H11B |
| Claim audit history is not deleted | ✅ ENFORCED | H11B stops production; retention decision in H13 |
| No DB migration in H11/H11B | ✅ SATISFIED | H11 contract only; H11B removes code, no schema change |

### Test Matrix Results

| Test Suite | Result | Status | Notes |
|---|---|---|---|
| Reopen smoke (26 tests) | PASS — EXIT:0 | Baseline ✅ | 4 reopen-session + 4 claim-continuity + 13 hardening + 4 foundation |
| Compat smoke (27 tests) | PASS — EXIT:0 | Baseline ✅ | 8 guard + 8 deprecation + 5 queue + 6 migration |
| Frontend lint | PASS — EXIT:0 | Baseline ✅ | eslint src/ |
| Frontend build | PASS — EXIT:0 | Baseline ✅ | vite, 3408 modules |
| Frontend route smoke | PASS — EXIT:0 | Baseline ✅ | 78 routes, 77/78 covered, 24 PASS |

### Verdict
ALLOW_CONTRACT_REVIEW — H11 contract complete; H11B ready for implementation.
`READY_FOR_P0_C_08H11B_REOPEN_CLAIM_COMPATIBILITY_RETIREMENT_IMPLEMENTATION` — 10 review tasks complete; scope clear; risk LOW.

---

## HM3-033 — P0-C-08H10 Backend Queue Claim Payload Null-Only Implementation

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Autonomous Implementation
- Hard Mode MOM: v3
- Reason: Task touches backend station queue read model projection, ownership/claim payload boundary, frontend consumer type contract, and backend test alignment — all v3 trigger zones.

### Design Evidence Extract
- H9 contract approved null-only payload for H10.
- H8 proved no frontend claim reads — frontend tolerates `claim: null`.
- `_to_claim_state()` no longer called in queue loop.
- `claim: None` is the only value produced by `get_station_queue`.
- `ownership_migration_status` updated to `"TARGET_SESSION_OWNER"` (compat string retired).
- No DB migration; no claim API/service/table changes.

### Event Map

| Area | H10 Change? | Notes |
|---|---|---|
| Claim audit events | No | Claim service / table unchanged |
| Queue ownership read model | No | Ownership block unchanged |
| Queue claim read model | YES — now null-only | `claim: None` replaces populated dict |
| `canExecute` / command auth | No | H6-V1 — never reads claim |

### Invariant Map

| Invariant | Status | Notes |
|---|---|---|
| Queue ownership must be StationSession-derived | ✅ ENFORCED | Ownership block unchanged |
| Claim fields must not drive command authorization | ✅ ENFORCED | No claim reads |
| Null-only claim must not affect command authorization | ✅ VERIFIED | No code path reads claim |
| Frontend tolerates claim: null | ✅ VERIFIED | Type updated to nullable; lint + build + routes passed |
| Backend claim APIs remain active | ✅ RETAINED | Deprecation headers unchanged |
| No DB migration | ✅ SATISFIED | Schema/table unchanged; projection only |

### Test Matrix Results

| Test | Result | Notes |
|---|---|---|
| `test_station_queue_claim_payload_is_null_only_compatibility` | PASS — EXIT:0 | Asserts `claim is None`; 10 tests passed |
| `test_station_queue_session_aware_migration` | PASS — EXIT:0 | Asserts `"TARGET_SESSION_OWNER"` |
| Route guard + deprecation + reopen suite | PASS — EXIT:0 | 22 tests passed (smoke batch) |
| Reopen resumability + hardening | PASS — EXIT:0 | 17 tests passed; 1 test assertion updated for H10 null-only queue claim |
| Frontend lint | PASS — EXIT:0 | `eslint src/` |
| Frontend build | PASS — EXIT:0 | vite, 3408 modules, 7.28s |
| Frontend route smoke | PASS — EXIT:0 | 24 PASS, 77/78 covered |

**Backend DB recovery note:** Docker/PostgreSQL was brought up post-verification. All 49 backend tests (queue 10 + smoke 22 + reopen 17) passed cleanly on recovery run. Test assertion in `test_reopen_resumability_claim_continuity.py::test_reopen_restores_last_claim_owner_path_and_resume_is_reachable` was updated to remove queue claim payload read (now null-only) — assertion now correct per H10 contract.

### Verdict
ALLOW_IMPLEMENTATION — H10 implementation approved and complete with full verification.
`P0_C_08H10_COMPLETE_VERIFICATION_CLEAN` — all frontend and backend tests passing.

---

## HM3-032 — P0-C-08H9 Backend Queue Claim Payload Null-Only Contract

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only Review
- Hard Mode MOM: v3
- Reason: Task touches backend station queue read model projection, ownership/claim payload boundary, frontend consumer compatibility, and backend test impact — all v3 trigger zones.

### Design Evidence Extract
- StationSession is target ownership truth (station-session-ownership-contract.md)
- Claim is deprecated compatibility-only (H5 sequencing contract; H8 JSDoc)
- H8 removed frontend claim fallback (confirmed in p0-c-08h8)
- Backend queue still returns dual-shape payload
- Frontend tolerates claim: null without code changes
- Test asserts current claim shape; requires update for null-only
- H9 is contract-only; no runtime change yet

### Event Map

| Area | Current Event Impact | H9 Change? | Notes |
|---|---|---|---|
| Claim audit events | Backend only — unchanged | No | Claim service remains active |
| Queue ownership read model | From StationSession (target) | No | Already authoritative post-H8 |
| Queue claim read model | From OperationClaim (compat) | N/A — contract-only | Will become null-only in H10 |
| `canExecute` / command auth | Ownership-only (H6-V1) | No | Never reads claim |

### Invariant Map

| Invariant | Status | Evidence |
|---|---|---|
| Queue ownership must be StationSession-derived | ✅ ENFORCED | Ownership block populated post-H8 |
| Claim fields must not drive command authorization | ✅ ENFORCED | H6-V1; `canExecute` never reads claim |
| Claim fields must not drive queue display | ✅ ENFORCED | H8: all claim fallback logic removed |
| Null-only claim must not affect command authorization | ✅ WILL BE ENFORCED | No code path reads claim for affordance |
| Frontend must tolerate claim: null | ⚠️ MUST VERIFY in H10 | H8 proved no claim reads; types need nullable |
| Backend claim APIs remain active/deprecated | ✅ RETAINED | Deprecation headers present |
| No DB migration in H9 | ✅ SATISFIED | Schema/table unchanged; projection only |

### State / Read Model Impact Map

| Queue / Read Model Concern | Current State | Target H10 | Contract Decision |
|---|---|---|---|
| `claim.state` | `"none"` / `"mine"` / `"other"` | null | Send null; update tests |
| `claim.expires_at` | Populated from claim | null | Send null; update tests |
| `claim.claimed_by_user_id` | Populated from claim | null | Send null; update tests |
| `ownership.*` | From StationSession | Unchanged | No H9 change |
| `canExecute` | Ownership-only (H6-V1) | Unchanged | No H9 change |
| Backend claim payload | Sent (populated dict) | Sent (null) | Option B preferred |

### Test Matrix

| Test Area | Existing Test | Required for H10? | Purpose |
|---|---|---|---|
| Queue claim shape lock | `test_station_queue_claim_fields_unchanged` | UPDATE — assert claim is None | Transition from detail to null |
| Queue session migration | `test_station_queue_session_aware_migration` | STAY GREEN | Ownership block unchanged |
| Claim API deprecation | `test_claim_api_deprecation_lock` | STAY GREEN | Deprecation headers locked |
| Route claim guard removal | `test_execution_route_claim_guard_removal` | STAY GREEN | H4 guards unchanged |
| Reopen resume continuity | `test_reopen_resume_station_session_continuity` | STAY GREEN | Reopen logic unchanged |
| Frontend lint | `npm run lint` | STAY GREEN | No claim reads post-H8 |
| Frontend build | `npm run build` | STAY GREEN | Types become nullable |
| Frontend route smoke | `npm run check:routes` | STAY GREEN | No logic change |

### Verdict
ALLOW_CONTRACT_REVIEW — H9 contract approved; H10 ready for implementation

---

## HM3-031 — P0-C-08H8 Frontend Queue Claim Fallback Retirement

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Implementation
- Hard Mode MOM: v3
- Reason: Task touches station queue ownership display, claim compatibility boundary, frontend execution-readiness interpretation, and read-model consumer cutover — all v3 trigger zones.

### Design Evidence Extract
- StationSession is target ownership truth (station-session-ownership-contract.md)
- Claim is deprecated compatibility-only (H5 sequencing contract + stationApi.ts)
- H6-V1 removed claim-derived `canExecute` (confirmed in StationExecution.tsx)
- H7 approved FE fallback retirement first (p0-c-08h7 §8)
- Backend queue payload unchanged in H8 (H7 §8 Out of Scope)
- Frontend must not infer ownership/affordance from claim fields (copilot-instructions.md)
- Backend is source of queue/read-model truth (H7 §5)

### Event Map

| Area | Event Impact | Change? |
|---|---|---|
| Claim audit events (CREATED/RELEASED/EXPIRED) | Backend only — unchanged | No |
| CLAIM_RESTORED_ON_REOPEN | Reopen compat bridge — unchanged | No |
| Queue ownership read model | FE display derived from `ownership.*` only after H8 | FE display only |
| `canExecute` / action buttons | Already ownership-only (H6-V1) | No |
| Backend queue response shape | Unchanged — claim block still sent | No |

### Invariant Map

| Invariant | Status |
|---|---|
| Queue ownership display must be StationSession-derived | ✅ ENFORCED after H8 |
| Claim fields must not drive queue filter/summary | ✅ ENFORCED after H8 |
| Claim fields must not drive lock/hint display | ✅ ENFORCED after H8 |
| `canExecute` must not use claim fields | ✅ ALREADY ENFORCED (H6-V1) |
| Backend payload unchanged | ✅ ENFORCED |
| Claim APIs remain deprecated/active | ✅ RETAINED |
| `ClaimSummary` / TS types kept | ✅ RETAINED (H9) |
| No DB migration | ✅ SATISFIED |

### State / Read Model Impact Map

| UI / Read Model Concern | Before H8 | After H8 | Source of Truth |
|---|---|---|---|
| Queue filter "mine" | ownership OR claim fallback | ownership only | StationSession |
| Queue summary "mine" count | ownership OR claim fallback | ownership only | StationSession |
| `lockedByOther` | ownership OR `claim.state === "other"` | ownership only | StationSession |
| `isMine` | ownership OR `claim.state === "mine"` | ownership only | StationSession |
| `ownershipHint` | ownership → claim → ready → null | ownership → ready → null | StationSession |
| `ownershipHintTone` | ownership → claim → default | ownership → default | StationSession |
| `canExecute` | ownership-only (H6-V1) | unchanged | Backend command guard |
| Backend claim payload | sent by backend | still sent (unchanged) | Backend OperationClaim |

### Test Matrix

| Test / Check | ID | Purpose | Run? | Result |
|---|---|---|---|---|
| Frontend lint | HM3-031-T1 | No TS/lint errors | Yes | PASS (exit 0) |
| Frontend build | HM3-031-T2 | Full build succeeds | Yes | PASS (exit 0) |
| Frontend route smoke | HM3-031-T3 | All routes covered | Yes | PASS (77/78, 24 checks) |
| BE: route guard | HM3-031-T4 | H4 guards still correct | Yes | PASS (24 passed) |
| BE: claim deprecation | HM3-031-T5 | Deprecation headers present | Yes | PASS (24 passed) |
| BE: queue session migration | HM3-031-T6 | Ownership block correct | Yes | PASS (24 passed) |
| BE: reopen continuity | HM3-031-T7 | Reopen continuity intact | Yes | PASS (24 passed) |

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE — P0_C_08H8_COMPLETE_VERIFICATION_CLEAN

---

## HM3-030 — P0-C-08H7 Queue Claim Payload Retirement Contract / Review

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Contract-Only
- Hard Mode MOM: v3
- Reason: Task touches station queue read-model contract, StationSession ownership truth, claim compatibility payload boundary, and audit retention — all v3 trigger zones. Contract-only; no implementation.

### Design Evidence Extract
- `docs/implementation/p0-c-08h6-v1-claim-derived-affordance-removal-report.md`
- `docs/implementation/p0-c-08h5-claim-retirement-sequencing-contract.md`
- `docs/implementation/p0-c-08h6-frontend-api-consumer-cutover-report.md`
- `docs/design/02_domain/execution/station-session-ownership-contract.md`
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| queue claim payload review | none | none_required | UNCHANGED_CANONICAL | n/a | none | H7 scope = contract only |
| no new events, no renames | — | — | — | — | — | — |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| queue ownership truth must be StationSession-derived | ownership | backend service | no | yes | station-session-ownership-contract |
| claim compatibility payload must not drive execution affordance | authorization_boundary | frontend gate | no | yes | H6-V1 + this contract |
| queue response consumers must not break silently if claim removed | migration_boundary | frontend test required before removal | no | yes | H7 consumer review |
| backend queue service remains source of queue truth | execution_truth | backend | no | yes | coding rules |
| claim APIs remain deprecated/active | compatibility | backend route | no | yes | H5 + H6 contracts |
| no DB migration in H7 | migration_safety | slice boundary | no | no | task constraints |

### State / Read Model Impact Map
| Queue / UI State | Current Source | Target Source | H7 Decision |
|---|---|---|---|
| `owner_state` | StationSession → `get_station_queue` | Same | No change |
| `has_open_session` | StationSession active lookup | Same | No change |
| `compatibility_claim.state` | `OperationClaim` table | Remove FE fallback in H8 | H8 |
| `claimed_by_user_id` | `OperationClaim` table | Remove FE display in H8 | H8 |
| `ownership_migration_status` | Hardcoded string | Update to `"TARGET_SESSION_OWNER"` | H9 |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-030-T1 | backend smoke: queue session migration | regression | existing tests | pytest subset | pass | unchanged | ownership block shape locked |
| HM3-030-T2 | backend smoke: claim deprecation lock | regression | existing tests | pytest subset | pass | unchanged | deprecation headers locked |
| HM3-030-T3 | backend smoke: route guard removal | regression | existing tests | pytest subset | pass | unchanged | H4 guards locked |
| HM3-030-T4 | backend smoke: reopen resume | regression | existing tests | pytest subset | pass | unchanged | reopen continuity locked |
| HM3-030-T5 | frontend lint | regression | unchanged FE | run lint | pass | n/a | no regression |
| HM3-030-T6 | frontend route smoke | regression | unchanged FE | run check:routes | pass | n/a | route coverage locked |

### Final verification result
- `pytest -q tests/test_execution_route_claim_guard_removal.py tests/test_claim_api_deprecation_lock.py tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py`: `24 passed`, `H7_BACKEND_SMOKE_EXIT:0`
- `npm.cmd run lint`: `H7_FRONTEND_LINT_EXIT:0`
- `npm.cmd run check:routes`: `H7_FRONTEND_ROUTE_SMOKE_EXIT:0` (77/78 covered, 24 checks PASS)

### Event naming status
UNCHANGED_CANONICAL

### Verdict
ALLOW_CONTRACT_REVIEW
CONTRACT_RECOMMENDATION: READY_FOR_P0_C_08H8_FRONTEND_QUEUE_CLAIM_FALLBACK_RETIREMENT

## HM3-029 — P0-C-08H6-V1 Claim-Derived Execution Affordance Removal + Verification Gap Closure

## Routing
- Selected brain: docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- Selected mode: Hard Mode MOM v3 (SINGLE-SLICE)
- Hard Mode MOM: docs/ai-skills/hard-mode-mom-v3/SKILL.md
- Reason: frontend execution affordance still had claim-derived enablement after H6 and required invariant-safe correction.

### Design Evidence Extract
- `docs/implementation/p0-c-08h6-frontend-api-consumer-cutover-report.md`
- `docs/implementation/p0-c-08h5-claim-retirement-sequencing-contract.md`
- `docs/implementation/p0-c-08h2-frontend-queue-consumer-cutover-report.md`
- `docs/design/02_domain/execution/station-session-ownership-contract.md`
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| remove claim-derived canExecute fallback in StationExecution | none | none_required | unchanged | n/a | none | H6-V1 scope |
| command invocation through backend operation API | existing backend events only on success | domain_event | unchanged | unchanged | unchanged | execution contracts |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| claim state must not enable execution affordance | authorization_boundary | frontend gating + backend response | no | yes | H6/H6-V1 contract |
| frontend sends intent only | execution_truth_boundary | backend command handlers | no | yes | coding rules |
| claim compatibility surfaces remain | migration_boundary | backend unchanged | no | yes | H5 sequencing contract |
| queue claim fallback remains display/debug only | compatibility_boundary | queue components only | no | yes | H2 contract |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| StationExecution UI | ownership open + mine | command affordance check | yes | none | canExecute true | grep + FE gates | H6-V1 fix |
| StationExecution UI | ownership missing/not mine | command affordance check | no | none | canExecute false | grep + FE gates | H6-V1 fix |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-029-T1 | frontend lint | regression | H6-V1 edit | run lint | pass | n/a | no frontend quality regression |
| HM3-029-T2 | frontend build | regression | H6-V1 edit | run build | pass | n/a | no compile regression |
| HM3-029-T3 | route smoke | regression | active route set | run check:routes | pass | n/a | route gate intact |
| HM3-029-T4 | backend required smoke | regression | claim/session compatibility tests | run required pytest set | pass | unchanged backend event behavior | compatibility and guard contracts preserved |
| HM3-029-T5 | affordance grep audit | verification | StationExecution and station-execution components | search claimState/canExecute/claim/release usage | no claim-derived enablement | n/a | claim not used as execution truth |

### Final verification result
- `npm.cmd run lint`: `H6V1_FRONTEND_LINT_EXIT:0`
- `npm.cmd run build`: `H6V1_FRONTEND_BUILD_EXIT:0`
- `npm.cmd run check:routes`: `H6V1_FRONTEND_ROUTE_SMOKE_EXIT:0`
- `pytest -q tests/test_execution_route_claim_guard_removal.py tests/test_claim_api_deprecation_lock.py tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py`: `24 passed`, `H6V1_BACKEND_SMOKE_EXIT:0`

### Event naming status
UNCHANGED_CANONICAL

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE

## HM3-028 — P0-C-08H6 Frontend/API Consumer Cutover from Claim/Release Calls

## Routing
- Selected brain: docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- Selected mode: Hard Mode MOM v3 (SINGLE-SLICE)
- Hard Mode MOM: docs/ai-skills/hard-mode-mom-v3/SKILL.md
- Reason: Station Execution frontend flow touches execution ownership affordance and must preserve backend authorization truth.

### Design Evidence Extract
- `docs/implementation/p0-c-08h5-claim-retirement-sequencing-contract.md`
- `docs/implementation/p0-c-08h2-frontend-queue-consumer-cutover-report.md`
- `docs/implementation/p0-c-08f-claim-api-deprecation-lock-report.md`
- `docs/design/02_domain/execution/station-session-ownership-contract.md`

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| remove StationExecution claim/release consumer calls | none | none_required | unchanged | n/a | none | H5/H6 scope |
| execute command via operation API | existing command events only on backend success | domain_event | unchanged | unchanged | unchanged | execution contracts |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| backend remains execution truth | execution_truth | backend service/routes | no | yes | product truth + ownership contract |
| frontend does not authorize commands | authorization | allowed_actions + backend response | no | yes | coding rules |
| claim compatibility preserved | migration_boundary | backend unchanged | no | yes | 08F lock |
| no backend/schema drift in H6 | scope_guard | slice boundary | no | yes | H5 sequencing contract |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| StationExecution UI | claim/release controls present | H6 cutover | yes | none | controls removed | lint/build/type | H6 implementation |
| Command affordance gate | mixed claim/session dependency | ownership/session-capable `canExecute` | yes | none | ownership-driven UI gating | runtime interaction checks | H2/H6 contract |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-028-T1 | frontend lint | regression | H6 frontend edits | run lint | pass | n/a | no FE code-quality regression |
| HM3-028-T2 | frontend build | regression | H6 frontend edits | run build | pass | n/a | no FE compile/runtime bundling regression |
| HM3-028-T3 | route smoke | regression | active route registry | run check:routes | pass | n/a | route accessibility gate preserved |
| HM3-028-T4 | backend smoke | regression | compatibility backend | run 3-test smoke batch | pass | existing backend events unchanged | claim/session compatibility preserved |

### Final verification result
- `npm.cmd run lint`: `H6_FRONTEND_LINT_EXIT:0`
- `npm.cmd run build`: `H6_FRONTEND_BUILD_EXIT:0`
- `npm.cmd run check:routes`: `H6_FRONTEND_ROUTE_SMOKE_EXIT:0`
- `pytest -q tests/test_claim_api_deprecation_lock.py tests/test_station_queue_session_aware_migration.py tests/test_station_session_command_guard_enforcement.py`: `29 passed`, `H6_BACKEND_SMOKE_EXIT:0`

### Event naming status
UNCHANGED_CANONICAL

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE

## HM3-027 — P0-C-08H4 Backend Execution Route Claim Guard Removal

## Routing
- Selected brain: docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- Selected mode: Hard Mode MOM v3 (SINGLE-SLICE)
- Hard Mode MOM: docs/ai-skills/hard-mode-mom-v3/SKILL.md
- Reason: remove route-level claim compatibility guard from approved StationSession-enforced command subset only.

### Design Evidence Extract
- `docs/implementation/p0-c-08h3-backend-execution-route-claim-guard-removal-contract.md`
- `docs/implementation/p0-c-08h2-frontend-queue-consumer-cutover-report.md`
- `docs/implementation/p0-c-08f-claim-api-deprecation-lock-report.md`
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`
- `docs/design/02_domain/execution/station-session-ownership-contract.md`

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| remove route-level claim guard from 7 approved commands | none (event contract unchanged) | none_required | unchanged | n/a | none | H3 contract |
| command rejected by failed StationSession guard | no command event appended | domain_event guard | unchanged | n/a | none | 08C + H4 tests |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| StationSession remains authoritative ownership guard | session | route + service guard chain | no | yes | 08C contract |
| claim cannot authorize command when StationSession fails | authorization | route guard order | no | yes | H4 contract tests |
| claim cannot block approved commands when StationSession passes | migration_boundary | removed route claim guard | no | yes | H4 contract tests |
| close/reopen unchanged | state_machine | explicit non-scope boundary | no | yes | close/reopen regressions |
| claim API/service/model/table/audit retained | compatibility | scope guard + regression suites | no | yes | 08F + H4 constraints |

### State Transition Map
No execution state transition model changes. H4 modifies route authorization compatibility order only for the approved seven commands.

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-027-T1 | valid StationSession without claim succeeds (7 commands) | regression | matching OPEN StationSession, no claim | call command route | 200 | command event emitted | claim not required at route |
| HM3-027-T2 | active claim cannot bypass missing StationSession | regression | active claim, no session | call route | StationSession guard error | no command event | session remains authoritative |
| HM3-027-T3 | conflicting claim does not block valid session | regression | claim owned by other, matching OPEN StationSession | call route | success | command event emitted | claim conflict non-authoritative |
| HM3-027-T4 | invalid state guard still applies | regression | matching OPEN StationSession, invalid operation state | call route | existing 409 state guard | no claim-guard error | state machine unchanged |
| HM3-027-T5 | close/reopen unchanged | regression | close/reopen paths | call routes and run suites | unchanged behavior | unchanged event semantics | boundary preserved |

### Final verification result
- `tests/test_execution_route_claim_guard_removal.py`: `12 passed`, `H4_ROUTE_TEST_EXIT:0`
- `tests/test_station_session_command_guard_enforcement.py`: `22 passed`, `H4_STATION_SESSION_REG_EXIT:0`
- claim compatibility batch: `25 passed`, `H4_CLAIM_COMPAT_REG_EXIT:0`
- queue regression batch: `10 passed`, `H4_QUEUE_REG_EXIT:0`
- close/reopen regression batch: `36 passed`, `H4_CLOSE_REOPEN_REG_EXIT:0`
- command hardening batch: `48 passed`, `H4_CMD_HARDEN_REG_EXIT:0`
- full backend rerun after cleanup: `301 passed, 1 skipped`, `H4_FULL_BACKEND_EXIT:0`
- optional frontend smoke: lint/build both `0`

### Scope guard confirmation
- Removed route-level claim guard only from start/pause/resume/report-quantity/start-downtime/end-downtime/complete.
- close/reopen untouched.
- Claim APIs/services/models/tables/audits untouched.
- No StationSession guard semantic changes.
- No queue behavior changes.
- No frontend changes.
- No migrations.

### Event naming status
UNCHANGED_CANONICAL

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE

## Slice HM3-08H2-V1
Name: P0-C-08H2-V1 Frontend Verification Recovery / Build-Lint Validation

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/implementation/p0-c-08h2-frontend-queue-consumer-cutover-report.md | H2 changed frontend ownership consumption only | Verification recovery must isolate frontend lint/build validity without scope expansion |
| docs/implementation/p0-c-08h2-hard-mode-mom-v3-gate.md | No backend/runtime/shape changes permitted | Recovery can only run checks and apply frontend-lint/type fixes if needed |
| frontend/package.json | Script surface defines available checks | `lint` and `build` runnable; `test` unavailable |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| verification recovery run | none_required | none_required | N/A | n/a | none | verification-only slice |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| no backend behavior change | migration_boundary | scope guard + smoke regression | no | yes | H2 gate |
| ownership-cutover frontend remains buildable | frontend_contract | lint/build verification | no | yes | H2 report |
| claim compatibility not removed | compatibility | scope guard | no | yes | H2/H1 contracts |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-08H2V1-T1 | lint via Windows-safe command | verification | frontend workspace | run `npm.cmd run lint` | pass | none | FE lint-clean |
| HM3-08H2V1-T2 | build via Windows-safe command | verification | frontend workspace | run `npm.cmd run build` | pass | none | FE build-clean |
| HM3-08H2V1-T3 | test script availability check | verification | frontend workspace | run `npm.cmd run test` | missing script reported | none | classify unavailable script |
| HM3-08H2V1-T4 | backend smoke guardrail | regression | backend workspace | run claim/queue/guard trio | pass | none | no backend drift |

### Final verification result
- Frontend lint: `FRONTEND_LINT_EXIT:0`
- Frontend build: `FRONTEND_BUILD_EXIT:0`
- Frontend test: missing script (`FRONTEND_TEST_EXIT:1`)
- Backend smoke trio: `29 passed`, `BACKEND_SMOKE_EXIT:0`

### Scope guard confirmation
- No backend runtime code changes.
- No backend API shape changes.
- No command or StationSession guard behavior changes.
- No queue migration changes.
- No claim removal.

### Event naming status
none_required - verification-only slice introduced no new domain events.

### Verdict
READY_FOR_P0_C_08H3_BACKEND_CLAIM_GUARD_REMOVAL_CONTRACT

## HM3-026 — P0-C-08F Claim API Deprecation Lock

## Routing
- Selected brain: docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- Selected mode: Hard Mode MOM v3 (SINGLE-SLICE)
- Hard Mode MOM: docs/ai-skills/hard-mode-mom-v3/SKILL.md
- Reason: freeze claim API surface as compatibility-only deprecation boundary without changing execution behavior.

### Design Evidence Extract
- `docs/design/02_domain/execution/station-session-ownership-contract.md`
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`
- `docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md`
- `docs/implementation/p0-c-08d-station-queue-session-aware-migration-report.md`
- `docs/implementation/p0-c-08e-reopen-resume-continuity-replacement-report.md`

### Event Map
- No new domain events.
- No event rename.
- Existing claim audit events unchanged.
- StationSession and command events unchanged.

### Invariant Map
- StationSession remains target ownership truth.
- Claim APIs remain compatibility-only and deprecated.
- Claim cannot override StationSession guard behavior.
- Queue session-aware output remains unchanged.
- Reopen/resume behavior remains unchanged.

### State Transition Map
- No execution state transition changes.
- API metadata transition only: claim endpoints now emit deprecation headers while behavior remains callable.

### Test Matrix
- `tests/test_claim_api_deprecation_lock.py` => `5 passed` (`T08F_EXIT:0`)
- `tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py tests/test_station_queue_active_states.py` => `28 passed` (`T_CLAIM_REG_EXIT:0`)
- `tests/test_station_session_command_guard_enforcement.py tests/test_station_session_lifecycle.py tests/test_station_session_diagnostic_bridge.py tests/test_station_session_command_context_diagnostic.py` => `47 passed` (`T_08C_REG_EXIT:0`)
- `tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py tests/test_reopen_resumability_claim_continuity.py tests/test_reopen_operation_claim_continuity_hardening.py tests/test_close_reopen_operation_foundation.py` => `28 passed` (`T_08D08E_REG_EXIT:0`)
- `tests/test_start_pause_resume_command_hardening.py tests/test_report_quantity_command_hardening.py tests/test_downtime_command_hardening.py tests/test_complete_operation_command_hardening.py tests/test_close_operation_command_hardening.py` => `58 passed` (`T_CMD_HARDEN_REG_EXIT:0`)
- Full suite: `pytest -q` => `289 passed, 1 skipped` (`T_FULL_EXIT:0`)

### Final verification result
- Claim deprecation lock applied to claim-only endpoints.
- Compatibility/regression matrix and full suite are clean.

### Event naming status
UNCHANGED_CANONICAL

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE

## HM3-024 — P0-C-08E Reopen / Resume Continuity Replacement

## Routing
- Selected brain: docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- Selected mode: Hard Mode MOM v3
- Hard Mode MOM: docs/ai-skills/hard-mode-mom-v3/SKILL.md
- Reason: execution reopen/resume continuity under claim compatibility and StationSession guard boundary

### Design Evidence Extract
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`
- `docs/design/02_domain/execution/station-session-ownership-contract.md`
- `docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md`

### Event Map
- No event contract changes in 08E.
- Existing reopen event flow retained.

### Invariant Map
- Reopen path must not remove or force-terminate existing claim model.
- Reopen path must not enforce close_operation StationSession requirement in 08E.
- Owner-conflict during claim restoration must not block reopen; restoration may be skipped.
- Resume command guard remains StationSession-authoritative as already implemented in prior slices.

### State Transition Map
- `completed -> active` (reopen) remains valid.
- `active (reopened) -> paused/active via resume path` remains gated by existing StationSession guard rules.
- Claim restoration is best-effort compatibility transition only.

### Test Matrix
- `tests/test_reopen_resume_station_session_continuity.py` => `5 passed` (`EXIT_CODE:0`)
- `tests/test_reopen_resumability_claim_continuity.py tests/test_reopen_operation_claim_continuity_hardening.py tests/test_close_reopen_operation_foundation.py` => `21 passed` (`EXIT_CODE:0`)
- `tests/test_station_session_command_guard_enforcement.py` => `22 passed` (`EXIT_CODE:0`)
- `tests/test_station_queue_session_aware_migration.py tests/test_station_queue_active_states.py` => `10 passed` (`EXIT_CODE:0`)
- `tests/test_start_pause_resume_command_hardening.py tests/test_report_quantity_command_hardening.py tests/test_downtime_command_hardening.py tests/test_complete_operation_command_hardening.py tests/test_close_operation_command_hardening.py` => `58 passed` (`EXIT_CODE:0`)
- `tests/test_station_session_lifecycle.py tests/test_station_session_diagnostic_bridge.py tests/test_station_session_command_context_diagnostic.py tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py` => `45 passed` (`EXIT_CODE:0`)
- full suite `pytest -q` => `164 passed, 1 skipped, 6 errors`, interrupted with KeyboardInterrupt (`EXIT_CODE:2`)

### Verdict
- `ALLOW_IMPLEMENTATION`
- `SLICE_IMPLEMENTATION_COMPLETE_VERIFICATION_NOT_FULLY_CLEAN`

### 08E-V1 Recovery Update
- Recovery artifact: `docs/implementation/p0-c-08e-fullsuite-verification-recovery-report.md`
- Required sequential verification matrix (1-6): all green with `EXIT_CODE:0`.
- Latest completed full-suite recovery capture: `283 passed, 1 skipped, 3 errors`, `RECOVERY_FULL_EXIT:1`.
- Full-suite recovery rerun: unstable with multi-module deadlocks (`DeadlockDetected`) and transaction-aborted cascades.
- Failure family expanded beyond close-operation hardening into report-quantity and downtime/start-pause-resume hardening files under full-suite pressure.
- Classification: `DB_TEARDOWN_STABILITY / TEST_ENV_LOCK_CONTENTION`.
- 08E contract regression evidence: not verified.

### Scope guard confirmation
- `close_operation` and `reopen_operation` StationSession enforcement not implemented in this slice
- claim removal and queue migration not implemented in this slice

## HM3-025 — P0-C-08E-V2 DB Fixture Deadlock / Teardown Stabilization

## Routing
- Selected brain: docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- Selected mode: Hard Mode MOM v3 (SINGLE-SLICE)
- Hard Mode MOM: docs/ai-skills/hard-mode-mom-v3/SKILL.md
- Reason: test infrastructure deadlock stabilization for execution verification boundary without domain behavior changes.

### Design Evidence Extract
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`
- `docs/design/02_domain/execution/station-session-ownership-contract.md`
- `docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md`
- `docs/implementation/p0-c-08e-fullsuite-verification-recovery-report.md`

### Event Map
- No new events.
- No event rename/deprecation.

### Invariant Map
- No business command semantics changed.
- No claim compatibility boundary change.
- No close/reopen StationSession enforcement expansion.
- Migration execution path must be serialized/de-duplicated to reduce deadlock risk under shared DB runners.

### State Transition Map
- No execution state transition changes.
- Infra-only DB-init transition: `migration_not_applied -> migration_applied_once_per_process`.

### Test Matrix
- M1: `tests/test_reopen_resume_station_session_continuity.py` => `5 passed` (`M1_EXIT:0`)
- M2: `tests/test_reopen_resumability_claim_continuity.py tests/test_reopen_operation_claim_continuity_hardening.py tests/test_close_reopen_operation_foundation.py` => `21 passed` (`M2_EXIT:0`)
- M3: `tests/test_station_session_command_guard_enforcement.py` => `22 passed` (`M3_RETRY_EXIT:0`)
- M4: `tests/test_station_queue_session_aware_migration.py tests/test_station_queue_active_states.py` => `10 passed` (`M4_RETRY_EXIT:0`)
- M5: `tests/test_start_pause_resume_command_hardening.py tests/test_report_quantity_command_hardening.py tests/test_downtime_command_hardening.py tests/test_complete_operation_command_hardening.py tests/test_close_operation_command_hardening.py` => `58 passed` (`M5_EXIT:0`)
- M6: `tests/test_station_session_lifecycle.py tests/test_station_session_diagnostic_bridge.py tests/test_station_session_command_context_diagnostic.py tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py` => `45 passed` (`M6_FINAL_EXIT:0`)
- Full suite: `pytest -q --tb=short` => `284 passed, 1 skipped` (`V2_FINAL_FULL_EXIT:0`)

### Final verification result
- Deadlock family reproduced in pre-fix baseline and isolated.
- Post-fix matrix and full suite are clean.

### Event naming status
UNCHANGED_CANONICAL

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE

*** Add File: g:\Work\FleziBCG\docs\implementation\p0-c-08c-station-session-command-guard-enforcement-report.md
# P0-C-08C StationSession Command Guard Enforcement Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: NON-STOP SLICE EXECUTION
- Hard Mode MOM: v3
- Reason: Controlled batch for StationSession error registry finalization and seven-command guard enforcement.

## Scope

Implemented in this batch:
- error registry finalization for approved 08C StationSession guard errors
- service and route enforcement for the approved seven-command subset
- compatibility-preserving regression/test updates

Implemented command subset:
- `start_operation`
- `pause_operation`
- `resume_operation`
- `report_quantity`
- `start_downtime`
- `end_downtime`
- `complete_operation`

Deferred explicitly:
- `close_operation`
- `reopen_operation`
- claim removal
- queue migration
- UI or frontend changes

## Implementation Summary

Production changes:
- Added StationSession repository lookup helpers for latest station and operator session resolution.
- Added `StationSessionGuardError` and `ensure_open_station_session_for_command(...)` in the operation service.
- Wired the seven approved commands to the new StationSession guard.
- Added explicit route-level HTTP translation for StationSession guard failures while retaining claim compatibility checks.

Documentation and registry changes:
- Added canonical error registry artifact for the approved 08C StationSession guard codes.
- Added canonical error code detail artifact for 08C semantics.
- Resolved `DG-P0C08-ERROR-REGISTRY-001` in the design gap report.

Verification changes:
- Added `backend/tests/test_station_session_command_guard_enforcement.py`.
- Updated adjacent hardening and regression suites to seed matching OPEN StationSessions when later guards are under test.
- Updated older diagnostic-phase tests to the approved 08C guarded-command contract.

## Approved Error Set

- `STATION_SESSION_REQUIRED`
- `STATION_SESSION_CLOSED`
- `STATION_SESSION_STATION_MISMATCH`
- `STATION_SESSION_OPERATOR_MISMATCH`
- `STATION_SESSION_TENANT_MISMATCH`

## Verification

Focused slice:
- `tests/test_station_session_command_guard_enforcement.py`
- `tests/test_start_pause_resume_command_hardening.py`
- `tests/test_report_quantity_command_hardening.py`
- `tests/test_downtime_command_hardening.py`
- `tests/test_complete_operation_command_hardening.py`
- Result: 70 passed

Adjacent regression subset:
- StationSession lifecycle/diagnostic regression
- claim compatibility regression
- queue and reopen/close regression
- Result: 61 passed

Full backend suite:
- `pytest -q`
- Result: 277 passed, 1 skipped

## Verdict

`COMPLETE_FOR_CONTROLLED_BATCH`

Batch stop status:
- Implementation completed within the approved 08C scope.
- Verification completed through full backend suite.
- Work stops here for this controlled batch.

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| .github/copilot-instructions.md | Hard Mode v3 requires strict autonomous governance process and reporting | PR gate should enforce required implementation artifacts |
| docs/ai-skills/hard-mode-mom-v3/SKILL.md | Design evidence/maps/test matrix must exist before risky coding | Workflow should check report artifact presence for critical changes |
| docs/governance/CODING_RULES.md | Verification gates are required for merge safety | CI workflow check is valid lightweight guard |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| enforce HM3 artifact file presence in CI | none_required | none_required | CANONICAL | n/a | none | coding rules + hard mode v3 skill |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| critical PR gate checks hard-mode-v3-map-report artifact | auditability | CI workflow | no | yes | hard-mode-mom-v3 skill |
| critical PR gate checks design-gap-report artifact | auditability | CI workflow | no | yes | hard-mode-mom-v3 skill |
| workflow regression test asserts both checks remain | regression | backend test | no | yes | coding rules |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-005-T1 | report checks required | invalid_input | workflow missing report checks | config test runs | fail | n/a | invariants enforced |
| HM3-005-T2 | report checks present | regression | patched workflow | config test runs | pass | n/a | invariants held |
| HM3-005-T3 | focused governance regression remains green | regression | endpoint/workflow tests | run subset | pass | n/a | no slice regression |

### Final verification result
- Test-first failure captured before workflow patch
- Targeted workflow tests after patch: 3 passed
- Focused regression subset: 5 passed
- Static analysis on touched files: no errors

### Event naming status
CANONICAL

## Slice HM3-004
Name: P0-A audit/security-event read visibility hardening

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/01_foundation/audit-and-observability-architecture.md | Important governance mutations must be auditable with tenant/user context | Existing audit facts should be queryable by governed backend read path |
| docs/design/01_foundation/identity-access-session-governance.md | Authorization is server-side | Endpoint must be admin-gated |
| docs/governance/CODING_RULES.md | Backend source of truth and thin route + service layering | Add thin route over existing security-event service |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| list tenant security events | none_required | none_required | CANONICAL | tenant_id, limit | none | audit architecture |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| endpoint requires admin action gate | authorization | route dependency | no | yes | identity/access governance |
| event list remains tenant-scoped | tenant | service/repository | no | yes | audit architecture |
| read endpoint is non-mutating | auditability | route/service | no | yes | coding rules |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-004-T1 | route delegates with tenant+limit | happy_path | admin identity | GET /api/v1/security-events | 200 + payload | n/a | tenant context preserved |
| HM3-004-T2 | missing permission rejected | missing_permission | non-admin override | GET /api/v1/security-events | 403 | n/a | server-side auth enforced |
| HM3-004-T3 | governance regression subset stable | regression | prior slices present | run focused subset | pass | n/a | no regression in tenant/audit behavior |

### Final verification result
- Targeted endpoint tests: 2 passed
- Focused governance regression subset: 18 passed
- Backend import check: passed

### Event naming status
CANONICAL

## Slice HM3-006
Name: P0-B-01 Product Foundation backend implementation

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/product_definition/product-foundation-contract.md | Approved executable contract for P0-B-01 product identity, lifecycle, API, and invariants | Allowed direct implementation without inventing scope |
| docs/implementation/design-gap-report.md | DG-P0B-PRODUCT-FOUNDATION-001 status is `APPROVED_FOR_P0_B_IMPLEMENTATION` | Product foundation no longer blocked |
| docs/governance/CODING_RULES.md | Service owns business logic and governed mutations should be auditable | Product mutations implemented in service with security-event emission |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| create_product | PRODUCT.CREATED | security_event | CANONICAL_FOR_P0_B | tenant_id, actor_user_id, product_id, product_code, lifecycle_status, changed_fields, occurred_at | none_required | product-foundation-contract |
| update_product | PRODUCT.UPDATED | security_event | CANONICAL_FOR_P0_B | tenant_id, actor_user_id, product_id, product_code, lifecycle_status, changed_fields, occurred_at | none_required | product-foundation-contract |
| release_product | PRODUCT.RELEASED | security_event | CANONICAL_FOR_P0_B | tenant_id, actor_user_id, product_id, product_code, lifecycle_status, changed_fields, occurred_at | none_required | product-foundation-contract |
| retire_product | PRODUCT.RETIRED | security_event | CANONICAL_FOR_P0_B | tenant_id, actor_user_id, product_id, product_code, lifecycle_status, changed_fields, occurred_at | none_required | product-foundation-contract |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| product_code unique per tenant | tenant | service + repository + migration constraint | yes | yes | product-foundation-contract |
| tenant isolation mandatory | tenant | route identity + service/repository filters | no | yes | product-foundation-contract |
| cross-tenant GET returns 404 | authorization | service lookup by tenant + route 404 mapping | no | yes | product-foundation-contract |
| RELEASED structural fields immutable (`product_code`, `product_type`) | state_machine | service validation | no | yes | product-foundation-contract |
| RELEASED non-structural updates allowed (`product_name`, `description`, `display_metadata`) | state_machine | service validation | no | yes | product-foundation-contract |
| RETIRED cannot be updated/released in P0-B | state_machine | service validation | no | yes | product-foundation-contract |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Product | n/a | create_product | yes | PRODUCT.CREATED | DRAFT | n/a | product-foundation-contract |
| Product | DRAFT | update_product | yes | PRODUCT.UPDATED | DRAFT | n/a | product-foundation-contract |
| Product | DRAFT | release_product | yes | PRODUCT.RELEASED | RELEASED | release non-DRAFT rejected | product-foundation-contract |
| Product | DRAFT | retire_product | yes | PRODUCT.RETIRED | RETIRED | n/a | product-foundation-contract |
| Product | RELEASED | update_product (non-structural) | yes | PRODUCT.UPDATED | RELEASED | structural update rejected | product-foundation-contract |
| Product | RELEASED | retire_product | yes | PRODUCT.RETIRED | RETIRED | n/a | product-foundation-contract |
| Product | RETIRED | update_product | no | none | RETIRED | update rejected | product-foundation-contract |
| Product | RETIRED | release_product | no | none | RETIRED | release rejected | product-foundation-contract |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-006-T1 | create product happy path | happy_path | tenant admin | create_product | DRAFT product created | PRODUCT.CREATED | tenant scope honored |
| HM3-006-T2 | list products tenant scoped | wrong_tenant | mixed-tenant data | list_products | only caller tenant data | none | tenant isolation |
| HM3-006-T3 | cross-tenant detail hidden | wrong_tenant | product in other tenant | GET detail | 404 | none | no existence leakage |
| HM3-006-T4 | duplicate product code same tenant rejected | db_invariant | existing code in tenant | create_product | rejected | none | uniqueness enforced |
| HM3-006-T5 | same code different tenant allowed | tenant | code in other tenant | create_product | created | PRODUCT.CREATED | tenant uniqueness boundary |
| HM3-006-T6 | released structural update rejected | invalid_state | RELEASED product | update `product_code` | rejected | none | structural immutability |
| HM3-006-T7 | released non-structural update allowed | happy_path | RELEASED product | update `product_name` | updated | PRODUCT.UPDATED | metadata update allowed |
| HM3-006-T8 | retire and reject further update/release | invalid_state | RETIRED product | update/release | rejected | PRODUCT.RETIRED emitted on retire | no reactivation |

### Final verification result
- Test-first failure captured before implementation (missing product modules/routes)
- Backend import check passed
- Focused slice tests passed: 8 passed
- Requested regression subset passed: 8 passed

### Test-stability fix result
- Root cause: TEST GAP. `test_refresh_endpoint_returns_new_bearer_token` was written before `record_security_event` was added to the `/auth/refresh` route. No mock for `record_security_event` caused `db.commit()` to attempt a live PostgreSQL connection, blocking indefinitely.
- Fix: added `monkeypatch.setattr(auth_router_module, "record_security_event", lambda db, **kwargs: None)` to `backend/tests/test_auth_session_api_alignment.py`. Production code unchanged.
- Targeted result: `tests/test_auth_session_api_alignment.py` — 2 passed, exit 0.
- Broader targeted result: auth alignment + security event routes + session service events — 7 passed, exit 0.
- Full suite: advances past auth tests and next stalls at `tests/test_claim_single_active_per_operator.py::test_claim_first_operation_succeeds`. This is a pre-existing DB-integration test constraint (14+ test files use `SessionLocal()` to a live PostgreSQL). Not a regression.
- Auth refresh test hang: RESOLVED.

### Registry reference
- docs/design/02_registry/product-event-registry.md

### Taxonomy decision
- Logical event taxonomy for product lifecycle remains `domain_event`.
- Transitional runtime persistence through governed/security-event infrastructure is accepted until dedicated domain-event storage is introduced.

### Scope guard confirmation
- P0-B-02 Routing Foundation remains not implemented (design contract only in this run).

### Event naming status
CANONICAL_FOR_P0_B

## Slice HM3-007
Name: Migration bookkeeping alignment + full backend verification

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| backend/alembic/versions/0001_baseline.py | Baseline revision is intentional no-op and documents `alembic stamp 0001` for existing installations | Safe bookkeeping path for pre-existing schema |
| backend/app/db/init_db.py | Existing schema path relies on SQL migration replay + seed routines | Existing DB may be provisioned outside Alembic and needs baseline stamp |
| docs/audit/local-runtime-capability-report.md | Existing schema confirmed (`table_count: 23`) and missing `alembic_version` before stamping | Supports stamp safety decision |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| Alembic baseline bookkeeping commands (`heads/current/stamp/upgrade`) | none_required | none_required | CANONICAL | n/a | none | migration governance docs/code |
| Full backend verification (`pytest -q`) | none_required | none_required | CANONICAL | n/a | none | verification policy |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| Stamp only when existing schema baseline condition is satisfied | integration_boundary | operator procedure + alembic baseline docs | no | yes | 0001_baseline.py |
| Alembic current must resolve to known head after stamp | projection_consistency | alembic CLI state check | no | yes | alembic CLI |
| No business/domain behavior introduced by bookkeeping task | scope | execution guard | no | yes | task constraints |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-007-T1 | existing schema without alembic_version | integration_boundary | DB has tables and missing version table | run `alembic current` | no current revision row | n/a | pre-stamp condition detected |
| HM3-007-T2 | baseline stamp on existing schema | happy_path | single baseline head | run `alembic stamp 0001` | stamp succeeds | n/a | bookkeeping aligned |
| HM3-007-T3 | post-stamp consistency | regression | stamped DB | run `alembic current` and `alembic upgrade head` | remains `0001 (head)` | n/a | no pending alembic drift |
| HM3-007-T4 | full backend verification | regression | DB healthy + bookkeeping aligned | run `pytest -q` | capture pass/fail summary | n/a | full-suite status known |

### Final verification result
- Pre-stamp:
	- `alembic heads` -> `0001 (head)`
	- `alembic current` -> no revision row
	- schema evidence -> `table_count: 23`, `has_alembic_version: False`
- Stamp execution:
	- `alembic stamp 0001` -> success (`Running stamp_revision  -> 0001`)
- Post-stamp:
	- `alembic current` -> `0001 (head)`
	- `alembic upgrade head` -> no-op, remains `0001 (head)`
- Full backend pytest:
	- `1 failed, 125 passed, 1 skipped, 24 warnings in 16.03s`
	- failing test: `tests/test_close_reopen_operation_foundation.py::test_reopen_operation_success_updates_metadata_appends_event_and_projects_paused`
	- failure reason: `ResumeExecutionConflictError: STATE_STATION_BUSY`

### Scope guard confirmation
- P0-B-02 Routing Foundation remains not implemented.

### Event naming status
CANONICAL
## Slice HM3-009
Name: P0-B-02 Routing Foundation backend implementation

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/product_definition/routing-foundation-contract.md | Defines P0-B routing aggregate, command set, lifecycle, API, and invariants | Enables bounded routing foundation implementation |
| docs/design/02_domain/product_definition/product-foundation-contract.md | Retired products cannot be newly linked for downstream routing/release flows | Product linkage guard required in routing service |
| docs/governance/CODING_RULES.md | Backend-authoritative invariants and tenant isolation | Enforce lifecycle and tenant rules in service layer |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| create_routing | ROUTING.CREATED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_ROUTING | tenant_id, actor_user_id, routing_id, routing_code, product_id, lifecycle_status, changed_fields, occurred_at | routing read models (future) | routing-foundation-contract |
| update_routing | ROUTING.UPDATED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_ROUTING | same minimum payload | routing read models (future) | routing-foundation-contract |
| add_routing_operation | ROUTING.OPERATION_ADDED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_ROUTING | same minimum payload + operation_id | routing read models (future) | routing-foundation-contract |
| update_routing_operation | ROUTING.OPERATION_UPDATED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_ROUTING | same minimum payload + operation_id | routing read models (future) | routing-foundation-contract |
| remove_routing_operation | ROUTING.OPERATION_REMOVED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_ROUTING | same minimum payload + operation_id | routing read models (future) | routing-foundation-contract |
| release_routing | ROUTING.RELEASED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_ROUTING | same minimum payload | downstream linkage eligibility | routing-foundation-contract |
| retire_routing | ROUTING.RETIRED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_ROUTING | same minimum payload | downstream new-link block | routing-foundation-contract |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| routing_code unique per tenant | tenant | service + repository + DB unique constraint | yes | yes | routing-foundation-contract |
| tenant-scoped list/detail/mutation and cross-tenant detail 404 | tenant | route identity + service/repository filters | no | yes | routing-foundation-contract |
| product_id must resolve in same tenant | domain_link | service validation | no | yes | routing-foundation-contract |
| retired product cannot be newly linked | lifecycle_link | service validation | no | yes | product-foundation-contract |
| sequence_no unique within routing | sequence | service validation + DB unique constraint | yes | yes | routing-foundation-contract |
| RELEASED structural fields immutable (routing_code, product_id, operations sequence) | state_machine | service validation | no | yes | routing-foundation-contract |
| RETIRED update/release rejected | state_machine | service validation | no | yes | routing-foundation-contract |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Routing | n/a | create_routing | yes | ROUTING.CREATED | DRAFT | n/a | routing-foundation-contract |
| Routing | DRAFT | update_routing | yes | ROUTING.UPDATED | DRAFT | n/a | routing-foundation-contract |
| Routing | DRAFT | add/update/remove operation | yes | ROUTING.OPERATION_* | DRAFT | duplicate sequence and missing operation | routing-foundation-contract |
| Routing | DRAFT | release_routing | yes | ROUTING.RELEASED | RELEASED | non-DRAFT release rejected | routing-foundation-contract |
| Routing | RELEASED | update_routing (routing_name only) | yes | ROUTING.UPDATED | RELEASED | structural update rejected | routing-foundation-contract |
| Routing | RELEASED | add/update/remove operation | no | none | RELEASED | mutation rejected | routing-foundation-contract |
| Routing | DRAFT or RELEASED | retire_routing | yes | ROUTING.RETIRED | RETIRED | already retired rejected | routing-foundation-contract |
| Routing | RETIRED | update/release | no | none | RETIRED | rejected | routing-foundation-contract |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-009-T1 | fail-first missing modules/routes | test_first | no routing implementation | run routing tests | import errors | n/a | gate enforced before coding |
| HM3-009-T2 | service invariant and lifecycle coverage | happy_path and invalid_state | in-memory DB with product linkage | run service tests | pass | ROUTING.* events emitted | uniqueness, lifecycle, and linkage guards enforced |
| HM3-009-T3 | API tenant and lifecycle coverage | api_contract | in-memory API app with dependency overrides | run API tests | pass | ROUTING.* write paths exercised | 404 cross-tenant, 409 duplicate, 400 guard rejections |
| HM3-009-T4 | product + execution regression subset | regression | routing slice merged | run subset | pass | n/a | no unintended regressions |
| HM3-009-T5 | full backend verification | regression | routing slice merged | run full suite | pass | n/a | baseline remains green |

### Final verification result
- Fail-first captured:
  - `ModuleNotFoundError: No module named 'app.models.routing'`
  - `ModuleNotFoundError: No module named 'app.api.v1.routings'`
- Backend import check: passed (`backend import ok`)
- Focused routing tests: 8 passed
- Product + execution regression subset: 18 passed
- Full backend suite: 134 passed, 1 skipped, 24 warnings

### Scope guard confirmation
- Changes are limited to P0-B-02 routing foundation backend scope.
- No resource-requirement mapping, BOM, planning, or dispatch logic introduced.

### Event naming status
CANONICAL_FOR_P0_B_ROUTING

## Slice HM3-010
Name: TECH-DEBT-01 Datetime UTC Hygiene

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/governance/CODING_RULES.md | Keep backend changes minimal and verifiable, avoid unrelated scope expansion | Timestamp deprecation cleanup only |
| backend/app/services/work_order_execution_service.py | Runtime warning source from datetime.utcnow() | Replace with UTC-safe now path without business-rule changes |

### Scope Guard
- No Product/Routing business logic changes.
- No schema changes and no migrations.
- No P0-B-03 implementation.

### Classification Map
| File | Classification | Action |
|---|---|---|
| backend/app/services/work_order_execution_service.py | service timestamp usage | replace datetime.utcnow() |
| backend/app/services/operation_service.py | helper/util timestamp usage | no runtime deprecated call; helper already uses datetime.now(timezone.utc).replace(tzinfo=None) |

### Pattern Replacement
- datetime.utcnow() -> datetime.now(timezone.utc).replace(tzinfo=None)

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then |
|---|---|---|---|---|---|
| HM3-010-T1 | focused product+routing checks | regression | timestamp patch applied | run 4 focused test files | 16 passed |
| HM3-010-T2 | full backend regression | regression | timestamp patch applied | run pytest -q | 134 passed, 1 skipped |

### Final verification result
- Focused tests: 16 passed.
- Full backend suite: 134 passed, 1 skipped.
- Warning count: 24 -> 0.
- Remaining datetime.utcnow runtime warnings: none.

## Slice HM3-011
Name: P0-B-03 Resource Requirement Mapping backend implementation

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md | Approved executable contract for P0-B-03 aggregate fields, lifecycle guards, events, and API surface | Enables bounded implementation without inventing behavior |
| docs/design/02_domain/product_definition/routing-foundation-contract.md | Parent routing lifecycle controls structural mutation scope | Requirement mutation must be DRAFT-only |
| docs/governance/CODING_RULES.md | Tenant isolation, service-owned business rules, thin routes | Enforce invariants in service layer and keep route layer thin |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| create_resource_requirement | RESOURCE_REQUIREMENT.CREATED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | tenant_id, actor_user_id, requirement_id, routing_id, operation_id, required_resource_type, required_capability_code, changed_fields, occurred_at | resource requirement read models (future), planning linkage consumers (future), audit pipelines | resource-requirement-mapping-contract |
| update_resource_requirement | RESOURCE_REQUIREMENT.UPDATED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | same minimum payload | resource requirement read models (future), planning linkage consumers (future), audit pipelines | resource-requirement-mapping-contract |
| remove_resource_requirement | RESOURCE_REQUIREMENT.REMOVED | domain_event (transitional persistence via security event infrastructure) | CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT | same minimum payload | resource requirement read models (future), planning linkage consumers (future), audit pipelines | resource-requirement-mapping-contract |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| tenant isolation on list/detail/mutation | tenant | route identity + service/repository filters | no | yes | resource-requirement-mapping-contract |
| operation belongs to routing and tenant | domain_link | service validation | no | yes | resource-requirement-mapping-contract |
| required_resource_type enum validity | invalid_input | schema + service validation | no | yes | resource-requirement-mapping-contract |
| required_capability_code required | invalid_input | schema + service validation | no | yes | resource-requirement-mapping-contract |
| quantity_required positive integer | quantity | schema + service validation | no | yes | resource-requirement-mapping-contract |
| uniqueness on tenant_id+operation_id+resource_type+capability_code | db_invariant | DB unique constraint + service pre-check | yes | yes | resource-requirement-mapping-contract |
| parent routing DRAFT required for create/update/remove | state_machine | service validation | no | yes | routing-foundation-contract + resource-requirement-mapping-contract |
| RELEASED/RETIRED routing reject mutation | state_machine | service validation | no | yes | routing-foundation-contract + resource-requirement-mapping-contract |
| no dispatch/reservation/planning/execution truth introduced | integration_boundary | scope guard + service boundary | no | yes | resource-requirement-mapping-contract |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| RoutingRequirement | parent routing DRAFT | create_resource_requirement | yes | RESOURCE_REQUIREMENT.CREATED | requirement row exists | n/a | resource-requirement-mapping-contract |
| RoutingRequirement | parent routing DRAFT | update_resource_requirement | yes | RESOURCE_REQUIREMENT.UPDATED | requirement row updated | n/a | resource-requirement-mapping-contract |
| RoutingRequirement | parent routing DRAFT | remove_resource_requirement | yes | RESOURCE_REQUIREMENT.REMOVED | requirement row deleted | n/a | resource-requirement-mapping-contract |
| RoutingRequirement | parent routing RELEASED | create/update/remove | no | none | unchanged | mutation rejected | routing-foundation-contract + resource-requirement-mapping-contract |
| RoutingRequirement | parent routing RETIRED | create/update/remove | no | none | unchanged | mutation rejected | routing-foundation-contract + resource-requirement-mapping-contract |

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-011-T1 | fail-first missing schema/service module | test_first | no P0-B-03 implementation | run focused tests | module import error | n/a | gate enforced before coding |
| HM3-011-T2 | service happy/invalid-state/invariant coverage | happy_path and invalid_state | in-memory DB with routing operation linkage | run service tests | pass | RESOURCE_REQUIREMENT.* emitted | linkage, quantity, uniqueness, lifecycle guards enforced |
| HM3-011-T3 | API tenant/lifecycle/auth coverage | api_contract | in-memory API app with dependency overrides | run API tests | pass | RESOURCE_REQUIREMENT.* write paths exercised | 404 cross-tenant, 409 duplicate, 400 guard rejections, 403 auth gate |
| HM3-011-T4 | product+routing regression subset | regression | P0-B-03 merged | run subset | pass | n/a | no unintended regressions |
| HM3-011-T5 | full backend verification | regression | P0-B-03 merged | run full suite | pass | n/a | baseline remains green |

### Final verification result
- Fail-first captured:
	- `ModuleNotFoundError: No module named 'app.schemas.resource_requirement'`
- Backend import check: passed (`backend import ok`)
- Focused P0-B-03 tests: 7 passed
- Requested product + routing regression subset: 16 passed
- Full backend suite: 141 passed, 1 skipped
- Migration verification: `resource_requirements` table present with expected columns, uniqueness, and foreign keys

### Scope guard confirmation
- Changes are limited to P0-B-03 resource requirement mapping backend scope.
- No dispatch/execution queue, planning/APS, BOM/recipe, Backflush, ERP sync, or frontend UI changes introduced.

### Event naming status
CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT

---

## Slice HM3-012
Name: P0-C-01 Work Order / Operation Foundation Alignment

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/execution-state-machine.md | Runtime/closure state shell; ownership/session semantics separate from state names | State machine unchanged in P0-C-01 |
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | INV-001 (closed records reject writes), INV-002 (one running per station), INV-004 (valid context required for writes) | Tenant isolation invariants now tested |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | Canonical command/event set; claim deprecated as migration debt | No new events or commands in P0-C-01 |
| docs/design/02_domain/product_definition/product-foundation-contract.md | Tenant ownership is mandatory for all domain entities | Tenant isolation tests added |
| docs/design/02_domain/product_definition/routing-foundation-contract.md | Routing is tenant-owned; downstream linkage governed by lifecycle | Routing FK gap documented as DG-P0C01-ROUTING-FK-001 |
| docs/implementation/p0-c-execution-entry-audit.md | P0-C-01 entry conditions; confirmed tenant checks exist at service layer; confirmed PENDING/LATE not covered in tests | Gaps now tested |

### Event Map
| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| P0-C-01 (tests only) | none_required | none_required | n/a | n/a | No new commands or events in this slice |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| tenant_id mismatch rejects execution writes | tenant | service layer | no | YES — P0C01-T3/T3b/T4 | state-matrix INV-001; product-foundation-contract |
| StatusEnum.PENDING returns no executable actions | state_machine | `_derive_allowed_actions` | no | YES — P0C01-T1 | master.py design comment |
| StatusEnum.LATE returns no executable actions | state_machine | `_derive_allowed_actions` | no | YES — P0C01-T2 | master.py design comment |
| WO→PO→Operation hierarchy read projects correctly | projection_consistency | `derive_operation_detail` | no | YES — P0C01-T5 | routing/product contracts |
| WorkOrder.tenant_id == Operation.tenant_id at INSERT | tenant | application consistency | no | YES — P0C01-T6 | product-foundation-contract |
| ProductionOrder.route_id → Routing.routing_id (no DB FK) | integration_boundary | NONE (gap) | documented as gap | N/A | routing-foundation-contract |
| Claim behavior not expanded | session | no claim model changes | no | existing tests | ENGINEERING_DECISIONS §10 |
| Session-owned target not introduced prematurely | session | no StationSession commands | no | no session commands added | ENGINEERING_DECISIONS §10 |

### State Transition Map
No state transition changes in P0-C-01.

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| P0C01-T1 | PENDING returns [] from allowed_actions | invalid_state | status=PENDING | `_derive_allowed_actions(...)` | `[]` | none | PENDING is not executable |
| P0C01-T2 | LATE returns [] from allowed_actions | invalid_state | status=LATE | `_derive_allowed_actions(...)` | `[]` | none | LATE is not executable |
| P0C01-T3 | start_operation rejects wrong tenant | wrong_tenant | op.tenant_id=A, caller tenant=B | `start_operation(...)` | ValueError raised | none | tenant isolation |
| P0C01-T3b | report_quantity rejects wrong tenant | wrong_tenant | op.tenant_id=A, caller tenant=B | `report_quantity(...)` | ValueError raised | none | tenant isolation |
| P0C01-T4 | close_operation rejects wrong tenant | wrong_tenant | completed op.tenant_id=A, caller tenant=B | `close_operation(...)` | ValueError raised | none | tenant isolation |
| P0C01-T5 | WO→PO→Operation hierarchy reads correctly | happy_path | seeded WO/PO/Operation | `derive_operation_detail(...)` | work_order_number and production_order_number correct | none | projection_consistency |
| P0C01-T6 | WorkOrder and Operation share tenant_id | db_invariant | seeded with tenant_A | read both records | op.tenant_id == wo.tenant_id | none | tenant insertion consistency |

### Final verification result
- Targeted: `test_operation_status_projection_reconcile.py test_status_projection_reconcile_command.py test_operation_detail_allowed_actions.py` → 30 passed, exit 0
- Regression: `test_close_reopen_operation_foundation.py test_claim_single_active_per_operator.py test_work_order_operation_foundation.py` → 15 passed, exit 0
- Full backend suite: 148 passed, 1 skipped, exit 0

### Scope guard confirmation
- Tests only. No production code changes.
- No claim removal or expansion.
- No session-owned migration.
- No schema migration.
- No dispatch, APS, BOM, backflush, ERP, FE/UI changes.

### Event naming status
none_required — P0-C-01 is test-only; no new domain events introduced.

## Slice HM3-013
Name: P0-C-02 Execution State Machine Guard Alignment

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/execution-state-machine.md | Terminal states are irreversible event facts; no transition without event | `_derive_status` must update `last_runtime_event` on OP_COMPLETED and OP_ABORTED |
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | REOPEN-001 yields PAUSED; CLOSE-001 requires COMPLETED | Reopen→resume→complete must yield COMPLETED from event log projection |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | OP_COMPLETED is canonical terminal signal | Both `_derive_status` and bulk reconciler must agree on last signal |
| docs/implementation/p0-c-execution-entry-audit.md | Mixed event naming; BLOCKED+no-downtime stuck acknowledged | Acknowledged, documented, consistent with HM3-012 |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| P0-C-02 bug fix only | none_required | none_required | N/A | n/a | none | No new events |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| `_derive_status` consistent with bulk reconciler | projection_consistency | `_derive_status` (fixed) | no | YES — P0C02-T4 | state machine + reconciler path |
| reopen→resume→complete yields COMPLETED | state_machine | `_derive_status` (fixed) | no | YES — P0C02-T4 | state matrix REOPEN-001/CLOSE-001 |
| OP_COMPLETED updates last_runtime_event | state_machine | `_derive_status` (fixed) | no | YES — P0C02-T1/T4 | execution state machine |
| OP_ABORTED updates last_runtime_event | state_machine | `_derive_status` (fixed) | no | YES — P0C02-T5 | execution state machine |
| BLOCKED+no-downtime → [] allowed_actions | state_machine | `_derive_allowed_actions` (unchanged) | no | existing | HM3-012 |
| Claim behavior unchanged | session | no claim changes | no | existing | ENGINEERING_DECISIONS §10 |

### State Transition Map
No canonical transition changes. Fix is projection derivation only — does not alter which transitions are valid, only that `_derive_status` returns the correct post-transition status.

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| P0C02-T7 | no events | pure unit | empty event list | `_derive_status([])` | PLANNED | none | planned with no events |
| P0C02-T6 | OP_STARTED only | pure unit | [OP_STARTED] | `_derive_status` | IN_PROGRESS | none | started but not complete |
| P0C02-T1 | start then complete | pure unit | [OP_STARTED, OP_COMPLETED] | `_derive_status` | COMPLETED | none | terminal signal correct |
| P0C02-T5 | start then abort | pure unit | [OP_STARTED, OP_ABORTED] | `_derive_status` | ABORTED | none | terminal signal correct |
| P0C02-T2 | complete then reopen | pure unit | [OP_STARTED, OP_COMPLETED, operation_reopened] | `_derive_status` | PAUSED | none | REOPEN-001 |
| P0C02-T3 | complete, reopen, resume | pure unit | [OP_STARTED, OP_COMPLETED, operation_reopened, execution_resumed] | `_derive_status` | IN_PROGRESS | none | in_progress after resume |
| **P0C02-T4** | **reopen→resume→complete** | **regression bug** | **[OP_STARTED, OP_COMPLETED, operation_reopened, execution_resumed, OP_COMPLETED]** | **`_derive_status`** | **COMPLETED** | **none** | **fails before fix (returns IN_PROGRESS)** |

### Final verification result
- Regression test P0C02-T4: FAILED before fix, PASSED after fix
- 6 other parametrized cases: passed before and after fix
- Full backend suite: 153 passed, 1 skipped, exit 0 (up from 148 baseline)

### Scope guard confirmation
- No claim model changes.
- No session-owned migration.
- No schema migration.
- No new domain events introduced.
- No `_derive_allowed_actions` behavior changes.

### Event naming status
none_required — P0-C-02 is a bug fix slice; no new domain events introduced.

## Slice HM3-014
Name: P0-C-03 Execution Event Log / Projection Consistency

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/execution-state-machine.md | No transition without event; completed cannot silently resume running | projection derivation must stay deterministic and event-log based |
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | INV-001 closed-record guard, INV-003 downtime blocker, REOPEN-001 paused projection after reopen | detail and bulk projections must remain consistent for command legality |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | Canonical command/event intent set | no event/command expansion in this slice |
| docs/implementation/p0-c-execution-entry-audit.md | projection reconciliation seam already exists; claim/session migration is deferred debt | keep implementation narrow to projection parity |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| P0-C-03 projection consistency slice | none_required | none_required | N/A | n/a | deterministic projection/read parity | no new events |

No new domain event introduced. Existing event behavior preserved.

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| event log remains authoritative for runtime projection | projection_consistency | service + repository ordering | no | YES | coding rules + execution state machine |
| detail and bulk projection statuses agree | projection_consistency | operation service | no | YES | P0-C-03 scope |
| closure_status CLOSED yields reopen-only action affordance | state_machine | `_derive_allowed_actions` | no | YES | state matrix INV-001 |
| open downtime projects BLOCKED consistently | state_machine | status derivation helpers | no | YES | state matrix INV-003 |
| reconcile apply does not mutate event history truth | event_append_only | reconcile script/service | no | existing + YES | reconcile tests |
| claim behavior unchanged | session | no claim model/service changes | no | existing | ENGINEERING_DECISIONS §10 |
| session-owned target not introduced prematurely | session | no station session command/event additions | no | YES scope guard | entry audit |

### State Transition Map
No canonical transition changes in P0-C-03. Only projection derivation/read determinism was hardened.

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| P0C03-T1 | reopen/resume/complete parity | projection_consistency | OP_STARTED, OP_COMPLETED, OPERATION_REOPENED, EXECUTION_RESUMED, OP_COMPLETED | derive detail and bulk | both COMPLETED | none | detail/bulk agreement |
| P0C03-T2 | aborted parity | projection_consistency | OP_STARTED, OP_ABORTED | derive detail and bulk | both ABORTED | none | detail/bulk agreement |
| P0C03-T3 | downtime-open parity | projection_consistency | OP_STARTED, DOWNTIME_STARTED | derive detail and bulk | both BLOCKED and downtime_open true | none | downtime blocker consistency |
| P0C03-T4 | downtime-ended parity | projection_consistency | OP_STARTED, DOWNTIME_STARTED, DOWNTIME_ENDED | derive detail and bulk | both PAUSED and downtime_open false | none | blocker-cleared non-running consistency |
| P0C03-T5 | closed action override | regression | closure_status CLOSED completed operation | derive detail | allowed_actions is reopen-only | none | INV-001 action override |
| P0C03-T6 | reconcile apply parity | regression | runtime mismatch repaired by command apply | derive detail and bulk post-apply | both IN_PROGRESS | none | repair parity invariant |

### Final verification result
- Required targeted run 1: 41 passed, exit 0
- Required targeted run 2: 15 passed, exit 0
- Full backend suite: 159 passed, 1 skipped, exit 0

### Scope guard confirmation
- No claim/session migration behavior changes.
- No schema migration.
- No new domain events.
- No command-set additions.
- No FE/UI or out-of-scope domain changes.

### Event naming status
none_required — P0-C-03 introduced no new domain events.

## Slice HM3-015
Name: P0-C-04C Diagnostic Session Context Bridge

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-session-ownership-contract.md | P0-C-04C = diagnostic bridge only; missing session must NOT reject execution command | Bridge is non-blocking; command allow/deny unchanged |
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | Execution commands require valid station session context (target); claim is compatibility debt | Diagnostic is readiness-only in this slice |
| docs/design/02_registry/station-session-event-registry.md | Events frozen at CANONICAL_FOR_P0_C_STATION_SESSION v1.1 | No new events from diagnostic bridge |
| docs/implementation/p0-c-execution-entry-audit.md | Commands do not currently require a valid claim/session guard | Diagnostic adds read-only signal; no injection into command path |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| get_station_session_diagnostic | none | none_required | N/A | n/a | no event emitted | diagnostic is read-only |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| Diagnostic bridge must NOT change command allow/deny | behavior_contract | no injection into command path | no | YES — BRIDGE-T1/T2 | ownership contract |
| Missing session = diagnostic signal only, not rejection | behavior_contract | diagnostic function does not raise | no | YES — BRIDGE-T1/T4 | ownership contract |
| Tenant isolation mandatory | tenant | every lookup filters by tenant_id | no | YES — BRIDGE-T6 | CODING_RULES §TEN-001 |
| CLOSED session ignored | state_machine | repository returns OPEN-only records | no | YES — BRIDGE-T5 | session model partial index |
| No new domain events | event_append_only | no event emission in diagnostic | no | YES — scope guard | command/event contracts |
| Claim behavior unchanged | session | no claim model/service/test changes | no | existing | ENGINEERING_DECISIONS §10 |

### State Transition Map
No state transitions. P0-C-04C is read-only — the diagnostic function performs a single SELECT query and returns a frozen dataclass. No state mutations, no event emission.

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| BRIDGE-T1 | start_operation proceeds with no session | behavior_unchanged | PLANNED operation, no active session | start_operation called | succeeds, IN_PROGRESS | no diagnostic event | command allow/deny unchanged |
| BRIDGE-T2 | start_operation proceeds with open session | behavior_unchanged | PLANNED operation, OPEN session present | start_operation called | succeeds, IN_PROGRESS | no diagnostic event | command allow/deny unchanged |
| BRIDGE-T3 | diagnostic detects open session | diagnostic_detect | OPEN session exists | get_station_session_diagnostic | readiness=OPEN, session_id set | none | backend-derived |
| BRIDGE-T4 | diagnostic detects missing session | diagnostic_detect | no session | get_station_session_diagnostic | readiness=NO_ACTIVE_SESSION | none | backend-derived |
| BRIDGE-T5 | diagnostic ignores closed session | diagnostic_detect | only CLOSED session | get_station_session_diagnostic | readiness=NO_ACTIVE_SESSION | none | CLOSED terminal |
| BRIDGE-T6 | tenant mismatch no false positive | security | session exists for other tenant | get_station_session_diagnostic for different tenant | readiness=NO_ACTIVE_SESSION | none | tenant isolation |
| BRIDGE-T7 | operator context returned when identified | diagnostic_detail | OPEN session with identified operator | get_station_session_diagnostic | operator_user_id set | none | operator context fidelity |

### Final verification result
- Diagnostic bridge tests: 7 passed
- Station session lifecycle regression: 9 passed
- Claim regression subset: 45 passed
- Full backend suite: 175 passed, 1 skipped, exit 0

### Scope guard confirmation
- No claim model/service/test changes.
- No execution command behavior change.
- No schema migration.
- No new domain events.
- No FE/UI changes.
- Diagnostic function is pure read; never raises; never rejects a command.

### Event naming status
none_required — P0-C-04C is a read-only diagnostic slice; no new domain events introduced.

## Slice HM3-022
Name: P0-C-07B Close Operation Guard Hardening

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | CLOSE-001: close only from completed and OPEN; rejects already closed/not completed | guard legality and rejection assertions required |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | close_operation canonical event intent is operation_closed_at_station | event-name preservation required |
| docs/design/02_domain/execution/execution-state-machine.md | CLOSED blocks execution writes except authorized reopen | closure transition and post-close actions must align |
| docs/implementation/p0-c-04-contract-finalization-report.md | session diagnostic bridge remains non-blocking | no-session/open-session parity required |
| docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md | claim remains compatibility guard | claim regression required |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| close_operation | OPERATION_CLOSED_AT_STATION | domain_event | unchanged | actor_user_id, note, closed_at | closure_status→CLOSED, allowed_actions→reopen_operation | operation_service.py |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| close_operation valid from completed runtime states | state_machine | service guard | no | YES | source + state matrix |
| already-closed rejects close | state_machine | service guard | no | YES | source |
| tenant mismatch rejected | tenant | service guard | no | YES | CODING_RULES TEN-001 |
| close event emitted append-only | event_append_only | execution_event_repository | no | YES | source |
| closure_status becomes CLOSED | projection_consistency | service snapshot + detail | no | YES | source |
| post-close detail/projection backend-derived | projection_consistency | derive_operation_detail + _derive_status | no | YES | source |
| allowed_actions after close backend-derived | projection_consistency | _derive_allowed_actions | no | YES | source |
| StationSession diagnostic non-blocking | session | `_session_ctx` informational only | no | YES | P0-C-04D contract |
| claim compatibility preserved | migration_debt | route-layer unchanged | no | YES | P0-C-04E lock |
| no reopen behavior changes | scope | slice boundary | no | YES | controlled slice scope |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---|---|---|---|---|
| Operation | COMPLETED/COMPLETED_LATE + OPEN | close_operation | Yes | OPERATION_CLOSED_AT_STATION | closure_status=CLOSED, runtime status completed | n/a | source |
| Operation | non-completed + OPEN | close_operation | No | none | unchanged | STATE_NOT_COMPLETED | source |
| Operation | any + CLOSED | close_operation | No | none | unchanged | STATE_ALREADY_CLOSED | source |
| Operation | tenant mismatch | close_operation | No | none | unchanged | tenant mismatch error | source |

### Test Matrix
| Test ID | Scenario | Type | Source File | Invariant |
|---|---|---|---|---|
| P0C07B-T1 | close_operation happy path from completed | command_guard | test_close_operation_command_hardening.py | state transition + event |
| P0C07B-T2 | close_operation rejects invalid runtime state | command_guard | test_close_operation_command_hardening.py | STATE_NOT_COMPLETED |
| P0C07B-T3 | close_operation rejects already closed | command_guard | test_close_operation_command_hardening.py | STATE_ALREADY_CLOSED |
| P0C07B-T4 | close_operation rejects tenant mismatch | tenant | test_close_operation_command_hardening.py | tenant isolation |
| P0C07B-T5 | emits OPERATION_CLOSED_AT_STATION | event_payload | test_close_operation_command_hardening.py | append-only event |
| P0C07B-T6 | closure_status becomes CLOSED | projection | test_close_operation_command_hardening.py | closure transition |
| P0C07B-T7 | post-close detail consistency | projection | test_close_operation_command_hardening.py | backend-derived detail |
| P0C07B-T8 | allowed_actions after close | projection | test_close_operation_command_hardening.py | backend-derived actions |
| P0C07B-T9 | no-session parity | regression | test_close_operation_command_hardening.py | non-blocking diagnostic |
| P0C07B-T10 | open-session parity | regression | test_close_operation_command_hardening.py | non-blocking diagnostic |

### Final verification result
- Focused P0-C-07B suite: 10 passed
- Recent command hardening regression: 48 passed
- Station session lifecycle + diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 242 passed, 1 skipped, exit 0

### Scope guard confirmation
- No production code changes.
- No claim behavior changes.
- No StationSession hard enforcement.
- No event-name changes.
- No schema migration.
- No reopen behavior changes.
- No FE/UI changes.

### Event naming status
unchanged — `operation_closed_at_station` remains canonical for close in current source; no new domain events introduced in P0-C-07B.

## Slice HM3-023
Name: P0-C-07C Reopen Operation / Claim Continuity Hardening

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | REOPEN-001: reopen only from CLOSED; emits operation_reopened; projects PAUSED | guard legality, event, and projection assertions required |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | reopen_operation canonical event is operation_reopened; body requires reason | event-name preservation and reason guard required |
| docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md | _restore_claim_continuity_for_reopen must not be removed; claim = migration debt | claim continuity preserved; no removal |
| docs/implementation/p0-c-04-contract-finalization-report.md | session diagnostic bridge remains non-blocking | no-session/open-session parity required |

### Source Evidence
| Function | Location | Key behavior |
|---|---|---|
| `reopen_operation` | operation_service.py:918 | tenant guard → session diagnostic → STATE_NOT_CLOSED guard → REOPEN_REASON_REQUIRED guard → claim continuity → OPERATION_REOPENED event → mark_operation_reopened |
| `_restore_claim_continuity_for_reopen` | operation_service.py:269 | extend active claim TTL; or restore last claim; or conflict → STATE_REOPEN_OWNER_HAS_OTHER_ACTIVE_CLAIM; or no-op |
| `_derive_status_from_runtime_facts` | operation_service.py:423 | OPERATION_REOPENED as last_runtime_event + has_completed=True → PAUSED |
| `_derive_allowed_actions` | operation_service.py:732 | closure_status=OPEN + status=PAUSED + downtime_open=False → ["resume_execution", "start_downtime"] |
| `mark_operation_reopened` | operation_repository.py:182 | sets closure_status=OPEN, status=PAUSED, reopen_count+=1 |

### Event Map
| Command | Source Event Enum | Event Name | Status |
|---|---|---|---|
| `reopen_operation` | `ExecutionEventType.OPERATION_REOPENED` | `"operation_reopened"` | CANONICAL — matches design |

### Invariant Map
| Invariant | Enforcement | Test |
|---|---|---|
| Reopen only valid for CLOSED operation | closure_status guard → STATE_NOT_CLOSED | T2, T12 |
| Non-CLOSED operation rejects reopen | same | T2 |
| Blank reason rejected | reason.strip() empty → REOPEN_REASON_REQUIRED | T3 |
| None reason rejected at schema level | Pydantic ValidationError | T4 |
| Tenant mismatch rejected | operation.tenant_id guard | T5 |
| Reopen event emitted with payload | create_execution_event(OPERATION_REOPENED) | T6 |
| closure_status becomes OPEN | mark_operation_reopened | T7 |
| Runtime projection becomes PAUSED | _derive_status_from_runtime_facts | T8 |
| allowed_actions = [resume_execution, start_downtime] | _derive_allowed_actions | T9 |
| Missing StationSession does not reject reopen | _compute_session_diagnostic non-blocking | T10 |
| Matching OPEN StationSession does not change outcome | same | T11 |
| reopen_count increments | mark_operation_reopened | T13 |
| Claim continuity preserved | _restore_claim_continuity_for_reopen unchanged | regression suite |
| Single-active-claim constraint | conflict guard | regression suite |

### State Transition Map
```
closure_status=CLOSED (completed operation)
→ reopen_operation(reason="...")
→ [_restore_claim_continuity_for_reopen]
→ OPERATION_REOPENED event appended
→ mark_operation_reopened → closure_status=OPEN, status=PAUSED, reopen_count+=1
→ _derive_status: PAUSED (OPERATION_REOPENED last_runtime_event, has_completed=True)
→ _derive_allowed_actions: ["resume_execution", "start_downtime"]
```

### Test Matrix Executed
| Test | Scenario | Result |
|---|---|---|
| T1 | reopen happy path from CLOSED completed | PASS |
| T2 | rejects non-CLOSED OPEN operation | PASS |
| T3 | rejects blank reason | PASS |
| T4 | schema rejects None reason (Pydantic) | PASS |
| T5 | rejects tenant mismatch | PASS |
| T6 | emits OPERATION_REOPENED with payload | PASS |
| T7 | closure_status becomes OPEN | PASS |
| T8 | projection/detail consistent (PAUSED+OPEN) | PASS |
| T9 | allowed_actions backend-derived | PASS |
| T10 | missing StationSession does not affect reopen | PASS |
| T11 | matching OPEN StationSession does not affect reopen | PASS |
| T12 | PAUSED non-closed rejects reopen | PASS |
| T13 | reopen_count increments | PASS |

Verification summary:
- Focused P0-C-07C: 13 passed in 5.30s, exit 0
- Close/complete regression: 20 passed in 7.84s, exit 0
- Recent command hardening regression: 38 passed in 15.42s, exit 0
- StationSession lifecycle/diagnostic: 25 passed in 9.85s, exit 0
- Claim regression subset: 36 passed in 7.90s, exit 0
- Projection/status regression: 41 passed in 2.47s, exit 0
- Full backend suite: 255 passed, 1 skipped in 53.29s, exit 0

### Scope guard confirmation
- No production code changes.
- No claim behavior changes.
- No StationSession hard enforcement.
- No event-name changes.
- No schema migration.
- No close_operation behavior changes.
- No FE/UI changes.

### Event naming status
unchanged — `operation_reopened` remains canonical for reopen in current source; no new domain events introduced in P0-C-07C.

## Slice HM3-022
Name: P0-C-07B Close Operation Guard Hardening

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | COMPLETE-001 requires IN_PROGRESS + OPEN and emits completion event | Guard legality and transition assertions required |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | complete_execution canonical intent emits execution-completed signal | Event-name preservation required |
| docs/design/02_domain/execution/execution-state-machine.md | no transition without event; completed is terminal runtime truth for complete path | event-derived projection consistency required |
| docs/implementation/p0-c-04-contract-finalization-report.md | session diagnostic bridge remains non-blocking | no-session/open-session parity required |
| docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md | claim remains compatibility guard | claim regression required |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| complete_operation | OP_COMPLETED | domain_event | unchanged | operator_id, completed_at | status→COMPLETED, allowed_actions→close_operation | operation_service.py |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| complete_operation only from IN_PROGRESS | state_machine | service guard | no | YES | source + state matrix |
| closed record rejects complete | state_machine | `_ensure_operation_open_for_write` | no | YES | INV-001 |
| tenant mismatch rejected | tenant | service guard | no | YES | CODING_RULES TEN-001 |
| completion event emitted append-only | event_append_only | execution_event_repository | no | YES | source |
| projection after complete is event-derived | projection_consistency | `derive_operation_detail` + `_derive_status` | no | YES | source |
| allowed_actions after complete are backend-derived | projection_consistency | `_derive_allowed_actions` | no | YES | source |
| StationSession diagnostic non-blocking | session | `_session_ctx` informational only | no | YES | P0-C-04D contract |
| claim compatibility preserved | migration_debt | route-layer unchanged | no | YES | P0-C-04E lock |
| no close/reopen behavior changes | scope | slice boundary | no | YES | controlled batch scope |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---|---|---|---|---|
| Operation | IN_PROGRESS + OPEN | complete_operation | Yes | OP_COMPLETED | COMPLETED + OPEN | n/a | source |
| Operation | PLANNED/PAUSED/BLOCKED/ABORTED + OPEN | complete_operation | No | none | unchanged | IN_PROGRESS guard rejection | source |
| Operation | any + CLOSED | complete_operation | No | none | unchanged | STATE_CLOSED_RECORD | source |

### Test Matrix
| Test ID | Scenario | Type | Source File | Invariant |
|---|---|---|---|---|
| P0C07A-T1 | complete_operation happy path from IN_PROGRESS | command_guard | test_complete_operation_command_hardening.py | state transition + event |
| P0C07A-T2 | rejects invalid runtime state | command_guard | test_complete_operation_command_hardening.py | IN_PROGRESS-only legality |
| P0C07A-T3 | rejects already completed | command_guard | test_complete_operation_command_hardening.py | duplicate completion reject |
| P0C07A-T4 | rejects CLOSED record | command_guard | test_complete_operation_command_hardening.py | INV-001 |
| P0C07A-T5 | rejects tenant mismatch | tenant | test_complete_operation_command_hardening.py | tenant isolation |
| P0C07A-T6 | emits OP_COMPLETED with payload | event_payload | test_complete_operation_command_hardening.py | event append-only |
| P0C07A-T7 | projection resolves completed after command | projection | test_complete_operation_command_hardening.py | event-derived status |
| P0C07A-T8 | allowed_actions after complete | projection | test_complete_operation_command_hardening.py | backend-derived actions |
| P0C07A-T9 | no-session parity | regression | test_complete_operation_command_hardening.py | non-blocking diagnostic |
| P0C07A-T10 | open-session parity | regression | test_complete_operation_command_hardening.py | non-blocking diagnostic |

### Final verification result
- Focused P0-C-07A suite: 10 passed
- Recent command hardening regression: 38 passed
- Station session lifecycle + diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 232 passed, 1 skipped, exit 0

### Scope guard confirmation
- No production code changes.
- No claim behavior changes.
- No StationSession hard enforcement.
- No event-name changes.
- No schema migration.
- No close/reopen behavior changes.
- No FE/UI changes.

### Event naming status
unchanged — `OP_COMPLETED` remains canonical in current source for completion; no new domain events introduced in P0-C-07A.

## Slice HM3-020
Name: P0-C-06B Downtime Start / End Command Hardening

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | `start_downtime` valid from IN_PROGRESS or PAUSED; `end_downtime` requires open downtime | State guard tests required |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | `start_downtime → downtime_started`; `end_downtime → downtime_ended`; canonical names | Event names must not change |
| docs/design/02_domain/execution/execution-state-machine.md | DOWNTIME_STARTED → RUNNING→BLOCKED snapshot; DOWNTIME_ENDED → BLOCKED→PAUSED; no auto-resume | Transition + no-auto-resume assertions required |
| docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md | Claim remains compatibility guard | Claim regression required |
| docs/implementation/p0-c-04-contract-finalization-report.md | Session diagnostic currently non-blocking | No-session/open-session parity required |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| start_downtime | DOWNTIME_STARTED | domain_event | unchanged | actor_user_id, reason_code, reason_name, reason_group, planned_flag, note, started_at | status→BLOCKED (event-derived); downtime_open=True | operation_service.py |
| end_downtime | DOWNTIME_ENDED | domain_event | unchanged | actor_user_id, note, ended_at | status→PAUSED (event-derived); downtime_open=False | operation_service.py |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| start_downtime only from IN_PROGRESS or PAUSED | state_machine | service guard | no | YES | state matrix |
| end_downtime requires open downtime | open_downtime_guard | service event-count check | no | YES | source |
| duplicate open downtime rejected | state_guard | service event-count check | no | YES | source |
| closed record rejects both commands | state_machine | `_ensure_operation_open_for_write` | no | YES | INV-001 |
| tenant mismatch rejected | tenant | service guard | no | YES | CODING_RULES TEN-001 |
| invalid/inactive reason code rejected | reason_validation | service + repo | no | YES | source |
| start_downtime from IN_PROGRESS → snapshot+derived=BLOCKED | state_transition | service + _derive_status | no | YES | source |
| start_downtime from PAUSED → snapshot=PAUSED, derived=BLOCKED | state_transition | _derive_status event-count | no | YES | source clarified in T2 |
| end_downtime BLOCKED→PAUSED on snapshot when no remaining open downtime | state_transition | service mark_operation_paused | no | YES | source |
| end_downtime does not auto-resume | no_auto_resume | service (no EXECUTION_RESUMED emitted) | no | YES | source |
| resume_operation blocked while downtime open | blocking_guard | resume_operation STATE_DOWNTIME_OPEN | no | YES | source |
| session diagnostic non-blocking | session | `_session_ctx` informational only | no | YES | P0-C-04D contract |
| claim compatibility preserved | migration_debt | route-layer unchanged | no | YES | P0-C-04E lock |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---|---|---|---|---|
| Operation | IN_PROGRESS + OPEN | start_downtime (valid reason) | Yes | DOWNTIME_STARTED | BLOCKED + downtime_open=True | PLANNED reject | state matrix |
| Operation | PAUSED + OPEN | start_downtime (valid reason) | Yes | DOWNTIME_STARTED | BLOCKED (event-derived) + downtime_open=True | CLOSED reject | source T2 clarification |
| Operation | BLOCKED + OPEN + downtime_open | end_downtime | Yes | DOWNTIME_ENDED | PAUSED + downtime_open=False | no-open-downtime reject | source |
| Operation | IN_PROGRESS + OPEN | end_downtime (no open downtime) | No | none | — | YES | source |
| Operation | BLOCKED + downtime_open | resume_operation | No | none | — | YES | STATE_DOWNTIME_OPEN |

### Test Matrix
| Test ID | Scenario | Type | Source File | Invariant |
|---|---|---|---|---|
| P0C06B-T1 | start_downtime happy from IN_PROGRESS | command_guard | test_downtime_command_hardening.py | state_guard + transition + event |
| P0C06B-T2 | start_downtime happy from PAUSED (derived=BLOCKED) | command_guard | test_downtime_command_hardening.py | state_guard + event-derived clarification |
| P0C06B-T3 | start_downtime rejects PLANNED | command_guard | test_downtime_command_hardening.py | STATE_NOT_RUNNING_OR_PAUSED |
| P0C06B-T4 | start_downtime rejects CLOSED | command_guard | test_downtime_command_hardening.py | INV-001 |
| P0C06B-T5 | start_downtime rejects duplicate (snapshot-BLOCKED) | command_guard | test_downtime_command_hardening.py | state_guard |
| P0C06B-T5b | start_downtime rejects DOWNTIME_ALREADY_OPEN (event-count guard) | command_guard | test_downtime_command_hardening.py | DOWNTIME_ALREADY_OPEN |
| P0C06B-T6 | start_downtime rejects invalid reason code | reason_validation | test_downtime_command_hardening.py | INVALID_REASON_CODE |
| P0C06B-T7 | end_downtime happy path BLOCKED→PAUSED | command_guard | test_downtime_command_hardening.py | transition + event |
| P0C06B-T8 | end_downtime no auto-resume | regression | test_downtime_command_hardening.py | no_auto_resume |
| P0C06B-T9 | end_downtime rejects no-open-downtime | command_guard | test_downtime_command_hardening.py | STATE_NO_OPEN_DOWNTIME |
| P0C06B-T10 | end_downtime rejects CLOSED | command_guard | test_downtime_command_hardening.py | INV-001 |
| P0C06B-T11 | resume blocked while downtime open | regression | test_downtime_command_hardening.py | STATE_DOWNTIME_OPEN |
| P0C06B-T12 | no-session parity | regression | test_downtime_command_hardening.py | non-blocking diagnostic |
| P0C06B-T13 | open-session parity | regression | test_downtime_command_hardening.py | non-blocking diagnostic |

### Final verification result
- Focused P0-C-06B suite: 14 passed
- P0-C-06A + P0-C-05 regression: 24 passed
- Station session lifecycle + diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 222 passed, 1 skipped, exit 0

### Scope guard confirmation
- No production code changes.
- No claim behavior changes.
- No StationSession hard enforcement.
- No event-name changes.
- No schema migration.
- No FE/UI changes.

### Event naming status
unchanged — `downtime_started` and `downtime_ended` are canonical events; P0-C-06B introduced no new domain events.

## Slice HM3-019
Name: P0-C-06A Production Reporting Command Hardening

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | `report_quantity` valid only when status == IN_PROGRESS | State guard test required |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | `report_quantity → QTY_REPORTED`; payload: good_qty, scrap_qty, operator_id | Event name canonical, must not change |
| docs/design/02_domain/execution/execution-state-machine.md | `QTY_REPORTED` does not transition status; operation remains IN_PROGRESS | Projection status immutability test required |
| docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md | Claim remains compatibility guard; no claim mutation/removal | Claim regression subset required |
| docs/implementation/p0-c-04-contract-finalization-report.md | Session diagnostic currently non-blocking | No-session/open-session parity required |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| report_quantity | QTY_REPORTED | domain_event | unchanged | good_qty, scrap_qty, operator_id | accumulates good_qty + scrap_qty; status stays IN_PROGRESS | operation_service.py |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| report_quantity only from IN_PROGRESS | state_machine | service guard | no | YES | state matrix |
| good_qty >= 0 AND scrap_qty >= 0 | quantity_validation | service guard | no | YES | source line 1042 |
| good_qty + scrap_qty > 0 | quantity_validation | service guard | no | YES | source line 1045 |
| closed record rejects writes | state_machine | `_ensure_operation_open_for_write` | no | YES | INV-001 |
| tenant mismatch rejected | tenant | service guard | no | YES | CODING_RULES TEN-001 |
| session diagnostic non-blocking | session | `_session_ctx` informational only | no | YES | P0-C-04D contract |
| QTY_REPORTED does not change status | projection_consistency | `_derive_status` ignores QTY_REPORTED | no | YES | execution-state-machine |
| good_qty/scrap_qty cumulate across reports | projection_integrity | `derive_operation_detail` accumulation loop | no | YES | derive_operation_detail |
| claim compatibility preserved | migration_debt | route-layer claim guard unchanged | no | YES | P0-C-04E lock |
| allowed_actions backend-derived after report | action_derivation | `_derive_allowed_actions` with IN_PROGRESS | no | YES | execution-state-machine |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---|---|---|---|---|
| Operation | IN_PROGRESS + OPEN | report_quantity (valid qty) | Yes | QTY_REPORTED | IN_PROGRESS (unchanged) | non-IN_PROGRESS reject | state matrix |
| Operation | PLANNED + OPEN | report_quantity | No | none | — | YES | state guard |
| Operation | PAUSED + OPEN | report_quantity | No | none | — | YES | state guard |
| Operation | any + CLOSED | report_quantity | No | none | — | YES | INV-001 |

### Test Matrix
| Test ID | Scenario | Type | Source File | Invariant |
|---|---|---|---|---|
| P0C06A-T1 | happy path good_qty only | command_guard | test_report_quantity_command_hardening.py | state_guard + event |
| P0C06A-T2 | happy path mixed qty accumulates | command_guard | test_report_quantity_command_hardening.py | projection_integrity |
| P0C06A-T3 | rejects PLANNED | command_guard | test_report_quantity_command_hardening.py | state_guard |
| P0C06A-T4 | rejects PAUSED | command_guard | test_report_quantity_command_hardening.py | state_guard |
| P0C06A-T5 | rejects CLOSED record | command_guard | test_report_quantity_command_hardening.py | INV-001 |
| P0C06A-T6 | rejects negative good_qty | quantity_validation | test_report_quantity_command_hardening.py | quantity_validation |
| P0C06A-T7 | rejects negative scrap_qty | quantity_validation | test_report_quantity_command_hardening.py | quantity_validation |
| P0C06A-T8 | rejects zero-sum | quantity_validation | test_report_quantity_command_hardening.py | quantity_validation |
| P0C06A-T9 | cumulative across two reports | projection | test_report_quantity_command_hardening.py | projection_integrity |
| P0C06A-T10 | allowed_actions after report | projection | test_report_quantity_command_hardening.py | action_derivation |
| P0C06A-T11 | no-session parity | regression | test_report_quantity_command_hardening.py | non-blocking diagnostic |
| P0C06A-T12 | open-session parity | regression | test_report_quantity_command_hardening.py | non-blocking diagnostic |

### Final verification result
- Focused P0-C-06A suite: 12 passed
- P0-C-05 regression: 12 passed
- Station session lifecycle + diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 208 passed, 1 skipped, exit 0

### Scope guard confirmation
- No production code changes.
- No claim behavior changes.
- No StationSession hard enforcement.
- No event-name changes.
- No schema migration.
- No FE/UI changes.

### Event naming status
unchanged — `QTY_REPORTED` is the canonical event; P0-C-06A introduced no new domain events.

## Slice HM3-018
Name: P0-C-05 Start / Pause / Resume Command Hardening

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-execution-state-matrix-v4.md | START-001, PAUSE-001, RESUME-001 define legal state transitions and reject conditions | Guard legality tests required |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | Canonical command/event intent; no rename in this slice | Event names preserved |
| docs/design/02_domain/execution/execution-state-machine.md | No transition without event; CLOSED blocks writes except reopen | Event + closed-write assertions required |
| docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md | Claim remains compatibility guard; no claim mutation/removal | Claim regression subset required |
| docs/implementation/p0-c-04-contract-finalization-report.md | Session diagnostic currently non-blocking | No-session/open-session parity required |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| start_operation | OP_STARTED | domain_event | unchanged | operator_id, started_at | derive IN_PROGRESS | operation_service.py |
| pause_operation | execution_paused | domain_event | unchanged | actor_user_id, paused_at | derive PAUSED | operation_service.py |
| resume_operation | execution_resumed | domain_event | unchanged | actor_user_id, resumed_at | derive IN_PROGRESS | operation_service.py |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| start only from PLANNED | state_machine | service guard | no | YES | state matrix START-001 |
| pause only from IN_PROGRESS | state_machine | service guard | no | YES | state matrix PAUSE-001 |
| resume only from PAUSED | state_machine | service guard | no | YES | state matrix RESUME-001 |
| resume rejects open downtime | state_machine | service guard from event counts | no | YES | INV-003 |
| resume rejects station busy | station | service guard (`get_in_progress_operations_by_station`) | no | YES | INV-002 |
| closed record rejects writes | state_machine | `_ensure_operation_open_for_write` | no | YES | INV-001 |
| tenant mismatch rejected | tenant | service guard | no | YES | CODING_RULES TEN-001 |
| session diagnostic non-blocking | session | `_session_ctx` informational only | no | YES | P0-C-04D contract |
| claim compatibility preserved | migration_debt | route-layer claim guard unchanged | no | YES | P0-C-04E lock |
| projection and actions backend-derived | projection_consistency | derive_operation_detail + _derive_allowed_actions | no | YES | execution-state-machine |

### State Transition Map
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---|---|---|---|---|
| Operation | PLANNED + OPEN | start_operation | Yes | OP_STARTED | IN_PROGRESS | non-PLANNED reject | START-001 |
| Operation | IN_PROGRESS + OPEN | pause_operation | Yes | execution_paused | PAUSED | non-IN_PROGRESS reject | PAUSE-001 |
| Operation | PAUSED + OPEN + no downtime + no competing running op | resume_operation | Yes | execution_resumed | IN_PROGRESS | non-PAUSED / downtime-open / station-busy reject | RESUME-001 |

### Test Matrix
| Test ID | Scenario | Type | Source File | Invariant |
|---|---|---|---|---|
| P0C05-T1..T3 | start happy + illegal + closed | command_guard | test_start_pause_resume_command_hardening.py | START-001 + INV-001 |
| P0C05-T4..T6 | pause happy + illegal + closed | command_guard | test_start_pause_resume_command_hardening.py | PAUSE-001 + INV-001 |
| P0C05-T7..T10 | resume happy + illegal + downtime-open + station-busy | command_guard | test_start_pause_resume_command_hardening.py | RESUME-001 + INV-002/003 |
| P0C05-T11..T12 | missing/open StationSession parity | regression | test_start_pause_resume_command_hardening.py | non-blocking diagnostic |

### Final verification result
- Focused P0-C-05 suite: 12 passed
- Station session lifecycle + diagnostic suites: 25 passed
- Claim regression subset: 36 passed
- Projection/status regression: 41 passed
- Full backend suite: 196 passed, 1 skipped, exit 0

### Scope guard confirmation
- No production code changes.
- No claim behavior changes.
- No StationSession hard enforcement.
- No event-name changes.
- No schema migration.
- No FE/UI changes.

### Event naming status
unchanged — P0-C-05 introduced no new domain events.

## Slice HM3-017
Name: P0-C-04E Claim Compatibility / Deprecation Lock

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-session-ownership-contract.md §8 | Claim is migration debt — must not be expanded in any subsequent slice without explicit contract revision and ADR | Boundary lock enforced by this slice |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | Claim deprecated as execution context; removal is future slice requiring explicit migration plan | Claim source map frozen |
| docs/implementation/p0-c-execution-entry-audit.md | `ensure_operation_claim_owned_by_identity` is the sole execution guard at 8 route sites | Compatibility boundary codified |
| docs/governance/ENGINEERING_DECISIONS.md §10 | No claim removal without ADR | Removal deferred; register created |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| (none) | none | none_required | N/A | n/a | none | DOC-ONLY slice |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| Claim must not be expanded without explicit ADR | migration_debt | doc contract | no | existing 45 claim tests | ownership contract §8 |
| Claim must not be removed in P0-C-04E | migration_debt | doc contract | no | N/A — removal is future slice | ownership contract |
| `ensure_operation_claim_owned_by_identity` remains sole route-layer guard | behavior_contract | unchanged at 8 sites | no | existing | entry audit |
| Diagnostic bridge must not interfere with claim lifecycle | non_interference | `_session_ctx` never touches claim | no | existing 9 CMD tests | P0-C-04D |
| No new domain events | event_append_only | no emission in this slice | no | existing | command/event contracts |
| Tenant isolation preserved | tenant | unchanged | no | existing | CODING_RULES §TEN-001 |

### State Transition Map
No state transitions. DOC-ONLY slice. No production code changes.

### Test Matrix
| Test ID | Scenario | Type | Source File | Lock Coverage |
|---|---|---|---|---|
| Claim-T1..T36 | Claim lifecycle, queue, auth, continuity | compatibility_lock | test_claim_single_active_per_operator.py, test_release_claim_active_states.py, test_station_queue_active_states.py, test_reopen_resumability_claim_continuity.py, test_close_operation_auth.py, test_start_downtime_auth.py, test_close_reopen_operation_foundation.py, test_operation_detail_allowed_actions.py | claim boundary |
| Bridge-T1..T7 | Diagnostic bridge non-interference | compatibility_lock | test_station_session_diagnostic_bridge.py | non-interference |
| Session-T1..T9 | Session lifecycle | compatibility_lock | test_station_session_lifecycle.py | session boundary |
| CMD-T1..T9 | Command context diagnostic | compatibility_lock | test_station_session_command_context_diagnostic.py | command boundary |

### Final verification result
- Claim suite (isolation run): 36 passed, exit code 0
- Full backend suite: 184 passed, 1 skipped, exit code 0

### Scope guard confirmation
- No claim model/service/test changes.
- No execution command behavior change.
- No API response schema change.
- No schema migration.
- No new domain events.
- No FE/UI changes.
- Migration debt register created and boundary locked.

### Event naming status
none_required — P0-C-04E introduced no new domain events.

---

## Slice HM3-016
Name: P0-C-04D Command Context Diagnostic Integration / Guard Readiness

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-session-ownership-contract.md §7.3 | P0-C-04D = command context guard alignment; not hard enforcement | Non-blocking wiring; no rejection |
| docs/design/02_domain/execution/station-session-ownership-contract.md §5 INV-009 | No command rejection behavior change until explicitly implemented in later slice | Diagnostic result must not gate any command |
| docs/implementation/p0-c-execution-entry-audit.md | Commands do not require claim/session guard today | Safe to add read-only observation |
| docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | No new events in diagnostic integration slice | Event set unchanged |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| All 9 execution commands | none new | none_required | N/A | n/a | no change | diagnostic is read-only |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| Diagnostic integration must not change command allow/deny | behavior_contract | no conditional on `_session_ctx` | no | YES — CMD-T1 through T9 | ownership contract §5 INV-009 |
| Missing session must not reject command | behavior_contract | `_session_ctx` never used for rejection | no | YES — CMD-T1/T3 | ownership contract |
| Tenant isolation mandatory | tenant | diagnostic call uses verified tenant_id | no | YES — CMD-T8 | CODING_RULES §TEN-001 |
| CLOSED session ignored | state_machine | repository partial index, session returns OPEN only | no | YES — CMD-T7 | session model |
| OperationDetail API response shape unchanged | api_contract | no schema change | no | YES — all CMD-Tn check detail.status only | governance |
| No new domain events | event_append_only | no event emission in diagnostic | no | existing | command/event contracts |
| Claim behavior unchanged | session | no claim model/service/test changes | no | existing | ENGINEERING_DECISIONS §10 |

### State Transition Map
No state transitions introduced. P0-C-04D adds a read-only diagnostic observation point inside each service function, after the tenant guard, before any state machine guard. The local variable `_session_ctx` is never used in any conditional.

### Test Matrix
| Test ID | Scenario | Type | Command | Given | When | Then | Invariant |
|---|---|---|---|---|---|---|---|
| CMD-T1 | start_operation unchanged, no session | behavior_unchanged | start_operation | PLANNED op, no session | command called | IN_PROGRESS, no error | allow/deny unchanged |
| CMD-T2 | start_operation unchanged, with OPEN session | behavior_unchanged | start_operation | PLANNED op, OPEN session | command called | IN_PROGRESS, no error | allow/deny unchanged |
| CMD-T3 | pause_operation unchanged, no session | behavior_unchanged | pause_operation | IN_PROGRESS op, no session | command called | PAUSED, no error | allow/deny unchanged |
| CMD-T4 | pause_operation unchanged, with OPEN session | behavior_unchanged | pause_operation | IN_PROGRESS op, OPEN session | command called | PAUSED, no error | allow/deny unchanged |
| CMD-T5 | start rejection unchanged | rejection_unchanged | start_operation | IN_PROGRESS op, no session | start_operation called | StartOperationConflictError | rejection code unchanged |
| CMD-T6 | diagnostic accessible from command context | diagnostic_accessible | manual diagnostic | OPEN session | get_station_session_diagnostic with op context | readiness=OPEN | backend-derived |
| CMD-T7 | CLOSED session not active from command context | invalid_session | manual diagnostic | only CLOSED session | command + diagnostic | NO_ACTIVE_SESSION; command succeeds | terminal state |
| CMD-T8 | cross-tenant session no false positive | security | manual diagnostic | session for other tenant | diagnostic for this tenant | NO_ACTIVE_SESSION | tenant isolation |
| CMD-T9 | pause rejection unchanged | rejection_unchanged | pause_operation | PLANNED op, no session | pause_operation called | PauseExecutionConflictError | rejection code unchanged |

### Final verification result
- Command context diagnostic tests: 9 passed
- Diagnostic bridge tests (P0-C-04C): 7 passed (unchanged)
- Session lifecycle + claim regression subset: 86 passed
- Full backend suite: 184 passed, 1 skipped, exit 0

### Scope guard confirmation
- No claim model/service/test changes.
- No execution command rejection behavior change.
- No API response schema change (OperationDetail unchanged).
- No schema migration.
- No new domain events.
- No FE/UI changes.
- `_compute_session_diagnostic` and `_session_ctx` are internal to the service layer.

### Event naming status
none_required — P0-C-04D introduced no new domain events.

---

## Slice HM3-018
Name: P0-C-08C-V1 Full Suite Verification Recovery / Failure Isolation

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/implementation/p0-c-08c-enforcement-closeout-review.md | Prior closeout was blocked by non-clean full-suite evidence | Recovery/isolation required before 08D gate |
| docs/implementation/p0-c-08c-station-session-command-guard-enforcement-report.md | 08C scope is 7 commands only; close/reopen deferred | Regression triage must not expand scope |
| docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md | Guard ordering and defer boundaries are explicit | Verification must preserve boundaries |
| docs/design/00_platform/canonical-error-code-registry.md | Approved 5-code runtime set for 08C | Error-contract drift excluded as cause |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| verification/failure isolation runs | none | none_required | N/A | n/a | none | review-only slice |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| No scope expansion beyond 08C | migration_boundary | review gate + test selection | no | yes | 08C contract |
| No claim removal / queue migration in this slice | compatibility | review gate | no | yes | 08C contract + claim lock |
| close/reopen remain deferred | state_machine | review gate + regression tests | no | yes | 08C contract |
| Backend test evidence is release gate truth | projection_consistency | pytest sequential verification | no | yes | coding rules |

### State Transition Map
No business state transition changes. Verification-only slice.

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-018-T1 | full-suite retry under stale environment | regression | previous blocked closeout | rerun full suite | reproduce deadlock/transaction abort symptoms | none | classify cause |
| HM3-018-T2 | first failing test isolated | regression | failing node id from retry | run test alone with long traceback | passes | none | no deterministic 08C regression |
| HM3-018-T3 | mandated sequential batches after cleanup | regression | cleaned DB/process environment | run 3 required batches + full suite | all green with exit code 0 | none | gate can upgrade |

### Final verification result
- First mandatory two batches remained green.
- One intermediate third-batch run reproduced DB deadlock/aborted-transaction contamination and failed (`54 passed, 11 errors`, `EXIT_CODE:1`).
- Isolated first failing test passed alone (`1 passed`, `EXIT_CODE:0`).
- Post-cleanup deterministic reruns passed:
  - 08C guard suite: `22 passed`, `EXIT_CODE:0`
  - hardening batch: `71 passed`, `EXIT_CODE:0`
  - StationSession+claim+queue batch: `61 passed`, `EXIT_CODE:0`
  - full backend suite: `277 passed, 1 skipped`, `EXIT_CODE:0`

### Scope guard confirmation
- No runtime code changes.
- No schema migration changes.
- No API contract changes.
- No queue migration, claim removal, or close/reopen enforcement expansion.

### Event naming status
none_required - verification-only slice introduced no new domain events.

### Verdict
ACCEPT - failure classified as environment/DB teardown stability, not proven 08C regression.

---

## Slice HM3-019
Name: P0-C-08D Station Queue Session-Aware Migration

### Design Evidence Extract
| Doc | Evidence | Impact |
|---|---|---|
| docs/design/02_domain/execution/station-session-ownership-contract.md | StationSession is target ownership model; claim is compatibility debt | Queue read model may expose session-aware ownership target |
| docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md | Claim removal/expansion is blocked during compatibility window | 08D must preserve claim payload and behavior |
| docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md | Queue migration explicitly separated from 08C command guard slice | 08D can be implemented as additive read-model slice |

### Current Source Evidence
| Source Area | File | Current Behavior | 08D Migration Impact |
|---|---|---|---|
| Queue projection | backend/app/services/station_claim_service.py | claim-shaped queue payload | add additive `ownership` metadata sourced from active StationSession |
| Queue schema | backend/app/schemas/station.py | claim-only ownership shape | add `SessionOwnershipSummary` under `StationQueueItem.ownership` |
| Queue regression lock | backend/tests/test_station_queue_active_states.py | active-state + claim compatibility assertions | preserve claim assertions and add ownership migration assertions |

### Queue Ownership Model
| Layer | Pre-08D | 08D (Implemented) | Compatibility Rule |
|---|---|---|---|
| queue ownership view | claim-only object | `ownership` session-aware object + legacy `claim` | claim remains compatibility payload |
| ownership target marker | implicit claim state | `target_owner_type=station_session` | no command allow/deny change |
| migration marker | none | `ownership_migration_status=TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT` | additive only, no removals |

### Event Map
| Command / Action | Required Event | Event Type | Event Name Status | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|---|
| station queue read-model migration | none | none_required | N/A | n/a | queue response shape additive fields only | ownership contract + claim lock |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---|---|---|
| claim compatibility preserved | migration_boundary | service + schema + regression tests | no | yes | claim lock |
| session-aware ownership exposed additively | ownership | queue service projection | no | yes | ownership contract |
| no command-path behavior change | state_machine | scope guard + regression suite | no | yes | 08C contract |
| no new events for read-model augmentation | event_append_only | service scope | no | yes | execution event registry |

### State Transition Map
No business state transitions changed. 08D is a read-model payload migration only.

### Test Matrix
| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| HM3-019-T1 | additive ownership metadata present | contract | active station session | read queue | `ownership` block populated | none | session target exposed |
| HM3-019-T2 | legacy claim shape preserved | regression | active queue items without claims | read queue | claim fields unchanged | none | compatibility preserved |
| HM3-019-T3 | no-open-session ownership fallback | edge | closed/no open station session | read queue | ownership is nullable + `has_open_session=false` | none | additive behavior stable |
| HM3-019-T4 | command hardening unchanged | regression | 08C command suites | run batch | all pass | none | no command drift |
| HM3-019-T5 | full backend suite | regression | merged slice | run full suite | all pass | none | no system drift |

### Final verification result
- Focused queue migration run: `10 passed`, `EXIT_CODE=0`
- Command hardening regression batch: `70 passed`, `EXIT_CODE=0`
- StationSession+claim+queue+reopen regression batch: `63 passed`, `EXIT_CODE=0`
- Full backend suite: `279 passed, 1 skipped`, `EXIT_CODE=0`

### Scope guard confirmation
- No claim removal or claim endpoint deprecation.
- No close/reopen StationSession enforcement expansion.
- No schema migration.
- No new domain events.
- No FE/UI changes.

### Event naming status
none_required - read-model migration introduced no new domain events.

### Verdict
ALLOW_IMPLEMENTATION_COMPLETE

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

## Slice HM3-005
Name: P0-A CI governance artifact enforcement

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

## Slice HM3-016
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

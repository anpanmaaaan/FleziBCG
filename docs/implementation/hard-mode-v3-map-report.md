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
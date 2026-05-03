# P0-A-11A Report

## Summary

P0-A-11A adds a dedicated approval current-behavior regression suite without changing approval runtime behavior.

The new tests lock the current approval contract identified in P0-A-11:

- exact six-value `VALID_ACTION_TYPES` set;
- invalid action rejection;
- `PENDING -> APPROVED` and `PENDING -> REJECTED` behavior;
- requester-versus-decider SoD enforcement;
- terminal-state rejection on double decision;
- tenant-aware rule selection and wildcard fallback;
- wrong-role rejection;
- approval-local audit row creation;
- impersonation-context persistence with SoD still enforced on the real user identity;
- `CANCELLED` remaining schema-only debt.

No approval service, model, repository, API, route guard, RBAC registry, seed logic, migration, frontend file, or MMD file was modified.

## Routing

- Selected brain: MOM Brain
- Selected mode: QA + Strict
- Hard Mode MOM: v3
- Reason: This slice hardens approval-governance behavior with regression tests around SoD, tenant-aware rule selection, action-code semantics, terminal-state behavior, and approval-local audit expectations without changing runtime behavior.

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| Current approval behavior contract | `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md` | Approval is narrow, tenant-aware, SoD-aware, and not generic |
| Canonical SoD rule | `docs/design/01_foundation/approval-and-separation-of-duties-model.md` | Requester must never equal decider, including under impersonation |
| Approval action codes | `docs/design/02_registry/action-code-registry.md`, `backend/app/security/rbac.py` | `approval.create` and `approval.decide` are the only approval action codes |
| Current supported runtime actions | `backend/app/services/approval_service.py` | `VALID_ACTION_TYPES` hardcodes six supported action types |
| Current approval state machine | `backend/app/services/approval_service.py`, `backend/app/schemas/approval.py` | Runtime supports `PENDING`, `APPROVED`, `REJECTED`; `CANCELLED` is schema-only |
| Tenant and wildcard rule lookup | `backend/app/repositories/approval_repository.py` | Rule lookup uses tenant + `*`; request lookup is tenant-scoped |
| Current audit behavior | `backend/app/services/approval_service.py` | Writes `ApprovalAuditLog` rows but no `SecurityEventLog` |

### Event Map

| Approval Action | Approval-local audit? | SecurityEventLog? | Decision |
|---|---|---|---|
| create request | Yes, `REQUEST_CREATED` | No | locked by regression test |
| approve request | Yes, `DECISION_MADE` | No | locked by regression test |
| reject request | Yes, `DECISION_MADE` | No | locked by regression test |
| impersonated decision context | decision stores impersonation session id if passed | No | locked by regression test |

### Invariant Map

| Invariant | Evidence | Test |
|---|---|---|
| Only current six action types are valid. | `VALID_ACTION_TYPES` hardcoded in service | `test_valid_action_types_exactly_match_current_supported_actions`, `test_invalid_action_type_is_rejected` |
| Requester cannot decide own approval. | SoD check in `decide_approval_request()` | `test_requester_cannot_decide_own_request` |
| Only matching approver role can decide. | allowed-role check in service | `test_wrong_approver_role_is_rejected` |
| Terminal approvals cannot be decided again. | non-pending check in service | `test_terminal_approval_cannot_be_decided_twice` |
| Tenant rule selection is enforced. | tenant-scoped repository lookup | `test_tenant_specific_rule_is_respected`, `test_wildcard_rule_fallback_works_when_no_tenant_specific_rule_exists`, `test_request_lookup_is_tenant_scoped` |
| No MMD runtime code is changed. | task scope | scope compliance only |
| Generic approval remains unimplemented. | hardcoded action set, schema-only `CANCELLED`, no scope-aware contract | `test_cancelled_remains_schema_only_debt` plus exact-set test |

### State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next State | Invalid Case Test |
|---|---|---|---:|---|---|---|
| `ApprovalRequest` | none | create | Yes | `REQUEST_CREATED` | `PENDING` | invalid action rejection |
| `ApprovalRequest` | `PENDING` | decide approved | Yes | `DECISION_MADE` | `APPROVED` | wrong-role / self-decision rejection |
| `ApprovalRequest` | `PENDING` | decide rejected | Yes | `DECISION_MADE` | `REJECTED` | wrong-role / self-decision rejection |
| `ApprovalRequest` | `APPROVED` or `REJECTED` | decide again | No | none | unchanged | terminal-state rejection |
| schema literal | `CANCELLED` | service path | No implementation | none | none | schema-only debt test |

### Test Matrix

| Test Case | Expected Result | File |
|---|---|---|
| exact current action type set | pass | `backend/tests/test_approval_service_current_behavior.py` |
| invalid action rejected | `ValueError` | same |
| supported request creation | `PENDING` request + `REQUEST_CREATED` audit row | same |
| approve path | decision row + `APPROVED` status + decision audit row | same |
| reject path | decision row + `REJECTED` status + decision audit row | same |
| self-decision rejection | `ValueError` | same |
| terminal-state rejection | `ValueError` | same |
| tenant rule selection | tenant-specific rule honored | same |
| wildcard fallback | wildcard rule honored when tenant-specific absent | same |
| wrong role rejected | `PermissionError` | same |
| impersonation context stored | `impersonation_session_id` persisted | same |
| real-user SoD under impersonation | `ValueError` when real user equals requester | same |
| `CANCELLED` schema-only | literal present, no service path | same |

### Verdict before coding

`ALLOW_P0A11A_APPROVAL_CURRENT_BEHAVIOR_REGRESSION_TESTS`

## Selected Option

Option A — Tests only.

Current approval behavior was testable directly at the service layer with isolated SQLite tables, so no production-code change was required.

## Tests Added / Updated

### Added

- `backend/tests/test_approval_service_current_behavior.py`

### Updated

- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`

## Approval Behavior Coverage Map

| Behavior | Covered? | Notes |
|---|---|---|
| exact six supported action types | Yes | exact-set assertion |
| invalid action rejection | Yes | create path |
| create supported approval request | Yes | service-level create |
| approve pending request | Yes | service-level decide |
| reject pending request | Yes | service-level decide |
| requester cannot self-approve | Yes | real-user SoD locked |
| requester cannot self-reject | Yes | same parameterized path |
| terminal decision cannot be repeated | Yes | both approved and rejected terminal states |
| tenant-specific rule respected | Yes | service-level rule fixture |
| wildcard fallback works | Yes | service-level rule fixture |
| wrong approver role rejected | Yes | `PermissionError` |
| approval-local audit rows created | Yes | request and decision audit rows asserted |
| impersonation path preserves real-user SoD | Yes | service-level `impersonation_session_id` and real-user rejection |
| `CANCELLED` schema-only debt | Yes | schema literal present, no service cancel path |

## Files Inspected

- `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md`
- `docs/audit/mmd-be-00-subdomain-evidence-contract-lock-report.md`
- `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md`
- `docs/audit/p0-a-08-role-permission-db-seeding-alignment-report.md`
- `docs/design/01_foundation/approval-and-separation-of-duties-model.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/design/01_foundation/role-model-and-scope-resolution.md`
- `docs/design/02_registry/action-code-registry.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`
- `backend/app/models/approval.py`
- `backend/app/models/impersonation.py`
- `backend/app/services/approval_service.py`
- `backend/app/repositories/approval_repository.py`
- `backend/app/api/v1/approvals.py`
- `backend/app/schemas/approval.py`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/services/security_event_service.py`
- `backend/tests/conftest.py`
- `backend/tests/test_access_service.py`
- `backend/tests/test_rbac_action_registry_alignment.py`
- `backend/tests/test_rbac_seed_alignment.py`
- `backend/tests/test_qa_foundation_authorization.py`
- `backend/tests/test_pr_gate_workflow_config.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`

## Files Changed

- `backend/tests/test_approval_service_current_behavior.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`
- `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md`

## Verification Commands Run

| Command | Result |
|---|---|
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_service_current_behavior.py` | completed |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | completed |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_qa_foundation_authorization.py tests/test_pr_gate_workflow_config.py` | completed |

## Results

| Check | Outcome |
|---|---|
| approval current-behavior test file | `17 passed, 1 warning` |
| RBAC registry + seed regressions | `40 passed, 1 warning` |
| auth + PR gate regressions | `6 passed, 1 warning` |
| warning | existing non-test-DB warning from `backend/tests/conftest.py` because `POSTGRES_DB=mes` |

## Existing Gaps / Known Debts

1. Approval remains non-generic because supported actions are hardcoded in runtime.
2. Approval still writes only approval-local audit rows, not `SecurityEventLog` rows.
3. `CANCELLED` remains schema-only debt with no service/API path.
4. Current rule lookup supports tenant-specific and wildcard rules, but this slice does not change any rule-merging semantics.
5. Approval is tenant-aware only; no sub-tenant scope-aware approval exists.

## Scope Compliance

- No MMD source, tests, docs, routes, services, models, migrations, or frontend files were touched.
- No approval runtime behavior was changed.
- No migrations were added.
- No API endpoints were added.
- No frontend/Admin UI work was added.
- No action codes, route guards, or seed logic were changed.

## Risks

1. The tests lock current behavior, including current debts, so future generic approval work will need deliberate contract updates rather than incidental behavior drift.
2. The current source comment about tenant-specific override behavior is broader than what this slice needs to lock; this slice only locks currently testable tenant-specific authorization and wildcard fallback behavior.

## Recommended Next Slice

After this test-hardening slice, the next safe step is a design-first generic approval extension contract slice that resolves governed resource identity, scope-aware approval applicability, and platform-level security-event evidence before any domain adoption.

## Stop Conditions Hit

None.
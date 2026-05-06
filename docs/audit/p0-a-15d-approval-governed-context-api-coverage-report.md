# P0-A-15D Report

## Summary

P0-A-15D adds API-layer integration coverage for approval governed context through POST /api/v1/approvals, without changing approval runtime behavior. The new suite verifies legacy payload compatibility, governed-context payload acceptance, response serialization, persistence, SecurityEventLog detail content, invalid action rejection, non-enforcement of governed action registry, subject field continuity, and absence of a cancel path/event.

All required replay suites passed. No migration, model, repository, or route behavior changes were introduced.

## Routing

- Selected brain: MOM Brain
- Selected mode: QA
- Hard Mode MOM: v3 ON
- Reason: This slice validates tenant/scope/auth-gated approval API behavior and security-event invariants at the HTTP boundary with strict non-expansion constraints.

## Hard Mode MOM v3 Gate

### Design Evidence Extract

- P0-A-15C closeout artifacts establish the service-level bridge baseline and non-change constraints.
- Approval route in backend/app/api/v1/approvals.py already uses ApprovalCreateRequest for input and ApprovalRequestResponse for output.
- Approval create schema in backend/app/schemas/approval.py already includes optional governed context fields.
- Bridge logic in backend/app/services/approval_service.py already persists governed context and enriches APPROVAL.REQUESTED detail when provided.
- Existing FastAPI test patterns (for example reason/product API tests and authorization tests) demonstrate stable dependency override patterns for auth/action dependencies and route-local DB dependencies.
- Approval SecurityEvent tests confirm approved taxonomy: APPROVAL.REQUESTED, APPROVAL.APPROVED, APPROVAL.REJECTED; APPROVAL.CANCELLED remains unimplemented.

### Event Map

- No new event type is introduced.
- APPROVAL.REQUESTED remains the create-request event.
- APPROVAL.REQUESTED includes governed context when provided through API payload.
- APPROVAL.APPROVED remains unchanged.
- APPROVAL.REJECTED remains unchanged.
- APPROVAL.CANCELLED remains unimplemented.

### Invariant Map

| Invariant | Evidence | Test |
|---|---|---|
| Legacy API payload remains valid | approval route + existing schema defaults | T-API-01 |
| Governed context API payload is optional | optional fields on create schema | T-API-02 |
| Governed context is returned in API response | route response model exposes governed fields | T-API-03 |
| Governed context is persisted | service create mapping persists fields | T-API-04 |
| SecurityEventLog includes governed context when provided | create service event detail logic | T-API-05 |
| Invalid legacy action_type is still rejected | create route catches ValueError -> 400 | T-API-06 |
| Governed action registry is not enforced yet | no registry validation in route/service | T-API-07 |
| No migration/model/repository changes | test-only slice constraints | verification |
| No MMD files changed | git status replay review | verification |

### State Transition Map

No lifecycle change:
- PENDING -> APPROVED
- PENDING -> REJECTED
- APPROVED / REJECTED terminal
- CANCELLED schema-only with no service path

### Test Matrix

| Test / Command | Expected |
|---|---|
| tests/test_approval_governed_context_api.py | T-API-01 through T-API-09 pass |
| tests/test_approval_create_governed_context_bridge.py | bridge baseline remains green |
| tests/test_approval_rule_scope_aware_matching.py | T-SA matching remains green |
| tests/test_approval_service_current_behavior.py | approval behavior baseline remains green |
| tests/test_approval_security_events.py | event baseline remains green |
| tests/test_pr_gate_workflow_config.py | gate coverage checks include P0-A-15D test |
| tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py | RBAC baseline remains green |
| tests/test_scope_rbac_foundation_alignment.py | scope foundation remains green |
| tests/test_qa_foundation_authorization.py | authorization baseline remains green |

### Verdict before coding/reporting

ALLOW_P0A15D_APPROVAL_GOVERNED_CONTEXT_API_INTEGRATION_COVERAGE

## Selected Option

Option A — API integration tests only.

No route patch was required. Existing route and service behavior already satisfied the contract; only integration coverage and gate inclusion were added.

## API Coverage Decision

Added backend/tests/test_approval_governed_context_api.py with nine API integration tests:
- T-API-01: legacy payload succeeds.
- T-API-02: governed payload with all context fields succeeds.
- T-API-03: API response includes all governed fields.
- T-API-04: persisted ApprovalRequest stores governed fields from API payload.
- T-API-05: APPROVAL.REQUESTED SecurityEventLog detail includes governed context from API payload.
- T-API-06: invalid legacy action_type is rejected.
- T-API-07: arbitrary governed_action_type is accepted as context-only.
- T-API-08: subject_type and subject_ref remain unchanged in response.
- T-API-09: no cancel endpoint/event introduced.

## Backward Compatibility Decision

Legacy API payload contract remains intact. Requests without governed fields still return successful create responses and default governed fields to null.

## SecurityEventLog API Payload Decision

Verified at API boundary: when governed context is supplied in POST /api/v1/approvals, APPROVAL.REQUESTED detail contains governed_resource_type, governed_resource_scope_ref, and governed_action_type tokens.

## Tests Added / Updated

Added:
- backend/tests/test_approval_governed_context_api.py

Updated:
- backend/tests/test_pr_gate_workflow_config.py
- .github/workflows/pr-gate.yml
- .github/workflows/backend-ci.yml

## Files Inspected

- docs/audit/p0-a-15c-01-approval-create-governed-context-bridge-closeout-report.md
- docs/audit/p0-a-15c-approval-create-governed-context-bridge-report.md
- backend/app/api/v1/approvals.py
- backend/app/schemas/approval.py
- backend/app/services/approval_service.py
- backend/app/repositories/approval_repository.py
- backend/tests/conftest.py
- backend/tests/test_qa_foundation_authorization.py
- backend/tests/test_reason_code_foundation_api.py
- backend/tests/test_product_foundation_api.py
- backend/tests/test_approval_security_events.py
- backend/tests/test_approval_create_governed_context_bridge.py
- backend/tests/test_approval_rule_scope_aware_matching.py
- backend/tests/test_pr_gate_workflow_config.py
- .github/workflows/pr-gate.yml
- .github/workflows/backend-ci.yml

## Files Changed

- backend/tests/test_approval_governed_context_api.py
- backend/tests/test_pr_gate_workflow_config.py
- .github/workflows/pr-gate.yml
- .github/workflows/backend-ci.yml
- docs/audit/p0-a-15d-approval-governed-context-api-coverage-report.md

## Verification Commands Run

- git status --short
- cd backend
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_governed_context_api.py
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_create_governed_context_bridge.py
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_rule_scope_aware_matching.py
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_service_current_behavior.py
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_security_events.py
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_pr_gate_workflow_config.py
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_scope_rbac_foundation_alignment.py
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_qa_foundation_authorization.py
- Optional: g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py

## Results

| Command | Result |
|---|---|
| git status --short | PASS |
| tests/test_approval_governed_context_api.py | PASS_WITH_WARNINGS (9 passed) |
| tests/test_approval_create_governed_context_bridge.py | PASS_WITH_WARNINGS (13 passed) |
| tests/test_approval_rule_scope_aware_matching.py | PASS_WITH_WARNINGS (12 passed) |
| tests/test_approval_service_current_behavior.py | PASS_WITH_WARNINGS (17 passed) |
| tests/test_approval_security_events.py | PASS_WITH_WARNINGS (6 passed) |
| tests/test_pr_gate_workflow_config.py | PASS_WITH_WARNINGS (9 passed) |
| tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py | PASS_WITH_WARNINGS (40 passed) |
| tests/test_scope_rbac_foundation_alignment.py | PASS_WITH_WARNINGS (10 passed) |
| tests/test_qa_foundation_authorization.py | PASS_WITH_WARNINGS (3 passed) |
| Optional alembic/migration/bootstrap suite | PASS_WITH_SKIPS (14 passed, 3 skipped) |

Aggregate required replay total: 119 passed, 0 failed.
Optional replay: +14 passed, 3 skipped.

Observed warning across suites (pre-existing): backend/tests/conftest.py warns POSTGRES_DB=mes does not look test-specific.

## Scope Compliance

- No migration added.
- No ApprovalRequest model field changed.
- No ApprovalRule schema field changed.
- No repository matching precedence changed.
- No governed action registry implementation added.
- No global governed_action_type enforcement added.
- VALID_ACTION_TYPES unchanged.
- No MASTER_DATA action type added.
- No APPROVAL.CANCELLED implementation added.
- No new endpoint added.
- No frontend/Admin UI changes.
- No MMD source/tests/docs modified.
- No route guard logic changed.
- No ACTION_CODE_REGISTRY changes.
- Auth tests were not weakened.

## Risks

Low risk. Changes are test-only plus CI/PR test list updates. The only runtime-facing verification concern remains the existing environment warning about test DB naming, which is pre-existing and unchanged.

## Recommended Next Slice

P0-A-15E: add API integration coverage for decision endpoint with governed-context-influenced rule selection (approve/reject path), while preserving SoD and impersonation invariants.

## Stop Conditions Hit

None.

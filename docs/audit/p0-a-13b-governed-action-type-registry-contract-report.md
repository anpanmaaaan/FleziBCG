# P0-A-13B Report

## Summary

P0-A-13B defines the governed action type registry contract as a design-first, docs-only slice.

Selected path is Option A: create the governed action type registry contract without runtime implementation.

Verification confirms runtime posture remains unchanged:

- approval runtime still uses six hardcoded action types,
- governed_action_type remains nullable schema foundation only,
- RBAC action registry remains unchanged,
- approval security-event emission remains unchanged,
- no migrations/API/frontend/Admin UI changes are introduced.

Required and optional verification tests are green.

## Routing

- Selected brain: MOM Brain
- Selected mode: Architecture + QA + Strict
- Hard Mode MOM: v3
- Reason: This slice defines governed approval taxonomy and RBAC boundary contract under tenant/scope/auth, security-event taxonomy, and critical authorization invariants.

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| Current approval runtime has narrow fixed action set | backend/app/services/approval_service.py | VALID_ACTION_TYPES contains only QC_HOLD, QC_RELEASE, SCRAP, REWORK, WO_SPLIT, WO_MERGE |
| governed_action_type exists in schema only | backend/app/models/approval.py, backend/app/schemas/approval.py | field exists nullable; no runtime enforcement or matching |
| governed action type and RBAC code are distinct | docs/design/01_foundation/governed-action-approval-applicability-contract.md, docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md | governed transition identity and permission identity are separate layers |
| RBAC action-code registry is canonical for API permission checks | backend/app/security/rbac.py, docs/design/02_registry/action-code-registry.md | approval.create and approval.decide remain APPROVE-family authorization gates |
| Security-event taxonomy remains stable | backend/app/services/approval_service.py, backend/tests/test_approval_security_events.py | APPROVAL.REQUESTED/APPROVED/REJECTED emitted; APPROVAL.CANCELLED remains unimplemented |
| P0-A-13A closeout already locked schema baseline | docs/audit/p0-a-13a-governed-resource-identity-schema-closeout-report.md | migration/schema/runtime compatibility validated |

### Event Map

| Approval Event | Current ApprovalAuditLog | Current SecurityEventLog | P0-A-13B Decision |
|---|---|---|---|
| request created | REQUEST_CREATED | APPROVAL.REQUESTED | unchanged |
| approved | DECISION_MADE | APPROVAL.APPROVED | unchanged |
| rejected | DECISION_MADE | APPROVAL.REJECTED | unchanged |
| cancelled | no service path | not emitted | unchanged (still unimplemented) |

### Invariant Map

| Invariant | Evidence | Contract Lock |
|---|---|---|
| Current VALID_ACTION_TYPES remains unchanged | backend/app/services/approval_service.py, tests/test_approval_service_current_behavior.py | locked |
| governed_action_type remains nullable schema-only | backend/app/models/approval.py, tests/test_approval_governed_resource_identity_schema.py | locked |
| Governed action type is not RBAC action code | governed-action-approval-applicability-contract.md, backend/app/security/rbac.py | locked |
| Approval remains additional governance gate after RBAC | docs/design/00_platform/authorization-model-overview.md, backend/app/api/v1/approvals.py | locked |
| No runtime registry is implemented | source inspection + slice scope | locked |
| No MMD files are changed | git status + no MMD edits | locked |
| No migration/API/frontend changes are made | slice scope + changed file set | locked |

### State Transition Map

Current runtime lifecycle remains unchanged:

- PENDING -> APPROVED
- PENDING -> REJECTED
- APPROVED / REJECTED are terminal
- CANCELLED remains schema-only with no service path

No lifecycle behavior change occurs in this slice.

### Test Matrix

| Test or Command | Expected | Result |
|---|---|---|
| git status --short | scope check only | PASS (unrelated changes only) |
| pytest tests/test_approval_governed_resource_identity_schema.py | pass | PASS (10) |
| pytest tests/test_approval_service_current_behavior.py | pass | PASS (17) |
| pytest tests/test_approval_security_events.py | pass | PASS (6) |
| pytest tests/test_pr_gate_workflow_config.py | pass | PASS (5) |
| pytest tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py | pass | PASS (40) |
| pytest tests/test_qa_foundation_authorization.py | pass | PASS (3) |
| optional pytest tests/test_scope_rbac_foundation_alignment.py | pass | PASS (10) |
| optional pytest tests/test_security_event_service.py | pass | PASS (2) |

Verdict before writing/reporting:

ALLOW_P0A13B_GOVERNED_ACTION_TYPE_REGISTRY_CONTRACT

## Selected Option

Option A — Create governed action type registry contract.

Why:

- P0-A-11C and P0-A-13 provide sufficient design/runtime evidence,
- relationship to RBAC can be defined safely at contract level,
- no runtime implementation is required for this decision slice.

## Governed Action Type Decision

Created new contract:

- docs/design/01_foundation/governed-action-type-registry-contract.md

Decision summary:

1. Governed action type is governed transition intent identity.
2. It is distinct from RBAC action code identity.
3. It follows naming convention: <domain>.<resource>.<transition>.
4. Current runtime stays unchanged until future implementation slice.
5. Future registry shape and adoption rules are defined contractually only.

## RBAC Relationship Decision

Locked relationship:

- RBAC action code answers permission to invoke/decide operation class.
- Governed action type answers transition intent under approval governance.
- Approval remains additional gate after RBAC; it does not replace RBAC.
- Future governed action types must map explicitly to required RBAC action codes.

No RBAC runtime code was changed.

## Runtime Posture Decision

Current runtime remains unchanged and explicitly locked:

1. VALID_ACTION_TYPES remains six fixed values.
2. governed_action_type remains nullable schema-only field.
3. No runtime governed action registry is implemented.
4. No governed_action_type enforcement is implemented.
5. No scope-aware rule matching is implemented.
6. APPROVAL.CANCELLED service path remains unimplemented.

## Files Inspected

- docs/audit/p0-a-13a-governed-resource-identity-schema-closeout-report.md
- docs/audit/p0-a-13-governed-resource-identity-schema-report.md
- docs/design/01_foundation/governed-action-approval-applicability-contract.md
- docs/design/01_foundation/approval-service-generic-extension-contract.md
- docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md
- docs/audit/p0-a-11b-generic-approval-extension-contract-report.md
- docs/audit/p0-a-11d-approval-governance-contract-closeout-report.md
- backend/app/models/approval.py
- backend/app/schemas/approval.py
- backend/app/services/approval_service.py
- backend/app/repositories/approval_repository.py
- backend/app/api/v1/approvals.py
- backend/app/security/rbac.py
- docs/design/02_registry/action-code-registry.md
- backend/tests/test_approval_governed_resource_identity_schema.py
- backend/tests/test_approval_service_current_behavior.py
- backend/tests/test_approval_security_events.py
- backend/tests/test_rbac_action_registry_alignment.py
- backend/tests/test_rbac_seed_alignment.py
- backend/tests/test_qa_foundation_authorization.py
- backend/tests/test_pr_gate_workflow_config.py

## Files Changed

- docs/design/01_foundation/governed-action-type-registry-contract.md (new)
- docs/audit/p0-a-13b-governed-action-type-registry-contract-report.md (new)

## Verification Commands Run

- git status --short
- cd backend
- python -m pytest -q tests/test_approval_governed_resource_identity_schema.py
- python -m pytest -q tests/test_approval_service_current_behavior.py
- python -m pytest -q tests/test_approval_security_events.py
- python -m pytest -q tests/test_pr_gate_workflow_config.py
- python -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py
- python -m pytest -q tests/test_qa_foundation_authorization.py
- optional: python -m pytest -q tests/test_scope_rbac_foundation_alignment.py
- optional: python -m pytest -q tests/test_security_event_service.py

## Results

Command outcomes:

- tests/test_approval_governed_resource_identity_schema.py: 10 passed, 1 warning
- tests/test_approval_service_current_behavior.py: 17 passed, 1 warning
- tests/test_approval_security_events.py: 6 passed, 1 warning
- tests/test_pr_gate_workflow_config.py: 5 passed, 1 warning
- tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py: 40 passed, 1 warning
- tests/test_qa_foundation_authorization.py: 3 passed, 1 warning
- optional tests/test_scope_rbac_foundation_alignment.py: 10 passed, 1 warning
- optional tests/test_security_event_service.py: 2 passed, 1 warning

Aggregate:

- required tests: 81 passed
- optional tests: 12 passed
- total observed in this slice: 93 passed
- failures: 0
- skips: 0 in required set
- warnings: recurring pre-existing warning from tests/conftest.py about POSTGRES_DB naming

Classification:

- PASS_WITH_WARNINGS (warnings are pre-existing environment warning only)

## Scope Compliance

Confirmed:

- no runtime approval behavior change,
- no VALID_ACTION_TYPES change,
- no ACTION_CODE_REGISTRY change,
- no runtime governed registry implementation,
- no migration additions,
- no API/frontend/Admin UI changes,
- no MMD files touched.

Unrelated workspace changes observed and untouched:

- frontend/tsconfig.json
- CLAUDE.md
- backend/bom_baseline_pytest_output.txt
- backend/bom_foundation_api_output_utf8.txt

## Risks

1. Contract exists but runtime registry does not yet exist; runtime adoption still pending.
2. governed_action_type remains nullable and unenforced; adoption slices must add validation/matching carefully.
3. Mapping model from governed action type to required_rbac_action_code is design-defined but not yet runtime-enforced.
4. Scope-aware applicability remains future work and can introduce policy complexity if not test-first.

## Recommended Next Slice

P0-A-14 — Scope-aware approval applicability and rule matching contract-to-runtime bridge.

Minimum target:

1. define runtime-safe mapping from governed_action_type to rule applicability dimensions,
2. keep backward compatibility with existing six action types,
3. add deterministic precedence tests for tenant/scope/resource/action matching,
4. preserve SoD and SecurityEventLog invariants.

## Stop Conditions Hit

None.

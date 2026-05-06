# P0-A-15C-01 Report

## Summary

P0-A-15C closeout replay is complete. The governed-context create-request bridge remains intact and verified: the create schema still exposes the 6 optional governed fields, the service still persists them, `APPROVAL.REQUESTED` still includes governed context when provided, and scope-aware decision-time matching still works end-to-end using the persisted request context.

All required verification suites passed. Alembic remains on a single head at `0012`. CI and PR gates both still include `tests/test_approval_create_governed_context_bridge.py`. No runtime behavior was changed in this closeout slice.

The workspace is dirty, but the observed changes are outside this closeout action and were not modified or staged here. No MMD files appeared in the replay status output.

## Routing

- Selected brain: MOM Brain
- Selected mode: QA
- Hard Mode MOM: v3 ON
- Reason: Verification replay for approval governance, tenant/scope/auth, audit/security events, scope-aware matching, and critical separation-of-duties invariants. This slice is evidence/verification only and stays narrower than backend implementation mode.

## Hard Mode MOM v3 Gate

### Design Evidence Extract

- [docs/audit/p0-a-15c-approval-create-governed-context-bridge-report.md](g:/Work/FleziBCG/docs/audit/p0-a-15c-approval-create-governed-context-bridge-report.md) records the P0-A-15C implementation baseline: optional governed fields added to create schema, service persistence, additive `APPROVAL.REQUESTED` detail, bridge tests, and gate coverage.
- [backend/app/schemas/approval.py](g:/Work/FleziBCG/backend/app/schemas/approval.py) shows `ApprovalCreateRequest` includes `governed_resource_type`, `governed_resource_id`, `governed_resource_display_ref`, `governed_resource_tenant_id`, `governed_resource_scope_ref`, and `governed_action_type`, all optional.
- [backend/app/services/approval_service.py](g:/Work/FleziBCG/backend/app/services/approval_service.py) shows `create_approval_request` persists all 6 governed fields and conditionally appends governed context to `APPROVAL.REQUESTED` detail.
- [backend/tests/test_approval_security_events.py](g:/Work/FleziBCG/backend/tests/test_approval_security_events.py) confirms the create/decision event taxonomy remains `APPROVAL.REQUESTED`, `APPROVAL.APPROVED`, and `APPROVAL.REJECTED`, with `APPROVAL.CANCELLED` still unimplemented.
- [backend/tests/test_approval_create_governed_context_bridge.py](g:/Work/FleziBCG/backend/tests/test_approval_create_governed_context_bridge.py) covers T-CB-01 through T-CB-10.
- [backend/app/repositories/approval_repository.py](g:/Work/FleziBCG/backend/app/repositories/approval_repository.py) and [backend/tests/test_approval_rule_scope_aware_matching.py](g:/Work/FleziBCG/backend/tests/test_approval_rule_scope_aware_matching.py) confirm the P0-A-15B matching path still depends on persisted governed context from the request.
- [.github/workflows/backend-ci.yml](g:/Work/FleziBCG/.github/workflows/backend-ci.yml) and [.github/workflows/pr-gate.yml](g:/Work/FleziBCG/.github/workflows/pr-gate.yml) still include `tests/test_approval_create_governed_context_bridge.py`.

### Event Map

| Event | Closeout Status |
|---|---|
| `APPROVAL.REQUESTED` | Unchanged in closeout; remains the create-request event and still includes governed context when provided |
| `APPROVAL.APPROVED` | Unchanged |
| `APPROVAL.REJECTED` | Unchanged |
| `APPROVAL.CANCELLED` | Still unimplemented |
| New events | None |

### Invariant Map

| Invariant | Evidence | Closeout Status |
|---|---|---|
| Existing create request without governed context remains valid | T-CB-01 | VERIFIED |
| Existing subject_type / subject_ref remain supported | T-CB-06 | VERIFIED |
| Governed context fields are optional | `ApprovalCreateRequest` defaults | VERIFIED |
| Governed context is persisted if provided | service mapping + T-CB-02 | VERIFIED |
| Decision-time matching can use persisted governed context | T-CB-05 + P0-A-15B suite | VERIFIED |
| No governed action registry enforcement occurs yet | T-CB-07 | VERIFIED |
| `VALID_ACTION_TYPES` unchanged | approval service current behavior + T-CB-08 | VERIFIED |
| No schema/migration change in closeout | verification-only slice | VERIFIED |
| No MMD files changed | `git status --short` replay | VERIFIED |
| CI/PR gate covers bridge tests | workflow files + gate test | VERIFIED |

### State Transition Map

No lifecycle change:
- `PENDING -> APPROVED`
- `PENDING -> REJECTED`
- `APPROVED` / `REJECTED` remain terminal
- `CANCELLED` remains schema-only with no service path

### Test Matrix

| Test / Command | Expected | Replay Result |
|---|---|---|
| `git status --short` | dirty worktree documented; no MMD touch | PASS |
| `alembic heads` | `0012 (head)` | BLOCKED_ENVIRONMENT via bare shell PATH; replayed successfully with venv |
| `python -m pytest -q tests/test_approval_create_governed_context_bridge.py` | T-CB suite green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_approval_rule_scope_aware_matching.py` | T-SA suite green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_approval_rule_scope_applicability_schema.py` | P0-A-15A schema baseline green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_approval_service_current_behavior.py` | approval regression green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_approval_governed_resource_identity_schema.py` | governed identity baseline green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_approval_security_events.py` | event regression green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_pr_gate_workflow_config.py` | gate coverage green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | RBAC/seed green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_scope_rbac_foundation_alignment.py` | scope foundation green | PASS_WITH_WARNINGS |
| `python -m pytest -q tests/test_qa_foundation_authorization.py` | QA auth baseline green | PASS_WITH_WARNINGS |
| optional `python -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py` | baseline green / expected skips | PASS_WITH_SKIPS |

### Verdict before reporting

`ALLOW_P0A15C01_APPROVAL_CREATE_CONTEXT_BRIDGE_CLOSEOUT_REPLAY`

## Selected Option

Option A — Closeout report only.

All required verification commands passed, CI/PR gate coverage is present, and no runtime or gate correction was required.

## Create Request Bridge Closeout

Replay confirms the P0-A-15C bridge remains present and unchanged:
- optional governed context fields remain on `ApprovalCreateRequest`
- `create_approval_request` still persists all optional governed fields into `ApprovalRequest`
- no create-request compatibility regression was observed
- no runtime code changes were made in this closeout slice

## Backward Compatibility Replay

Replay confirms backward compatibility remains intact:
- legacy create requests without governed context still succeed
- `subject_type` and `subject_ref` remain supported and unchanged
- `VALID_ACTION_TYPES` remains authoritative for `action_type` validation
- no new registry enforcement was introduced for `governed_action_type`

## SecurityEventLog Payload Replay

Replay confirms the SecurityEventLog behavior remains stable:
- `APPROVAL.REQUESTED` is still emitted for request creation
- governed context is included when provided
- create requests without governed context do not leak governed keys into the detail string
- `APPROVAL.APPROVED` and `APPROVAL.REJECTED` remain unchanged
- `APPROVAL.CANCELLED` remains unimplemented

## End-to-End Matching Replay

Replay confirms the end-to-end path remains intact:
1. create schema accepts optional governed context
2. service persists the fields on `ApprovalRequest`
3. decision-time matching reads the persisted fields
4. scope-aware rule specificity still selects the proper approver set

P0-A-15B matching tests remained green throughout the closeout replay.

## Runtime Non-Change Verification

No runtime files were edited in this closeout slice. This replay only inspected sources, ran commands, and created this closeout report.

Observed dirty-worktree files at replay start:
- `backend/app/api/v1/products.py`
- `backend/app/services/approval_service.py`
- `backend/tests/test_approval_create_governed_context_bridge.py`
- `backend/tests/test_reason_code_allowed_actions_13b.py`
- `backend/tests/test_scope_rbac_foundation_alignment.py`
- `frontend/tsconfig.json`
- `CLAUDE.md`

These changes were not touched or staged by this closeout task. No MMD files appeared in the status output.

## CI / PR Gate Coverage

Replay confirms both gates still cover the bridge suite:
- `.github/workflows/backend-ci.yml` has a dedicated `P0-A-15C tests — approval create governed context bridge` step
- `.github/workflows/pr-gate.yml` includes `tests/test_approval_create_governed_context_bridge.py`
- `backend/tests/test_pr_gate_workflow_config.py` includes a guard asserting the bridge suite remains in PR gate

## Remaining Approval Debts

- `APPROVAL.CANCELLED` is still schema-only debt with no service path
- HTTP/API-layer integration coverage for the new optional governed fields is not yet frozen in this closeout slice
- no domain-specific approval callers are yet verified here to populate governed context automatically

## Files Inspected

- `./.github/copilot-instructions.md`
- `./.github/agent/AGENT.md`
- `./docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `./docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `./.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `./docs/design/INDEX.md`
- `./docs/design/AUTHORITATIVE_FILE_MAP.md`
- `./docs/governance/CODING_RULES.md`
- `./docs/governance/ENGINEERING_DECISIONS.md`
- `./docs/governance/SOURCE_STRUCTURE.md`
- `./docs/design/00_platform/product-business-truth-overview.md`
- `./docs/audit/p0-a-15c-approval-create-governed-context-bridge-report.md`
- `./backend/app/schemas/approval.py`
- `./backend/app/services/approval_service.py`
- `./backend/app/repositories/approval_repository.py`
- `./backend/app/models/approval.py`
- `./backend/tests/test_approval_create_governed_context_bridge.py`
- `./backend/tests/test_approval_rule_scope_aware_matching.py`
- `./backend/tests/test_approval_rule_scope_applicability_schema.py`
- `./backend/tests/test_approval_service_current_behavior.py`
- `./backend/tests/test_approval_security_events.py`
- `./backend/tests/test_approval_governed_resource_identity_schema.py`
- `./backend/tests/test_pr_gate_workflow_config.py`
- `./.github/workflows/backend-ci.yml`
- `./.github/workflows/pr-gate.yml`

## Files Changed

- `docs/audit/p0-a-15c-01-approval-create-governed-context-bridge-closeout-report.md`

## Verification Commands Run

```text
git status --short
cd backend
alembic heads
g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic heads
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_create_governed_context_bridge.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_rule_scope_aware_matching.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_rule_scope_applicability_schema.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_service_current_behavior.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_governed_resource_identity_schema.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_security_events.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_pr_gate_workflow_config.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_scope_rbac_foundation_alignment.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_qa_foundation_authorization.py
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
```

## Results

| Command | Result |
|---|---|
| `git status --short` | PASS |
| `alembic heads` | BLOCKED_ENVIRONMENT (`alembic` not on PATH in shell) |
| `python -m alembic heads` via venv | PASS — `0012 (head)` |
| `test_approval_create_governed_context_bridge.py` | PASS_WITH_WARNINGS — 13 passed |
| `test_approval_rule_scope_aware_matching.py` | PASS_WITH_WARNINGS — 12 passed |
| `test_approval_rule_scope_applicability_schema.py` | PASS_WITH_WARNINGS — 12 passed |
| `test_approval_service_current_behavior.py` | PASS_WITH_WARNINGS — 17 passed |
| `test_approval_governed_resource_identity_schema.py` | PASS_WITH_WARNINGS — 10 passed |
| `test_approval_security_events.py` | PASS_WITH_WARNINGS — 6 passed |
| `test_pr_gate_workflow_config.py` | PASS_WITH_WARNINGS — 8 passed |
| `test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | PASS_WITH_WARNINGS — 40 passed |
| `test_scope_rbac_foundation_alignment.py` | PASS_WITH_WARNINGS — 10 passed |
| `test_qa_foundation_authorization.py` | PASS_WITH_WARNINGS — 3 passed |
| optional alembic/smoke suite | PASS_WITH_SKIPS — 14 passed, 3 skipped |

Aggregate replay total: 145 passed, 3 skipped, 0 failed.

Warnings were consistent across suites:
- `backend/tests/conftest.py:234` warns that `POSTGRES_DB=mes` does not look test-specific.
- This is a pre-existing environment warning and did not block any replay suite.

## Scope Compliance

- No approval runtime code was changed
- No migrations were added
- No `ApprovalRequest` model fields were modified
- No `ApprovalRule` schema fields were modified
- Repository matching precedence was not changed
- No governed action registry was implemented
- `governed_action_type` was not globally enforced
- `VALID_ACTION_TYPES` was not modified
- `APPROVAL.CANCELLED` was not implemented
- No new approval endpoints were added
- No frontend/Admin UI was added
- No MMD source, tests, or docs were modified
- No route guards were changed
- No `ACTION_CODE_REGISTRY` changes were made
- No tests were weakened

## Risks

Low. The only replay anomaly was a shell-path issue for the bare `alembic` command, which was resolved by running the same check through the configured virtualenv interpreter. Product behavior and test outcomes remained stable.

## Recommended Next Slice

P0-A-15D should freeze the HTTP/API layer with FastAPI integration coverage for `POST /approvals` using the new optional governed context fields. After that, the first domain-specific governed approval caller can be integrated and verified.

## Stop Conditions Hit

None.

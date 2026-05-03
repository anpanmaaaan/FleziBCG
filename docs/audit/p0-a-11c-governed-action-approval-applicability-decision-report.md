# P0-A-11C Report

## Summary

P0-A-11C completes the design-first governed action registry and approval applicability decision slice without changing runtime code.

This slice defines the source-of-truth relationship between governed approval action types and RBAC action codes, defines the future approval applicability model, and defines the expected `APPROVAL.*` security-event taxonomy for future runtime adoption.

No approval runtime files were modified. No MMD files were modified.

Validation confirmed the docs-only slice did not affect approval, scope, or auth baselines. One RBAC registry regression failed locally due to an unrelated existing drift: `admin.master_data.bom.manage` is present in `ACTION_CODE_REGISTRY` but not in the expected canonical registry test set.

## Routing

- Selected brain: MOM Brain
- Selected mode: Architecture + Strict
- Hard Mode MOM: v3
- Reason: This slice defines governance contract truth for governed action semantics, RBAC relationship, tenant/scope applicability, SoD boundary, and approval security-event taxonomy while explicitly forbidding runtime implementation.

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| P0-A-11B left governed action registry ownership and applicability shape intentionally open. | `docs/design/01_foundation/approval-service-generic-extension-contract.md` | A follow-on design decision was still required before runtime adoption. |
| Current approval runtime action identity is narrow and not generic. | `backend/app/services/approval_service.py`, `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md` | Current `action_type` is a hardcoded six-value allowlist. |
| Current approval API auth already uses separate RBAC action codes. | `backend/app/api/v1/approvals.py`, `backend/app/security/rbac.py` | `approval.create` and `approval.decide` guard API operations, not governed transition meaning. |
| Canonical authorization model separates action auth from approval/policy and SoD. | `docs/design/00_platform/authorization-model-overview.md` | Approval is an additional governance layer, not RBAC replacement. |
| Canonical scope hierarchy already exists beyond tenant. | `backend/app/models/rbac.py`, `docs/design/01_foundation/role-model-and-scope-resolution.md` | tenant, plant, area, line, station, equipment are canonical. |
| Current approval rule matching is tenant + action only. | `backend/app/models/approval.py`, `backend/app/repositories/approval_repository.py` | No governed resource or scope-aware rule matching exists yet. |
| Platform security-event mechanism exists but approval lacks canonical taxonomy. | `backend/app/services/security_event_service.py`, `backend/app/models/security_event.py` | A taxonomy decision can be made now without runtime change. |

### Event Map

| Approval Event | Current Support | Future Contract | Decision |
|---|---|---|---|
| approval request created | `REQUEST_CREATED` approval-local audit only | `APPROVAL.REQUESTED` | define taxonomy now |
| approval approved | `DECISION_MADE` approval-local audit only | `APPROVAL.APPROVED` | define taxonomy now |
| approval rejected | `DECISION_MADE` approval-local audit only | `APPROVAL.REJECTED` | define taxonomy now |
| approval cancelled | schema-only debt, no runtime path | `APPROVAL.CANCELLED` only if later implemented | keep conditional |

### Invariant Map

| Invariant | Evidence | Contract Lock |
|---|---|---|
| Governed action types must be registry-controlled. | Current runtime hardcodes action types; RBAC action codes are registry-controlled. | Future governed action types are dedicated registry-controlled contract values. |
| Approval does not replace RBAC. | Authorization model explicitly layers policy/approval after action auth. | Governed action types and RBAC action codes remain distinct. |
| Governed resource identity must be explicit. | Current source only has `subject_type` and `subject_ref`. | Future approval identity must be explicit and backend-owned. |
| Scope applicability must be backend-resolved. | Scope model and auth model are backend-owned. | No frontend-derived applicability. |
| Approval rule matching must include tenant and scope. | Current tenant-only rule matching is insufficient for generic adoption. | Future matching must be tenant and canonical-scope aware. |
| Platform security-event taxonomy must be defined before runtime adoption. | SecurityEventLog exists; approval taxonomy does not yet. | Future `APPROVAL.*` taxonomy is now defined at contract level. |
| No runtime code is changed in this slice. | Task scope and actual diff. | docs-only slice. |
| No MMD files are changed in this slice. | Task scope and actual diff. | MMD remained read-only context. |

### State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next State | Invalid Case Test |
|---|---|---|---:|---|---|---|
| `ApprovalRequest` | none | create | Yes | `REQUEST_CREATED` | `PENDING` | invalid action rejection |
| `ApprovalRequest` | `PENDING` | decide approved | Yes | `DECISION_MADE` | `APPROVED` | wrong-role / self-decision rejection |
| `ApprovalRequest` | `PENDING` | decide rejected | Yes | `DECISION_MADE` | `REJECTED` | wrong-role / self-decision rejection |
| `ApprovalRequest` | `APPROVED` or `REJECTED` | decide again | No | none | unchanged | terminal-state rejection |
| schema literal | `CANCELLED` | service path | No implementation | none | none | schema-only debt test |

Future event taxonomy target:

- `APPROVAL.REQUESTED`
- `APPROVAL.APPROVED`
- `APPROVAL.REJECTED`
- `APPROVAL.CANCELLED` only if intentionally implemented later

### Test Matrix

| Future Test Area | Required Test |
|---|---|
| governed action registry tests | governed action types are registry-controlled and exact |
| RBAC/governed-action mapping tests | governed action types map explicitly to RBAC action codes or command intents |
| governed resource identity tests | explicit governed resource identity contract is enforced |
| tenant/scope applicability tests | backend resolves tenant plus canonical scope applicability |
| approval rule matching tests | matching includes tenant, scope, resource type, governed action type, requester role, acting role |
| SoD negative tests | requester cannot decide own request |
| security event taxonomy tests | future approval events use canonical `APPROVAL.*` names |
| backward compatibility tests for current six action types | current narrow approval behavior remains stable until migration |

### Verdict before writing

`ALLOW_P0A11C_GOVERNED_ACTION_APPROVAL_APPLICABILITY_DECISION`

## Selected Option

Option A — Create governed action/applicability decision contract.

P0-A-11B provided enough baseline to define the remaining contract decisions safely without runtime or MMD changes.

## Governed Action Decision

Created:

- `docs/design/01_foundation/governed-action-approval-applicability-contract.md`

Decision summary:

1. future governed approval action types are separate from RBAC action codes,
2. future governed approval action types must be registry-controlled,
3. future governed approval action types must be explicitly mapped to RBAC action codes or command intents,
4. approval remains a governance layer, not the source of permission truth.

## RBAC Relationship Decision

The contract defines a strict separation:

- RBAC action code answers whether the actor may invoke or decide a protected operation class.
- Governed approval action type answers which governed transition is being requested for a governed resource.

Approval is therefore additive to RBAC, not a replacement for it.

## Governed Resource Identity Decision

The contract reaffirms the future explicit governed resource identity candidates:

- `governed_resource_type`
- `governed_resource_id`
- `governed_resource_display_ref`
- `governed_resource_tenant_id`
- `governed_resource_scope_ref`
- `governed_action_type`

It also defines the relationship to current `subject_type` and `subject_ref`: they may remain compatibility/display fields, but they are not sufficient long-term governed identity.

## Scope Applicability Decision

The contract defines future approval applicability as backend-resolved and tenant plus canonical-scope aware.

At minimum, future applicability must evaluate:

- tenant
- scope reference
- governed resource type
- governed action type
- requester role
- acting role

## Security Event Taxonomy Decision

The contract defines the future canonical approval security-event taxonomy:

- `APPROVAL.REQUESTED`
- `APPROVAL.APPROVED`
- `APPROVAL.REJECTED`
- `APPROVAL.CANCELLED` only if later implemented intentionally

This slice defines taxonomy expectations only and does not implement event emission.

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `docs/design/INDEX.md`
- `docs/design/AUTHORITATIVE_FILE_MAP.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`
- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/design/00_platform/product-scope-and-phase-boundary.md`
- `docs/design/00_platform/system-overview-and-target-state.md`
- `docs/design/00_platform/domain-boundary-map.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/design/00_platform/canonical-error-code-registry.md`
- `docs/design/00_platform/canonical-error-codes.md`
- `docs/design/01_foundation/approval-and-separation-of-duties-model.md`
- `docs/design/01_foundation/role-model-and-scope-resolution.md`
- `docs/design/01_foundation/approval-service-generic-extension-contract.md`
- `docs/design/02_registry/action-code-registry.md`
- `docs/design/05_application/canonical-api-contract.md`
- `docs/audit/p0-a-11b-generic-approval-extension-contract-report.md`
- `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md`
- `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md`
- `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md`
- `docs/audit/p0-a-08-role-permission-db-seeding-alignment-report.md`
- `docs/audit/p0-a-06a-02-scope-foundation-verification-replay-report.md`
- `docs/audit/p0-a-baseline-01-foundation-schema-baseline-freeze-report.md`
- `docs/audit/mmd-be-00-subdomain-evidence-contract-lock-report.md`
- `docs/audit/p0-a-10b-iep-mmd-action-boundary-decision-report.md`
- `backend/app/models/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/repositories/approval_repository.py`
- `backend/app/api/v1/approvals.py`
- `backend/app/schemas/approval.py`
- `backend/app/models/rbac.py`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/services/security_event_service.py`
- `backend/app/models/security_event.py`
- `backend/tests/test_approval_service_current_behavior.py`
- `backend/tests/test_rbac_action_registry_alignment.py`
- `backend/tests/test_rbac_seed_alignment.py`
- `backend/tests/test_scope_rbac_foundation_alignment.py`
- `backend/tests/test_qa_foundation_authorization.py`
- `backend/tests/test_pr_gate_workflow_config.py`

## Files Changed

- `docs/design/01_foundation/governed-action-approval-applicability-contract.md`
- `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md`
- `docs/design/01_foundation/approval-service-generic-extension-contract.md`

## Verification Commands Run

| Command | Result |
|---|---|
| `git status --short` | completed |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_service_current_behavior.py` | completed |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | completed |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_scope_rbac_foundation_alignment.py` | completed |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_qa_foundation_authorization.py tests/test_pr_gate_workflow_config.py` | completed |

## Results

| Check | Outcome |
|---|---|
| `git status --short` | workspace already dirty before this slice; this slice added only `docs/design/01_foundation/governed-action-approval-applicability-contract.md`, `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md`, and one-line doc cross-reference in `docs/design/01_foundation/approval-service-generic-extension-contract.md` |
| approval current-behavior regression | `17 passed, 1 warning` |
| RBAC registry + seed alignment | `1 failed, 39 passed, 1 warning` |
| scope foundation alignment | `10 passed, 1 warning` |
| auth + PR gate regressions | `6 passed, 1 warning` |
| recurring warning | existing non-test-DB warning from `backend/tests/conftest.py` because `POSTGRES_DB=mes` |

RBAC failure details:

- failing test: `tests/test_rbac_action_registry_alignment.py::test_action_code_registry_contains_exactly_canonical_set`
- observed failure: unexpected runtime code `admin.master_data.bom.manage`
- interpretation: unrelated existing registry/doc/test drift outside the scope of this docs-only slice

## Existing Gaps / Known Debts

1. Current approval runtime is still narrow and non-generic.
2. Current approval rule matching is tenant plus action only.
3. Current approval still lacks platform approval business events.
4. Physical registry, schema, and applicability storage design remain intentionally deferred.
5. Local RBAC registry alignment is currently dirty outside this slice because `admin.master_data.bom.manage` exists in runtime but is not reflected in the expected canonical set used by the failing regression.

## Scope Compliance

- No approval runtime file was changed.
- No MMD runtime, test, or doc file was changed.
- No migration was added.
- No API was added or modified.
- No frontend/Admin UI was added.
- No action code or route guard was changed.
- The failing RBAC registry regression came from unrelated existing runtime/doc drift and was not introduced by this slice.

## Risks

1. Future teams could still conflate governed action types with RBAC action codes if they skip this contract.
2. Future implementation will still require deliberate registry, schema, and event-payload design; this slice only locks the decision boundary.
3. Local full governance validation remains partially blocked until the unrelated `admin.master_data.bom.manage` registry drift is reconciled in its owning slice.

## Recommended Next Slice

The next safe slice is a design-first governed action registry shape and approval rule specificity precedence note, still without runtime implementation, so later schema/API work has a tighter migration target.

## Stop Conditions Hit

None.
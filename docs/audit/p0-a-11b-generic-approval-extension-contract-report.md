# P0-A-11B Report

## Summary

P0-A-11B completes the design-first generic approval extension contract slice without changing runtime code.

This slice defines the future governed resource boundary for approval extension and explicitly blocks runtime adoption until governed resource identity, registry-controlled governed action types, scope-aware applicability, platform security-event evidence, and domain-owned state mutation rules are in place.

No approval runtime files were modified. No MMD files were modified.

## Routing

- Selected brain: MOM Brain
- Selected mode: Architecture + Strict
- Hard Mode MOM: v3
- Reason: This slice defines a governance contract for future approval extension across authorization, SoD, scope, audit/security evidence, and future API/DB implications, while keeping runtime unchanged.

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| Current approval capability is narrow and non-generic. | `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md` | Approval is generic only at schema shape, not runtime capability. |
| Current approval behavior is now regression-locked. | `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md`, `backend/tests/test_approval_service_current_behavior.py` | Six action types, tenant-aware lookup, SoD, and audit-local behavior are locked. |
| Canonical SoD rule uses real requester versus real decider identity. | `docs/design/01_foundation/approval-and-separation-of-duties-model.md`, `backend/app/services/approval_service.py`, `backend/app/security/dependencies.py` | Impersonation must not bypass requester != decider. |
| Approval is part of backend authorization layering, not RBAC-only. | `docs/design/00_platform/authorization-model-overview.md` | Governed actions require identity + role + scope + action + approval/policy + SoD. |
| Canonical scope hierarchy is broader than tenant. | `docs/design/00_platform/product-business-truth-overview.md`, `docs/design/01_foundation/role-model-and-scope-resolution.md`, `backend/app/security/rbac.py` | tenant, plant, area, line, station, equipment are canonical. |
| Current approval data model lacks explicit governed resource identity. | `backend/app/models/approval.py`, `backend/app/schemas/approval.py` | Only `subject_type` and `subject_ref` exist today. |
| Platform security-event capability exists separately from approval-local audit. | `backend/app/services/security_event_service.py`, `backend/app/models/security_event.py` | Approval currently does not use platform security-event logging. |

### Event Map

| Approval Action | Current Approval-local Audit | Current SecurityEventLog | Future Required SecurityEventLog | Decision |
|---|---|---|---|---|
| create request | `REQUEST_CREATED` | No | Yes | future generic adoption must emit platform security evidence |
| decide approved | `DECISION_MADE` | No | Yes | future generic adoption must emit platform security evidence |
| decide rejected | `DECISION_MADE` | No | Yes | future generic adoption must emit platform security evidence |
| impersonated decision | decision stores impersonation session id; impersonation permission-use audit exists | No approval business event | Yes | future security evidence must preserve real user and impersonation context |

### Invariant Map

| Invariant | Evidence | Contract Lock |
|---|---|---|
| Generic approval must not accept arbitrary unmanaged action strings. | Current runtime hardcodes action types and approval action codes remain registry-controlled. | Future governed action type must be registry-controlled and migration-safe. |
| Governed resource identity must be explicit. | Current source only has `subject_type` and `subject_ref`. | Future contract requires explicit governed resource identity fields. |
| Requester/decider SoD must use real user identity. | Canonical SoD doc and current service behavior. | `requester_real_user_id != decider_real_user_id` remains mandatory. |
| Approval applicability must be tenant/scope-aware before domain adoption. | Canonical hierarchy already includes plant/area/line/station/equipment; current approval is tenant-only. | Domain adoption is blocked until scope-aware applicability exists. |
| Approval decision must not directly mutate domain truth. | Domain boundary and coding rules. | Approval remains a gate, not the domain state owner. |
| Domain service remains source of truth for the state transition. | Foundation owns approval; domain owns domain truth. | Future adoption must preserve domain-owned mutation. |
| Platform audit/security evidence is required for future governed approval actions. | Platform security-event mechanism exists but approval does not use it yet. | Future generic approval must emit platform security evidence. |
| No runtime code is changed in this slice. | Task scope and actual diff. | docs-only contract slice. |
| No MMD files are changed in this slice. | Task scope and actual diff. | MMD remained read-only context. |

### State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next State | Invalid Case Test |
|---|---|---|---:|---|---|---|
| `ApprovalRequest` | none | create | Yes | `REQUEST_CREATED` | `PENDING` | invalid action rejection |
| `ApprovalRequest` | `PENDING` | decide approved | Yes | `DECISION_MADE` | `APPROVED` | wrong-role / self-decision rejection |
| `ApprovalRequest` | `PENDING` | decide rejected | Yes | `DECISION_MADE` | `REJECTED` | wrong-role / self-decision rejection |
| `ApprovalRequest` | `APPROVED` or `REJECTED` | decide again | No | none | unchanged | terminal-state rejection |
| schema literal | `CANCELLED` | service path | No implementation | none | none | schema-only debt test |

Future contract lifecycle:

- `REQUESTED/PENDING -> APPROVED`
- `REQUESTED/PENDING -> REJECTED`
- optional `CANCELLED` only if intentionally implemented later

### Test Matrix

| Future Test Area | Required Test |
|---|---|
| generic action type registry tests | future governed action types must be registry-controlled and not arbitrary strings |
| governed resource identity tests | request/decision contracts must carry explicit governed resource identity |
| tenant/scope approval applicability tests | approval applicability must resolve canonical scope correctly |
| SoD negative tests | requester cannot decide own request |
| impersonation SoD tests | real user identity remains authoritative for SoD |
| security event emission tests | approval request/decision emits platform security evidence |
| domain adoption tests | approval is a gate and target domain service remains source of truth |
| terminal-state tests | terminal requests reject repeat decisions unless intentionally changed |
| backwards compatibility tests for current six action types | current fixed action set remains stable until deliberate contract change |

### Verdict before writing

`ALLOW_P0A11B_GENERIC_APPROVAL_EXTENSION_CONTRACT`

## Selected Option

Option A — Create generic approval extension contract.

P0-A-11 and P0-A-11A provide enough evidence to define the future generic boundary safely without changing runtime implementation.

## Generic Approval Contract Decision

Created:

- `docs/design/01_foundation/approval-service-generic-extension-contract.md`

Decision summary:

1. current approval remains intentionally non-generic at runtime,
2. future generic approval must use explicit governed resource identity,
3. future governed action type must be registry-controlled,
4. future applicability must be tenant and canonical-scope aware,
5. future approval/security evidence must use platform `SecurityEventLog` or equivalent,
6. future domain adoption must keep domain service as source of truth.

## Governed Resource Identity Contract

The new contract defines explicit contract-candidate fields for future generic adoption:

- `governed_resource_type`
- `governed_resource_id`
- `governed_resource_display_ref`
- `governed_resource_tenant_id`
- `governed_resource_scope_ref`
- `governed_action_type`

The contract explicitly rejects freeform `subject_type` and `subject_ref` as the only governed identity for generic adoption.

## Scope Applicability Contract

The contract requires future approval applicability to support the canonical hierarchy:

- tenant
- plant
- area
- line
- station
- equipment

Tenant-only applicability is explicitly called insufficient for future domain adoption.

## Audit / Security Event Contract

The contract requires future approval request and decision actions to emit platform security/audit evidence in addition to any approval-local audit rows retained for compatibility.

At minimum, future event evidence must preserve tenant, real actor, governed resource identity, governed action type, and outcome/decision.

## Domain Adoption Contract

The contract explicitly states that approval is a governance gate, not the domain state owner.

Any future approved transition must still be executed and validated by the target domain service, which remains the source of truth for the real state change.

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
- `docs/design/00_platform/system-overview-and-target-state.md`
- `docs/design/00_platform/domain-boundary-map.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/design/01_foundation/approval-and-separation-of-duties-model.md`
- `docs/design/01_foundation/role-model-and-scope-resolution.md`
- `docs/design/02_registry/action-code-registry.md`
- `docs/design/05_application/canonical-api-contract.md`
- `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md`
- `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md`
- `backend/app/models/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/repositories/approval_repository.py`
- `backend/app/api/v1/approvals.py`
- `backend/app/schemas/approval.py`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/services/security_event_service.py`
- `backend/app/models/security_event.py`
- `backend/tests/test_approval_service_current_behavior.py`

## Files Changed

- `docs/design/01_foundation/approval-service-generic-extension-contract.md`
- `docs/audit/p0-a-11b-generic-approval-extension-contract-report.md`

## Verification Commands Run

| Command | Result |
|---|---|
| `git status --short` | completed |
| `cd backend; python -m pytest -q tests/test_approval_service_current_behavior.py` | completed |
| `cd backend; python -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | completed |
| `cd backend; python -m pytest -q tests/test_qa_foundation_authorization.py tests/test_pr_gate_workflow_config.py` | completed |

## Results

| Check | Outcome |
|---|---|
| `git status --short` | intended new files plus unrelated pre-existing workspace changes were present; no approval runtime or MMD file was modified by this slice |
| approval current-behavior regression | `17 passed, 1 warning` |
| RBAC registry + seed alignment | `40 passed, 1 warning` |
| authorization + PR gate sanity | `6 passed, 1 warning` |
| warning | existing non-test-DB warning from `backend/tests/conftest.py` because `POSTGRES_DB=mes` |

## Existing Gaps / Known Debts

1. Current approval remains runtime-non-generic.
2. Current approval is tenant-aware only.
3. Current approval does not emit platform security-event evidence.
4. `CANCELLED` remains schema-only debt.
5. Future governed action registry ownership is still an open design question.

## Scope Compliance

- No approval runtime file was changed.
- No MMD runtime, test, or doc file was changed.
- No migration was added.
- No API was added or modified.
- No frontend/Admin UI was added.
- No action code or route guard was changed.

## Risks

1. Future teams may still try to over-read current approval schema shape as generic capability; this contract is intended to block that shortcut.
2. Future implementation work will still need deliberate API/DB design and migration handling; this slice only defines the boundary.

## Recommended Next Slice

The next safe slice is a design-first governed action registry and approval applicability model decision, still without runtime adoption, so the future implementation has a stable source of truth for governed action naming, resource identity binding, and scope-aware policy evaluation.

## Stop Conditions Hit

None.
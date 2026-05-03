# P0-A-11 Report

## Summary

P0-A-11 is completed as a report-only contract-lock slice.

Current approval capability is internally understandable and narrow enough to document safely:

- the approval service is generic only at the table/schema level, not at the capability level;
- runtime support is limited to a hardcoded six-value `action_type` allowlist in the service;
- approval decisions are tenant-scoped and enforce requester-versus-decider separation using the real user identity even under impersonation;
- audit evidence is recorded in approval-local tables and impersonation audit hooks, not in the platform security-event log;
- no domain-specific generic extension exists yet for MMD release/retire or other governed adoption.

Option A was selected. No runtime code was changed. No MMD runtime file was modified.

## Routing

- Selected brain: MOM Brain
- Selected mode: Architecture + Strict
- Hard Mode MOM: v3
- Reason: Approval capability is a foundation governance surface with SoD, role/action/scope implications, tenant boundary implications, and audit/security evidence requirements. The task is a contract-lock audit, not a runtime implementation slice.

## Hard Mode MOM v3 Gate

### Design Evidence Extract

#### Source docs read

| Doc | Why used |
|---|---|
| `.github/copilot-instructions.md` | Required repo operating rules and Hard Mode trigger confirmation |
| `.github/agent/AGENT.md` | Mandatory coding behavior baseline |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | Required routing selection |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | Required v3 gate structure |
| `docs/design/INDEX.md` | Authoritative design entry order |
| `docs/design/AUTHORITATIVE_FILE_MAP.md` | Authoritative design/governance map |
| `docs/governance/CODING_RULES.md` | Backend truth, service-layer ownership, governance-first rules |
| `docs/governance/ENGINEERING_DECISIONS.md` | Tenant/scope isolation and requester != decider invariant |
| `docs/governance/SOURCE_STRUCTURE.md` | Source ownership boundaries |
| `docs/design/00_platform/product-business-truth-overview.md` | Platform governance and approval truth baseline |
| `docs/design/00_platform/system-overview-and-target-state.md` | Foundation approval/delegation capability positioning |
| `docs/design/00_platform/domain-boundary-map.md` | Approval/SoD belongs to foundation boundary |
| `docs/design/00_platform/authorization-model-overview.md` | Identity + role + scope + action + policy/approval + SoD model |
| `docs/design/01_foundation/role-model-and-scope-resolution.md` | Role/scope model baseline |
| `docs/design/01_foundation/approval-and-separation-of-duties-model.md` | Canonical SoD rule |
| `docs/design/05_application/api-catalog-current-baseline.md` | Current approval API surface baseline |
| `docs/design/05_application/canonical-api-contract.md` | Contract rules for backend APIs |
| `docs/design/02_registry/action-code-registry.md` | Canonical approval action codes |
| `docs/audit/mmd-be-00-subdomain-evidence-contract-lock-report.md` | Confirms MMD approval/generic-extension debt and current no-workflow posture |
| `docs/audit/p0-a-10b-iep-mmd-action-boundary-decision-report.md` | Confirms MMD release/retire split is future and approval workflow is not implemented |
| `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md` | Confirms action registry alignment and approval codes |
| `docs/audit/p0-a-08-role-permission-db-seeding-alignment-report.md` | Confirms approval actions are seeded via APPROVE family |
| `docs/audit/p0-a-06a-02-scope-foundation-verification-replay-report.md` | Confirms tenant/scope/auth baseline replay |
| `docs/audit/p0-a-baseline-01-foundation-schema-baseline-freeze-report.md` | Confirms approval tables are part of foundation baseline |

#### Commands / actions found

| Command / Action | Domain | Source | Evidence |
|---|---|---|---|
| `approval.create` | Foundation approval | `backend/app/security/rbac.py` | Registered as `APPROVE` family action |
| `approval.decide` | Foundation approval | `backend/app/security/rbac.py` | Registered as `APPROVE` family action |
| `POST /approvals` | API | `backend/app/api/v1/approvals.py` | Guarded by `require_action("approval.create")` |
| `GET /approvals/pending` | API | `backend/app/api/v1/approvals.py` | Guarded by `require_permission("APPROVE")` |
| `POST /approvals/{request_id}/decide` | API | `backend/app/api/v1/approvals.py` | Guarded by `require_action("approval.decide")` |
| `create_approval_request` | Service | `backend/app/services/approval_service.py` | Creates request + approval-local audit record |
| `decide_approval_request` | Service | `backend/app/services/approval_service.py` | Enforces pending-only, requester != decider, role match to rule |
| `seed_approval_rules` | Service/bootstrap | `backend/app/services/approval_service.py` and `backend/app/db/init_db.py` | Seeds wildcard rules for fixed action types |

#### Events found

| Event | Trigger | Source | Evidence |
|---|---|---|---|
| `REQUEST_CREATED` | Approval request creation | `backend/app/services/approval_service.py` | Written to `ApprovalAuditLog` in same transaction |
| `DECISION_MADE` | Approval decision | `backend/app/services/approval_service.py` | Written to `ApprovalAuditLog` in same transaction |
| impersonation permission-use audit | Approval route invocation under impersonation | `backend/app/security/dependencies.py` | `require_action()` logs impersonation permission use |

#### States found

| State | Entity | Source | Evidence |
|---|---|---|---|
| `PENDING` | `ApprovalRequest.status` | `backend/app/services/approval_service.py` | Create path always sets `PENDING` |
| `APPROVED` | `ApprovalRequest.status` | `backend/app/services/approval_service.py` and `backend/app/schemas/approval.py` | Decision path sets request status to decision value |
| `REJECTED` | `ApprovalRequest.status` | `backend/app/services/approval_service.py` and `backend/app/schemas/approval.py` | Decision path sets request status to decision value |
| `CANCELLED` | schema literal only | `backend/app/schemas/approval.py` | Declared in type alias but no service/API path found |

#### Invariants found

| Invariant | Type | Source | Evidence |
|---|---|---|---|
| requester must never equal decider, including under impersonation | SoD | `docs/design/01_foundation/approval-and-separation-of-duties-model.md` and `backend/app/services/approval_service.py` | Service compares request `requester_id` to real `decider_user_id` |
| approval rules are tenant-aware and wildcard-overridable | tenant / policy | `backend/app/models/approval.py` and `backend/app/repositories/approval_repository.py` | Rules query matches `tenant_id` plus `*`, tenant-specific sorted before wildcard |
| approval request lookup is tenant-scoped | tenant | `backend/app/repositories/approval_repository.py` | `get_request_by_id` filters by `request_id` and `tenant_id` |
| business rules belong in service layer | layering | `docs/governance/CODING_RULES.md` and `backend/app/services/approval_service.py` | SoD and allowed-role logic lives in service, not route |
| approval routes must use registered approval codes only | authorization | `docs/design/02_registry/action-code-registry.md` and `backend/tests/test_rbac_action_registry_alignment.py` | Approval routes locked to `approval.*` codes |

#### Explicit exclusions

| Exclusion | Source | Reason |
|---|---|---|
| generic approval extension for MMD release/retire | task scope + `docs/audit/p0-a-10b-iep-mmd-action-boundary-decision-report.md` | Explicitly deferred; approval workflow not implemented for MMD adoption |
| new action codes or route guard changes | task scope | Out of scope |
| MMD runtime mutations | task scope | Another team is active on MMD |
| migrations / new API / frontend | task scope | Report-only slice |

### Event Map

| Approval Area | Emits audit/security event? | Event Type(s) | Gap |
|---|---|---|---|
| request creation | Yes, approval-local audit only | `REQUEST_CREATED` in `approval_audit_logs` | No `SecurityEventLog` entry emitted |
| decision create/approve/reject | Yes, approval-local audit only | `DECISION_MADE` in `approval_audit_logs`; `ApprovalDecision` row also created | No platform `security_event_service.record_security_event()` call |
| approval route use under impersonation | Yes, impersonation audit path | `log_impersonation_permission_use` via dependency | Audit is about impersonated permission use, not approval business event semantics |
| approval rule seed/bootstrap | No explicit audit event | none | Seeded rules are not separately security-event logged |

Current source is auditable at the approval-table level, but not yet auditable through the platform-wide security-event stream used by other governed services.

### Invariant Map

| Invariant | Evidence | Test / Contract Lock |
|---|---|---|
| Approval must preserve requester/approver separation where SoD applies. | `approval_service.decide_approval_request()` rejects `requester_id == decider_user_id`; canonical SoD doc says requester must never equal decider. | Contract lock in this report; no dedicated approval pytest currently present. |
| Approval must be tenant/scope aware before domain-wide use. | Current implementation is tenant-aware only: rules and requests filter by `tenant_id`; no plant/area/line/station/equipment scope evaluation exists. | Contract lock: future domain-wide use requires explicit scope resolution, not just tenant match. |
| Approval must emit audit/security evidence for governed actions. | Current implementation writes `ApprovalAuditLog` and impersonation audit, but does not use `SecurityEventLog`. | Contract lock: future generic adoption must add platform security-event evidence before governed domain rollout. |
| Domain release/retire adoption must not bypass RBAC/action codes. | Action registry defines only `approval.create` and `approval.decide`; MMD split is explicitly deferred pending approval workflow and role-family gate. | Locked by `test_rbac_action_registry_alignment.py` and prior audit reports. |
| No MMD runtime code is changed in this slice. | Git status showed unrelated MMD changes already present; this slice adds only a report file. | Contract lock for scope compliance. |
| No new action type is implemented in this slice. | `VALID_ACTION_TYPES` remains unchanged and no runtime file is edited. | Contract lock for scope compliance. |

### State Transition Map

| Entity | Current State | Command | Allowed? | Event | Next State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| `ApprovalRequest` | none | create request | Yes | `REQUEST_CREATED` audit row | `PENDING` | No dedicated approval test present | `backend/app/services/approval_service.py` |
| `ApprovalRequest` | `PENDING` | decide `APPROVED` | Yes if tenant matches, decider is not requester, and role is allowed | `DECISION_MADE` audit row + `ApprovalDecision` row | `APPROVED` | No dedicated approval test present | `backend/app/services/approval_service.py` |
| `ApprovalRequest` | `PENDING` | decide `REJECTED` | Yes if tenant matches, decider is not requester, and role is allowed | `DECISION_MADE` audit row + `ApprovalDecision` row | `REJECTED` | No dedicated approval test present | `backend/app/services/approval_service.py` |
| `ApprovalRequest` | `APPROVED` or `REJECTED` | decide again | No | none | unchanged | No dedicated approval test present | `backend/app/services/approval_service.py` rejects non-pending |

Actual source names are `PENDING`, `APPROVED`, and `REJECTED` in runtime behavior.
`CANCELLED` appears in schema literals only and is not implemented by service or route.

### Test Matrix

| Current / Future Test Area | Required Test |
|---|---|
| Current registry alignment | `tests/test_rbac_action_registry_alignment.py` must continue locking `approval.create` and `approval.decide` to `APPROVE`. |
| Current seed alignment | `tests/test_rbac_seed_alignment.py` must continue proving APPROVE-family action rows are seeded for QAL/PMG roles. |
| Current auth gate | `tests/test_qa_foundation_authorization.py` must continue proving route-level auth failures remain enforced. |
| Current approval service model/state | Add dedicated tests for create pending, approve, reject, double-decide rejection, and missing rule rejection before extending service generically. |
| Current SoD negative | Add dedicated tests proving requester cannot decide own request, including impersonation case. |
| Current tenant isolation | Add dedicated tests proving cross-tenant request lookup and decision remain non-leaking / rejected. |
| Future scope isolation | Add tests for plant/area/line/station/equipment scoped approval applicability before domain-wide rollout. |
| Future action-code guard | Add tests proving domain adoption still requires its domain action code plus approval policy, not approval alone. |
| Future audit event | Add tests proving approval decisions emit `SecurityEventLog` records with governed resource context. |
| Future domain adoption | Add domain-specific tests for MMD release/retire or other governed transitions only after generic extension contract is implemented. |

### Verdict before writing

`ALLOW_P0A11_APPROVAL_SERVICE_CAPABILITY_CONTRACT_LOCK`

Reason: current approval source is consistent enough to document safely, and a safe report-only boundary can be maintained without touching MMD or approval runtime code.

## Selected Option

Option A — Contract-lock current approval capability only.

Reasons:

1. Current approval source is internally understandable.
2. Generic extension is not implemented yet, but the current boundary is documentable.
3. No runtime correction was required for this slice.
4. Creating only the audit report avoids conflict with active MMD work.

## Approval Service Capability Map

| Capability Area | Current Source Truth |
|---|---|
| rule source | `ApprovalRule` table, queried by tenant-specific plus wildcard match |
| supported request actions | hardcoded six-value allowlist in `VALID_ACTION_TYPES` |
| default seeded rules | `QC_HOLD -> QAL`, `QC_RELEASE -> QAL`, `SCRAP -> QAL/PMG`, `REWORK -> QAL`, `WO_SPLIT -> PMG`, `WO_MERGE -> PMG` |
| request creation | allowed via `approval.create`; persists `ApprovalRequest` with `PENDING` status |
| decision | allowed via `approval.decide`; requires pending status, requester != decider, and effective role in current rule set |
| pending list | available to any caller with `APPROVE` family permission |
| tenant behavior | request and rule resolution are tenant-scoped; tenant-specific rules can override wildcard defaults |
| impersonation handling | effective acting role is used for approval policy check; real user id is used for requester-versus-decider SoD check; decision record stores `impersonation_session_id` |
| generic resource binding | absent; only opaque `subject_type` and `subject_ref` strings exist |
| domain side effect | absent; decision does not invoke domain services or lifecycle transitions |

## Approval Model / State Map

### Model fields

| Model | Fields / shape | Notes |
|---|---|---|
| `ApprovalRule` | `action_type`, `approver_role_code`, `tenant_id`, `is_active`, `created_at` | Unique on `(action_type, approver_role_code, tenant_id)` |
| `ApprovalRequest` | `tenant_id`, `action_type`, `requester_id`, `requester_role_code`, `subject_type`, `subject_ref`, `reason`, `status`, timestamps | `subject_type` and `subject_ref` are descriptive only; no FK/generic resource contract exists |
| `ApprovalDecision` | `request_id`, `decider_id`, `decider_role_code`, `decision`, `comment`, `impersonation_session_id`, `created_at` | Records actual human decider and impersonation session context |
| `ApprovalAuditLog` | `request_id`, `user_id`, `role_code`, `tenant_id`, `event_type`, `detail`, `created_at` | Separate approval-local audit stream |

### Current lifecycle states

```text
REQUEST CREATED -> PENDING
PENDING -> APPROVED
PENDING -> REJECTED
APPROVED / REJECTED -> terminal in current service
```

`CANCELLED` is declared in the schema type alias but not implemented by service, repository, or API.

## Current Action Type Map

| Action Type | Seeded Approver Role(s) | Current Source |
|---|---|---|
| `QC_HOLD` | `QAL` | hardcoded in `_DEFAULT_RULES`; allowed by `VALID_ACTION_TYPES` |
| `QC_RELEASE` | `QAL` | hardcoded in `_DEFAULT_RULES`; allowed by `VALID_ACTION_TYPES` |
| `SCRAP` | `QAL`, `PMG` | hardcoded in `_DEFAULT_RULES`; allowed by `VALID_ACTION_TYPES` |
| `REWORK` | `QAL` | hardcoded in `_DEFAULT_RULES`; allowed by `VALID_ACTION_TYPES` |
| `WO_SPLIT` | `PMG` | hardcoded in `_DEFAULT_RULES`; allowed by `VALID_ACTION_TYPES` |
| `WO_MERGE` | `PMG` | hardcoded in `_DEFAULT_RULES`; allowed by `VALID_ACTION_TYPES` |

Contract lock: current approval capability is not generic because any new governed action still requires runtime code changes to `VALID_ACTION_TYPES` and likely new default rules.

## Event / Audit Boundary Map

| Boundary | Current Behavior | Result |
|---|---|---|
| approval-local audit | `ApprovalAuditLog` receives `REQUEST_CREATED` and `DECISION_MADE` | present |
| decision fact storage | `ApprovalDecision` row created for each decision | present |
| impersonation audit | dependency-level impersonation permission-use logging | present |
| platform security events | `security_event_service.record_security_event()` not called anywhere in approval service or routes | absent |
| domain event emission | no domain events or callbacks | absent |

Current source is auditable enough to reconstruct approval-local behavior, but not enough to satisfy a generic governed-action extension contract that expects platform-wide security-event evidence.

## SoD / Authorization Boundary

| Boundary | Current Source Truth | Gap |
|---|---|---|
| create permission | `POST /approvals` uses `require_action("approval.create")` | none for current API surface |
| decide permission | `POST /approvals/{id}/decide` uses `require_action("approval.decide")` | none for current API surface |
| pending list permission | `GET /approvals/pending` uses `require_permission("APPROVE")` | not narrowed by action or subject scope |
| approval policy | effective role must appear in `ApprovalRule` set for `action_type` and tenant | no richer policy layer beyond tenant + acting role |
| SoD | requester cannot decide own request; check uses real user identity, not acting role | no dedicated regression test found |
| scope | no plant/area/line/station/equipment constraint in approval rule or request model | domain-wide use is not safe yet |
| authorization layering | route guard + service rule check both apply | no domain action linkage beyond approval action code |

## Generic Extension Contract

Before any domain uses approval generically for release, retire, or similar governed transitions, the following contract must exist:

1. Governed action binding must be explicit.
   Current `action_type` is an unstructured string and `subject_type` / `subject_ref` are opaque. A future generic contract needs a stable governed-resource identity and operation contract, not just descriptive strings.

2. Approval policy must be backend-derived and domain-aware.
   Tenant-level approver-role lookup is insufficient for domain-wide use. The policy must incorporate resource context, action semantics, and applicable scope.

3. Scope resolution must extend beyond tenant.
   Current approval rules do not encode plant, area, line, station, or equipment scope. Domain adoption is unsafe until scope-aware applicability is defined and tested.

4. Audit/security evidence must be promoted to platform-level governance evidence.
   Approval-local audit rows are useful but insufficient as the only governed-action evidence. Future generic decisions must emit `SecurityEventLog` records with resource context and actor context.

5. Approval must not replace domain RBAC/action codes.
   Approval must remain an additional gate. A domain action still requires its own route/service authorization and invariants.

6. State transition ownership must stay in the target domain service.
   Approval may authorize a domain transition, but it must not directly become the source of domain state truth.

7. SoD must remain bound to the real human actor, including impersonation.
   Current source does this correctly and future generic extension must preserve it.

## Domain Adoption Preconditions

| Preconditions before any domain adopts approval | Status |
|---|---|
| dedicated generic contract for governed resource identity and action semantics | NOT MET |
| explicit scope-aware approval applicability | NOT MET |
| platform `SecurityEventLog` emission for approval creation/decision | NOT MET |
| dedicated approval service tests for state, SoD, tenant isolation, impersonation, missing-rule, and role mismatch paths | NOT MET |
| clear domain-specific integration point where domain service remains source of truth | NOT MET |
| MMD release/retire split and role-family governance gate from P0-A-10B | NOT MET |
| no conflict with active MMD runtime work | MET for this report-only slice |

Implication: MMD release/retire must not adopt the current approval service yet.

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `.github/flezibcg-ai-brain-v6-auto-execution.prompt.md`
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
- `docs/design/01_foundation/role-model-and-scope-resolution.md`
- `docs/design/01_foundation/approval-and-separation-of-duties-model.md`
- `docs/design/05_application/api-catalog-current-baseline.md`
- `docs/design/05_application/canonical-api-contract.md`
- `docs/design/02_registry/action-code-registry.md`
- `docs/design/00_platform/canonical-error-code-registry.md`
- `docs/design/00_platform/canonical-error-codes.md`
- `docs/audit/mmd-be-00-subdomain-evidence-contract-lock-report.md`
- `docs/audit/p0-a-10b-iep-mmd-action-boundary-decision-report.md`
- `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md`
- `docs/audit/p0-a-08-role-permission-db-seeding-alignment-report.md`
- `docs/audit/p0-a-06a-02-scope-foundation-verification-replay-report.md`
- `docs/audit/p0-a-baseline-01-foundation-schema-baseline-freeze-report.md`
- `backend/app/models/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/repositories/approval_repository.py`
- `backend/app/api/v1/approvals.py`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/services/security_event_service.py`
- `backend/app/models/security_event.py`
- `backend/app/db/init_db.py`
- `backend/app/api/v1/router.py`
- `backend/app/schemas/approval.py`
- `backend/tests/test_rbac_action_registry_alignment.py`
- `backend/tests/test_rbac_seed_alignment.py`
- `backend/tests/test_qa_foundation_authorization.py`
- `backend/tests/test_pr_gate_workflow_config.py`

## Files Changed

- `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md`

## Verification Commands Run

| Command | Result |
|---|---|
| `git status --short` | completed |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | completed |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_qa_foundation_authorization.py tests/test_pr_gate_workflow_config.py` | completed |

Approval test glob note:

- `backend/tests/test_approval*.py` matched no files in the workspace, so no dedicated approval pytest suite could be run.

## Results

| Check | Outcome |
|---|---|
| `git status --short` | workspace already dirty with unrelated backend/frontend/MMD changes; this slice did not touch them |
| approval pytest glob | no matching files found |
| RBAC registry + seed alignment | `40 passed, 1 warning` |
| QA authorization + PR gate workflow | `6 passed, 1 warning` |
| warnings | both runs emitted the existing non-test-DB warning from `backend/tests/conftest.py` (`POSTGRES_DB=mes`) |

## Existing Gaps / Known Debts

1. `VALID_ACTION_TYPES` is hardcoded in service code, so approval is not currently extensible without a code change.
2. `ApprovalRequest.subject_type` and `subject_ref` are opaque strings, not a governed generic resource contract.
3. `ApprovalRequest.status` includes schema literal `CANCELLED`, but no runtime cancel path exists.
4. No dedicated approval pytest files are present for service/API/SoD/tenant isolation behavior.
5. Approval decisions do not emit `SecurityEventLog` entries, unlike other governed services that use `security_event_service`.
6. Current approval policy is tenant-aware only; it is not scope-aware below tenant.
7. No domain integration path exists that converts an approval decision into a governed domain transition while keeping the domain service as source of truth.

## Scope Compliance

| Rule | Status |
|---|---|
| No MMD runtime source modified | CONFIRMED |
| No approval runtime source modified | CONFIRMED |
| No new action code added | CONFIRMED |
| No route guard changed | CONFIRMED |
| No migration added | CONFIRMED |
| No frontend/Admin UI added | CONFIRMED |
| No runtime auth evaluator behavior changed | CONFIRMED |
| Only audit report added | CONFIRMED |

## Risks

1. The current approval service could be mistaken for generic capability because the tables are generic-looking; this report locks that it is not generic at runtime.
2. Future teams could adopt approval for governed lifecycle transitions without platform security-event emission unless this contract is followed.
3. Missing approval-specific automated tests increase drift risk around SoD, tenant isolation, and impersonation behavior.
4. `CANCELLED` appearing in schema but not in runtime may cause mistaken assumptions in future API consumers.

## Recommended Next Slice

P0-A-12 or equivalent foundation slice: define and test the generic approval extension contract before any domain adoption.

Minimum scope for that future slice:

- explicit governed-resource identity contract;
- scope-aware approval applicability;
- platform security-event emission for approval actions;
- approval service/API test suite for state, SoD, tenant, impersonation, and missing-rule paths;
- domain integration rules that preserve domain-service source of truth;
- no MMD rollout until the P0-A-10B action-boundary preconditions are satisfied.

## Stop Conditions Hit

None.

The source was consistent enough to document safely, and a report-only boundary was maintained.
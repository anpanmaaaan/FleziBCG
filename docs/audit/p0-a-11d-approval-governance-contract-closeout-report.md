# P0-A-11D Report

## Summary

P0-A-11D closes out the P0-A approval governance contract chain.

The chain — P0-A-11 through P0-A-11C, plus P0-A-REG-01 for registry drift — is fully verified. All required verification suites pass. No runtime behavior was changed.

**Option A** was selected. All verification commands pass. No stale approval or governance files were found requiring correction. No runtime correction is required.

**Total verified: 73 passed, 0 failed, 1 warning (pre-existing, unrelated to governance).**

The approval governance baseline is now explicitly closed with:
- current capability locked by tests (P0-A-11 + P0-A-11A);
- generic approval extension boundary defined (P0-A-11B);
- governed action type / applicability model defined (P0-A-11C);
- BOM action registry drift fully resolved (P0-A-REG-01);
- full verification replay confirmed (this slice).

---

## Routing

- Selected brain: MOM Brain
- Selected mode: QA + Strict
- Hard Mode MOM: v3
- Reason: This slice validates approval governance, separation of duties, governed action semantics, tenant/scope applicability contracts, role/action/scope assignment, audit/security event taxonomy, CI/PR gate correctness, and critical authorization invariants. Hard Mode MOM v3 is mandatory.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| P0-A-11 locked current approval capability | `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md` | Approval is narrow (6-action-type hardcoded), tenant-aware, SoD-aware, audit-local only. |
| P0-A-11A added current-behavior regression suite | `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md`, `backend/tests/test_approval_service_current_behavior.py` | 17 tests lock exact action types, SoD, terminal-state, tenant-aware lookup, audit-row creation, impersonation context. |
| P0-A-11B defined generic approval extension contract | `docs/audit/p0-a-11b-generic-approval-extension-contract-report.md`, `docs/design/01_foundation/approval-service-generic-extension-contract.md` | Future adoption blocked until governed resource identity, scope-aware applicability, and platform security-event evidence are in place. |
| P0-A-11C defined governed action / applicability contract | `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md`, `docs/design/01_foundation/governed-action-approval-applicability-contract.md` | Governed action types are separate from RBAC action codes, must be registry-controlled. APPROVAL.* security-event taxonomy defined. Generic runtime adoption blocked until prerequisites are met. |
| P0-A-REG-01 resolved BOM action registry drift | `docs/audit/p0-a-reg-01-bom-action-registry-drift-triage-report.md` | `admin.master_data.bom.manage` intentionally added by MMD-BE-09A. Test expected set and history row were the only stale artefacts; both aligned. |
| Current runtime `VALID_ACTION_TYPES` is 6 values | `backend/app/services/approval_service.py` | `QC_HOLD`, `QC_RELEASE`, `SCRAP`, `REWORK`, `WO_SPLIT`, `WO_MERGE` |
| Current approval API action codes | `backend/app/api/v1/approvals.py`, `backend/app/security/rbac.py` | `approval.create` and `approval.decide` guard API routes |
| Current approval state machine | `backend/app/services/approval_service.py`, `backend/app/models/approval.py`, `backend/app/schemas/approval.py` | `PENDING → APPROVED`, `PENDING → REJECTED` are runtime. `CANCELLED` is schema-only. |
| Approval-local audit only | `backend/app/services/approval_service.py` | Writes `ApprovalAuditLog` with `REQUEST_CREATED` and `DECISION_MADE`; no `SecurityEventLog` emission. |
| Platform security-event mechanism exists separately | `backend/app/services/security_event_service.py`, `backend/app/models/security_event.py` | Approval taxonomy `APPROVAL.*` defined as future contract in P0-A-11C; not yet emitted. |
| SoD uses real user identity including under impersonation | `backend/app/services/approval_service.py`, `backend/app/security/dependencies.py` | `requester_id != decider_id` enforced on real user IDs; impersonation does not bypass SoD. |
| RBAC action registry fully aligned | `backend/app/security/rbac.py`, `backend/tests/test_rbac_action_registry_alignment.py` | 22 codes: 9 execution + 2 approval + 3 IAM admin + 5 MMD + 1 downtime_reason + 1 security_event.read = 22. |
| Seed alignment is dynamic | `backend/tests/test_rbac_seed_alignment.py` | Counts derived from `ACTION_CODE_REGISTRY` dynamically; no hardcoded count drift possible. |
| Canonical scope hierarchy | `docs/design/01_foundation/role-model-and-scope-resolution.md`, `backend/app/models/rbac.py` | tenant, plant, area, line, station, equipment. Approval is currently tenant-only rule matching. |
| CI/PR gate includes approval and auth suites | `.github/workflows/backend-ci.yml`, `.github/workflows/pr-gate.yml` | Verified below. |

### Event Map

| Approval Event | Current Source | Current Emission | Future Contract | Closeout Decision |
|---|---|---|---|---|
| `REQUEST_CREATED` | `approval_service.create_approval_request()` | `ApprovalAuditLog` only | `APPROVAL.REQUESTED` platform `SecurityEventLog` | Contract-defined in P0-A-11C; not yet emitted; debt documented |
| `DECISION_MADE` (approved) | `approval_service.decide_approval_request()` | `ApprovalAuditLog` only | `APPROVAL.APPROVED` platform `SecurityEventLog` | Contract-defined in P0-A-11C; not yet emitted; debt documented |
| `DECISION_MADE` (rejected) | `approval_service.decide_approval_request()` | `ApprovalAuditLog` only | `APPROVAL.REJECTED` platform `SecurityEventLog` | Contract-defined in P0-A-11C; not yet emitted; debt documented |
| `CANCELLED` | Not implemented in service | None | `APPROVAL.CANCELLED` only if cancellation is implemented | Schema-only debt; no runtime path; P0-A-11A regression confirms no implementation |
| impersonation permission-use | `require_action()` in dependencies | Impersonation audit hook | Preserved in future adoption | Current behavior locked by P0-A-11A |

### Invariant Map

| Invariant | Evidence | Closeout Status |
|---|---|---|
| Current approval behavior is locked by regression tests. | `backend/tests/test_approval_service_current_behavior.py` 17 tests | ✅ LOCKED — 17 passed |
| Generic approval remains unimplemented. | P0-A-11B contract; current service has no governed resource fields. | ✅ CONFIRMED — no runtime implementation added in this chain |
| Governed approval action types remain contract-only (not runtime). | P0-A-11C contract; `VALID_ACTION_TYPES` unchanged. | ✅ CONFIRMED — no MASTER_DATA or new action type added |
| Approval does not replace RBAC. | `docs/design/00_platform/authorization-model-overview.md`; `approval.create`/`approval.decide` are separate RBAC codes. | ✅ CONFIRMED |
| SoD uses real user identity. | `approval_service.py` `decide_approval_request()` uses `requester_id != decider_id` on real IDs. | ✅ LOCKED by test `test_requester_cannot_decide_own_request` |
| Scope-aware approval applicability is future contract only. | P0-A-11B + P0-A-11C contracts; current rule lookup is tenant + action only. | ✅ CONFIRMED — no scope-aware applicability added |
| Platform `SecurityEventLog` approval emission is future contract only. | P0-A-11C defines APPROVAL.* taxonomy; current service does not emit. | ✅ CONFIRMED — P0-A-11A regression confirms no SecurityEventLog emission |
| RBAC registry/seed tests are green after BOM drift resolution. | P0-A-REG-01 + this verification replay. | ✅ 40 passed |
| No MMD files were changed in this governance chain. | git status; source inspection. | ✅ CONFIRMED — all MMD changes are from another team, untouched |
| Approval does not directly mutate domain truth. | Architecture rules; approval service does not call domain services. | ✅ CONFIRMED |

### State Transition Map

```
PENDING ──[decide: APPROVED]──► APPROVED  (terminal)
PENDING ──[decide: REJECTED]──► REJECTED  (terminal)
PENDING ──[CANCELLED]──────────► CANCELLED (schema-only; no service path exists)
APPROVED / REJECTED ──[re-decide]──► REJECTED (non-pending check raises ValueError)
```

No lifecycle change occurs in this slice. The state machine is unchanged from P0-A-11A.

### Test Matrix

| Test / Command | Expected | Result |
|---|---|---|
| `test_valid_action_types_exactly_match_current_supported_actions` | `VALID_ACTION_TYPES == {QC_HOLD, QC_RELEASE, SCRAP, REWORK, WO_SPLIT, WO_MERGE}` | PASS |
| `test_invalid_action_type_is_rejected` | ValueError on unknown action type | PASS |
| `test_approval_happy_path_approved` | PENDING → APPROVED, audit row created | PASS |
| `test_approval_happy_path_rejected` | PENDING → REJECTED, audit row created | PASS |
| `test_requester_cannot_decide_own_request` | SoD ValueError | PASS |
| `test_wrong_approver_role_is_rejected` | Role mismatch ValueError | PASS |
| `test_terminal_approval_cannot_be_decided_twice` | Non-pending ValueError | PASS |
| `test_tenant_specific_rule_is_respected` | Tenant-scoped rule chosen over wildcard | PASS |
| `test_wildcard_rule_fallback_works_when_no_tenant_specific_rule_exists` | Wildcard rule used | PASS |
| `test_request_lookup_is_tenant_scoped` | Cross-tenant request not found | PASS |
| `test_cancelled_status_is_schema_only_and_no_service_path_exists` | No service method for CANCELLED | PASS |
| `test_approval_audit_log_row_is_created_for_request` | REQUEST_CREATED audit row | PASS |
| `test_approval_audit_log_row_is_created_for_decision` | DECISION_MADE audit row | PASS |
| `test_approval_creates_no_security_event_log_entry` | No SecurityEventLog row | PASS |
| `test_impersonation_context_is_stored_with_decision` | Impersonation session ID stored | PASS |
| `test_sod_is_enforced_even_under_impersonation` | SoD still applied on real user | PASS |
| `test_no_matching_rule_raises_value_error` | No active rule → ValueError | PASS |
| `test_rbac_action_registry_alignment.py` (40 tests) | Registry + seed fully aligned | PASS |
| `test_scope_rbac_foundation_alignment.py` (10 tests) | Scope foundation aligned | PASS |
| `test_qa_foundation_authorization.py` + `test_pr_gate_workflow_config.py` (6 tests) | Auth + PR gate pass | PASS |

**Total: 73 passed, 0 failed.**

### Verdict before verification/report

`ALLOW_P0A11D_APPROVAL_GOVERNANCE_CLOSEOUT_REPLAY`

---

## Selected Option

**Option A — Closeout report only.**

All required verification commands pass. No stale approval/governance files requiring correction were found. No runtime correction is required.

---

## Approval Governance Chain Map

| Slice | Report | Contract Doc | Status |
|---|---|---|---|
| P0-A-11 | `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md` | N/A (capability lock) | ✅ Closed |
| P0-A-11A | `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md` | `backend/tests/test_approval_service_current_behavior.py` | ✅ Closed — 17 tests locked |
| P0-A-11B | `docs/audit/p0-a-11b-generic-approval-extension-contract-report.md` | `docs/design/01_foundation/approval-service-generic-extension-contract.md` | ✅ Closed — design-first contract |
| P0-A-11C | `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md` | `docs/design/01_foundation/governed-action-approval-applicability-contract.md` | ✅ Closed — design-first contract; BOM drift deferred to P0-A-REG-01 |
| P0-A-REG-01 | `docs/audit/p0-a-reg-01-bom-action-registry-drift-triage-report.md` | N/A (registry triage) | ✅ Closed — BOM drift resolved |
| **P0-A-11D** | **This report** | N/A (closeout verification) | ✅ **CLOSED** |

---

## Verification Replay Matrix

| Command | Suite | Result | Classification |
|---|---|---|---|
| `git status --short` | Workspace scope compliance | Unrelated MMD/station/frontend dirty changes only; this slice has no changed files | PASS |
| `pytest -q tests/test_approval_service_current_behavior.py` | Approval current-behavior regression | 17 passed, 1 warning | PASS_WITH_WARNINGS (warning is pre-existing) |
| `pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | RBAC registry + seed alignment | 40 passed, 1 warning | PASS_WITH_WARNINGS (warning is pre-existing) |
| `pytest -q tests/test_scope_rbac_foundation_alignment.py` | Scope foundation alignment | 10 passed, 1 warning | PASS_WITH_WARNINGS (warning is pre-existing) |
| `pytest -q tests/test_qa_foundation_authorization.py tests/test_pr_gate_workflow_config.py` | QA auth + PR gate | 6 passed, 1 warning | PASS_WITH_WARNINGS (warning is pre-existing) |

**Recurring warning**: `conftest.py:238: UserWarning: Running tests against a DB that does not look test-specific. URL: postgresql+psycopg://mes:***@localhost:5432/mes`. This is a pre-existing environment warning from `POSTGRES_DB=mes`. All approval and registry tests use in-memory SQLite or pure-Python unit tests that are unaffected by this warning. The warning predates this chain.

---

## Contract Baseline Decision

The P0-A approval governance contract chain is **CLOSED** as of 2026-05-03.

### Current baseline

| Surface | Baseline State |
|---|---|
| Approval capability | Narrow: 6 hardcoded action types (`QC_HOLD`, `QC_RELEASE`, `SCRAP`, `REWORK`, `WO_SPLIT`, `WO_MERGE`) |
| Approval state machine | `PENDING → APPROVED`, `PENDING → REJECTED` (runtime); `CANCELLED` schema-only |
| Approval SoD | `requester_id != decider_id` on real user identity; impersonation cannot bypass |
| Approval rule lookup | Tenant-scoped with wildcard fallback; action-type keyed |
| Approval audit | `ApprovalAuditLog` only (`REQUEST_CREATED`, `DECISION_MADE`) |
| Platform SecurityEventLog from approval | None — future contract only |
| Governed action type contract | Design-only (P0-A-11C); no runtime implementation |
| RBAC action codes for approval routes | `approval.create`, `approval.decide` |
| RBAC action registry | 22 codes fully aligned across runtime, governance doc, and test expected set |
| BOM action code drift | Resolved by P0-A-REG-01 |

### Contracts active as baseline

| Contract Doc | Purpose |
|---|---|
| `docs/design/01_foundation/approval-and-separation-of-duties-model.md` | Canonical SoD rule |
| `docs/design/01_foundation/approval-service-generic-extension-contract.md` | Generic approval extension boundary |
| `docs/design/01_foundation/governed-action-approval-applicability-contract.md` | Governed action type / applicability / APPROVAL.* taxonomy |
| `docs/design/02_registry/action-code-registry.md` | Canonical RBAC action code governance record |

---

## Remaining Approval Debts

| Debt | Source | Contract Reference | Required Before |
|---|---|---|---|
| `APPROVAL.REQUESTED` platform SecurityEventLog emission | P0-A-11B + P0-A-11C contracts | `governed-action-approval-applicability-contract.md` §10 | Generic runtime adoption |
| `APPROVAL.APPROVED` platform SecurityEventLog emission | P0-A-11B + P0-A-11C contracts | §10 | Generic runtime adoption |
| `APPROVAL.REJECTED` platform SecurityEventLog emission | P0-A-11B + P0-A-11C contracts | §10 | Generic runtime adoption |
| `APPROVAL.CANCELLED` platform SecurityEventLog emission | P0-A-11C contract | §10 | Only if cancellation service path is implemented |
| `CANCELLED` service path | P0-A-11A regression locks it as schema-only | §9 debt | Future explicit slice if cancellation needed |
| Governed action type registry | P0-A-11C §4 decision | `governed-action-approval-applicability-contract.md` §4 | Generic runtime adoption |
| Explicit governed resource identity fields | P0-A-11B contract; current model has only `subject_type`/`subject_ref` | §6 future contract candidate fields | Generic runtime adoption |
| Scope-aware applicability (plant/area/line/station/equipment) | P0-A-11B + P0-A-11C; current rule lookup is tenant + action only | §7 future contract | Domain adoption of generic approval |
| Rule specificity precedence (tenant-specific over wildcard, scope-level precedence) | P0-A-11C §7 | `governed-action-approval-applicability-contract.md` §7 | Generic runtime adoption |
| `requester_role` + `acting_role` in applicability evaluation | P0-A-11C §7 | §7 | Generic runtime adoption |
| MASTER_DATA approval action type | P0-A-11B + P0-A-11C; currently out of scope | §16 | MMD release/retire governed approval implementation |

All debts are documented in `docs/design/01_foundation/governed-action-approval-applicability-contract.md` §16 (Final Decision) and §9 (Open Debts).

---

## Files Inspected

### Mandatory operating files
- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`

### Approval governance chain
- `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md`
- `docs/audit/p0-a-11a-approval-service-current-behavior-regression-report.md`
- `docs/design/01_foundation/approval-service-generic-extension-contract.md`
- `docs/audit/p0-a-11b-generic-approval-extension-contract-report.md`
- `docs/design/01_foundation/governed-action-approval-applicability-contract.md`
- `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md`
- `docs/audit/p0-a-reg-01-bom-action-registry-drift-triage-report.md`

### Registry/design baseline
- `docs/design/02_registry/action-code-registry.md`
- `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md`
- `docs/audit/p0-a-08-role-permission-db-seeding-alignment-report.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/design/01_foundation/approval-and-separation-of-duties-model.md`
- `docs/design/01_foundation/role-model-and-scope-resolution.md`

### Backend source
- `backend/app/models/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/security/rbac.py`
- `backend/tests/test_approval_service_current_behavior.py`
- `backend/tests/test_rbac_action_registry_alignment.py`
- `backend/tests/test_rbac_seed_alignment.py`

---

## Files Changed

None. This is a verification-only slice.

---

## Verification Commands Run

```powershell
Set-Location "g:/Work/FleziBCG"
git status --short

Push-Location "g:/Work/FleziBCG/backend"
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q tests/test_approval_service_current_behavior.py
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q tests/test_scope_rbac_foundation_alignment.py
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q tests/test_qa_foundation_authorization.py tests/test_pr_gate_workflow_config.py
Pop-Location
```

---

## Results

| Suite | Count | Status |
|---|---|---|
| Approval current-behavior regression | 17 passed, 1 warning | PASS_WITH_WARNINGS |
| RBAC action registry alignment | 20 passed | PASS |
| RBAC seed alignment | 20 passed | PASS |
| Scope foundation alignment | 10 passed, 1 warning | PASS_WITH_WARNINGS |
| QA foundation authorization | 3 passed | PASS |
| PR gate workflow config | 3 passed, 1 warning | PASS_WITH_WARNINGS |
| **Total** | **73 passed, 0 failed** | ✅ **ALL GREEN** |

The recurring warning (`conftest.py:238: UserWarning: Running tests against a DB that does not look test-specific`) is a pre-existing environment warning from `POSTGRES_DB=mes`. It does not affect test results. All approval and registry tests use in-memory SQLite.

---

## Scope Compliance

- No approval runtime source was changed.
- No approval model, schema, repository, or API was changed.
- No RBAC action codes were added or changed.
- No `ACTION_CODE_REGISTRY` entries were added or changed.
- No `seed_rbac_core` or `seed_approval_rules` were changed.
- No migrations were added.
- No API endpoints were added.
- No frontend or Admin UI was changed.
- No MMD runtime source, MMD tests, or MMD docs were touched (all MMD dirty changes in `git status` are from another active team).
- No route guards were changed.
- No governance tests were weakened.
- This slice created only `docs/audit/p0-a-11d-approval-governance-contract-closeout-report.md`.

Unrelated dirty workspace changes (all from MMD team and station session work):

| File | Owner | Status |
|---|---|---|
| `backend/app/api/v1/products.py` | MMD team | Untouched |
| `backend/app/repositories/bom_repository.py` | MMD team | Untouched |
| `backend/app/schemas/bom.py` | MMD team | Untouched |
| `backend/app/services/bom_service.py` | MMD team | Untouched |
| `backend/tests/test_bom_foundation_api.py` | MMD team | Untouched |
| `backend/tests/test_bom_foundation_service.py` | MMD team | Untouched |
| `backend/tests/test_mmd_rbac_action_codes.py` | MMD team | Untouched |
| `backend/tests/test_station_queue_session_aware_migration.py` | Station team | Untouched |
| `backend/tests/test_station_session_command_context_diagnostic.py` | Station team | Untouched |
| `backend/tests/test_station_session_lifecycle.py` | Station team | Untouched |
| `docker/README.dev.md` | Infra | Untouched |
| `frontend/src/app/api/stationApi.ts` | Frontend/Station team | Untouched |
| `frontend/src/app/i18n/namespaces.ts` | Frontend team | Untouched |
| `frontend/tsconfig.json` | Frontend team | Untouched |
| `CLAUDE.md` (untracked) | Infra | Untouched |
| `docs/audit/tech-debt-testenv-02-backend-test-db-connectivity.md` (untracked) | Infra | Untouched |
| `frontend/scripts/govadmin-responsive-screenshots.mjs` (untracked) | Frontend team | Untouched |
| `scripts/` (untracked) | Infra | Untouched |

---

## Risks

1. **APPROVAL.* taxonomy is contract-defined but not emitted.** Any future slice that wires `SecurityEventLog` emission must implement the exact event codes defined in P0-A-11C §10. Partial or inconsistent taxonomy adoption creates audit gaps.

2. **`CANCELLED` service path does not exist.** The schema field exists but no service method creates a `CANCELLED` request. Any future cancellation implementation must be a new explicit slice with its own v3 gate.

3. **Generic approval runtime adoption is still blocked.** P0-A-11C §16 lists five hard prerequisites: governed action type registry, explicit governed resource identity, scope-aware applicability, rule-specificity precedence, and security-event taxonomy wiring. None are implemented yet. Any implementation that skips any prerequisite violates the contract.

4. **MASTER_DATA approval action type is not defined.** MMD release/retire governed approval would require this type, which requires a new slice with registry decision and approval rule seeding. This is not included in the current baseline.

5. **`admin.master_data.bom.manage` has no BOM write endpoints.** This action code is a registered prerequisite for MMD-BE-12 but has no actual write routes. Attempts to invoke it will fail authorization. MMD-BE-12 must create the routes before this code has runtime meaning.

---

## Recommended Next Slice

Choose based on product priority:

### If continuing approval domain work
- **P0-A-12** (suggested): Implement `APPROVAL.REQUESTED` / `APPROVAL.APPROVED` / `APPROVAL.REJECTED` `SecurityEventLog` emission for the current narrow approval service. This can be done without generic extension. Prerequisites from P0-A-11B still apply; the security-event taxonomy is already defined.

### If enabling MMD release/retire governed approval
- Define `MASTER_DATA` approval action type as a new registry slice.
- Define scope-aware applicability rule for MMD resource types.
- Wire `ApprovalRule` for the governed resource type + scope.

### If completing governed resource identity
- Add `governed_resource_type`, `governed_resource_id`, `governed_resource_tenant_id` fields to `ApprovalRequest` as a new migration slice.
- This is a prerequisite for generic adoption.

### If confirming full governance baseline health
- Run `test_mmd_rbac_action_codes.py` to confirm MMD-team BOM action tests also pass alongside governance tests.

---

## Stop Conditions Hit

None.

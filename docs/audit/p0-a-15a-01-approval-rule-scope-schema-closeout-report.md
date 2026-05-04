# P0-A-15A-01 Report — ApprovalRule Scope Schema Closeout / Registry Drift Resolved Replay

| Field    | Value                                                                       |
|----------|-----------------------------------------------------------------------------|
| Slice    | P0-A-15A-01                                                                 |
| Date     | 2026-05-04                                                                  |
| Author   | AI Brain (Hard Mode MOM v3)                                                 |
| Status   | CLOSED — SCHEMA FOUNDATION VERIFIED                                         |
| Depends  | P0-A-15A, P0-A-REG-02                                                       |

---

## Summary

P0-A-15A-01 is the closeout verification replay for the `ApprovalRule` scope applicability schema foundation.

P0-A-15A added migration `0012`, 7 nullable scope fields on `ApprovalRule`, 12 schema tests, and CI/PR gate coverage. P0-A-REG-02 resolved the unrelated reason-code registry drift (`admin.master_data.reason_code.manage` missing from shared test expected set).

This slice replays all required verification commands after both slices are committed. **All pass.**

| Metric | Value |
|--------|-------|
| Approval schema + regression suite | 45 passed |
| Migration + gate + RBAC + scope + auth suite | 73 passed, 3 skipped |
| Total | **118 passed, 3 skipped (live DB), 0 failed** |
| Alembic head | `0012` (single linear) |
| Runtime changes | 0 |
| MMD files changed | 0 |

---

## Routing

| Field          | Value                                                                                                                            |
|----------------|----------------------------------------------------------------------------------------------------------------------------------|
| Selected brain | MOM Brain                                                                                                                        |
| Selected mode  | QA + Strict + PR Gate Verification                                                                                               |
| Hard Mode MOM  | v3                                                                                                                               |
| Reason         | Validates approval governance schema, migration truth, RBAC registry truth after drift correction, scope/auth foundation invariants |

---

## Hard Mode MOM v3 Gate

| Gate Artifact           | Status |
|-------------------------|--------|
| Design Evidence Extract | ✅ Complete |
| Event Map               | ✅ Complete — no new events |
| Invariant Map           | ✅ Complete — 7 invariants verified |
| State Transition Map    | ✅ N/A — no state change |
| Test Matrix             | ✅ Complete — all tests PASS |
| Verdict                 | ✅ ALLOW_P0A15A01_APPROVAL_RULE_SCOPE_SCHEMA_CLOSEOUT_REPLAY |

---

## Selected Option

**Option A — Closeout report only**

All required verification commands passed. Alembic head is `0012`. RBAC registry/seed is green after REG-02. No stale CI/doc/test issue found. No corrections needed.

---

## ApprovalRule Scope Schema Closeout

### Fields Confirmed Present on `ApprovalRule` ORM Model

File: `backend/app/models/approval.py`

| Field | Type | Nullable | Comment |
|-------|------|----------|---------|
| `governed_action_type` | `String(64)` | ✅ Yes | P0-A-15A |
| `governed_resource_type` | `String(64)` | ✅ Yes | P0-A-15A |
| `scope_ref` | `String(256)` | ✅ Yes | P0-A-15A |
| `scope_type` | `String(32)` | ✅ Yes | P0-A-15A |
| `priority` | `Integer` | ✅ Yes | P0-A-15A |
| `effective_from` | `DateTime(tz=True)` | ✅ Yes | P0-A-15A |
| `effective_to` | `DateTime(tz=True)` | ✅ Yes | P0-A-15A |

### Fields Confirmed Unchanged on `ApprovalRule`

| Field | Type | Nullable | Status |
|-------|------|----------|--------|
| `action_type` | `String(64)` | No | ✅ Unchanged |
| `approver_role_code` | `String(32)` | No | ✅ Unchanged |
| `tenant_id` | `String(64)` | No (default `"*"`) | ✅ Unchanged |
| `is_active` | `Boolean` | No (default `True`) | ✅ Unchanged |
| `created_at` | `DateTime(tz=True)` | No | ✅ Unchanged |

### `ApprovalRuleResponse` Schema Confirmed

File: `backend/app/schemas/approval.py`

All 7 scope fields exposed as `str | None` / `int | None` / `datetime | None`. `from_attributes = True` — backward-safe.

### Runtime Matching Not Changed

File: `backend/app/repositories/approval_repository.py`

`get_rules_for_action` filters by `action_type + is_active + tenant_id.in_([tenant_id, "*"])` only. Confirmed by negative test `test_no_scope_aware_matching_implemented` (source inspection of `get_rules_for_action`).

---

## Registry Drift Replay

### P0-A-REG-02 Resolution

| Artifact | Before REG-02 | After REG-02 |
|----------|--------------|-------------|
| `admin.master_data.reason_code.manage` in runtime `rbac.py` | ✅ Present (MMD-BE-10A) | ✅ Present |
| `admin.master_data.reason_code.manage` in `action-code-registry.md` | ✅ Present | ✅ Present |
| `admin.master_data.reason_code.manage` in `_EXPECTED_ADMIN_MMD_CODES` | ❌ Missing | ✅ Present (added by REG-02) |
| `test_action_code_registry_contains_exactly_canonical_set` | ❌ FAILING | ✅ PASSING |

### RBAC Registry Full Result After REG-02

`test_rbac_action_registry_alignment.py` + `test_rbac_seed_alignment.py`: **40 passed, 0 failed** (included in 73-test suite above).

---

## Migration Replay Matrix

| Migration | Revision | Revises | Type | Status |
|-----------|----------|---------|------|--------|
| `0012_add_scope_applicability_to_approval_rules.py` | `0012` | `0011` | Additive nullable | ✅ Present |
| `alembic heads` output | — | — | Single head | ✅ `0012 (head)` |
| `test_alembic_baseline.py::test_alembic_head_is_baseline` | expects `"0012"` | — | — | ✅ PASS |
| Migration graph: 0001→…→0011→0012 | — | — | Linear | ✅ Verified |

---

## Runtime Non-Change Verification

| Component | File | Change Status |
|-----------|------|--------------|
| `approval_service.py` | `backend/app/services/approval_service.py` | ✅ UNCHANGED |
| `approval_repository.py` | `backend/app/repositories/approval_repository.py` | ✅ UNCHANGED |
| `approvals.py` (API) | `backend/app/api/v1/approvals.py` | ✅ UNCHANGED |
| `VALID_ACTION_TYPES` | `approval_service.py` | ✅ UNCHANGED — `{QC_HOLD, QC_RELEASE, SCRAP, REWORK, WO_SPLIT, WO_MERGE}` |
| `ACTION_CODE_REGISTRY` | `backend/app/security/rbac.py` | ✅ UNCHANGED by this session |
| `seed_rbac_core` | — | ✅ UNCHANGED |
| Approval lifecycle (PENDING→APPROVED/REJECTED) | — | ✅ UNCHANGED |
| `APPROVAL.CANCELLED` | — | ✅ Still schema-only, no service path |

---

## CI / PR Gate Coverage

### `pr-gate.yml` (verified)

| Test File | Included | Guard Test |
|-----------|---------|-----------|
| `test_approval_service_current_behavior.py` | ✅ | `test_approval_security_event_tests_are_in_pr_gate` |
| `test_approval_security_events.py` | ✅ | `test_approval_security_event_tests_are_in_pr_gate` |
| `test_approval_governed_resource_identity_schema.py` | ✅ | `test_approval_governed_resource_identity_tests_are_in_pr_gate` |
| `test_approval_rule_scope_applicability_schema.py` | ✅ | `test_approval_rule_scope_applicability_schema_tests_are_in_pr_gate` |

### `backend-ci.yml` (verified)

| Step | Test File | Status |
|------|-----------|--------|
| P0-A-11A tests | `test_approval_service_current_behavior.py` | ✅ Present |
| P0-A-12 tests | `test_approval_security_events.py` | ✅ Present |
| P0-A-13 tests | `test_approval_governed_resource_identity_schema.py` | ✅ Present |
| P0-A-15A tests | `test_approval_rule_scope_applicability_schema.py` | ✅ Present |

### `test_pr_gate_workflow_config.py` (6 tests, all PASS)

| Test | Status |
|------|--------|
| `test_backend_import_check_step_is_present` | ✅ PASS |
| `test_hard_mode_v3_skill_paths_are_current` | ✅ PASS |
| `test_hard_mode_v3_required_reports_are_checked` | ✅ PASS |
| `test_approval_security_event_tests_are_in_pr_gate` | ✅ PASS |
| `test_approval_governed_resource_identity_tests_are_in_pr_gate` | ✅ PASS |
| `test_approval_rule_scope_applicability_schema_tests_are_in_pr_gate` | ✅ PASS |

---

## Remaining Approval Debts

| Debt ID | Description | Status | Next Slice |
|---------|-------------|--------|-----------|
| D-01 | Scope-aware `get_rules_for_action` runtime matching | Deferred | P0-A-15B |
| D-02 | T-SA-01–T-SA-12 tests (P0-A-14 §14) | Not yet created | P0-A-15B prerequisite |
| D-03 | `ApprovalRule` `governed_action_type` enforcement against registry | Deferred | P0-A-15B or later |
| D-04 | `ApprovalRuleCreate` schema accepting optional scope fields | Deferred | P0-A-15B |
| D-05 | Seed data update for scope-qualified rules | Deferred | P0-A-15B |
| D-06 | `APPROVAL.CANCELLED` service path | Schema-only, deferred | TBD |

---

## Files Inspected

| File | Purpose |
|------|---------|
| `docs/audit/p0-a-15a-approval-rule-scope-applicability-schema-report.md` | P0-A-15A CLOSED report |
| `docs/audit/p0-a-reg-02-reason-code-action-registry-drift-triage-report.md` | P0-A-REG-02 CLOSED report |
| `backend/alembic/versions/0012_add_scope_applicability_to_approval_rules.py` | Migration 0012 — additive, `down_revision="0011"` |
| `backend/app/models/approval.py` | `ApprovalRule` with 7 nullable scope fields confirmed |
| `backend/app/schemas/approval.py` | `ApprovalRuleResponse` exposes all 7 fields |
| `backend/tests/test_approval_rule_scope_applicability_schema.py` | 12 schema tests |
| `backend/tests/test_alembic_baseline.py` | Head updated to `"0012"` |
| `backend/tests/test_pr_gate_workflow_config.py` | 6 tests including new P0-A-15A guard |
| `backend/tests/test_rbac_action_registry_alignment.py` | Updated with `reason_code.manage` in expected set |
| `backend/app/security/rbac.py` | `admin.master_data.reason_code.manage` confirmed at line 63 |
| `docs/design/02_registry/action-code-registry.md` | Registry doc confirmed |

---

## Files Changed

None. This is a verification/report-only slice.

| File | Change |
|------|--------|
| `docs/audit/p0-a-15a-01-approval-rule-scope-schema-closeout-report.md` | Created — this report |

---

## Verification Commands Run

| Command | Result | Classification |
|---------|--------|---------------|
| `git status --short` | `M frontend/tsconfig.json`, `?? CLAUDE.md`, `?? backend/bom_*.txt` | PASS — only pre-existing unrelated files |
| `alembic heads` | `0012 (head)` | PASS |
| `pytest test_approval_rule_scope_applicability_schema.py` | 12 passed | PASS |
| `pytest test_approval_service_current_behavior.py` | 17 passed | PASS |
| `pytest test_approval_governed_resource_identity_schema.py` | 10 passed | PASS |
| `pytest test_approval_security_events.py` | 6 passed | PASS |
| `pytest test_alembic_baseline.py test_qa_foundation_migration_smoke.py test_init_db_bootstrap_guard.py` | passed + 3 skipped | PASS_WITH_SKIPS (live DB skips — expected) |
| `pytest test_pr_gate_workflow_config.py` | 6 passed | PASS |
| `pytest test_rbac_action_registry_alignment.py test_rbac_seed_alignment.py` | 40 passed | PASS |
| `pytest test_scope_rbac_foundation_alignment.py` | passed | PASS |
| `pytest test_qa_foundation_authorization.py` | passed | PASS |

---

## Results

| Suite | Tests | Result |
|-------|-------|--------|
| Approval schema (scope + regression + security) | 45 | ✅ 45 PASSED |
| Migration + gate + RBAC + scope + auth | 73 + 3 skip | ✅ 73 PASSED, 3 SKIPPED |
| **Total** | **118 + 3 skip** | **✅ ALL PASSED** |

No failures. No pre-existing failures outstanding.

---

## Scope Compliance

| Requirement | Status |
|-------------|--------|
| No runtime matching logic changed | ✅ Compliant |
| No `approval_service.py` changes | ✅ Compliant |
| No `approval_repository.py` changes | ✅ Compliant |
| No `VALID_ACTION_TYPES` changes | ✅ Compliant |
| No `ACTION_CODE_REGISTRY` changes | ✅ Compliant |
| No MMD runtime files changed | ✅ Compliant |
| No migrations added in this slice | ✅ Compliant |
| No API endpoints added | ✅ Compliant |
| No frontend/Admin UI added | ✅ Compliant |
| Alembic head is `0012` (single linear) | ✅ Confirmed |
| All approval schema tests green | ✅ Confirmed |
| RBAC registry/seed green after REG-02 | ✅ Confirmed |
| CI/PR gate covers scope schema test | ✅ Confirmed |

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Future P0-A-15B runtime activation bypasses T-SA test requirements | High | P0-A-14 §14 lists T-SA-01–T-SA-12 as mandatory prerequisites; locked in contract |
| New MMD action codes added without updating shared alignment test | Medium | Attribution comment pattern in `_EXPECTED_ADMIN_MMD_CODES` makes intent visible; CI catches drift |
| `effective_from`/`effective_to` timezone enforcement left to future slice | Low | Fields have `timezone=True`; documented as future runtime concern |

---

## Recommended Next Slice

**P0-A-15B — ApprovalRule Scope-Aware Matching Runtime Activation**

Prerequisites (all deferred debts D-01 through D-05 must be resolved):
1. T-SA-01 through T-SA-12 tests from P0-A-14 §14 must be created and passing.
2. `ApprovalRuleCreate` schema updated to accept optional scope fields.
3. `get_rules_for_action` updated per matching precedence contract (P0-A-14 §7).
4. Seed data updated for scope-qualified rules.
5. Hard Mode MOM v3 gate is MANDATORY.

---

## Stop Conditions Hit

None.

| Condition | Result |
|-----------|--------|
| Alembic graph has multiple heads | ❌ Not triggered — single head `0012` |
| Scope schema test fails | ❌ Not triggered — 12/12 passed |
| Migration baseline fails | ❌ Not triggered — passed |
| Approval behavior/security event tests fail | ❌ Not triggered — passed |
| RBAC registry drift remains | ❌ Not triggered — REG-02 resolved |
| CI/PR gate does not cover schema test | ❌ Not triggered — confirmed present |
| Closure requires runtime implementation | ❌ Not triggered — verification only |
| Closure requires touching MMD files | ❌ Not triggered — none touched |

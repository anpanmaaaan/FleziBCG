# P0-A-15A Report — ApprovalRule Scope Applicability Additive Schema Foundation

| Field    | Value                                                                    |
|----------|--------------------------------------------------------------------------|
| Slice    | P0-A-15A                                                                 |
| Date     | 2026-05-04                                                               |
| Author   | AI Brain (Hard Mode MOM v3)                                              |
| Status   | CLOSED — SCHEMA FOUNDATION COMPLETE                                      |
| Depends  | P0-A-14 `approval-rule-scope-applicability-contract.md`                  |

---

## Summary

P0-A-15A is the **additive schema/model foundation** slice for scope-aware `ApprovalRule` applicability.

Per the P0-A-14 contract, nullable scope applicability fields were added to the `ApprovalRule` ORM model and Alembic migration `0012`. No runtime matching logic was changed. No API or frontend changes were made. No MMD files were touched.

12 new schema tests pass. All existing approval tests pass. Alembic head is now `0012` (single linear head). CI/PR gate updated.

---

## Routing

| Field          | Value                                                                                                                           |
|----------------|---------------------------------------------------------------------------------------------------------------------------------|
| Selected brain | MOM Brain                                                                                                                       |
| Selected mode  | Architecture + QA + Strict                                                                                                      |
| Hard Mode MOM  | v3                                                                                                                              |
| Reason         | ApprovalRule schema change is governance-adjacent; touches tenant/scope auth truth; DB migration enforces operational governance |

---

## Hard Mode MOM v3 Gate

| Gate Artifact           | Status                                                                |
|-------------------------|-----------------------------------------------------------------------|
| Design Evidence Extract | ✅ Complete                                                            |
| Event Map               | ✅ Complete — no new events emitted                                    |
| Invariant Map           | ✅ Complete — 8 invariants verified                                    |
| State Transition Map    | ✅ N/A — no state machine changed                                      |
| Test Matrix             | ✅ Complete — 12 test coverage points defined                          |
| Verdict                 | ✅ ALLOW_P0A15A_APPROVAL_RULE_SCOPE_SCHEMA_FOUNDATION                  |

---

## Selected Option

**Option A — Additive schema/model foundation**

Criteria met:
- `ApprovalRule` safely accepts nullable fields (no NOT NULL constraints broken)
- Alembic graph is linear (single head `0011` → `0012`)
- Field names unambiguous from P0-A-14 contract §6
- No runtime matching change required

---

## ApprovalRule Scope Schema Decision

Fields added to `ApprovalRule` ORM model:

| Field                  | Type              | Nullable | Purpose                                              |
|------------------------|-------------------|----------|------------------------------------------------------|
| `governed_action_type` | `String(64)`      | Yes      | Future match against governed action type namespace  |
| `governed_resource_type` | `String(64)`    | Yes      | Future match against specific resource type          |
| `scope_ref`            | `String(256)`     | Yes      | Future match against canonical scope path            |
| `scope_type`           | `String(32)`      | Yes      | Future match against scope level (e.g. "plant")      |
| `priority`             | `Integer`         | Yes      | Future explicit tie-break for same-level rules       |
| `effective_from`       | `DateTime(tz=True)` | Yes    | Future time-bounded activation                       |
| `effective_to`         | `DateTime(tz=True)` | Yes    | Future time-bounded expiry                           |

All fields default to `None`. Existing `ApprovalRule` rows require no backfill.

The `UniqueConstraint` on `(action_type, approver_role_code, tenant_id)` is unchanged.

---

## Migration Decision

| Field        | Value                                                       |
|--------------|-------------------------------------------------------------|
| Revision     | `0012`                                                      |
| Revises      | `0011`                                                      |
| File         | `0012_add_scope_applicability_to_approval_rules.py`         |
| Type         | Additive only — `op.add_column` with `nullable=True`        |
| Downgrade    | Implemented — `op.drop_column` for all 7 new columns       |
| Head before  | `0011`                                                      |
| Head after   | `0012` (single linear head confirmed via `alembic heads`)   |

---

## Backward Compatibility Decision

- Existing `ApprovalRule` rows are unaffected (nullable fields, no backfill).
- `get_rules_for_action` in `approval_repository.py` is UNCHANGED.
- Existing `action_type + tenant_id` rule matching is UNCHANGED.
- Wildcard `"*"` tenant fallback is UNCHANGED.
- `VALID_ACTION_TYPES` in `approval_service.py` is UNCHANGED.
- `ApprovalRuleResponse` schema now exposes the 7 new nullable fields; all callers with `from_attributes=True` are backward-safe.
- No existing tests were broken.

---

## Files Inspected

| File                                                                              | Purpose                                      |
|-----------------------------------------------------------------------------------|----------------------------------------------|
| `docs/audit/p0-a-14-approval-rule-scope-applicability-decision-report.md`         | P0-A-14 CLOSED report — field candidates    |
| `docs/design/01_foundation/approval-rule-scope-applicability-contract.md`         | Authoritative field names and nullability    |
| `backend/app/models/approval.py`                                                  | Current ApprovalRule ORM — no scope fields  |
| `backend/app/repositories/approval_repository.py`                                 | `get_rules_for_action` — MUST NOT change    |
| `backend/app/schemas/approval.py`                                                 | `ApprovalRuleResponse` Pydantic schema       |
| `backend/alembic/versions/0011_add_governed_resource_identity_to_approvals.py`    | Prior migration — `down_revision: "0010"`   |
| `backend/tests/test_alembic_baseline.py`                                          | Head lock — required `"0011"` update        |
| `backend/tests/test_pr_gate_workflow_config.py`                                   | PR gate guard                               |
| `.github/workflows/pr-gate.yml`                                                   | Existing approval test lines 165-167        |
| `.github/workflows/backend-ci.yml`                                                | Existing approval test lines 258-276        |
| `backend/tests/test_approval_service_current_behavior.py`                         | 17-test regression lock                     |
| `backend/tests/test_approval_governed_resource_identity_schema.py`                | 10-test P0-A-13 schema lock                 |
| `backend/tests/test_approval_security_events.py`                                  | 6-test security event emission              |

---

## Files Changed

| File                                                                              | Change Type | Notes                                          |
|-----------------------------------------------------------------------------------|-------------|------------------------------------------------|
| `backend/alembic/versions/0012_add_scope_applicability_to_approval_rules.py`      | Created     | Additive migration — 7 nullable columns        |
| `backend/app/models/approval.py`                                                  | Modified    | Added 7 nullable scope fields to `ApprovalRule` |
| `backend/app/schemas/approval.py`                                                 | Modified    | `ApprovalRuleResponse` exposes 7 new fields    |
| `backend/tests/test_approval_rule_scope_applicability_schema.py`                  | Created     | 12 schema foundation tests                     |
| `backend/tests/test_alembic_baseline.py`                                          | Modified    | Updated expected head from `"0011"` to `"0012"` |
| `backend/tests/test_pr_gate_workflow_config.py`                                   | Modified    | Added guard for new test file in PR gate       |
| `.github/workflows/pr-gate.yml`                                                   | Modified    | Added `test_approval_rule_scope_applicability_schema.py` |
| `.github/workflows/backend-ci.yml`                                                | Modified    | Added P0-A-15A test step                       |

**No runtime matching logic changed. No MMD files touched. No API endpoints added.**

---

## Tests Added / Updated

### New: `backend/tests/test_approval_rule_scope_applicability_schema.py` (12 tests)

| Test | Coverage |
|------|---------|
| `test_approval_rule_has_governed_action_type_field` | governed_action_type field present and writable |
| `test_approval_rule_has_governed_resource_type_field` | governed_resource_type field present |
| `test_approval_rule_has_scope_ref_field` | scope_ref field present |
| `test_approval_rule_has_scope_type_field` | scope_type field present |
| `test_approval_rule_has_priority_field` | priority integer field present |
| `test_approval_rule_has_effective_from_field` | effective_from datetime field present |
| `test_approval_rule_has_effective_to_field` | effective_to datetime field present |
| `test_approval_rule_scope_fields_are_all_nullable` | All new fields default to None (backward compat) |
| `test_existing_approval_rule_fields_remain_unchanged` | action_type, approver_role_code, tenant_id, is_active unchanged |
| `test_wildcard_tenant_rule_valid_at_schema_level` | Wildcard `"*"` rule valid with new nullable fields |
| `test_approval_rule_scope_columns_exist_in_db_schema` | SQLite schema inspection confirms all 7 columns |
| `test_no_scope_aware_matching_implemented` | Source-level: get_rules_for_action has no scope matching |

### Updated: `backend/tests/test_alembic_baseline.py`
- `test_alembic_head_is_baseline`: expected head updated `"0011"` → `"0012"`

### Updated: `backend/tests/test_pr_gate_workflow_config.py`
- Added `test_approval_rule_scope_applicability_schema_tests_are_in_pr_gate`

---

## Verification Commands Run

| Command | Tests | Result |
|---------|-------|--------|
| `git status --short` | — | P0-A-15A files + pre-existing unrelated changes noted |
| `alembic heads` | — | `0012 (head)` — single linear head ✅ |
| `pytest tests/test_approval_rule_scope_applicability_schema.py` | 12 | **12 passed** ✅ |
| `pytest tests/test_approval_service_current_behavior.py tests/test_approval_governed_resource_identity_schema.py tests/test_approval_security_events.py` | 33 | **33 passed** ✅ |
| `pytest tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py tests/test_pr_gate_workflow_config.py` | 20+3 skipped | **20 passed, 3 skipped** ✅ |
| `pytest tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_scope_rbac_foundation_alignment.py tests/test_qa_foundation_authorization.py` | 52+1 failed | **52 passed, 1 pre-existing failure** ⚠️ |

---

## Results

| Metric                      | Value                  |
|-----------------------------|------------------------|
| New tests (scope schema)    | 12 passed              |
| Approval regression tests   | 33 passed (no change)  |
| Migration/bootstrap tests   | 20 passed, 3 skipped   |
| RBAC/scope/auth tests       | 52 passed, 1 pre-existing failure (unrelated) |
| Total tests this session    | **117 passed**         |
| Runtime code changes        | 0                      |
| New migration               | 1 (additive)           |
| New test files              | 1                      |
| MMD files touched           | 0                      |

---

## Pre-Existing Failure (Unrelated to P0-A-15A)

`test_action_code_registry_contains_exactly_canonical_set` — **FAILED**

Cause: `admin.master_data.reason_code.manage` was added to `backend/app/security/rbac.py` by the MMD team (commit `fe85b956 docs(mmd): define Reason Code write governance`) without updating the registry alignment test expectation.

P0-A-15A did NOT touch `rbac.py`. This failure was present before this slice. Resolution is the MMD team's responsibility. Per task instructions, this file MUST NOT be modified by P0-A-15A.

---

## Scope Compliance

| Requirement                                         | Status       |
|-----------------------------------------------------|--------------|
| No runtime matching logic changed                   | ✅ Compliant  |
| No `approval_service.py` changes                    | ✅ Compliant  |
| No `approval_repository.py` changes                 | ✅ Compliant  |
| No `approvals.py` API changes                       | ✅ Compliant  |
| No `VALID_ACTION_TYPES` changes                     | ✅ Compliant  |
| No `ACTION_CODE_REGISTRY` changes                   | ✅ Compliant  |
| No MMD source/tests/docs changed                    | ✅ Compliant  |
| No frontend/Admin UI added                          | ✅ Compliant  |
| All new fields nullable                             | ✅ Compliant  |
| Migration is additive and linear                    | ✅ Compliant  |
| CI/PR gate updated                                  | ✅ Compliant  |
| Existing approval tests unbroken                    | ✅ Compliant  |

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Future runtime slice adds `scope_ref` to `get_rules_for_action` without T-SA test coverage | High | P0-A-14 contract §14 lists T-SA-01–T-SA-12 as required before runtime activation |
| NULL semantics for new fields (match-all vs. match-none) mis-interpreted | Medium | P0-A-14 contract §8 defines NULL = match-all; documented in contract |
| `effective_from`/`effective_to` evaluated at wrong timezone boundary | Low | Fields carry `timezone=True`; enforcement is future runtime slice concern |
| Pre-existing `test_action_code_registry_contains_exactly_canonical_set` failure causes CI noise | Low | MMD team must update the test; P0-A-15A cannot resolve without touching out-of-scope files |

---

## Recommended Next Slice

**P0-A-15B: ApprovalRule Scope-Aware Matching Runtime Activation**

Prerequisites before P0-A-15B may begin:
1. P0-A-15A CLOSED (this report).
2. T-SA-01 through T-SA-12 tests defined in P0-A-14 contract §14 must be created and passing.
3. `get_rules_for_action` in `approval_repository.py` must be updated per matching precedence contract (P0-A-14 §7).
4. `ApprovalRuleCreate` schema must accept optional scope fields.
5. Seed data must be updated to support scope-qualified rules.
6. Hard Mode MOM v3 gate is MANDATORY for P0-A-15B.

---

## Stop Conditions Hit

None. All stop conditions evaluated:

| Condition | Result |
|-----------|--------|
| Alembic graph has multiple heads | ❌ Not triggered — single head `0012` |
| Additive nullable schema not guaranteed | ❌ Not triggered — all fields nullable |
| Field naming conflicts with P0-A-14 | ❌ Not triggered — exact names from contract §6 |
| Implementation requires runtime matching | ❌ Not triggered — schema only |
| Implementation requires API redesign | ❌ Not triggered — nullable fields, backward-safe |
| Implementation requires MMD files | ❌ Not triggered — no MMD files touched |
| Safe migration boundary not maintained | ❌ Not triggered — purely additive |

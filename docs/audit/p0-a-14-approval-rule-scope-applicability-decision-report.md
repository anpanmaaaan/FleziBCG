# P0-A-14 Audit Report — Approval Rule Scope-Aware Applicability Decision

| Field        | Value                                                                 |
|--------------|-----------------------------------------------------------------------|
| Slice        | P0-A-14                                                               |
| Date         | 2026-05-04                                                            |
| Author       | AI Brain (Hard Mode MOM v3)                                           |
| Status       | CLOSED — DOCS-ONLY                                                    |
| Depends      | P0-A-13B `governed-action-type-registry-contract.md`                  |

---

## Summary

P0-A-14 is a **design-only decision slice**. No runtime code, migration, or test was changed.

The purpose was to lock the contract for how `ApprovalRule` applicability must evolve to support scope-aware matching before any runtime adoption occurs.

A contract document was created at:  
`docs/design/01_foundation/approval-rule-scope-applicability-contract.md`

All verification tests passed. Hard Mode MOM v3 gate was fully executed.

---

## Routing

| Field              | Value                                                  |
|--------------------|--------------------------------------------------------|
| Selected brain     | MOM Brain                                              |
| Selected mode      | Architecture + QA + Strict                             |
| Hard Mode MOM      | v3                                                     |
| Reason             | Approval rule matching is execution-adjacent; scope/tenant auth is governed; design lock for future runtime slice requires full gate |

---

## Hard Mode MOM v3 Gate

| Gate Artifact         | Status   |
|-----------------------|----------|
| Design Evidence Extract | ✅ Complete |
| Event Map             | ✅ Complete |
| Invariant Map         | ✅ Complete |
| State Transition Map  | ✅ N/A (no state machine changed) |
| Test Matrix           | ✅ Complete |
| Verdict               | ✅ ALLOW_P0A14_APPROVAL_RULE_SCOPE_APPLICABILITY_DECISION |

---

## Selected Option

**Option A: Create scope applicability contract (docs-only)**

A runtime option (Option B) was available but not selected. Runtime changes are deferred to a future slice that includes DB migration, service change, and T-SA-01 through T-SA-12 tests per Section 14 of the contract.

---

## Scope Applicability Decision

The following design decisions are now locked in the contract:

1. `ApprovalRule` must become scope-aware, governed-resource-type-aware, and governed-action-type-aware in a future runtime slice.

2. New matching dimensions: `governed_action_type`, `governed_resource_type`, `scope_ref`, `scope_type`.

3. All new fields MUST be nullable to preserve backward compatibility.

4. Existing rules (action_type + tenant_id only) continue to match via legacy fallback.

---

## Rule Matching Precedence Decision

The following precedence order is locked for future runtime activation:

| Priority | Criteria                                                            |
|----------|---------------------------------------------------------------------|
| 1        | tenant + scope_ref + governed_resource_type + governed_action_type |
| 2        | tenant + scope_ref + governed_action_type                           |
| 3        | tenant + governed_resource_type + governed_action_type              |
| 4        | tenant + governed_action_type                                       |
| 5        | tenant + action_type (legacy)                                       |
| 6        | wildcard tenant `"*"` + action_type                                 |

---

## Backward Compatibility Decision

- Existing `ApprovalRule` rows are unaffected.
- New fields default to NULL (match-all for new dimensions).
- Legacy action_type + tenant_id matching is preserved as priority 5/6 fallback.
- No existing tests are broken.

---

## Runtime Posture Decision

**UNCHANGED in P0-A-14.**

Current runtime continues to match `action_type + tenant_id` only, with `"*"` wildcard for tenant. No scope-aware evaluation occurs at runtime after this slice.

---

## Files Inspected

| File                                                                         | Purpose                                      |
|------------------------------------------------------------------------------|----------------------------------------------|
| `backend/app/models/approval.py`                                             | ApprovalRule + ApprovalRequest ORM models    |
| `backend/app/repositories/approval_repository.py`                           | Rule lookup logic                            |
| `backend/app/services/approval_service.py`                                   | VALID_ACTION_TYPES; security event emission  |
| `backend/app/schemas/approval.py`                                            | Pydantic request/response contracts          |
| `backend/app/models/rbac.py`                                                 | Scope canonical hierarchy                    |
| `backend/app/security/rbac.py`                                               | RBAC action registry                         |
| `backend/alembic/versions/0011_add_governed_resource_identity_to_approvals.py` | Migration head                             |
| `docs/design/01_foundation/governed-action-approval-applicability-contract.md` | P0-A-11C contract (Section 9 intent)       |
| `docs/design/01_foundation/governed-action-type-registry-contract.md`        | P0-A-13B contract (action type taxonomy)    |
| `backend/tests/test_approval_service_current_behavior.py`                    | 17-test regression lock                      |
| `backend/tests/test_approval_governed_resource_identity_schema.py`           | 10-test P0-A-13 schema lock                  |
| `backend/tests/test_approval_security_events.py`                             | 6-test security event emission               |
| `backend/tests/test_pr_gate_workflow_config.py`                              | 5-test CI/PR gate guard                      |
| `backend/tests/test_rbac_action_registry_alignment.py`                       | RBAC action registry alignment               |
| `backend/tests/test_rbac_seed_alignment.py`                                  | RBAC seed alignment                          |
| `backend/tests/test_scope_rbac_foundation_alignment.py`                      | Scope RBAC foundation                        |
| `backend/tests/test_qa_foundation_authorization.py`                          | QA foundation authorization                  |

---

## Files Changed

| File                                                                              | Change Type | Notes                            |
|-----------------------------------------------------------------------------------|-------------|----------------------------------|
| `docs/design/01_foundation/approval-rule-scope-applicability-contract.md`         | Created     | P0-A-14 scope applicability lock |
| `docs/audit/p0-a-14-approval-rule-scope-applicability-decision-report.md`         | Created     | This report                      |

**No runtime files changed. No migrations created. No tests created or modified.**

---

## Verification Commands Run

| Command                                                             | Tests | Result  |
|---------------------------------------------------------------------|-------|---------|
| `pytest tests/test_approval_service_current_behavior.py`            | 17    | PASSED  |
| `pytest tests/test_approval_governed_resource_identity_schema.py`   | 10    | PASSED  |
| `pytest tests/test_approval_security_events.py`                     | 6     | PASSED  |
| `pytest tests/test_pr_gate_workflow_config.py`                      | 5     | PASSED  |
| `pytest tests/test_rbac_action_registry_alignment.py`               | —     | PASSED  |
| `pytest tests/test_rbac_seed_alignment.py`                          | —     | PASSED  |
| `pytest tests/test_scope_rbac_foundation_alignment.py`              | —     | PASSED  |
| `pytest tests/test_qa_foundation_authorization.py`                  | —     | PASSED  |

Combined totals: **91 tests passed, 0 failed, 1 warning (benign DB name warning)**.

---

## Results

| Metric                | Value    |
|-----------------------|----------|
| Total tests passed    | 91       |
| Total tests failed    | 0        |
| Runtime code changes  | 0        |
| Migration changes     | 0        |
| Test file changes     | 0        |
| New contract docs     | 1        |
| Audit report docs     | 1        |

---

## Unrelated Modified Files Noted

The following files were modified in the workspace but are **unrelated to P0-A-14** (confirmed by user):

| File                                                                  | Status     | Note                              |
|-----------------------------------------------------------------------|------------|-----------------------------------|
| `backend/tests/test_approval_governed_resource_identity_schema.py`   | M (git)    | Modified by another team; unrelated |
| `frontend/tsconfig.json`                                              | M (git)    | Frontend config; unrelated          |
| `docs/audit/p0-a-12c-approval-governed-resource-identity-isolation.md` | ?? (untracked) | Created by another team; unrelated |
| `CLAUDE.md`                                                           | ?? (untracked) | Project context file; unrelated    |

These are not part of P0-A-14 scope.

---

## Scope Compliance

| Requirement                                    | Status     |
|------------------------------------------------|------------|
| No runtime changes                             | ✅ Compliant |
| No migration changes                           | ✅ Compliant |
| No test changes                                | ✅ Compliant |
| Contract created                               | ✅ Complete  |
| Hard Mode MOM v3 gate executed                 | ✅ Complete  |
| Backward compatibility preserved               | ✅ Confirmed |
| Existing tests unbroken                        | ✅ 91 passed |

---

## Risks

| Risk                                                                   | Severity | Mitigation                                            |
|------------------------------------------------------------------------|----------|-------------------------------------------------------|
| Future runtime slice bypasses matching precedence defined in contract  | High     | Contract is binding; future slice must cite P0-A-14   |
| NULL semantics for new fields mis-implemented (match-all vs. match-none) | Medium | Section 8 of contract defines NULL = match-all         |
| Priority tie-break not implemented in future runtime slice             | Low      | Section 7 defines priority resolution; T-SA-09 required |
| scope_ref as plain string may cause consistency drift                  | Low      | OQ-1 in contract tracks this open question             |

---

## Recommended Next Slice

**P0-A-15: Approval Rule Scope-Aware Migration + Runtime Activation**

Prerequisites before P0-A-15 may begin:
1. This contract (P0-A-14) is CLOSED.
2. All T-SA-01 through T-SA-12 tests defined in Section 14 of the contract must be written and pass.
3. A new Alembic migration adding nullable scope fields to `approval_rules` must be reviewed by Hard Mode MOM v3.
4. `get_rules_for_action` in `approval_repository.py` must be updated to accept and apply scope matching dimensions.

---

## Stop Conditions Hit

None. All gate conditions were satisfied. No blocking issues found.

---

## Final Verdict

> **P0-A-14 CLOSED.**  
> Approval Rule Scope-Aware Applicability Contract created and locked.  
> 91 tests passed. No runtime changes. No regressions.  
> Next slice: P0-A-15 (runtime activation, with migration and T-SA tests).

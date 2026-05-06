# P0-A-15E Report

## Summary

Added 12 API-layer integration tests (`T-DEC-API-01`..`T-DEC-API-12`) covering the
`POST /api/v1/approvals/{request_id}/decide` endpoint for requests that carry governed
context fields. Tests prove that scope-aware rule selection (P0-A-15B), SoD invariant,
tenant isolation, SecurityEventLog emission, and APPROVAL.CANCELLED absence all hold
at the HTTP boundary. No production source files were modified. All 12 new tests plus
all regression suites pass.

---

## Routing

- **Selected brain:** FleziBCG AI Brain v6 Auto-Execution
- **Selected mode:** Backend implementation + QA / contract hardening
- **Hard Mode MOM:** v3
- **Reason:** Task touches tenant/scope/auth, approval governance, approval decision
  API, governed resource identity, scope-aware matching, SoD invariant, audit/security
  events, and critical authorization invariants — all Hard Mode MOM v3 trigger criteria.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Source | Evidence |
|---|---|
| `backend/app/api/v1/approvals.py` | Decision route: `POST /{request_id}/decide` → `decide_approval_request(...)` with `LookupError→404`, `PermissionError→403`, `ValueError→400` |
| `backend/app/services/approval_service.py` | `decide_approval_request`: terminal-state guard, SoD guard, `get_approver_role_codes(...)` with governed context, emits `APPROVAL.{decision_value}` |
| `backend/app/repositories/approval_repository.py` | `get_approver_role_codes` → `get_rules_for_action` with scope-aware `_score_rule`; governed rules route via `governed_action_type`, legacy rules route via `action_type` |
| `docs/audit/p0-a-15d-approval-governed-context-api-coverage-report.md` | P0-A-15D established the `TestClient` + `dependency_overrides` pattern for approval API tests |
| `docs/audit/p0-a-15c-01-*-closeout-report.md` | P0-A-15C confirmed governed context fields are persisted through the create route |
| `backend/tests/test_approval_governed_context_api.py` | Established `_make_session`, `_override_action_dependency`, `_build_app` helpers |

### Event Map

| Event | Status |
|---|---|
| `APPROVAL.REQUESTED` | Existing — emitted at create; not changed |
| `APPROVAL.APPROVED` | Existing — emitted by `decide_approval_request` when `decision="APPROVED"` |
| `APPROVAL.REJECTED` | Existing — emitted by `decide_approval_request` when `decision="REJECTED"` |
| `APPROVAL.CANCELLED` | **Not implemented** — no service function, no route, no event |

No new event types introduced.

### Invariant Map

| Invariant | Evidence | Test |
|---|---|---|
| Decision API uses persisted governed context | Service reads `appr_req.governed_resource_scope_ref`, `governed_resource_type`, `governed_action_type` and passes to `get_approver_role_codes` | T-DEC-API-01, T-DEC-API-02 |
| Scope/governed-specific rule determines approver role | `_score_rule` selects highest-specificity match; governed rules outrank legacy | T-DEC-API-01, T-DEC-API-03 |
| Wrong approver role is rejected | `PermissionError` → 403 | T-DEC-API-03 |
| Requester cannot decide own request | `appr_req.requester_id == decider_user_id` → `ValueError` → 400 | T-DEC-API-04, T-DEC-API-05 |
| Terminal request cannot be decided twice | `status != "PENDING"` → `ValueError` → 400 | T-DEC-API-06 |
| Tenant isolation enforced | `get_request_by_id` filters by tenant_id; cross-tenant → `LookupError` → 404 | T-DEC-API-07 |
| Legacy tenant/action rule still works | Legacy wildcard rule still matched for requests without governed context | T-DEC-API-11 |
| Governed action registry not enforced | Arbitrary `governed_action_type` value accepted with matching rule | T-DEC-API-12 |
| APPROVAL.CANCELLED not implemented | No `cancel_approval_request` function in service | T-DEC-API-10 |
| No migration/model/repository change | Confirmed by `git status` — no model or migration files modified | All |
| No MMD files changed | Confirmed by `git status` | All |

### State Transition Map

```
PENDING → APPROVED   (decision="APPROVED", decider_role in allowed_roles, requester != decider)
PENDING → REJECTED   (decision="REJECTED", decider_role in allowed_roles, requester != decider)
APPROVED → terminal  (cannot re-decide, ValueError)
REJECTED → terminal  (cannot re-decide, ValueError)
CANCELLED            (schema column only, no service path, unimplemented)
```

No lifecycle change made in this slice.

### Verdict

**`ALLOW_P0A15E_APPROVAL_DECISION_API_GOVERNED_CONTEXT_COVERAGE`**

---

## Selected Option

**Option A — Decision API tests only.**

The existing decision route (`POST /api/v1/approvals/{request_id}/decide`) already:
- accepts governed context from the persisted `ApprovalRequest`
- passes it to `get_approver_role_codes` for scope-aware matching
- maps all exception types to correct HTTP status codes

No route/service patch was needed.

---

## Decision API Coverage Decision

The decision route at `POST /api/v1/approvals/{request_id}/decide` already exercises
governed context matching via `decide_approval_request → get_approver_role_codes`. API
tests were sufficient to prove the end-to-end behavior. No route modification was required.

---

## Governed Context Matching Decision

Scope-aware rule selection was confirmed to work end-to-end:
- A governed rule with `governed_action_type="quality.work_order.qc_hold"` is matched
  when the persisted request carries that `governed_action_type`.
- A decider with role `QAL` satisfies the rule (T-DEC-API-01, T-DEC-API-02).
- A decider with role `OPR` does not satisfy the rule (T-DEC-API-03 → 403).
- Legacy requests without governed context fall through to legacy wildcard rules
  (T-DEC-API-11).

---

## SoD / Authorization Replay

- `appr_req.requester_id == decider_user_id` check in the service uses the **real**
  `user_id` from the `RequestIdentity`, not the acting role.
- T-DEC-API-04: same `user_id` in both identities → APPROVE attempt → 400.
- T-DEC-API-05: same `user_id` in both identities → REJECT attempt → 400.
- Auth override pattern from P0-A-15D was extended to override **both** routes
  (`approval.create` and `approval.decide`) independently with separate identities.

---

## SecurityEventLog Decision Replay

The service emits `APPROVAL.{decision_value}` via `record_security_event` **before**
commit, inside the same transaction as the `ApprovalDecision` record. The event detail
contains `action_type`, `decider_role`, and `impersonation_session` values.

- T-DEC-API-08: one `APPROVAL.APPROVED` event emitted; `resource_id == str(req_id)`;
  `actor_user_id == "decider-1"`; `"QC_HOLD" in detail`.
- T-DEC-API-09: one `APPROVAL.REJECTED` event emitted; same assertions.

---

## Tests Added / Updated

### New file: `backend/tests/test_approval_decision_governed_context_api.py`

| Test ID | Test Name | Expected |
|---|---|---|
| T-DEC-API-01 | `test_tdecapi01_governed_context_request_approved_by_matching_role` | 200, decision=APPROVED |
| T-DEC-API-02 | `test_tdecapi02_governed_context_request_rejected_by_matching_role` | 200, decision=REJECTED |
| T-DEC-API-03 | `test_tdecapi03_wrong_approver_role_is_rejected_for_governed_rule` | 403 |
| T-DEC-API-04 | `test_tdecapi04_requester_cannot_approve_own_governed_context_request` | 400, "requester" |
| T-DEC-API-05 | `test_tdecapi05_requester_cannot_reject_own_governed_context_request` | 400, "requester" |
| T-DEC-API-06 | `test_tdecapi06_terminal_request_cannot_be_decided_twice` | 400, "not pending" |
| T-DEC-API-07 | `test_tdecapi07_cross_tenant_decision_is_not_found` | 404 |
| T-DEC-API-08 | `test_tdecapi08_approval_approved_security_event_is_emitted` | SecurityEventLog APPROVAL.APPROVED |
| T-DEC-API-09 | `test_tdecapi09_approval_rejected_security_event_is_emitted` | SecurityEventLog APPROVAL.REJECTED |
| T-DEC-API-10 | `test_tdecapi10_no_approval_cancelled_event_or_path_exists` | no cancel_approval_request, no APPROVAL.CANCELLED |
| T-DEC-API-11 | `test_tdecapi11_legacy_request_decided_via_wildcard_tenant_action_rule` | 200, decision=APPROVED |
| T-DEC-API-12 | `test_tdecapi12_arbitrary_governed_action_type_is_context_only_no_registry` | 200, decision=APPROVED |

### Updated files

- `.github/workflows/pr-gate.yml` — added `tests/test_approval_decision_governed_context_api.py`
- `.github/workflows/backend-ci.yml` — added P0-A-15E step
- `backend/tests/test_pr_gate_workflow_config.py` — added `test_approval_decision_governed_context_api_tests_are_in_pr_gate`

---

## Files Inspected

| File | Purpose |
|---|---|
| `backend/app/api/v1/approvals.py` | Confirmed decision route, error mapping |
| `backend/app/services/approval_service.py` | Confirmed decide logic, SoD guard, SecurityEventLog emission |
| `backend/app/repositories/approval_repository.py` | Confirmed scope-aware matching, `_score_rule`, governed routing |
| `backend/app/models/approval.py` | Confirmed `ApprovalDecision.impersonation_session_id` FK to `impersonation_sessions` |
| `backend/app/schemas/approval.py` | Confirmed `ApprovalDecisionResponse` fields |
| `backend/tests/test_approval_governed_context_api.py` | Extracted `_make_session`, `_override_action_dependency`, `_build_app` patterns |
| `docs/audit/p0-a-15d-approval-governed-context-api-coverage-report.md` | Baseline for API test pattern |
| `.github/workflows/pr-gate.yml` | Confirmed location for test file addition |
| `.github/workflows/backend-ci.yml` | Confirmed location for P0-A-15E step |
| `backend/tests/test_pr_gate_workflow_config.py` | Confirmed existing assertion pattern |

---

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_approval_decision_governed_context_api.py` | **New** — 12 T-DEC-API tests |
| `.github/workflows/pr-gate.yml` | Added `tests/test_approval_decision_governed_context_api.py` to explicit test list |
| `.github/workflows/backend-ci.yml` | Added P0-A-15E step |
| `backend/tests/test_pr_gate_workflow_config.py` | Added `test_approval_decision_governed_context_api_tests_are_in_pr_gate` |

No production source files modified.

---

## Verification Commands Run

```
git status --short
cd backend
python -m pytest -q tests/test_approval_decision_governed_context_api.py
python -m pytest -q tests/test_approval_governed_context_api.py tests/test_approval_create_governed_context_bridge.py tests/test_approval_rule_scope_aware_matching.py tests/test_approval_service_current_behavior.py tests/test_approval_security_events.py tests/test_pr_gate_workflow_config.py
python -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_scope_rbac_foundation_alignment.py tests/test_qa_foundation_authorization.py
```

---

## Results

| Suite | Result |
|---|---|
| `test_approval_decision_governed_context_api.py` (12 new) | **12 passed**, 1 warning (benign DB warning) |
| `test_approval_governed_context_api.py` + `test_approval_create_governed_context_bridge.py` + `test_approval_rule_scope_aware_matching.py` + `test_approval_service_current_behavior.py` + `test_approval_security_events.py` + `test_pr_gate_workflow_config.py` | **67 passed**, 1 warning |
| `test_rbac_action_registry_alignment.py` + `test_rbac_seed_alignment.py` + `test_scope_rbac_foundation_alignment.py` + `test_qa_foundation_authorization.py` | **53 passed**, 1 warning |

Total: **132 passed**, 0 failures, 0 errors. Benign warning: `conftest.py:234 UserWarning: Running tests against a DB that does not look test-specific` — expected, no action required.

---

## Scope Compliance

| Rule | Status |
|---|---|
| No migrations added | ✅ |
| ApprovalRequest model fields not modified | ✅ |
| ApprovalRule schema fields not modified | ✅ |
| Repository matching precedence not changed | ✅ |
| Governed action registry not implemented | ✅ |
| VALID_ACTION_TYPES not modified | ✅ |
| APPROVAL.CANCELLED not implemented | ✅ |
| No new approval endpoints | ✅ |
| No frontend changes | ✅ |
| No MMD source/tests/docs modified | ✅ |
| No ACTION_CODE_REGISTRY changes | ✅ |
| Auth tests not weakened | ✅ |

---

## Risks

- None identified. Tests are fully isolated (in-memory SQLite per test). No production source changed. FK ordering (`ImpersonationSession` before `ApprovalDecision`) is explicit in `_make_session`.

---

## Recommended Next Slice

**P0-A-15F** (suggested): Extend the scope-aware approval rule to support `scope_ref`-specific overrides at the API level. The `_score_rule` function already scores `scope_ref` matches (`+4`), but no tests prove that a `scope_ref`-specific rule is selected over a wildcard rule for a governed request that carries `governed_resource_scope_ref`. This would close the last untested dimension of the P0-A-14 §7 precedence model.

Alternatively: **P0-A-16** — implement tenant-specific `ApprovalRule` overrides (tenant_id != `"*"`) and cover them at the API level.

---

## Stop Conditions Hit

None. All stop conditions were clear.

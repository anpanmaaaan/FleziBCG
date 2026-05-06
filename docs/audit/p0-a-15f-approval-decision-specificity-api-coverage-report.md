# P0-A-15F Report

## Summary

Added 19 API-layer integration tests in `backend/tests/test_approval_decision_specificity_api.py`
covering the 12 required T-SPEC-API IDs (plus 7 negative/sub-case variants) for approval decision
specificity precedence and wildcard fallback behavior through the HTTP boundary. Tests prove that
`_score_rule` precedence from P0-A-14 §7 / P0-A-15B is honored at `POST /api/v1/approvals/{request_id}/decide`.
No production source files were modified. All 19 new tests pass; all regression suites remain green
(133 total passed across all related suites).

---

## Routing

- **Selected brain:** FleziBCG AI Brain v6 Auto-Execution
- **Selected mode:** Backend implementation + QA / contract hardening
- **Hard Mode MOM:** v3
- **Reason:** Task touches tenant/scope/auth, approval governance, decision API, scope-aware
  rule matching, SoD invariant, audit/security events, and critical authorization invariants —
  all Hard Mode MOM v3 trigger criteria.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Source | Evidence |
|---|---|
| `backend/app/repositories/approval_repository.py` | `_score_rule`: +8 tenant-specific, +4 scope_ref match, +2 governed_resource_type match, +1 governed_action_type present; None = incompatible. "First non-empty level wins" → max score group returned. Governed rules route via `governed_action_type`; legacy rules via `action_type`. |
| `backend/app/services/approval_service.py` | `decide_approval_request` passes `scope_ref=appr_req.governed_resource_scope_ref`, `governed_resource_type`, `governed_action_type` to `get_approver_role_codes`. Emits `APPROVAL.{decision_value}`. |
| `backend/app/api/v1/approvals.py` | Decision route: `LookupError→404`, `PermissionError→403`, `ValueError→400`. |
| `docs/audit/p0-a-15e-approval-decision-governed-context-api-coverage-report.md` | P0-A-15E established 12 baseline decision API tests with the `_build_app` / `_override_action_dependency` pattern. |
| `docs/audit/p0-a-15d-approval-governed-context-api-coverage-report.md` | P0-A-15D established the TestClient + dependency_overrides pattern for approval API tests. |
| `backend/app/models/approval.py` | `ApprovalRule` UniqueConstraint: `(action_type, approver_role_code, tenant_id)` — different role_codes allow multiple coexisting rules per action+tenant. |

### Event Map

| Event | Status |
|---|---|
| `APPROVAL.REQUESTED` | Existing — emitted at create; not changed |
| `APPROVAL.APPROVED` | Existing — emitted on `decision="APPROVED"` |
| `APPROVAL.REJECTED` | Existing — emitted on `decision="REJECTED"` |
| `APPROVAL.CANCELLED` | **Not implemented** — no service function, no route, no event |

No new event types introduced.

### Invariant Map

| Invariant | Evidence | Test |
|---|---|---|
| Scope-specific rule beats tenant/action rule | `_score_rule` score+4 for scope match vs score 0 for no-scope rule | T-SPEC-API-01, T-SPEC-API-01b |
| Scope-specific rule beats tenant wildcard * | score 8+4=12 vs score 0; tenant-b rule not in tenant-a query | T-SPEC-API-02 |
| Full governed rule beats scope-only rule | score 4+2+1=7 vs score 4; max score group returned | T-SPEC-API-03, T-SPEC-API-03b |
| Tenant + governed_action rule beats tenant + legacy rule | score 8+1=9 vs score 8 | T-SPEC-API-04 |
| Wrong scope is incompatible → fallback to no-scope rule | `_score_rule` returns None for scope mismatch | T-SPEC-API-05, T-SPEC-API-05b |
| Wrong governed_action_type → not action-compatible → fallback to legacy | Governed rule routing via governed_action_type; mismatch = excluded | T-SPEC-API-06, T-SPEC-API-06b |
| Wildcard fallback still decides legacy requests | score 0 rule still matched | T-SPEC-API-07 |
| Tenant isolation holds even with other-tenant specificity rules | `tenant_id.in_([tenant_id, "*"])` excludes other-tenant rules | T-SPEC-API-08, T-SPEC-API-08b |
| Priority tie-breaking includes all tied-score roles | All max-score rules contribute to `allowed_roles` set | T-SPEC-API-09a, T-SPEC-API-09b |
| SecurityEventLog taxonomy unchanged | APPROVED / REJECTED only; no new types | T-SPEC-API-10, T-SPEC-API-10b |
| APPROVAL.CANCELLED not introduced | No service function, no events | T-SPEC-API-11 |
| Governed action registry not enforced | Arbitrary governed_action_type string works | T-SPEC-API-12 |
| No migration/model/repository/service/route change | Confirmed by `git status` | All |
| No MMD files changed | Confirmed by `git status` | All |

### State Transition Map

```
PENDING → APPROVED   (decision="APPROVED", decider_role in allowed_roles, requester != decider)
PENDING → REJECTED   (decision="REJECTED", decider_role in allowed_roles, requester != decider)
APPROVED → terminal  (cannot re-decide)
REJECTED → terminal  (cannot re-decide)
CANCELLED            (schema column only, no service path, unimplemented)
```

No lifecycle change made in this slice.

### Test Matrix

| Test ID | Description | Expected |
|---|---|---|
| T-SPEC-API-01 | Scope-specific rule (score 4) beats no-scope rule (score 0) | 200, QAL can decide |
| T-SPEC-API-01b | PMG (no-scope rule) is 403 when scope-specific QAL rule wins | 403 |
| T-SPEC-API-02 | Scope-specific tenant rule (score 12) beats wildcard (score 0) | 200, QAL can decide |
| T-SPEC-API-03 | Full governed rule (score 7) beats scope-only rule (score 4) | 200, QAL can decide |
| T-SPEC-API-03b | PMG (score 4 rule) is 403 when governed QAL rule wins | 403 |
| T-SPEC-API-04 | Tenant + governed_action rule (score 9) beats tenant + legacy (score 8) | 200, QAL can decide |
| T-SPEC-API-05 | Wrong scope → incompatible → fallback to no-scope PMG rule | 200, PMG can decide |
| T-SPEC-API-05b | QAL is 403 because its scope rule is excluded on mismatch | 403 |
| T-SPEC-API-06 | Wrong governed_action_type → not compatible → fallback to legacy PMG | 200, PMG can decide |
| T-SPEC-API-06b | QAL is 403 because governed rule not action-compatible | 403 |
| T-SPEC-API-07 | Wildcard fallback decides legacy request | 200 |
| T-SPEC-API-08 | Tenant isolation: tenant-b rule not fetched for tenant-a | 200, QAL from wildcard |
| T-SPEC-API-08b | MGR is 403 in tenant-a; its rule is tenant-b only | 403 |
| T-SPEC-API-09a | Priority tie: QAL (priority=1) is in allowed_roles → 200 | 200 |
| T-SPEC-API-09b | Priority tie: MGR (priority=2) is in allowed_roles → 200 | 200 |
| T-SPEC-API-10 | After APPROVED: exactly one APPROVAL.APPROVED event emitted | SecurityEventLog count=1 |
| T-SPEC-API-10b | After REJECTED: exactly one APPROVAL.REJECTED event emitted | SecurityEventLog count=1 |
| T-SPEC-API-11 | No APPROVAL.CANCELLED event or cancel_approval_request function | assert not hasattr |
| T-SPEC-API-12 | Arbitrary governed_action_type → decision succeeds, no registry | 200 |

### Verdict

**`ALLOW_P0A15F_APPROVAL_DECISION_API_SPECIFICITY_COVERAGE`**

---

## Selected Option

**Option A — API specificity tests only.**

The existing decision route and service already correctly implement the P0-A-14 §7 scoring model.
No route, service, repository, or model patch was required.

---

## Specificity API Coverage Decision

`_score_rule` scoring model was confirmed end-to-end through the HTTP boundary:

| Dimension | Rule field | Score | Mismatch behavior |
|---|---|---|---|
| Tenant-specific | `tenant_id != "*"` | +8 | Not fetched by query |
| Scope match | `scope_ref` non-null AND matches | +4 | `None` (excluded) |
| Resource type | `governed_resource_type` non-null AND matches | +2 | `None` (excluded) |
| Governed action | `governed_action_type` present | +1 | Not action-compatible |

All four dimensions were tested in isolation and combination through API-level tests.

---

## Wildcard Fallback Replay

Three fallback scenarios were verified:

1. **Scope mismatch** (T-SPEC-API-05): scope-specific rule excluded → no-scope rule wins.
2. **Wrong governed_action_type** (T-SPEC-API-06): governed rule not action-compatible → legacy rule wins.
3. **Pure legacy request** (T-SPEC-API-07): no context fields → wildcard rule wins.

All fallback paths return 200 with the fallback-role decider; the higher-specificity role's
decider returns 403 (confirmed in negative sub-tests).

---

## SecurityEventLog Replay

- T-SPEC-API-10: After `decision=APPROVED`, query for `event_type in (APPROVED, REJECTED, CANCELLED)` → exactly 1 result with `event_type=APPROVAL.APPROVED`.
- T-SPEC-API-10b: Same query after `decision=REJECTED` → exactly 1 result with `event_type=APPROVAL.REJECTED`.
- T-SPEC-API-11: `APPROVAL.CANCELLED` event count = 0; `cancel_approval_request` function does not exist in service.

No new event type was introduced in this slice.

---

## Tests Added / Updated

### New file: `backend/tests/test_approval_decision_specificity_api.py`

19 tests covering T-SPEC-API-01 through T-SPEC-API-12 (with 7 negative/sub-case variants).

### Updated files

- `.github/workflows/pr-gate.yml` — added `tests/test_approval_decision_specificity_api.py`
- `.github/workflows/backend-ci.yml` — added P0-A-15F step
- `backend/tests/test_pr_gate_workflow_config.py` — added `test_approval_decision_specificity_api_tests_are_in_pr_gate`

---

## Files Inspected

| File | Purpose |
|---|---|
| `backend/app/repositories/approval_repository.py` | Confirmed `_score_rule` scoring, action routing, max-score group selection |
| `backend/app/services/approval_service.py` | Confirmed governed context forwarding to `get_approver_role_codes` |
| `backend/app/api/v1/approvals.py` | Confirmed error mapping (LookupError→404, PermissionError→403, ValueError→400) |
| `backend/app/models/approval.py` | Confirmed `ApprovalRule` UniqueConstraint `(action_type, approver_role_code, tenant_id)` |
| `backend/tests/test_approval_decision_governed_context_api.py` | Extracted helper pattern (`_make_session`, `_override_action_dependency`, `_build_app`) |
| `docs/audit/p0-a-15e-approval-decision-governed-context-api-coverage-report.md` | Baseline for P0-A-15E decision API test pattern |
| `.github/workflows/pr-gate.yml` | Confirmed location for test file addition |
| `.github/workflows/backend-ci.yml` | Confirmed location for P0-A-15F step |
| `backend/tests/test_pr_gate_workflow_config.py` | Confirmed existing assertion pattern |

---

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_approval_decision_specificity_api.py` | **New** — 19 tests (T-SPEC-API-01..T-SPEC-API-12 + 7 negative variants) |
| `.github/workflows/pr-gate.yml` | Added `tests/test_approval_decision_specificity_api.py` to explicit test list |
| `.github/workflows/backend-ci.yml` | Added P0-A-15F step |
| `backend/tests/test_pr_gate_workflow_config.py` | Added `test_approval_decision_specificity_api_tests_are_in_pr_gate` |

No production source files modified.

---

## Verification Commands Run

```
git status --short
cd backend
python -m pytest -q tests/test_approval_decision_specificity_api.py
python -m pytest -q tests/test_approval_decision_governed_context_api.py tests/test_approval_governed_context_api.py tests/test_approval_create_governed_context_bridge.py tests/test_approval_rule_scope_aware_matching.py tests/test_approval_service_current_behavior.py tests/test_approval_security_events.py tests/test_pr_gate_workflow_config.py tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_scope_rbac_foundation_alignment.py tests/test_qa_foundation_authorization.py
```

---

## Results

| Suite | Result |
|---|---|
| `test_approval_decision_specificity_api.py` (19 new) | **19 passed**, 1 warning (benign) |
| All approval + RBAC regression suites (11 files) | **133 passed**, 1 warning |

Total: **152 passed**, 0 failures, 0 errors. Benign warning: `conftest.py UserWarning: TEST DB NOT REACHABLE` or `Running tests against a DB that does not look test-specific` — expected, no action required.

---

## Scope Compliance

| Rule | Status |
|---|---|
| No migrations added | ✅ |
| ApprovalRequest model fields not modified | ✅ |
| ApprovalRule schema fields not modified | ✅ |
| Repository matching precedence not changed | ✅ |
| Approval service decision logic not changed | ✅ |
| Approval API route logic not changed | ✅ |
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

- None identified. All tests use isolated in-memory SQLite. No production source changed.
  `ApprovalRule` UniqueConstraint `(action_type, approver_role_code, tenant_id)` is respected
  in all test fixtures (different role_codes used for coexisting rules).

---

## Recommended Next Slice

**P0-A-16** (suggested): Tenant-specific `ApprovalRule` override coverage — verify that a
tenant-specific rule (score +8) consistently overrides a wildcard rule (score 0) for the
same action_type and role when both exist in the DB. This closes the remaining untested
dimension of P0-A-14 §7 at the API level (tenant-specific override without scope/governed dims).

Alternatively: **P0-A-17** — priority-level override within the same score group (i.e., two
rules at the same score, different priorities, verify deterministic sort output is stable
across re-runs).

---

## Stop Conditions Hit

None. All stop conditions were clear.

# P0-A-16 Report

## Summary

Added 14 API-layer integration tests in `backend/tests/test_approval_decision_tenant_override_api.py`
covering the 12 required T-TENANT-API IDs (plus 2 negative sub-case variants) for tenant-specific
approval rule override behavior through the HTTP decision boundary. Tests prove that the +8 score
for `tenant_id != "*"` from P0-A-14 §7 is correctly honored, that other-tenant rules are not
fetched, and that all SoD/terminal-state/SecurityEventLog invariants hold under tenant-specific
rules. No production source files were modified. All 14 new tests pass; all regression suites
remain green (153 total passed).

---

## Routing

- **Selected brain:** FleziBCG AI Brain v6 Auto-Execution
- **Selected mode:** Backend implementation + QA / contract hardening
- **Hard Mode MOM:** v3
- **Reason:** Touches tenant/scope/auth, approval governance, decision API, tenant-specific rule
  selection, SoD invariant, audit/security events — all Hard Mode MOM v3 trigger criteria.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Source | Evidence |
|---|---|
| `backend/app/repositories/approval_repository.py` | `_score_rule`: +8 for `tenant_id != "*"`. `get_rules_for_action` fetches `tenant_id.in_([tenant_id, "*"])` — other-tenant rules never fetched. "First non-empty level wins" → max score group → allowed_roles. |
| `backend/app/services/approval_service.py` | `decide_approval_request`: forwards governed context to `get_approver_role_codes`, emits `APPROVAL.{decision_value}`. |
| `backend/app/api/v1/approvals.py` | `LookupError→404`, `PermissionError→403`, `ValueError→400`. |
| `backend/app/models/approval.py` | `ApprovalRule` UniqueConstraint: `(action_type, approver_role_code, tenant_id)` — different role_codes can coexist for same action+tenant. |
| `docs/audit/p0-a-15f-approval-decision-specificity-api-coverage-report.md` | P0-A-15F confirmed all other specificity dimensions. Tenant-specific was the last remaining P0-A-14 §7 dimension to cover at API level. |
| `docs/audit/p0-a-15e-approval-decision-governed-context-api-coverage-report.md` | Established `_build_app` / `_override_action_dependency` pattern for dual-identity approval API tests. |

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
| Tenant-specific rule (score 8) beats wildcard (score 0) | `_score_rule` +8 for non-wildcard tenant; max score group selected | T-TENANT-API-01 |
| Tenant-specific beats multiple wildcards | All wildcard rules at score 0 are in lower group | T-TENANT-API-02 |
| Wildcard role forbidden when tenant-specific rule wins | Only max-score group in allowed_roles | T-TENANT-API-02b, T-TENANT-API-04 |
| Other-tenant rules not fetched | Query `tenant_id.in_([tenant_id, "*"])` excludes other tenants | T-TENANT-API-03 |
| Wildcard fallback valid when no tenant-specific rule | Score 0 wildcard still wins as sole candidate | T-TENANT-API-05 |
| Cross-tenant decision → 404 | `get_request_by_id` filters by tenant_id | T-TENANT-API-06 |
| SoD: requester cannot APPROVE own request | `requester_id == decider_user_id` → ValueError → 400 | T-TENANT-API-07 |
| SoD: requester cannot REJECT own request | Same invariant | T-TENANT-API-08 |
| Terminal request cannot be decided twice | `status != "PENDING"` → ValueError → 400 | T-TENANT-API-09 |
| SecurityEventLog taxonomy unchanged | APPROVED / REJECTED only; no new types | T-TENANT-API-10, T-TENANT-API-10b |
| APPROVAL.CANCELLED not introduced | No service function, no events | T-TENANT-API-11 |
| Governed action registry not enforced | Arbitrary governed_action_type string works | T-TENANT-API-12 |
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
| T-TENANT-API-01 | Tenant-specific rule (score 8) beats wildcard (score 0) | 200, QAL decides |
| T-TENANT-API-02 | Tenant-specific beats multiple wildcard rules | 200, QAL decides |
| T-TENANT-API-02b | Wildcard PMG role forbidden when tenant-specific QAL rule wins | 403 |
| T-TENANT-API-03 | Other-tenant rule not fetched → no rules for tenant-a → 400 | 400, "no approval rules" |
| T-TENANT-API-04 | Wildcard role (PMG) is 403 when tenant-specific QAL rule wins | 403 |
| T-TENANT-API-05 | Wildcard fallback when no tenant-specific rule | 200 |
| T-TENANT-API-06 | Cross-tenant decision → 404 (tenant isolation) | 404 |
| T-TENANT-API-07 | SoD: requester cannot APPROVE own request | 400, "requester" |
| T-TENANT-API-08 | SoD: requester cannot REJECT own request | 400, "requester" |
| T-TENANT-API-09 | Terminal request cannot be decided twice | 400, "not pending" |
| T-TENANT-API-10 | After APPROVED: exactly APPROVAL.APPROVED emitted | count=1 |
| T-TENANT-API-10b | After REJECTED: exactly APPROVAL.REJECTED emitted | count=1 |
| T-TENANT-API-11 | No APPROVAL.CANCELLED event or function | assert not hasattr |
| T-TENANT-API-12 | Arbitrary governed_action_type — no registry enforcement | 200 |

### Verdict

**`ALLOW_P0A16_APPROVAL_DECISION_API_TENANT_RULE_OVERRIDE_COVERAGE`**

---

## Selected Option

**Option A — API tenant-specific override tests only.**

The existing route, service, and repository already correctly implement tenant-specific
rule scoring (+8). No runtime patch required.

---

## Tenant-Specific Override Coverage Decision

The +8 score dimension from P0-A-14 §7 was confirmed end-to-end through the HTTP boundary:

- **T-TENANT-API-01/02**: QAL (score 8 via tenant-specific rule) can decide; PMG (score 0 via wildcard) cannot.
- **T-TENANT-API-03**: Other-tenant rules are excluded from the DB query — zero rules found for tenant-a → 400.
- **T-TENANT-API-04**: Confirms that the lower-score wildcard role is explicitly forbidden (403) when the tenant-specific rule exists for a different role.
- **T-TENANT-API-05**: Wildcard-only (score 0) setup still produces a valid decision when no tenant-specific rule exists.

All P0-A-14 §7 dimensions are now covered at the API level:

| Dimension | Score | Covered by |
|---|---|---|
| Tenant-specific rule | +8 | **P0-A-16 (this slice)** |
| Scope_ref match | +4 | P0-A-15F T-SPEC-API-01/02 |
| Governed resource type | +2 | P0-A-15F T-SPEC-API-03 |
| Governed action type present | +1 | P0-A-15F T-SPEC-API-03/04 |

---

## Wildcard Fallback Replay

- **T-TENANT-API-05**: No tenant-specific rule seeded → wildcard rule (score 0) is sole candidate → allowed_roles={QAL} → 200.
- Consistent with P0-A-15F T-SPEC-API-07 (pure legacy fallback behavior).

---

## SoD / Tenant Isolation Replay

- **T-TENANT-API-07/08**: `requester_id == decider_user_id` guard fires even under tenant-specific rules → 400.
- **T-TENANT-API-06**: `get_request_by_id(db, request_id, tenant_id)` returns `None` for cross-tenant → LookupError → 404. Consistent with P0-A-15E T-DEC-API-07.

---

## SecurityEventLog Replay

- **T-TENANT-API-10**: After APPROVED → exactly 1 `APPROVAL.APPROVED` event in `SecurityEventLog`.
- **T-TENANT-API-10b**: After REJECTED → exactly 1 `APPROVAL.REJECTED` event.
- **T-TENANT-API-11**: `APPROVAL.CANCELLED` event count = 0; `cancel_approval_request` function does not exist.
- No new event taxonomy introduced.

---

## Tests Added / Updated

### New file: `backend/tests/test_approval_decision_tenant_override_api.py`

14 tests covering T-TENANT-API-01 through T-TENANT-API-12 (with 2 negative variants).

### Updated files

- `.github/workflows/pr-gate.yml` — added `tests/test_approval_decision_tenant_override_api.py`
- `.github/workflows/backend-ci.yml` — added P0-A-16 step
- `backend/tests/test_pr_gate_workflow_config.py` — added `test_approval_decision_tenant_override_api_tests_are_in_pr_gate`

---

## Files Inspected

| File | Purpose |
|---|---|
| `backend/app/repositories/approval_repository.py` | Confirmed +8 tenant-specific scoring, `tenant_id.in_([tenant_id, "*"])` query |
| `backend/app/services/approval_service.py` | Confirmed SoD guard, governed context forwarding, SecurityEventLog emission |
| `backend/app/api/v1/approvals.py` | Confirmed error mapping |
| `backend/app/models/approval.py` | Confirmed UniqueConstraint `(action_type, approver_role_code, tenant_id)` |
| `backend/tests/test_approval_decision_specificity_api.py` | Extracted `_make_session`, `_rule`, `_seed`, `_build_app` helpers |
| `docs/audit/p0-a-15f-approval-decision-specificity-api-coverage-report.md` | Confirmed which P0-A-14 §7 dimensions remained uncovered |

---

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_approval_decision_tenant_override_api.py` | **New** — 14 tests (T-TENANT-API-01..T-TENANT-API-12 + 2 negative variants) |
| `.github/workflows/pr-gate.yml` | Added to explicit test list |
| `.github/workflows/backend-ci.yml` | Added P0-A-16 step |
| `backend/tests/test_pr_gate_workflow_config.py` | Added gate assertion |

No production source files modified.

### Unrelated workspace changes (not touched)

`backend/app/api/v1/products.py`, `backend/tests/test_reason_code_allowed_actions_13b.py`,
`backend/tests/test_scope_rbac_foundation_alignment.py`, `frontend/src/app/components/Layout.tsx`,
`frontend/src/app/components/TopBar.tsx` (deleted), `frontend/src/app/components/index.ts`,
`frontend/src/app/i18n/namespaces.ts`, `frontend/src/app/i18n/registry/en.ts`,
`frontend/src/app/i18n/registry/ja.ts`, `frontend/tsconfig.json`, `CLAUDE.md`,
`frontend/src/app/components/AppHeader.tsx` (new, FE team), `frontend/e2e/header-operational-context.spec.ts`,
`docs/audit/fe-header-01-*.md`, `docs/audit/fe-header-02-*.md`.

---

## Verification Commands Run

```
git status --short
cd backend
python -m pytest -q tests/test_approval_decision_tenant_override_api.py
python -m pytest -q tests/test_approval_decision_specificity_api.py tests/test_approval_decision_governed_context_api.py tests/test_approval_governed_context_api.py tests/test_approval_create_governed_context_bridge.py tests/test_approval_rule_scope_aware_matching.py tests/test_approval_service_current_behavior.py tests/test_approval_security_events.py tests/test_pr_gate_workflow_config.py tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_scope_rbac_foundation_alignment.py tests/test_qa_foundation_authorization.py
```

---

## Results

| Suite | Result |
|---|---|
| `test_approval_decision_tenant_override_api.py` (14 new) | **14 passed**, 1 warning (benign) |
| All approval + RBAC regression suites (12 files) | **153 passed**, 1 warning |

Total: **167 passed**, 0 failures, 0 errors. Benign warning: `conftest.py UserWarning: Running tests against a DB that does not look test-specific` — expected.

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

None identified. All tests use isolated in-memory SQLite sessions. `ApprovalRule`
UniqueConstraint `(action_type, approver_role_code, tenant_id)` respected in all fixtures.

---

## Recommended Next Slice

**P0-A-17** (suggested): Combine all four P0-A-14 §7 scoring dimensions into a single
"full precedence cascade" API test — one request where tenant-specific + scope + resource_type
+ governed_action_type all match, asserting that only the maximally-specific role can decide.
This would be a final integration proof that all four dimensions compose correctly end-to-end.

Alternatively: **P0-A-18** — approval rule lifecycle (soft-delete `is_active=False` prevents
match; reactivation restores eligibility) at the API level.

---

## Stop Conditions Hit

None. All stop conditions were clear.

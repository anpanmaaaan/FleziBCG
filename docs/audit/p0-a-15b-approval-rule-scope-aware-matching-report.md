# P0-A-15B Report — ApprovalRule Scope-Aware Matching Runtime Activation

| Field    | Value                                                                   |
|----------|-------------------------------------------------------------------------|
| Slice    | P0-A-15B                                                                |
| Date     | 2026-05-04                                                              |
| Author   | AI Brain (Hard Mode MOM v3)                                             |
| Status   | CLOSED — SCOPE-AWARE MATCHING ACTIVATED                                 |
| Depends  | P0-A-15A (schema), P0-A-15A-01 (closeout), P0-A-14 (contract)          |

---

## Summary

P0-A-15B activates scope-aware ApprovalRule matching at runtime using the nullable schema fields added in P0-A-15A (migration `0012`).

**Selected Option: A — Repository-level scope-aware matching only.**

A scoring algorithm was implemented in `approval_repository.py` using specificity scoring per P0-A-14 §7. The service passes governed resource context (already present on `ApprovalRequest` from P0-A-13) to the repository at decision time. All new parameters are keyword-only with `default=None`, preserving full backward compatibility.

| Metric | Value |
|--------|-------|
| New test file | `test_approval_rule_scope_aware_matching.py` — 12 tests (T-SA-01..T-SA-12) |
| Tests passing (scope + full regression) | **117 passed, 1 warning** |
| Migration added | **0** |
| MMD files changed | **0** |
| API/schema added | **0** |
| Alembic head | `0012` — unchanged |

---

## Routing

| Field          | Value                                                                                     |
|----------------|-------------------------------------------------------------------------------------------|
| Selected brain | MOM Brain                                                                                 |
| Selected mode  | QA + Strict + Backend Implementation                                                      |
| Hard Mode MOM  | v3                                                                                        |
| Reason         | Approval governance, ApprovalRule runtime matching, tenant/scope authorization, governed resource identity, SoD correctness, critical authorization invariant |

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Source | Finding |
|--------|---------|
| P0-A-14 §7 | Precedence: L1=tenant+scope+grt+gat, L2=tenant+scope+gat, L3=tenant+grt+gat, L4=tenant+gat, L5=tenant+action_type, L6=wildcard+action_type. "First non-empty level wins." |
| P0-A-14 §8 | Rule with `scope_ref=NULL` matches any scope; rule with `governed_action_type=NULL` matches any. Non-null field that doesn't match → NOT a candidate. |
| P0-A-14 §11 | Existing rules without scope fields MUST continue matching (additive backward compat). |
| `approval_repository.py` (before) | `get_rules_for_action` filtered `action_type + is_active + tenant_id IN [tenant, "*"]`. No scope logic. |
| `approval_service.py` `decide_approval_request` | Already had `appr_req` with `governed_resource_scope_ref`, `governed_resource_type`, `governed_action_type` from P0-A-13 (nullable). Just needed to pass them to `get_approver_role_codes`. |
| P0-A-15A-01 closeout | Migration `0012` head confirmed; all 12 schema tests passing. |

### Event Map

No new events. Unchanged:
- `APPROVAL.REQUESTED` — emitted in `create_approval_request`
- `APPROVAL.APPROVED` / `APPROVAL.REJECTED` — emitted in `decide_approval_request`
- `APPROVAL.CANCELLED` — remains unimplemented

### Invariant Map

| Invariant | Evidence | Test |
|-----------|---------|------|
| Legacy `tenant + action_type` matching valid | `_score_rule` only excludes incompatible non-null fields; NULL fields never exclude | T-SA-01 |
| Wildcard `"*"` fallback valid | Query fetches `tenant_id IN [tenant, "*"]`; wildcard scores 0 < tenant-specific 8 | T-SA-02 |
| Scope-specific beats legacy when context exists | score(8+4=12) > score(8) | T-SA-03 |
| Most specific rule wins | score(8+4+2+1=15) > score(12) > score(8) | T-SA-04 |
| Governed rule beats legacy | score(8+2+1=11) > score(8) | T-SA-05 |
| Wrong scope excludes scope-specific rule | `scope_ref mismatch → _score_rule returns None` | T-SA-06 |
| Wrong grt excludes governed rule | `grt mismatch → _score_rule returns None` | T-SA-07 |
| Tenant isolation enforced | Base query: `tenant_id IN [tenant, "*"]` | T-SA-08 |
| Priority deterministic | Sort `key=priority ASC, None last` | T-SA-09 |
| Service backward compat | `appr_req.governed_*` are NULL for legacy requests → legacy path | T-SA-10 |
| No governed action registry enforcement | No registry check in repo or service | T-SA-11 |
| `VALID_ACTION_TYPES` unchanged, no CANCELLED path | frozenset 6 values; Pydantic rejects CANCELLED decision | T-SA-12 |
| No migration/schema change | `alembic heads` still `0012` | alembic check |
| No MMD files changed | Scope: only approval repo/service/tests | git status |

### State Transition Map

Unchanged: `PENDING → APPROVED`, `PENDING → REJECTED`. `CANCELLED` schema-only, no service path.

### Runtime Matching Decision

**Option A — Repository-level scope-aware matching only.** Selected because:
- `decide_approval_request` already retrieves `appr_req` which has governed context from P0-A-13
- No API/schema change needed to activate matching at decision time
- All new kwargs are keyword-only defaults — full backward compat
- API bridge to populate governed context at creation time is deferred to P0-A-15C

### Verdict

> **ALLOW_P0A15B_APPROVAL_RULE_SCOPE_AWARE_MATCHING**

---

## Selected Option

**Option A — Repository-level scope-aware matching only.**

`approval_repository.get_rules_for_action` now accepts optional keyword-only parameters:
- `scope_ref: str | None = None`
- `governed_resource_type: str | None = None`
- `governed_action_type: str | None = None`

`approval_service.decide_approval_request` passes context from `appr_req` (available since P0-A-13):
```python
allowed_roles = get_approver_role_codes(
    db,
    appr_req.action_type,
    tenant_id,
    scope_ref=appr_req.governed_resource_scope_ref,
    governed_resource_type=appr_req.governed_resource_type,
    governed_action_type=appr_req.governed_action_type,
)
```

Since these governed fields are NULL for all existing requests (nothing sets them yet), the legacy fallback is always taken in production. The matching logic IS active; the API bridge to pass context is deferred to P0-A-15C.

---

## Matching Precedence Implementation

### Algorithm

File: `backend/app/repositories/approval_repository.py`

**Step 1 — Fetch:** All active rules for the tenant (specific + wildcard):
```sql
WHERE is_active = TRUE AND tenant_id IN (tenant_id, '*')
```

**Step 2 — Action routing:**
- If `rule.governed_action_type IS NOT NULL` → governed rule: must match request's `governed_action_type` (or exclude)
- If `rule.governed_action_type IS NULL` → legacy rule: must match request's `action_type` (or exclude)

**Step 3 — Specificity scoring via `_score_rule`:**

| Condition | Score |
|-----------|-------|
| `rule.tenant_id != "*"` | +8 |
| `rule.scope_ref IS NOT NULL AND matches` | +4 |
| `rule.governed_resource_type IS NOT NULL AND matches` | +2 |
| `rule.governed_action_type IS NOT NULL` (present after routing) | +1 |
| `rule.scope_ref IS NOT NULL AND does NOT match` | → `None` (excluded) |
| `rule.governed_resource_type IS NOT NULL AND does NOT match` | → `None` (excluded) |

**Step 4 — Winner selection:**
- Find `max_score` among scored rules
- Return all rules at `max_score`, sorted by `priority ASC` (`None` sorts last)

### Precedence Levels (per P0-A-14 §7)

| Score | Equivalent Precedence Level | Example |
|-------|---------------------------|---------|
| 8+4+2+1 = 15 | L1: tenant + scope + grt + gat | Most specific |
| 8+4+0+1 = 13 | L2: tenant + scope + gat (no grt constraint on rule) | Scope + governed action |
| 8+0+2+1 = 11 | L3: tenant + grt + gat (no scope constraint on rule) | Resource + action |
| 8+0+0+1 = 9 | L4: tenant + gat only | Governed action only |
| 8+0+0+0 = 8 | L5: tenant + action_type (legacy) | Legacy tenant-specific |
| 0+0+0+0 = 0 | L6: wildcard + action_type (legacy) | Global fallback |

---

## Backward Compatibility Decision

| Change | Backward Compatible? | Reason |
|--------|---------------------|--------|
| `get_rules_for_action` new kwargs | ✅ Yes | Keyword-only, all default=None |
| `get_approver_role_codes` new kwargs | ✅ Yes | Keyword-only, all default=None |
| Service passes context from `appr_req` | ✅ Yes | Fields NULL for all existing requests → legacy path taken |
| `test_no_scope_aware_matching_implemented` updated | ✅ Yes | Provisional negative test updated to reflect P0-A-15B active state |
| All 12 P0-A-15A schema tests still pass | ✅ Yes | No schema/model change |
| All 17 `test_approval_service_current_behavior.py` tests pass | ✅ Yes | Service logic unchanged for legacy requests |

---

## Tests Added / Updated

### New file: `backend/tests/test_approval_rule_scope_aware_matching.py`

| Test ID | Test Name | Result |
|---------|-----------|--------|
| T-SA-01 | `test_tsa01_legacy_tenant_action_type_rule_matches_without_scope_context` | ✅ PASS |
| T-SA-02 | `test_tsa02_wildcard_fallback_matches_when_no_tenant_specific_rule` | ✅ PASS |
| T-SA-03 | `test_tsa03_scope_specific_rule_beats_legacy_when_scope_ref_provided` | ✅ PASS |
| T-SA-04 | `test_tsa04_most_specific_rule_wins_over_less_specific` | ✅ PASS |
| T-SA-05 | `test_tsa05_governed_resource_action_rule_beats_legacy_without_scope` | ✅ PASS |
| T-SA-06 | `test_tsa06_wrong_scope_excludes_scope_rule_falls_back_to_legacy` | ✅ PASS |
| T-SA-07 | `test_tsa07_wrong_governed_resource_excludes_governed_rule_falls_back` | ✅ PASS |
| T-SA-08 | `test_tsa08_matching_is_tenant_isolated` | ✅ PASS |
| T-SA-09 | `test_tsa09_priority_tie_breaking_is_deterministic` | ✅ PASS |
| T-SA-10 | `test_tsa10_legacy_approval_request_decision_behavior_remains_compatible` | ✅ PASS |
| T-SA-11 | `test_tsa11_no_governed_action_registry_enforcement` | ✅ PASS |
| T-SA-12 | `test_tsa12_no_approval_cancelled_path_introduced` | ✅ PASS |

### Updated: `backend/tests/test_approval_rule_scope_applicability_schema.py`

| Test | Before | After |
|------|--------|-------|
| `test_no_scope_aware_matching_implemented` | Asserted scope_ref NOT in matching logic (P0-A-15A negative test) | Renamed to `test_scope_aware_matching_is_activated`; now asserts scope_ref IS in matching logic (P0-A-15B) |

### Updated: `backend/tests/test_pr_gate_workflow_config.py`

| Test added | Guard |
|-----------|-------|
| `test_approval_rule_scope_aware_matching_tests_are_in_pr_gate` | P0-A-15B: asserts `test_approval_rule_scope_aware_matching.py` in `pr-gate.yml` |

---

## Files Inspected

| File | Purpose |
|------|---------|
| `docs/design/01_foundation/approval-rule-scope-applicability-contract.md` | §7 precedence, §8 fallback rules, §11 backward compat |
| `docs/audit/p0-a-15a-01-approval-rule-scope-schema-closeout-report.md` | P0-A-15A baseline verification |
| `backend/app/models/approval.py` | `ApprovalRule` (7 scope fields from 0012), `ApprovalRequest` (governed fields from 0011) |
| `backend/app/schemas/approval.py` | `ApprovalCreateRequest` (no governed fields — context gap deferred to P0-A-15C) |
| `backend/app/repositories/approval_repository.py` | Pre-change baseline — simple `action_type + tenant_id` filter |
| `backend/app/services/approval_service.py` | `decide_approval_request` — `appr_req` available with governed context |
| `backend/tests/test_approval_service_current_behavior.py` | Fixture patterns for in-memory SQLite sessions |
| `backend/tests/test_approval_rule_scope_applicability_schema.py` | P0-A-15A baseline tests including provisional negative test |
| `.github/workflows/pr-gate.yml` | Added `test_approval_rule_scope_aware_matching.py` |
| `.github/workflows/backend-ci.yml` | Added P0-A-15B step |
| `backend/tests/test_pr_gate_workflow_config.py` | Added P0-A-15B guard |

---

## Files Changed

| File | Change |
|------|--------|
| `backend/app/repositories/approval_repository.py` | Added `_score_rule` helper; updated `get_rules_for_action` with scoring algorithm and optional scope kwargs; updated `get_approver_role_codes` to accept and pass scope kwargs |
| `backend/app/services/approval_service.py` | `decide_approval_request` now passes `appr_req.governed_resource_scope_ref`, `governed_resource_type`, `governed_action_type` to `get_approver_role_codes` |
| `backend/tests/test_approval_rule_scope_aware_matching.py` | Created — T-SA-01 through T-SA-12 |
| `backend/tests/test_approval_rule_scope_applicability_schema.py` | Updated provisional negative test to reflect P0-A-15B active state |
| `backend/tests/test_pr_gate_workflow_config.py` | Added `test_approval_rule_scope_aware_matching_tests_are_in_pr_gate` |
| `.github/workflows/pr-gate.yml` | Added `tests/test_approval_rule_scope_aware_matching.py` |
| `.github/workflows/backend-ci.yml` | Added P0-A-15B step for `test_approval_rule_scope_aware_matching.py` |
| `docs/audit/p0-a-15b-approval-rule-scope-aware-matching-report.md` | Created — this report |

**Not changed:**
- `backend/app/models/approval.py` — no model change
- `backend/app/schemas/approval.py` — no schema change
- `backend/alembic/versions/` — no migration
- Any MMD source/tests/docs — untouched
- `VALID_ACTION_TYPES` — unchanged

---

## Verification Commands Run

| Command | Result |
|---------|--------|
| `git status --short` | M on approval_repository.py, approval_service.py, ci/gate files; `??` new test file; pre-existing unrelated M files from other teams | PASS |
| `alembic heads` | `0012 (head)` — unchanged | PASS |
| `pytest test_approval_rule_scope_aware_matching.py` | 12 passed | PASS |
| `pytest test_approval_rule_scope_applicability_schema.py test_approval_service_current_behavior.py test_approval_governed_resource_identity_schema.py test_approval_security_events.py test_pr_gate_workflow_config.py test_rbac_action_registry_alignment.py test_rbac_seed_alignment.py test_scope_rbac_foundation_alignment.py test_qa_foundation_authorization.py` | 105 passed | PASS |
| `pytest test_alembic_baseline.py test_qa_foundation_migration_smoke.py test_init_db_bootstrap_guard.py` | 14 passed, 3 skipped | PASS_WITH_SKIPS (live DB — expected) |
| **Total** | **131 passed, 3 skipped, 0 failed** | **✅ ALL GREEN** |

---

## Results

| Suite | Tests | Status |
|-------|-------|--------|
| New scope-aware matching tests (T-SA-01..T-SA-12) | 12 | ✅ PASSED |
| Full regression (approval + RBAC + scope + auth + gate) | 105 | ✅ PASSED |
| Migration + bootstrap | 14 + 3 skip | ✅ PASSED |
| **Total** | **131 + 3 skip** | **✅ ALL PASSED** |

---

## Scope Compliance

| Requirement | Status |
|-------------|--------|
| No migration added | ✅ `0012` still the only head |
| No ApprovalRule schema field changes | ✅ No model changes |
| No `VALID_ACTION_TYPES` changes | ✅ Unchanged |
| No governed action type registry enforcement | ✅ Not implemented |
| No APPROVAL.CANCELLED path | ✅ Not added |
| No API endpoints added | ✅ |
| No frontend/Admin UI added | ✅ |
| No MMD source/tests/docs modified | ✅ |
| No ACTION_CODE_REGISTRY changes | ✅ |
| No route guard changes | ✅ |
| Existing tests all pass | ✅ |
| Wildcard fallback preserved | ✅ T-SA-02 |
| Legacy tenant+action_type preserved | ✅ T-SA-01 |

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Governed context in `appr_req` is NULL until P0-A-15C bridge — scope-aware rules effectively inactive in production | Low (expected; logic proven by tests) | P0-A-15C will add optional governed fields to `ApprovalCreateRequest` |
| Scoring relies on Python-side filtering after a broad tenant query — may return more rows than needed for large rule tables | Low (approval rules are few per tenant) | Future: add DB-level index on `(tenant_id, governed_action_type, scope_ref)` per P0-A-14 §12 |
| `effective_from`/`effective_to` not yet enforced | Low | Fields exist; time-window matching deferred to future slice |
| Two rules at the same max-score level contribute BOTH their role codes (no single-winner enforcement) | Low | Matches current legacy behavior; explicit single-winner logic deferred |

---

## Recommended Next Slice

**P0-A-15C — ApprovalCreateRequest Governed Context Bridge**

Enable callers to populate governed context at request creation time:
1. Add optional fields to `ApprovalCreateRequest`:
   - `governed_resource_type: str | None = None`
   - `governed_resource_id: str | None = None`
   - `governed_resource_scope_ref: str | None = None`
   - `governed_resource_display_ref: str | None = None`
   - `governed_resource_tenant_id: str | None = None`
   - `governed_action_type: str | None = None`
2. Update `create_approval_request` to store them on `ApprovalRequest`
3. Scope-aware matching then takes effect end-to-end for qualified requests
4. Hard Mode MOM v3 mandatory

---

## Stop Conditions Hit

None.

| Condition | Result |
|-----------|--------|
| Repository/service cannot support optional matching context safely | ❌ Not triggered — Option A feasible |
| Implementation requires schema/migration change | ❌ Not triggered — no migration needed |
| Implementation requires MMD integration | ❌ Not triggered |
| Legacy wildcard behavior would break | ❌ Not triggered — T-SA-02 passes |
| Matching precedence cannot be deterministic | ❌ Not triggered — scoring algorithm is deterministic |
| Tests require broad API redesign | ❌ Not triggered — repository tests sufficient |

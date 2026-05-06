# P0-A-17B Report — Approval Decision Same-Score Deferred Specificity Completion

## Summary

P0-A-17 deferred three API tests that required P0-A-15A scope fields and P0-A-15B scoring.
Those prerequisites are present on `autocode` (confirmed by POST-MERGE-VERIFY-01).
This slice completed the three deferred tests with zero runtime changes.

- Branch: `autocode`
- Selected Option: **Option A — Complete deferred tests only**
- Tests added: 5 (T-TIE-API-02a, 02b, 03a, 03b, 05)
- Total T-TIE suite after this slice: **15 tests, 15/15 passing**
- Full governance regression: **183 passed, 1 warning** (SQLite in-memory, live DB skip expected)
- No runtime code changed. No migrations added. No MMD files touched.

---

## Routing

- **Selected brain:** MOM Brain (FleziBCG AI Brain v6 Auto-Execution)
- **Selected mode:** Strict (governance-invariant test completion)
- **Hard Mode MOM:** v3 ON
- **Reason:** Task touches approval governance, approval decision API, same-score rule behavior,
  scope-aware matching, wildcard fallback, tenant/scope/auth, SoD invariant,
  SecurityEventLog taxonomy, critical authorization invariants.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source |
|---|---|
| Branch: `autocode`, HEAD `0fdda61f` | `git branch --show-current` |
| P0-A-15A scope fields on `ApprovalRule` | `app/models/approval.py` — `scope_ref`, `governed_resource_type`, `governed_action_type`, `priority` all nullable |
| `_score_rule` scoring: +8/+4/+2/+1 | `approval_repository.py` |
| "First non-empty level wins" | `approval_repository.py` `get_rules_for_action` — max_score group |
| Incompatibility rules | `_score_rule` — non-null non-matching field → `None` |
| Request governed context → scorer | `approval_service.py` — `scope_ref=appr_req.governed_resource_scope_ref`, `governed_resource_type=appr_req.governed_resource_type` |
| `governed_resource_scope_ref` in schema | `ApprovalCreateRequest.governed_resource_scope_ref` |
| Existing same-score tests passing | 10/15 in `test_approval_decision_same_score_api.py` before this slice |
| T-TIE-API-02/03/05 deferred marker removed | Stale SCOPE NOTE updated in file |

### Event Map

No new event types introduced.

| Event | Status |
|---|---|
| `APPROVAL.REQUESTED` | Unchanged |
| `APPROVAL.APPROVED` | Unchanged |
| `APPROVAL.REJECTED` | Unchanged |
| `APPROVAL.CANCELLED` | Unimplemented — unchanged |

### Invariant Map

| Invariant | Evidence | Tested by |
|---|---|---|
| All roles in max-score group allowed | `max_score` group → `allowed_roles` union | T-TIE-API-02a/b, 03a/b |
| Roles outside max-score group rejected | Only max-score rules form `allowed_roles` | T-TIE-API-05 |
| Lower-score wildcard rejected when higher-score group exists | WRK score=0 < QAL/PMG score=8 → max group wins | T-TIE-API-05 |
| SoD: requester ≠ decider | `approval_service.py` guard | T-TIE-API-09, 10 |
| Tenant isolation | `get_request_by_id` filters by `tenant_id` | T-TIE-API-07 |
| SecurityEventLog taxonomy unchanged | No new event types | T-TIE-API-11, 12 |
| No migration/model/service/API route change | Test-only slice | Scope check |

### State Transition Map

No lifecycle change.

```
PENDING → APPROVED  (terminal)
PENDING → REJECTED  (terminal)
CANCELLED — schema-only, no service path
```

### Test Matrix

| Test ID | Description | Status |
|---|---|---|
| T-TIE-API-01a | Two wildcard rules — QAL accepted | Pre-existing ✓ |
| T-TIE-API-01b | Two wildcard rules — PMG accepted | Pre-existing ✓ |
| **T-TIE-API-02a** | Scope-specific tie (score=12) — QAL accepted | **NEW ✓** |
| **T-TIE-API-02b** | Scope-specific tie (score=12) — PMG accepted | **NEW ✓** |
| **T-TIE-API-03a** | Governed resource tie (score=10) — QAL accepted | **NEW ✓** |
| **T-TIE-API-03b** | Governed resource tie (score=10) — PMG accepted | **NEW ✓** |
| T-TIE-API-04 | Role with no rule → 403 | Pre-existing ✓ |
| **T-TIE-API-05** | Lower-score wildcard rejected by higher-score group | **NEW ✓** |
| T-TIE-API-06 | Repeated fresh requests stable | Pre-existing ✓ |
| T-TIE-API-07 | Tenant isolation | Pre-existing ✓ |
| T-TIE-API-08 | Terminal re-decide guard | Pre-existing ✓ |
| T-TIE-API-09 | SoD APPROVE | Pre-existing ✓ |
| T-TIE-API-10 | SoD REJECT | Pre-existing ✓ |
| T-TIE-API-11 | SecurityEventLog taxonomy | Pre-existing ✓ |
| T-TIE-API-12 | No APPROVAL.CANCELLED path | Pre-existing ✓ |

### Verdict

**`ALLOW_P0A17B_SAME_SCORE_DEFERRED_SPECIFICITY_COMPLETION`**

---

## Selected Option

**Option A — Complete deferred tests only.**

All prerequisites present on `autocode`. Test additions require no runtime changes.

---

## Deferred Tests Completed

| Test | Defer reason (P0-A-17) | Resolution (P0-A-17B) |
|---|---|---|
| T-TIE-API-02 | `scope_ref` not on `ApprovalRule` (P0-A-15A not merged) | P0-A-15A present on `autocode`. Added T-TIE-API-02a/b. |
| T-TIE-API-03 | `governed_resource_type` not on `ApprovalRule` (P0-A-15A not merged) | P0-A-15A present on `autocode`. Added T-TIE-API-03a/b. |
| T-TIE-API-05 | Scoring system (`_score_rule`) not present (P0-A-15B not merged) | P0-A-15B present on `autocode`. Added T-TIE-API-05. |

---

## Same-Score Specificity Replay

### T-TIE-API-02 — Scope-Specific Tie

**Setup:**
```
Rule 1: (QC_HOLD, QAL, tenant-a, scope_ref="plant:LINE-1") → score = 8 + 4 = 12
Rule 2: (QC_HOLD, PMG, tenant-a, scope_ref="plant:LINE-1") → score = 8 + 4 = 12
Request: governed_resource_scope_ref="plant:LINE-1"
```

**Scoring path:**
- `_score_rule(rule, scope_ref="plant:LINE-1", governed_resource_type=None)`
- Both rules: `tenant_id != "*"` → +8; `rule.scope_ref == "plant:LINE-1"` → +4. Total = 12.
- `max_score = 12`. `best_rules = [QAL, PMG]`. `allowed_roles = {QAL, PMG}`.

**Result:** T-TIE-API-02a (QAL) → 200 ✓. T-TIE-API-02b (PMG) → 200 ✓.

### T-TIE-API-03 — Governed Resource Tie

**Setup:**
```
Rule 1: (QC_HOLD, QAL, tenant-a, governed_resource_type="WORK_ORDER") → score = 8 + 2 = 10
Rule 2: (QC_HOLD, PMG, tenant-a, governed_resource_type="WORK_ORDER") → score = 8 + 2 = 10
Request: governed_resource_type="WORK_ORDER"
```

**Scoring path:**
- Both rules: `tenant_id != "*"` → +8; `rule.governed_resource_type == "WORK_ORDER"` → +2. Total = 10.
- `max_score = 10`. `best_rules = [QAL, PMG]`. `allowed_roles = {QAL, PMG}`.

**Result:** T-TIE-API-03a (QAL) → 200 ✓. T-TIE-API-03b (PMG) → 200 ✓.

---

## Wildcard Lower-Score Rejection Replay

### T-TIE-API-05 — Lower-Score Wildcard Rejected

**Setup:**
```
Rule 1: (QC_HOLD, QAL, tenant-a) → score = 8   ← max group
Rule 2: (QC_HOLD, PMG, tenant-a) → score = 8   ← max group
Rule 3: (QC_HOLD, WRK, "*")      → score = 0   ← excluded
Request: no scope/governed context (legacy request)
```

**Scoring path:**
- QAL/PMG: `tenant_id == "tenant-a" != "*"` → +8. Total = 8.
- WRK: `tenant_id == "*"` → +0. Total = 0.
- `max_score = 8`. WRK's rule (score=0) is below max → excluded from best_rules.
- `allowed_roles = {QAL, PMG}`. WRK not in allowed_roles → `PermissionError` → 403.

**Result:** T-TIE-API-05 (WRK decider) → 403 ✓.

---

## SoD / Tenant Isolation Replay

Pre-existing tests — confirmed green:

- T-TIE-API-07: Tenant-b decider cannot access tenant-a request → 404 ✓
- T-TIE-API-09: Same-user APPROVE own request → 400 "requester" ✓
- T-TIE-API-10: Same-user REJECT own request → 400 "requester" ✓

---

## SecurityEventLog Replay

Pre-existing tests — confirmed green:

- T-TIE-API-11: After APPROVED decision, exactly one `APPROVAL.APPROVED` event, no `APPROVAL.CANCELLED` ✓
- T-TIE-API-12: `cancel_approval_request` not on service module; no `APPROVAL.CANCELLED` event after full lifecycle ✓

---

## Tests Added / Updated

**File:** `backend/tests/test_approval_decision_same_score_api.py`

| Change | Detail |
|---|---|
| Module docstring SCOPE NOTE updated | "T-TIE-API-02/03/05 completed in P0-A-17B" replaces stale defer statement |
| `_rule` helper signature updated | Added `scope_ref`, `governed_resource_type`, `governed_action_type`, `priority` params (matching P0-A-15A fields). Stale "NOT on current model" comment removed. |
| `_scope_payload` helper added | Builds request payload with `governed_resource_scope_ref` for scope-rule tests |
| `_governed_resource_payload` helper added | Builds request payload with `governed_resource_type` for governed-resource-rule tests |
| `test_ttieapi02a_scope_specific_tie_qal_accepted` added | T-TIE-API-02a |
| `test_ttieapi02b_scope_specific_tie_pmg_accepted` added | T-TIE-API-02b |
| `test_ttieapi03a_governed_resource_tie_qal_accepted` added | T-TIE-API-03a |
| `test_ttieapi03b_governed_resource_tie_pmg_accepted` added | T-TIE-API-03b |
| `test_ttieapi05_lower_score_wildcard_rejected_when_higher_score_group_exists` added | T-TIE-API-05 |
| `# [T-TIE-API-02 and T-TIE-API-03 deferred ...]` comment removed | No longer deferred |

**Test count before:** 10  
**Test count after:** 15

---

## Files Inspected

- `backend/app/models/approval.py`
- `backend/app/repositories/approval_repository.py`
- `backend/app/services/approval_service.py`
- `backend/app/schemas/approval.py`
- `backend/tests/test_approval_decision_same_score_api.py`
- `backend/tests/test_approval_decision_specificity_api.py`
- `backend/tests/test_approval_decision_tenant_override_api.py`
- `backend/tests/test_approval_decision_governed_context_api.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`
- `docs/audit/post-merge-verify-01-autocode-baseline-report.md` (via session context)

---

## Files Changed

| File | Change type |
|---|---|
| `backend/tests/test_approval_decision_same_score_api.py` | Tests added, helpers updated, stale docstring updated |

**No other files changed.** No migrations, no models, no schemas, no service, no API routes, no MMD files, no workflow files.

---

## Verification Commands Run

```powershell
# Branch / git state
git branch --show-current          # → autocode
git status --short                 # → M tests/test_product_version_foundation_api.py (unrelated)

# Pre-change baseline
$env:DATABASE_URL="postgresql+psycopg://x:x@127.0.0.1:9991/x"
cd backend
pytest -q test_approval_decision_same_score_api.py test_approval_decision_specificity_api.py test_approval_decision_tenant_override_api.py
# → 43 passed, 1 warning

# New T-TIE suite
pytest -v test_approval_decision_same_score_api.py
# → 15 passed, 1 warning in 3.79s

# Full governance regression
pytest -q [14 approval+RBAC+gate files]
# → 183 passed, 1 warning in 8.55s
```

---

## Results

| Category | Result |
|---|---|
| Branch | `autocode` ✓ |
| P0-A-15A scope fields on `ApprovalRule` | Confirmed present ✓ |
| P0-A-15B scoring in `approval_repository.py` | Confirmed present ✓ |
| T-TIE-API-02a | ✓ pass |
| T-TIE-API-02b | ✓ pass |
| T-TIE-API-03a | ✓ pass |
| T-TIE-API-03b | ✓ pass |
| T-TIE-API-05 | ✓ pass |
| Full T-TIE suite (15/15) | ✓ |
| P0-A-15F specificity API tests | ✓ pass |
| P0-A-16 tenant override API tests | ✓ pass |
| Approval current behavior | ✓ pass |
| Approval SecurityEventLog | ✓ pass |
| RBAC registry + seed | ✓ pass |
| Scope RBAC foundation | ✓ pass |
| QA authorization | ✓ pass |
| CI/PR gate coverage | Already covered — no workflow change needed ✓ |
| No runtime code changed | ✓ |
| No migration added | ✓ |
| No MMD files touched | ✓ |

**Overall verdict: PASS — P0-A-17B complete.**

---

## Scope Compliance

| Constraint | Status |
|---|---|
| No migrations added | ✓ |
| `ApprovalRequest` model fields unchanged | ✓ |
| `ApprovalRule` schema fields unchanged | ✓ |
| Repository matching precedence unchanged | ✓ |
| Approval service decision logic unchanged | ✓ |
| Approval API route logic unchanged | ✓ |
| Governed action registry not implemented | ✓ |
| `governed_action_type` not globally enforced | ✓ |
| `VALID_ACTION_TYPES` unchanged | ✓ |
| `APPROVAL.CANCELLED` not implemented | ✓ |
| No new approval endpoints | ✓ |
| No frontend changes | ✓ |
| No Admin UI changes | ✓ |
| No MMD source/tests/docs modified | ✓ |
| No route guards changed | ✓ |
| `ACTION_CODE_REGISTRY` unchanged | ✓ |
| No auth tests weakened | ✓ |
| Unrelated modified file (`test_product_version_foundation_api.py`) not touched | ✓ |

---

## Risks

| Risk | Severity | Notes |
|---|---|---|
| `test_product_version_foundation_api.py` modified but unstaged | INFO | Unrelated to this slice. Not touched. |
| T-TIE-API-02/03 use `governed_resource_scope_ref` only (no `governed_action_type`) | INFO | Scope is complete for same-score group coverage; governed_action_type dimension tested separately in P0-A-15F |

---

## Recommended Next Slice

**P0-A-18** — Governed action type enforcement: validate `governed_action_type` against a registry when rules specify it. Currently `governed_action_type` on rules provides +1 scoring but no registry enforcement. The `VALID_ACTION_TYPES` set does not include governed_action_type values. A slice to enforce the governed action type namespace would close this gap.

Alternatively, continue with the next roadmap slice per `docs/roadmap/`.

---

## Stop Conditions Hit

None.

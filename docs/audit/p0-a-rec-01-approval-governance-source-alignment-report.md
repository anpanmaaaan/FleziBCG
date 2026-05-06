# P0-A-REC-01 Report — Approval Governance Source Alignment / Alembic Chain Triage

## Summary

P0-A-REC-01 is a **source audit / triage task**. It establishes ground truth for
the approval governance codebase on the `enhance-design-system` branch, reconciles
inaccurate claims carried forward in a previous session summary, and assesses the
health of the Alembic migration chain.

**Key findings:**

1. **Session summary was inaccurate in two ways:**
   - Claimed P0-A-15A through P0-A-16 were implemented on disk — **FALSE** on the
     current branch (`enhance-design-system`). Those commits exist only on the
     `autocode` branch.
   - Claimed `0013_product_version_bom_bindings.py` had `down_revision = "0012"` —
     **FALSE** on `enhance-design-system`. It has `down_revision = "0011"`. The
     Alembic chain is **NOT broken** on this branch.

2. **The `autocode` branch is ahead** with P0-A-14 through P0-A-16A commits
   including: scope fields on `ApprovalRule` (migration 0012), `_score_rule`
   scoring system, and tests T-TIE-02, 03, 05 coverage.

3. **Current working tree** (`enhance-design-system`) has 4 uncommitted
   P0-A-17 artefacts plus untracked `.github/agents/`, `.github/instructions/`,
   `.github/prompts/` directories (likely VS Code Copilot customizations, not P0-A work).

4. **All 43 approval tests pass** (SQLite in-memory; no live DB required on this branch).

5. **PR gate and backend-ci.yml** are modified (staged) to include `test_approval_decision_same_score_api.py`.

6. **Selected Option: Option A** — report-only. P0-A-17 partial changes are safe and
   consistent. No unsafe uncommitted files detected. Recommend committing P0-A-17 artefacts.

---

## Routing

- **Selected brain:** MOM Brain (FleziBCG AI Brain v6 Auto-Execution)
- **Selected mode:** Debug/Triage (source audit / evidence mode)
- **Hard Mode MOM:** v3 ON
- **Reason:** Touches approval governance baseline truth, Alembic migration truth,
  CI/PR gate truth, source/report contradiction, tenant/scope/auth foundation,
  critical authorization invariant.

---

## Selected Option

**Option A: Report-only.**

P0-A-17 uncommitted artefacts are safe, self-consistent, and all tests pass.
Recommend committing them. No unsafe/broken state detected on `enhance-design-system`.

---

## Source / Report Contradiction Summary

| Claim (prior session summary) | Actual disk state | Verdict |
|---|---|---|
| Alembic chain broken: `0013.down_revision = "0012"`, no `0012.py` | `0013.down_revision = "0011"`, chain is healthy (head = `0013`) | **INACCURATE** |
| P0-A-15A scope fields on `ApprovalRule` implemented | `ApprovalRule` has no `scope_ref`, `governed_resource_type`, `governed_action_type`, `priority` on `enhance-design-system` | **INACCURATE for this branch** — fields exist on `autocode` |
| P0-A-15B `_score_rule` scoring in repository | `approval_repository.py` has no `_score_rule`; 3-param `get_rules_for_action` only | **INACCURATE for this branch** — scoring exists on `autocode` |
| P0-A-15C through P0-A-16A test files on disk | None of those 6 test files exist on `enhance-design-system` | **INACCURATE for this branch** — files exist on `autocode` |
| Broken chain required DATABASE_URL workaround for all tests | Chain healthy; SQLite in-memory tests run without workaround (DATABASE_URL workaround still valid for other purposes) | **INACCURATE — no broken chain** |

---

## Git State

| Property | Value |
|---|---|
| Current branch | `enhance-design-system` |
| HEAD commit | `4f3c7a92` — `feat(mmd): add BOM Product Version binding API` |
| Remote up-to-date | Yes — `Your branch is up to date with 'origin/enhance-design-system'` |
| Merge base with `main` | `0bad61ad` |
| Merge base with `autocode` | `0bad61ad` |

### Uncommitted changes (from `git status --short`, relative to repo root)

| File | Status | Source |
|---|---|---|
| `.github/workflows/backend-ci.yml` | Modified (staged) | P0-A-17 |
| `.github/workflows/pr-gate.yml` | Modified (staged) | P0-A-17 |
| `backend/tests/test_pr_gate_workflow_config.py` | Modified (staged) | P0-A-17 |
| `backend/tests/test_mmd_rbac_action_codes.py` | Modified (staged) | MMD-related |
| `.github/agents/` | Untracked | VS Code Copilot customization |
| `.github/instructions/` | Untracked | VS Code Copilot customization |
| `.github/prompts/` | Untracked | VS Code Copilot customization |
| `backend/tests/test_approval_decision_same_score_api.py` | Untracked | P0-A-17 |
| `docs/audit/mmd-be-14a-bom-product-version-binding-boundary-release-validation.md` | Untracked | MMD |
| `docs/audit/p0-a-17-approval-decision-same-score-api-coverage-report.md` | Untracked | P0-A-17 |

### Branches of interest

| Branch | Last P0-A commit |
|---|---|
| `enhance-design-system` (HEAD) | P0-A-13A (committed) + P0-A-17 artefacts (uncommitted) |
| `autocode` | P0-A-16A (committed) — includes P0-A-14 through P0-A-16A |
| `main` | P0-A-13A (via merge from enhance-design-system) |

### P0-A commits on `autocode` not on `enhance-design-system`

```
P0-A-14     define approval rule scope applicability contract
P0-A-REG-02 align reason code action registry governance
P0-A-15A    add approval rule scope applicability schema
P0-A-15A-01 close approval rule scope schema baseline
P0-A-15B    activate approval rule scope-aware matching
P0-A-15B-01 close approval rule scope-aware matching baseline
P0-A-15C    bridge approval create governed context
P0-A-15D    add approval governed context API coverage
P0-A-15E    add approval decision governed context API coverage
P0-A-15F    add approval decision specificity API coverage
P0-A-16     add approval decision tenant override API coverage
P0-A-16A    close approval decision specificity API baseline
```

---

## Actual Approval Source State (enhance-design-system, on disk)

### `backend/app/models/approval.py`

**`ApprovalRule` columns:** `id`, `action_type`, `approver_role_code`, `tenant_id`,
`is_active`, `created_at`

- **NO** scope fields: `scope_ref`, `governed_resource_type`, `governed_action_type`,
  `scope_type`, `priority`, `effective_from`, `effective_to` absent.
- `UniqueConstraint: (action_type, approver_role_code, tenant_id)`

**`ApprovalRequest` columns:** `id`, `tenant_id`, `action_type`, `requester_id`,
`requester_role_code`, `subject_type`, `subject_ref`,
`governed_resource_type`, `governed_resource_id`, `governed_resource_display_ref`,
`governed_resource_tenant_id`, `governed_resource_scope_ref`, `governed_action_type`,
`reason`, `status`, `created_at`, `updated_at`

- P0-A-13 governed resource identity fields: **PRESENT**.

**`ApprovalDecision` columns:** includes `impersonation_session_id` FK.

### `backend/app/repositories/approval_repository.py`

- `get_rules_for_action(db, action_type, tenant_id)` — **3 params only, no scope context**.
- `get_approver_role_codes(db, action_type, tenant_id)` — 3 params.
- No `_score_rule` function. No scope-aware matching.

### `backend/app/services/approval_service.py`

- Calls `get_approver_role_codes(db, appr_req.action_type, tenant_id)` — 3 params.
- SoD guard: `requester_id == decider_user_id → ValueError → 400`.
- Terminal state guard: `status != "PENDING" → ValueError → 400`.
- Emits `APPROVAL.APPROVED` / `APPROVAL.REJECTED` security events.
- No `APPROVAL.CANCELLED` path.

### `backend/app/schemas/approval.py`

- `ApprovalRuleResponse` has: `id`, `action_type`, `approver_role_code`, `tenant_id`,
  `is_active`, `created_at`. **No scope fields**.
- `ApprovalRequestResponse` includes governed resource identity fields (P0-A-13).
- `ApprovalCreateRequest`: `action_type`, `subject_type`, `subject_ref`, `reason`.
  **No governed context fields in create schema.**

### `backend/app/api/v1/approvals.py`

- Routes: `POST /approvals` (create), `GET /approvals/pending`, `POST /approvals/{id}/decide`.
- Error mapping: `LookupError→404, PermissionError→403, ValueError→400`.
- No scope-aware parameters in any route.

---

## Actual Alembic State

| Migration | Filename | `down_revision` | Status |
|---|---|---|---|
| 0001 | `0001_baseline.py` | None | ✓ |
| 0002 | `0002_add_refresh_tokens.py` | `0001` | ✓ |
| 0003 | `0003_routing_operation_extended_fields.py` | `0002` | ✓ |
| 0004 | `0004_add_user_lifecycle_status.py` | `0003` | ✓ |
| 0005 | `0005_add_plant_hierarchy.py` | `0004` | ✓ |
| 0006 | `0006_add_tenant_lifecycle_anchor.py` | `0005` | ✓ |
| 0007 | `0007_product_versions.py` | `0006` | ✓ |
| 0008 | `0008_boms.py` | `0007` | ✓ |
| 0009 | `0009_drop_station_claims.py` | `0008` | ✓ |
| 0010 | `0010_reason_codes.py` | `0009` | ✓ |
| 0011 | `0011_add_governed_resource_identity_to_approvals.py` | `0010` | ✓ |
| 0012 | **ABSENT** | — | ⚠ Not on this branch (exists on `autocode`) |
| 0013 | `0013_product_version_bom_bindings.py` | `0011` | ✓ |

**Alembic chain:** Linear, single head `0013`. **HEALTHY** on `enhance-design-system`.

Alembic `heads` output: `0013 (head)` — confirmed.

> **Correction to P0-A-17 report:** The P0-A-17 report stated `0013.down_revision = "0012"`
> and the chain was broken. This was incorrect for the `enhance-design-system` branch.
> On `autocode`, P0-A-15A added migration 0012, and `0013` on that branch was modified
> to point to `0012`. On `enhance-design-system`, `0013.down_revision = "0011"`.
> **No Alembic chain repair needed on this branch.**

---

## Actual Test / CI Gate State

### Committed approval test files on `enhance-design-system`

| File | Status | Committed | P0-A slice |
|---|---|---|---|
| `test_approval_service_current_behavior.py` | ✓ Pass | Yes (P0-A-11A) | P0-A-11A |
| `test_approval_security_events.py` | ✓ Pass | Yes (P0-A-12) | P0-A-12 |
| `test_approval_governed_resource_identity_schema.py` | ✓ Pass | Yes (P0-A-13A) | P0-A-13A |
| `test_approval_decision_same_score_api.py` | ✓ Pass (10 tests) | **Untracked** | P0-A-17 |

### Approval test files that do NOT exist on this branch

| Claimed file | Claimed slice | Exists on disk? |
|---|---|---|
| `test_approval_rule_scope_applicability_schema.py` | P0-A-15A | No |
| `test_approval_rule_scope_aware_matching.py` | P0-A-15B | No |
| `test_approval_create_governed_context_bridge.py` | P0-A-15C | No |
| `test_approval_governed_context_api.py` | P0-A-15D | No |
| `test_approval_decision_governed_context_api.py` | P0-A-15E | No |
| `test_approval_decision_specificity_api.py` | P0-A-15F | No |
| `test_approval_decision_tenant_override_api.py` | P0-A-16 | No |

These files exist on the `autocode` branch as part of committed P0-A-15A through P0-A-16A work.

### PR gate (`pr-gate.yml`) — modified (uncommitted)

Adds `tests/test_approval_decision_same_score_api.py` to the backend test run list.
All existing approval tests confirmed present in pr-gate.yml.

### Backend CI (`backend-ci.yml`) — modified (uncommitted)

Adds a P0-A-17 step after P0-A-13 step.

### `test_pr_gate_workflow_config.py` — modified (uncommitted)

Adds assertion `test_approval_decision_same_score_api_tests_are_in_pr_gate`.

---

## Claimed Baseline vs Disk Matrix

| Claimed baseline | Expected artifact | On disk (`enhance-design-system`)? | On `autocode`? |
|---|---|---|---|
| P0-A-11A current behavior regression | `test_approval_service_current_behavior.py` | ✓ Yes (committed) | ✓ Yes |
| P0-A-12 security events | `test_approval_security_events.py` | ✓ Yes (committed) | ✓ Yes |
| P0-A-13 governed resource fields | `ApprovalRequest` governed_resource_* fields; migration 0011 | ✓ Yes (committed) | ✓ Yes |
| P0-A-13A schema baseline | `test_approval_governed_resource_identity_schema.py` | ✓ Yes (committed) | ✓ Yes |
| P0-A-14 scope applicability contract | Design doc only | Not checked | ✓ Yes (commit) |
| P0-A-15A scope fields | `ApprovalRule.scope_ref`, `.governed_resource_type`, `.governed_action_type`, `.priority`; migration 0012 | ✗ No | ✓ Yes (committed on autocode) |
| P0-A-15B scoring system | `_score_rule` in `approval_repository.py` | ✗ No | ✓ Yes (committed on autocode) |
| P0-A-15C bridge test | `test_approval_create_governed_context_bridge.py` | ✗ No | ✓ Yes |
| P0-A-15D create API tests | `test_approval_governed_context_api.py` | ✗ No | ✓ Yes |
| P0-A-15E decision API tests | `test_approval_decision_governed_context_api.py` | ✗ No | ✓ Yes |
| P0-A-15F specificity tests | `test_approval_decision_specificity_api.py` | ✗ No | ✓ Yes |
| P0-A-16 tenant override tests | `test_approval_decision_tenant_override_api.py` | ✗ No | ✓ Yes |
| P0-A-16A baseline close | commit on autocode | ✗ No | ✓ Yes |
| P0-A-17 same-score tests (10/12) | `test_approval_decision_same_score_api.py` | ✓ Yes (untracked) | Not present |
| Alembic 0012 | `0012_*.py` | ✗ No (not needed on this branch) | ✓ Yes (on autocode) |
| Alembic 0013 | `0013_product_version_bom_bindings.py` | ✓ Yes | ✓ Yes (modified) |

---

## P0-A-17 Partial Change Classification

| File | Classification | Recommendation |
|---|---|---|
| `backend/tests/test_approval_decision_same_score_api.py` | Untracked, 10 tests passing | **KEEP — commit** |
| `.github/workflows/pr-gate.yml` | Modified (staged), adds same_score test | **KEEP — commit** |
| `.github/workflows/backend-ci.yml` | Modified (staged), adds P0-A-17 step | **KEEP — commit** |
| `backend/tests/test_pr_gate_workflow_config.py` | Modified (staged), adds P0-A-17 assertion | **KEEP — commit** |
| `docs/audit/p0-a-17-approval-decision-same-score-api-coverage-report.md` | Untracked, reference doc | **KEEP — commit** |

No file should be reverted. All P0-A-17 artefacts are safe, tested, and self-consistent.

**Note on Alembic DATABASE_URL workaround in P0-A-17 report:** The P0-A-17 report's
documentation of the `DATABASE_URL=postgresql+psycopg://x:x@127.0.0.1:9991/x`
workaround was written under the incorrect belief that the chain was broken. On
`enhance-design-system`, no such workaround is needed for the Alembic chain — the
chain is healthy and `alembic heads` returns `0013 (head)`. The DATABASE_URL
environment variable is still useful for bypassing the live Postgres dependency
during local SQLite in-memory test runs; this is unchanged behavior.

---

## Verification Commands Run

```powershell
# Alembic chain
cd G:\Work\FleziBCG\backend
g:/Work/FleziBCG/.venv/Scripts/python.exe -m alembic heads
# → 0013 (head) — single linear head, chain healthy

# Approval test suite (43 tests)
$env:DATABASE_URL = "postgresql+psycopg://x:x@127.0.0.1:9991/x"
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q \
  tests/test_approval_service_current_behavior.py \
  tests/test_approval_security_events.py \
  tests/test_approval_governed_resource_identity_schema.py \
  tests/test_approval_decision_same_score_api.py --tb=short
# → 43 passed, 1 warning

# PR gate + RBAC alignment (56 tests)
g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q \
  tests/test_pr_gate_workflow_config.py \
  tests/test_rbac_action_registry_alignment.py \
  tests/test_rbac_seed_alignment.py \
  tests/test_scope_rbac_foundation_alignment.py --tb=short
# → 56 passed, 1 warning
```

---

## Scope Compliance

| Constraint | Status |
|---|---|
| Did NOT implement P0-A-15A/B | ✓ Compliant |
| Did NOT repair Alembic migrations | ✓ Compliant (no repair needed) |
| Did NOT edit `0013_product_version_bom_bindings.py` | ✓ Compliant |
| Did NOT modify approval runtime (model/schema/repository/service/API) | ✓ Compliant |
| Did NOT modify MMD source/tests | ✓ Compliant |
| Report-only unless Option B needed | ✓ Option A selected |

---

## Severity Findings

| Finding | Severity | Impact |
|---|---|---|
| Session summary inaccuracy: P0-A-15A–16 claimed as implemented on disk | HIGH | Led to incorrect workarounds in P0-A-17 (DATABASE_URL hack, deferred test framing) |
| Session summary inaccuracy: broken Alembic chain claimed | MEDIUM | DATABASE_URL workaround was documented as mandatory; it is not |
| P0-A-14 through P0-A-16A work exists only on `autocode` branch | HIGH | 12 commits not merged to `enhance-design-system` or `main` |
| P0-A-17 artefacts uncommitted | LOW | Safe to commit; all tests pass |
| `test_mmd_rbac_action_codes.py` modified (staged) | INFO | Not P0-A scope; MMD-related; not examined in this report |

---

## Recovery Recommendation

### Immediate (in-scope for P0-A-REC-01)

1. **Commit P0-A-17 artefacts** on `enhance-design-system`:
   - `backend/tests/test_approval_decision_same_score_api.py` (new file)
   - `.github/workflows/pr-gate.yml` (modified)
   - `.github/workflows/backend-ci.yml` (modified)
   - `backend/tests/test_pr_gate_workflow_config.py` (modified)
   - `docs/audit/p0-a-17-approval-decision-same-score-api-coverage-report.md` (new file)
   - This report (`docs/audit/p0-a-rec-01-approval-governance-source-alignment-report.md`)

2. **Update P0-A-17 report** to correct the Alembic chain claim (0013→0011, not broken).

### Next slice decision

The `autocode` branch contains P0-A-14 through P0-A-16A (scope fields, scoring
system, API coverage). Two paths forward:

**Option X — Cherry-pick / merge `autocode` P0-A work into `enhance-design-system`:**
- Prerequisite: confirm `autocode` tests pass on that branch
- Risk: merge conflicts with MMD changes on `enhance-design-system`
- Benefit: brings full scope-aware matching, unblocks T-TIE-API-02/03/05

**Option Y — Implement P0-A-14 through P0-A-15B fresh on `enhance-design-system`:**
- Cleaner if `autocode` divergence is too large
- Requires: design doc review, migration 0012 creation (scope fields on ApprovalRule),
  `_score_rule` in repository, schema update, 3 deferred P0-A-17 tests
- Unblocks T-TIE-API-02, 03, 05

**Recommended:** Evaluate `autocode` branch divergence before choosing. If
cherry-pick is clean, Option X is lower effort. If conflicts are deep, Option Y.

---

## Recommended Next Slice

**P0-A-15A** — Add scope applicability fields to `ApprovalRule` model + migration 0012
(either via `autocode` cherry-pick or fresh implementation on `enhance-design-system`).
This is the prerequisite for P0-A-15B, P0-A-17 deferred tests, and the full
governance-aware decision path.

---

## Stop Conditions Hit

| Condition | Details |
|---|---|
| Source/report contradiction confirmed | P0-A-15A–16 not on current branch; Alembic chain not broken |
| Option A selected: report-only | P0-A-17 artefacts are safe; no unsafe changes detected |
| Scope boundary respected | No runtime edits; no migration edits; no MMD edits |

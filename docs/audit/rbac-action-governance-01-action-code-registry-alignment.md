# RBAC-ACTION-GOVERNANCE-01 — Action Code Registry / MMD RBAC Alignment Isolation

**Audit Report · Hard Mode MOM v3 Verified**
**Task ID:** RBAC-ACTION-GOVERNANCE-01
**Date:** 2026-05-04
**Auditor:** AI Brain MOM v3 Auto-Execution
**Status:** COMPLETE — COMMITTED

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** QA / Strict + Source audit / evidence mode
- **Hard Mode MOM:** v3 ON
- **Reason:** Touches RBAC/action code governance, authorization action registry alignment, MMD action codes, critical permission invariant (role/action/scope assignment trigger in `has_action()`)

---

## Summary

The RBAC-ACTION-GOVERNANCE-01 slice validates the addition of `admin.master_data.reason_code.manage`
to `ACTION_CODE_REGISTRY` in `backend/app/security/rbac.py`, its corresponding entry in
`docs/design/02_registry/action-code-registry.md`, and 7 new regression tests in
`backend/tests/test_mmd_rbac_action_codes.py`.

All three governance files were **committed at `44756c4fe`** (commit message:
`fix(mmd): add Reason Code manage action code`) prior to this audit. The working tree diff
for all three files is empty — the `M` status in the initial git status was due to CRLF
line endings in the Windows working copy.

**Verdict:** Governance contract is valid. 77 focused RBAC tests pass. Ruff is green.
The slice is clean and complete.

---

## Working Tree Classification

| File | Category | Notes |
|------|----------|-------|
| `backend/app/security/rbac.py` | RBAC/action governance — **COMMITTED** | `44756c4fe`; CRLF-only diff, no content change |
| `backend/tests/test_mmd_rbac_action_codes.py` | RBAC/action governance — **COMMITTED** | `44756c4fe`; CRLF-only diff, no content change |
| `docs/design/02_registry/action-code-registry.md` | RBAC/action governance — **COMMITTED** | `44756c4fe`; CRLF-only diff, no content change |
| `docs/audit/mmd-be-10a-reason-code-action-code-registry-patch.md` | RBAC audit doc — **COMMITTED** | `44756c4fe`; 185-line audit report for implementation slice |
| `backend/app/models/approval.py` | Approval schema slice — **COMMITTED** | `29595575e` (P0-A-15A), separate slice |
| `backend/app/schemas/approval.py` | Approval schema slice — **COMMITTED** | `29595575e` (P0-A-15A), separate slice |
| `backend/tests/test_alembic_baseline.py` | Approval schema slice — **COMMITTED** | `29595575e` (P0-A-15A) |
| `backend/tests/test_pr_gate_workflow_config.py` | Approval schema slice — **COMMITTED** | `29595575e` (P0-A-15A) |
| `.github/workflows/backend-ci.yml` | CI config — **COMMITTED** | `29595575e` (P0-A-15A) |
| `.github/workflows/pr-gate.yml` | CI config — **COMMITTED** | `29595575e` (P0-A-15A) |
| `frontend/tsconfig.json` | Unrelated frontend — CRLF dirty | Not in this slice; CRLF only |
| `CLAUDE.md` | Human-owned note — UNTRACKED | Not in scope; do not stage |
| `backend/bom_baseline_pytest_output.txt` | Generated artifact — UNTRACKED | Do not stage |
| `backend/bom_foundation_api_output_utf8.txt` | Generated artifact — UNTRACKED | Do not stage |

**Result:** No unstaged governance files remain. Working tree residual = 1 CRLF file + 1 note + 2 artifacts.

---

## Design Evidence Extract

| Source | Relevant Fact |
|--------|---------------|
| `docs/design/02_domain/product_definition/reason-code-write-governance-contract.md` §13 | Backend Implementation Readiness Gate: `admin.master_data.reason_code.manage` must be registered by MMD-BE-10A before write routes (MMD-BE-13) can be built |
| `docs/audit/mmd-be-10-reason-code-write-governance-contract.md` §6 | Authorization/Action-Code Decisions: action code absent at time of contract; MMD-BE-10A must add it |
| `docs/design/02_registry/action-code-registry.md` §Governance Rules | Rule 4: adding new action code requires (a) `rbac.py` entry, (b) registry doc entry, (c) regression test — all three satisfied |
| `backend/app/api/v1/reason_codes.py` | Only `GET /reason-codes` and `GET /reason-codes/{id}` exist; both use `require_authenticated_identity`; no write routes yet |
| `backend/app/security/rbac.py` L63 | `"admin.master_data.reason_code.manage": "ADMIN"` added after BOM entry, before config section |

---

## Invariant Map

| Invariant | Status | Evidence |
|-----------|--------|----------|
| Backend is source of permission truth | ✓ UPHELD | `has_action()` in `rbac.py` is the server-side check; no FE change; no persona logic |
| Persona is NOT permission | ✓ UPHELD | No role-family or persona mapping changes; ADMIN family assignment is explicit |
| JWT proves identity only | ✓ UPHELD | `ACTION_CODE_REGISTRY` is static Python dict; no JWT claim used to derive action |
| Action registry must not drift from seeded/allowed backend actions | ✓ UPHELD | `test_rbac_action_registry_alignment.py` passes (20 tests); `test_rbac_seed_alignment.py` passes (20 tests) |
| MMD action codes must be explicit and auditable | ✓ UPHELD | New code `admin.master_data.reason_code.manage` follows `admin.master_data.<entity>.manage` naming convention; covered by 7 new tests |
| No frontend or shell screen can invent allowed actions | ✓ UPHELD | `reason_codes.py` API uses `require_authenticated_identity` for reads; no write routes exist; no FE change |
| No tenant/scope/auth semantics weakened | ✓ UPHELD | ADMIN family retained; `SCOPE_TYPE_*` constants unchanged; `FORBIDDEN_ACTING_ROLES` unchanged |

---

## Action Code Governance Decision

### New Action Code: `admin.master_data.reason_code.manage`

| Property | Value |
|----------|-------|
| Code | `admin.master_data.reason_code.manage` |
| Family | `ADMIN` |
| Domain | Manufacturing Master Data (MMD) |
| Classification | Forward-declared authorization contract |
| Purpose | Govern future Reason Code write routes (MMD-BE-13) |
| Status | Registered in `rbac.py`; registered in `action-code-registry.md`; tested |
| Write API exists | NO — deferred to MMD-BE-13 |
| Read routes affected | NO — GET routes already use `require_authenticated_identity` (unchanged) |
| DB change | NONE |
| Seed data change | NONE |
| Role assignment change | NONE |

**Decision:** Action code is correctly scoped to ADMIN family. It is domain-specific (not shared with IAM `admin.user.manage`). Naming convention `admin.master_data.<entity>.manage` is consistent. No production behavior change — the code is only used when a route calls `require_action()`, which no Reason Code route does yet.

---

## Changes Made

All changes were committed at `44756c4fe` before this audit ran.

| File | Change | Lines |
|------|--------|-------|
| `backend/app/security/rbac.py` | Added `"admin.master_data.reason_code.manage": "ADMIN"` | +1 |
| `backend/tests/test_mmd_rbac_action_codes.py` | Added 7 MMD-BE-10A regression tests | +103 |
| `docs/design/02_registry/action-code-registry.md` | Added `admin.master_data.reason_code.manage` row to MMD table | +1 |
| `docs/audit/mmd-be-10a-reason-code-action-code-registry-patch.md` | Implementation audit doc | +185 |

---

## Files Changed (This Slice)

- [backend/app/security/rbac.py](../../backend/app/security/rbac.py) — COMMITTED
- [backend/tests/test_mmd_rbac_action_codes.py](../../backend/tests/test_mmd_rbac_action_codes.py) — COMMITTED
- [docs/design/02_registry/action-code-registry.md](../02_registry/action-code-registry.md) — COMMITTED
- [docs/audit/mmd-be-10a-reason-code-action-code-registry-patch.md](mmd-be-10a-reason-code-action-code-registry-patch.md) — COMMITTED

---

## Verification Results

### Focused RBAC / Action Code Tests

```
tests/test_mmd_rbac_action_codes.py   31 passed
tests/test_rbac_action_registry_alignment.py  20 passed
tests/test_rbac_seed_alignment.py     20 passed
tests/test_rbac_configure_family_boundary.py   6 passed
─────────────────────────────────────────────
TOTAL: 77 passed  0 failed  exit code 0
```

### Ruff Lint Check

```
ruff check .  →  All checks passed!  exit code 0
```

### Git Status (Post-Audit)

```
 M frontend/tsconfig.json   ← CRLF only, not in scope
?? CLAUDE.md               ← human-owned note, not in scope
?? backend/bom_baseline_pytest_output.txt   ← generated artifact
?? backend/bom_foundation_api_output_utf8.txt  ← generated artifact
```

All 4 RBAC governance files: **committed, no unstaged changes**.

---

## Scope Compliance

| Constraint | Status |
|------------|--------|
| No ruff format applied | ✓ CONFIRMED — only `ruff check .` was run |
| No frontend changed | ✓ CONFIRMED — `frontend/tsconfig.json` CRLF-only, not touched in this slice |
| No production behavior changed outside action-code alignment | ✓ CONFIRMED — no write routes exist; code is forward-declared; no runtime dispatch changed |
| No auth/tenant/scope semantics weakened | ✓ CONFIRMED — ADMIN family retained; `has_action()` logic unchanged |
| No unrelated artifact staged | ✓ CONFIRMED — `CLAUDE.md`, `bom_*.txt`, `frontend/tsconfig.json` excluded |
| No DB migration | ✓ CONFIRMED — static Python dict change only |
| No broad RBAC refactor | ✓ CONFIRMED — one dict entry added |

---

## BACKEND-QA-BASELINE-03 Readiness

| Condition | Status |
|-----------|--------|
| RBAC governance files committed | ✓ `44756c4fe` |
| Approval schema slice committed | ✓ `29595575e` |
| Ruff lint green | ✓ |
| RBAC/MMD tests green (77 passed) | ✓ |
| Working tree residual | 1 CRLF file + 1 note + 2 artifacts — none block BASELINE-03 |

**BACKEND-QA-BASELINE-03 is not blocked by this slice.**

Remaining residual before BASELINE-03:
1. `frontend/tsconfig.json` — CRLF only; can be committed or left (not backend)
2. `CLAUDE.md` — untracked note; leave as-is or commit separately
3. `backend/bom_*.txt` — generated artifacts; should be gitignored or deleted
4. `backend/run_tests.py` — not visible in current status (may have been resolved); verify if present

---

## Recommended Next Slice

**BACKEND-QA-ARTIFACTS-01** — Classify and purge remaining non-code working tree residuals before BACKEND-QA-BASELINE-03:
- Add `backend/*.txt` / `backend/bom_*.txt` to `.gitignore` (or delete)
- Decide `CLAUDE.md` fate (commit or add to `.gitignore`)
- Verify `frontend/tsconfig.json` CRLF: `git diff frontend/tsconfig.json` content must be zero; can be committed as CRLF normalization

Then: **BACKEND-QA-BASELINE-03** — `python -m ruff format .` mechanical baseline.

---

## Suggested Commit Commands

The RBAC governance files are **already committed**. No additional commit is needed for this slice.

To commit this audit report:
```bash
git add docs/audit/rbac-action-governance-01-action-code-registry-alignment.md
git commit -m "docs(qa): RBAC-ACTION-GOVERNANCE-01 action code registry alignment audit"
```

To commit the remaining audit docs from prior slices (if not yet committed):
```bash
# Verify which audit docs are untracked first:
git status --short docs/audit/

# Then selectively add verified audit docs:
git add docs/audit/rbac-action-governance-01-action-code-registry-alignment.md
git commit -m "docs(qa): RBAC-ACTION-GOVERNANCE-01 action code registry alignment audit"
```

**Do NOT stage:** `frontend/tsconfig.json`, `CLAUDE.md`, `backend/bom_*.txt`

# BACKEND-QA-LINT-CLEANUP-02 Report

## Routing
- Selected brain: MOM Brain
- Selected mode: QA / contract hardening mode + source audit/evidence mode
- Hard Mode MOM: ON (v3)
- Reason: Slice validates lint and isolation while repository currently contains governance-adjacent approval/RBAC changes; v3 evidence gate applied before any edits.

## Hard Mode MOM v3 Gate

### Verdict before coding
ALLOW_IMPLEMENTATION

### Design Evidence Extract

| Source doc | Why used | Evidence used |
|---|---|---|
| `docs/governance/CODING_RULES.md` | Mechanical-only scope and verification gates | Lint cleanup must be non-behavioral and isolated |
| `docs/governance/ENGINEERING_DECISIONS.md` | Backend truth and governance boundaries | No permission/execution truth moved to frontend |
| `docs/governance/SOURCE_STRUCTURE.md` | File ownership boundaries | `backend/scripts` and `backend/tests` are valid cleanup targets |
| `docs/audit/p0-a-12c-approval-governed-resource-identity-isolation.md` | Previous blocker baseline | Identified remaining Ruff blockers from prior slice |
| `docs/audit/backend-qa-lint-cleanup-01-unrelated-ruff-findings.md` | Prior lint-cleanup methodology | Confirmed mechanical import/variable cleanup pattern |
| `docs/audit/backend-qa-baseline-02-ruff-lint-gate.md` | CI lint gate expectations | `ruff check .` must be green for unblock |
| `backend/ruff.toml` | Active rule-set and per-file ignores | Select = `E4,E7,E9,F`; no blanket suppressions |
| `backend/scripts/verify_backend.py` | Required post-fix verification | `--testenv-only` includes import/lint/db/testenv checks |

### Invariant Map

| Invariant | Category | Enforcement |
|---|---|---|
| No production behavior change for this slice | auditability | Only lint-only code edits allowed |
| No auth/tenant/scope weakening | authorization | No service/security logic edited |
| No ruff format baseline action in this slice | process | `ruff format` not executed |
| CI lint gate must stay strict | quality gate | `ruff check .` must pass globally |
| Unrelated artifacts must remain isolated | change hygiene | Classification table + separate commit guidance |

### Test Matrix

| Test ID | Scenario | Command | Expected | Result |
|---|---|---|---|---|
| LC2-T1 | Global Ruff audit | `python -m ruff check .` | Pass | Pass |
| LC2-T2 | BOM focused regression | `pytest -q tests/test_bom_allowed_actions_12b_a.py tests/test_bom_capability_guard_12b_a.py` | Pass | 10 passed |
| LC2-T3 | Backend testenv verification | `python scripts/verify_backend.py --testenv-only` | Pass | Pass |
| LC2-T4 | Non-destructive script smoke | `python scripts/audit_broken_ops.py --dry-run --skip-init-db` | Safe run | Pass (dry-run only) |

## Summary

Current global backend lint is already green. The previously reported Ruff blockers (`backend/scripts/audit_broken_ops.py`, `backend/tests/test_bom_allowed_actions_12b_a.py`, `backend/tests/test_bom_capability_guard_12b_a.py`) are now resolved and pass under current rule-set.

This slice therefore focuses on:
1. confirming no remaining Ruff findings,
2. verifying focused BOM tests and testenv gate,
3. classifying unrelated dirty artifacts/files for isolation before BACKEND-QA-BASELINE-03.

## Ruff Failure Audit

Command run:

```powershell
Push-Location "g:/Work/FleziBCG/backend"
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m ruff check .
Pop-Location
```

Result:

```text
All checks passed!
RUFF_EXIT_CODE=0
```

Exact current Ruff failures found: **none**.

Classification of originally reported findings:
- `backend/scripts/audit_broken_ops.py`: unused import issue resolved.
- `backend/tests/test_bom_allowed_actions_12b_a.py`: unused import + unused assignment resolved.
- `backend/tests/test_bom_capability_guard_12b_a.py`: unused imports resolved.

## Changes Made

No additional source edits were required in this slice.

Reason: by the time this audit ran, global Ruff was already green and focused BOM tests were passing.

## Files Changed

No files were modified by BACKEND-QA-LINT-CLEANUP-02 execution itself.

Current tracked dirty files (pre-existing to this slice) from `git status`:
- `backend/app/security/rbac.py`
- `backend/tests/test_mmd_rbac_action_codes.py`
- `docs/design/02_registry/action-code-registry.md`
- `frontend/tsconfig.json`

Current untracked files:
- `CLAUDE.md`
- `backend/bom_baseline_pytest_output.txt`
- `backend/bom_foundation_api_output_utf8.txt`
- `backend/run_tests.py`

## Focused Test Results

Command:

```powershell
Push-Location "g:/Work/FleziBCG/backend"
$env:PYTHONPATH='.'
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q tests/test_bom_allowed_actions_12b_a.py tests/test_bom_capability_guard_12b_a.py
Pop-Location
```

Result:
- `10 passed, 1 warning`
- Warning is existing DB test isolation warning from `tests/conftest.py`, not introduced by this slice.

## Artifact Classification

| File | Classification | Decision |
|---|---|---|
| `backend/app/security/rbac.py` | Backend domain/governance change | Keep and commit separately (not lint-cleanup-02) |
| `backend/tests/test_mmd_rbac_action_codes.py` | Backend test for governance/domain | Keep and commit separately (not lint-cleanup-02) |
| `docs/design/02_registry/action-code-registry.md` | Design/registry contract update | Keep and commit separately with related domain slice |
| `frontend/tsconfig.json` | Frontend unrelated change | Stash before BACKEND-QA-BASELINE-03 |
| `CLAUDE.md` | Repo note / unknown ownership | Unknown / needs human decision |
| `backend/bom_baseline_pytest_output.txt` | Generated/output artifact | Delete or archive outside git before baseline slice |
| `backend/bom_foundation_api_output_utf8.txt` | Generated/output artifact | Delete or archive outside git before baseline slice |
| `backend/run_tests.py` | Utility/WIP script, unrelated | Unknown / needs human decision (or commit separately if intentional) |

## Verification Results

### Global Ruff
- `python -m ruff check .` → PASS

### Focused BOM tests
- `python -m pytest -q tests/test_bom_allowed_actions_12b_a.py tests/test_bom_capability_guard_12b_a.py` → PASS (`10 passed`)

### verify_backend.py --testenv-only
- `python scripts/verify_backend.py --testenv-only` → PASS
  - Backend import: PASS
  - Ruff lint: PASS
  - DB connectivity: PASS
  - Testenv safety/connectivity: PASS

### audit_broken_ops safe smoke
- `python scripts/audit_broken_ops.py --dry-run --skip-init-db` → PASS (non-destructive dry-run)
- No cleanup executed; output confirms dry-run only.

## Scope Compliance
- No ruff format applied: **Confirmed**
- No frontend changed: **Confirmed** (frontend file was not edited)
- No production behavior changed: **Confirmed**
- No auth/tenant/scope semantics weakened: **Confirmed**
- No unrelated domain refactor: **Confirmed**

## BACKEND-QA-BASELINE-03 Readiness

Status: **Partially unblocked**.

Now satisfied:
- Global backend Ruff gate is green.
- Required focused BOM tests are green.
- `verify_backend.py --testenv-only` is green.

Remaining blockers:
1. Working tree still contains unrelated backend/design/frontend/output artifacts.
2. BACKEND-QA-BASELINE-03 requires a clean/isolated mechanical formatting surface.

## Recommended Next Slice

1. Isolate and commit/stash non-lint files first:
   - backend governance/RBAC files in one separate intentful slice,
   - frontend and generated artifacts out of backend baseline path.
2. Re-run precondition check for BACKEND-QA-BASELINE-03:
   - `git status --short` must show no unrelated backend dirty files.
3. Then execute BASELINE-03 mechanical `ruff format` workflow.

## Suggested Commit Commands

Do not commit automatically. Suggested commands:

### A) Commit non-lint backend governance slice separately (if intentional)

```bash
git add backend/app/security/rbac.py backend/tests/test_mmd_rbac_action_codes.py docs/design/02_registry/action-code-registry.md
git commit -m "feat(rbac): add action code governance alignment updates"
```

### B) Remove generated artifacts from working tree

```bash
rm backend/bom_baseline_pytest_output.txt backend/bom_foundation_api_output_utf8.txt
```

(Use PowerShell equivalent `Remove-Item` on Windows if needed.)

### C) Stash unrelated frontend and unknown files before BASELINE-03

```bash
git stash push -m "pre-baseline03-nonbackend-artifacts" -- frontend/tsconfig.json CLAUDE.md backend/run_tests.py
```

### D) Precondition re-check for BASELINE-03

```bash
git status --short
```

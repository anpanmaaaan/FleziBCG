# P0-A-REG-01 Report

## Summary

P0-A-REG-01 triages the BOM action code registry drift discovered during P0-A-11C validation and resolves it with a minimal non-MMD governance test/doc alignment.

The drift was: `admin.master_data.bom.manage` existed in the runtime `ACTION_CODE_REGISTRY` and in the canonical `action-code-registry.md` governance doc, but was absent from the expected canonical set used in `test_rbac_action_registry_alignment.py`.

Evidence confirmed this is **Option B**: the code was intentionally added by the MMD team under slice MMD-BE-09A as a prerequisite for the future BOM write API (MMD-BE-12). The only stale artifacts were the test expected set and a missing history row in the governance doc.

**Option B** was selected. No MMD runtime source was modified.

## Routing

- Selected brain: MOM Brain
- Selected mode: QA + Strict
- Hard Mode MOM: v3
- Reason: Task touches RBAC action registry truth, seed alignment, MMD governance boundary, CI/PR gate correctness, and critical authorization invariant.

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| `admin.master_data.bom.manage` in runtime registry | `backend/app/security/rbac.py` MMD block | Intentionally added with ADMIN family, under MMD-BE-09A slice |
| `admin.master_data.bom.manage` in governance doc | `docs/design/02_registry/action-code-registry.md` MMD table | Entry present: "Create, update, add/remove items, release, or retire a BOM (when write APIs are enabled by MMD-BE-12)" |
| MMD audit report fully documents the addition | `docs/audit/mmd-be-09a-bom-action-code-registry-patch.md` | Objective stated: "Register `admin.master_data.bom.manage` as a hard prerequisite for BOM write API (MMD-BE-12). No BOM write endpoints are created in this slice." Verification output: tests pass. |
| Test expected set was stale | `backend/tests/test_rbac_action_registry_alignment.py` `_EXPECTED_ADMIN_MMD_CODES` | Contained only 4 MMD codes; BOM code absent; failing test: `test_action_code_registry_contains_exactly_canonical_set` |
| Seed alignment tests are fully dynamic | `backend/tests/test_rbac_seed_alignment.py` | `_ADMIN_FAMILY_ACTION_CODES` and RP counts derived dynamically from `ACTION_CODE_REGISTRY`; no hardcoded values; no update needed |
| History table in governance doc was missing MMD-BE-09A row | `docs/design/02_registry/action-code-registry.md` history | No entry for MMD-BE-09A / BOM code addition |
| P0-A-11C identified the drift as unrelated to its docs-only slice | `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md` | "The failing RBAC registry regression came from unrelated existing runtime/doc drift and was not introduced by this slice." |

### Event Map

Governance test/doc alignment slice. No runtime events are emitted.

- No MMD service, model, route, or migration behavior is changed.
- No approval event taxonomy is changed.
- No execution state machine is changed.

### Invariant Map

| Invariant | Evidence | Decision |
|---|---|---|
| Runtime action registry and canonical governance tests must not drift silently. | Failing test confirms drift. | Fixed by adding BOM code to expected set. |
| Action codes must be intentionally governed. | MMD-BE-09A audit report fully documents intent and verification. | Code is intentional; drift is only in the test expected set and history doc. |
| MMD runtime work is owned by the active MMD team. | Task scope; `mmd-be-09a` report confirms ownership. | MMD runtime source untouched. |
| Non-MMD governance tests may be aligned when evidence is unambiguous. | Evidence is unambiguous — code in runtime AND doc AND audit report. | Option B is safe and appropriate. |
| No MMD source is changed in this slice. | Actual diff confirmed. | Verified. |

### State Transition Map

Not applicable. No runtime state transition is implemented. No BOM lifecycle or write behavior is changed.

### Test Matrix

| Test / Command | Before Fix | After Fix |
|---|---|---|
| `test_action_code_registry_contains_exactly_canonical_set` | FAILING — unexpected code `admin.master_data.bom.manage` | PASS |
| `test_rbac_seed_alignment.py` (all 20) | Already PASS — tests are dynamic | PASS |
| `test_approval_service_current_behavior.py` (17) | PASS — unaffected | PASS |
| `test_scope_rbac_foundation_alignment.py` (10) | PASS — unaffected | PASS |
| `test_qa_foundation_authorization.py` + `test_pr_gate_workflow_config.py` (6) | PASS — unaffected | PASS |

### Verdict before writing

`ALLOW_P0A_REG01_BOM_ACTION_REGISTRY_DRIFT_TRIAGE`

## Selected Option

**Option B — Minimal non-MMD registry test/doc alignment.**

Evidence was unambiguous:

1. `admin.master_data.bom.manage` is intentionally present in the runtime `ACTION_CODE_REGISTRY`.
2. The canonical `action-code-registry.md` governance doc also contains the entry.
3. `docs/audit/mmd-be-09a-bom-action-code-registry-patch.md` explicitly documents the slice that added it.
4. The only stale artifacts were the test expected set and a missing history row.

Changes were limited to governance tests and docs only. No MMD runtime source was modified.

## Drift Evidence Map

| Surface | State Before This Slice | State After This Slice |
|---|---|---|
| `backend/app/security/rbac.py ACTION_CODE_REGISTRY` | Contains `admin.master_data.bom.manage` (MMD-BE-09A) | Unchanged — no modification |
| `docs/design/02_registry/action-code-registry.md` table | Contains `admin.master_data.bom.manage` row | Unchanged — BOM row already present |
| `docs/design/02_registry/action-code-registry.md` history | Missing MMD-BE-09A entry | Added `MMD-BE-09A` history row |
| `backend/tests/test_rbac_action_registry_alignment.py _EXPECTED_ADMIN_MMD_CODES` | 4 codes — BOM absent | 5 codes — BOM added |
| `backend/tests/test_rbac_seed_alignment.py` | Fully dynamic — no change needed | Unchanged |

## Runtime Registry vs Canonical Registry

| Code | In `rbac.py` ACTION_CODE_REGISTRY | In `action-code-registry.md` | In test `_EXPECTED_ADMIN_MMD_CODES` (before) | In test (after) |
|---|:---:|:---:|:---:|:---:|
| `admin.master_data.product.manage` | ✅ | ✅ | ✅ | ✅ |
| `admin.master_data.product_version.manage` | ✅ | ✅ | ✅ | ✅ |
| `admin.master_data.routing.manage` | ✅ | ✅ | ✅ | ✅ |
| `admin.master_data.resource_requirement.manage` | ✅ | ✅ | ✅ | ✅ |
| `admin.master_data.bom.manage` | ✅ | ✅ | ❌ (stale) | ✅ (fixed) |

All three surfaces are now aligned.

## Test Failure Classification

| Test | Classification | Root Cause |
|---|---|---|
| `test_action_code_registry_contains_exactly_canonical_set` | Stale expected set | `_EXPECTED_ADMIN_MMD_CODES` was not updated when MMD-BE-09A added `admin.master_data.bom.manage` to the runtime registry |

This is a governance test/doc drift, not a runtime code error. The runtime and governance doc were already aligned.

## Ownership Decision

| Item | Owner | Decision |
|---|---|---|
| `admin.master_data.bom.manage` runtime code | MMD team (MMD-BE-09A) | Intentional — no action required on runtime source |
| `action-code-registry.md` BOM row | MMD team (MMD-BE-09A) | Already correct — no change required to row |
| `action-code-registry.md` history | P0-A-REG-01 (this slice) | Added missing MMD-BE-09A history entry |
| `test_rbac_action_registry_alignment.py` expected set | P0-A-REG-01 (this slice) | Added `admin.master_data.bom.manage` to `_EXPECTED_ADMIN_MMD_CODES` |
| `test_rbac_seed_alignment.py` | No change needed | Tests are already dynamic |

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md`
- `docs/audit/mmd-be-09a-bom-action-code-registry-patch.md`
- `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md`
- `docs/audit/p0-a-08-role-permission-db-seeding-alignment-report.md`
- `docs/design/02_registry/action-code-registry.md`
- `backend/app/security/rbac.py`
- `backend/tests/test_rbac_action_registry_alignment.py`
- `backend/tests/test_rbac_seed_alignment.py`

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_rbac_action_registry_alignment.py` | Added `admin.master_data.bom.manage` to `_EXPECTED_ADMIN_MMD_CODES` with attribution comment |
| `docs/design/02_registry/action-code-registry.md` | Added missing `MMD-BE-09A` history row |
| `docs/audit/p0-a-reg-01-bom-action-registry-drift-triage-report.md` | Created (this file) |

## Verification Commands Run

| Command | Result |
|---|---|
| `git status --short` | Confirmed workspace dirty with unrelated MMD/station/frontend changes; this slice changed only test and registry doc |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | `40 passed, 1 warning` |
| `cd backend; g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_approval_service_current_behavior.py tests/test_scope_rbac_foundation_alignment.py tests/test_qa_foundation_authorization.py tests/test_pr_gate_workflow_config.py` | `33 passed, 1 warning` |

## Results

| Check | Outcome |
|---|---|
| RBAC registry + seed alignment | `40 passed, 1 warning` |
| Approval current-behavior regression | `17 passed, 1 warning` |
| Scope foundation alignment | `10 passed, 1 warning` |
| Auth + PR gate regressions | `6 passed, 1 warning` |
| Recurring warning | Existing non-test-DB warning from `backend/tests/conftest.py` because `POSTGRES_DB=mes` |

**Total: 73 passed, 0 failed, 1 warning.**

The previously failing test `test_action_code_registry_contains_exactly_canonical_set` now passes.

## Scope Compliance

- No MMD runtime source was changed: no `bom_service.py`, `bom_repository.py`, `schemas/bom.py`, `api/v1/products.py`, or any MMD model/migration/route.
- No BOM write behavior was added.
- No migrations were added.
- No API endpoints were added.
- No frontend or Admin UI was changed.
- No approval contracts were changed.
- No route guards were changed.
- `ACTION_CODE_REGISTRY` in `rbac.py` was not changed.
- `seed_rbac_core()` was not changed.
- Unrelated workspace changes from other teams (station sessions, MMD BOM service/schema/repository, frontend) were not touched.

## Risks

1. If the MMD team subsequently removes `admin.master_data.bom.manage` from the runtime registry before MMD-BE-12 is implemented, this governance test fix must be reversed in the same slice.
2. The full governance validation pass was previously blocked by this drift. It is now green for the RBAC/registry/seed/approval/scope/auth surfaces.

## Recommended Next Slice

The governance foundation for the RBAC registry and seed alignment is now clean. The recommended next step depends on team priority:

- **If continuing P0-A-11C direction**: write the governed action registry shape and approval rule specificity precedence design note (deferred by P0-A-11C).
- **If confirming broader governance baseline**: run `test_mmd_rbac_action_codes.py` to verify the MMD team's BOM-specific tests (added in MMD-BE-09A) also still pass cleanly alongside the governance test alignment.

## Stop Conditions Hit

None.

# MMD-FULLSTACK-12B-B Patch Report

Date: May 3, 2026  
Slice: MMD-FULLSTACK-12B-B  
Status: PASS

## Routing
- Selected brain: docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- Selected mode: Hard Mode MOM v2 (test-harness alignment only; no governed runtime semantics changed)
- Hard Mode MOM: v2
- Reason: This slice only aligns backend test harness behavior with already-approved server-derived capability read projection and does not alter execution state, auth policy, or write invariants.

## Scope
- Goal: Fix failing BOM read API tests caused by capability lookup path (`has_action`) in minimal SQLite harnesses.
- Allowed changes: Test-harness alignment only.
- Out of scope: Runtime semantics, write authorization, API contract changes, DB migrations, frontend runtime behavior.

## Failure Diagnosis

| Category | Candidate | Verdict | Evidence |
|---|---|---|---|
| A | Test harness incomplete for RBAC lookup path | ROOT CAUSE | Failures show `OperationalError: no such table: user_role_assignments` while evaluating `has_action(...)` from BOM read endpoints in minimal SQLite test app builders. |
| B | Missing/incorrect route dependency override | Not root cause | Existing write-route tests already use dependency overrides; failures occur on read path capability lookup, not write route guard wiring. |
| C | Runtime authorization regression | Rejected | Runtime policy unchanged: writes still enforced by `require_action("admin.master_data.bom.manage")`; read remains authenticated with additive capability projection. |
| D | Data-model/schema drift requiring migration | Rejected | No migration required; issue exists only in local minimal test harness schema used by foundation API tests. |

## Capability Lookup Path
1. `GET /api/v1/products/{product_id}/boms` and `GET /api/v1/products/{product_id}/boms/{bom_id}` now project capability fields.
2. These handlers call `has_action(db, identity, "admin.master_data.bom.manage")` to compute `allowed_actions`.
3. In `backend/tests/test_bom_foundation_api.py`, lightweight SQLite app builders do not create RBAC tables.
4. `has_action` executes RBAC joins (`user_role_assignments`, `role_permissions`, `permissions`, `scopes`) and fails with missing table errors.

## Patch Decision
- Selected option: Harness alignment patch (Option A/B class), no runtime logic changes.
- Why this option: It preserves production behavior and verifies the additive read projection contract while avoiding false negatives from incomplete in-test RBAC schema.
- What changed:
  - Updated [backend/tests/test_bom_foundation_api.py](backend/tests/test_bom_foundation_api.py)
  - Patched test app builders to control `product_router_module.has_action` in harness context.
  - Added assertions that read payloads include `allowed_actions` and expected non-manage values in baseline read tests.
- What did not change:
  - No changes to `backend/app/api/v1/products.py` runtime auth logic.
  - No changes to mutation permission code paths.
  - No migrations.
  - No frontend runtime code changes.

## Files Modified In Slice
- Updated: [backend/tests/test_bom_foundation_api.py](backend/tests/test_bom_foundation_api.py)
- Created: [docs/audit/mmd-fullstack-12b-b-bom-capability-read-auth-test-alignment.md](docs/audit/mmd-fullstack-12b-b-bom-capability-read-auth-test-alignment.md)

## Verification Evidence

### Backend Required Suite

Command:
```bash
cd backend
python -m pytest -q tests/test_bom_foundation_api.py
```
Result: 44 passed, 1 warning

Command:
```bash
cd backend
python -m pytest -q tests/test_bom_foundation_service.py
```
Result: 22 passed, 1 warning

Command:
```bash
cd backend
python -m pytest -q tests/test_mmd_rbac_action_codes.py
```
Result: 24 passed, 1 warning

Command:
```bash
cd backend
python -m pytest -q tests/test_bom_capability_guard_12b_a.py
```
Result: 4 passed, 1 warning

Command:
```bash
cd backend
python -m pytest -q tests/test_bom_allowed_actions_12b_a.py
```
Result: 6 passed, 1 warning

Command:
```bash
cd backend
python -m pytest -q tests/test_bom_foundation_api.py tests/test_bom_foundation_service.py tests/test_mmd_rbac_action_codes.py tests/test_bom_capability_guard_12b_a.py tests/test_bom_allowed_actions_12b_a.py
```
Result: 100 passed, 1 warning

### Backend Adjacent Checks

Command:
```bash
cd backend
python -m pytest -q tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_reason_code_foundation_api.py
```
Result: 49 passed, 1 warning

### Frontend Required Checks

Command:
```bash
cd frontend
npm.cmd run check:mmd:read
```
Result: 134 passed, 0 failed

Command:
```bash
cd frontend
npm.cmd run check:routes
```
Result: PASS (24 checks passed, 0 failed; 78 registered routes, 77 covered, 1 redirect excluded)

## Governance and Invariants Check
- Backend remains source of truth.
- Frontend remains intent-only; no new auth derivation in UI.
- Read capability projection is additive and server-derived.
- Write authorization remains strictly server-side via `admin.master_data.bom.manage`.
- No protected invariant was weakened.

## Residual Risk
- Global module monkeypatching in test harness requires care if test execution model changes to parallel module-shared workers.
- Current suite passes under existing test runner settings; no runtime risk identified.

## Final Verdict
PASS. 12B-B is complete as a narrow test-harness alignment patch with full required backend and frontend verification evidence and no runtime authorization semantic changes.

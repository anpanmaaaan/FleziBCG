# WORKSPACE-CLEAN-01 Report — Reason Code Dirty Workspace Triage Before Next P0-A

## Summary

Triage of the dirty workspace after P0-A-17B-01 closeout.

- Branch: `autocode` ✓
- **Option A selected** — dirty files are intentional, coherent work from an active MMD-FULLSTACK-13D slice
- No approval governance files are dirty
- No workflow/CI files are dirty
- Reason code tests: **62 passed, 1 warning** — all green
- Approval sanity + RBAC: **61 passed, 1 warning** — no regression
- **Recommendation: Do not revert. Continue as MMD-FULLSTACK-13D-CLOSEOUT slice.**

---

## Routing

- **Selected brain:** MOM Brain (FleziBCG AI Brain v6 Auto-Execution)
- **Selected mode:** Debug/Triage (workspace triage only)
- **Hard Mode MOM:** Not triggered (no execution/approval/auth/migration changes)
- **Reason:** Workspace inspection only. Dirty files are MMD reason code domain, frontend API types, and agent config. No approval governance, no IAM, no migration changes.

---

## Selected Option

**Option A — Dirty files are intentional Reason Code work.**

All backend changes are coherent, consistent, and test-aligned. The change in `reason_code_repository.py` is paired with exactly matching test updates in both test files. Frontend changes are MMD product API types + a minor station API fix. All tests pass. No regressions.

---

## Git State

| Property | Value |
|---|---|
| Branch | `autocode` |
| Modified files (unstaged) | 7 |
| Untracked files | 7 |

### Modified files

| File | Domain |
|---|---|
| `.github/agents/flezibcg-po-sa.agent.md` | Agent config |
| `backend/app/repositories/reason_code_repository.py` | MMD Reason Code |
| `backend/tests/test_reason_code_foundation_api.py` | MMD Reason Code |
| `backend/tests/test_reason_code_foundation_service.py` | MMD Reason Code |
| `frontend/src/app/api/index.ts` | MMD Frontend API types |
| `frontend/src/app/api/productApi.ts` | MMD Frontend API types |
| `frontend/src/app/api/stationApi.ts` | Frontend Station API fix |

### Untracked files

| File | Domain |
|---|---|
| `.github/agents/flezibcg-execution.agent.md` | Agent config (new) |
| `.github/agents/flezibcg-fe.agent.md` | Agent config (new) |
| `.github/agents/flezibcg-iam.agent.md` | Agent config (new) |
| `.github/agents/flezibcg-mmd.agent.md` | Agent config (new) |
| `.github/agents/flezibcg-quality.agent.md` | Agent config (new) |
| `.github/agents/flezibcg-tester.agent.md` | Agent config (new) |
| `.github/agents/flezibcg.agent.md` | Agent config (new) |

---

## Dirty File Classification

| File | Status | Domain | Likely Owner | Recommendation | Reason |
|---|---|---|---|---|---|
| `backend/app/repositories/reason_code_repository.py` | Modified | MMD Reason Code | MMD slice (MMD-FULLSTACK-13D) | **Keep — commit with slice** | Coherent behavior change: default filter changed from RELEASED-only to all-active. Tests are aligned. |
| `backend/tests/test_reason_code_foundation_api.py` | Modified | MMD Reason Code | MMD slice (MMD-FULLSTACK-13D) | **Keep — commit with slice** | Tests updated to match repository behavior change. RC-005 (DRAFT) added to fixture; assertions updated. 62/62 pass. |
| `backend/tests/test_reason_code_foundation_service.py` | Modified | MMD Reason Code | MMD slice (MMD-FULLSTACK-13D) | **Keep — commit with slice** | Service test docstrings + assertions updated to match repository behavior change. All pass. |
| `frontend/src/app/api/productApi.ts` | Modified | MMD Frontend API types | MMD-FE (BOM binding) | **Keep — commit with slice** | Adds `bom_binding_required_for_release` field to `ProductVersionItemFromAPI`, `ProductVersionCreateRequest`, `ProductVersionUpdateRequest`. Adds `ProductVersionBomBindingResponse` / `ProductVersionBomBindingCreateRequest` types and `getProductVersionBomBinding`, `bindBomToProductVersion`, `unbindBomFromProductVersion` API calls. Matches backend BOM binding routes (MMD-BE-14). |
| `frontend/src/app/api/index.ts` | Modified | MMD Frontend API types | MMD-FE (BOM binding) | **Keep — commit with slice** | Re-exports `ProductVersionBomBindingCreateRequest` and `ProductVersionBomBindingResponse` from `productApi.ts`. Consistent with above. |
| `frontend/src/app/api/stationApi.ts` | Modified | Frontend Station API | FE fix | **Keep — commit with slice** | Minor fix: `JSON.stringify(payload)` → `payload` for `openSession` and `closeSession`. The `request()` helper already handles serialisation; double-stringify was a bug. Non-breaking fix. |
| `.github/agents/flezibcg-po-sa.agent.md` | Modified | Agent config | AI tooling | **Keep — commit with slice** | 161 lines vs 150 in HEAD (+11). Expanded PO-SA agent mode instructions. Non-functional for tests. |
| `.github/agents/flezibcg-execution.agent.md` | Untracked | Agent config | AI tooling | **Stage and commit** | New specialist agent file. Non-functional for tests. |
| `.github/agents/flezibcg-fe.agent.md` | Untracked | Agent config | AI tooling | **Stage and commit** | New specialist agent file. |
| `.github/agents/flezibcg-iam.agent.md` | Untracked | Agent config | AI tooling | **Stage and commit** | New specialist agent file. |
| `.github/agents/flezibcg-mmd.agent.md` | Untracked | Agent config | AI tooling | **Stage and commit** | New specialist agent file. |
| `.github/agents/flezibcg-quality.agent.md` | Untracked | Agent config | AI tooling | **Stage and commit** | New specialist agent file. |
| `.github/agents/flezibcg-tester.agent.md` | Untracked | Agent config | AI tooling | **Stage and commit** | New specialist agent file. |
| `.github/agents/flezibcg.agent.md` | Untracked | Agent config | AI tooling | **Stage and commit** | New root agent (orchestrator). Routes to all specialists. |

### Approval governance files — dirty?

**None.** Zero approval governance files are modified.

### Workflow/CI files — dirty?

**None.** `.github/workflows/*.yml` and `test_pr_gate_workflow_config.py` are clean.

### Migration files — dirty?

**None.** `backend/alembic/versions/` is clean.

---

## What Each Change Does

### `reason_code_repository.py`

**Behavior change: MMD-FULLSTACK-13D**

```python
# Before (HEAD):
if lifecycle_status is None:
    query = query.where(ReasonCode.lifecycle_status == "RELEASED")  # hard RELEASED default

# After (working tree):
if lifecycle_status is not None:
    query = query.where(ReasonCode.lifecycle_status == lifecycle_status)  # no default status filter
```

**Intent:** The management UI needs to show newly created DRAFT codes immediately.
The old default silently hid DRAFT codes, so newly created codes were invisible until released.
Operational callers that want only RELEASED codes must now pass `lifecycle_status="RELEASED"` explicitly.

**Risk:** Any caller that relied on the implicit RELEASED default without passing `lifecycle_status` will now see DRAFT and RETIRED codes too. This is a breaking change to the default behavior. Tests already updated to reflect this. Any API consumer not in this workspace must be audited.

### Frontend `productApi.ts` / `index.ts`

Adds the TypeScript types and API client methods for BOM binding on ProductVersion (MMD-BE-14):
- `ProductVersionBomBindingResponse`
- `ProductVersionBomBindingCreateRequest`
- `getProductVersionBomBinding`, `bindBomToProductVersion`, `unbindBomFromProductVersion`
- `bom_binding_required_for_release` field on version create/update/read

These match the backend `GET/POST/DELETE /products/{id}/versions/{id}/bom-binding` routes already committed in the merge.

### Frontend `stationApi.ts`

Bug fix: `JSON.stringify(payload)` → `payload` in `openSession` and `closeSession`.
The `request()` helper serialises automatically; double-stringify sent garbled JSON.

### `.github/agents/*.agent.md`

New agent mode files for VS Code Copilot agent customization. Non-functional for backend tests.

---

## Approval Baseline Impact

| Test | Result |
|---|---|
| `test_approval_decision_same_score_api.py` (15/15) | PASS — no regression |
| `test_approval_security_events.py` | PASS — no regression |
| `test_rbac_action_registry_alignment.py` | PASS |
| `test_rbac_seed_alignment.py` | PASS |

**Zero approval regression from reason code or frontend changes.**

---

## MMD / Reason Code Impact

| Test | Result |
|---|---|
| `test_reason_code_foundation_api.py` | 62 passed — PASS |
| `test_reason_code_foundation_service.py` | included in 62 — PASS |

**All reason code tests pass with the working tree changes.**

---

## Verification Commands Run

```powershell
# Branch / git state
git branch --show-current          # → autocode
git status --porcelain
# → 7 modified, 7 untracked

# Diffs
git diff -- backend/app/repositories/reason_code_repository.py
git diff -- backend/tests/test_reason_code_foundation_api.py
git diff -- backend/tests/test_reason_code_foundation_service.py
git diff -- frontend/src/app/api/index.ts frontend/src/app/api/productApi.ts frontend/src/app/api/stationApi.ts

# Reason code tests
cd backend
$env:DATABASE_URL="postgresql+psycopg://x:x@127.0.0.1:9991/x"
pytest -q tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py
# → 62 passed, 1 warning

# Approval sanity check
pytest -q tests/test_approval_decision_same_score_api.py tests/test_approval_security_events.py tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py
# → 61 passed, 1 warning
```

---

## Results

| Category | Result |
|---|---|
| Branch | `autocode` ✓ |
| Approval files dirty | None ✓ |
| Workflow/CI files dirty | None ✓ |
| Migration files dirty | None ✓ |
| Reason code tests | 62 passed ✓ |
| Approval regression check | 61 passed ✓ |
| Backend changes coherent with tests | ✓ |
| Frontend changes coherent with backend routes | ✓ |
| Station API fix is non-breaking | ✓ |

---

## Scope Compliance

| Constraint | Status |
|---|---|
| Did not implement reason code behavior (triage only) | ✓ |
| Did not edit approval runtime | ✓ |
| Did not edit migrations | ✓ |
| Did not edit workflows | ✓ |
| Did not revert any files | ✓ |
| Did not commit automatically | ✓ |
| Did not run broad refactors | ✓ |
| Did not touch unrelated MMD files | ✓ |

---

## Recommendation

**Do not revert. Do not stash.**

The working tree represents a coherent, partially-implemented MMD-FULLSTACK-13D slice that:

1. **Changes a significant behavior** (`reason_code_repository.py` default filter) — this is already aligned with tests.
2. **Adds BOM binding frontend types** — consistent with backend routes committed in the merge.
3. **Fixes a stationApi bug** — small non-breaking fix.
4. **Adds agent config files** — non-functional for tests.

All pieces belong to the same commit or a related commit group. The right action is to continue the slice to completion, verify remaining gaps, and commit.

**Suggested commit grouping:**

| Commit | Files |
|---|---|
| `feat(mmd-rc): change reason code default filter to all-active statuses (MMD-FULLSTACK-13D)` | `reason_code_repository.py`, `test_reason_code_foundation_api.py`, `test_reason_code_foundation_service.py` |
| `feat(mmd-fe): add BOM binding types and API client (MMD-BE-14)` | `frontend/src/app/api/productApi.ts`, `frontend/src/app/api/index.ts` |
| `fix(fe): remove double JSON.stringify in stationApi openSession/closeSession` | `frontend/src/app/api/stationApi.ts` |
| `chore(agents): add specialist agent config files` | `.github/agents/*.agent.md` |

Do not mix commits — especially do not mix the reason code behavior change with agent config.

**Before committing:** confirm whether any other caller of `list_reason_codes_by_tenant` passes no `lifecycle_status` and depends on the RELEASED-only default. Search: `list_reason_codes`, `list_reason_codes_by_tenant` across `backend/app/`.

---

## Next Safe Slice

**MMD-FULLSTACK-13D-CLOSEOUT — Reason Code Validation UX Hardening Closeout / Verification**

Tasks for that slice:

1. Audit all callers of `list_reason_codes` / `list_reason_codes_by_tenant` for implicit RELEASED default reliance.
2. Confirm the design contract (`docs/design/02_domain/product_definition/reason-code-validation-ux-contract.md`) aligns with the behavior change.
3. Confirm the untracked audit doc (`docs/audit/mmd-fullstack-13d-reason-code-validation-ux-hardening.md`) is complete.
4. Run full governance regression to confirm zero approval/RBAC regression.
5. Commit in clean groups as above.
6. Update CI/PR gate if `test_reason_code_foundation_api.py` / `test_reason_code_foundation_service.py` are not already in workflow files.

---

## Stop Conditions Hit

None.

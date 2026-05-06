# MMD-FULLSTACK-13D-CLOSEOUT Report
## Reason Code Lifecycle Default Caller Audit

**Date**: 2026-05-07  
**Branch**: `autocode`  
**Slice**: MMD-FULLSTACK-13D-CLOSEOUT  
**Predecessor report**: `docs/audit/workspace-clean-01-reason-code-dirty-workspace-triage-report.md`

---

## Summary

The `WORKSPACE-CLEAN-01` triage flagged a critical behavior change in `reason_code_repository.py`: the default filter was changed from `lifecycle_status="RELEASED"` to all-active (no status filter when `lifecycle_status=None`). This report closes out that audit.

**Verdict: `ALLOW_MMD_FULLSTACK_13D_CLOSEOUT_CALLER_AUDIT`**  
**Selected Option: A — Behavior is intentional, safe, and contract-aligned**

All callers were audited. No caller implicitly relied on the old RELEASED-only default for correctness. The only frontend consumer is the admin management page, which intentionally requires DRAFT visibility. No operational or execution callers exist.

All tests pass:
- **62 passed** — reason code foundation tests
- **61 passed** — RBAC + approval baseline
- **Frontend build: ✓ 3409 modules transformed, 0 errors**
- **MMD regression check: 201 PASS, 0 FAIL**

---

## Routing

- **Selected brain:** MOM Brain (FleziBCG AI Brain v6 Auto-Execution)
- **Selected mode:** Strict
- **Hard Mode MOM:** v3 ON
- **Reason:** Touches MMD governance, lifecycle visibility, tenant-scoped master data, API behavior compatibility, and CI/PR gate safety. Caller audit with design evidence extraction required before closing.

---

## Design Evidence Extract

### Source docs read

| Doc | Why used |
|---|---|
| `backend/app/repositories/reason_code_repository.py` | Source of behavior change — docstring, implementation |
| `backend/app/services/reason_code_service.py` | Service-layer caller; `list_reason_codes` transparent pass-through |
| `backend/app/api/v1/reason_codes.py` | API endpoint caller; `lifecycle_status` from query param |
| `frontend/src/app/api/reasonCodeApi.ts` | Frontend API client; `listReasonCodes` with optional param |
| `frontend/src/app/pages/ReasonCodes.tsx` | Only frontend caller — management page |
| `docs/audit/mmd-fullstack-13d-reason-code-validation-ux-hardening.md` | MMD-FULLSTACK-13D audit evidence |
| `docs/design/02_domain/product_definition/reason-code-validation-ux-contract.md` | UX contract scope confirmation |
| `docs/audit/mmd-fullstack-14-bom-product-version-binding-fe-integration.md` | MMD-FE-14 evidence classifying new dirty files |

### Invariants found

| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| API endpoint passes `lifecycle_status` from query param verbatim | Contract | `reason_codes.py:63-89` | No invisible default added at API layer |
| Service passes `lifecycle_status` through transparently | Contract | `reason_code_service.py:130-150` | No invisible default added at service layer |
| Only caller in management page; does not pass `lifecycle_status` | Product intent | `ReasonCodes.tsx:151,170` | Intentional — management page wants all active |
| No execution/quality/station callers | Scope boundary | grep across `backend/app/**/*.py` | Zero non-test, non-RC-service references |
| Repository docstring documents new behavior | Governance | `reason_code_repository.py:22-24` | `"Operational callers that want only RELEASED codes must pass lifecycle_status='RELEASED' explicitly."` |

---

## Selected Option

**Option A — Caller audit confirms behavior is intentional**

**Reason:**

1. The call chain (API → service → repository) is transparent: `lifecycle_status` flows from the HTTP client to the repository without any invisible default at service or API layer.
2. The only frontend consumer is the **admin management page** (`ReasonCodes.tsx`), which does not pass `lifecycle_status` and intentionally needs to see DRAFT codes so newly created codes appear without requiring a lifecycle transition.
3. No execution, quality, station, production, or backflush service calls `list_reason_codes_by_tenant` or `list_reason_codes`.
4. Any operational dropdown that needs RELEASED-only codes would call the API with `lifecycle_status=RELEASED` in the query string. No such operational dropdown currently exists in the codebase (downtime analysis uses mock data).
5. The repository docstring explicitly documents the intentional behavior.
6. All tests (62 reason code, 61 approval/RBAC) pass against the changed behavior.

---

## Git State

| Property | Value |
|---|---|
| Branch | `autocode` ✓ |
| Modified files | 10 |
| Untracked files | 2 |
| Stash | `stash@{0}: On autocode: pre-mmd-be-14-unrelated-changes` |

### Modified files — full inventory

| # | File | Domain | Slice | Classification |
|---|---|---|---|---|
| 1 | `backend/app/repositories/reason_code_repository.py` | MMD Reason Code | MMD-FULLSTACK-13D | Intentional behavior change; docstring documents new default |
| 2 | `backend/tests/test_reason_code_foundation_api.py` | MMD Reason Code | MMD-FULLSTACK-13D | Updated tests; new RC-005 DRAFT fixture; 34 tests passing |
| 3 | `backend/tests/test_reason_code_foundation_service.py` | MMD Reason Code | MMD-FULLSTACK-13D | Updated test expectations; 28 tests passing |
| 4 | `frontend/src/app/api/productApi.ts` | MMD Frontend | MMD-FE-14 / MMD-BE-14 | BOM binding API types and methods |
| 5 | `frontend/src/app/api/index.ts` | MMD Frontend | MMD-FE-14 | BOM binding type re-exports |
| 6 | `frontend/src/app/api/stationApi.ts` | Frontend Station | Bug fix | Remove double `JSON.stringify` in `openSession`/`closeSession` |
| 7 | `frontend/src/app/i18n/registry/en.ts` | MMD Frontend i18n | MMD-FE-14 | BOM binding i18n keys (en) |
| 8 | `frontend/src/app/i18n/registry/ja.ts` | MMD Frontend i18n | MMD-FE-14 | BOM binding i18n keys (ja) |
| 9 | `frontend/src/app/pages/ProductDetail.tsx` | MMD Frontend | MMD-FE-14 | BOM binding UI — version selection, binding view, release readiness (+348 lines) |
| 10 | `frontend/scripts/mmd-read-integration-regression-check.mjs` | CI regression check | MMD-FE-14 | Extended with BOM binding regression assertions (+88 lines) |

### Untracked files — full inventory

| # | File | Domain | Classification |
|---|---|---|---|
| 1 | `docs/audit/mmd-fullstack-14-bom-product-version-binding-fe-integration.md` | Audit doc | MMD-FE-14 audit report |
| 2 | `docs/audit/workspace-clean-01-reason-code-dirty-workspace-triage-report.md` | Audit doc | WORKSPACE-CLEAN-01 triage report (created in session) |

### Note on stash

`stash@{0}: pre-mmd-be-14-unrelated-changes` exists. Do **not** pop this stash automatically. Understand its contents before using. It may contain pre-existing unrelated changes isolated before MMD-FE-14 work began.

### Note on previously-identified agent files

`.github/agents/*.agent.md` files reported as untracked by `WORKSPACE-CLEAN-01` are no longer dirty. They were committed (or stashed) in the intervening commits. They do not appear in current `git status`.

---

## Dirty File Groups

| Group | Files | Action |
|---|---|---|
| **A — Reason Code backend** | `reason_code_repository.py`, `test_reason_code_foundation_api.py`, `test_reason_code_foundation_service.py` | Commit together — single logical change |
| **B — BOM Binding frontend** | `productApi.ts`, `index.ts`, `stationApi.ts`, `en.ts`, `ja.ts`, `ProductDetail.tsx`, `mmd-read-integration-regression-check.mjs` | Commit together — single MMD-FE-14 slice |
| **C — Audit docs** | `workspace-clean-01-...-report.md`, `mmd-fullstack-13d-...-closeout-report.md`, `mmd-fullstack-14-...-fe-integration.md` | Commit together or with their owning slice |

---

## Reason Code Caller Audit

### Call chain

```
GET /v1/reason-codes?lifecycle_status=<optional>
  → reason_codes.py::list_reason_codes(lifecycle_status: str | None = None, ...)
    → reason_code_service.py::list_reason_codes(lifecycle_status=lifecycle_status, ...)
      → reason_code_repository.py::list_reason_codes_by_tenant(lifecycle_status=lifecycle_status, ...)
```

`lifecycle_status` flows transparently from HTTP client to DB query. No layer adds an invisible default.

### Caller matrix

| Caller | Layer | Passes lifecycle_status? | Expected behavior | Safe under new default? | Decision |
|---|---|---|---|---|---|
| `reason_codes.py::list_reason_codes` | API | Yes — forwarded from HTTP query param | Client-controlled | ✓ Safe — client can pass RELEASED if needed | Accept |
| `reason_code_service.py::list_reason_codes` | Service | Yes — forwarded from API caller | Pass-through | ✓ Safe — no invisible override | Accept |
| `ReasonCodes.tsx` (management page) | Frontend | No — not passed | Admin wants DRAFT + RELEASED | ✓ Intentional new behavior | Accept |
| Execution services (station, operation, downtime) | None | N/A — no callers found | N/A | ✓ N/A | No concern |
| Quality services | None | N/A — no callers found | N/A | ✓ N/A | No concern |
| Seed/migration scripts | None | N/A — no callers found | N/A | ✓ N/A | No concern |

### Grep evidence

```text
grep: list_reason_codes_by_tenant — 3 non-test files:
  1. app/repositories/reason_code_repository.py  (definition)
  2. app/services/reason_code_service.py  (single caller)
  3. app/api/v1/reason_codes.py  (imports list_reason_codes from service, not repo)
```

Zero references in execution, quality, station, production, or material modules.

---

## Lifecycle Default Decision

### What `lifecycle_status=None` means now

Returning all **active** reason codes regardless of lifecycle status (DRAFT + RELEASED).  
Inactive codes are still excluded unless `include_inactive=True` is also passed.

### Is this correct for each use case?

| Use case | Expected | Actual under new default | Correct? |
|---|---|---|---|
| Admin management page (`ReasonCodes.tsx`) | See DRAFT + RELEASED | All active — DRAFT + RELEASED | ✓ Yes |
| Operator downtime dropdown (hypothetical) | RELEASED only | Would see DRAFT + RELEASED | ⚠ Would need `?lifecycle_status=RELEASED` |
| Operator execution pause dropdown (hypothetical) | RELEASED only | Would see DRAFT + RELEASED | ⚠ Would need `?lifecycle_status=RELEASED` |

**The ⚠ rows are hypothetical — no such operational dropdown currently exists in the codebase.**  
When operational dropdowns are implemented (execution, downtime, quality), the caller MUST pass `lifecycle_status=RELEASED` explicitly. This requirement is now documented in the repository docstring.

### May DRAFT reason codes appear in operational dropdowns?

**No.** When operational use is implemented, the caller must pass `lifecycle_status="RELEASED"`. The repository default is not a safety gate for operational use — the caller is responsible for specifying the correct filter. This is the same pattern used by all other MMD entities (BOM, Routing, ProductVersion require explicit RELEASED checks in the services that need them).

### Does the API endpoint need a different default than the repository?

**No — with one future consideration.** The current endpoint is admin/management-only in frontend usage. If a new operational endpoint needs reason codes, it should pass `lifecycle_status=RELEASED` at the service call level, not rely on a query param from the client (to prevent DRAFT codes leaking into execution via a missing query param). This is a design note for future slices, not a blocking issue for this closeout.

---

## Frontend API Impact

### `frontend/src/app/api/productApi.ts`

Adds BOM binding types and API methods (MMD-FE-14):
- `bom_binding_required_for_release` field on version read/create/update types
- `ProductVersionBomBindingResponse` — binding details including `allowed_actions.can_remove`
- `ProductVersionBomBindingCreateRequest` — bind request payload
- Three API methods: `getProductVersionBomBinding`, `bindBomToProductVersion`, `unbindBomFromProductVersion`

Matches backend routes at `GET/POST/DELETE /{product_id}/versions/{version_id}/bom-binding`.

**Non-negotiable check:** Frontend UI (ProductDetail.tsx) reads `binding.allowed_actions?.can_remove` from backend response — does NOT derive authorization client-side. ✓

### `frontend/src/app/api/index.ts`

Re-exports `ProductVersionBomBindingCreateRequest`, `ProductVersionBomBindingResponse`. Consistent with `productApi.ts` additions.

### `frontend/src/app/api/stationApi.ts`

Bug fix only: `body: JSON.stringify(payload)` → `body: payload` in `openSession` and `closeSession`.  
The `request()` helper already serializes JSON. Double-stringify would have sent a JSON-encoded string as the body (double-encoded). Non-breaking fix — no type changes.

### `frontend/src/app/i18n/registry/en.ts` / `ja.ts`

Added BOM binding i18n keys under `productDetail.binding.*` and `productDetail.versions.*` namespaces. Not related to reason codes.

### `frontend/src/app/pages/ProductDetail.tsx`

Substantial BOM binding UI addition (+348 lines). Key non-negotiable checks:
- `binding.allowed_actions?.can_remove` — from backend response ✓
- `selectedVersionIsDraft` — UI enablement gate (intent-only; backend enforces) ✓
- `canShowBindIntent` / `canShowUnbindIntent` — computed from backend-truth fields ✓
- No lifecycle state machine logic derived in frontend ✓

### Approval governance files dirty?

**None.** Zero approval governance files modified.

### Migration files dirty?

**None.** `backend/alembic/versions/` clean.

---

## Verification Commands Run

```powershell
# Branch check
Set-Location G:\Work\FleziBCG
git branch --show-current  # → autocode

# Full git state
git status --short  # → 10 modified, 2 untracked
git diff --stat HEAD  # → 635 insertions(+), 35 deletions(-)

# Reason code caller search
grep -r "list_reason_codes_by_tenant" backend/app/  # → 3 non-test files (definition + 2 callers)
grep -r "lifecycle_status.*RELEASED" backend/app/   # → no implicit defaults outside RC repo

# Backend tests
Set-Location G:\Work\FleziBCG\backend
$env:DATABASE_URL="postgresql+psycopg://x:x@127.0.0.1:9991/x"
pytest -q tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py
# → 62 passed, 1 warning

pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_approval_decision_same_score_api.py tests/test_approval_security_events.py
# → 61 passed, 1 warning

# Frontend build
Set-Location G:\Work\FleziBCG\frontend
node node_modules/vite/bin/vite.js build
# → ✓ 3409 modules transformed. Built in 10.26s. 0 errors.

# MMD regression check
node scripts/mmd-read-integration-regression-check.mjs
# → SUMMARY: 201 passed, 0 failed
```

---

## Results

| Category | Result |
|---|---|
| Branch | `autocode` ✓ |
| Caller audit — RC repository | No unsafe callers found ✓ |
| Caller audit — execution/quality/station | Zero callers found ✓ |
| Lifecycle default documented in source | ✓ (repository docstring) |
| Reason code tests | 62 passed ✓ |
| RBAC + approval regression | 61 passed ✓ |
| Frontend build | ✓ 3409 modules, 0 errors |
| MMD regression check | 201 PASS, 0 FAIL ✓ |
| Approval governance files dirty | None ✓ |
| Migration files dirty | None ✓ |

---

## Files Changed

This slice is **audit-only**. No source files were modified by this closeout slice.  
All dirty files pre-existed before this slice ran.

---

## Scope Compliance

| Constraint | Status |
|---|---|
| Did not implement Reason Code features | ✓ |
| Did not change approval runtime | ✓ |
| Did not change migrations | ✓ |
| Did not change workflows | ✓ |
| Did not revert files | ✓ |
| Did not commit automatically | ✓ |
| Did not use `git add .` | ✓ |
| Did not touch unrelated files | ✓ |
| Did not weaken tests | ✓ |

---

## Commit Grouping Recommendation

Commit in three clean groups. Do not mix groups.

### Commit 1 — Reason Code lifecycle default change (MMD-FULLSTACK-13D)

```bash
git add backend/app/repositories/reason_code_repository.py
git add backend/tests/test_reason_code_foundation_api.py
git add backend/tests/test_reason_code_foundation_service.py
git add docs/audit/workspace-clean-01-reason-code-dirty-workspace-triage-report.md
git add docs/audit/mmd-fullstack-13d-reason-code-lifecycle-default-closeout-report.md
git commit -m "feat(mmd-rc): change reason code default filter to all-active statuses (MMD-FULLSTACK-13D)

Default lifecycle_status=None now returns all active reason codes.
Operational callers must pass lifecycle_status='RELEASED' explicitly.
Only caller is management page (admin), which intentionally wants DRAFT visibility.
62 tests pass."
```

### Commit 2 — BOM Binding frontend integration (MMD-FE-14)

```bash
git add frontend/src/app/api/productApi.ts
git add frontend/src/app/api/index.ts
git add frontend/src/app/api/stationApi.ts
git add frontend/src/app/i18n/registry/en.ts
git add frontend/src/app/i18n/registry/ja.ts
git add frontend/src/app/pages/ProductDetail.tsx
git add frontend/scripts/mmd-read-integration-regression-check.mjs
git add docs/audit/mmd-fullstack-14-bom-product-version-binding-fe-integration.md
git commit -m "feat(mmd-fe-14): add BOM binding UI and API types to ProductDetail

- productApi: binding response/request types, get/bind/unbind helpers
- stationApi: fix double JSON.stringify bug in openSession/closeSession
- ProductDetail: version selection, binding view, release readiness panel
- i18n: en/ja binding keys added
- mmd-read regression: 201 checks pass"
```

### Order

Commit 1 first (backend foundation), then Commit 2 (frontend).

### Do NOT include

- `.github/agents/` files — verify they are already committed; if not, add a separate commit 0
- Any stash contents — do not pop stash automatically

---

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Future operational dropdown omits `lifecycle_status=RELEASED` | Medium | Document in repo notes; add regression test when dropdown is built |
| Stash `pre-mmd-be-14-unrelated-changes` contains unknown changes | Low | Do not pop automatically; inspect with `git stash show -p stash@{0}` before deciding |
| ProductDetail.tsx is large (+348 lines); full page review not done in this slice | Low | MMD-FE-14 audit doc exists; regression check passes 201/201; build clean |

---

## Recommended Next Slice

**MMD-FULLSTACK-13D + MMD-FE-14 — Commit and verify**

Steps:
1. Inspect stash: `git stash show -p stash@{0}` — classify before continuing
2. Commit group 1 (reason code)
3. Commit group 2 (BOM binding frontend)
4. Run `npm run lint:i18n:registry` to confirm key parity (en/ja)
5. Run `npm run check:routes` for route smoke check
6. Run full backend regression: `pytest -q tests/ --tb=short`
7. Document any follow-up for operational dropdown RELEASED enforcement

**Future slice when operator-facing dropdowns are implemented:**  
Any caller of `reasonCodeApi.listReasonCodes` for execution/downtime/pause/quality-hold MUST pass `lifecycle_status: "RELEASED"`.

---

## Stop Conditions Hit

None.

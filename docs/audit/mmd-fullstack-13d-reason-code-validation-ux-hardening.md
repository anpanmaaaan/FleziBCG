# MMD-FULLSTACK-13D Audit Report
## Reason Code Create/Edit Validation UX Hardening

**Date**: 2025  
**Branch**: `autocode`  
**Slice**: MMD-FULLSTACK-13D  
**Depends on**: MMD-BE-10, MMD-BE-10A, MMD-BE-13, MMD-FULLSTACK-13, MMD-FULLSTACK-13B, MMD-FULLSTACK-13C

---

## 1. Objective

Replace the generic `"Invalid input. Please check the form."` error message with field-level validation UX in the Reason Code Create and Edit modals. This slice covers:

- Client-side pre-submit validation with inline field errors and focus management
- Backend 422 response parsing into field-level errors
- Backend 409 response mapping to the `reason_code` field
- Domain field constrained to enum via `<select>` (replaces unconstrained `<input type="text">`)
- Category field with datalist suggestions from loaded data
- Accessibility attributes (`aria-invalid`, `aria-describedby`, `role="alert"`) on all validated fields

---

## 2. Design Evidence Inspected

| Document | Finding |
|----------|---------|
| `reason-code-foundation-contract.md` | Entity shape; domain enum values: `EXECUTION_PAUSE, DOWNTIME, SCRAP, QUALITY_HOLD, MAINTENANCE, MATERIAL, REWORK, EXCEPTION, GENERAL` |
| `reason-code-write-governance-contract.md` | Backend is source of truth; frontend sends intent only; 422/409/403 error shapes documented |
| `backend/app/schemas/reason_code.py` | `ReasonCodeCreateRequest` has `extra="forbid"`, required fields: `reason_domain`, `reason_category`, `reason_code`, `reason_name`. `ReasonCodeUpdateRequest` excludes all three immutable fields at type level |
| `backend/app/api/v1/reason_codes.py` | 422 from Pydantic; 409 from `ValueError` with "Duplicate"; 403 from `require_action` |

---

## 3. Hard Mode MOM Assessment

**MOM v3: OFF** — This slice touches only validation UX display logic. It does not touch:
- Execution state machine
- Commands or events
- Projections or read models
- Authorization or IAM lifecycle
- DB migration
- Lifecycle transitions

---

## 4. Files Changed

### `frontend/src/app/pages/ReasonCodes.tsx`

| Change | Detail |
|--------|--------|
| `REASON_DOMAINS` constant | Added before component; 9 enum values from `reason-code-foundation-contract.md §2`. Backend remains final validator. |
| `createFieldErrors` / `editFieldErrors` state | `Record<string, string>`, initialized `{}` |
| `extractFieldErrors(err)` | Parses 422 array `detail` into `{fieldName: msg}` map; maps 409 → `{reason_code: ...}` |
| `categorySuggestions` useMemo | Derived from `codes`, filtered by selected `createForm.reasonDomain` |
| `handleCreate` | Pre-submit validation for 4 required fields + sortOrder integer check; focus management; on backend 422/409 → field errors; on other errors → summary |
| `handleEdit` | Pre-submit validation for `reason_name` required + sortOrder integer; immutable fields explicitly excluded with comment |
| `openEdit` | Added `setEditFieldErrors({})` |
| Create modal cancel | Added `setCreateFieldErrors({})` |
| Edit modal cancel | Added `setEditFieldErrors({})` |
| Create Domain field | `<input type="text">` → `<select id="create-reasonDomain">` with REASON_DOMAINS; `onChange` also resets `reasonCategory` |
| Create Category field | Added `id`, `list="create-category-suggestions"`, `aria-invalid`, `aria-describedby`, inline error `<p>`, `<datalist>` |
| Create Code/Name fields | Added `id`, `aria-invalid`, `aria-describedby`, removed `required` (custom JS validation), inline error `<p>` |
| Create SortOrder | Added `id="create-sortOrder"`, `aria-invalid`, `aria-describedby`, inline error `<p>`; wrapper changed to `items-start` |
| Edit Name field | Added `id="edit-reasonName"`, `aria-invalid`, `aria-describedby`, removed `required`, inline error `<p>` |
| Edit SortOrder | Added `id="edit-sortOrder"`, `aria-invalid`, `aria-describedby`, inline error `<p>` |

### `frontend/src/app/i18n/registry/en.ts`

7 keys added after `rcWrite.error.validation`:
- `rcWrite.error.field.reasonDomain.required`
- `rcWrite.error.field.reasonCategory.required`
- `rcWrite.error.field.reasonCode.required`
- `rcWrite.error.field.reasonName.required`
- `rcWrite.error.field.sortOrder.invalidNumber`
- `rcWrite.error.field.reasonCode.duplicate`
- `rcWrite.modal.field.reasonDomain.placeholder`

### `frontend/src/app/i18n/registry/ja.ts`

Same 7 keys added in Japanese.

### `frontend/scripts/mmd-read-integration-regression-check.mjs`

Section N added (N1–N10):
- N1: Domain field is `<select>` with constrained id
- N2: `REASON_DOMAINS` constant defined
- N3: Field error state (`createFieldErrors`, `editFieldErrors`) present
- N4: `extractFieldErrors` with 409 mapping present
- N5: `aria-invalid` on form fields
- N6: Category datalist present
- N7: EN field error keys present
- N8: JA field error keys present
- N9: Generic validation fallback key preserved in both registries
- N10: Comment confirming immutable fields excluded in edit handler

---

## 5. Verification Results

| Check | Result |
|-------|--------|
| `npm run check:mmd:read` | **192 PASS, 0 FAIL** (incl. all 10 Section N checks) |
| `npm run build` | **✓ built in 8.77s** — no TypeScript errors |
| `npm run lint` | **Clean** — no ESLint errors |
| `npm run lint:i18n:registry` | **PASS: en.ts and ja.ts are key-synchronized (1864 keys)** |
| `npm run check:routes` | **24 PASS, 0 FAIL** |

---

## 6. Governance Invariants Verified

| Invariant | Status |
|-----------|--------|
| Frontend sends intent only | ✅ — all write calls use `ReasonCodeCreateRequest` / `ReasonCodeUpdateRequest`; no lifecycle, tenant, or ID fields added |
| Edit payload excludes immutable fields | ✅ — `reason_domain`, `reason_category`, `reason_code` absent from edit form and `ReasonCodeUpdateRequest` at type level |
| `rcWrite.error.validation` fallback preserved | ✅ — used as summary on 422 with field errors; still present in both registries |
| Backend remains domain enum authority | ✅ — `REASON_DOMAINS` is a UX constraint only; comment in source; backend will validate |
| Authorization not derived in frontend | ✅ — 403 still maps to `resolveWriteError()`; no `can_create` / `can_update` used in validation path |

---

## 7. Risks and Remaining Items

| Risk | Severity | Status |
|------|----------|--------|
| `REASON_DOMAINS` list becomes stale if backend adds new values | Low | Acceptable — UX degrades gracefully (user can't select new domain until constant is updated); backend accepts the value either way |
| Category free text allows input that will 422 server-side if backend adds categorical constraints | Low | Acceptable — backend 422 will surface via `extractFieldErrors` and show inline error |
| No E2E tests for field-level validation UX | Medium | Out of scope for this slice; test matrix is defined in contract doc |

---

## 8. Definition of Done

- [x] Domain field is a constrained `<select>` (not free text)
- [x] Client-side validation runs before API call for all required fields
- [x] First invalid field receives focus on validation failure
- [x] Backend 422 response mapped to individual field errors
- [x] Backend 409 response mapped to `reason_code` field error
- [x] `aria-invalid` + `aria-describedby` + `role="alert"` on all validated fields
- [x] Category field has datalist suggestions from loaded data
- [x] i18n keys in both EN and JA registries, key-synchronized
- [x] Generic validation fallback key preserved
- [x] Edit handler explicitly excludes immutable fields with comment
- [x] Field errors cleared on modal close/cancel and on modal open
- [x] All regression checks pass (192/192)
- [x] Build clean, lint clean, i18n parity clean, route check clean
- [x] Validation UX contract doc created

---

## P1 Doc Index Patch

**Slice**: MMD-FULLSTACK-13D-P1  
**Date**: 2026-05-06

- Registered `docs/design/02_domain/product_definition/reason-code-validation-ux-contract.md` in `docs/design/INDEX.md` under a new `2026-05-06 (MMD-FULLSTACK-13D)` addendum entry.
- Registered it in `docs/design/AUTHORITATIVE_FILE_MAP.md` under a new `Reason Code write and validation UX truth` section, positioned as the UI validation UX companion contract — does not replace `reason-code-foundation-contract.md` or `reason-code-write-governance-contract.md`.
- No frontend runtime code changed (ReasonCodes.tsx, en.ts, ja.ts, regression script, API files untouched).
- No backend code changed.
- `git diff --check` passed — no whitespace/conflict markers.
- Source-level grep confirmed all three reference strings present in their respective files.


# Reason Code Validation UX Contract

**Slice**: MMD-FULLSTACK-13D  
**Status**: Implemented  
**Depends on**: `reason-code-foundation-contract.md`, `reason-code-write-governance-contract.md`

---

## 1. Scope

This contract governs field-level validation UX for the Reason Code **Create** and **Edit** modals in `ReasonCodes.tsx`. It defines:

- Which fields are validated client-side and how
- How backend error responses (422, 409) are parsed into field-level errors
- Accessibility requirements for error display
- What validation the frontend must **not** attempt to perform

This contract does **not** govern backend validation rules, lifecycle transitions, or authorization.

---

## 2. Source-of-Truth Principles

| Rule | Authority |
|------|-----------|
| Field required-ness | Backend (Pydantic schema) — UI provides early signal only |
| Domain enum values | Backend (accepts any string that passes server validation) — UI restricts to known enum for UX |
| Duplicate code rejection | Backend only — 409 response mapped to `reason_code` field |
| Authorization (can_create, can_update) | Backend only — 403 response |
| Lifecycle transitions | Backend only — never derived in UI |

---

## 3. Field Ownership Matrix

### Create Form (`ReasonCodeCreateRequest`)

| Field | UI id | Validated | Validation Rule | Mutable after create |
|-------|--------|-----------|-----------------|----------------------|
| `reason_domain` | `create-reasonDomain` | Yes | Required; constrained to `REASON_DOMAINS` enum via `<select>` | No |
| `reason_category` | `create-reasonCategory` | Yes | Required (trimmed non-empty); suggestions via datalist | No |
| `reason_code` | `create-reasonCode` | Yes | Required (trimmed non-empty) | No |
| `reason_name` | `create-reasonName` | Yes | Required (trimmed non-empty) | Yes |
| `description` | _(none)_ | No | Optional | Yes |
| `requires_comment` | _(checkbox)_ | No | Boolean toggle | Yes |
| `sort_order` | `create-sortOrder` | Yes | Integer if provided (not empty) | Yes |

### Edit Form (`ReasonCodeUpdateRequest`)

| Field | UI id | Validated | Validation Rule |
|-------|--------|-----------|-----------------|
| `reason_name` | `edit-reasonName` | Yes | Required (trimmed non-empty) |
| `description` | _(none)_ | No | Optional |
| `requires_comment` | _(checkbox)_ | No | Boolean toggle |
| `sort_order` | `edit-sortOrder` | Yes | Integer if provided (not empty) |
| `is_active` | _(checkbox)_ | No | Boolean toggle |

**Immutable fields in Edit**: `reason_domain`, `reason_category`, `reason_code` — these are never included in the edit payload and never validated client-side.

---

## 4. `REASON_DOMAINS` Enum (UI constraint)

The Create modal Domain field is a `<select>` constrained to:

```
EXECUTION_PAUSE, DOWNTIME, SCRAP, QUALITY_HOLD, MAINTENANCE,
MATERIAL, REWORK, EXCEPTION, GENERAL
```

Source: `reason-code-foundation-contract.md §2`. The backend remains the final validator; this list may be extended by updating both the constant and the backend schema in the same vertical slice.

---

## 5. Category Datalist Behavior

The Create modal Category field provides suggestions via `<datalist>` populated from existing reason codes in the loaded dataset, filtered by the currently selected domain. Suggestions are:
- Derived client-side from already-loaded data (no extra API call)
- Not exhaustive — free text entry is always allowed
- Cleared when the user changes the Domain selection

---

## 6. Client-Side Validation Rules

Validation runs on form submit before any API call. If any field fails:
1. `setCreateFieldErrors(errs)` / `setEditFieldErrors(errs)` is called with all failing fields
2. The first failing field (in focus order) receives `.focus()`
3. The API call is **not** made

**Focus order (Create)**: `reason_domain` → `reason_category` → `reason_code` → `reason_name` → `sort_order`  
**Focus order (Edit)**: `reason_name` → `sort_order`

---

## 7. Backend Error Mapping Contract

### 422 (Pydantic Validation Error)

FastAPI 422 body: `{"detail": [{"loc": ["body", "<field>"], "msg": "...", "type": "..."}]}`

Parsing:
- `loc[loc.length - 1]` → field name key
- `msg` from response used verbatim if non-empty; falls back to `rcWrite.error.validation`
- All field errors in the array are shown simultaneously

### 409 (Duplicate Code)

Maps to: `{ reason_code: t("rcWrite.error.field.reasonCode.duplicate") }`

### 403 / 401 / 404

No field-level errors — shown as summary `actionError` only.

### Any other error

Shown as summary `actionError` using `resolveWriteError()`.

---

## 8. Error Display Accessibility Requirements

For each validated field:
- Input/select has `id="<form>-<fieldCamelCase>"` (e.g., `create-reasonDomain`)
- `aria-invalid={!!fieldErrors.<field_key>}` present
- `aria-describedby` points to error `<p>` id when error present
- Error `<p>` has `role="alert"` and `id="<input-id>-error"`
- Error `<p>` uses `text-red-600` and red `border-red-400` on the input when active

---

## 9. i18n Keys (MMD-FULLSTACK-13D additions)

| Key | EN | Purpose |
|-----|----|---------|
| `rcWrite.error.field.reasonDomain.required` | Domain is required. | Client-side validation |
| `rcWrite.error.field.reasonCategory.required` | Category is required. | Client-side validation |
| `rcWrite.error.field.reasonCode.required` | Code is required. | Client-side validation |
| `rcWrite.error.field.reasonName.required` | Name is required. | Client-side validation |
| `rcWrite.error.field.sortOrder.invalidNumber` | Sort order must be a whole number. | Client-side validation |
| `rcWrite.error.field.reasonCode.duplicate` | A reason code with this code already exists in this domain. | 409 backend mapping |
| `rcWrite.modal.field.reasonDomain.placeholder` | Select domain... | Select placeholder |

Pre-existing fallback key (`rcWrite.error.validation`) is preserved and used as summary and as fallback for unknown 422 field messages.

---

## 10. Explicit Non-Goals

- Frontend does **not** check for duplicate reason codes before submit
- Frontend does **not** validate that `reason_code` format matches any pattern (e.g., uppercase, no spaces) — backend enforces
- Frontend does **not** enforce lifecycle-based restrictions on which fields can be edited
- Frontend does **not** compute authorization from client state

---

## 11. Test Matrix

| Scenario | Expected UX |
|----------|-------------|
| Submit Create with all fields empty | All 4 required fields get inline errors; domain focused |
| Submit Create with domain only | category, code, name errors shown |
| Submit Create with invalid sort_order (e.g., "abc") | sort_order error shown |
| Submit Create with duplicate code | API 409 → inline error on reason_code field |
| Submit Create with backend 422 on reason_name | Inline error on reason_name from backend msg |
| Submit Create with 403 | Summary actionError only; no field errors |
| Submit Edit with empty name | reason_name inline error; focus on edit-reasonName |
| Submit Edit with non-integer sort_order | sort_order inline error |
| Cancel Create modal | Field errors cleared; actionError cleared |
| Cancel Edit modal | Field errors cleared; actionError cleared |
| Re-open Edit modal | editFieldErrors reset to {} |
| Change domain in Create | reasonCategory reset to "", categorySuggestions filtered |

---

## 12. Files Changed (MMD-FULLSTACK-13D)

| File | Change |
|------|--------|
| `frontend/src/app/pages/ReasonCodes.tsx` | REASON_DOMAINS constant; createFieldErrors/editFieldErrors state; extractFieldErrors fn; categorySuggestions useMemo; updated handleCreate/handleEdit; modal field aria attributes and error display; Domain field → select; Category field → with datalist |
| `frontend/src/app/i18n/registry/en.ts` | 7 new `rcWrite.error.field.*` and `rcWrite.modal.field.reasonDomain.placeholder` keys |
| `frontend/src/app/i18n/registry/ja.ts` | Same 7 keys in Japanese |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | Section N (N1–N10): 10 new regression checks for 13D invariants |

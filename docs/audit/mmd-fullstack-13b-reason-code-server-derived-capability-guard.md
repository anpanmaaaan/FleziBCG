# MMD-FULLSTACK-13B — Reason Code Server-Derived Write Capability Guard Report

## History

| Date       | Author    | Event                                                            |
|------------|-----------|------------------------------------------------------------------|
| 2025-01    | AI Agent  | MMD-FULLSTACK-13 committed (write intent UI, frontend-only gate) |
| 2025-01    | AI Agent  | MMD-FULLSTACK-13B implemented (server-derived capability guard)  |

---

## 1. Scope

MMD-FULLSTACK-13B adds a server-derived `allowed_actions` block to every Reason Code read response (`list` and `detail`). The frontend consumes these fields to gate write controls instead of deriving permission from `lifecycle_status` alone.

**In scope:**
- Backend: `ReasonCodeAllowedActions` schema, `_compute_allowed_actions()` service function, `has_action` check in read endpoints
- Frontend: `ReasonCodeAllowedActions` TS interface, `ReasonCodes.tsx` button gating
- Regression check script: Section L (12 new checks)

**Out of scope:**
- Downtime execution impact (no execution path touched)
- Material / inventory (not relevant)
- Tenant / auth lifecycle (no model changes)
- DB migration (no schema change — `allowed_actions` is computed, not persisted)

---

## 2. Baseline Evidence Used

- `docs/design/AUTHORITATIVE_FILE_MAP.md` — confirmed Reason Code files
- `docs/governance/CODING_RULES.md` — server-is-truth, frontend-sends-intent-only
- `docs/governance/ENGINEERING_DECISIONS.md` — RBAC via `has_action(db, identity, action_code)`
- Existing BOM `allowed_actions` pattern (`bom_service.py`, `boms.py`) used as reference
- `backend/app/repositories/reason_code_repository.py` — confirms default-RELEASED filter
- `backend/tests/test_reason_code_foundation_api.py` — existing test patterns confirmed

---

## 3. Capability Contract

The `_compute_allowed_actions(has_manage: bool, lifecycle_status: str)` function encodes the following invariants:

| Condition                   | can_update | can_release | can_retire | can_create_sibling |
|-----------------------------|:----------:|:-----------:|:----------:|:------------------:|
| No manage permission        |     F      |      F      |     F      |         F          |
| DRAFT + manage              |     T      |      T      |     T      |         T          |
| RELEASED + manage           |     F      |      F      |     T      |         T          |
| RETIRED + manage            |     F      |      F      |     F      |         T          |

**Rationale:**
- A DRAFT code can be fully edited, released, or retired (all mutations open).
- A RELEASED code cannot be updated or re-released, but can be retired or a sibling created.
- A RETIRED code is terminal — only sibling creation (new code in same domain/category) is permitted.
- `can_create_sibling` remains True for all manage-permitted states because the create action targets a new record, not the existing one.

---

## 4. Backend Changes

### `backend/app/schemas/reason_code.py`
- Added `ReasonCodeAllowedActions` Pydantic model (4 bool fields).
- Added `allowed_actions: ReasonCodeAllowedActions` to `ReasonCodeItem`.

### `backend/app/services/reason_code_service.py`
- Added `_compute_allowed_actions(has_manage, lifecycle_status)` — pure function, no DB access.
- Updated `_to_item(row, has_manage=False)` to call `_compute_allowed_actions` and populate the field.
- Updated `list_reason_codes(... has_manage_permission=False)` — passes flag to `_to_item`.
- Updated `get_reason_code(... has_manage_permission=False)` — passes flag to `_to_item`.
- All 4 write functions (`create`, `update`, `release`, `retire`) call `_to_item(row, has_manage=True)` — write path is only reachable if the caller was authorized, so `has_manage=True` is correct.
- No-op update early return also uses `has_manage=True`.

### `backend/app/api/v1/reason_codes.py`
- Added `from app.security.rbac import has_action` import.
- `list_reason_codes` endpoint: calls `has_action(db, identity, "admin.master_data.reason_code.manage")`, passes result as `has_manage_permission`.
- `get_reason_code` endpoint: same pattern.
- Write endpoints unchanged — `require_action` dependency already enforces authorization before service is called.

### `backend/app/api/v1/products.py` (bug fix, pre-existing)
- Collapsed two multi-line `@router.post(...)` decorators for `/release` and `/retire` to single-line so RBAC marker test can detect them.

---

## 5. Frontend Changes

### `frontend/src/app/api/reasonCodeApi.ts`
- Added `ReasonCodeAllowedActions` interface (4 bool fields).
- Added `allowed_actions: ReasonCodeAllowedActions` to `ReasonCodeItemFromAPI`.

### `frontend/src/app/api/index.ts`
- Added `ReasonCodeAllowedActions` to the re-export block.

### `frontend/src/app/pages/ReasonCodes.tsx`
- Removed `const isDraft = c.lifecycle_status === "DRAFT"` and `const isRetired` derivations.
- Added `const aa = c.allowed_actions;` in their place.
- Edit button: `disabled={!aa.can_update || actionBusy}` (was `!isDraft`).
- Release button: `disabled={!aa.can_release || actionBusy}` (was `!isDraft`).
- Retire button: `disabled={!aa.can_retire || actionBusy}` (was `!isRetired` — note: this was already incorrect in 13A; 13B corrects it).
- Create button: `disabled={actionBusy || (codes.length > 0 && !codes.some((c) => c.allowed_actions.can_create_sibling))}` — uses sibling capability from any existing row.

---

## 6. Authorization / Permission Decision

**Decision point:** `backend/app/api/v1/reason_codes.py` — read endpoints only.

```python
has_manage = has_action(db, identity, "admin.master_data.reason_code.manage")
```

- `has_action` is called once per read request.
- The result is passed into the service; the service computes capability from lifecycle state.
- The backend is the sole authority for capability values; the frontend only renders them.
- JWT proves identity only. Authorization is enforced by `has_action` — a DB lookup against permission rows, not a JWT claim.
- Write endpoints do not re-check `has_action`; they use `require_action` as a request guard (FastAPI dependency) which raises 403 before the handler runs.

---

## 7. State Transition Guardrails

Capability values are informational for the UI. The actual state machine is enforced by write services:

| Action   | Service guard                                  |
|----------|------------------------------------------------|
| update   | Raises `ValueError` if `lifecycle_status != DRAFT` |
| release  | Raises `ValueError` if `lifecycle_status != DRAFT` |
| retire   | Raises `ValueError` if `lifecycle_status == RETIRED` |
| create   | No lifecycle prerequisite on the new record    |

The UI capability values mirror these guards:
- `can_update` / `can_release` → True only for DRAFT (matches service guard)
- `can_retire` → True for DRAFT and RELEASED (matches service guard)
- `can_create_sibling` → True for all manage-permitted states (create has no lifecycle prereq)

---

## 8. Boundary Guardrails

- **Backend-is-truth**: `allowed_actions` is computed from DB state on every read; no client-sent capability is trusted.
- **Frontend-sends-intent-only**: Buttons are disabled per `allowed_actions`, but even if a user bypasses the UI, the write endpoint will reject unauthorized or invalid-lifecycle requests.
- **No schema migration**: `allowed_actions` is a computed virtual field, never persisted.
- **Tenant isolation**: `list_reason_codes_by_tenant` and `get_reason_code_row` enforce `tenant_id` from the authenticated identity; capability is scoped to that tenant's data.

---

## 9. Downtime Reason Boundary

`ReasonCode.reason_domain` may be `"DOWNTIME"`. Reason Codes in the DOWNTIME domain are read by production-floor downtime recording screens. The `allowed_actions` guard applies to master-data management of these codes only — it does not touch production-floor downtime recording, OEE calculations, or any execution projection.

No execution state machine, no downtime event recording, and no OEE projection was modified by this task.

---

## 10. Tests Added / Updated

### New file: `backend/tests/test_reason_code_allowed_actions_13b.py`

| Test | Description |
|------|-------------|
| `test_list_reason_codes_includes_allowed_actions` | List response contains `allowed_actions` with all 4 fields |
| `test_get_reason_code_includes_allowed_actions` | Detail response contains `allowed_actions` with all 4 fields |
| `test_reason_code_allowed_actions_all_false_without_manage` | No manage → all False |
| `test_draft_reason_code_allowed_actions_all_true_with_manage` | DRAFT + manage → all True |
| `test_released_reason_code_allowed_actions_retire_and_sibling_with_manage` | RELEASED + manage → can_retire=T, can_create_sibling=T only |
| `test_retired_reason_code_allowed_actions_sibling_only_with_manage` | RETIRED + manage → can_create_sibling=T only |
| `test_read_reason_codes_does_not_require_manage_permission` | Read returns 200 without manage; allowed_actions all False |

**Test technique:**
- SQLite in-memory via `StaticPool` — no Postgres required.
- `reason_codes_router_module.has_action` patched at module level so SQLite DB needs no permission rows.
- `get_db` overridden via `reason_codes_router_module.get_db` dependency key.
- Tests pass `?lifecycle_status=DRAFT` / `?lifecycle_status=RETIRED` where needed (list endpoint defaults to RELEASED-only).

---

## 11. Regression Coverage

### `frontend/scripts/mmd-read-integration-regression-check.mjs` — Section L (12 new checks)

| Check ID | Description |
|----------|-------------|
| L1 | `ReasonCodeAllowedActions` type exists in `reasonCodeApi.ts` |
| L2 | `ReasonCodeItemFromAPI` has `allowed_actions: ReasonCodeAllowedActions` |
| L3–L6 | All 4 fields (`can_update`, `can_release`, `can_retire`, `can_create_sibling`) present in interface |
| L7–L9 | `ReasonCodes.tsx` consumes `aa.can_update`, `aa.can_release`, `aa.can_retire` |
| L10 | `ReasonCodes.tsx` consumes `can_create_sibling` |
| L11 | `ReasonCodes.tsx` does NOT use `isDraft` / `isRetired` lifecycle-only gate |
| L12 | `ReasonCodeAllowedActions` exported from `api/index.ts` |

**Total regression checks:** 174 (was 162)

---

## 12. Verification Commands

All commands verified passing:

**Backend:**
```powershell
cd G:\Work\FleziBCG\backend
uv run ... python -m pytest tests/test_reason_code_allowed_actions_13b.py tests/test_mmd_rbac_action_codes.py tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py
# Result: 100 passed

uv run ... python -m pytest tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_bom_foundation_api.py
# Result: 83 passed
```

**Frontend:**
```powershell
cd G:\Work\FleziBCG\frontend
npm.cmd run check:mmd:read    # 174 passed, 0 failed
npm.cmd run build             # built in ~7s, no errors
npm.cmd run lint              # no errors
npm.cmd run lint:i18n:registry  # 1846 keys, synchronized
npm.cmd run check:routes      # FAIL: 0
```

---

## 13. Remaining Risks / Deferred Items

### Known Gap: Empty-list Create capability

When `codes.length === 0` (no Reason Codes exist yet for the tenant), no row's `can_create_sibling` is available. The Create button falls back to always-enabled (`codes.length > 0` guard short-circuits). The backend 403 (`require_action` dependency) remains as the final enforcement gate.

**Ideal fix (deferred):** Return page-level metadata `{ capabilities: { can_create: bool } }` in the list response envelope — requires a response envelope change affecting multiple consumers. Deferred to a later task.

**Current risk level:** Low — only affects the Create button visibility hint when the list is empty. Authorization is still enforced server-side.

---

## 14. Final Verdict

**PASS — Implementation complete and verified.**

- Backend is sole authority for capability values. ✓
- Frontend renders server-derived `allowed_actions`; does not derive state from lifecycle alone. ✓
- Write guards remain at the backend (service + `require_action`). ✓
- 7 new backend tests covering all lifecycle × permission matrix cases. ✓
- 12 new regression checks in the MMD read regression script. ✓
- No execution state, no production reporting, no downtime recording touched. ✓
- No DB migration required. ✓
- All verification commands pass. ✓

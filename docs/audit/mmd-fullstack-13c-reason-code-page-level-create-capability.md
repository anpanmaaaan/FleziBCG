# MMD-FULLSTACK-13C — Reason Code Page-Level Create Capability / Empty List Guard

## History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2025-07 | AI Agent | Initial report — all changes verified |

---

## 1. Scope

**Ticket:** MMD-FULLSTACK-13C  
**Summary:** Reason Code page-level Create capability guard to fix the empty-list gap.

**Problem closed:** When the Reason Code list was empty (`codes.length === 0`), no row was available from which to read `allowed_actions.can_create_sibling`. The Create button was permanently disabled for all users on first load with an empty list.

**Solution:** Dedicated `GET /api/v1/reason-codes/capabilities` endpoint returns `{ can_create: bool, reason: null }` computed server-side from the caller's permission. Frontend fetches this on mount and gates the Create button on the result.

**Builds on:** MMD-FULLSTACK-13B (row-level `allowed_actions` per item, `can_create_sibling` still present in type definitions).

---

## 2. Baseline Evidence Used

- `docs/governance/CODING_RULES.md` — backend is source of truth; frontend sends intent only
- `docs/governance/ENGINEERING_DECISIONS.md` — RBAC is always server-side; `has_action` is the authority
- `backend/app/security/rbac.py` — `has_action(db, identity, action_code) -> bool`
- `backend/app/api/v1/reason_codes.py` (13B state) — `require_authenticated_identity`, `require_action`, existing endpoints
- `backend/app/schemas/reason_code.py` (13B state) — `ReasonCodeAllowedActions`, `ReasonCodeItem`
- `backend/tests/test_reason_code_allowed_actions_13b.py` (13B state) — 7 existing tests; `_build_app` fixture with `has_action` patch

---

## 3. Page-Level Capability Contract

| Field | Value |
|-------|-------|
| Endpoint | `GET /api/v1/reason-codes/capabilities` |
| Auth required | Authenticated identity (`require_authenticated_identity`) |
| Manage action NOT required | Endpoint is readable by any authenticated user |
| `can_create` rule | `has_action(db, IdentityLike(...), "admin.master_data.reason_code.manage")` |
| `reason` field | `null` (reserved for future message localization) |
| Manage user | `can_create = true` |
| Non-manage user | `can_create = false` |
| Unauthenticated | 401 — endpoint requires authentication |
| Capability fetch failure (frontend) | Create button disabled; backend 403 is final guard |

**Non-negotiable invariant:** `can_create` is computed entirely server-side from RBAC action lookup. Frontend does not compute or assume authorization.

---

## 4. Backend Changes

### 4.1 `backend/app/schemas/reason_code.py`

Added `ReasonCodeCapabilities` schema **before** `ReasonCodeAllowedActions`:

```python
class ReasonCodeCapabilities(BaseModel):
    """Page-level Reason Code create capability (MMD-FULLSTACK-13C)."""
    can_create: bool
    reason: str | None = None
```

### 4.2 `backend/app/api/v1/reason_codes.py`

**Import change:** Added `ReasonCodeCapabilities` to schema import.

**New endpoint** added at top of Read section (before list endpoint):

```python
@router.get("/capabilities", response_model=ReasonCodeCapabilities)
def get_reason_code_capabilities(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> ReasonCodeCapabilities:
    """Return page-level create capability (MMD-FULLSTACK-13C)."""
    can_create = has_action(
        db,
        IdentityLike(
            user_id=identity.user_id,
            tenant_id=identity.tenant_id,
            is_authenticated=identity.is_authenticated,
            acting_role_code=identity.acting_role_code,
        ),
        "admin.master_data.reason_code.manage",
    )
    return ReasonCodeCapabilities(can_create=can_create)
```

**Route ordering note:** `/capabilities` is registered before `/{code_id}` to prevent the path parameter from matching the literal string "capabilities".

---

## 5. Frontend Changes

### 5.1 `frontend/src/app/api/reasonCodeApi.ts`

Added `ReasonCodeCapabilities` interface:

```typescript
export interface ReasonCodeCapabilities {
  can_create: boolean;
  reason?: string | null;
}
```

Added `getCapabilities()` helper inside the `reasonCodeApi` object:

```typescript
getCapabilities(signal?: AbortSignal) {
  return request<ReasonCodeCapabilities>(`${BASE_PATH}/capabilities`, { signal });
},
```

### 5.2 `frontend/src/app/api/index.ts`

Added `ReasonCodeCapabilities` to the re-export block.

### 5.3 `frontend/src/app/pages/ReasonCodes.tsx`

**State added:**
```typescript
const [rcCapabilities, setRcCapabilities] = useState<ReasonCodeCapabilities | null>(null);
```

**Effect added** (parallel to list fetch, uses AbortController):
```typescript
useEffect(() => {
  const controller = new AbortController();
  reasonCodeApi
    .getCapabilities(controller.signal)
    .then((cap) => setRcCapabilities(cap))
    .catch(() => {
      // On failure, Create stays disabled; backend 403 is final guard
    });
  return () => controller.abort();
}, []);
```

**Create button updated:**

| Before (13B) | After (13C) |
|---|---|
| `disabled={actionBusy \|\| (codes.length > 0 && !codes.some((c) => c.allowed_actions.can_create_sibling))}` | `disabled={actionBusy \|\| !rcCapabilities?.can_create}` |
| Empty list → button always disabled | Empty list → button correctly reflects user's manage permission |
| `title` — no tooltip | `title={rcCapabilities?.can_create === false ? t("rcWrite.tooltip.createForbidden") : ""}` |

### 5.4 i18n Keys

Added to `en.ts`:
```
"rcWrite.tooltip.createForbidden": "Admin permission required to create reason codes."
```

Added to `ja.ts`:
```
"rcWrite.tooltip.createForbidden": "理由コードを作成するには管理者権限が必要です。"
```

Total i18n registry keys after change: **1847** (parity verified).

---

## 6. Authorization / Permission Decision

| Layer | Decision |
|-------|----------|
| Capability READ | `require_authenticated_identity` — any authenticated user can read their own capability |
| `can_create` computation | `has_action(db, identity, "admin.master_data.reason_code.manage")` — RBAC lookup, server-side |
| Create endpoint guard | Unchanged from 13B — `require_action("admin.master_data.reason_code.manage")` |
| Frontend | Calls `getCapabilities()` on mount; gates Create button on `can_create` |
| Failure mode | Capability fetch failure → Create stays disabled (null default state) |
| Backend invariant | Even if frontend bypasses, `require_action` on `POST /reason-codes` returns 403 |

**Separation of concerns:** Reading capability does not require manage permission. The manage permission is only needed to perform the actual creation. This mirrors standard UX practice of letting the UI show correct state without requiring the user to already hold the permission to read the page.

---

## 7. Empty-List Create Behavior

| Scenario | Before 13C | After 13C |
|---|---|---|
| List empty + manage user | Create disabled (no rows to derive `can_create_sibling` from) | Create enabled |
| List empty + non-manage user | Create disabled (correct but for wrong reason) | Create disabled (correct reason) |
| List non-empty + manage user | Create enabled (derived from first row) | Create enabled (from capabilities) |
| List non-empty + non-manage user | Create disabled | Create disabled |
| Capabilities fetch fails | — | Create disabled; backend 403 final guard |

---

## 8. Boundary Guardrails

- `can_create_sibling` remains in `ReasonCodeAllowedActions` type definition and row-level API responses (not removed). It may be used for future row-context actions.
- The Create button no longer reads `can_create_sibling` from rows — it reads `rcCapabilities.can_create` exclusively.
- The capabilities endpoint returns only authorization signal, not business data. No PII or sensitive state is exposed.
- The endpoint is not cacheable client-side beyond the component lifetime (abort signal used for cleanup).

---

## 9. Downtime Reason Code Boundary

This ticket does not affect Downtime records, execution state, or operational data. Reason Codes are master data (not execution data). No projection, event, or downtime invariant is touched.

---

## 10. Tests Added / Updated

### Backend — `backend/tests/test_reason_code_allowed_actions_13b.py`

Three new tests appended (tests #8–#10):

| Test | Description |
|------|-------------|
| `test_capabilities_endpoint_returns_can_create_true_for_manage_user` | Manage user → `can_create=true` |
| `test_capabilities_endpoint_returns_can_create_false_for_non_manage_user` | Non-manage user → `can_create=false` |
| `test_capabilities_endpoint_does_not_require_manage_permission` | 200 response for non-manage authenticated user |

File total: **10 tests** (7 from 13B + 3 from 13C).

---

## 11. Regression Coverage

### Backend (103 tests)

| Suite | Tests | Result |
|-------|-------|--------|
| `test_reason_code_allowed_actions_13b.py` | 10 | PASS |
| `test_reason_code_foundation_api.py` | ~45 | PASS |
| `test_reason_code_foundation_service.py` | ~15 | PASS |
| `test_mmd_rbac_action_codes.py` | ~33 | PASS |

### Adjacent MMD (83 tests)

| Suite | Tests | Result |
|-------|-------|--------|
| `test_product_foundation_api.py` | ~30 | PASS |
| `test_product_version_foundation_api.py` | ~30 | PASS |
| `test_bom_foundation_api.py` | ~23 | PASS |

### Frontend Regression Script

| Metric | Value |
|--------|-------|
| Total checks | **182** (was 174 in 13B) |
| Section M new checks | 8 (M1–M8) |
| L10 updated | Now checks `can_create_sibling` exists in type definition (not in page Create gate) |
| Result | **182 passed, 0 failed** |

### Frontend Build / Lint / i18n / Routes

| Check | Result |
|-------|--------|
| `npm run build` | Clean (no errors) |
| `npm run lint` | 0 errors |
| `npm run lint:i18n:registry` | PASS — 1847 keys synchronized |
| `npm run check:routes` | FAIL: 0 |

---

## 12. Verification Commands

### Backend

```powershell
cd G:\Work\FleziBCG\backend
uv run --with pytest --with fastapi --with sqlalchemy --with httpx --with anyio --with passlib --with "python-jose" --with bcrypt --with pydantic-settings --with psycopg --with "psycopg-binary" --with alembic --python 3.12 python -m pytest tests/test_reason_code_allowed_actions_13b.py tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py tests/test_mmd_rbac_action_codes.py
# Expected: 103 passed

uv run ... python -m pytest tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_bom_foundation_api.py
# Expected: 83 passed
```

### Frontend

```powershell
cd G:\Work\FleziBCG\frontend
npm.cmd run check:mmd:read    # Expected: 182 passed, 0 failed
npm.cmd run build              # Expected: built in ~7s, no errors
npm.cmd run lint               # Expected: 0 errors
npm.cmd run lint:i18n:registry # Expected: PASS (1847 keys)
npm.cmd run check:routes       # Expected: FAIL: 0
```

---

## 13. Remaining Risks / Deferred Items

| Item | Risk | Mitigation |
|------|------|------------|
| `can_create_sibling` in row-level responses still present | Low — data is ignored by Create button | May be removed in a future cleanup ticket |
| Capabilities fetch adds 1 extra API call on mount | Performance — negligible | Single lightweight GET, no auth body |
| `reason` field in `ReasonCodeCapabilities` always null | UX — tooltip text is hardcoded in i18n | Backend can populate reason in future for richer UI messages |
| No E2E Playwright test for empty-list Create visibility | Coverage gap | Deferred to E2E backlog |

---

## 14. Final Verdict

**VERIFIED — APPROVED TO SHIP**

All backend tests pass (103 direct + 83 adjacent). All frontend checks pass (182 regression checks, build clean, lint clean, i18n parity, route guard clean). The empty-list Create capability gap is closed. Authorization is server-derived. Frontend does not compute or assume RBAC decisions. Backend `require_action` remains the final enforcement layer.

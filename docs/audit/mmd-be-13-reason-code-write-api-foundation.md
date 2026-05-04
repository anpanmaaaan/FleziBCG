# MMD-BE-13 — Reason Code Write API Foundation

## History

| Date       | Author         | Status   |
|------------|----------------|----------|
| 2025-05-30 | GitHub Copilot | Complete |

**Prerequisite:** MMD-BE-10A (Reason Code manage action code added to registry) — committed.

---

## Scope

Implement the write API for Reason Code master data:
- `POST /api/v1/reason-codes` — create (DRAFT lifecycle)
- `PATCH /api/v1/reason-codes/{id}` — update metadata (DRAFT only)
- `POST /api/v1/reason-codes/{id}/release` — DRAFT → RELEASED
- `POST /api/v1/reason-codes/{id}/retire` — DRAFT|RELEASED → RETIRED

All write endpoints gated by `admin.master_data.reason_code.manage` action code.

**Out of scope (invariant-protected):**
- No downtime_reason coupling or mapping
- No execution, quality, material/inventory, or ERP side effects
- No hard delete, reactivation, clone, bulk import, policy binding
- No DB migrations (model pre-exists from MMD-BE-07)
- No frontend changes

---

## Baseline Evidence (MMD-BE-07 / MMD-BE-10A)

- `ReasonCode` ORM model: `lifecycle_status` field (DRAFT/RELEASED/RETIRED), no `downtime_reason_id`
- `ACTION_CODE_REGISTRY`: `"admin.master_data.reason_code.manage": "ADMIN"` (MMD-BE-10A)
- Existing read API: `GET /api/v1/reason-codes`, `GET /api/v1/reason-codes/{id}` (require_authenticated_identity)
- Existing service: `list_reason_codes`, `get_reason_code` (read-only)

---

## Write Contract (Service Layer)

### `create_reason_code(db, *, tenant_id, actor_user_id, payload)`
- Trims and uppercases `reason_domain`
- Checks for duplicate `(tenant_id, reason_domain, reason_code)` — raises `ValueError` if exists
- Sets `lifecycle_status = "DRAFT"` — immutable at create time
- `tenant_id` always from identity, never from payload
- Emits `REASONCODE.CREATED` security event

### `update_reason_code(db, *, tenant_id, actor_user_id, reason_code_id, payload)`
- Rejects if `lifecycle_status != "DRAFT"` → `ValueError("{status} Reason Code metadata cannot be updated")`
- Mutable fields: `reason_name`, `description`, `requires_comment`, `sort_order`, `is_active`
- Immutable fields: `reason_code`, `reason_domain`, `reason_category`, `tenant_id`, `lifecycle_status`, `downtime_reason_id`
- Uses `model_fields_set` to correctly handle `description=None` (allow explicit null)
- No-op if no changes detected
- Emits `REASONCODE.UPDATED` security event

### `release_reason_code(db, *, tenant_id, actor_user_id, reason_code_id)`
- Rejects RETIRED → `ValueError("RETIRED Reason Code cannot be released")`
- Rejects not-DRAFT → `ValueError("Only DRAFT Reason Codes can be released")`
- Sets `lifecycle_status = "RELEASED"`
- Emits `REASONCODE.RELEASED` security event

### `retire_reason_code(db, *, tenant_id, actor_user_id, reason_code_id)`
- Rejects if already RETIRED → `ValueError("Reason Code is already RETIRED")`
- Sets `lifecycle_status = "RETIRED"` from any non-RETIRED status
- Emits `REASONCODE.RETIRED` security event

---

## API Contract

| Method | Path | Auth | Success | Client Error |
|--------|------|------|---------|--------------|
| POST | `/api/v1/reason-codes` | `require_action("admin.master_data.reason_code.manage")` | 201 | 409 (duplicate), 422 (invalid payload) |
| PATCH | `/api/v1/reason-codes/{id}` | `require_action("admin.master_data.reason_code.manage")` | 200 | 404 (not found), 409 (wrong status), 422 (invalid payload) |
| POST | `/api/v1/reason-codes/{id}/release` | `require_action("admin.master_data.reason_code.manage")` | 200 | 404 (not found), 409 (wrong status) |
| POST | `/api/v1/reason-codes/{id}/retire` | `require_action("admin.master_data.reason_code.manage")` | 200 | 404 (not found), 409 (already retired) |

---

## Authorization

- Action code: `admin.master_data.reason_code.manage`
- Minimum role: `ADMIN` (as registered in `ACTION_CODE_REGISTRY`)
- Read endpoints remain `require_authenticated_identity` (no role restriction)
- Authorization is always server-side; frontend sends intent only

---

## Invariant Enforcement (extra="forbid")

`ReasonCodeCreateRequest` forbids: `tenant_id`, `lifecycle_status`, `reason_code_id`, `downtime_reason_id`

`ReasonCodeUpdateRequest` forbids: `tenant_id`, `lifecycle_status`, `reason_code_id`, `reason_code`, `reason_domain`, `reason_category`, `downtime_reason_id`

Pydantic raises 422 if any forbidden field is present in the payload.

---

## Files Changed

| File | Change |
|------|--------|
| `backend/app/schemas/reason_code.py` | Added `ReasonCodeCreateRequest`, `ReasonCodeUpdateRequest` |
| `backend/app/repositories/reason_code_repository.py` | Added `get_reason_code_by_code`, `create_reason_code_row`, `update_reason_code_row` |
| `backend/app/services/reason_code_service.py` | Added `_emit_reason_code_event`, `_get_or_404`, `create_reason_code`, `update_reason_code`, `release_reason_code`, `retire_reason_code` |
| `backend/app/api/v1/reason_codes.py` | Added 4 write endpoints (POST, PATCH, POST /release, POST /retire) |
| `backend/tests/test_reason_code_foundation_api.py` | Updated 405 test; added `_make_managed_app`, `_override_rc_manage` helpers; added 22 write API tests |
| `backend/tests/test_reason_code_foundation_service.py` | Added `SecurityEventLog` fixture table; added `TestCreateReasonCode`, `TestUpdateReasonCode`, `TestReleaseReasonCode`, `TestRetireReasonCode` test classes; added 2 boundary guard tests |
| `backend/tests/test_mmd_rbac_action_codes.py` | Updated `test_no_reason_code_write_routes_exist_yet` → `test_reason_code_write_routes_exist_and_are_scoped` |

---

## Downtime Reason Boundary

- `reason_code_service.py` does not import or reference `downtime_reason` modules
- `reason_codes.py` router does not reference downtime tables
- No field `downtime_reason_id` is present in write request schemas
- `extra="forbid"` on write schemas rejects any client attempt to inject `downtime_reason_id`

---

## Boundary Guardrails (Tested)

| Guard | Test |
|-------|------|
| No DELETE route | `test_reason_code_hard_delete_route_does_not_exist` |
| No forbidden routes | `test_no_reason_code_hard_delete_reactivate_activate_deactivate_clone_bulk_map_policy_routes_exist` |
| GET routes stay as authenticated-read | `test_reason_code_read_endpoints_do_not_require_manage_action` |
| No downtime_reason in service | `test_reason_code_write_does_not_modify_downtime_reason_api` |
| No execution/quality/ERP terms in service | `test_no_execution_material_quality_erp_side_effects` |

---

## Verification Results

### Backend

```
uv run ... python -m pytest -q tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py
59 passed, 1 warning

uv run ... python -m pytest -q tests/test_mmd_rbac_action_codes.py
31 passed, 1 warning
```

### Frontend

```
npm.cmd run check:mmd:read
SUMMARY: 134 passed, 0 failed
PASS all checks
```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Tenant bleed via payload | `tenant_id` from identity only, `extra="forbid"` on schemas |
| Lifecycle state corruption | Release/retire transitions validated in service with explicit state checks |
| Downtime coupling creep | Boundary guard tests in both service and API test suites |
| Unauthorized writes | `require_action("admin.master_data.reason_code.manage")` on all 4 write endpoints |
| DB migration needed | ReasonCode model pre-exists from MMD-BE-07, no schema changes required |

---

## Final Verdict

**PASS — MMD-BE-13 implementation is complete and verified.**

All write commands (create/update/release/retire) are implemented with correct:
- Lifecycle state machine enforcement
- Tenant scoping (all server-side)
- Action code authorization (`admin.master_data.reason_code.manage`)
- Forbidden payload field rejection (422)
- Audit event emission for all mutations
- No downtime_reason, execution, quality, ERP, or material move side effects

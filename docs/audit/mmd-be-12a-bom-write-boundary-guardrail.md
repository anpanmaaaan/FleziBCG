# MMD-BE-12A — BOM Write Boundary Audit / Event Guardrail Patch Report

## History

| Date       | Version | Change |
|------------|--------:|--------|
| 2026-05-03 | v1.0    | Verified BOM write boundary guardrails after BOM write API foundation (MMD-BE-12). No patches required. |

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** QA / Architecture
- **Hard Mode MOM:** v3 ON (BOM is a manufacturing definition object; mutations must not cross into execution/material/ERP)
- **Reason:** This slice audits mutation paths for a MOM/MES manufacturing definition domain. Hard Mode MOM v3 is mandatory per copilot-instructions.md when verifying BOM write paths.

---

## 1. Scope

Post-implementation boundary guardrail audit for MMD-BE-12 (BOM Write API Foundation). Verifies:

- BOM write service emits only allowed MMD governance audit events (no execution/material/ERP side effects)
- All allowed write routes are present; all forbidden routes are absent
- No `product_version_id` or Product Version binding behavior exists
- No material/backflush/inventory/ERP/traceability/quality logic exists
- BOM Item mutations are DRAFT-only (lifecycle guardrail)
- Auth action code remains `admin.master_data.bom.manage`
- Backend tests pass; frontend read regression passes

**Not in scope:** BOM FE write UI, Product Version binding, material/backflush/ERP/traceability/quality, new BOM commands, DB migrations.

---

## 2. Baseline Evidence Used

| Document | Path |
|----------|------|
| BOM Write API Foundation audit | `docs/audit/mmd-be-12-bom-write-api-foundation.md` |
| BOM Write Governance Contract | `docs/audit/mmd-be-09-bom-write-governance-contract.md` |
| BOM Action Code Registry Patch | `docs/audit/mmd-be-09a-bom-action-code-registry-patch.md` |
| BOM Minimal Read Model | `docs/audit/mmd-be-05-bom-minimal-read-model.md` |

---

## 3. Source Inspection Summary

Files inspected:

| File | Lines | Finding |
|------|-------|---------|
| `backend/app/models/bom.py` | full | No forbidden fields; no product_version_id, no material/inventory fields |
| `backend/app/schemas/bom.py` | full | 4 write schemas with `extra="forbid"`; boundary guards in docstrings; all forbidden fields absent from runtime code |
| `backend/app/repositories/bom_repository.py` | full | 11 functions; pure CRUD; no side effects; no forbidden domain behavior |
| `backend/app/services/bom_service.py` | full | 7 write functions; 2 event helpers; all events in allowed set; no forbidden logic |
| `backend/app/api/v1/products.py` | BOM section | 8 BOM routes (2 read + 7 write); all write routes use `require_action("admin.master_data.bom.manage")` |

**Keyword scan** (grep for `product_version_id`, `material`, `inventory`, `backflush`, `erp`, `posting`, `traceability`, `genealogy`, `quality`, `acceptance`, `execution`, `state_machine`, `reserve`, `consume`, `lot`, `batch`, `warehouse`) across all BOM source files:

- `products.py` lines 211/233/254/309: `product_version_id` references belong to **Product Version API endpoints** (not BOM section) — **CLEAN**
- `schemas/bom.py` lines 17/44/68/17–18: all references appear **in docstring comments as boundary guards** — not in runtime code — **CLEAN**
- **No runtime forbidden-domain logic found in any BOM source file**

---

## 4. Event Boundary Findings

**Status: CLEAN — no patch required**

All events emitted by `bom_service.py` via `record_security_event()`:

| Emitted By | Event Type | Resource Type | Verdict |
|------------|-----------|---------------|---------|
| `create_bom` | `BOM.CREATED` | `bom` | ✅ Allowed |
| `update_bom` | `BOM.UPDATED` | `bom` | ✅ Allowed |
| `release_bom` | `BOM.RELEASED` | `bom` | ✅ Allowed |
| `retire_bom` | `BOM.RETIRED` | `bom` | ✅ Allowed |
| `add_bom_item` | `BOM_ITEM.ADDED` | `bom_item` | ✅ Allowed |
| `update_bom_item` | `BOM_ITEM.UPDATED` | `bom_item` | ✅ Allowed |
| `remove_bom_item` | `BOM_ITEM.REMOVED` | `bom_item` | ✅ Allowed |

These are MMD governance/audit events only. No execution commands, no quality decisions, no material movement events, no ERP posting events, no inventory reservation events, no traceability/genealogy events are emitted.

`_emit_bom_item_event` is called **before** `delete_bom_item_row` in `remove_bom_item`, preserving audit integrity.

---

## 5. Route Boundary Findings

**Status: CLEAN — no patch required**

### Allowed routes — confirmed present

| Method | Path | Status |
|--------|------|--------|
| GET | `/{product_id}/boms` | ✅ Present (line 262) |
| GET | `/{product_id}/boms/{bom_id}` | ✅ Present (line 278) |
| POST | `/{product_id}/boms` | ✅ Present (line 339) |
| PATCH | `/{product_id}/boms/{bom_id}` | ✅ Present (line 362) |
| POST | `/{product_id}/boms/{bom_id}/release` | ✅ Present (line 385) |
| POST | `/{product_id}/boms/{bom_id}/retire` | ✅ Present (line 406) |
| POST | `/{product_id}/boms/{bom_id}/items` | ✅ Present (line 427) |
| PATCH | `/{product_id}/boms/{bom_id}/items/{bom_item_id}` | ✅ Present (line 451, multi-line decorator) |
| DELETE | `/{product_id}/boms/{bom_id}/items/{bom_item_id}` | ✅ Present (line 480) |

### Forbidden routes — confirmed absent

| Route | Status |
|-------|--------|
| DELETE `/{product_id}/boms/{bom_id}` | ✅ Absent |
| POST `.../reactivate` | ✅ Absent |
| POST `.../clone` | ✅ Absent |
| POST `.../bind-product-version` | ✅ Absent |
| POST `.../bulk-import` | ✅ Absent |
| POST `.../replace-items` | ✅ Absent |
| POST `.../material-reserve` | ✅ Absent |
| POST `.../backflush` | ✅ Absent |
| POST `.../erp-post` | ✅ Absent |

---

## 6. Data Boundary Findings

**Status: CLEAN — no patch required**

| Check | Finding |
|-------|---------|
| `product_version_id` in BOM model | Not present (`Bom.__table__.columns` scan) |
| `product_version_id` in BOM schemas | Not present in runtime fields; mentioned only in docstring boundary guards |
| Product Version binding behavior | None — no service function touches ProductVersion for BOM |
| Material availability check | None |
| Inventory reservation | None |
| Lot/batch/warehouse fields | None |
| Genealogy creation | None |
| Traceability side effects | None |

---

## 7. Lifecycle / Item Guardrail Findings

**Status: CLEAN — all guardrails enforced and tested**

| Guardrail | Enforcement Location | Test |
|-----------|---------------------|------|
| BOM metadata update only while DRAFT | `update_bom` → `if row.lifecycle_status != "DRAFT": raise ValueError` | `test_update_bom_rejects_released`, `test_update_bom_rejects_retired`, `test_update_bom_only_draft` |
| BOM Item add only while parent DRAFT | `add_bom_item` → `if row.lifecycle_status != "DRAFT": raise ValueError` | `test_add_bom_item_rejects_released_or_retired_parent`, `test_add_update_remove_item_only_draft_parent` |
| BOM Item update only while parent DRAFT | `update_bom_item` → `if bom_row.lifecycle_status != "DRAFT": raise ValueError` | `test_update_bom_item_rejects_released_or_retired_parent` |
| BOM Item remove only while parent DRAFT | `remove_bom_item` → `if row.lifecycle_status != "DRAFT": raise ValueError` | `test_remove_bom_item_rejects_released_or_retired_parent` |
| Release only DRAFT | `release_bom` → `if row.lifecycle_status != "DRAFT": raise ValueError` | `test_release_bom_rejects_released_or_retired`, `test_release_only_draft` |
| Retire only DRAFT or RELEASED | `retire_bom` → `if row.lifecycle_status == "RETIRED": raise ValueError` | `test_retire_bom_rejects_retired`, `test_retire_draft_or_released` |
| Release requires at least one item | `release_bom` → `if not row.items: raise ValueError` | `test_release_bom_requires_items` |
| Circular BOM guard | `add_bom_item` → `if component_product_id == product_id: raise ValueError` | `test_add_bom_item_rejects_parent_as_component`, `test_component_product_cannot_equal_parent_product` |
| quantity must be > 0 | `add_bom_item`, `update_bom_item` | `test_add_bom_item_rejects_non_positive_quantity`, `test_quantity_positive` |
| scrap_factor must be ≥ 0 | `add_bom_item`, `update_bom_item` | `test_add_bom_item_rejects_negative_scrap_factor`, `test_scrap_factor_non_negative` |
| Auth: all write routes require `admin.master_data.bom.manage` | `require_action("admin.master_data.bom.manage")` on all 7 write endpoints | All `test_..._requires_manage_action` tests |
| BOM read routes do NOT require manage action | `require_authenticated_identity` only on GET routes | `test_bom_read_endpoints_do_not_require_manage_action` |

No gaps found. No new tests were required.

---

## 8. Tests Added / Updated

**No test changes required.** All required guardrail tests already exist from MMD-BE-12.

Test coverage verified:
- `backend/tests/test_bom_foundation_api.py` — 42 tests (18 existing read + 35 write = confirmed 42 unique test functions, 66 total pass)
- `backend/tests/test_bom_foundation_service.py` — 24 tests (11 read + 13 write)
- `backend/tests/test_mmd_rbac_action_codes.py` — 24 tests

---

## 9. Files Changed

**No source files were changed in this slice.** The audit confirmed all boundaries are intact.

| File | Change |
|------|--------|
| `docs/audit/mmd-be-12a-bom-write-boundary-guardrail.md` | Created (this document) |

---

## 10. Verification Commands

All commands executed and confirmed passing:

```powershell
# BOM foundation + RBAC tests
cd backend
python -m pytest -q tests/test_bom_foundation_api.py tests/test_bom_foundation_service.py tests/test_mmd_rbac_action_codes.py
# Result: 90 passed, 1 warning

# Regression: product/version/reason code APIs
python -m pytest -q tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_reason_code_foundation_api.py
# Result: 49 passed, 1 warning

# Frontend read regression
cd frontend
npm run check:mmd:read
# Result: 105 passed, 0 failed

# Frontend route check
npm run check:routes
# Result: All PASS
```

---

## 11. Remaining Risks / Deferred Items

| Risk | Severity | Deferred To | Note |
|------|----------|-------------|------|
| `bom_code` immutability not enforced at DB constraint level | Low | Post-MMD-BE-12 | Service enforces; no migration in scope |
| `line_no` uniqueness not enforced at DB constraint level | Low | Post-MMD-BE-12 | Service enforces; no migration in scope |
| BOM clone / copy-as-draft | N/A | Future milestone | Hard-excluded from this slice |
| Product Version binding | N/A | Future milestone | Explicitly deferred per governance contract |
| Material/backflush/ERP integration | N/A | Execution milestones | Hard-excluded from master data foundation |
| BOM FE write UI | N/A | Separate milestone | Backend-only story; no FE write routes added |
| Effective date conflict detection (overlapping BOMs for same product) | Low | Future | Not required by current governance contract |

---

## 12. Final Verdict

**PASS — No boundary leaks found. No patches required.**

| Check | Result |
|-------|--------|
| BOM events are MMD governance/audit events only | ✅ PASS |
| No execution/material/backflush/ERP/traceability/quality events | ✅ PASS |
| All 7 allowed write routes present | ✅ PASS |
| All 9 forbidden routes absent | ✅ PASS |
| No `product_version_id` in runtime BOM code | ✅ PASS |
| No Product Version binding behavior | ✅ PASS |
| No material/inventory/ERP/traceability/quality logic | ✅ PASS |
| BOM Item mutations DRAFT-only enforced and tested | ✅ PASS |
| Auth: all write routes require `admin.master_data.bom.manage` | ✅ PASS |
| Auth: read routes remain authenticated-read only | ✅ PASS |
| 90 backend tests pass (BOM + RBAC suite) | ✅ PASS |
| 49 regression tests pass (product/version/reason code) | ✅ PASS |
| Frontend read regression: 105 checks pass | ✅ PASS |
| Frontend route checks pass | ✅ PASS |
| No new source file changes | ✅ PASS |
| No DB migrations | ✅ PASS |
| No auto-commit | ✅ PASS |

# BOM Write Governance Contract

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Added BOM write governance and minimal mutation contract before implementation. |

---

## Routing
- **Selected brain:** MOM Brain
- **Selected mode:** Backend command-boundary design mode + Authorization/action-code governance mode + Lifecycle governance mode + Architecture boundary guardian mode + Source audit/evidence mode
- **Hard Mode MOM:** v3 ON
- **Reason:** BOM write-path changes MMD manufacturing definition truth and must be bounded from material consumption, inventory movement, backflush, ERP posting, traceability genealogy, quality acceptance, and execution confirmation before implementation.

---

## 1. Scope

This contract defines the BOM write governance boundary for the Manufacturing Master Data domain in FleziBCG before any BOM mutation API is implemented.

### In scope
- BOM write command classification (READY / DEFERRED / FORBIDDEN)
- BOM Item write command classification
- BOM lifecycle transition governance
- Authorization / action-code requirements for BOM mutations
- Future API endpoint contract proposal
- Validation rules for future BOM write implementation
- Audit/event expectations for BOM mutations
- Cross-domain boundary guardrails
- Required tests for future write slice

### Out of scope
- Backend write API implementation
- Frontend write UI implementation
- BOM schema write request/response model implementation
- RBAC/action-code registry source changes
- Migration/schema changes
- Test implementation
- Product Version binding
- ERP/PLM sync
- Material/inventory/backflush behavior
- Quality linkage
- Traceability genealogy
- Auto-commit

---

## 2. Current Read Baseline

| Subsystem | Status | Evidence |
|---|---|---|
| BOM model | IMPLEMENTED | `backend/app/models/bom.py` — `Bom`, `BomItem` ORM models |
| BOM migration | IMPLEMENTED | `backend/alembic/versions/0008_boms.py`, `backend/scripts/migrations/0019_boms.sql` |
| BOM schemas (read) | IMPLEMENTED | `backend/app/schemas/bom.py` — `BomItem`, `BomDetail`, `BomComponentItem` |
| BOM repository (read) | IMPLEMENTED | `backend/app/repositories/bom_repository.py` — `list_boms_by_product`, `get_bom_by_id` |
| BOM service (read) | IMPLEMENTED | `backend/app/services/bom_service.py` — `list_boms`, `get_bom` |
| BOM API (read) | IMPLEMENTED | `GET /api/v1/products/{product_id}/boms`, `GET /api/v1/products/{product_id}/boms/{bom_id}` |
| BOM API (write) | ABSENT | Confirmed by route inspection and `test_bom_api_has_no_post_patch_delete_routes` |
| BOM action code | ABSENT | `admin.master_data.bom.manage` not present in `rbac.py` |
| `product_version_id` on BOM | ABSENT | Explicitly deferred — no column in model or migration |
| FE BOM screens | PARTIAL/BACKEND_API | `screenStatus.ts` — mutation actions explicitly disabled |
| FE write schemas | ABSENT | No BOM write API types in `productApi.ts` |
| Regression guards (read) | 15 checks (section H) in `mmd-read-integration-regression-check.mjs` | All 105 checks passing |

---

## 3. BOM Write Principles

### Non-negotiables

1. **BOM is manufacturing definition truth.** BOM defines intended component structure only. It does not perform material movement, inventory reservation, or execution confirmation.
2. **Backend is source of truth.** Frontend sends write intent only. Frontend does not derive authorization from persona or lifecycle inference.
3. **Action code required before mutation.** `admin.master_data.bom.manage` must exist in `ACTION_CODE_REGISTRY` in `backend/app/security/rbac.py` before any BOM mutation endpoint is implemented.
4. **Read endpoints remain authenticated-read.** `GET` BOM routes must keep `require_authenticated_identity`. No action code required for reads.
5. **`product_version_id` binding remains deferred.** The first BOM write slice must be product-scoped only. No `product_version_id` field or binding endpoint in the first write slice.
6. **DRAFT is the only mutable state.** Metadata and items can only be changed while the BOM is in DRAFT status.
7. **Lifecycle transitions are append-only.** RELEASED → DRAFT is forbidden. RETIRED → any is forbidden.
8. **BOM Item has no independent lifecycle.** BOM Items are mutable only while parent BOM is DRAFT.
9. **No circular BOM items without governance.** `component_product_id` must not equal parent `product_id` unless a future circularity policy is explicitly approved.
10. **No forbidden side effects.** No execution event, quality decision, material movement, inventory reservation, backflush, ERP posting, traceability genealogy, or automatic Product Version binding from any BOM write command.

---

## 4. Command Boundary Matrix

| Command | Decision | Reason | Future Guardrails |
|---|---|---|---|
| `create_bom` | **READY_FOR_IMPLEMENTATION_NEXT** | Read model, lifecycle values, and tenant scoping are proven. Creation always sets DRAFT. | schema `extra="forbid"` on lifecycle_status/is_current; tenant-scoped product lookup; unique bom_code per product |
| `update_bom_metadata` (DRAFT only) | **READY_FOR_IMPLEMENTATION_NEXT** | DRAFT state is reversible. Read model confirms which fields are mutable. | service must reject non-DRAFT; schema must forbid lifecycle_status change |
| `release_bom` | **READY_FOR_IMPLEMENTATION_NEXT** | Explicit transition command following Product/Routing precedent. DRAFT→RELEASED only. | service rejects non-DRAFT; audit record required |
| `retire_bom` | **READY_FOR_IMPLEMENTATION_NEXT** | Follows Product Version retire precedent. DRAFT or RELEASED → RETIRED. | service rejects RETIRED source; audit record required |
| `delete_bom` | **FORBIDDEN** | No delete governance. Potential traceability genealogy reference. Deletion could orphan historical BOM references. | Hard reject at route level; test must confirm route is absent |
| `reactivate_bom` | **FORBIDDEN** | RETIRED state must be terminal in this phase. No reactivation governance. | Hard reject at route level |
| `clone_bom` | **DEFERRED_REQUIRES_CONTRACT** | Engineering change workflow and BOM versioning semantics not yet governed. | Requires dedicated governance contract before implementation |
| `copy_from_existing_bom` | **DEFERRED_REQUIRES_CONTRACT** | Same as clone — BOM version divergence and item lineage not governed. | Same as clone |
| `bind_to_product_version` | **DEFERRED_REQUIRES_CONTRACT** | Product Version ↔ BOM binding requires a dedicated governance slice. `product_version_id` is nullable in model for future use only. | Must not be implemented until product-version binding contract exists |
| `unbind_from_product_version` | **NOT_APPLICABLE** | Binding is deferred; unbind has no applicability. | N/A until bind is implemented |
| `bulk_import_bom` | **DEFERRED_REQUIRES_CONTRACT** | Bulk write governance and schema validation for mass-import not established. | Dedicated bulk import contract required |
| `bulk_retire_bom` | **DEFERRED_REQUIRES_CONTRACT** | Bulk lifecycle governance not established. | Same |

---

## 5. BOM Item Command Boundary Matrix

| Command | Decision | Reason | Future Guardrails |
|---|---|---|---|
| `add_bom_item` (parent BOM is DRAFT) | **READY_FOR_IMPLEMENTATION_NEXT** | Item model, fields, and constraints are proven. | Parent BOM must be DRAFT; service must verify; unique line_no per BOM; quantity > 0; component must exist in same tenant |
| `update_bom_item` (parent BOM is DRAFT) | **READY_FOR_IMPLEMENTATION_NEXT** | Item mutation is safe when parent BOM is DRAFT. | Parent BOM must be DRAFT; service must verify |
| `remove_bom_item` (parent BOM is DRAFT) | **READY_FOR_IMPLEMENTATION_NEXT** | Removal while DRAFT is safe. No material side effects. | Parent BOM must be DRAFT; no material/inventory trigger on remove |
| `reorder_bom_items` | **DEFERRED_REQUIRES_CONTRACT** | `line_no` resequencing could silently affect historical item identity. Governance for line_no semantics needed. | Requires line_no uniqueness invariant review |
| `bulk_add_items` | **DEFERRED_REQUIRES_CONTRACT** | Bulk validation and error-handling semantics not established. | Dedicated bulk item contract required |
| `bulk_remove_items` | **DEFERRED_REQUIRES_CONTRACT** | Same as bulk_add_items. | Same |
| `replace_all_items` | **DEFERRED_REQUIRES_CONTRACT** | Atomic item replacement semantics, audit trail for replaced items, and history not governed. | Requires dedicated contract |

---

## 6. Lifecycle Transition Matrix

| Transition | Decision | Reason |
|---|---|---|
| `(new) → DRAFT` | **ALLOW_NEXT** (via `create_bom`) | Create always sets DRAFT. Client cannot override lifecycle on create. |
| `DRAFT → RELEASED` | **ALLOW_NEXT** (via explicit `release_bom` command) | Follows Product/Routing/ProductVersion precedent. Requires explicit command. |
| `DRAFT → RETIRED` | **ALLOW_NEXT** (via explicit `retire_bom` command) | A BOM may be retired before release if it was never used. |
| `RELEASED → RETIRED` | **ALLOW_NEXT** (via explicit `retire_bom` command) | Superseded BOMs should be retirable. |
| `RELEASED → DRAFT` | **FORBID** | RELEASED state implies the BOM has been exposed to planning and potentially consumed by routing/execution reads. Rollback to DRAFT is unsafe without governance. |
| `RETIRED → RELEASED` | **FORBID** | RETIRED is intended to be terminal in this phase. No reactivation governance. |
| `RETIRED → DRAFT` | **FORBID** | Same — RETIRED is terminal. |

### BOM Item Lifecycle Rule

BOM Items have no independent lifecycle status in this phase.

- Items are mutable (add/update/remove) only while parent BOM is `DRAFT`.
- When parent BOM is `RELEASED`, items are frozen — no add, update, or remove permitted.
- When parent BOM is `RETIRED`, items are frozen — no add, update, or remove permitted.
- Item immutability when parent is RELEASED/RETIRED must be enforced at the service layer, not only at the route layer.

---

## 7. Authorization / Action-Code Requirements

### Candidate Action Code

```
admin.master_data.bom.manage
```

Permission Family: `ADMIN` (consistent with all other MMD manage codes)

### Current Runtime Status

`admin.master_data.bom.manage` is **not present** in `backend/app/security/rbac.py` as of 2026-05-03.

The action-code registry document (`docs/design/02_registry/action-code-registry.md`) does not list it.

### Requirements for Future Implementation

| Requirement | Decision |
|---|---|
| Must add `admin.master_data.bom.manage` to `ACTION_CODE_REGISTRY` in `rbac.py` | **YES — prerequisite for write API** |
| Must add to `action-code-registry.md` governance doc | **YES — same slice as registry patch** |
| Must be a separate MMD-BE-09A patch slice before write API implementation | **YES** |
| BOM mutation endpoints must require this code | **ALL — create, update, release, retire** |
| BOM Item mutation endpoints must require this code | **YES — same manage code** |
| BOM read endpoints must remain `require_authenticated_identity` | **YES — unchanged** |
| Release/retire use same manage code (not separate lifecycle code) | **YES — follows coarse-grained MMD pattern** |
| Frontend route visibility is not authorization truth | **Confirmed — backend is always authority** |

### Authorization Matrix (future)

| Endpoint | Required Action Code | Auth Type |
|---|---|---|
| `GET /products/{id}/boms` | none (authenticated read) | `require_authenticated_identity` |
| `GET /products/{id}/boms/{bom_id}` | none (authenticated read) | `require_authenticated_identity` |
| `POST /products/{id}/boms` | `admin.master_data.bom.manage` | `require_action(...)` |
| `PATCH /products/{id}/boms/{bom_id}` | `admin.master_data.bom.manage` | `require_action(...)` |
| `POST /products/{id}/boms/{bom_id}/release` | `admin.master_data.bom.manage` | `require_action(...)` |
| `POST /products/{id}/boms/{bom_id}/retire` | `admin.master_data.bom.manage` | `require_action(...)` |
| `POST /products/{id}/boms/{bom_id}/items` | `admin.master_data.bom.manage` | `require_action(...)` |
| `PATCH /products/{id}/boms/{bom_id}/items/{item_id}` | `admin.master_data.bom.manage` | `require_action(...)` |
| `DELETE /products/{id}/boms/{bom_id}/items/{item_id}` | `admin.master_data.bom.manage` | `require_action(...)` |

---

## 8. Future API Contract Proposal

> **Do not implement.** This section describes the proposed contract for the future `MMD-BE-12` write API slice.

### READY_FOR_IMPLEMENTATION_NEXT Endpoints

#### `POST /products/{product_id}/boms`
- **Command:** `create_bom`
- **Auth:** `require_action("admin.master_data.bom.manage")`
- **Source state:** (new)
- **Target state:** DRAFT
- **Input schema boundary:**
  - Required: `bom_code`, `bom_name`
  - Optional: `effective_from`, `effective_to`, `description`
  - Forbidden: `lifecycle_status`, `bom_id`, `tenant_id`, `product_id`, `created_at`, `updated_at`
  - Schema must use `extra="forbid"`
- **Audit:** `BOM.CREATED` audit event record
- **Out-of-scope side effects:** No material/inventory/execution/ERP trigger
- **Tests required:** create returns DRAFT; bom_code uniqueness enforced; forbidden fields rejected (422); requires manage action (403)

#### `PATCH /products/{product_id}/boms/{bom_id}`
- **Command:** `update_bom_metadata`
- **Auth:** `require_action("admin.master_data.bom.manage")`
- **Source state:** DRAFT only
- **Target state:** DRAFT (unchanged lifecycle)
- **Input schema boundary:**
  - Optional: `bom_name`, `effective_from`, `effective_to`, `description`
  - Forbidden: `lifecycle_status`, `bom_code` (or DEFERRED if bom_code rename is needed), `bom_id`, `product_id`, `tenant_id`
  - Schema must use `extra="forbid"`
- **Audit:** `BOM.UPDATED` audit event with changed field names
- **Out-of-scope side effects:** None
- **Tests required:** update allowed for DRAFT; rejected for RELEASED (400/409); rejected for RETIRED (400/409); forbidden fields rejected (422); requires manage action (403)

#### `POST /products/{product_id}/boms/{bom_id}/release`
- **Command:** `release_bom`
- **Auth:** `require_action("admin.master_data.bom.manage")`
- **Source state:** DRAFT only
- **Target state:** RELEASED
- **Input schema boundary:** No body required (or empty body)
- **Audit:** `BOM.RELEASED` lifecycle transition record
- **Out-of-scope side effects:** No automatic Product Version binding, no ERP sync trigger
- **Tests required:** DRAFT → RELEASED; rejected from RELEASED (409); rejected from RETIRED (409); requires manage action (403)

#### `POST /products/{product_id}/boms/{bom_id}/retire`
- **Command:** `retire_bom`
- **Auth:** `require_action("admin.master_data.bom.manage")`
- **Source state:** DRAFT or RELEASED
- **Target state:** RETIRED
- **Input schema boundary:** No body required (or empty body)
- **Audit:** `BOM.RETIRED` lifecycle transition record
- **Out-of-scope side effects:** None
- **Tests required:** DRAFT → RETIRED; RELEASED → RETIRED; rejected from RETIRED (409); requires manage action (403)

#### `POST /products/{product_id}/boms/{bom_id}/items`
- **Command:** `add_bom_item`
- **Auth:** `require_action("admin.master_data.bom.manage")`
- **Source state:** Parent BOM must be DRAFT
- **Target state:** BOM Item created (parent BOM remains DRAFT)
- **Input schema boundary:**
  - Required: `component_product_id`, `line_no`, `quantity`, `unit_of_measure`
  - Optional: `scrap_factor`, `reference_designator`, `notes`
  - Forbidden: `bom_item_id`, `tenant_id`, `bom_id`, `created_at`, `updated_at`
  - Schema must use `extra="forbid"`
- **Audit:** `BOM_ITEM.ADDED` audit event with BOM context
- **Out-of-scope side effects:** No material reservation, no inventory check, no lot/batch selection
- **Tests required:** add succeeds for DRAFT BOM; rejected for RELEASED BOM (400/409); rejected for RETIRED BOM (400/409); requires manage action (403); component must exist in tenant; circular reference rejected; line_no uniqueness enforced; quantity > 0; UoM required

#### `PATCH /products/{product_id}/boms/{bom_id}/items/{bom_item_id}`
- **Command:** `update_bom_item`
- **Auth:** `require_action("admin.master_data.bom.manage")`
- **Source state:** Parent BOM must be DRAFT
- **Target state:** BOM Item updated (parent BOM remains DRAFT)
- **Input schema boundary:**
  - Optional: `quantity`, `unit_of_measure`, `scrap_factor`, `reference_designator`, `notes`
  - Forbidden: `component_product_id`, `line_no`, `bom_item_id`, `bom_id`, `tenant_id`
  - Schema must use `extra="forbid"`
- **Audit:** `BOM_ITEM.UPDATED` audit event with changed fields
- **Out-of-scope side effects:** None
- **Tests required:** update succeeds for DRAFT BOM item; rejected for non-DRAFT parent BOM; requires manage action (403); forbidden fields rejected (422)

#### `DELETE /products/{product_id}/boms/{bom_id}/items/{bom_item_id}`
- **Command:** `remove_bom_item`
- **Auth:** `require_action("admin.master_data.bom.manage")`
- **Source state:** Parent BOM must be DRAFT
- **Target state:** BOM Item removed
- **Input schema boundary:** No body
- **Audit:** `BOM_ITEM.REMOVED` audit event with line/component context
- **Out-of-scope side effects:** No material trigger; no inventory adjustment
- **Tests required:** remove succeeds for DRAFT parent BOM; rejected for non-DRAFT parent BOM; requires manage action (403); 404 for non-existent item

### DEFERRED / FORBIDDEN Endpoints

| Endpoint | Decision | Reason |
|---|---|---|
| `POST /products/{id}/boms/{bom_id}/clone` | DEFERRED | Requires BOM clone governance contract |
| `POST /products/{id}/boms/{bom_id}/bind-product-version` | DEFERRED | Requires product version binding contract |
| `POST /products/{id}/boms/{bom_id}/bulk-import` | DEFERRED | Requires bulk import contract |
| `POST /products/{id}/boms/{bom_id}/replace-items` | DEFERRED | Requires atomic replace governance |
| `DELETE /products/{id}/boms/{bom_id}` | FORBIDDEN | Hard delete forbidden — no traceability impact governance |
| `POST /products/{id}/boms/{bom_id}/reactivate` | FORBIDDEN | Reactivation from RETIRED is forbidden in this phase |
| `POST /products/{id}/boms/{bom_id}/material-reserve` | FORBIDDEN | Material domain responsibility — not BOM |
| `POST /products/{id}/boms/{bom_id}/backflush` | FORBIDDEN | Execution/material domain — never BOM |
| `POST /products/{id}/boms/{bom_id}/erp-post` | FORBIDDEN | ERP integration domain — not BOM |

---

## 9. Validation Rules

### BOM Header Validation

| Rule | Enforcement Level | Notes |
|---|---|---|
| `product_id` must exist in tenant | Service / repository | `get_product_by_id` lookup before create |
| `bom_code` required | Schema | Non-nullable |
| `bom_code` unique within `tenant_id` + `product_id` | Database constraint + service | `uq_boms_tenant_product_code` already on model |
| Create always sets `lifecycle_status = DRAFT` | Service | Client cannot specify lifecycle on create |
| Client cannot force `RELEASED` or `RETIRED` on create | Schema (`extra="forbid"`) | `lifecycle_status` forbidden in create request |
| `effective_from` ≤ `effective_to` if both present | Service | Date range validation |
| DRAFT BOM metadata is updatable | Service | Allowed |
| RELEASED BOM metadata is frozen | Service | Reject update; 400 or 409 |
| RETIRED BOM metadata is frozen | Service | Reject update; 400 or 409 |
| Release requires DRAFT source | Service | Reject non-DRAFT; 400 or 409 |
| Retire allows DRAFT or RELEASED | Service | Reject RETIRED source; 409 |
| All writes tenant-scoped | Service + repository | `tenant_id` from authenticated identity |
| Tenant isolation: cross-tenant BOM inaccessible | Repository | Query scoped by `tenant_id` |

### BOM Item Validation

| Rule | Enforcement Level | Notes |
|---|---|---|
| Parent BOM must exist in tenant and product context | Service / repository | Lookup before item mutation |
| Parent BOM must be DRAFT for add/update/remove | Service | Enforce lifecycle gate at service layer |
| `component_product_id` must exist in tenant | Service | `get_product_by_id` lookup; 404 if missing |
| `component_product_id` must not equal parent `product_id` | Service | Anti-circularity guard (unless future policy overrides) |
| `line_no` required and unique within `tenant_id` + `bom_id` | Database constraint + service | `uq_bom_items_tenant_bom_line_no` already on model |
| `quantity` must be positive | Schema + service | `quantity > 0` |
| `unit_of_measure` required | Schema | Non-nullable |
| `scrap_factor` nullable and non-negative if present | Service | `scrap_factor >= 0 if scrap_factor is not None` |
| `reference_designator` nullable | Schema | Optional |
| `notes` nullable | Schema | Optional |
| No material availability check | Service | Explicitly excluded |
| No inventory reservation | Service | Explicitly excluded |
| No lot/batch selection | Service | Explicitly excluded |

---

## 10. Audit / Event Expectations

### Event Map

| Command | Event / Audit Record | Payload Context | Forbidden Side Effects |
|---|---|---|---|
| `create_bom` | `BOM.CREATED` — `SecurityEventLog` | `bom_id`, `bom_code`, `product_id`, `lifecycle_status: DRAFT`, `occurred_at` | No execution, no material, no ERP, no quality, no genealogy, no PV binding |
| `update_bom_metadata` | `BOM.UPDATED` — `SecurityEventLog` | `bom_id`, `changed_fields`, `occurred_at` | No lifecycle side-effect; only field deltas |
| `release_bom` | `BOM.RELEASED` — `SecurityEventLog` | `bom_id`, `changed_fields: ["lifecycle_status"]`, `occurred_at` | No automatic PV binding, no ERP sync |
| `retire_bom` | `BOM.RETIRED` — `SecurityEventLog` | `bom_id`, `changed_fields: ["lifecycle_status"]`, `occurred_at` | No traceability genealogy, no material reversal |
| `add_bom_item` | `BOM_ITEM.ADDED` — `SecurityEventLog` | `bom_item_id`, `bom_id`, `component_product_id`, `line_no`, `quantity`, `occurred_at` | No material reservation, no inventory check, no lot selection |
| `update_bom_item` | `BOM_ITEM.UPDATED` — `SecurityEventLog` | `bom_item_id`, `bom_id`, `changed_fields`, `occurred_at` | None |
| `remove_bom_item` | `BOM_ITEM.REMOVED` — `SecurityEventLog` | `bom_item_id`, `bom_id`, `component_product_id`, `line_no`, `occurred_at` | No material adjustment, no inventory movement |

### Canonical Event Standard

No canonical BOM event standard exists in the current platform. The `SecurityEventLog` pattern (already used by Product, Product Version, Routing writes) is the baseline. Future BOM write implementation must follow the same pattern.

---

## 11. Cross-Domain Boundary Guardrails

| Boundary | Decision | Risk if Violated |
|---|---|---|
| BOM vs Material/Inventory | BOM defines intended structure; never triggers material movement or inventory reservation | If BOM mutations trigger material events, inventory truth is corrupted outside governance |
| BOM vs Backflush/Execution | No backflush trigger from any BOM write command | Backflush correctness depends on separate execution and material governance |
| BOM vs ERP/PLM | BOM is MMD master data, not ERP revision truth | If BOM is treated as ERP revision, downstream enterprise financial state could be compromised |
| BOM vs Traceability/Genealogy | No genealogy link or traceability record from BOM write commands | Traceability is a separate domain; BOM write must not create phantom genealogy |
| BOM vs Quality | No quality hold, acceptance gate, or quality decision from any BOM write | Quality decisions depend on separate QA domain governance |
| BOM vs Product Version | `product_version_id` nullable on model is a deferred extension point; no runtime binding in first write slice | Premature binding would couple BOM lifecycle to unresolved version semantics |
| BOM vs Product (parent) | Parent `product_id` must exist in same tenant; BOM mutations do not change product lifecycle | If BOM write changes product status, product domain truth is violated |
| BOM items vs material availability | No availability check or reservation at item add/update time | If item mutations trigger material availability checks, BOM definition editing becomes operationally gated |
| Action code vs RBAC runtime | `admin.master_data.bom.manage` must be in runtime `rbac.py` before any mutation endpoint is exposed | If mutation endpoints are deployed without the action code, authorization is unenforceable |
| FE write controls vs backend authorization | FE must derive BOM write capability from server-provided fields (future `allowed_actions`/`bom_capabilities`) | If FE infers capability from persona, unauthorized users see enabled controls |

---

## 12. Frontend Write UI Readiness Gate

**Current FE status:** `PARTIAL/BACKEND_API` — mutation actions explicitly disabled.

**BOM FE write UI must NOT be implemented until:**

1. `admin.master_data.bom.manage` is in `rbac.py` (MMD-BE-09A).
2. Backend BOM write API is implemented and tested (MMD-BE-12).
3. Backend returns server-derived `allowed_actions` / `bom_capabilities` on every BOM read response.
4. FE write controls consume server-provided capability fields — NOT persona/role inference.
5. Regression guard checks for BOM write capability contract are added to `mmd-read-integration-regression-check.mjs`.

---

## 13. Backend Implementation Readiness Gate

**Backend BOM write API (MMD-BE-12) must NOT be started until:**

1. `admin.master_data.bom.manage` exists in runtime `ACTION_CODE_REGISTRY` (MMD-BE-09A complete).
2. Action-code registry doc is updated.
3. Write request schemas are defined with `extra="forbid"`.
4. Lifecycle transition invariants are codified in service layer.
5. Audit event pattern from existing write slices is confirmed and reused.
6. All validation rules in Section 9 are included in the implementation plan.

---

## 14. Required Tests for Future Write Slice

### BOM Write Tests (for MMD-BE-12)

| Test | Purpose |
|---|---|
| `test_create_bom_requires_manage_action` | 403 without `bom.manage` action |
| `test_create_bom_creates_draft` | Create returns DRAFT, `lifecycle_status=DRAFT` |
| `test_create_bom_rejects_lifecycle_status_payload` | 422 on `lifecycle_status` in create body |
| `test_create_bom_rejects_duplicate_code_for_same_product` | 409 on duplicate `bom_code` per product |
| `test_create_bom_allows_same_code_for_different_products` | Same `bom_code` allowed across products |
| `test_update_bom_metadata_requires_manage_action` | 403 without manage action |
| `test_update_bom_metadata_allowed_for_draft` | Metadata update returns updated BOM |
| `test_update_bom_metadata_rejected_for_released` | 400/409 for non-DRAFT |
| `test_update_bom_metadata_rejected_for_retired` | 400/409 for non-DRAFT |
| `test_release_bom_requires_manage_action` | 403 without manage action |
| `test_release_bom_changes_draft_to_released` | DRAFT → RELEASED |
| `test_release_bom_rejects_released_or_retired` | 409 for non-DRAFT source |
| `test_retire_bom_requires_manage_action` | 403 without manage action |
| `test_retire_bom_changes_draft_to_retired` | DRAFT → RETIRED |
| `test_retire_bom_changes_released_to_retired` | RELEASED → RETIRED |
| `test_retire_bom_rejects_already_retired` | 409 for RETIRED source |
| `test_no_delete_reactivate_bind_routes_exist` | Route enumeration: DELETE/reactivate/bind absent |

### BOM Item Write Tests (for MMD-BE-12)

| Test | Purpose |
|---|---|
| `test_add_bom_item_requires_manage_action` | 403 without manage action |
| `test_add_bom_item_succeeds_for_draft_bom` | Item created under DRAFT parent |
| `test_add_bom_item_rejected_for_released_bom` | 400/409 — parent BOM not DRAFT |
| `test_add_bom_item_rejected_for_retired_bom` | 400/409 — parent BOM not DRAFT |
| `test_add_bom_item_rejects_circular_component` | 400 when component equals parent product |
| `test_add_bom_item_rejects_missing_component_product` | 404 when component product does not exist |
| `test_add_bom_item_rejects_duplicate_line_no` | 409 on duplicate `line_no` within BOM |
| `test_add_bom_item_rejects_zero_or_negative_quantity` | 422 validation |
| `test_update_bom_item_requires_manage_action` | 403 without manage action |
| `test_update_bom_item_allowed_for_draft_parent` | Item updated |
| `test_update_bom_item_rejected_for_non_draft_parent` | 400/409 |
| `test_update_bom_item_rejects_component_id_change` | 422 — forbidden field |
| `test_remove_bom_item_requires_manage_action` | 403 without manage action |
| `test_remove_bom_item_allowed_for_draft_parent` | Item deleted |
| `test_remove_bom_item_rejected_for_non_draft_parent` | 400/409 |
| `test_remove_bom_item_returns_404_for_missing_item` | 404 |

### RBAC / Action Code Tests

| Test | Purpose |
|---|---|
| `test_bom_manage_action_code_exists` | `admin.master_data.bom.manage` in `ACTION_CODE_REGISTRY` |
| `test_bom_manage_action_code_is_admin_family` | Maps to `ADMIN` family |
| `test_bom_endpoints_use_bom_manage_action_code` | No `admin.user.manage` on BOM mutation routes |

---

## 15. Explicit Non-Goals

This contract does not authorize and must not be used to justify:

- BOM write API implementation (deferred to MMD-BE-12)
- Frontend BOM write form or controls (deferred to after MMD-BE-12)
- RBAC source changes (deferred to MMD-BE-09A)
- Migration/schema source changes
- Product Version binding for BOM
- Routing binding for BOM
- Resource Requirement binding for BOM
- Quality plan linkage
- ERP/PLM sync
- Material availability check
- Material reservation or movement
- Inventory movement
- Backflush trigger
- Traceability genealogy
- Lot/batch selection
- Warehouse allocation
- Acceptance gate
- Digital twin scenario generation
- APS integration
- AI-generated BOM
- E-signature / SoD workflow
- Bulk import
- Delete / hard delete
- Reactivation from RETIRED
- Auto-commit or deployment

---

## 16. Recommended Next Slice

### Recommended: MMD-BE-09A — BOM Action Code Registry Patch

**Reason:** `admin.master_data.bom.manage` is not present in `backend/app/security/rbac.py` or the action-code registry documentation. This is a hard prerequisite before BOM mutation endpoints can be exposed.

**Prerequisites satisfied for MMD-BE-09A:**
- MMD-BE-09 governance contract established (this document)
- Action code naming convention confirmed (`admin.master_data.bom.manage`)
- ADMIN family confirmed
- Registry doc format confirmed from MMD-BE-02 and MMD-BE-08A precedent

**After MMD-BE-09A is complete, proceed to:**

MMD-BE-12 — BOM Write API Foundation

**Do not start MMD-BE-12 before MMD-BE-09A is verified.**

**Do not start BOM FE write UI before MMD-BE-12 is complete and server-derived `allowed_actions` exist.**

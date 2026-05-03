# MMD-BE-09 — BOM Write Governance / Minimal Mutation Contract Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Created BOM write governance contract before mutation implementation. |

---

## Routing
- **Selected brain:** MOM Brain
- **Selected mode:** Backend command-boundary design mode + Authorization/action-code governance mode + Lifecycle governance mode + Architecture boundary guardian mode + Source audit/evidence mode + Critical reviewer mode
- **Hard Mode MOM:** v3 ON
- **Reason:** BOM write-path changes MMD manufacturing definition truth. Confusion with material consumption, inventory movement, backflush, ERP posting, traceability genealogy, quality acceptance, and execution confirmation is a real risk. Full Hard Mode MOM v3 evidence required before document creation.

---

## 1. Scope

Documentation-only governance slice. No runtime source changes.

**Purpose:**
- Define the BOM write command boundary before any BOM mutation API is implemented
- Lock lifecycle transition governance
- Lock authorization / action-code requirements
- Propose future API contract
- Define validation rules
- Define audit/event expectations
- Establish boundary guardrails
- Classify all deferred and forbidden commands
- Recommend next implementation slice

**Out of scope:** All runtime implementation, migration, schema, RBAC changes, test changes, and frontend changes.

---

## 2. Baseline Evidence Used

### Mandatory inputs reviewed

| Document | Status | Key Finding |
|---|---|---|
| `docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md` | ✅ Inspected | BOM read baseline frozen; 105 regression checks passing |
| `docs/audit/mmd-write-gov-01-command-boundary.md` | ✅ Inspected | BOM classified `DEFERRED_REQUIRES_CONTRACT`; no action code |
| `docs/audit/mmd-pv-write-baseline-01-product-version-write-freeze-handoff.md` | ✅ Inspected | PV write frozen; precedent for lifecycle governance and capability projection |
| `docs/audit/mmd-be-04-bom-foundation-contract-boundary-lock.md` | ✅ Inspected | `product_version_id` deferred; product-scoped first slice confirmed |
| `docs/audit/mmd-be-05-bom-minimal-read-model.md` | ✅ Inspected | BOM read model, migration, and service confirmed implemented |
| `docs/audit/mmd-fullstack-07-bom-fe-read-integration.md` | ✅ Inspected | FE screens PARTIAL/BACKEND_API; mutation disabled |
| `docs/audit/mmd-be-02-rbac-action-code-fix.md` | ✅ Inspected | MMD action code pattern confirmed (`admin.master_data.{entity}.manage`) |

### Optional inputs reviewed

| Document | Status | Key Finding |
|---|---|---|
| `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md` | ✅ Inspected | BOM write state `DEFERRED_REQUIRES_CONTRACT` confirmed |
| `docs/design/02_domain/product_definition/bom-foundation-contract.md` | ✅ Inspected | Entity contract, field list, lifecycle values confirmed |
| `docs/design/02_domain/product_definition/product-version-write-governance-contract.md` | ✅ Inspected | PV write contract used as structural template |
| `docs/design/02_registry/action-code-registry.md` | ✅ Inspected | `admin.master_data.bom.manage` NOT listed — ABSENT |
| `docs/design/00_platform/product-business-truth-overview.md` | ✅ Inspected | BOM is MMD definition truth, not ERP revision truth confirmed |

---

## 3. Source Inspection Summary

### Backend

| File | Finding |
|---|---|
| `backend/app/models/bom.py` | `Bom` model: `bom_id`, `tenant_id`, `product_id`, `bom_code`, `bom_name`, `lifecycle_status` (default DRAFT), `effective_from`, `effective_to`, `description`, `created_at`, `updated_at`. **No `product_version_id` field.** `BomItem` model with all required item fields. |
| `backend/app/schemas/bom.py` | Read schemas only: `BomComponentItem`, `BomItem`, `BomDetail`. No write request schemas. `_ALLOWED_BOM_LIFECYCLE_STATUSES = {"DRAFT", "RELEASED", "RETIRED"}` defined. |
| `backend/app/repositories/bom_repository.py` | Read functions only: `list_boms_by_product`, `get_bom_by_id`. No write repository functions. |
| `backend/app/services/bom_service.py` | Read functions only: `_to_component_item`, `_to_bom_item`, `_to_bom_detail`, `list_boms`, `get_bom`. No write service functions. |
| `backend/app/api/v1/products.py` | BOM routes: `GET /{product_id}/boms` and `GET /{product_id}/boms/{bom_id}` only. **No POST, PATCH, or DELETE BOM routes.** |
| `backend/app/security/rbac.py` | Lines 58–61: `admin.master_data.product.manage`, `admin.master_data.product_version.manage`, `admin.master_data.routing.manage`, `admin.master_data.resource_requirement.manage`. **`admin.master_data.bom.manage` ABSENT.** |
| `backend/alembic/versions/0008_boms.py` | Comment explicitly states: "No product_version_id on boms in this revision." |

### Frontend

| File | Finding |
|---|---|
| `frontend/src/app/pages/BomList.tsx` | Read-only; product selection + BOM list display; note: "BOM component truth is loaded from backend MMD API. All create/edit/release/retire actions require backend connection." |
| `frontend/src/app/pages/BomDetail.tsx` | Read-only; no write controls active; mutation actions disabled |
| `frontend/src/app/screenStatus.ts` | `bomList: { phase: "PARTIAL", dataSource: "BACKEND_API", notes: "Mutation actions remain disabled." }`, `bomDetail: { phase: "PARTIAL", dataSource: "BACKEND_API", notes: "Mutation actions remain disabled." }` |
| `frontend/src/app/api/productApi.ts` | BOM read types only: `BomItemFromAPI`, `BomComponentItemFromAPI`, `BomFromAPI`. No write request types. |

### Existing BOM Tests

| Test File | Tests | Key Guards |
|---|---|---|
| `test_bom_foundation_api.py` | 11 tests | `test_bom_routes_do_not_expose_write_methods`, `test_bom_api_has_no_post_patch_delete_routes`, `test_bom_model_has_no_backflush_or_erp_fields`, `test_bom_model_has_no_inventory_movement_fields` |
| `test_bom_foundation_service.py` | 9 tests | `test_lifecycle_status_values_are_stable`, `test_bom_model_does_not_include_product_version_binding` |
| `test_mmd_rbac_action_codes.py` | No BOM code test (yet) | `admin.master_data.bom.manage` absent from registry — no existing test confirms or denies |

### No Stop Conditions Triggered

| Stop Condition | Status |
|---|---|
| BOM foundation contract missing | ✅ Present |
| BOM read model/source cannot be inspected | ✅ Inspected |
| BOM foundation contract conflicts with this prompt | ✅ Consistent |
| Current BOM source already has hidden write APIs | ✅ Confirmed absent |
| Action-code source cannot be inspected | ✅ Inspected; `bom.manage` confirmed absent |
| BOM write governance would require immediate runtime source changes | ✅ This slice is documentation-only |
| Unresolved merge conflicts | ✅ None detected |

---

## 4. BOM Write Decisions

| Command | Decision | Reason | Future Guardrails |
|---|---|---|---|
| `create_bom` | **READY_FOR_IMPLEMENTATION_NEXT** | Read model proven; lifecycle values defined; tenant scoping established | `extra="forbid"` on write schema; lifecycle_status forbidden in request; unique bom_code per product |
| `update_bom_metadata` (DRAFT only) | **READY_FOR_IMPLEMENTATION_NEXT** | DRAFT state is reversible; field set is clear | Service must reject non-DRAFT; schema forbids lifecycle_status field |
| `release_bom` | **READY_FOR_IMPLEMENTATION_NEXT** | DRAFT→RELEASED transition follows Product/Routing/PV precedent | Service rejects non-DRAFT; audit record required; no PV binding side-effect |
| `retire_bom` | **READY_FOR_IMPLEMENTATION_NEXT** | DRAFT→RETIRED and RELEASED→RETIRED follow PV precedent | Service rejects RETIRED source; audit record required |
| `delete_bom` | **FORBIDDEN** | No delete governance; potential historical reference; traceability risk | Hard reject at route level; absence test required |
| `reactivate_bom` | **FORBIDDEN** | RETIRED is terminal in this phase | Hard reject at route level; absence test required |
| `clone_bom` | **DEFERRED_REQUIRES_CONTRACT** | BOM versioning and item lineage semantics not yet governed | Requires dedicated governance contract |
| `copy_from_existing_bom` | **DEFERRED_REQUIRES_CONTRACT** | Same as clone | Same |
| `bind_to_product_version` | **DEFERRED_REQUIRES_CONTRACT** | `product_version_id` is nullable extension point only; binding contract does not exist | Hard reject if attempted before contract |
| `unbind_from_product_version` | **NOT_APPLICABLE** | Binding not implemented | N/A |
| `bulk_import_bom` | **DEFERRED_REQUIRES_CONTRACT** | Bulk validation semantics not established | Dedicated contract required |
| `bulk_retire_bom` | **DEFERRED_REQUIRES_CONTRACT** | Bulk lifecycle semantics not established | Same |

---

## 5. BOM Item Write Decisions

| Command | Decision | Reason | Future Guardrails |
|---|---|---|---|
| `add_bom_item` (parent DRAFT) | **READY_FOR_IMPLEMENTATION_NEXT** | Item model, fields, and constraints proven; parent DRAFT gate is clear | Service verifies parent DRAFT; component existence; circularity guard; line_no uniqueness; quantity > 0 |
| `update_bom_item` (parent DRAFT) | **READY_FOR_IMPLEMENTATION_NEXT** | Mutation is safe while parent is DRAFT | Service verifies parent DRAFT; component_product_id and line_no are immutable |
| `remove_bom_item` (parent DRAFT) | **READY_FOR_IMPLEMENTATION_NEXT** | Removal safe while parent DRAFT; no material side-effect | Service verifies parent DRAFT |
| `reorder_bom_items` | **DEFERRED_REQUIRES_CONTRACT** | `line_no` resequencing could affect historical item identity | line_no semantics review required |
| `bulk_add_items` | **DEFERRED_REQUIRES_CONTRACT** | Bulk validation and rollback semantics not established | Dedicated contract |
| `bulk_remove_items` | **DEFERRED_REQUIRES_CONTRACT** | Same | Same |
| `replace_all_items` | **DEFERRED_REQUIRES_CONTRACT** | Atomic replace semantics and audit trail for removed items not governed | Requires governance contract |

---

## 6. Lifecycle Transition Decisions

| Transition | Decision | Reason |
|---|---|---|
| `(new) → DRAFT` | **ALLOW_NEXT** | Create always sets DRAFT; client cannot override |
| `DRAFT → RELEASED` | **ALLOW_NEXT** | Explicit release command; follows Product/Routing/PV precedent |
| `DRAFT → RETIRED` | **ALLOW_NEXT** | BOM retired before release; permissible if never used |
| `RELEASED → RETIRED` | **ALLOW_NEXT** | Superseded BOMs must be retirable |
| `RELEASED → DRAFT` | **FORBID** | BOM exposed to planning reads; rollback unsafe without governance |
| `RETIRED → RELEASED` | **FORBID** | RETIRED is terminal in this phase |
| `RETIRED → DRAFT` | **FORBID** | RETIRED is terminal in this phase |

### BOM Item Lifecycle Rule

BOM Items have no independent lifecycle. Item mutations (add/update/remove) are gated by parent BOM `lifecycle_status = DRAFT`. Service layer must enforce this — route layer alone is insufficient.

---

## 7. Authorization / Action-Code Decisions

### Key Finding

`admin.master_data.bom.manage` is **ABSENT** from `backend/app/security/rbac.py` (lines 58–61 confirmed).

It is also absent from `docs/design/02_registry/action-code-registry.md`.

### Decisions

| Decision | Verdict |
|---|---|
| Code to use | `admin.master_data.bom.manage` |
| Permission Family | `ADMIN` |
| Must be added before BOM write API | **YES — hard prerequisite** |
| Separate slice for code addition | **YES — MMD-BE-09A** |
| All mutation endpoints require this code | **YES — create, update, release, retire, add/update/remove item** |
| Read endpoints remain `require_authenticated_identity` | **YES — unchanged** |
| Single code covers lifecycle transitions | **YES — coarse-grained MMD pattern** |
| Frontend route visibility is not authorization truth | **Confirmed** |

---

## 8. Future API Contract Proposal

### READY_FOR_IMPLEMENTATION_NEXT (for MMD-BE-12)

| Endpoint | Command | Auth | Source State | Target State |
|---|---|---|---|---|
| `POST /products/{id}/boms` | `create_bom` | `admin.master_data.bom.manage` | (new) | DRAFT |
| `PATCH /products/{id}/boms/{bom_id}` | `update_bom_metadata` | `admin.master_data.bom.manage` | DRAFT | DRAFT |
| `POST /products/{id}/boms/{bom_id}/release` | `release_bom` | `admin.master_data.bom.manage` | DRAFT | RELEASED |
| `POST /products/{id}/boms/{bom_id}/retire` | `retire_bom` | `admin.master_data.bom.manage` | DRAFT or RELEASED | RETIRED |
| `POST /products/{id}/boms/{bom_id}/items` | `add_bom_item` | `admin.master_data.bom.manage` | Parent DRAFT | item created |
| `PATCH /products/{id}/boms/{bom_id}/items/{item_id}` | `update_bom_item` | `admin.master_data.bom.manage` | Parent DRAFT | item updated |
| `DELETE /products/{id}/boms/{bom_id}/items/{item_id}` | `remove_bom_item` | `admin.master_data.bom.manage` | Parent DRAFT | item removed |

### DEFERRED

| Endpoint | Decision |
|---|---|
| `POST /products/{id}/boms/{bom_id}/clone` | DEFERRED — requires governance contract |
| `POST /products/{id}/boms/{bom_id}/bind-product-version` | DEFERRED — requires PV binding contract |
| `POST /products/{id}/boms/{bom_id}/bulk-import` | DEFERRED — requires bulk contract |
| `POST /products/{id}/boms/{bom_id}/replace-items` | DEFERRED — requires atomic replace governance |

### FORBIDDEN

| Endpoint | Decision |
|---|---|
| `DELETE /products/{id}/boms/{bom_id}` | FORBIDDEN — no delete governance; route must be absent |
| `POST /products/{id}/boms/{bom_id}/reactivate` | FORBIDDEN — RETIRED is terminal |
| `POST /products/{id}/boms/{bom_id}/material-reserve` | FORBIDDEN — material domain |
| `POST /products/{id}/boms/{bom_id}/backflush` | FORBIDDEN — execution domain |
| `POST /products/{id}/boms/{bom_id}/erp-post` | FORBIDDEN — ERP integration domain |

---

## 9. Audit / Event Expectations

| Command | Audit Record | Forbidden Side Effects |
|---|---|---|
| `create_bom` | `BOM.CREATED` → `SecurityEventLog` | No execution, material, ERP, quality, genealogy, PV binding |
| `update_bom_metadata` | `BOM.UPDATED` → `SecurityEventLog` | No lifecycle side-effect |
| `release_bom` | `BOM.RELEASED` → `SecurityEventLog` | No automatic PV binding, no ERP sync |
| `retire_bom` | `BOM.RETIRED` → `SecurityEventLog` | No traceability genealogy, no material reversal |
| `add_bom_item` | `BOM_ITEM.ADDED` → `SecurityEventLog` | No material reservation, no inventory check, no lot selection |
| `update_bom_item` | `BOM_ITEM.UPDATED` → `SecurityEventLog` | None |
| `remove_bom_item` | `BOM_ITEM.REMOVED` → `SecurityEventLog` | No material adjustment, no inventory movement |

**Canonical event standard:** No BOM-specific event standard exists. `SecurityEventLog` (used by Product, ProductVersion, Routing writes) is the established baseline pattern. Future BOM write implementation must follow the same pattern.

---

## 10. Boundary Guardrails

| Boundary | Decision | Risk if Violated |
|---|---|---|
| BOM vs Material/Inventory | No material movement or reservation from BOM write | Inventory truth corrupted outside governance |
| BOM vs Backflush/Execution | No backflush trigger from BOM write | Execution correctness depends on separate governance |
| BOM vs ERP/PLM | BOM is MMD master data, not ERP revision truth | Enterprise financial state compromised |
| BOM vs Traceability/Genealogy | No genealogy link from BOM write | Phantom genealogy would compromise traceability integrity |
| BOM vs Quality | No quality hold or acceptance gate from BOM write | Quality decisions must come from QA domain |
| BOM vs Product Version | `product_version_id` nullable is a deferred extension point only | Premature binding couples BOM lifecycle to unresolved version semantics |
| BOM vs Product (parent) | Parent must exist in same tenant; BOM mutations do not change product lifecycle | Product domain truth violated |
| BOM items vs material availability | No availability check at item add/update time | BOM definition editing becomes operationally gated |
| Action code vs RBAC runtime | `admin.master_data.bom.manage` must be in `rbac.py` before mutation endpoints exposed | Authorization unenforceable at runtime |
| FE write controls vs backend authorization | FE must derive BOM capability from server-provided fields | Unauthorized users see enabled controls if FE infers |

---

## 11. Future Test Requirements

### RBAC / Action Code (MMD-BE-09A)
- `test_bom_manage_action_code_exists` — confirms `admin.master_data.bom.manage` in `ACTION_CODE_REGISTRY`
- `test_bom_manage_action_code_is_admin_family` — maps to `ADMIN` family
- `test_bom_endpoints_use_bom_manage_action_code` — no `admin.user.manage` on BOM mutation routes

### BOM Write (MMD-BE-12)
- 17 BOM header write tests (create, update, release, retire, forbidden routes)
- 16 BOM Item write tests (add, update, remove — parent state gates, forbidden states, validation)

Full test matrix defined in `docs/design/02_domain/product_definition/bom-write-governance-contract.md` Section 14.

---

## 12. Recommended Next Slice

### MMD-BE-09A — BOM Action Code Registry Patch

**Reason:** `admin.master_data.bom.manage` is not present in runtime `backend/app/security/rbac.py` or `docs/design/02_registry/action-code-registry.md`. This is a **hard prerequisite** — BOM mutation endpoints must require this code, but cannot use it until it exists in the registry.

**Prerequisites satisfied:**
- MMD-BE-09 governance contract established (this slice)
- Action code naming confirmed: `admin.master_data.bom.manage`
- ADMIN family confirmed
- Registry doc format confirmed from MMD-BE-02 and MMD-BE-08A precedent

**After MMD-BE-09A:**
- Proceed to **MMD-BE-12 — BOM Write API Foundation**

**Do not start MMD-BE-12 before MMD-BE-09A is verified.**

**Do not recommend BOM FE write UI before:**
- MMD-BE-12 is complete
- Server-derived `allowed_actions` / `bom_capabilities` are available on BOM read responses
- Regression guards for BOM capability contract are added to `mmd-read-integration-regression-check.mjs`

---

## 13. Verification / Diff

```powershell
cd g:\Work\FleziBCG
git diff -- docs/design/02_domain/product_definition/bom-write-governance-contract.md docs/audit/mmd-be-09-bom-write-governance-contract.md
git status --short
```

**Expected diff:** Two new files — `bom-write-governance-contract.md` and `mmd-be-09-bom-write-governance-contract.md`.

**Expected changed runtime files:** None. No runtime source, migration, schema, test, or frontend file is modified by this slice.

---

## 14. Final Verdict

**GOVERNANCE CONTRACT ESTABLISHED — DOCUMENTATION-ONLY SLICE COMPLETE.**

All classification decisions made:

| Area | Status |
|---|---|
| BOM write command classification (12 commands) | ✅ All classified |
| BOM Item write command classification (7 commands) | ✅ All classified |
| Lifecycle transition matrix | ✅ All transitions governed |
| Authorization / action-code decision | ✅ `admin.master_data.bom.manage` — ABSENT, must be added in MMD-BE-09A |
| Future API contract proposal | ✅ 7 READY endpoints + DEFERRED + FORBIDDEN |
| Validation rules (BOM header + BOM Item) | ✅ Defined |
| Audit/event expectations (7 commands) | ✅ Defined |
| Cross-domain boundary guardrails (10 boundaries) | ✅ Defined |
| Backend implementation readiness gate | ✅ Defined |
| Frontend write UI readiness gate | ✅ Defined |
| Future test requirements (36 tests) | ✅ Defined |
| Recommended next slice | ✅ MMD-BE-09A — BOM Action Code Registry Patch |
| Runtime source modified | ✅ None |
| Migration modified | ✅ None |
| Tests modified | ✅ None |
| Frontend runtime modified | ✅ None |
| Auto-commit performed | ✅ None |

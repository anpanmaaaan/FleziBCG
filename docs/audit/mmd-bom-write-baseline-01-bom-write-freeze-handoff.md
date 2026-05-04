# MMD-BOM-WRITE-BASELINE-01 — BOM Write Baseline Freeze / Handoff

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-04 | v1.0 | Frozen BOM write baseline after backend write API, action code registry, boundary audit, frontend write intent, server-derived capability guard, verification hardening, and read-auth test harness alignment. |

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Full-stack baseline freeze mode + Source audit / evidence mode + Authorization / capability projection review mode + Hard Mode MOM v3 mode + Critical reviewer mode
- **Hard Mode MOM:** v3 ON
- **Reason:** This freeze captures BOM write behavior, authorization, lifecycle transitions, and boundary guardrails before expanding to Reason Codes, Product Version binding, material/backflush, ERP, or traceability. Hard Mode MOM v3 is mandatory per copilot-instructions.md for any slice freezing BOM write-path, lifecycle, and authorization invariants.

---

## 1. Scope

This baseline freeze documents the completed state of BOM write governance, backend write API, frontend write intent, server-derived capability guard, and verification hardening across slices:

| Slice | Type | Status |
|---|---|---|
| MMD-BE-09 — BOM Write Governance / Minimal Mutation Contract | Documentation governance | ✅ Complete |
| MMD-BE-09A — BOM Action Code Registry Patch | Backend registry patch | ✅ Complete |
| MMD-BE-12 — BOM Write API Foundation | Backend API implementation | ✅ Complete |
| MMD-BE-12A — BOM Write Boundary Audit / Event Guardrail Patch | Backend QA audit | ✅ Complete |
| MMD-FULLSTACK-12 — BOM FE Write Intent / Governance-Gated Integration | Frontend write intent | ✅ Complete |
| MMD-FULLSTACK-12B — BOM Server-Derived Write Capability Guard | FE + BE capability projection | ✅ Complete |
| MMD-FULLSTACK-12B-A — BOM Capability Guard Verification Completion | Verification hardening | ✅ Complete |
| MMD-FULLSTACK-12B-B — BOM Capability Read Auth Test Harness Alignment | Test harness alignment | ✅ Complete |

**Not in scope:** New BOM commands, Product Version binding, material/backflush/ERP/traceability/quality, execution state machine, new frontend screens, DB migrations, runtime source changes.

---

## 2. Baseline Inputs Reviewed

| Document | Status | Key Finding |
|---|---|---|
| `docs/audit/mmd-be-09-bom-write-governance-contract.md` | ✅ Inspected | BOM write governance contract: 4 header commands + 3 item commands; lifecycle DRAFT→RELEASED→RETIRED; action code `admin.master_data.bom.manage` proposed; all boundary guardrails defined. |
| `docs/audit/mmd-be-09a-bom-action-code-registry-patch.md` | ✅ Inspected | `admin.master_data.bom.manage` registered at `rbac.py:62`. BOM read endpoints confirmed as not requiring this action code. |
| `docs/audit/mmd-be-12-bom-write-api-foundation.md` | ✅ Inspected | 7 governed write endpoints implemented; all use `require_action("admin.master_data.bom.manage")`; `extra="forbid"` on all write schemas; no forbidden fields. |
| `docs/audit/mmd-be-12a-bom-write-boundary-guardrail.md` | ✅ Inspected | Boundary audit clean: no product_version_id, no material/backflush/ERP/traceability; 7 allowed events confirmed. |
| `docs/audit/mmd-fullstack-12-bom-fe-write-intent.md` | ✅ Inspected | FE write-intent API helpers, create gating on BomList, lifecycle-plausible controls on BomDetail. |
| `docs/audit/mmd-fullstack-12b-bom-server-derived-capability-guard.md` | ✅ Inspected | ProductBomCapabilities (can_create) and BomAllowedActions (7 fields) added to BE schemas and FE types; FE migrated from local lifecycle inference to server-derived capability consumption. |
| `docs/audit/mmd-fullstack-12b-a-bom-capability-guard-verification.md` | ✅ Inspected | 109 backend tests passing; 134 frontend checks; build/lint/i18n/routes all pass. |
| `docs/audit/mmd-fullstack-12b-b-bom-capability-read-auth-test-alignment.md` | ✅ Inspected | Test harness aligned; 100 BOM-related backend tests, 134 frontend checks, route gate pass. |
| `docs/audit/mmd-write-gov-01-command-boundary.md` | ✅ Inspected | BOM classified `DEFERRED_REQUIRES_CONTRACT` at write-gov-01 baseline; now promoted to implemented. |
| `docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md` | ✅ Inspected | Read baseline frozen; 105 regression checks (pre-write). BOM read model confirmed stable. |

### Design Documents Inspected

| Document | Status | Key Finding |
|---|---|---|
| `docs/design/02_domain/product_definition/bom-write-governance-contract.md` | ✅ Inspected | Lifecycle state machine, validation rules, audit event expectations, boundary guardrails — all align with implemented behavior. |
| `docs/design/02_domain/product_definition/bom-foundation-contract.md` | ✅ Inspected | No `product_version_id` in this revision. Product-scoped BOM. |
| `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md` | ✅ Inspected | BOM state was `DEFERRED_REQUIRES_CONTRACT`; now implemented through BE-09 through FULLSTACK-12B-B. |
| `docs/design/02_registry/action-code-registry.md` | ✅ Inspected | `admin.master_data.bom.manage` entry confirmed present after MMD-BE-09A. |
| `docs/design/00_platform/product-business-truth-overview.md` | ✅ Inspected | BOM is MMD definition truth, not ERP revision truth. No inventory/ERP coupling. |

---

## 3. Source Inspection Summary

### Backend

| File | Inspected | Key Finding |
|---|---|---|
| `backend/app/security/rbac.py` | ✅ | `admin.master_data.bom.manage` at line 62 — present, family ADMIN. |
| `backend/app/schemas/bom.py` | ✅ | BomCreateRequest, BomUpdateRequest, BomItemCreateRequest, BomItemUpdateRequest all `extra="forbid"`. `lifecycle_status`, `product_version_id` absent. `BomAllowedActions` (7 fields) and `BomComponentItem` confirmed. |
| `backend/app/schemas/product.py` | ✅ | `ProductBomCapabilities(can_create: bool)` present in `ProductItem`. `ProductItem.bom_capabilities` confirmed. |
| `backend/app/repositories/bom_repository.py` | ✅ | Pure CRUD; no forbidden domain side effects. |
| `backend/app/services/bom_service.py` | ✅ | `_compute_allowed_actions(has_manage, lifecycle_status)` implements all 6 branches correctly. 7 write service functions confirmed. |
| `backend/app/services/product_service.py` | ✅ | `has_bom_manage_permission` param passed through; `bom_capabilities.can_create` derived from this param. |
| `backend/app/api/v1/products.py` | ✅ | Read BOM endpoints: `require_authenticated_identity` + `has_action(...)`. Write BOM endpoints: all 7 use `require_action("admin.master_data.bom.manage")`. BOM write section clearly marked `# ─── BOM write endpoints — MMD-BE-12`. |
| `backend/tests/test_bom_foundation_api.py` | ✅ | 44 tests; harness patched in 12B-B for RBAC lookup support. |
| `backend/tests/test_bom_foundation_service.py` | ✅ | 22 tests covering service logic. |
| `backend/tests/test_mmd_rbac_action_codes.py` | ✅ | 24 tests; includes `admin.master_data.bom.manage` action code tests. |
| `backend/tests/test_bom_capability_guard_12b_a.py` | ✅ | 4 tests — product-level `bom_capabilities` presence and value. |
| `backend/tests/test_bom_allowed_actions_12b_a.py` | ✅ | 6 tests — `allowed_actions` matrix for DRAFT/RELEASED/RETIRED + manage/non-manage. |

### Frontend

| File | Inspected | Key Finding |
|---|---|---|
| `frontend/src/app/api/productApi.ts` | ✅ | `ProductBomCapabilities`, `BomAllowedActions` (7 fields), `BomItemFromAPI`, `BomFromAPI` types present. `BomItemFromAPI.allowed_actions: BomAllowedActions` confirmed. `ProductItemFromAPI.bom_capabilities: ProductBomCapabilities` confirmed. |
| `frontend/src/app/api/index.ts` | ✅ | `productApi` exported. |
| `frontend/src/app/pages/BomList.tsx` | ✅ | `canCreateBom = selectedProduct?.bom_capabilities?.can_create ?? false` — server-derived. No persona-based gating. |
| `frontend/src/app/pages/BomDetail.tsx` | ✅ | All 6 write-control flags derived from `bom?.allowed_actions.*`. No lifecycle-only inference. |
| `frontend/src/app/screenStatus.ts` | ✅ | `bomList` and `bomDetail`: `phase: "PARTIAL"`, `dataSource: "BACKEND_API"`. **Known notes gap**: notes still say "Mutation actions remain disabled" — outdated after FULLSTACK-12. Non-blocking; phase/dataSource are accurate. |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | ✅ | J1–J12 checks cover BOM capability guard; total 134 checks. |
| `frontend/src/app/i18n/registry/en.ts` | ✅ | `bomWrite.*` keys present including error, success, confirm namespaces. |
| `frontend/src/app/i18n/registry/ja.ts` | ✅ | `bomWrite.*` keys synchronized with en.ts. |
| `frontend/src/app/i18n/namespaces.ts` | ✅ | `bomWrite` namespace registered. |

---

## 4. Implemented BOM Write Baseline

### 9.1 Implemented BOM Command Matrix

| Command | Backend Route | FE Control | Auth | Lifecycle Rule | Status |
|---|---|---|---|---|---|
| create BOM | `POST /api/v1/products/{product_id}/boms` | BomList create form (enabled by `bom_capabilities.can_create`) | `admin.master_data.bom.manage` | Creates as DRAFT | ✅ Implemented |
| update BOM metadata | `PATCH /api/v1/products/{product_id}/boms/{bom_id}` | BomDetail edit metadata panel (enabled by `allowed_actions.can_update`) | `admin.master_data.bom.manage` | DRAFT only | ✅ Implemented |
| release BOM | `POST /api/v1/products/{product_id}/boms/{bom_id}/release` | BomDetail release button (enabled by `allowed_actions.can_release`) | `admin.master_data.bom.manage` | DRAFT → RELEASED | ✅ Implemented |
| retire BOM | `POST /api/v1/products/{product_id}/boms/{bom_id}/retire` | BomDetail retire button (enabled by `allowed_actions.can_retire`) | `admin.master_data.bom.manage` | DRAFT or RELEASED → RETIRED | ✅ Implemented |

---

## 5. Implemented BOM Item Write Baseline

### 9.2 Implemented BOM Item Command Matrix

| Command | Backend Route | FE Control | Auth | Parent State Rule | Status |
|---|---|---|---|---|---|
| add BOM Item | `POST /api/v1/products/{product_id}/boms/{bom_id}/items` | BomDetail add item form (enabled by `allowed_actions.can_add_item`) | `admin.master_data.bom.manage` | Parent BOM must be DRAFT | ✅ Implemented |
| update BOM Item | `PATCH /api/v1/products/{product_id}/boms/{bom_id}/items/{bom_item_id}` | BomDetail item edit inline (enabled by `allowed_actions.can_update_item`) | `admin.master_data.bom.manage` | Parent BOM must be DRAFT | ✅ Implemented |
| remove BOM Item | `DELETE /api/v1/products/{product_id}/boms/{bom_id}/items/{bom_item_id}` | BomDetail item remove button (enabled by `allowed_actions.can_remove_item`) | `admin.master_data.bom.manage` | Parent BOM must be DRAFT | ✅ Implemented |

---

## 6. Backend API Baseline

### BOM Read Endpoints

| Method | Path | Auth | Response | Status |
|---|---|---|---|---|
| GET | `/api/v1/products/{product_id}/boms` | `require_authenticated_identity` + `has_action(bom.manage)` for capability | `list[BomItem]` with `allowed_actions` | ✅ |
| GET | `/api/v1/products/{product_id}/boms/{bom_id}` | `require_authenticated_identity` + `has_action(bom.manage)` for capability | `BomDetail` with `items` and `allowed_actions` | ✅ |

### BOM Write Endpoints

| Method | Path | Auth | Request Body | Status |
|---|---|---|---|---|
| POST | `/api/v1/products/{product_id}/boms` | `require_action(bom.manage)` | `BomCreateRequest` | ✅ 201 |
| PATCH | `/api/v1/products/{product_id}/boms/{bom_id}` | `require_action(bom.manage)` | `BomUpdateRequest` | ✅ 200 |
| POST | `/api/v1/products/{product_id}/boms/{bom_id}/release` | `require_action(bom.manage)` | (none) | ✅ 200 |
| POST | `/api/v1/products/{product_id}/boms/{bom_id}/retire` | `require_action(bom.manage)` | (none) | ✅ 200 |
| POST | `/api/v1/products/{product_id}/boms/{bom_id}/items` | `require_action(bom.manage)` | `BomItemCreateRequest` | ✅ 201 |
| PATCH | `/api/v1/products/{product_id}/boms/{bom_id}/items/{bom_item_id}` | `require_action(bom.manage)` | `BomItemUpdateRequest` | ✅ 200 |
| DELETE | `/api/v1/products/{product_id}/boms/{bom_id}/items/{bom_item_id}` | `require_action(bom.manage)` | (none) | ✅ 204 |

---

## 7. Frontend UI Baseline

| Screen | Route | Phase | Data Source | Write Controls | Notes |
|---|---|---|---|---|---|
| BomList | `/bom` | PARTIAL | BACKEND_API | Create BOM form gated by `bom_capabilities.can_create` | screenStatus notes outdated (see gap §13) |
| BomDetail | `/bom/:id` | PARTIAL | BACKEND_API | Edit/Release/Retire + item add/update/remove all gated by `allowed_actions.*` | screenStatus notes outdated (see gap §13) |

**Write payloads confirmed clean:**
- BomList create form sends: `bom_code`, `bom_name`, `effective_from`, `effective_to`, `description` only.
- BomDetail metadata update sends: `bom_name`, `effective_from`, `effective_to`, `description` only.
- BomDetail item create sends: `component_product_id`, `line_no`, `quantity`, `unit_of_measure`, `scrap_factor`, `reference_designator`, `notes` only.
- BomDetail item update sends: `quantity`, `unit_of_measure`, `scrap_factor`, `reference_designator`, `notes` only.
- **No** `lifecycle_status` in any payload.
- **No** `product_version_id` in any payload.

---

## 8. Authorization / Capability Baseline

### 9.4 Capability Matrix

| Capability | Level | Backend Source | FE Consumer | Rule |
|---|---|---|---|---|
| `bom_capabilities.can_create` | Product | `has_action(db, identity, "admin.master_data.bom.manage")` via product service | BomList.tsx line 52 | True iff user has `bom.manage`; `product.manage` does NOT imply this |
| `allowed_actions.can_update` | BOM | `has_manage && lifecycle_status == "DRAFT"` | BomDetail.tsx line 281 | False for RELEASED, RETIRED |
| `allowed_actions.can_release` | BOM | `has_manage && lifecycle_status == "DRAFT"` | BomDetail.tsx line 282 | False for RELEASED, RETIRED |
| `allowed_actions.can_retire` | BOM | `has_manage && lifecycle_status in [DRAFT, RELEASED]` | BomDetail.tsx line 283 | False for RETIRED |
| `allowed_actions.can_add_item` | BOM | `has_manage && lifecycle_status == "DRAFT"` | BomDetail.tsx line 284 | False for RELEASED, RETIRED |
| `allowed_actions.can_update_item` | BOM | `has_manage && lifecycle_status == "DRAFT"` | BomDetail.tsx line 285 | False for RELEASED, RETIRED |
| `allowed_actions.can_remove_item` | BOM | `has_manage && lifecycle_status == "DRAFT"` | BomDetail.tsx line 286 | False for RELEASED, RETIRED |
| `allowed_actions.can_create_sibling` | BOM | `has_manage` (any lifecycle) | productApi.ts type defined; UI control not yet wired | True for DRAFT and RELEASED; sibling create = new BOM for same product |

### 9.5 Lifecycle Capability Matrix

| Lifecycle | has_bom_manage | can_update | can_release | can_retire | can_add_item | can_update_item | can_remove_item | can_create_sibling |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| DRAFT | Yes | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RELEASED | Yes | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| RETIRED | Yes | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| DRAFT | No | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| RELEASED | No | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| RETIRED | No | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 9. Lifecycle Transition Baseline

```
(new) ──[create]──► DRAFT ──[release]──► RELEASED ──[retire]──► RETIRED
                      │                                              ▲
                      └──────────────────[retire]────────────────────┘
```

| Transition | Command | Guard | Notes |
|---|---|---|---|
| (new) → DRAFT | create BOM | `bom.manage` required | `bom_code` immutable after creation |
| DRAFT → RELEASED | release BOM | `bom.manage` required; must have ≥1 item | Service enforces |
| DRAFT → RETIRED | retire BOM | `bom.manage` required | Direct retire from DRAFT allowed |
| RELEASED → RETIRED | retire BOM | `bom.manage` required | |
| RETIRED → any | — | ❌ Forbidden | Terminal state |
| any → DRAFT | reactivate | ❌ Forbidden | No reactivate command |

---

## 10. Audit / Event Baseline

All BOM mutations emit audit events via `record_security_event()`. Events are governance/audit only — no execution, ERP, or operational side effects.

| Event Type | Resource Type | Trigger | Ordering Guarantee |
|---|---|---|---|
| `BOM.CREATED` | `bom` | `create_bom_service` | Emit after create |
| `BOM.UPDATED` | `bom` | `update_bom_service` | Emit after update |
| `BOM.RELEASED` | `bom` | `release_bom_service` | Emit after lifecycle change |
| `BOM.RETIRED` | `bom` | `retire_bom_service` | Emit after lifecycle change |
| `BOM_ITEM.ADDED` | `bom_item` | `add_bom_item_service` | Emit after create |
| `BOM_ITEM.UPDATED` | `bom_item` | `update_bom_item_service` | Emit after update |
| `BOM_ITEM.REMOVED` | `bom_item` | `remove_bom_item_service` | **Emit before delete** (audit integrity) |

No execution commands, quality decisions, material movement events, ERP posting events, inventory reservation events, or traceability/genealogy events are emitted.

---

## 11. Regression Coverage Baseline

### 9.7 Regression Coverage Baseline

| Area | Coverage | Command / Evidence | Status |
|---|---|---|---|
| BOM API (foundation + write routes) | 44 tests | `test_bom_foundation_api.py` | ✅ |
| BOM service (read + write logic) | 22 tests | `test_bom_foundation_service.py` | ✅ |
| BOM RBAC action codes | 24 tests | `test_mmd_rbac_action_codes.py` | ✅ |
| BOM capability guard (product-level) | 4 tests | `test_bom_capability_guard_12b_a.py` | ✅ |
| BOM allowed_actions matrix | 6 tests | `test_bom_allowed_actions_12b_a.py` | ✅ |
| Combined BOM backend gate | 100 tests | 5 files combined | ✅ |
| Adjacent MMD backend checks | 49 tests | product + pv + reason_code foundation | ✅ |
| Frontend mmd-read regression | 134 checks (incl. J1–J12 BOM capability checks) | `npm run check:mmd:read` | ✅ |
| Frontend build | Pass (3409 modules) | `npm run build` | ✅ |
| Frontend lint | Pass (0 errors) | `npm run lint` | ✅ |
| Frontend i18n registry | Pass (1816 keys, en/ja synced) | `npm run lint:i18n:registry` | ✅ |
| Route smoke | Pass (78 routes, 77 covered, 1 redirect excluded) | `npm run check:routes` | ✅ |
| Optional `npm run lint:i18n` | May be blocked by CRLF issue in CI; registry check is the authoritative gate | `lint:i18n:registry` preferred | ⚠ Optional |

---

## 12. Boundary Guardrails

### 9.6 Boundary Guardrails

| Boundary | Current Decision | Evidence | Risk if Violated |
|---|---|---|---|
| BOM vs Product Version | `product_version_id` deferred; not in BOM model, schema, or service | `bom-foundation-contract.md`: "No product_version_id in this revision"; `alembic/versions/0008_boms.py` comment; `BomCreateRequest` `extra="forbid"` | Coupling BOM definition truth to PV lifecycle without governance would introduce version-bind side effects and break BOM lifecycle independence |
| BOM vs ERP/PLM | No ERP posting, PLM sync, or bill of process coupling | `mmd-be-12a` keyword scan clean; no `erp`, `plm`, `posting` references in BOM source | ERP coupling without contract would create unsupported synchronization commitments |
| BOM vs Material / Inventory | No material availability check, lot/batch, inventory reservation, or consumption logic | `mmd-be-12a` scan clean; no `inventory`, `reserve`, `consume`, `lot`, `batch` in BOM source | Any material side effect from BOM mutation would bypass MES execution control |
| BOM vs Backflush | No backflush trigger from BOM mutation | `mmd-be-12a` scan clean; `backflush` absent from BOM source | Backflush is triggered by execution/completion, not BOM definition change |
| BOM vs Traceability / Genealogy | No genealogy record on BOM mutation | No `traceability`, `genealogy`, `lineage` in BOM source | Genealogy is execution domain truth; coupling to BOM write is a domain boundary violation |
| BOM vs Execution | No execution order/operation/station side effects | No execution model references in BOM source | BOM is a definition object; execution correctness depends on it being stable during active runs |
| BOM vs Quality | No quality hold trigger, acceptance decision, or inspection record on BOM mutation | No `quality`, `acceptance`, `inspection`, `hold` in BOM source | Quality decisions belong to QA domain; BOM mutation must not affect quality hold state |
| BOM vs Warehouse | No warehouse allocation, location assignment, or warehouse movement | No `warehouse`, `location`, `allocation` in BOM source | Warehouse operations are operational domain; not triggered by BOM definition changes |
| Frontend UI vs Authorization Truth | FE disables controls using server-derived `allowed_actions`; final authority is backend `require_action` returning 403 | `products.py` write routes all use `require_action`; FE defaults all capabilities to `false` | If FE were to enable controls based on local logic (persona, JWT claims), it would bypass authorization truth |
| Product manage vs BOM manage | `admin.master_data.product.manage` does NOT grant BOM create capability | `product_service.py`: `bom_capabilities.can_create` derived only from `has_bom_manage_permission`; no cross-action code inference | Granting BOM write from product manage would violate domain-specific action code separation established in MMD-BE-02 |

---

## 13. Known Gaps / Deferred Items

| Gap | Type | Priority | Notes |
|---|---|---|---|
| `frontend/src/app/screenStatus.ts` notes for BomList and BomDetail | Documentation drift | Low | Notes still say "Mutation actions remain disabled" — outdated after MMD-FULLSTACK-12. Phase and dataSource are accurate. Non-blocking. Should be updated in a future housekeeping slice. |
| `allowed_actions.can_create_sibling` FE wiring | Deferred | Medium | Type defined and computed by backend; FE type present in `productApi.ts`; no BomList/BomDetail UI control wired to it yet. Intentionally deferred — next BOM write slice can add sibling-create shortcut. |
| BOM release guard: minimum 1 item | Soft documentation | Low | Backend service enforces "cannot release with zero items" but this is not explicitly shown in FE pre-flight validation. UX refinement deferred. |
| BOM code immutability: FE label | Soft documentation | Low | `bom_code` is immutable after creation (service enforces) but the BomDetail metadata edit panel does not explicitly show it as read-only. UX refinement deferred. |
| `product_version_id` binding | Explicitly deferred | High | Requires MMD-BOM-WRITE-02 governance contract before any binding can be added. Must not be added without full Hard Mode MOM v3 slice. |
| Hard delete BOM | Explicitly forbidden | — | No reactivate path exists; cannot be added without product governance review. |
| Bulk import / replace-all / reorder | Explicitly forbidden | — | Requires separate compound-command governance slice if ever needed. |
| Material / backflush / ERP coupling | Explicitly forbidden | — | Out of BOM domain scope; requires separate integration governance. |
| Reason Code write governance | Next planned | High | MMD-BE-10 is the recommended next slice. |

---

## 14. Do-Not-Do Rules for Future Agents

The following actions are **FORBIDDEN** without a new governance slice, a new Hard Mode MOM v3 evidence set, and explicit product owner approval:

1. **DO NOT** add a hard-delete BOM endpoint (`DELETE /products/{id}/boms/{bom_id}`).
2. **DO NOT** add a reactivate BOM endpoint or transition RETIRED → DRAFT.
3. **DO NOT** add clone/copy BOM commands.
4. **DO NOT** add bulk import, bulk retire, replace-all-items, or reorder-items endpoints.
5. **DO NOT** add `product_version_id` to the BOM model, schema, or any BOM endpoint without completing MMD-BOM-WRITE-02.
6. **DO NOT** add `bind_to_product_version` or `unbind_from_product_version` BOM commands without completing MMD-BOM-WRITE-02.
7. **DO NOT** trigger material availability checks, inventory reservation, lot/batch selection, or warehouse allocation from BOM mutation.
8. **DO NOT** trigger backflush from BOM creation, update, release, or retire.
9. **DO NOT** trigger ERP posting, PLM sync, or BOM revision publication from BOM mutations.
10. **DO NOT** trigger traceability genealogy record creation from BOM mutations.
11. **DO NOT** trigger quality acceptance, quality hold, or inspection from BOM mutations.
12. **DO NOT** derive `bom_capabilities.can_create` from `admin.master_data.product.manage`. It must come from `admin.master_data.bom.manage` only.
13. **DO NOT** derive BOM write capability from persona, JWT claims, or user role name in frontend.
14. **DO NOT** include `lifecycle_status` or `product_version_id` in any BOM write request payload from the frontend.
15. **DO NOT** use BOM as material consumption truth or production confirmation trigger.
16. **DO NOT** modify `_compute_allowed_actions` state matrix without a governance slice that regenerates the full test matrix.
17. **DO NOT** weaken `extra="forbid"` on any BOM write schema.

---

## 15. Recommended Next Slices

**Recommended: MMD-BE-10 — Reason Code Write Governance / Minimal Mutation Contract**

Reason: Product Version write baseline and BOM write baseline are now governed and frozen. Reason Codes are the remaining MMD read-complete domain needing write governance before mutation implementation. This follows the same pattern as MMD-BE-09 (BOM governance before implementation).

| Next Slice | Recommendation | Condition |
|---|---|---|
| MMD-BE-10 — Reason Code Write Governance | ✅ Recommended default | Proceed unless explicit business priority change |
| MMD-FE-QA-02 — Browser Screenshot Runtime QA | Only if visual/runtime evidence required first | Optional; can be deferred |
| MMD-BOM-WRITE-02 — BOM Product Version Binding Governance Contract | Only if business explicitly prioritizes PV-BOM binding before Reason Code write | Requires full Hard Mode MOM v3 evidence set |
| MMD-PV-WRITE-02 — Product Version set_current Governance Contract | Only if business explicitly prioritizes current-version switching first | Requires Hard Mode MOM v3 evidence set |

---

## 16. Verification Commands

**Note on evidence reuse:** This is a documentation-only baseline freeze slice. No backend runtime source, frontend runtime source, tests, or migrations were modified since MMD-FULLSTACK-12B-B (completed May 3, 2026). The evidence below is from MMD-FULLSTACK-12B-B and MMD-FULLSTACK-12B-A, which together constitute the most recent full verification run. This reuse is explicitly permitted per task instructions when source has not changed.

### Backend BOM Verification Gate

```bash
cd backend
python -m pytest -q \
  tests/test_bom_foundation_api.py \
  tests/test_bom_foundation_service.py \
  tests/test_mmd_rbac_action_codes.py \
  tests/test_bom_capability_guard_12b_a.py \
  tests/test_bom_allowed_actions_12b_a.py
```

**Last known result (MMD-FULLSTACK-12B-B, May 3 2026):** 100 passed, 1 warning

| File | Tests | Result |
|---|---|---|
| `test_bom_foundation_api.py` | 44 | ✅ Passed |
| `test_bom_foundation_service.py` | 22 | ✅ Passed |
| `test_mmd_rbac_action_codes.py` | 24 | ✅ Passed |
| `test_bom_capability_guard_12b_a.py` | 4 | ✅ Passed |
| `test_bom_allowed_actions_12b_a.py` | 6 | ✅ Passed |
| **Combined** | **100** | ✅ Passed |

### Adjacent Backend Checks

```bash
cd backend
python -m pytest -q \
  tests/test_product_foundation_api.py \
  tests/test_product_version_foundation_api.py \
  tests/test_reason_code_foundation_api.py
```

**Last known result:** 49 passed, 1 warning

### Frontend Regression Gate

```bash
cd frontend
npm run check:mmd:read
```

**Last known result:** 134 passed, 0 failed (includes J1–J12 BOM capability checks)

```bash
cd frontend
npm run build
```

**Last known result:** BUILD SUCCEEDED (3409 modules)

```bash
cd frontend
npm run lint
```

**Last known result:** PASS (0 eslint errors)

```bash
cd frontend
npm run lint:i18n:registry
```

**Last known result:** PASS (1816 keys, en.ts and ja.ts synchronized)

```bash
cd frontend
npm run check:routes
```

**Last known result:** PASS (78 routes registered, 77 covered, 1 redirect excluded; 24 checks passed)

Optional (may be blocked by CRLF in CI):
```bash
cd frontend
npm run lint:i18n
```

---

## 17. Final Freeze Verdict

**FROZEN — BOM Write Baseline v1.0**

The BOM write baseline is complete and verified as of May 4, 2026.

**What is frozen:**

- 4 BOM header write commands (create/update/release/retire) — governed, tested, verified
- 3 BOM item write commands (add/update/remove) — governed, tested, verified
- `admin.master_data.bom.manage` as the sole mutation action code
- `bom_capabilities.can_create` as the server-derived product-level create gate
- 7-field `allowed_actions` as the server-derived BOM-level write control gate
- DRAFT/RELEASED/RETIRED lifecycle state machine with enforced transitions
- 100 BOM-related backend tests passing
- 134 frontend regression checks passing (including J1–J12 BOM capability guard)
- Frontend build, lint, i18n registry, and route smoke gate all passing
- All boundary guardrails enforced: no product_version_id, no material/backflush/ERP/traceability/quality side effects

**What is explicitly NOT frozen (deferred/forbidden):**

- Hard delete, reactivate, clone, bulk, replace-all, reorder
- Product Version binding (`product_version_id`, `bind_to_product_version`)
- Material, inventory, backflush, ERP, traceability, quality, warehouse coupling
- Any inference of BOM create capability from `product.manage`

**Next recommended slice:** MMD-BE-10 — Reason Code Write Governance / Minimal Mutation Contract

**Freeze integrity:** All required invariants verified. All stop conditions clear. Governance boundaries maintained.

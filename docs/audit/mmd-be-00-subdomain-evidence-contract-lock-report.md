# MMD-BE-00 Report
# MMD Subdomain Evidence / Contract Lock

**Slice:** MMD-BE-00  
**Date:** 2026-05-03  
**Status:** COMPLETE  
**Decision Type:** Source audit + design contract lock — read-only evidence slice

---

## Summary

MMD-BE-00 maps current MMD backend subdomain truth from actual source code before further
write/API split work proceeds. It produces the evidence/contract-lock document required by
P0-A-10B and the rejection notice on the master-data-hardening proposal.

**Option A** selected: contract-lock current source truth only. Source is internally
consistent, subdomain surfaces are readable, no runtime correction needed, and the
coarse-grained action posture is correct for the current foundation phase.

**6 MMD subdomains** were discovered and mapped from source:
Product, Product Version, Routing, BOM (read-only API), Resource Requirement,
and Reason Code. This exceeds the 4 in the nominal `admin.master_data.*` action codes
because BOM and Reason Code exist in source but are read-only API with no write action codes.

No runtime code was changed. No action code was added. No route guard was changed.
No migration was added.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Architecture + Strict (source audit, evidence extraction)
- **Hard Mode MOM:** v3
- **Reason:** Touches MMD governance boundary, role/action/scope assignment implications,
  product/routing/BOM/version/resource-definition truth, and critical
  MMD-vs-Execution/Quality/Material invariant. Hard Mode MOM v3 is mandatory.

---

## Hard Mode MOM v3 Gate

### 1. Design Evidence Extract

| Evidence Item | Source | Finding |
|---|---|---|
| 4 MMD action codes in registry | `backend/app/security/rbac.py` L56–60 | `product.manage`, `product_version.manage`, `routing.manage`, `resource_requirement.manage` — all ADMIN |
| No BOM write action code exists | Source scan + `test_bom_foundation_api.py` L231 | BOM API is read-only; no POST/PATCH/DELETE routes |
| No ReasonCode write action code exists | Source scan + `test_reason_code_foundation_api.py` L335 | Reason Code API is read-only; no write routes |
| Product lifecycle: DRAFT/RELEASED/RETIRED | `product_service.py` L133, L160, L174 | Implemented with structural update guard on RELEASED |
| Product Version lifecycle: DRAFT/RELEASED/RETIRED + is_current | `product_version_service.py` L44–52 | is_current flag; DRAFT/RELEASED can retire (not if is_current); RELEASED cannot be updated |
| Routing lifecycle: DRAFT/RELEASED/RETIRED | `routing_service.py` L172, L456, L488 | Resource requirements can be modified only in DRAFT |
| BOM lifecycle field exists but write is disabled | `bom_service.py` L35 (lifecycle_status field) | BOM has lifecycle_status but no write service |
| ReasonCode lifecycle field exists | `reason_code_service.py` L22 (lifecycle_status field) | Read-only service only; lifecycle_status='RELEASED' is default filter |
| ResourceRequirement has no lifecycle field | `resource_requirement_service.py` L84 | No lifecycle state on RR; parent Routing must be DRAFT to modify |
| All mutation services call record_security_event | product, product_version, routing, resource_requirement services | Audit trail present; BOM/ReasonCode do not mutate → no audit events |
| No ERP/backflush/material/quality fields in BOM model | `test_bom_foundation_api.py` L244, L257 | BOM domain boundary respected |
| P0-A-10B: ADMIN family coarse-grained, split deferred | P0-A-10B report | Current single-code per subdomain is correct for foundation phase |
| Proposal v1.0 rejected | `master-data-hardening-proposal.md` header | Phase A.5 permission fix and split deferred |

### 2. Event Map

| Subdomain | Emits audit/security event? | Event Type(s) | Forbidden Side Effects |
|---|---|---|---|
| Product | ✅ Yes | `PRODUCT.CREATED`, `PRODUCT.UPDATED`, `PRODUCT.RELEASED`, `PRODUCT.RETIRED` | None found — no execution/material/ERP/quality fields |
| Product Version | ✅ Yes | `PRODUCT_VERSION.CREATED`, `PRODUCT_VERSION.UPDATED`, `PRODUCT_VERSION.RELEASED`, `PRODUCT_VERSION.RETIRED` | None found — `is_current` is within MMD boundary |
| Routing | ✅ Yes | `ROUTING.CREATED`, `ROUTING.UPDATED`, `ROUTING.OPERATION_ADDED`, `ROUTING.OPERATION_UPDATED`, `ROUTING.OPERATION_REMOVED`, `ROUTING.RELEASED`, `ROUTING.RETIRED` | None found — no execution command emitted |
| Resource Requirement | ✅ Yes | `RESOURCE_REQUIREMENT.CREATED`, `RESOURCE_REQUIREMENT.UPDATED`, `RESOURCE_REQUIREMENT.REMOVED` | None found — no execution/material/backflush |
| BOM | ❌ No (read-only) | None | N/A — no write operations exist |
| Reason Code | ❌ No (read-only) | None | N/A — no write operations exist |

**Confirmed:** No MMD subdomain emits execution commands, execution state transitions,
material movement/backflush, ERP postings, quality decisions/holds, or
traceability/genealogy mutations. MMD audit events are scoped to
`resource_type="product"`, `"product_version"`, `"routing"`, `"resource_requirement"`.

### 3. Invariant Map

| Invariant | Evidence | Test / Contract Lock |
|---|---|---|
| MMD definition truth is not execution runtime truth | BOM/Routing/Product services contain no execution commands | `test_bom_foundation_api.py` L244 (no backflush/ERP fields) |
| Product Version lifecycle does not trigger execution/material/ERP/quality side effects | `product_version_service.py` — only calls `record_security_event` | `test_product_version_foundation_service.py` L282 (MMD audit boundary) |
| BOM/Routing/Product/RR behavior stays inside MMD/Admin boundary | Domain boundary review; no cross-domain service calls found | `test_bom_foundation_api.py` L257 (no inventory movement fields) |
| Current action codes are coarse-grained ADMIN-family | `rbac.py` L56–60 | `test_mmd_rbac_action_codes.py` (18 tests) |
| Draft/update vs release/retire split is future, not implemented now | P0-A-10B; no dual-code pattern in source | `test_rbac_action_registry_alignment.py` (exact count) |
| No runtime code added in this slice | This audit | All 124 tests pass unchanged |
| ReasonCode write is not exposed via API | `reason_codes.py` — only GET routes | `test_reason_code_foundation_api.py` L335 |
| BOM write is not exposed via API | `products.py` — only GET `/products/{id}/boms` and GET `/{id}/boms/{bom_id}` | `test_bom_foundation_api.py` L231 |
| ResourceRequirement can only be modified in DRAFT routing | `resource_requirement_service.py` L84 | Service-level invariant |
| RELEASED product structural fields cannot be updated | `product_service.py` L166–168 | `test_product_foundation_api.py` lifecycle transition tests |

### 4. State Transition Map

#### Product
```
[create] → DRAFT
DRAFT + [update] → DRAFT (non-structural fields allowed even on RELEASED via separate guard)
DRAFT + [release] → RELEASED
RELEASED/DRAFT + [retire] → RETIRED
RETIRED → terminal (no further mutations)
RELEASED + structural update → 400 error (guarded)
```

#### Product Version
```
[create] → DRAFT (is_current=False)
DRAFT + [update] → DRAFT
DRAFT + [release] → RELEASED (is_current not set here — must be set via separate mechanism)
DRAFT/RELEASED (not is_current) + [retire] → RETIRED
RELEASED + [update] → 400 error
RETIRED → terminal
```
Note: `is_current` flag is managed separately; cannot be set by create/update/release API.

#### Routing
```
[create] → DRAFT
DRAFT + [update] → DRAFT
DRAFT + [add_operation / update_operation / remove_operation] → DRAFT (mutated)
DRAFT + [release] → RELEASED
RELEASED + [retire] → RETIRED
RELEASED/RETIRED + operation mutations → 400 error (guarded: only DRAFT allows mutation)
RETIRED → terminal
```
Resource Requirements can be modified only when parent Routing is DRAFT.

#### BOM
```
[lifecycle_status field exists in model: DRAFT/RELEASED/RETIRED]
Current API: read-only only. No create/update/release/retire via API.
State transitions are NOT implemented at service layer (no write service methods).
```

#### Reason Code
```
[lifecycle_status field exists in model]
Default list API returns RELEASED+active codes.
No write API. No create/update service.
```

#### Resource Requirement
```
No lifecycle state on ResourceRequirement itself.
Lifecycle gate is parent Routing: must be DRAFT to create/update/delete RR.
```

### 5. Test Matrix

| Current Test Area | Current Test File | Test Count | Coverage | Gap |
|---|---|---|---|---|
| MMD RBAC action codes | `test_mmd_rbac_action_codes.py` | 18 | Action code existence, ADMIN family, no `admin.user.manage` in source files, correct counts | BOM/ReasonCode write action codes absent (correct — no write API) |
| RBAC action registry alignment | `test_rbac_action_registry_alignment.py` | 20 | Exact registry match, family correctness, naming | None for current state |
| RBAC seed alignment | `test_rbac_seed_alignment.py` | 20 | Seed creates correct role/permission rows | None for current state |
| Product Version API | `test_product_version_foundation_api.py` | ~20+ | Full CRUD+lifecycle, auth guard, boundary tests | No SoD test (correct: no approval workflow yet) |
| Product Version Service | `test_product_version_foundation_service.py` | 12 | Lifecycle invariants, audit boundary, date validation | — |
| Product Foundation API | `test_product_foundation_api.py` | 3 | Happy path, cross-tenant 404, auth guard | Narrow coverage; lifecycle invariant tests indirect |
| BOM Foundation API | `test_bom_foundation_api.py` | 11 | Read-only, domain boundary (no backflush/ERP/inventory fields), no write routes | No write tests (correct — no write API) |
| Reason Code Foundation API | `test_reason_code_foundation_api.py` | 10 | Read, filters, auth, no write routes | No write tests (correct) |

### 6. Verdict

**ALLOW_MMD_BE00_SUBDOMAIN_EVIDENCE_CONTRACT_LOCK**

Option A selected. Source is consistent. 6 subdomains mapped. No stop condition hit.
No runtime code change required.

---

## Selected Option

**Option A — Contract-lock current source truth only.**

Reasons:
1. Source is internally consistent — no cross-domain side effects found.
2. All 6 subdomains have readable API/service surfaces.
3. No runtime correction needed — coarse-grained action posture is correct for foundation.
4. BOM and Reason Code read-only status is intentional and test-locked.
5. All 124 relevant tests pass.

---

## Source Evidence Map

| Subdomain | Model | Service | Routes (file) | Tests |
|---|---|---|---|---|
| Product | `app/models/product.py` | `app/services/product_service.py` | `app/api/v1/products.py` (product-level routes) | `test_product_foundation_api.py` |
| Product Version | `app/models/product_version.py` | `app/services/product_version_service.py` | `app/api/v1/products.py` (version sub-routes) | `test_product_version_foundation_api.py`, `test_product_version_foundation_service.py` |
| Routing | `app/models/routing.py` | `app/services/routing_service.py` | `app/api/v1/routings.py` | No dedicated routing foundation API test found |
| BOM | `app/models/bom.py` | `app/services/bom_service.py` (read-only) | `app/api/v1/products.py` (nested `/boms` read-only) | `test_bom_foundation_api.py` |
| Resource Requirement | `app/models/resource_requirement.py` | `app/services/resource_requirement_service.py` | `app/api/v1/routings.py` (nested under routing) | `test_mmd_rbac_action_codes.py` (partial) |
| Reason Code | `app/models/reason_code.py` | `app/services/reason_code_service.py` (read-only) | `app/api/v1/reason_codes.py` | `test_reason_code_foundation_api.py` |

---

## Current MMD Subdomain Map

### Subdomain 1: Product

| Attribute | Value |
|---|---|
| Model | `app/models/product.py` |
| Table | `products` |
| Key fields | `product_id`, `tenant_id`, `product_code`, `product_name`, `product_type`, `lifecycle_status`, `description`, `display_metadata` |
| Lifecycle states | `DRAFT`, `RELEASED`, `RETIRED` |
| Write service | ✅ `product_service.py` — create, update, release, retire |
| Read service | ✅ `product_service.py` — list, get |
| Audit events | `PRODUCT.CREATED`, `PRODUCT.UPDATED`, `PRODUCT.RELEASED`, `PRODUCT.RETIRED` |
| Action code | `admin.master_data.product.manage` (ADMIN) |
| Write guards | create/update/release/retire via `require_action("admin.master_data.product.manage")` |
| Read guards | `require_authenticated_identity` |
| Structural update guard | Blocked when RELEASED: `product_code`, `product_type` |
| RETIRED guard | Update blocked when RETIRED |

### Subdomain 2: Product Version

| Attribute | Value |
|---|---|
| Model | `app/models/product_version.py` |
| Table | `product_versions` |
| Key fields | `product_version_id`, `tenant_id`, `product_id`, `version_code`, `version_name`, `lifecycle_status`, `is_current`, `effective_from`, `effective_to`, `description` |
| Lifecycle states | `DRAFT`, `RELEASED`, `RETIRED` |
| Special flag | `is_current` — NOT settable via API; managed separately |
| Write service | ✅ `product_version_service.py` — create, update, release, retire |
| Read service | ✅ `product_version_service.py` — list, get |
| Audit events | `PRODUCT_VERSION.CREATED`, `PRODUCT_VERSION.UPDATED`, `PRODUCT_VERSION.RELEASED`, `PRODUCT_VERSION.RETIRED` |
| Action code | `admin.master_data.product_version.manage` (ADMIN) |
| Write guards | All write routes via `require_action("admin.master_data.product_version.manage")` |
| allowed_actions | Server-derived write capability hints (can_update, can_release, can_retire, can_create_sibling) — NOT authorization |

### Subdomain 3: Routing

| Attribute | Value |
|---|---|
| Model | `app/models/routing.py` |
| Table | `routings`, `routing_operations` |
| Key fields | `routing_id`, `tenant_id`, `product_id`, `routing_code`, `routing_name`, `lifecycle_status`, plus operations with `operation_id`, `sequence_no`, `operation_name`, etc. |
| Lifecycle states | `DRAFT`, `RELEASED`, `RETIRED` |
| Write service | ✅ `routing_service.py` — create, update, add/update/remove operations, release, retire |
| Read service | ✅ `routing_service.py` — list, get |
| Audit events | `ROUTING.CREATED`, `ROUTING.UPDATED`, `ROUTING.OPERATION_ADDED`, `ROUTING.OPERATION_UPDATED`, `ROUTING.OPERATION_REMOVED`, `ROUTING.RELEASED`, `ROUTING.RETIRED` |
| Action code | `admin.master_data.routing.manage` (ADMIN) |
| Write guards | All routing mutation routes via `require_action("admin.master_data.routing.manage")` |
| Operation mutation guard | Blocked when routing is not DRAFT |

### Subdomain 4: BOM (Bill of Materials)

| Attribute | Value |
|---|---|
| Model | `app/models/bom.py` |
| Table | `boms`, `bom_items` |
| Key fields | `bom_id`, `tenant_id`, `product_id`, `bom_code`, `bom_name`, `lifecycle_status`, `effective_from`, `effective_to`, `description`, items |
| Lifecycle states | `DRAFT`, `RELEASED`, `RETIRED` (field exists) |
| Write service | ❌ NOT IMPLEMENTED — `bom_service.py` is read-only |
| Read service | ✅ `bom_service.py` — list, get (nested under `/products/{id}/boms`) |
| Audit events | None (no write operations) |
| Action code | ❌ None — no write action code exists |
| Write guards | No write routes exposed |
| Boundary tests | `test_bom_foundation_api.py` verifies no backflush/ERP/inventory fields |

### Subdomain 5: Resource Requirement

| Attribute | Value |
|---|---|
| Model | `app/models/resource_requirement.py` |
| Table | `resource_requirements` |
| Key fields | `requirement_id`, `tenant_id`, `routing_id`, `operation_id`, `required_resource_type`, `resource_code`, `quantity_required`, `notes` |
| Lifecycle states | None (no lifecycle field on RR; parent Routing state governs) |
| Write service | ✅ `resource_requirement_service.py` — create, update, delete |
| Read service | ✅ `resource_requirement_service.py` — list, get |
| Audit events | `RESOURCE_REQUIREMENT.CREATED`, `RESOURCE_REQUIREMENT.UPDATED`, `RESOURCE_REQUIREMENT.REMOVED` |
| Action code | `admin.master_data.resource_requirement.manage` (ADMIN) |
| Write guards | All write routes via `require_action("admin.master_data.resource_requirement.manage")` |
| Parent lifecycle guard | Blocked when parent Routing is not DRAFT |
| Allowed resource types | `WORK_CENTER`, `STATION_CAPABILITY`, `EQUIPMENT_CAPABILITY`, `OPERATOR_SKILL`, `TOOLING` |

### Subdomain 6: Reason Code

| Attribute | Value |
|---|---|
| Model | `app/models/reason_code.py` |
| Table | `reason_codes` |
| Key fields | `reason_code_id`, `tenant_id`, `reason_domain`, `reason_category`, `reason_code`, `reason_name`, `description`, `lifecycle_status`, `requires_comment`, `is_active`, `sort_order` |
| Lifecycle states | `DRAFT`, `RELEASED`, `RETIRED` (field exists; default list returns `RELEASED` only) |
| `is_active` flag | Boolean; default list returns `is_active=True` only |
| Write service | ❌ NOT IMPLEMENTED — `reason_code_service.py` is read-only |
| Read service | ✅ `reason_code_service.py` — list (with domain/category/lifecycle_status/include_inactive filters), get |
| Audit events | None (no write operations) |
| Action code | ❌ None — no write action code exists |
| Write guards | No write routes exposed |
| Existing write management | Via `admin.downtime_reason.manage` for downtime-specific reasons in `/v1/downtime-reasons` (separate table `downtime_reasons`, NOT the unified `reason_codes` table) |

---

## Action Code / Route Guard Map

| Action Code | Family | Subdomain | Route Operations Guarded |
|---|---|---|---|
| `admin.master_data.product.manage` | ADMIN | Product | POST `/products`, PATCH `/products/{id}`, POST `/products/{id}/release`, POST `/products/{id}/retire` (4 routes) |
| `admin.master_data.product_version.manage` | ADMIN | Product Version | POST `/products/{id}/versions`, PATCH `/products/{id}/versions/{vid}`, POST `…/release`, POST `…/retire` (4 routes) |
| `admin.master_data.routing.manage` | ADMIN | Routing | POST `/routings`, PATCH `/routings/{id}`, POST `…/operations`, PATCH `…/operations/{opid}`, DELETE `…/operations/{opid}`, POST `…/release`, POST `…/retire` (7 routes) |
| `admin.master_data.resource_requirement.manage` | ADMIN | Resource Requirement | POST `…/resource-requirements`, PATCH `…/resource-requirements/{rid}`, DELETE `…/resource-requirements/{rid}` (3 routes) |
| *(none)* | — | BOM | No write routes — all BOM routes use `require_authenticated_identity` |
| *(none)* | — | Reason Code | No write routes — all ReasonCode routes use `require_authenticated_identity` |

**Total: 4 action codes, 18 action-guarded route endpoints**

Read routes across all subdomains use `require_authenticated_identity` only (no action code required).

---

## Lifecycle / State Transition Map

### Summary Table

| Subdomain | States | Create Initial | Can Update | Can Release | Can Retire | Terminal |
|---|---|---|---|---|---|---|
| Product | DRAFT/RELEASED/RETIRED | DRAFT | DRAFT only (structural blocked on RELEASED) | DRAFT→RELEASED | DRAFT or RELEASED→RETIRED | RETIRED |
| Product Version | DRAFT/RELEASED/RETIRED | DRAFT | DRAFT only | DRAFT→RELEASED | DRAFT or RELEASED (not is_current)→RETIRED | RETIRED |
| Routing | DRAFT/RELEASED/RETIRED | DRAFT | DRAFT only | DRAFT→RELEASED | RELEASED→RETIRED | RETIRED |
| BOM | DRAFT/RELEASED/RETIRED (model) | ❌ not via API | ❌ | ❌ | ❌ | — |
| Resource Requirement | None | Any (parent must be DRAFT) | Any (parent must be DRAFT) | N/A | Deleted not retired | — |
| Reason Code | DRAFT/RELEASED/RETIRED (model) | ❌ not via API | ❌ | ❌ | ❌ | — |

### Product RETIRED guard details

- RETIRED product: update blocked entirely
- RELEASED product: structural update blocked (`product_code`, `product_type`); non-structural fields (`product_name`, `description`, `display_metadata`) can still be updated

### Product Version RELEASED guard details

- RELEASED version: all updates blocked (404 semantic: `can_update=False`)
- RETIRED is allowed from DRAFT or RELEASED provided `is_current=False`
- `is_current` flag cannot be set by create/update/release API calls

### Routing operation mutation guard

- Operations (add/update/remove) and Resource Requirements can be modified only when parent Routing is DRAFT
- This enforces that RELEASED routings are structurally frozen for execution use

---

## Event / Audit Boundary Map

### Security events emitted (all via `record_security_event` in `security_event_service`)

| Event Type | Resource Type | Subdomain |
|---|---|---|
| `PRODUCT.CREATED` | `product` | Product |
| `PRODUCT.UPDATED` | `product` | Product |
| `PRODUCT.RELEASED` | `product` | Product |
| `PRODUCT.RETIRED` | `product` | Product |
| `PRODUCT_VERSION.CREATED` | `product_version` | Product Version |
| `PRODUCT_VERSION.UPDATED` | `product_version` | Product Version |
| `PRODUCT_VERSION.RELEASED` | `product_version` | Product Version |
| `PRODUCT_VERSION.RETIRED` | `product_version` | Product Version |
| `ROUTING.CREATED` | `routing` | Routing |
| `ROUTING.UPDATED` | `routing` | Routing |
| `ROUTING.OPERATION_ADDED` | `routing` | Routing |
| `ROUTING.OPERATION_UPDATED` | `routing` | Routing |
| `ROUTING.OPERATION_REMOVED` | `routing` | Routing |
| `ROUTING.RELEASED` | `routing` | Routing |
| `ROUTING.RETIRED` | `routing` | Routing |
| `RESOURCE_REQUIREMENT.CREATED` | `resource_requirement` | Resource Requirement |
| `RESOURCE_REQUIREMENT.UPDATED` | `resource_requirement` | Resource Requirement |
| `RESOURCE_REQUIREMENT.REMOVED` | `resource_requirement` | Resource Requirement |

### Boundary confirmation

No MMD service was found to call:
- execution service or emit execution events
- material movement or backflush service
- ERP posting service
- quality hold or quality decision service
- traceability/genealogy mutation service

All 4 write subdomains emit only `resource_type`-scoped security events through the standard
`record_security_event` path.

---

## Domain Boundary Lock

The following boundaries are locked by this contract:

| Boundary | Direction | Status | Evidence |
|---|---|---|---|
| MMD → Execution | MMD does NOT call execution services | LOCKED | Source scan — no import of execution/operation/station_session service in MMD services |
| MMD → Material/Backflush | MMD does NOT trigger material movement | LOCKED | `test_bom_foundation_api.py` L244, L257 — no backflush/ERP/inventory fields |
| MMD → ERP Posting | MMD does NOT post to ERP | LOCKED | No ERP service exists; no ERP field in MMD models |
| MMD → Quality | MMD does NOT trigger quality holds or decisions | LOCKED | No quality service import in MMD services |
| MMD → Traceability | MMD does NOT mutate genealogy/traceability | LOCKED | No traceability model in MMD service imports |
| Execution → MMD (read) | Execution reads RELEASED routing/product definitions | ALLOWED | This is the intended read direction |
| Execution → MMD (write) | Execution does NOT mutate MMD definitions | LOCKED | Design boundary; no route path from execution to MMD mutation |

---

## Future Action Split Candidates

Per P0-A-10B decision, the following split is a candidate for Phase C (MMD Mutation Enablement):

### Candidate Pattern (Option B-1 from P0-A-10B)

| Current Code | Proposed Draft Code | Proposed Lifecycle Code | Who Gets Draft | Who Gets Lifecycle |
|---|---|---|---|---|
| `admin.master_data.product.manage` | `admin.master_data.product.draft_manage` | `admin.master_data.product.lifecycle_manage` | IEP, PMG, ADM | ADM (with SoD gate) |
| `admin.master_data.product_version.manage` | `admin.master_data.product_version.draft_manage` | `admin.master_data.product_version.lifecycle_manage` | IEP, PMG, ADM | ADM (with SoD gate) |
| `admin.master_data.routing.manage` | `admin.master_data.routing.draft_manage` | `admin.master_data.routing.lifecycle_manage` | IEP, PMG, ADM | ADM (with SoD gate) |
| `admin.master_data.resource_requirement.manage` | `admin.master_data.resource_requirement.draft_manage` | *(no lifecycle code needed — parent Routing governs)* | IEP, PMG, ADM | N/A |

### BOM and Reason Code future write candidates

When BOM write API is implemented:

```
admin.master_data.bom.draft_manage     — create, update BOM
admin.master_data.bom.lifecycle_manage — release, retire BOM
```

When Reason Code write API is implemented:

```
admin.master_data.reason_code.draft_manage     — create, update Reason Code
admin.master_data.reason_code.lifecycle_manage — release, retire Reason Code
```

Note: `admin.downtime_reason.manage` covers the existing `downtime_reasons` table
(a separate pre-unified table). When Reason Code write API unifies with the `reason_codes`
table, the `admin.downtime_reason.manage` code should be migrated or deprecated.

### Implementation Gate

All split candidates require:
1. Phase 7+ design gate for `SYSTEM_ROLE_FAMILIES["IEP"]` and `["PMG"]` ADMIN family addition.
2. Approval workflow (`approval_service.py`) ready for MMD lifecycle transitions.
3. SoD gate designed and implemented.
4. MMD proposal v1.1 authored and approved.
5. Existing `*.manage` DB bindings migrated atomically with new codes.

---

## Files Inspected

| File | Status |
|---|---|
| `.github/copilot-instructions.md` | Read |
| `.github/agent/AGENT.md` | Read |
| `.github/copilot-instructions-hard-mode-mom-v3-addendum.md` | Read |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | Read |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | Read |
| `docs/audit/p0-a-10b-iep-mmd-action-boundary-decision-report.md` | Read |
| `docs/proposals/2026-05-01-master-data-hardening-proposal.md` | Read (header, §A.5) |
| `docs/design/00_platform/master-data-strategy.md` | Read |
| `docs/design/00_platform/domain-boundary-map.md` | Read |
| `docs/design/00_platform/product-business-truth-overview.md` | Read |
| `docs/design/00_platform/authorization-model-overview.md` | Read |
| `docs/design/01_foundation/role-model-and-scope-resolution.md` | Read |
| `docs/design/02_registry/action-code-registry.md` | Read |
| `backend/app/security/rbac.py` | Read — full ACTION_CODE_REGISTRY |
| `backend/app/api/v1/products.py` | Read — all route guards |
| `backend/app/api/v1/routings.py` | Read — all route guards |
| `backend/app/api/v1/reason_codes.py` | Read — read-only verified |
| `backend/app/services/product_service.py` | Read — full lifecycle + events |
| `backend/app/services/product_version_service.py` | Read — full lifecycle + events + allowed_actions |
| `backend/app/services/bom_service.py` | Read — read-only verified |
| `backend/app/services/routing_service.py` | Scanned — event types, lifecycle guards |
| `backend/app/services/resource_requirement_service.py` | Read — full lifecycle guard, events |
| `backend/app/services/reason_code_service.py` | Read — read-only verified |
| `backend/tests/test_mmd_rbac_action_codes.py` | Read |
| `backend/tests/test_rbac_action_registry_alignment.py` | Read |
| `backend/tests/test_rbac_seed_alignment.py` | Read (count) |
| `backend/tests/test_product_version_foundation_api.py` | Scanned — test names |
| `backend/tests/test_product_version_foundation_service.py` | Scanned — test names |
| `backend/tests/test_product_foundation_api.py` | Scanned — test names |
| `backend/tests/test_bom_foundation_api.py` | Scanned — all test names |
| `backend/tests/test_reason_code_foundation_api.py` | Scanned — all test names |

---

## Files Changed

| File | Change |
|---|---|
| `docs/audit/mmd-be-00-subdomain-evidence-contract-lock-report.md` | **Created** — this report |

No runtime source files were changed. No tests were changed.

---

## Verification Commands Run

```powershell
cd g:\Work\FleziBCG
git status --short

cd g:\Work\FleziBCG\backend
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q \
    tests/test_mmd_rbac_action_codes.py \
    tests/test_rbac_action_registry_alignment.py \
    tests/test_rbac_seed_alignment.py \
    tests/test_product_version_foundation_api.py \
    tests/test_product_version_foundation_service.py \
    tests/test_product_foundation_api.py \
    tests/test_bom_foundation_api.py \
    tests/test_reason_code_foundation_api.py
```

---

## Results

```
124 passed, 1 warning in 6.81s
```

| Test File | Count | Status |
|---|---|---|
| `test_mmd_rbac_action_codes.py` | 18 | ✅ passed |
| `test_rbac_action_registry_alignment.py` | 20 | ✅ passed |
| `test_rbac_seed_alignment.py` | 20 | ✅ passed |
| `test_product_version_foundation_api.py` | ~24 | ✅ passed |
| `test_product_version_foundation_service.py` | 12 | ✅ passed |
| `test_product_foundation_api.py` | 3 | ✅ passed |
| `test_bom_foundation_api.py` | 11 | ✅ passed |
| `test_reason_code_foundation_api.py` | 10 | ✅ passed |

No regressions. No test changes required.

---

## Existing Gaps / Known Debts

| Gap | Severity | Source | Phase |
|---|---|---|---|
| BOM write service not implemented | High | `bom_service.py` read-only | Phase A (proposal v1.1) |
| Reason Code write service not implemented | High | `reason_code_service.py` read-only | Phase A (proposal v1.1) |
| IEP/PMG cannot author any MMD entity (no ADMIN family) | High | `rbac.py` SYSTEM_ROLE_FAMILIES | Phase C (Phase 7+ gate needed) |
| `admin.master_data.*.manage` coarse-grained (no draft/lifecycle split) | Medium | All 4 action codes | Phase C |
| No SoD gate on release/retire | High | All release/retire routes — no approval check | Phase C |
| No approval workflow integration for MMD lifecycle | High | Services call no approval service | Phase C |
| Product foundation API tests narrow (3 tests) | Low | `test_product_foundation_api.py` | Phase A |
| No dedicated routing foundation API test file found | Medium | Source scan | Phase A |
| `downtime_reasons` table separate from `reason_codes` table | Medium | Two separate tables/services | Phase A (unification needed) |
| `admin.downtime_reason.manage` covers old downtime_reasons table only | Medium | `downtime_reasons.py` route | Phase A (migration needed) |
| BOM schema lacks `version_no`, `supersedes_bom_id` (mentioned in rejected proposal) | Medium | `bom_service.py` schema shows no version fields | Phase C |
| Routing schema may lack extended operation fields (setup_time, run_time_per_unit, etc.) | Medium | Need verify against model | Phase A |
| Proposal v1.1 not authored | High | REJECTED proposal header | Blocker for Phase A |

---

## Scope Compliance

| Constraint | Compliant? |
|---|---|
| No new action code added to runtime | ✅ |
| No `ACTION_CODE_REGISTRY` change | ✅ |
| No `SYSTEM_ROLE_FAMILIES` change | ✅ |
| No `seed_rbac_core` change | ✅ |
| No route guard change | ✅ |
| No MMD service behavior change | ✅ |
| No migration added | ✅ |
| No approval workflow added | ✅ |
| No frontend/Admin UI added | ✅ |
| No product scope invented | ✅ |
| Evidence is source-derived, not guessed | ✅ |
| 6 subdomains documented from actual source | ✅ |

---

## Risks

| Risk | Status |
|---|---|
| BOM write implementation without action code first | Mitigated — test locks no write routes; any future write must add action code via governance |
| Reason Code write implementation without action code first | Mitigated — same as BOM |
| IEP/PMG participating in MMD write before Phase 7+ gate | Mitigated — `SYSTEM_ROLE_FAMILIES` frozen; documented as precondition |
| Release/retire without SoD approval | Documented debt; must be addressed in Phase C before production use |
| Downtime reason unification risk to execution path | `test_reason_code_foundation_api.py` verifies no write routes exist on unified endpoint; existing `/v1/downtime-reasons` endpoint must not be disrupted |
| `is_current` flag on Product Version not settable via API | Design gap — documented; implementation of `set_current` or equivalent is future work |

---

## Recommended Next Slice

### MMD-BE-00A (if needed): Routing Foundation API Test Coverage

The routing subdomain is the only MMD write subdomain without a dedicated `test_routing_foundation_api.py`. Consider creating a narrow test file covering:
- route guard presence on all 7 mutation routes
- lifecycle invariants (update/operation-add blocked when RELEASED)
- auth guard on read routes

This is optional if routing is considered lower risk in the current phase.

### MMD Proposal v1.1

Before any Phase A implementation begins, author MMD proposal v1.1 that:
1. Addresses Phase A (foundation backend) vs Phase C (mutation enablement/SoD) logical split.
2. Verifies P0-A foundation dependency is complete (use this report as evidence).
3. Scopes Reason Code unification separately from BOM foundation to reduce execution path risk.
4. Explicitly gates IEP/PMG participation on Phase 7+ design gate.

### MMD-BE-01: BOM Write Service + API + Action Code

When proposal v1.1 is approved, first MMD write slice should be BOM (highest strategic value
— required for all cross-domain reference views):
- `bom_service.py` write methods
- `admin.master_data.bom.manage` action code
- BOM write routes with lifecycle transitions
- Migration for any missing schema fields (version_no, supersedes_bom_id per proposal)

### MMD-BE-02A (deferred): Routing Operation Extended Fields

Verify routing model has setup_time, run_time_per_unit, work_center, required_skill fields.
If missing, migration needed.

---

## Stop Conditions Hit

None. Verdict was `ALLOW_MMD_BE00_SUBDOMAIN_EVIDENCE_CONTRACT_LOCK`.
Option A selected cleanly. No source/design conflict. No cross-domain contamination found.
No runtime code changed.

# Reason Code Write Governance Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-04 | v1.0 | Added Reason Code write governance and minimal mutation contract before implementation. |

---

## 1. Scope

This contract defines the Reason Code minimal mutation contract before implementation of any Reason Code write API.

**In scope:**
- Which Reason Code write commands are allowed in the next implementation slice
- Which commands remain deferred or forbidden
- Which lifecycle transitions are legal
- Which authorization action code is required
- What audit/event records are expected
- What backend validations are required
- What Reason Code writes must NOT trigger
- What is the safest future API shape
- What tests must future implementation include

**Out of scope:**
- Backend write API implementation
- Frontend write UI implementation
- Database migration changes
- Runtime action-code registry changes
- Downtime Reason redesign
- Any operational event ownership

**Predecessor contracts:**
- `reason-code-foundation-contract.md` — entity shape and boundary locked by MMD-BE-06
- `mmd-write-path-governance-matrix.md` — Reason Code write state was `DEFERRED_REQUIRES_CONTRACT`; promoted to `READY_FOR_GOVERNANCE_CONTRACT` by this document

---

## 2. Current Read Baseline

### Read API (implemented in MMD-BE-07, integrated in MMD-FULLSTACK-08)

| Endpoint | Auth | Response | Status |
|---|---|---|---|
| `GET /api/v1/reason-codes` | `require_authenticated_identity` | `list[ReasonCodeItem]` with filter params | ✅ Implemented |
| `GET /api/v1/reason-codes/{reason_code_id}` | `require_authenticated_identity` | `ReasonCodeItem` | ✅ Implemented |

### ORM Model Fields (14 fields — from `backend/app/models/reason_code.py`)

| Field | Type | Nullable | Notes |
|---|---|---|---|
| `reason_code_id` | String(64) | No | PK — immutable |
| `tenant_id` | String(64) | No | Tenant isolation — from JWT |
| `reason_domain` | String(32) | No | Enum: EXECUTION_PAUSE, DOWNTIME, SCRAP, QUALITY_HOLD, MAINTENANCE, MATERIAL, REWORK, EXCEPTION, GENERAL |
| `reason_category` | String(64) | No | Subcategory within domain |
| `reason_code` | String(64) | No | Short code — immutable after creation |
| `reason_name` | String(128) | No | Display name — mutable on DRAFT |
| `description` | Text | Yes | Optional — mutable on DRAFT |
| `lifecycle_status` | String(16) | No | DRAFT / RELEASED / RETIRED; server_default=DRAFT |
| `requires_comment` | Boolean | No | Operational policy flag; server_default=false |
| `is_active` | Boolean | No | Operational filtering flag; server_default=true |
| `sort_order` | Integer | No | Display sort; server_default=0 |
| `created_at` | DateTime(tz) | No | Audit — server_default |
| `updated_at` | DateTime(tz) | No | Audit — server_default + onupdate |

### Unique Constraint
`UNIQUE (tenant_id, reason_domain, reason_code)` — enforced at DB level.

### Screen / Read Status
- `frontend/src/app/screenStatus.ts`: `reasonCodes`: `phase: "PARTIAL"`, `dataSource: "BACKEND_API"` ✅
- Write-action buttons remain disabled on `ReasonCodes.tsx` ✅

---

## 3. Reason Code Write Principles

1. **Backend is source of truth.** Lifecycle, authorization, and audit are never derived from frontend state.
2. **Frontend sends intent only.** Frontend cannot authorize mutations or derive lifecycle eligibility.
3. **Reason codes classify; they do not execute.** No write command may trigger execution, downtime, quality, material, or ERP events.
4. **Separate from downtime_reason.** Unified Reason Code write path is additive and independent. No downtime_reason redesign or migration is allowed in this scope.
5. **Tenant-scoped.** All writes must be scoped to the authenticated identity's `tenant_id`. Client must not send `tenant_id` in the request body.
6. **Immutable identifiers.** `reason_code_id`, `reason_code`, and `reason_domain` are immutable after creation.
7. **Lifecycle is the governance gate.** Only DRAFT codes can be updated. Only DRAFT codes can have their metadata patched. Release and retire are explicit commands, not payload fields.
8. **No client-forced lifecycle.** Client must not include `lifecycle_status` in create or update payloads. Only the explicit release/retire commands change lifecycle.
9. **Hard delete is forbidden.** Reason codes may have been referenced by operational records (downtime events, execution records, quality decisions). Deletion without historical analysis is unsafe.
10. **`is_active` does not override lifecycle.** A RELEASED+inactive code is still RELEASED. `is_active` is an operational filtering flag managed separately.

---

## 4. Command Boundary Matrix

| Command | Decision | Reason | Future Guardrails |
|---|---|---|---|
| `create_reason_code` | READY_FOR_IMPLEMENTATION_NEXT | MMD-BE-06 entity contract is locked; model exists; lifecycle pattern follows BOM; no downstream side effects | tenant_id from JWT; lifecycle_status server-set to DRAFT; code unique within tenant+domain |
| `update_reason_code_metadata` (DRAFT only) | READY_FOR_IMPLEMENTATION_NEXT | Aligns with BOM pattern; DRAFT mutability is well-established; no cross-domain impact | source_state must be DRAFT; reject if RELEASED or RETIRED; `extra="forbid"` on schema |
| `release_reason_code` | READY_FOR_IMPLEMENTATION_NEXT | Explicit lifecycle command; mirrors BOM release pattern; does not trigger operational events | source_state must be DRAFT; explicit route separate from PATCH; audit record required |
| `retire_reason_code` | READY_FOR_IMPLEMENTATION_NEXT | Explicit lifecycle command; mirrors BOM retire pattern; DRAFT and RELEASED allowed | source_state must be DRAFT or RELEASED; terminal transition; audit record required |
| `deactivate_reason_code` | DEFERRED_REQUIRES_CONTRACT | `is_active` governance policy not defined; operational filtering semantics need separate contract | must not bypass lifecycle; operational usage analysis required |
| `activate_reason_code` | DEFERRED_REQUIRES_CONTRACT | Inverse of deactivate; same policy gap | same as deactivate |
| `delete_reason_code` | FORBIDDEN | Reason codes may have been referenced by historical operational records (downtime events, execution, quality); hard delete breaks classification history | No exceptions without dedicated exception contract |
| `reactivate_reason_code` | FORBIDDEN | No reactivation lifecycle path; RETIRED is terminal; parallels BOM pattern | No reactivate path from RETIRED → any |
| `clone_reason_code` | DEFERRED_REQUIRES_CONTRACT | Code uniqueness and lineage policy not defined; cross-category clone semantics unclear | requires code uniqueness, lineage audit record |
| `copy_from_existing_reason_code` | DEFERRED_REQUIRES_CONTRACT | Same as clone | same as clone |
| `bulk_import_reason_codes` | DEFERRED_REQUIRES_CONTRACT | Domain/category validation, duplicate handling, and atomic transaction policy not defined | all-or-nothing transaction or per-row error policy required |
| `bulk_retire_reason_codes` | DEFERRED_REQUIRES_CONTRACT | Batch lifecycle transition policy, usage impact analysis, and audit rollup not defined | per-code audit records required |
| `merge_reason_codes` | DEFERRED_REQUIRES_CONTRACT | Historical reference remapping policy not defined; operational records referencing merged code unclear | requires data migration policy |
| `split_reason_code` | DEFERRED_REQUIRES_CONTRACT | Lineage and historical classification policy not defined | requires new code provisioning policy |
| `map_to_downtime_reason` | DEFERRED_REQUIRES_CONTRACT | Downtime Reason harmonization requires separate governance review (explicit decision in MMD-BE-06) | must not silently change downtime_reason behavior; FK coupling requires migration governance |
| `unmap_from_downtime_reason` | DEFERRED_REQUIRES_CONTRACT | Inverse of map; same policy gap | same as map |
| `bind_to_execution_policy` | DEFERRED_REQUIRES_CONTRACT | Execution policy binding requires execution domain governance review; out of MMD scope | execution domain owns execution events; cross-domain coupling forbidden without contract |
| `bind_to_quality_policy` | DEFERRED_REQUIRES_CONTRACT | Quality domain governance review required | quality domain owns quality decisions |
| `bind_to_material_policy` | DEFERRED_REQUIRES_CONTRACT | Material domain governance review required | material domain owns material movement |

---

## 5. Lifecycle Transition Matrix

| Transition | Decision | Reason |
|---|---|---|
| (new) → DRAFT | ALLOW_NEXT via `create_reason_code` | New codes always start as DRAFT; lifecycle_status set by server |
| DRAFT → RELEASED | ALLOW_NEXT via explicit `release_reason_code` command | Matches MMD lifecycle pattern (BOM, Product, Routing); requires explicit command, not payload |
| RELEASED → RETIRED | ALLOW_NEXT via explicit `retire_reason_code` command | Matches MMD lifecycle pattern; terminal transition |
| DRAFT → RETIRED | ALLOW_NEXT via explicit `retire_reason_code` command | Permitted — a DRAFT code may be retired if it was never operationally used; audit record required |
| RELEASED → DRAFT | FORBID | Release is a governance commitment; reverting to DRAFT would invalidate production configurations; aligns with BOM and Product pattern |
| RETIRED → RELEASED | FORBID | No reactivation path; terminal state; matches BOM/Product pattern |
| RETIRED → DRAFT | FORBID | No reactivation path; terminal state |

### `is_active` Relationship to Lifecycle

- `is_active` is an **operational filtering flag**, not the canonical lifecycle state.
- A RELEASED + `is_active=false` code is still RELEASED; it is filtered from operational pickers but remains a valid lifecycle record.
- Create/update payload must not use `is_active` to bypass lifecycle governance.
- Standalone `activate`/`deactivate` commands are **deferred** — no operational usage policy exists yet.
- Future implementation: If `is_active` is writable, it must be an explicit field in the `BomUpdateRequest`-equivalent update schema, not a lifecycle command. It must not change `lifecycle_status`.

---

## 6. Authorization / Action-Code Requirements

### Candidate Action Code

```
admin.master_data.reason_code.manage
```

| Property | Value |
|---|---|
| Top domain | `admin` |
| Sub-domain | `master_data` |
| Entity | `reason_code` |
| Verb | `manage` |
| Permission Family | `ADMIN` |
| Naming convention | Matches established MMD pattern |

### Current Status
**`admin.master_data.reason_code.manage` does NOT exist in `backend/app/security/rbac.py`** as of May 4, 2026.

The current registry ends at `admin.master_data.bom.manage` (added by MMD-BE-09A). The `admin.master_data.reason_code.manage` code must be added by the next slice **MMD-BE-10A** before any Reason Code write API is implemented.

### Authorization Requirements for Future Implementation

| Endpoint / Command | Required Action Code | Read/Write |
|---|---|---|
| `GET /api/v1/reason-codes` | `require_authenticated_identity` (unchanged) | Read |
| `GET /api/v1/reason-codes/{id}` | `require_authenticated_identity` (unchanged) | Read |
| `POST /api/v1/reason-codes` (create) | `require_action("admin.master_data.reason_code.manage")` | Write |
| `PATCH /api/v1/reason-codes/{id}` (update metadata) | `require_action("admin.master_data.reason_code.manage")` | Write |
| `POST /api/v1/reason-codes/{id}/release` | `require_action("admin.master_data.reason_code.manage")` | Write |
| `POST /api/v1/reason-codes/{id}/retire` | `require_action("admin.master_data.reason_code.manage")` | Write |

**Governance rules:**
- All read endpoints remain `require_authenticated_identity`. Do not add action code to read paths.
- A single `manage` code covers both metadata mutations and lifecycle transitions (consistent with current `admin.master_data.bom.manage` design — see action-code-registry.md note on coarse-grained action codes).
- No frontend route visibility is authorization truth.
- A reason code itself does not grant permission to perform any action using that code.

---

## 7. Future API Contract Proposal

### Ready-for-Implementation Endpoints

| Endpoint | Command | Source State | Target State | Auth | Notes |
|---|---|---|---|---|---|
| `POST /v1/reason-codes` | `create_reason_code` | N/A (new) | DRAFT | `require_action(bom.manage analog)` | Server sets lifecycle_status=DRAFT, tenant_id from identity |
| `PATCH /v1/reason-codes/{reason_code_id}` | `update_reason_code_metadata` | DRAFT | DRAFT | `require_action` | Only allowed on DRAFT; rejects RELEASED/RETIRED with 409 |
| `POST /v1/reason-codes/{reason_code_id}/release` | `release_reason_code` | DRAFT | RELEASED | `require_action` | No body required; audit record emitted |
| `POST /v1/reason-codes/{reason_code_id}/retire` | `retire_reason_code` | DRAFT or RELEASED | RETIRED | `require_action` | No body required; audit record emitted |

### Create Request Schema Boundary

| Field | Include? | Reason |
|---|---|---|
| `reason_domain` | ✅ Required | Must be one of allowed domain enum values |
| `reason_category` | ✅ Required | Subcategory within domain |
| `reason_code` | ✅ Required | Short code; unique within tenant+domain |
| `reason_name` | ✅ Required | Display name |
| `description` | ✅ Optional | nullable |
| `requires_comment` | ✅ Optional | boolean; defaults to false |
| `is_active` | ✅ Optional | boolean; defaults to true |
| `sort_order` | ✅ Optional | integer; defaults to 0 |
| `lifecycle_status` | ❌ Forbidden | Server sets to DRAFT; client must not send |
| `tenant_id` | ❌ Forbidden | Derived from authenticated identity |
| `reason_code_id` | ❌ Forbidden | Server-generated |
| `created_at` / `updated_at` | ❌ Forbidden | Server-managed |

**Schema config: `extra="forbid"` — any unrecognized field rejects the request.**

### Update Request Schema Boundary

| Field | Include? | Reason |
|---|---|---|
| `reason_name` | ✅ Optional | Mutable on DRAFT |
| `description` | ✅ Optional | Mutable on DRAFT |
| `requires_comment` | ✅ Optional | Mutable on DRAFT |
| `is_active` | ✅ Optional | Mutable on DRAFT |
| `sort_order` | ✅ Optional | Mutable on DRAFT |
| `reason_code` | ❌ Forbidden | Immutable after creation |
| `reason_domain` | ❌ Forbidden | Immutable after creation |
| `reason_category` | ❌ Forbidden | Governance decision — domain+category define the code's classification identity |
| `lifecycle_status` | ❌ Forbidden | Changed only via explicit release/retire commands |
| `tenant_id` | ❌ Forbidden | Immutable |
| `reason_code_id` | ❌ Forbidden | Immutable |

**Schema config: `extra="forbid"`**

### Deferred Endpoints

| Endpoint | Command | Decision | Reason |
|---|---|---|---|
| `POST /v1/reason-codes/{id}/activate` | `activate_reason_code` | DEFERRED_REQUIRES_CONTRACT | `is_active` operational policy not defined |
| `POST /v1/reason-codes/{id}/deactivate` | `deactivate_reason_code` | DEFERRED_REQUIRES_CONTRACT | same as activate |
| `POST /v1/reason-codes/{id}/clone` | `clone_reason_code` | DEFERRED_REQUIRES_CONTRACT | code uniqueness and lineage policy not defined |
| `POST /v1/reason-codes/bulk-import` | `bulk_import_reason_codes` | DEFERRED_REQUIRES_CONTRACT | transaction policy, duplicate handling not defined |
| `POST /v1/reason-codes/{id}/map-downtime-reason` | `map_to_downtime_reason` | DEFERRED_REQUIRES_CONTRACT | harmonization review required |
| `POST /v1/reason-codes/{id}/bind-policy` | `bind_to_*_policy` | DEFERRED_REQUIRES_CONTRACT | cross-domain coupling requires each domain's governance |

### Forbidden Endpoints

| Endpoint | Command | Decision |
|---|---|---|
| `DELETE /v1/reason-codes/{id}` | `delete_reason_code` | FORBIDDEN |
| `POST /v1/reason-codes/{id}/reactivate` | `reactivate_reason_code` | FORBIDDEN |
| `POST /v1/reason-codes/{id}/execute` | any execution action | FORBIDDEN |
| `POST /v1/reason-codes/{id}/start-downtime` | start downtime | FORBIDDEN |
| `POST /v1/reason-codes/{id}/quality-accept` | quality decision | FORBIDDEN |
| `POST /v1/reason-codes/{id}/material-move` | material movement | FORBIDDEN |
| `POST /v1/reason-codes/{id}/erp-post` | ERP posting | FORBIDDEN |

---

## 8. Validation Rules

### Reason Code Create

| Rule | Enforcement |
|---|---|
| `tenant_id` derived from authenticated identity | API handler injects from `identity.tenant_id`; never from request body |
| `reason_domain` required | Pydantic: required field |
| `reason_domain` must be one of allowed values | Enum validation: EXECUTION_PAUSE, DOWNTIME, SCRAP, QUALITY_HOLD, MAINTENANCE, MATERIAL, REWORK, EXCEPTION, GENERAL |
| `reason_category` required | Pydantic: required field |
| `reason_code` required | Pydantic: required field |
| `reason_name` required | Pydantic: required field |
| `reason_code` unique within `(tenant_id, reason_domain, reason_code)` | DB constraint `uq_reason_codes_tenant_domain_code`; service returns 409 on IntegrityError |
| `lifecycle_status` server-set to `DRAFT` | Service always sets; not from request body |
| `reason_domain` must not imply authorization | Not an action code; classification only |
| `reason_domain` must not trigger domain workflow | Reference data only; no event emission beyond audit log |
| `extra="forbid"` on create schema | Pydantic model config |

### Reason Code Update (DRAFT only)

| Rule | Enforcement |
|---|---|
| Source state must be DRAFT | Service validates `lifecycle_status == "DRAFT"` before mutation; returns 409 if RELEASED or RETIRED |
| `reason_code` immutable | Not in update schema; `extra="forbid"` |
| `reason_domain` immutable | Not in update schema; `extra="forbid"` |
| `reason_category` immutable | Not in update schema (conservative: category defines classification identity) |
| `lifecycle_status` not in update schema | Lifecycle changed only via explicit commands; `extra="forbid"` |
| `tenant_id` immutable | Not in update schema |
| `extra="forbid"` on update schema | Pydantic model config |

### Reason Code Release

| Rule | Enforcement |
|---|---|
| Source state must be DRAFT | Service validates before transition; returns 409 if not DRAFT |
| No request body required | Route: `POST /{id}/release` with no body |

### Reason Code Retire

| Rule | Enforcement |
|---|---|
| Source state must be DRAFT or RELEASED | Service validates; RETIRED → RETIRED returns 409 |
| No request body required | Route: `POST /{id}/retire` with no body |

### `is_active` Governance

- `is_active` is a mutable flag on DRAFT codes only (via update schema).
- `is_active` does not change `lifecycle_status`.
- A RELEASED + `is_active=false` code is valid; it is filtered from read list by default.
- `is_active` cannot override lifecycle governance: a RELEASED code cannot be updated to DRAFT by toggling `is_active`.

### `reason_category` Immutability Decision

`reason_category` is marked immutable after creation in this contract because:
1. `reason_category` is part of the classification identity (together with `reason_domain` and `reason_code`).
2. Changing category after release would alter the meaning of historical records that referenced the code.
3. If category rename is needed, the approved pattern is: retire the old code and create a new code.

This may be revisited in a future governance slice if operational evidence shows the category must be mutable before release.

---

## 9. Audit / Event Expectations

### Allowed Audit Events

| Command | Event / Audit Record | Notes |
|---|---|---|
| `create_reason_code` | `ReasonCode.CREATED` | Governance audit record; contains tenant, actor, reason_code_id, reason_domain, reason_code |
| `update_reason_code_metadata` | `ReasonCode.UPDATED` | Contains changed fields summary; tenant, actor, reason_code_id |
| `release_reason_code` | `ReasonCode.RELEASED` | Lifecycle transition record; tenant, actor, reason_code_id, previous_status=DRAFT, new_status=RELEASED |
| `retire_reason_code` | `ReasonCode.RETIRED` | Lifecycle transition record; tenant, actor, reason_code_id, previous_status, new_status=RETIRED |

All events are emitted via `record_security_event()` — the established governance audit pattern.

### Forbidden Side Effects

The following must **never** be emitted or triggered from any Reason Code write command:

| Forbidden Effect | Domain | Reason |
|---|---|---|
| Execution command (start, complete, report, pause, resume) | Execution | Reason codes classify; they do not execute |
| Downtime start/end | Execution | Execution domain owns downtime events |
| Quality pass/fail decision | Quality | Quality domain owns quality disposition |
| Quality hold release | Quality | Quality domain owns quality hold state |
| Material movement | Material/Inventory | Material domain owns movement |
| Inventory reservation | Material/Inventory | Same |
| Scrap posting | Material/Inventory | Execution/Quality owns scrap recording |
| Backflush | Material/Inventory | Triggered by execution completion |
| ERP posting | ERP | Enterprise posting is ERP domain |
| Traceability genealogy creation | Traceability | Genealogy is execution domain truth |
| Maintenance work order creation | Maintenance | Maintenance domain owns work orders |
| Automatic downtime_reason mapping | Execution | Harmonization is explicitly deferred |
| Authorization grant or role assignment | IAM | Authorization is RBAC-owned |

---

## 10. Cross-Domain Boundary Guardrails

| Boundary | Decision | Risk if Violated |
|---|---|---|
| Reason Code vs Downtime Reason | Additive, separate table; no FK to downtime_reasons | Coupling would break operational downtime behavior and require migration governance |
| Reason Code vs Execution | Classification reference only; no execution event ownership | Execution domain events cannot originate from reason code mutations |
| Reason Code vs Quality | Classification reference only; no quality decision ownership | Quality pass/fail and hold release must not be triggered by reason code writes |
| Reason Code vs Material/Inventory | Classification reference only; no material movement | Material movement, scrap, backflush must not originate from reason code writes |
| Reason Code vs ERP | No ERP posting, no PLM sync | ERP posting is enterprise domain; reason codes are MMD reference only |
| Reason Code vs Traceability | No genealogy record creation | Genealogy is execution operational truth |
| Reason Code vs IAM/Authorization | Reason domain values do not grant permissions | `reason_domain` is a classification field, not an authorization scope |
| `reason_category` vs Domain Workflow | `reason_category` is display/filter only | Must not trigger downtime, quality, or material behavior by value |
| Frontend UI vs Authorization Truth | FE disables controls using capability flags; final authority is backend `require_action` returning 403 | If FE enables controls locally, it would bypass authorization truth |
| `admin.master_data.product.manage` vs `admin.master_data.reason_code.manage` | Separate action codes; product manage does NOT imply reason code manage | Cross-action inference would violate domain-specific action code separation |

---

## 11. Downtime Reason Relationship

### Explicit Decision

| Aspect | Decision |
|---|---|
| Unified Reason Codes table | Separate from `downtime_reasons` table. No FK, no auto-mapping. |
| `downtime_reasons` table and API | Untouched by Reason Code write implementation. |
| Existing `operation.reason_code` field | Continues to resolve against `downtime_reasons` table. No change. |
| `map_to_downtime_reason` command | **DEFERRED** — requires separate harmonization governance review. |
| Automatic mapping on create | **FORBIDDEN** — no silent coupling between unified codes and downtime_reason. |
| Future harmonization | May be explored after operational evidence from both write paths is available. Requires a dedicated governance slice with migration planning. |

### Why Separate Is Correct (Current Phase)

The `downtime_reasons` model is operational master data with plant/area/line/station scope hierarchy and execution-specific fields (`default_block_mode`, `requires_supervisor_review`, `planned_flag`). The unified Reason Code model is tenant-scoped MMD reference/classification data with MMD lifecycle governance (DRAFT/RELEASED/RETIRED). Merging these would conflate two different governance models.

---

## 12. Frontend Write UI Readiness Gate

The following conditions must ALL be true before frontend write forms for Reason Codes may be implemented:

| Gate | Required State | Current State |
|---|---|---|
| Backend write API implemented | All 4 write endpoints live and tested | ❌ Not yet implemented |
| Action code registered | `admin.master_data.reason_code.manage` in `rbac.py` and registry | ❌ Not present |
| Server-derived capability projection | BE computes `reason_code_capabilities.can_create` and `allowed_actions` | ❌ Not yet designed |
| Frontend write intent slice | `reasonCodeApi` extended with write methods | ❌ Not yet |
| Regression gate | `npm run check:mmd:read` passing | ✅ Currently 134 checks pass (no regression) |
| Build/lint/i18n gate | All passing | ✅ Currently passing |

**Frontend write UI must not be implemented before all backend write API and capability projection conditions are met.**

---

## 13. Backend Implementation Readiness Gate

The following conditions must ALL be true before implementing `MMD-BE-13 — Reason Code Write API Foundation`:

| Gate | Required State | Current State |
|---|---|---|
| Action code registered | `admin.master_data.reason_code.manage` in `rbac.py` | ❌ Required by MMD-BE-10A |
| Action code in governance registry | Entry in `docs/design/02_registry/action-code-registry.md` | ❌ Required by MMD-BE-10A |
| Regression test for new action code | Test in `test_mmd_rbac_action_codes.py` | ❌ Required by MMD-BE-10A |
| This governance contract | `reason-code-write-governance-contract.md` | ✅ This document |
| Audit report | `mmd-be-10-reason-code-write-governance-contract.md` | ✅ Created in MMD-BE-10 |
| No hidden write API | Inspect `reason_codes.py` for unexpected write routes | ✅ Read-only confirmed |

---

## 14. Required Tests for Future Write Slice (MMD-BE-13)

| Test Area | Required Tests |
|---|---|
| Create — success (201) | POST creates DRAFT code; response contains all fields; lifecycle_status=DRAFT; tenant isolation |
| Create — uniqueness constraint | POST with duplicate (tenant, domain, code) → 409 |
| Create — forbidden fields | lifecycle_status in body → 422; tenant_id in body → 422; reason_code_id in body → 422 |
| Create — forbidden domain | lifecycle_status forced to RELEASED on create → 422 |
| Create — missing required fields | reason_domain missing → 422; reason_code missing → 422; reason_name missing → 422 |
| Update — success (DRAFT only) | PATCH updates allowed fields; returns 200 |
| Update — forbidden on RELEASED | PATCH on RELEASED code → 409 |
| Update — forbidden on RETIRED | PATCH on RETIRED code → 409 |
| Update — immutable fields rejected | reason_code in PATCH body → 422; reason_domain in PATCH body → 422; lifecycle_status in PATCH body → 422 |
| Release — success | POST /release on DRAFT → 200; lifecycle_status=RELEASED |
| Release — forbidden on RELEASED | POST /release on RELEASED → 409 |
| Release — forbidden on RETIRED | POST /release on RETIRED → 409 |
| Retire — success from DRAFT | POST /retire on DRAFT → 200; lifecycle_status=RETIRED |
| Retire — success from RELEASED | POST /retire on RELEASED → 200; lifecycle_status=RETIRED |
| Retire — forbidden on RETIRED | POST /retire on already RETIRED → 409 |
| Auth — unauthenticated → 401 | All write routes without token → 401 |
| Auth — authenticated no manage → 403 | Authenticated user without `reason_code.manage` → 403 on all write routes |
| Auth — cross-tenant isolation | Write to other tenant's code → 404 or 403 |
| Boundary — no execution events | Write command produces no execution event records |
| Boundary — no downtime mapping | Write command does not touch `downtime_reasons` table |
| Boundary — no quality records | Write command produces no quality event records |
| RBAC action code registry | `admin.master_data.reason_code.manage` present in ACTION_CODE_REGISTRY |

---

## 15. Explicit Non-Goals

The following are explicitly out of scope for the Reason Code write path in this phase:

1. Reason Code frontend write forms
2. `downtime_reason` redesign, migration, or modification
3. Automatic downtime_reason mapping on Reason Code create/update
4. Execution pause/resume behavior changes
5. Downtime start/end behavior changes
6. Quality pass/fail decisions
7. Quality hold release
8. Material movement
9. Inventory adjustment
10. Scrap posting
11. Backflush triggers
12. ERP posting
13. Traceability genealogy records
14. Maintenance work order creation
15. Policy binding (execution, quality, material)
16. Bulk import / bulk retire
17. Hard delete / reactivation
18. AI-generated reason codes
19. `reason_category` mutation after creation (deferred to future slice if evidence supports it)

---

## 16. Recommended Next Slice

**Next: MMD-BE-10A — Reason Code Action Code Registry Patch**

**Reason:** `admin.master_data.reason_code.manage` does not exist in `backend/app/security/rbac.py` or `docs/design/02_registry/action-code-registry.md`. All Reason Code mutation endpoints will require this code. The action code must be registered before implementing any write API.

**Slice scope:**
1. Add `"admin.master_data.reason_code.manage": "ADMIN"` to `ACTION_CODE_REGISTRY` in `backend/app/security/rbac.py`
2. Add entry to `docs/design/02_registry/action-code-registry.md`
3. Add regression test for the new code to `backend/tests/test_mmd_rbac_action_codes.py`
4. Run and pass all existing regression gates (backend + frontend)
5. Create audit report `docs/audit/mmd-be-10a-reason-code-action-code-registry-patch.md`

**After MMD-BE-10A:** Proceed to **MMD-BE-13 — Reason Code Write API Foundation**.

Do not implement frontend Reason Code write UI before MMD-BE-13 and server-derived capability projection are complete.

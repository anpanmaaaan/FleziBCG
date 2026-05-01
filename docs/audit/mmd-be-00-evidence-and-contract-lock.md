# MMD-BE-00 Evidence & Contract Lock

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Initial evidence audit per PO-SA review. Source-only inspection. No code changes. |

---

## 1. Executive Verdict

### 1.1 One-line summary

MMD backend foundation **partially ready** for read/list/detail expansion, but **NOT ready** for release/retire/approval/versioning rollout. 3 high-severity blockers identified that must be resolved before any Phase C-style work.

### 1.2 Top findings

| # | Finding | Severity | Implication |
|---|---|---|---|
| F1 | `approval_service.py` is **NOT generic** — only supports 6 hardcoded action types (QC_HOLD/QC_RELEASE/SCRAP/REWORK/WO_SPLIT/WO_MERGE). Master data resource_type not in scope. | **P1 BLOCKER** | Phase C (release/retire approval) of proposal v1.0 cannot start without extending approval service. |
| F2 | `release_product` / `release_routing` / `retire_product` / `retire_routing` **already exist as direct mutation paths**, NOT gated by approval. | **P1 BLOCKER (governance debt)** | Anyone with `admin.user.manage` can currently release/retire master data without SoD. Pre-existing debt, not introduced by proposal. |
| F3 | `ACTION_CODE_REGISTRY` is hardcoded Python dict in `app/security/rbac.py` — **no `admin.master_data.*` action codes registered**. All MMD APIs use `admin.user.manage` placeholder. | **P1 HIGH** | Phase A.5 (permission code fix) requires source code edit + re-seed of RBAC, not just config. |
| F4 | All MMD repositories use `db.commit()` immediately after add/update — same atomicity concern as Slice 0 event envelope proposal. | **P2 MEDIUM** | Service layer cannot wrap event-write + snapshot-update in single transaction. |
| F5 | Scope hierarchy infrastructure exists (`Scope` table with tenant/plant/area/line/station/equipment), but MMD entities (Product, Routing, BOM, ResourceRequirement) are **only tenant-scoped** — no plant/line/station scope binding. | **P2 MEDIUM** | Future scope-aware MMD authorization not possible without schema extension. |
| F6 | Resource Requirement API **does exist** but nested under `/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements`, not at `/v1/resource-requirements` (as MMD report assumed). | **P3 INFO** | Frontend client gap is correct, but BE infrastructure largely complete. |
| F7 | DowntimeReason model has scope hierarchy columns (`plant_code, area_code, line_code, station_scope_value`) **declared but unused** by current resolver. Pre-existing master-data debt. | **P3 INFO** | Reason code unification slice (MMD-BE-04) must decide: preserve, drop, or activate these columns. |
| F8 | Routing model **lacks** the extended operation fields (`setup_time, run_time_per_unit, work_center, required_skill, required_skill_level, qc_checkpoint_count`) that MMD report expects. Mock fixture has them; backend doesn't. | **P2 MEDIUM** | MMD-BE-01 (Routing Operation Extended Read) requires schema migration + service change, not just response shape. |
| F9 | Alembic baseline (`0001_baseline.py`) is **intentional no-op** — schema established by `Base.metadata.create_all()` + 12 SQL migration scripts in `backend/scripts/migrations/`. Future changes via `alembic revision --autogenerate`. | **P2 MEDIUM** | Migration posture is non-standard. Care needed when adding columns; cannot rely on autogenerate without verifying baseline state. |

### 1.3 Recommended approval direction

**Approve** start of MMD-BE-01 (Routing Operation Extended Read) **with scope correction** — it requires schema migration, not just response shape change. Recommended slice ordering revision in Section 15.

**Defer until F1-F3 resolved:**

- Release/retire flows for any new MMD domain (BOM).
- Permission code fix (F3) requires Action Registry path verified.
- Approval workflow integration for MMD (F1) requires approval_service generic extension.

---

## 2. Source Areas Inspected

All paths relative to `G:\Work\FleziBCG\`.

### 2.1 Models

| File | Status |
|---|---|
| `backend/app/models/product.py` | Inspected via service layer references |
| `backend/app/models/routing.py` | Fully inspected (61 lines) |
| `backend/app/models/resource_requirement.py` | Fully inspected (44 lines) |
| `backend/app/models/downtime_reason.py` | Fully inspected (63 lines) |
| `backend/app/models/security_event.py` | Fully inspected (24 lines) |
| `backend/app/models/approval.py` | Fully inspected (102 lines) |
| `backend/app/models/master.py` | Listed only — Not verified content |
| `backend/app/models/rbac.py` | Inspected via security/rbac.py imports — Not directly read |

### 2.2 Services

| File | Status |
|---|---|
| `backend/app/services/product_service.py` | Fully inspected (276 lines) |
| `backend/app/services/routing_service.py` | Fully inspected (510 lines) |
| `backend/app/services/resource_requirement_service.py` | Fully inspected (386 lines) |
| `backend/app/services/downtime_reason_service.py` | Fully inspected (75 lines) |
| `backend/app/services/security_event_service.py` | Fully inspected (42 lines) |
| `backend/app/services/approval_service.py` | Fully inspected (224 lines) |

### 2.3 Repositories

| File | Status |
|---|---|
| `backend/app/repositories/routing_repository.py` | Fully inspected (96 lines) |
| `backend/app/repositories/product_repository.py` | Not directly read — pattern inferred from service usage |
| `backend/app/repositories/resource_requirement_repository.py` | Not directly read — pattern inferred |
| `backend/app/repositories/downtime_reason_repository.py` | Not directly read — pattern inferred |
| `backend/app/repositories/security_event_repository.py` | Not directly read — interface inferred from service |
| `backend/app/repositories/approval_repository.py` | Not directly read — interface inferred from service |

### 2.4 API endpoints

| File | Status |
|---|---|
| `backend/app/api/v1/products.py` | Fully inspected (129 lines) |
| `backend/app/api/v1/routings.py` | Fully inspected (340 lines, includes resource-requirements nested routes) |
| `backend/app/api/v1/downtime_reasons.py` | Fully inspected (80 lines) |

### 2.5 Security / RBAC

| File | Status |
|---|---|
| `backend/app/security/dependencies.py` | Fully inspected (221 lines) |
| `backend/app/security/rbac.py` | Fully inspected (639 lines) |
| `backend/app/security/auth.py` | Listed only — Not verified |

### 2.6 Migration

| File | Status |
|---|---|
| `backend/alembic/versions/0001_baseline.py` | Fully inspected (40 lines) |
| `backend/alembic/env.py` | Listed only — Not verified |
| `backend/scripts/migrations/0001-0012*` | Listed in baseline comment — Not verified content |

---

## 3. Product Domain Evidence

### 3.1 Lifecycle

Confirmed 3-state lifecycle: `DRAFT → RELEASED → RETIRED`. Evidence: `product_service.py:130` (default `DRAFT` on create), `:236` (only DRAFT can release), `:262` (already RETIRED check).

### 3.2 Versioning

**No version_no field. No supersedes_id field.** Lifecycle is the only version concept.

Evidence: schema fields list at `product_service.py:39-51` (`_to_item`) — only `product_id, tenant_id, product_code, product_name, product_type, lifecycle_status, description, display_metadata, created_at, updated_at`. Schema in `schemas/product.py` Not directly verified but service signature confirms.

### 3.3 Lifecycle invariants (already implemented)

- `product_code` unique per tenant (`product_service.py:120-122`).
- RETIRED cannot be updated (`product_service.py:165-166`).
- RELEASED cannot have `product_code` or `product_type` changed — structural protection (`product_service.py:174-175, 185-186`).
- Only DRAFT can be released (`product_service.py:235-236`).
- Already RETIRED cannot retire again (`product_service.py:262-263`).

### 3.4 Audit

Audit emitted via `_emit_product_event` → `record_security_event` (`product_service.py:58-89`). Event types: `PRODUCT.CREATED`, `PRODUCT.UPDATED`, `PRODUCT.RELEASED`, `PRODUCT.RETIRED`. Detail JSON includes `product_id, product_code, lifecycle_status, changed_fields, occurred_at, event_name_status`.

### 3.5 Authorization (current placeholder)

All mutating endpoints use `require_action("admin.user.manage")`:

- `products.py:55` create
- `products.py:75` update
- `products.py:97` release
- `products.py:116` retire

`admin.user.manage` is an `ADMIN` family action (`rbac.py:55`). **Semantic mismatch.**

### 3.6 Tenant isolation

Verified — all queries filter by `tenant_id`. Service explicitly threads `tenant_id` from `RequestIdentity` through to repository (`products.py:32, 43, 60`). Repository layer assumed to honor (Not directly verified for product_repository).

### 3.7 Release/retire path

**DIRECT mutation, no approval gate.** `release_product()` (`product_service.py:224-248`) immediately mutates `lifecycle_status` and commits via `update_product_row`. Same for `retire_product` (`:251-275`). No call to `approval_service`.

**This is the F2 governance debt.** Existing in source today.

---

## 4. Routing Domain Evidence

### 4.1 Lifecycle

Same 3-state as Product: `DRAFT → RELEASED → RETIRED`. Evidence: `routing_service.py:204` default DRAFT, `:466` only DRAFT can release, `:495` already RETIRED check.

### 4.2 Versioning

**No version_no field. No supersedes_id field.** Same as Product. Schema fields confirmed at `routing_service.py:80-92` (`_to_item`): `routing_id, tenant_id, product_id, routing_code, routing_name, lifecycle_status, operations[], created_at, updated_at`.

### 4.3 Routing model schema

Verified in `models/routing.py`:

- Routing: `routing_id (PK), tenant_id (indexed), product_id (FK indexed), routing_code, routing_name, lifecycle_status, created_at, updated_at`. Unique constraint `(tenant_id, routing_code)`.
- RoutingOperation: `operation_id (PK), tenant_id (indexed), routing_id (FK indexed), operation_code, operation_name, sequence_no, standard_cycle_time, required_resource_type, created_at, updated_at`. Unique constraint `(routing_id, sequence_no)`.

### 4.4 Routing extended operation fields — MISSING

Routing operation model (`models/routing.py:39-60`) has **only**: `operation_code, operation_name, sequence_no, standard_cycle_time, required_resource_type`.

**Missing fields** (per MMD report's `RoutingOperationItemFromAPI` mock):

- `setup_time`
- `run_time_per_unit`
- `work_center`
- `required_skill`
- `required_skill_level`
- `qc_checkpoint_count`

→ MMD-BE-01 is NOT a "response shape extension". It is a **schema migration + model change + repository update + service projection update**. Significantly larger than initially scoped.

### 4.5 Lifecycle invariants

- `routing_code` unique per tenant (`routing_service.py:194-196`).
- RETIRED cannot be updated (`routing_service.py:231-232`).
- RELEASED cannot have `routing_code` or `product_id` changed (`routing_service.py:238-239, 248-249`).
- Routing operations can only be added/updated/removed in DRAFT (`routing_service.py:167-169` `_ensure_draft_for_operation_mutation`).
- Sequence_no unique per routing (`routing_service.py:300, 378`).
- Product link validation: linked product cannot be RETIRED (`routing_service.py:57-63`).
- Only DRAFT can be released (`routing_service.py:465-466`).
- Release re-validates product link (`routing_service.py:468`).

### 4.6 Audit

Same pattern as Product. Event types: `ROUTING.CREATED, ROUTING.UPDATED, ROUTING.RELEASED, ROUTING.RETIRED, ROUTING.OPERATION_ADDED, ROUTING.OPERATION_UPDATED, ROUTING.OPERATION_REMOVED`. Code at `routing_service.py:95-164`.

### 4.7 Authorization

Same `admin.user.manage` placeholder. All mutation endpoints in `routings.py` use `require_action("admin.user.manage")` (`routings.py:72, 91, 115, 139, 163, 183, 202, 267, 296, 325`).

### 4.8 Tenant isolation

Verified at repository layer (`routing_repository.py`). Every query filters `Routing.tenant_id == tenant_id`. Operations also include `tenant_id` filter (`:43-44`).

### 4.9 Release/retire — direct mutation

Same as Product. No approval gate. `release_routing()` (`:452-481`), `retire_routing()` (`:484-509`).

### 4.10 Repository commit pattern — concern

`routing_repository.py:67-71, 74-77, 80-84, 87-90, 93-95` — every mutation function calls `db.commit()` immediately. Service layer cannot wrap multi-step operations in a single transaction.

Example: `add_routing_operation` (`routing_service.py:277-329`) does:

1. Read routing (1 query)
2. Read operation by sequence (1 query)
3. Create operation (1 commit via repository)
4. Re-read routing (1 query)
5. Emit security event (1 commit via security_event_service)

**Two separate commits** for one logical operation. If commit 2 fails after commit 1, audit is lost but operation persists.

This matches root cause A from Slice 0 event envelope proposal.

---

## 5. Resource Requirement Evidence

### 5.1 Model

`models/resource_requirement.py:12-43`:

- `requirement_id (PK), tenant_id (indexed), routing_id (FK indexed), operation_id (FK indexed), required_resource_type, required_capability_code, quantity_required, notes, metadata_json, created_at, updated_at`.
- Unique constraint: `(tenant_id, operation_id, required_resource_type, required_capability_code)`.

### 5.2 Lifecycle

**No lifecycle column.** Resource Requirement is **not lifecycle-managed** as DRAFT/RELEASED/RETIRED. It inherits governance from parent Routing — only mutable when parent Routing is DRAFT (`resource_requirement_service.py:97-99`).

→ This is a **valid design choice** but conflicts with proposal v1.0 assumption that ResourceRequirement needs DRAFT/RELEASED/RETIRED. Decision needed: keep inherited governance, or add own lifecycle.

### 5.3 Validation

- `required_resource_type` whitelisted: `WORK_CENTER, STATION_CAPABILITY, EQUIPMENT_CAPABILITY, OPERATOR_SKILL, TOOLING` (`resource_requirement_service.py:29-35, 64-68`).
- `quantity_required > 0` (`:71-74`).
- Unique key check (`:215-223`).
- Routing must exist + be DRAFT (`:84-100`).

### 5.4 Audit

Event types: `RESOURCE_REQUIREMENT.CREATED, RESOURCE_REQUIREMENT.UPDATED, RESOURCE_REQUIREMENT.REMOVED` (`resource_requirement_service.py:241, 343, 380`).

### 5.5 API endpoints — already exposed

In `routings.py:217-339`:

- `GET /v1/routings/{routing_id}/operations/{operation_id}/resource-requirements`
- `GET /v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}`
- `POST /v1/routings/{routing_id}/operations/{operation_id}/resource-requirements`
- `PATCH /v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}`
- `DELETE /v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}`

→ **Backend is more complete than MMD report suggested.** The "missing API" is missing **frontend client**, not backend endpoint. Path is nested under routing, not at top-level `/v1/resource-requirements`.

### 5.6 Tenant isolation

Verified — `tenant_id` threaded through every call (`:163, 175, 217, 252`).

---

## 6. Reason / Downtime Evidence

### 6.1 Model — DowntimeReason only

`models/downtime_reason.py:27-62`:

- `id (PK auto), tenant_id, plant_code/area_code/line_code/station_scope_value (nullable scope), reason_code, reason_name, reason_group, planned_flag, default_block_mode, requires_comment, requires_supervisor_review, active_flag, sort_order, created_at, updated_at`.
- `reason_group` is enum: `BREAKDOWN, MATERIAL, QUALITY, CHANGEOVER, PLANNED_STOP, UTILITIES, OTHER` (`models/downtime_reason.py:17-24`).

**No unified `reason_codes` table for other domains** (scrap/pause/reopen/quality_hold). Confirmed via service inspection.

### 6.2 Scope hierarchy columns — declared but unused

`models/downtime_reason.py:33-39`:

```
plant_code, area_code, line_code, station_scope_value (all nullable)
```

Comment at `:33-35`: *"baseline resolver only uses tenant_id + reason_code. Narrower scoped rows are master-data debt tracked in the refactor review note."*

→ **Pre-existing tech debt.** Reason code unification slice (MMD-BE-04) must decide what to do with these columns.

### 6.3 Service operations

Only 3 functions in `downtime_reason_service.py`:

- `list_downtime_reasons` (read, filtered by `active_flag`)
- `upsert_downtime_reason` (no DRAFT/RELEASED/RETIRED — direct upsert)
- `deactivate_downtime_reason` (sets `active_flag=False`, not RETIRED state)

→ **No 3-state lifecycle.** Active/inactive flag only.

### 6.4 Audit

Event types: `MASTER.DOWNTIME_REASON_UPSERT, MASTER.DOWNTIME_REASON_DEACTIVATE` (`downtime_reason_service.py:44, 70`). Different naming convention from Product/Routing (uses `MASTER.` prefix vs `PRODUCT./ROUTING.`).

→ Naming convention inconsistency. Worth aligning during unification.

### 6.5 API

`/v1/downtime-reasons` GET (active list), POST (upsert, requires `admin.user.manage`), `/{reason_code}/deactivate` POST (requires `admin.user.manage`). Code at `downtime_reasons.py:33-79`.

### 6.6 Station Execution downtime path — operationally critical

The GET endpoint at `downtime_reasons.py:33-45` is consumed by Station Execution `StartDowntimeDialog`. Comment notes: *"This is the canonical source for the FE Start-Downtime picker. Clients must submit the chosen reason_code on start_downtime."*

→ **Any unification slice MUST preserve this exact response contract**, or break Station Execution. Mandatory regression test.

---

## 7. Tenant / Scope Isolation Evidence

### 7.1 Tenant isolation — STRONG

Pattern verified across all MMD services and repositories:

- Tenant resolved from JWT via `RequestIdentity.tenant_id` (`security/dependencies.py:14-23, 52-71`).
- Tenant header validated against JWT (`:41-49`).
- All MMD queries filter by `tenant_id` (verified in `routing_repository.py:11, 22, 27`).
- Service signatures use keyword-only `tenant_id` parameter.

### 7.2 Scope isolation — INFRASTRUCTURE EXISTS, NOT WIRED FOR MMD

`Scope` table exists with hierarchy: `tenant, plant, area, line, station, equipment` (`security/rbac.py:72-78` constants).

Scope-aware permission check exists: `_scope_contains` (`rbac.py:595-638`) walks scope tree to check assignment scope contains target scope.

**But:**

- MMD entities (Product, Routing, BOM-future, ResourceRequirement) have **only `tenant_id`**, no `scope_path` or scope binding.
- Permission checks for MMD APIs do not pass `target_scope_type` / `target_scope_value` — falls through to tenant-only authorization (`rbac.py:386-412`).

→ **Future scope-aware MMD authorization (e.g., "IEP at PLANT_01 can only manage products of PLANT_01") not possible** without schema extension.

### 7.3 Impersonation handling

`require_action` resolves impersonation session and replaces `acting_role_code` in identity (`dependencies.py:176-220`). Real `user_id` preserved for audit.

Impersonation forbidden roles: `ADM, OTS` (`rbac.py:83`). Cannot impersonate ADM or OTS.

### 7.4 Multi-tenant default

Default tenant id `"default"` at `dependencies.py:39`. ProductCreated event sets `tenant_id: str = "default"` default in `execution_event_repository.py:16`. Production deployment must override.

---

## 8. Auth / Action Registry Evidence

### 8.1 Action Registry location

`app/security/rbac.py:41-56`:

```python
ACTION_CODE_REGISTRY: dict[str, PermissionFamily] = {
    "execution.start": "EXECUTE",
    "execution.complete": "EXECUTE",
    "execution.report_quantity": "EXECUTE",
    "execution.pause": "EXECUTE",
    "execution.resume": "EXECUTE",
    "execution.start_downtime": "EXECUTE",
    "execution.end_downtime": "EXECUTE",
    "execution.close": "EXECUTE",
    "execution.reopen": "EXECUTE",
    "approval.create": "APPROVE",
    "approval.decide": "APPROVE",
    "admin.impersonation.create": "ADMIN",
    "admin.impersonation.revoke": "ADMIN",
    "admin.user.manage": "ADMIN",
}
```

→ **No `admin.master_data.*` action codes.** All MMD APIs use `admin.user.manage` placeholder.

### 8.2 Action Registry registration mechanism

Action codes are seeded into DB by `seed_rbac_core` (`rbac.py:228-379`). Each action code becomes a `Permission` row with `action_code = code, family = mapped family`. Bound to system roles via `RolePermission`.

→ **Adding new action codes requires:** edit `ACTION_CODE_REGISTRY` dict + re-run `seed_rbac_core` (or migration that inserts permission rows). Not config-only.

→ **F3 implication:** MMD-BE-05 (Permission code fix) is NOT a config change. It is a source code edit + DB re-seed migration.

### 8.3 Action Registry frontend exposure

FE has `ActionRegistry.tsx` page (per MMD report). **Not verified** if it reads from DB or hardcoded list. PO-SA assumption: FE Foundation/IAM team is building this. Coordination needed.

### 8.4 Permission family model

5 families: `VIEW, EXECUTE, APPROVE, CONFIGURE, ADMIN` (`rbac.py:20`). System role → families binding at `:25-37`:

- OPR: EXECUTE
- SUP: VIEW, EXECUTE
- IEP: VIEW, CONFIGURE
- QCI: VIEW
- QAL: VIEW, APPROVE
- PMG: VIEW, APPROVE
- EXE: VIEW
- ADM: VIEW, ADMIN
- OTS: VIEW, ADMIN
- PLN: VIEW
- INV: VIEW

Comment at `:24`: *"FROZEN per Phase 6 governance. Do NOT modify without a Phase 7+ design gate."*

→ **Implication for MMD:** new MMD action codes must map to one of 5 existing families. Likely `CONFIGURE` for create/update DRAFT (IEP/PMG eligible) and `APPROVE` for release/retire (QAL/PMG eligible).

### 8.5 Deny-wins evaluation

`_evaluate_permission_rows` (`rbac.py:446-527`) implements deny-wins: a single deny row overrides any allow rows.

→ Good for safety. MMD slice can add deny rules without permission escalation risk.

---

## 9. Audit / Security Event Evidence

### 9.1 Schema

`SecurityEventLog` table (`models/security_event.py:10-23`):

- `id (PK auto), tenant_id (indexed), actor_user_id (indexed nullable), event_type (indexed), resource_type (nullable), resource_id (nullable), detail (text nullable), created_at (indexed)`.

### 9.2 Write contract

`record_security_event` (`security_event_service.py:10-32`):

- `event_type` required, normalized `.strip().upper()`.
- `commit=True` default — service-level commit by default. Can pass `commit=False` for transaction wrapping.

→ **Good design.** But MMD services do not use `commit=False`, so audit emits in separate transaction from data mutation. This is the F4 atomicity concern.

### 9.3 Read contract

`get_security_events(tenant_id, limit=100)` — basic paging only (`:35-41`). No filter by `resource_type`, no filter by time range, no filter by `actor_user_id`. Audit Trail UI tab will need richer query API.

### 9.4 Naming conventions in current source

| Domain | Event prefix | Examples |
|---|---|---|
| Product | `PRODUCT.` | `PRODUCT.CREATED, .UPDATED, .RELEASED, .RETIRED` |
| Routing | `ROUTING.` | `ROUTING.CREATED, .UPDATED, .RELEASED, .RETIRED, .OPERATION_ADDED, .OPERATION_UPDATED, .OPERATION_REMOVED` |
| ResourceRequirement | `RESOURCE_REQUIREMENT.` | `RESOURCE_REQUIREMENT.CREATED, .UPDATED, .REMOVED` |
| Downtime Reason | `MASTER.` | `MASTER.DOWNTIME_REASON_UPSERT, .DOWNTIME_REASON_DEACTIVATE` |
| Approval | (separate `approval_audit_logs` table) | `REQUEST_CREATED, DECISION_MADE` |

→ **Inconsistency: DowntimeReason uses `MASTER.` prefix, others use entity name.** Worth aligning during unification.

→ **Approval has its own audit table** (`approval_audit_logs`), separate from `security_event_logs`. Adds a slight friction for unified audit timeline.

---

## 10. Approval Service Evidence

### 10.1 CRITICAL FINDING — NOT GENERIC

`approval_service.py:22-31`:

```python
VALID_ACTION_TYPES = frozenset({
    "QC_HOLD", "QC_RELEASE", "SCRAP", "REWORK", "WO_SPLIT", "WO_MERGE",
})
```

**Master data resource types NOT in scope.** Calling `create_approval_request` with `action_type="MASTER_DATA_RELEASE_PRODUCT"` (or similar) raises `ValueError`.

→ **F1 BLOCKER.** Phase C of proposal v1.0 cannot start without extending this whitelist.

### 10.2 Generic capability — PARTIALLY GENERIC

The schema is more generic than the whitelist:

`ApprovalRequest` (`models/approval.py:32-56`) has:

- `subject_type` (nullable string) — could be `"product"`, `"routing"`, `"bom"`.
- `subject_ref` (nullable string) — could be the resource ID.
- `action_type` (string) — gated by whitelist.
- `requester_id`, `tenant_id`, `reason`, `status`.

→ **Schema supports generic resources.** Only the whitelist gates. Extension requires:

1. Add new action types to `VALID_ACTION_TYPES`.
2. Add corresponding `_DEFAULT_RULES` for approver role mapping.
3. Re-seed via `seed_approval_rules`.

### 10.3 SoD enforcement — VERIFIED

`approval_service.py:158-162`:

```python
# INVARIANT (separation of duties): requester_id != decider_user_id.
if appr_req.requester_id == decider_user_id:
    raise ValueError("Requester cannot approve their own request")
```

→ **SoD enforced at code level.** Good. Note: uses real `user_id` even under impersonation.

### 10.4 Audit ghi cả requester và decider — VERIFIED

`_log_event` (`:68-86`) writes to `ApprovalAuditLog` with `event_type="REQUEST_CREATED"` (requester) and `"DECISION_MADE"` (decider). Both events linked via `request_id`.

`ApprovalDecision` row (`:185-194`) records `decider_id, decider_role_code, decision, comment, impersonation_session_id`.

→ **Full requester/decider audit trail.** Verified.

### 10.5 Tenant-scoped rules

`ApprovalRule` table (`models/approval.py:10-29`) has `tenant_id` column with default `"*"` (wildcard). Tenant-specific rules can override wildcard.

→ **Configurable per-tenant approval roles** supported.

### 10.6 Dev/staging bypass — NOT FOUND

No `dev_bypass`, `single_person_allowed`, or similar flag found in approval_service.

→ **Cannot disable SoD even in dev.** Means FleziBCG cannot run with single-user testing on flows that require approval.

→ **Implication:** if MMD adopts approval flow, dev/staging needs at least 2 user accounts. Or proposal v1.1 must add bypass flag with strong production guard.

### 10.7 Approval-to-action coupling — MISSING

After `decide_approval_request` returns "APPROVED", **nothing automatic triggers the actual action** (e.g., release product). Caller must check decision status and then invoke the mutation manually.

→ **Implication:** MMD release flow with approval needs:

1. Endpoint `POST /v1/products/{id}/request-release` → creates approval request.
2. Approval pending state.
3. Endpoint `POST /v1/approvals/{id}/decide` → records decision.
4. **Separate mechanism** to invoke `release_product()` after approval. Either:
   - Pull-based: caller polls approval status, invokes release if approved.
   - Push-based: approval service emits event, listener invokes release. (No event broker yet.)
   - Synchronous: approval decide endpoint invokes release directly. (Couples approval service to MMD service.)

→ Architecture decision needed before implementation.

---

## 11. Alembic / Migration Evidence

### 11.1 Posture — NON-STANDARD

`alembic/versions/0001_baseline.py` is **intentional no-op**:

```python
def upgrade() -> None:
    # INTENTIONAL NO-OP: schema was already established outside Alembic.
    pass

def downgrade() -> None:
    # INTENTIONAL NO-OP: we cannot safely drop a pre-existing baseline schema.
    pass
```

Comment at `:7-19` documents:

- Schema established by `Base.metadata.create_all()` + 12 SQL migration scripts (`backend/scripts/migrations/0001-0012`).
- Existing installations: `alembic stamp 0001`.
- New installations: `python -m app.db.init_db` then `alembic stamp 0001`.
- Future schema changes: `alembic revision --autogenerate`.

### 11.2 Implications

- **Cannot autogenerate** future revisions reliably without verifying that current `Base.metadata` matches actual DB schema.
- New migration must be **manually authored** with explicit `op.add_column / op.create_table`. Don't rely on autogenerate diff.
- Backfill scripts for new columns (e.g., `version_no`) need to be in same migration or in subsequent data migration.
- Downgrade path must be explicit.

### 11.3 Versioning of migrations

Single revision `0001` only at present. Long migration chain to expect once active development resumes.

→ **Stop condition relevant:** if migration structure changes (e.g., switch to autogenerate fully), Slice 0/MMD slices must adapt.

---

## 12. Contract Decisions Proposed

These are PO-SA proposals, **not yet team-approved**. To be validated via proposal v1.1 or per-slice spec.

### 12.1 Lifecycle naming convention

**Proposal:** keep UPPER_SNAKE for lifecycle states (`DRAFT, RELEASED, RETIRED`) — matches existing source. Resolve mismatch with execution domain (which uses lower_snake `planned, in_progress, paused, blocked`) **out of MMD scope**.

### 12.2 Versioning naming convention

**Proposal:** when adding versioning columns (deferred to Phase C):

- `version_no INT NOT NULL DEFAULT 1`
- `supersedes_<entity>_id` (e.g., `supersedes_product_id`) — entity-prefixed, not generic `supersedes_id`. Reason: avoid ambiguity in joins, easier index design.
- `superseded_by_<entity>_id` for forward link.
- `released_at TIMESTAMPTZ NULL`, `retired_at TIMESTAMPTZ NULL`.

### 12.3 Unique constraint strategy

**Proposal:** `(tenant_id, <code>) WHERE lifecycle_status = 'RELEASED'` partial unique index. Allows multiple DRAFT/RETIRED rows but only 1 RELEASED at a time per business code.

### 12.4 Action code naming convention

**Proposal:**

- `admin.master_data.<entity>.<verb>` e.g., `admin.master_data.product.create`.
- Verbs: `create, update, release_request, retire_request, release_decide, retire_decide`.
- Family mapping: `create/update → CONFIGURE`, `release_request/retire_request → CONFIGURE`, `release_decide/retire_decide → APPROVE`.

### 12.5 Approval action_type naming

**Proposal:** `MASTER_DATA_<ENTITY>_<VERB>` e.g., `MASTER_DATA_PRODUCT_RELEASE`, `MASTER_DATA_PRODUCT_RETIRE`. Consistent with existing whitelist style.

### 12.6 Approval-to-action coupling

**Proposal:** **Synchronous invocation in decide endpoint.** When approval `DECISION_MADE` with `decision="APPROVED"`, the same transaction invokes the relevant service method. This is simplest and avoids polling. Tradeoff: couples approval service to MMD services.

Alternative considered: pull-based (caller checks status). Rejected for UX (user has to refresh).

Alternative considered: push via event broker. Rejected (no broker yet).

### 12.7 Repository commit pattern

**Proposal:** **Defer fix to Slice 0** (event envelope hardening proposal already addresses for `execution_events`). For MMD, accept current pattern in Phase A/B (read-only/draft work — lower risk). Address in Phase C when atomic event+approval+mutation needed.

### 12.8 ResourceRequirement lifecycle

**Proposal:** **Keep inherited governance** (mutable only when parent Routing is DRAFT). Do not add own DRAFT/RELEASED/RETIRED. Reason: ResourceRequirement is dependent on Routing — independent lifecycle creates confusion.

→ This is an explicit correction to proposal v1.0 Section A.3.

### 12.9 Audit event prefix

**Proposal:** standardize to entity prefix. Migrate `MASTER.DOWNTIME_REASON_*` → `REASON_CODE.*` (or `DOWNTIME_REASON.*` if not unifying).

### 12.10 Reason Code unification path

**Proposal:** **Option 1 confirmed.** Single table `reason_codes` (or extend `downtime_reasons` rename). `/v1/downtime-reasons` becomes a delegating view that queries `domain="downtime" AND active_flag=True`. Migration backfill domain column from existing rows.

→ Defer concrete schema to MMD-BE-04 design.

---

## 13. Risk Findings

### 13.1 P1 BLOCKER risks

| ID | Risk | Mitigation |
|---|---|---|
| R1 | Approval service whitelist not generic. Attempting MMD release approval will hard-fail at runtime. | Block MMD release/retire approval flow until `VALID_ACTION_TYPES` extended + `_DEFAULT_RULES` populated + tested. |
| R2 | Direct release/retire paths exist in source (governance debt). Anyone with `admin.user.manage` can release/retire production master data. | Document as known debt. **Do not introduce new release/retire paths for BOM** in Phase A — only after approval gating is in place. |
| R3 | Action code registry is hardcoded. Adding `admin.master_data.*` requires source change + re-seed. | Coordinate with FE Foundation/IAM team to ensure Action Registry FE reads from DB (not from hardcoded TS dict). Verify before MMD-BE-05. |

### 13.2 P2 MEDIUM risks

| ID | Risk | Mitigation |
|---|---|---|
| R4 | Repository commit-in-repository breaks atomic guarantees. Audit can desync from data on partial failure. | Document. Address in Slice 0 (event envelope) for execution. For MMD, accept in read-only slices. Refactor before Phase C (release/retire with approval). |
| R5 | MMD entities only tenant-scoped, not plant/line scoped. Future scope-aware authorization not possible without schema change. | Document. Defer to P2 future consideration. Current tenant-only is acceptable for early-stage multi-plant tenants. |
| R6 | Routing extended fields missing in model. MMD-BE-01 is larger than expected (schema migration). | Re-scope MMD-BE-01 (see Section 15). |
| R7 | Alembic posture is non-standard (no-op baseline + 12 SQL scripts). Future migrations need careful manual authoring. | Document. Each MMD slice that adds a column must include manually-written migration with verified upgrade + downgrade. |
| R8 | DowntimeReason scope hierarchy columns unused. Reason code unification slice (MMD-BE-04) must decide preserve/drop/activate. | Defer to MMD-BE-04 design discussion. |

### 13.3 P3 INFO observations

| ID | Observation | Action |
|---|---|---|
| R9 | Resource Requirement API already exposed (nested route). MMD report assumed missing. | Adjust MMD-BE-02 scope: only verify backend completeness + add frontend client. No new BE endpoint needed. |
| R10 | Audit event naming inconsistency (`MASTER.` vs entity prefix). | Address in MMD-BE-04 (reason code unification slice). |
| R11 | Approval service has no dev/staging bypass. Dev environments need 2+ user accounts for approval testing. | Document. Decide in MMD-BE-04 / Phase C design. |
| R12 | Approval-to-action coupling not designed. After "APPROVED" decision, no automatic invocation. | Resolve via Section 12.6 proposal (synchronous in decide endpoint). Validate in Phase C design. |

---

## 14. Stop Conditions Found

Re-evaluate against An's stop conditions list:

| Stop condition (per An) | Found? | Detail |
|---|---|---|
| Tenant isolation not identifiable | ❌ Not triggered | Strong tenant isolation verified across all MMD code paths. |
| MMD APIs using broad permission placeholder beyond Product | ✅ **TRIGGERED** | `admin.user.manage` placeholder used in `routings.py`, `products.py`, `downtime_reasons.py`, and nested resource_requirements routes. **Pervasive.** |
| `approval_service.py` not generic but source exposing release/retire direct | ✅ **TRIGGERED** | Direct release/retire exists in product_service + routing_service. Approval service whitelist does not include MMD. **Both conditions met.** |
| Migration structure unclear or `create_all()` production path | ⚠️ **PARTIALLY TRIGGERED** | Baseline 0001 documents `Base.metadata.create_all()` is the established mechanism — non-standard but documented. Future migrations via `alembic revision --autogenerate`. Risk noted but not a hard stop. |
| Audit/security event write contract unclear | ❌ Not triggered | Contract clear (`record_security_event` signature explicit, `commit` parameter exposed). |
| Source different from proposal v1.0 assumption | ✅ **TRIGGERED** | Multiple deltas: ResourceRequirement API exists (nested), Routing extended fields missing in model, ResourceRequirement has no own lifecycle, DowntimeReason has scope columns unused. |

→ **3 of 6 stop conditions triggered.** Mandatory pause + report to An (this document) before any implementation slice.

---

## 15. Recommended MMD-BE-01 Scope

### 15.1 Original An-proposed sequence

```
MMD-BE-01: Routing Operation Extended Read API
MMD-BE-02: Resource Requirements Read API Exposure
MMD-BE-03: BOM Backend Foundation (DRAFT/read-only)
MMD-BE-04: Unified Reason Codes + downtime backward compat
MMD-BE-05: Permission Code Fix
```

### 15.2 PO-SA recommended revision based on evidence

```
MMD-BE-01 (NEW): Routing Operation Extended Schema + Read API
   - Was: response shape extension only
   - Now: schema migration + model extension + service projection update + API
   - Effort: ~1 week (was estimated as 2-3 days)

MMD-BE-02 (REVISED): Resource Requirements FE Client (BE already complete)
   - Was: expose Resource Requirements API
   - Now: API already exposed nested under routing. Slice = FE client + verify schema completeness.
   - Effort: ~3-5 days

MMD-BE-03: BOM Backend Foundation, DRAFT-only (UNCHANGED scope)
   - Schema + service + repository + list/detail + components, no release/retire
   - Effort: ~1.5-2 weeks

MMD-BE-04: Unified Reason Codes + downtime backward compat (UNCHANGED scope)
   - Critical regression test for Station Execution
   - Decide scope hierarchy column fate
   - Effort: ~1.5 weeks

MMD-BE-05: Permission Code Fix (UNCHANGED scope, BLOCKED on FE Action Registry verification)
   - Coordinate with FE Foundation/IAM team
   - Effort: ~3-5 days after coordination unblocks
```

### 15.3 Recommended START slice = MMD-BE-01

**Rationale:**

- Routing model schema extension is straightforward (add 6 columns).
- Read API extension is low-risk (no mutation logic change).
- Unblocks Frontend Routing Operation Detail screen (high visibility for IEP).
- No dependency on F1/F2/F3 blockers (no approval, no permission code, no release/retire).
- Migration practice for the team (manual Alembic revision, not autogenerate).

### 15.4 Stop conditions for MMD-BE-01

Pause MMD-BE-01 if:

- Routing operation extended fields conflict with WorkOrder operation cache or Execution layer (dependency check needed).
- Migration cannot run cleanly on production-like data (existing routing operations rows need backfill defaults — verify column nullability strategy).
- Test infrastructure for migration up/down not in place.

---

## 16. Next-Slice Prompt Draft

```text
SLICE: MMD-BE-01 — Routing Operation Extended Schema + Read API
HARD MODE MOM v3: REQUIRED (touches schema, governance audit, tenant scope)

INTENT
  Extend routing_operations table + RoutingOperation model + service projection +
  GET /v1/routings/{id} response to include 6 extended operation fields:
    setup_time (float, nullable)
    run_time_per_unit (float, nullable)
    work_center (string 64, nullable)
    required_skill (string 64, nullable)
    required_skill_level (string 32, nullable)
    qc_checkpoint_count (int, nullable, default 0)

BASELINE SOURCES TO READ FIRST
  - docs/audit/mmd-be-00-evidence-and-contract-lock.md (this document)
  - docs/audit/mmd-current-state-report.md (frontend gap context)
  - backend/app/models/routing.py
  - backend/app/services/routing_service.py
  - backend/app/repositories/routing_repository.py
  - backend/app/api/v1/routings.py
  - backend/app/schemas/routing.py
  - backend/alembic/versions/0001_baseline.py
  - frontend/src/app/api/routingApi.ts (FE schema reference)
  - frontend/src/app/pages/RoutingOperationDetail.tsx (mock fixture for field semantics)

IN SCOPE
  - Add 6 columns to routing_operations table via Alembic migration (manual, not autogenerate)
  - Add 6 fields to RoutingOperation model
  - Add 6 fields to RoutingOperationItem schema response
  - Update _to_operation_item() projection in routing_service.py
  - Maintain backward compatibility: existing RoutingItem.operations[] still works
  - Tests:
      - Migration up/down on test DB
      - GET /v1/routings/{id} response includes new fields when populated
      - GET /v1/routings/{id} response handles NULL gracefully when not populated
      - Existing routing operation create/update/delete continue working

EXPLICITLY OUT OF SCOPE
  - NO release/retire changes
  - NO approval workflow
  - NO permission code change (still uses admin.user.manage)
  - NO BOM domain
  - NO reason code changes
  - NO frontend changes (frontend client update is separate slice)
  - NO new API endpoints (extend existing GET only)
  - NO POST/PATCH support for new fields in this slice (extend in future slice)

IMPLEMENTATION RULES
  - Manual Alembic revision (cannot trust autogenerate per baseline policy)
  - All new columns nullable (no backfill required for existing rows)
  - Keep existing field order, append new fields at end
  - Do not refactor unrelated code
  - Do not change repository commit pattern in this slice

TESTS REQUIRED
  - tests/test_routing_operation_extended_schema.py (migration test)
  - tests/test_routing_operation_extended_response.py (API test)
  - Existing routing tests must continue passing (regression)

VERIFICATION COMMANDS
  cd backend
  pytest tests/ -v
  alembic upgrade head
  alembic downgrade -1
  alembic upgrade head

DOCUMENTATION UPDATES
  - docs/design/02_domain/product_definition/manufacturing-master-data-and-product-definition-domain.md
    (update field list for routing operation)
  - Note in CHANGELOG or release notes

DEFINITION OF DONE
  - Migration up + down clean on test DB
  - All new fields visible in GET /v1/routings/{id} response
  - Backward compatibility verified (no existing test broken)
  - Test coverage for new fields: happy path + NULL handling
  - Hard Mode MOM v3 evidence pack produced and reviewed

STOP CONDITIONS
  - If Alembic migration fails on production-like data → pause + report
  - If new fields conflict with execution layer expectations → pause + investigate
  - If WorkOrder operation cache references RoutingOperation projection → expand scope or defer
```

---

## Appendix — File / Line Evidence

| Claim | Source | Line(s) |
|---|---|---|
| Product lifecycle 3-state | `backend/app/services/product_service.py` | 130, 236, 262 |
| Product no version_no field | `backend/app/services/product_service.py` | 39-51 (`_to_item`) |
| Product release direct mutation | `backend/app/services/product_service.py` | 224-248 |
| Product retire direct mutation | `backend/app/services/product_service.py` | 251-275 |
| Product API `admin.user.manage` placeholder | `backend/app/api/v1/products.py` | 55, 75, 97, 116 |
| Routing lifecycle 3-state | `backend/app/services/routing_service.py` | 204, 466, 495 |
| Routing operation model schema | `backend/app/models/routing.py` | 39-60 |
| Routing extended fields missing | `backend/app/models/routing.py` | 51-52 only |
| Routing repository commits per-call | `backend/app/repositories/routing_repository.py` | 67-95 |
| Resource Requirement no own lifecycle | `backend/app/services/resource_requirement_service.py` | 97-99 |
| Resource Requirement API nested under routing | `backend/app/api/v1/routings.py` | 217-339 |
| DowntimeReason scope columns unused | `backend/app/models/downtime_reason.py` | 33-39 |
| DowntimeReason no 3-state lifecycle | `backend/app/services/downtime_reason_service.py` | 16-75 (only list, upsert, deactivate) |
| Audit naming inconsistency | `backend/app/services/downtime_reason_service.py` | 44, 70 (`MASTER.` prefix) |
| Tenant isolation pattern | `backend/app/security/dependencies.py` | 14-23, 41-49, 52-71, 81-112 |
| Scope hierarchy infrastructure | `backend/app/security/rbac.py` | 72-78, 595-638 |
| MMD entities tenant-only | `backend/app/models/routing.py`, `models/resource_requirement.py` | (no scope_path column) |
| ACTION_CODE_REGISTRY hardcoded | `backend/app/security/rbac.py` | 41-56 |
| ACTION_CODE_REGISTRY no MMD codes | `backend/app/security/rbac.py` | 41-56 |
| Permission family FROZEN | `backend/app/security/rbac.py` | 24-37 |
| Approval whitelist not generic | `backend/app/services/approval_service.py` | 22-31 |
| Approval default rules | `backend/app/services/approval_service.py` | 34-42 |
| Approval SoD enforcement | `backend/app/services/approval_service.py` | 158-162 |
| Approval audit logging | `backend/app/services/approval_service.py` | 68-86, 196-203 |
| Approval impersonation tracking | `backend/app/services/approval_service.py` | 185-194 |
| Approval no dev bypass flag | `backend/app/services/approval_service.py` | (absence verified across 224 lines) |
| Approval-to-action coupling absent | `backend/app/services/approval_service.py` | (no callback/listener pattern) |
| Security event write contract | `backend/app/services/security_event_service.py` | 10-32 |
| Security event read API limited | `backend/app/services/security_event_service.py` | 35-41 |
| Alembic baseline no-op | `backend/alembic/versions/0001_baseline.py` | 31-39 |
| Alembic uses Base.metadata.create_all() | `backend/alembic/versions/0001_baseline.py` | 7-19 (comment) |

---

**End of MMD-BE-00 Evidence & Contract Lock**

**Status: Ready for An / team review. No implementation work performed. Awaiting decision on proposal v1.1 + MMD-BE-01 slice approval.**

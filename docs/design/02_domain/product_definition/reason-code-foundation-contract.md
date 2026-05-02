# Reason Code Foundation Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Created unified reason code foundation contract and implementation boundary lock. No code changes; documentation-only. |

---

## 1. Scope

This contract defines the minimal foundation for a **Unified Reason Code** reference/classification system in Manufacturing Master Data.

**What is in scope:**
- Define reason code domain meaning
- Establish separation from operational downtime reasons
- Propose minimal entity contract
- Propose read API shape
- Document future write governance
- Establish boundary guardrails

**What is NOT in scope:**
- Backend implementation (ORM, migration, API, tests)
- Frontend integration
- Write-path workflow
- Harmonization with existing downtime_reason behavior
- Execution/quality/material event ownership

---

## 2. Domain Meaning

### Unified Reason Code Definition
A **Reason Code** is a **reference/classification** value that provides semantic context for operational decisions and events across multiple manufacturing domains.

**Key principle:** Reason codes are **classification truth only**. They do NOT create, execute, or own operational events.

### Domains Supported
Reason codes may classify events in these domains:

| Domain | Purpose | Example |
|---|---|---|
| **EXECUTION_PAUSE** | Execution pause classification | "Operator Break", "Waiting for Material" |
| **DOWNTIME** | Downtime event classification | "Planned Maintenance", "Equipment Breakdown" |
| **SCRAP** | Scrap/rejection classification | "Dimensional Defect", "Material Issue" |
| **QUALITY_HOLD** | Quality hold classification | "Surface Appearance", "Dimensional Inspection" |
| **MAINTENANCE** | Maintenance event classification | "Preventive Maintenance", "Corrective Maintenance" |
| **MATERIAL** | Material/WIP adjustment classification | "Receipt Discrepancy", "Yield Adjustment" |
| **REWORK** | Rework/reopen classification | "Rework Required", "Process Non-Conformance" |
| **EXCEPTION** | Generic operational exception | "System Issue", "Operator Override" |
| **GENERAL** | Catch-all for ungrouped reasons | "Other", "Miscellaneous" |

---

## 3. In Scope for Minimal Foundation

The first implementation MAY include:

- ✅ Separate database table: `reason_codes` (not merging with `downtime_reasons`)
- ✅ Tenant-scoped master data
- ✅ Minimal fields: ID, tenant_id, reason_domain, reason_category, reason_code, reason_name, description, lifecycle_status, sort_order, timestamps
- ✅ Read API: list, get by ID, filter by domain/category
- ✅ Lifecycle governance: DRAFT / RELEASED / RETIRED statuses for MMD consistency
- ✅ Operational policies: requires_comment flag (if needed)

The first implementation MUST NOT include:

- ❌ Write-path API or admin workflow
- ❌ Integration with existing downtime_reason behavior
- ❌ Execution event generation
- ❌ Quality acceptance workflow
- ❌ Material movement/inventory implications
- ❌ ERP sync or external system integration

---

## 4. Explicitly Out of Scope

**This slice does NOT:**

- Create or implement the reason_code table
- Create or implement the reason_code schema
- Create or implement the reason_code API
- Create database migration
- Write tests
- Integrate with execution, quality, material, or maintenance workflows
- Change existing downtime_reason behavior or API
- Implement write-path or admin governance
- Define action codes (admin.reason_codes.manage, etc.)
- Implement FE integration or retire ReasonCodes.tsx shell page

**Future slices WILL:**

- MMD-BE-07: Implement reason_codes table, schema, read API, tests
- MMD-FULLSTACK-08: Integrate FE ReasonCodes read
- Future: Unified reason codes write path (if governance approves)
- Future: Harmonization with downtime_reason (separate governance review)

---

## 5. Relationship to Existing Downtime Reasons

### Current DowntimeReason Model
**Location:** `backend/app/models/downtime_reason.py`

**Purpose:** Operational downtime reason selection and classification for execution pause/downtime commands

**Scope Hierarchy:** Tenant → Plant → Area → Line → Station (narrowing)

**Domain:** Execution owns downtime events; downtime_reason provides reference/classification

**Key Fields:**
- reason_code (unique per tenant)
- reason_name, reason_group (BREAKDOWN, MATERIAL, QUALITY, CHANGEOVER, PLANNED_STOP, UTILITIES, OTHER)
- planned_flag, requires_comment, requires_supervisor_review, active_flag
- sort_order, created_at, updated_at

**API:**
- GET /downtime-reasons (list active for tenant)
- POST /downtime-reasons (upsert, requires admin.user.manage)
- POST /downtime-reasons/{reason_code}/deactivate (requires admin.user.manage)

### Relationship Strategy: Additive, Not Replacement

**For MMD-BE-06 and MMD-BE-07:**

1. Unified reason codes are a **separate, independent** table
2. No synchronization or dependency on downtime_reason
3. Downtime_reason continues to work exactly as today
4. No breaking changes to downtime API or behavior

**For future harmonization (separate slice, not this contract):**

- Unified reason codes MAY provide a broader classification framework
- A future slice could map downtime_reason → unified code for analytics
- But this is explicitly deferred and requires separate governance review
- Any changes to downtime_reason behavior are **out of scope** for this contract

### Why Separate, Not Merged?

| Decision | Reason |
|---|---|
| **Separate tables** | Downtime_reason is operational and execution-scoped; unified codes are reference and domain-agnostic |
| **Different scoping** | Downtime_reason has plant/area/line/station hierarchy; unified codes are tenant-only (initially) |
| **Different lifecycle** | Downtime_reason uses planned_flag/active_flag; unified codes use DRAFT/RELEASED/RETIRED for MMD consistency |
| **Future flexibility** | Keeping separate allows independent evolution and defers harmonization to explicit governance review |

---

## 6. Entity Contract

### Minimal Field Proposal

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| reason_code_id | UUID or Int | ✅ | Auto-generated | Primary key. Sequential int acceptable if tenant-unique only. |
| tenant_id | String(64) | ✅ | From request | Tenant scope — required for all master data |
| reason_domain | String(32) or Enum | ✅ | None | One of: EXECUTION_PAUSE, DOWNTIME, SCRAP, QUALITY_HOLD, MAINTENANCE, MATERIAL, REWORK, EXCEPTION, GENERAL |
| reason_category | String(64) | ✅ | None | Subcategory within domain (e.g., "Planned Maintenance" within DOWNTIME) |
| reason_code | String(64) | ✅ | None | Unique within (tenant, reason_domain). Short code like "DT-MAINT-01" |
| reason_name | String(128) | ✅ | None | Display name (e.g., "Scheduled Preventive Maintenance") |
| description | Text | ⭕ | NULL | Optional detailed description for operators |
| lifecycle_status | Enum | ✅ | DRAFT | One of: DRAFT, RELEASED, RETIRED. Matches MMD phase model. |
| requires_comment | Boolean | ⭕ | False | If true, operation using this code must include comment |
| is_active | Boolean | ⭕ | True | Operational flag for faster filtering (complement to lifecycle_status) |
| sort_order | Integer | ⭕ | 0 | Display ordering within category |
| created_at | DateTime (UTC) | ✅ | NOW | Audit timestamp |
| updated_at | DateTime (UTC) | ✅ | NOW | Audit timestamp |
| created_by | String(64) | ⭕ | NULL | Optional audit: user who created |
| updated_by | String(64) | ⭕ | NULL | Optional audit: user who last updated |

**Legend:**
- ✅ = Required in minimal foundation
- ⭕ = Optional in minimal foundation (may defer to future slices)

### Rationale

**Why lifecycle_status + is_active?**
- `lifecycle_status` (DRAFT/RELEASED/RETIRED) aligns with MMD governance model
- `is_active` provides operational filtering without breaking RELEASED codes
- Future write-path can enforce governance rules on status transitions

**Why reason_domain + reason_category?**
- reason_domain ensures codes are properly scoped (execution vs quality vs material)
- reason_category allows subcategorization for operators (e.g., "Planned Maintenance" vs "Unplanned Breakdown" within DOWNTIME)
- Supports future filtering UI: "Show me downtime reasons → breakdown category"

**Why reason_code as string, not ID-based lookup?**
- Operational systems (execution, quality, material) need human-readable codes
- reason_code is what gets stored in operation.reason_code, etc.
- reason_code_id is internal database key

---

## 7. Domain / Category Strategy

### Supported Domain / Category Matrix

| Domain | Recommended Categories | Notes |
|---|---|---|
| **EXECUTION_PAUSE** | Operator Break, Waiting for Material, Tool Change, Setup, Other Pause | Used when execution pauses but downtime does not start |
| **DOWNTIME** | Planned Maintenance, Unplanned Breakdown, Material Shortage, Utilities Issue, Environmental, Other Downtime | Full equipment/line downtime |
| **SCRAP** | Dimensional Defect, Surface/Finish Defect, Raw Material Issue, Process Defect, Operator Error, Environmental, Other Scrap | Scrapped parts or batches |
| **QUALITY_HOLD** | Dimensional Inspection, Surface Appearance, Environmental Test, Material Cert, Process Audit, Other Hold | Quality inspection suspension |
| **MAINTENANCE** | Preventive Maintenance, Corrective Maintenance, Predictive Maintenance, Emergency Repair, Other Maintenance | Maintenance events |
| **MATERIAL** | Receipt Discrepancy, Yield Variance, Inventory Adjustment, Return/Recall, Supplier Issue, Other Material | Material/WIP adjustments |
| **REWORK** | Rework Required, Scrap Reversal, Process Rerun, Quality Retest, Environmental Recheck, Other Rework | Operations reopened for rework |
| **EXCEPTION** | System Issue, Operator Override, Safety Event, Environmental Incident, Other Exception | Ungrouped operational exceptions |
| **GENERAL** | Other, Miscellaneous, Unclassified | Fallback category |

### Category Definition Rules

1. **Categories are domain-specific** — a reason code belongs to ONE domain only
2. **Categories are read-only for first implementation** — deferred to data-seeding or admin workflow in future
3. **Categories may vary per tenant** — future slices may support tenant-specific catalogs
4. **Categories must not imply operational ownership** — "Quality Hold" is classification, not authorization for QC approval

---

## 8. Lifecycle Status

### Choice: DRAFT / RELEASED / RETIRED

**Recommended:** Use `lifecycle_status` field with enum: DRAFT | RELEASED | RETIRED

**Rationale:**
- Aligns with MMD governance model (product, routing, resource requirements all use same pattern)
- Supports future write-path: DRAFT (creation) → RELEASED (operational) → RETIRED (archived)
- Clear semantics: DRAFT = not yet active, RELEASED = in use, RETIRED = no longer used

**Operational semantics:**
- RELEASED codes are included in list/filter results for operators
- DRAFT codes are hidden until released (admin workflow, future)
- RETIRED codes are hidden but remain in audit trail (immutable)

**Optional complement:** `is_active` boolean for faster filtering without parsing status transitions

---

## 9. Read API Contract Proposal

### Proposed Endpoints

#### List Reason Codes
```
GET /v1/reason-codes

Query parameters (optional):
  - domain=DOWNTIME|SCRAP|... (filter by domain)
  - category=Planned Maintenance|... (filter by category within domain)
  - lifecycle_status=RELEASED|... (filter by status, default RELEASED)
  - include_inactive=false (include is_active=false codes, default false)

Response: 200 OK
{
  "reason_codes": [
    {
      "reason_code_id": "...",
      "reason_domain": "DOWNTIME",
      "reason_category": "Planned Maintenance",
      "reason_code": "DT-MAINT-01",
      "reason_name": "Scheduled Preventive Maintenance",
      "description": "Planned downtime for routine maintenance",
      "lifecycle_status": "RELEASED",
      "requires_comment": false,
      "sort_order": 10
    },
    ...
  ]
}
```

#### Get Single Reason Code
```
GET /v1/reason-codes/{reason_code_id}

Response: 200 OK (same shape as list item)

Response: 404 NOT FOUND (if not found or not RELEASED)
```

#### Filter by Domain (convenience)
```
GET /v1/reason-codes/domains/{domain}

e.g., GET /v1/reason-codes/domains/DOWNTIME

Response: 200 OK (list of codes in that domain)
```

### Authentication & Authorization

- All endpoints require authenticated identity (tenant_id derived from JWT)
- Read endpoints do NOT require action code (open to all authenticated users)
- Response is automatically filtered to tenant_id from request identity
- Future write endpoints will require action code (e.g., admin.reason_codes.manage)

---

## 10. Future Write Governance

**This contract does NOT define write-path.** Explicitly deferred.

**Future considerations (separate slice):**

1. **Admin workflow:** Who can create/edit/release/retire reason codes?
2. **Action codes:** admin.reason_codes.manage vs finer-grained (admin.reason_codes.create, etc.)
3. **Approval:** Do reason codes need approval before RELEASED, or auto-released on creation?
4. **Audit:** Track who created/updated each code?
5. **Tenant isolation:** Can tenants define their own catalogs, or use global MMD-curated ones?

---

## 11. Boundary Guardrails

| Guardrail | Enforcement | Notes |
|---|---|---|
| **Reason codes do NOT execute events** | Verify: No backend code path that takes action based on reason_code alone | Reason code provides context; domain system (execution, quality, material) owns the event |
| **Reason codes do NOT move material** | Verify: reason_code field is read-only in MATERIAL domain; no inventory/WIP/scrap command generated | Material movement is owned by WIP/backflush service, not reason codes |
| **Reason codes do NOT pass/fail quality** | Verify: QUALITY_HOLD codes do not include or imply pass/reject decision | Quality acceptance is owned by QA service, not reason codes |
| **Reason codes do NOT replace downtime_reason** | Verify: downtime_reason API continues unchanged; no breaking migration | Separate tables, no dependency. Future harmonization is explicit governance review |
| **Reason codes do NOT imply authorization** | Verify: Listing reason codes does not grant action permission; RBAC remains server-side | Code visibility ≠ authorization to use code |
| **Reason codes do NOT generate audit events** | Verify: Creating/listing reason codes does not create operational audit records | Reason codes are reference data; audit events are owned by domain services |
| **Reason codes are tenant-isolated** | Verify: All queries filter by tenant_id; no cross-tenant data leak | Standard MMD pattern |
| **Reason codes are append-only (RETIRED is immutable)** | Verify: Once reason_code_id is assigned, it never changes; RETIRED codes remain in history | Audit trail integrity |

---

## 12. Invariants

1. **Single source of truth:** Reason codes are stored in one table per tenant; no replication or caching without invalidation
2. **Immutable IDs:** reason_code_id and reason_code never change after initial creation
3. **Unique per domain:** Within a tenant, (reason_domain, reason_code) is unique
4. **Lifecycle consistency:** RETIRED codes are not included in active lists but remain queryable for audit
5. **Domain ownership:** Each reason code belongs to exactly ONE reason_domain; no cross-domain codes
6. **Category containment:** reason_category is always subordinate to reason_domain; invalid domain/category pairs are rejected
7. **Classification only:** reason_code fields do not contain operational data (timestamps, operators, quantities, etc.)

---

## 13. Recommended Implementation Slices

### Slice 1: MMD-BE-06 (This Slice)
- **Type:** Documentation-only
- **Deliverables:** Foundation contract, boundary lock, design evidence
- **Duration:** 1-2 hours
- **Outcome:** Clear contract before backend implementation

### Slice 2: MMD-BE-07 (Next Slice, if approved)
- **Type:** Backend implementation
- **Deliverables:** reason_codes table, schema, read API, tests
- **Tasks:**
  1. Create Alembic migration: 0009_reason_codes.py
  2. Create ORM model: backend/app/models/reason_code.py
  3. Create Pydantic schema: backend/app/schemas/reason_code.py
  4. Create service: backend/app/services/reason_code_service.py (list, get)
  5. Create API: backend/app/api/v1/reason_codes.py (read endpoints)
  6. Create tests: backend/tests/test_reason_code_*.py
  7. Seed baseline reason codes (if applicable)
- **Duration:** 4-6 hours

### Slice 3: MMD-FULLSTACK-08 (After BE-07)
- **Type:** Frontend read integration
- **Deliverables:** Replace ReasonCodes.tsx mock with backend API
- **Tasks:**
  1. Create reasonCodeApi.ts helpers (listReasonCodes, getReasonCode, filterByDomain)
  2. Rewrite ReasonCodes.tsx to load from backend
  3. Add i18n keys
  4. Update screenStatus.ts (reasonCodes: PARTIAL → CONNECTED)
  5. Run regression checks
  6. Create audit report
- **Duration:** 3-4 hours

### Future Slices (If Governance Approves)
- **Slice 4:** Reason code write-path (create, edit, release, retire — deferred to separate governance)
- **Slice 5:** Harmonization with downtime_reason (separate governance review required)
- **Slice 6:** Tenant-specific reason code catalogs (if multi-tenant requirement)
- **Slice 7:** Integration with execution/quality/material systems (domain-owned workflows)

---

## Final Verdict

✅ **APPROVED FOR NEXT SLICE:** The Unified Reason Code foundation contract is safe to implement as three sequential slices (documentation → backend → frontend) without breaking existing downtime_reason behavior or violating manufacturing domain boundaries.

**Key assurances:**
1. Reason codes are classification/reference only
2. Existing downtime_reason remains untouched
3. No operational event generation in scope
4. Clear boundary guardrails documented
5. Lifecycle governance aligns with MMD
6. Minimal foundation supports future extension

**Recommended next step:** Approve MMD-BE-07 backend implementation slice to proceed with reason_codes table, schema, and read API.


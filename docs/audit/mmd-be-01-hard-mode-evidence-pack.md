# MMD-BE-01 Hard Mode MOM v3 Evidence Pack

| Field | Value |
|---|---|
| Slice | MMD-BE-01 — Routing Operation Extended Schema + Read API |
| Branch | `master-data-hardening/mmd-be-01-routing-op-extended-read` (empty placeholder; will resume after PRE merged) |
| Date | 2026-05-01 |
| Status | **AUTHORIZED PENDING MMD-BE-01-PRE MERGE** — scope reduced from 6 → 3 fields per An's Option A decision |
| Hard Mode MOM v3 | TRIGGERED (DB migration enforcing operational truth) |
| Predecessor | `docs/audit/mmd-be-00-evidence-and-contract-lock.md` |
| Prerequisite slice | `MMD-BE-01-PRE` — branch `master-data-hardening/mmd-be-01-pre-routing-contract-v1-2-boundary-patch` (updates `routing-foundation-contract.md` v1.1 → v1.2) |
| Decision history | 2026-05-01 — PO-SA evidence pack v1.0 surfaced contract gap; An chose Option A with scope correction; PRE slice inserted; this pack revised to v1.1 reflecting reduced scope |

---

## 1. Slice Identity

### 1.1 REVISED approved scope (per An's Option A decision, 2026-05-01)

Add **3 nullable columns** to `routing_operations` via manual Alembic migration:

- `setup_time` (float, nullable) — operation prep time before run begins
- `run_time_per_unit` (float, nullable) — time per produced unit during steady-state run
- `work_center_code` (string 64, nullable) — work center code; tenant-scoped string, not yet a foreign-key to a work_centers entity

Update model `RoutingOperation`, response schema `RoutingOperationItem`, service projection `_to_operation_item`, extend GET `/v1/routings/{id}`. Tests for migration up/down + API response.

### 1.2 Original 6-field scope reduced

| Original candidate | Decision | Rationale | New canonical home |
|---|---|---|---|
| `setup_time` | ✅ Approved | Operation-owned, cycle decomposition | RoutingOperation |
| `run_time_per_unit` | ✅ Approved | Operation-owned, cycle decomposition | RoutingOperation |
| `work_center` → renamed `work_center_code` | ✅ Approved | Operation-owned resource binding | RoutingOperation |
| `required_skill` | ⏸ Deferred | Overlap with ResourceRequirement (`OPERATOR_SKILL` resource type already exists) | ResourceRequirement domain |
| `required_skill_level` | ⏸ Deferred | Same as above | ResourceRequirement domain |
| `qc_checkpoint_count` | ❌ Rejected as RoutingOperation column | Quality Lite domain owns checkpoint definitions; count would be perceived truth divorced from canonical record | Quality Lite (may appear later as derived/read-only summary, not source) |

### 1.3 Naming change

`work_center` → `work_center_code` per project naming convention (existing fields use `_code` suffix: `product_code, routing_code, operation_code, reason_code, required_capability_code`). An explicitly preferred this in scope correction.

### 1.4 Out of scope

No release/retire change, no approval, no permission code change, no BOM, no reason codes, no FE, no new endpoints, no POST/PATCH for new fields, no refactor. **No required_skill / required_skill_level / qc_checkpoint_count** in any form on RoutingOperation.

---

## 2. Hard Mode v3 Trigger Justification

| Trigger | Applies? | Notes |
|---|---|---|
| execution state machine | ❌ | No execution touch |
| execution commands/events | ❌ | No execution event |
| projections/read models | ⚠️ Marginal | Slice touches `_to_operation_item` projection, but only adds fields, no semantic change |
| station/session/operator/equipment | ❌ | No |
| production reporting | ❌ | No |
| downtime | ❌ | No |
| completion/closure | ❌ | No |
| quality hold | ❌ | No |
| material/inventory execution impact | ❌ | No |
| tenant/scope/auth | ❌ | No auth change |
| IAM lifecycle | ❌ | No |
| role/action/scope assignment | ❌ | No |
| audit/security event | ❌ | No new audit event |
| critical invariant | ⚠️ Marginal | All new columns nullable — no new constraint |
| **DB migration enforcing governance or operational truth** | ✅ | **Schema migration on routing_operations** |

→ Hard Mode v3 triggered solely by DB migration. Lower-stakes than execution-touching slices, but evidence pack still required per An's directive.

---

## 3. Design Evidence Extract

### 3.1 Authoritative sources read

| Source | Status | Coverage of slice fields |
|---|---|---|
| `docs/design/02_domain/product_definition/manufacturing-master-data-and-product-definition-domain.md` (v1.0) | Inspected (35 lines, full) | Domain overview only — no field-level guidance |
| `docs/design/02_domain/product_definition/routing-foundation-contract.md` (v1.1) | Inspected (172 lines, full) | **Section 3 specifies exactly 6 minimum fields per operation** |
| `docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md` | Located via grep, not yet inspected (referenced for `required_skill` boundary check) | Referenced only |
| `docs/design/02_registry/routing-event-registry.md` | Located via grep, not yet inspected | Referenced for ROUTING.OPERATION_* event payloads |
| `docs/audit/mmd-current-state-report.md` (v1.0) | Inspected previously | Source of slice's 6 field list (FE mock fixture) |
| `docs/audit/mmd-be-00-evidence-and-contract-lock.md` (v1.0) | Authored predecessor | Confirmed model gap |
| `backend/app/schemas/routing.py` | Inspected (58 lines, full) | Confirmed schemas don't have 6 fields |
| `backend/app/models/routing.py` | Inspected previously | Confirmed model has only 5 columns beyond identity |

### 3.2 CRITICAL FINDING — Contract Gap (RESOLVED via MMD-BE-01-PRE)

**Original gap:** `routing-foundation-contract.md` v1.1 Section 3 listed only 6 minimum operation fields (`operation_id, operation_code, operation_name, sequence_no, standard_cycle_time, required_resource_type`). The 6 candidate slice fields were not in the contract.

**Resolution:** An chose Option A. Prerequisite slice `MMD-BE-01-PRE` patches the contract:

- v1.2 Section 3 adds 3 RoutingOperation-owned extended fields with explicit semantics: `setup_time`, `run_time_per_unit`, `work_center_code`.
- v1.2 Section 10.1 explicitly defers `required_skill` / `required_skill_level` to ResourceRequirement domain.
- v1.2 Section 10.2 explicitly rejects `qc_checkpoint_count` as RoutingOperation column; reserves Quality Lite as canonical home.
- v1.2 Section 13 authorizes MMD-BE-01 implementation after PRE merge.

→ Contract gap closed. MMD-BE-01 implementation authority restored, narrowed to 3 fields.

### 3.3 Field-by-field decision summary (post-Option A)

| Slice field | Decision | Final canonical home |
|---|---|---|
| `setup_time` | ✅ Approved | RoutingOperation (v1.2) |
| `run_time_per_unit` | ✅ Approved | RoutingOperation (v1.2) |
| `work_center_code` (renamed) | ✅ Approved | RoutingOperation (v1.2) |
| `required_skill` | ⏸ Deferred to ResourceRequirement | ResourceRequirement (`required_resource_type=OPERATOR_SKILL` + `required_capability_code`) |
| `required_skill_level` | ⏸ Deferred to ResourceRequirement | ResourceRequirement capability semantics |
| `qc_checkpoint_count` | ❌ Rejected as RoutingOperation column | Quality Lite (future derived projection only) |

### 3.4 Domain boundary findings (closed)

**Skill duplication concern:** Resolved by deferring `required_skill` / `required_skill_level` from RoutingOperation. ResourceRequirement remains the single source of truth for operator skill requirements.

**Quality domain boundary concern:** Resolved by rejecting `qc_checkpoint_count` from RoutingOperation. If a UI summary count is needed in routing screens, it must be sourced as a derived read-only projection from Quality Lite, not stored on RoutingOperation.

### 3.5 Implementation history (pre-existing in source code)

`backend/app/models/routing.py:39-60` — Routing operation has only: `operation_code, operation_name, sequence_no, standard_cycle_time, required_resource_type`. Matches contract v1.1 Section 3 exactly.

→ Source code is aligned with contract today. MMD-BE-01 (post-PRE merge) extends source to match contract v1.2.

---

## 4. Event Map

### 4.1 Existing events touched

| Event | Trigger | Payload field changes? |
|---|---|---|
| `ROUTING.OPERATION_ADDED` | `add_routing_operation` (POST `/v1/routings/{id}/operations`) | **Out of scope** — slice does not add POST support for new fields |
| `ROUTING.OPERATION_UPDATED` | `update_routing_operation` (PATCH) | **Out of scope** — slice does not add PATCH support for new fields |

### 4.2 New events introduced

**None.** Slice is read-extension only.

### 4.3 Event registry implications

`docs/design/02_registry/routing-event-registry.md` event payload `changed_fields` array — currently only existing fields can appear. Future MMD-BE-01b (write support for new fields) will need to update event registry payload contract.

→ Defer to a follow-up slice.

---

## 5. Invariant Map

### 5.1 Existing invariants preserved

Per `routing-foundation-contract.md` Section 8:

- ✅ `routing_code` unique per tenant — not touched
- ✅ Routing tenant-scoped — not touched
- ✅ `product_id` references same tenant — not touched
- ✅ `sequence_no` unique within routing — not touched
- ✅ RELEASED routing structural updates rejected — not touched (slice doesn't add write paths)
- ✅ RETIRED routing cannot be linked downstream — not touched

### 5.2 New invariants introduced by slice

**None.** All 6 new columns nullable, no constraints, no business logic.

### 5.3 Implicit invariants worth flagging (3 fields only)

| Implicit invariant | Risk |
|---|---|
| `setup_time >= 0` | No DB CHECK constraint in slice. Negative values would be data dirty — undetected. |
| `run_time_per_unit >= 0` | Same — no validation in slice. |
| `work_center_code` references real work center | No FK in P0-B. Free-text — could refer to non-existent work center. Contract v1.2 Section 8 flags this as soft invariant. |
| `setup_time + run_time_per_unit ≤ standard_cycle_time` (if both populated) | Not enforced. Contract v1.2 Section 3 declares `standard_cycle_time` is authoritative target if conflict. |

→ Slice is read-only, so these are "reading dirty data" risks, not "writing dirty data" risks. Once a future write-path slice (MMD-BE-01b or similar) adds POST/PATCH for these fields, contract v1.2 Section 8 soft invariants MUST become enforced rules.

---

## 6. State Transition Map

**N/A.** Slice does not touch lifecycle state machine. Lifecycle states (`DRAFT, RELEASED, RETIRED`) and their transitions remain governed by existing `release_routing` / `retire_routing` / `update_routing` paths — none of which are modified.

---

## 7. Test Matrix

### 7.1 Migration tests

| ID | Test | Expected |
|---|---|---|
| T1 | `alembic upgrade head` on clean DB | 3 columns added (`setup_time`, `run_time_per_unit`, `work_center_code`), all nullable |
| T2 | `alembic downgrade -1` | 3 columns dropped, schema reverts to prior state |
| T3 | `alembic upgrade head` after T2 | Re-up clean (idempotent migration) |
| T4 | `alembic upgrade head` on production-like DB with existing routing_operations rows | Existing rows persist with NULL in new columns; no data loss |

### 7.2 Model tests

| ID | Test | Expected |
|---|---|---|
| T5 | Create RoutingOperation with all 3 new fields populated | Persists, can re-read |
| T6 | Create RoutingOperation with all 3 new fields NULL | Persists, can re-read with NULL values |
| T7 | Update RoutingOperation existing fields, leave new fields untouched | Existing fields update, new fields remain NULL |

### 7.3 API response tests

| ID | Test | Expected |
|---|---|---|
| T8 | GET `/v1/routings/{id}` for routing with operation containing new field values | Response includes 3 new fields with values |
| T9 | GET `/v1/routings/{id}` for routing with operation containing NULL new fields | Response includes 3 new fields with NULL/None |
| T10 | GET `/v1/routings/{id}` schema serialization for backward compat | Existing field order preserved, 3 new fields appended |

### 7.4 Regression tests

| ID | Test | Expected |
|---|---|---|
| T11 | Existing `tests/test_routing_*` tests pass unchanged | All green |
| T12 | Existing `tests/test_resource_requirement_*` pass unchanged | All green |
| T13 | POST `/v1/routings/{id}/operations` with old payload (no new fields) | Operation created with NULL new fields; no schema break |
| T14 | PATCH `/v1/routings/{id}/operations/{op_id}` with old payload | Operation updated; new fields untouched |

### 7.5 Negative tests (defensive)

| ID | Test | Expected |
|---|---|---|
| T15 | Migration applied twice (idempotency) | No error on second up |
| T16 | API response includes new fields even when no operations populate them | 3 new fields present as NULL in JSON response |
| T17 | RoutingOperation create/update with old payload (no new fields) does NOT silently accept payloads attempting `required_skill` / `required_skill_level` / `qc_checkpoint_count` | Pydantic schema rejects unknown fields (or ignores per ConfigDict.extra setting) — explicitly verified |

---

## 8. Verdict before coding

### 8.1 PO-SA verdict (revised): **AUTHORIZED PENDING MMD-BE-01-PRE MERGE**

**Decision history:**

- Original (this pack v1.0): PAUSE — contract gap surfaced.
- An (2026-05-01): chose Option A with scope correction. 3 fields approved, 2 deferred to ResourceRequirement, 1 rejected (Quality Lite owns).
- Current (this pack v1.1): authorized for 3-field implementation, conditional on PRE merge.

**Reasoning preserved for audit:**

- Canonical contract `routing-foundation-contract.md` v1.1 (status `READY_FOR_HUMAN_REVIEW_BEFORE_IMPLEMENTATION`) did NOT list any of the 6 candidate fields.
- 2 fields (`required_skill`, `required_skill_level`) overlapped Resource Requirement domain (`required_resource_type=OPERATOR_SKILL` already supported).
- 1 field (`qc_checkpoint_count`) crossed Quality Lite domain boundary.
- An's Option A correctly invokes Hard Mode MOM v3 principle: design first, code second.

### 8.2 Updated execution plan

**Step 1 (current slice — MMD-BE-01-PRE):** Update `routing-foundation-contract.md` v1.1 → v1.2. **Doc-only**. No code, no migration, no schema change. Branch: `master-data-hardening/mmd-be-01-pre-routing-contract-v1-2-boundary-patch`.

**Step 2 (after PRE merged — MMD-BE-01):** Implement 3-field schema migration + model + service projection + API response extension + tests. Branch: `master-data-hardening/mmd-be-01-routing-op-extended-read`. Hard Mode MOM v3 evidence pack (this document) authorizes implementation per contract v1.2 Section 13.

**Step 3 (future slice — out of MMD-BE-01 scope):** Resource Requirement screen FE wiring may later need `required_skill` semantics. To be planned as a separate slice referencing ResourceRequirement domain only.

**Step 4 (future slice — out of MMD-BE-01 scope):** If routing UI needs QC checkpoint count, build a derived projection from Quality Lite read-model. Not via RoutingOperation column.

### 8.3 What this evidence pack v1.1 does

- Reflects An's Option A scope correction.
- Reduces test matrix from 6 fields to 3 fields.
- References contract v1.2 (in PRE branch) as authority source.
- Explicitly preserves rationale for deferred / rejected fields.

### 8.4 What this evidence pack v1.1 does NOT do

- Does not implement schema migration (MMD-BE-01 work, after PRE merged).
- Does not modify model, schema, service, repository, API.
- Does not modify tests.
- Does not commit to MMD-BE-01 branch — branch exists but is empty placeholder.
- Does not authorize PRE merge — that is An's review decision on the PRE branch (separate from this pack).

---

## 9. Appendix — File / Line Evidence

| Claim | Source | Line(s) |
|---|---|---|
| Routing canonical contract minimum 6 fields | `docs/design/02_domain/product_definition/routing-foundation-contract.md` | 38-44 |
| Routing contract explicit exclusions | `docs/design/02_domain/product_definition/routing-foundation-contract.md` | 140-150 |
| Routing contract review status | `docs/design/02_domain/product_definition/routing-foundation-contract.md` | 10, 165 |
| Routing model current schema | `backend/app/models/routing.py` | 39-60 |
| Routing schema current shape | `backend/app/schemas/routing.py` | 8-22, 36-46 |
| Resource Requirement supports OPERATOR_SKILL type | `backend/app/services/resource_requirement_service.py` | 29-35 |
| Routing event payload spec | `docs/design/02_registry/routing-event-registry.md` | 28 |
| Routing operation invariants | `docs/design/02_domain/product_definition/routing-foundation-contract.md` | 105-118 |

---

**End of MMD-BE-01 Hard Mode MOM v3 Evidence Pack**

**Status: PAUSE. Awaiting An's decision on Option A / B / C before code.**

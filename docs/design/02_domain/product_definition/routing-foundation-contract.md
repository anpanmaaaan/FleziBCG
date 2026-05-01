# Routing Foundation Contract

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial P0-B routing foundation draft contract (doc-only, no implementation). |
| 2026-04-29 | v1.1 | Coverage review completed; marked READY_FOR_HUMAN_REVIEW_BEFORE_IMPLEMENTATION with explicit non-implementation boundary. |
| 2026-05-01 | v1.2 | MMD-BE-01-PRE boundary patch: extended operation sequence with 3 RoutingOperation-owned fields (`setup_time`, `run_time_per_unit`, `work_center_code`); explicitly deferred `required_skill` / `required_skill_level` to ResourceRequirement domain; explicitly rejected `qc_checkpoint_count` as RoutingOperation source-of-truth (Quality Lite owns checkpoint definition). Status moved to APPROVED for P0-B operation fields extension. |

Status: APPROVED for P0-B operation fields extension (v1.2 boundary patch). Pending An merge of branch `master-data-hardening/mmd-be-01-pre-routing-contract-v1-2-boundary-patch`.

## 1. Purpose

Define the minimum routing foundation contract for P0-B without expanding into execution-dispatch, recipe, or planning systems.

## 2. P0-B Routing Aggregate (Minimum)

Required fields:
- routing_id
- tenant_id
- product_id
- routing_code
- routing_name
- lifecycle_status
- operations sequence

Field intent:
- routing_id: immutable routing identity key.
- tenant_id: tenant ownership and isolation boundary.
- product_id: product linkage key for routing applicability.
- routing_code: business key, unique inside tenant.
- routing_name: display name.
- lifecycle_status: routing lifecycle state machine field.
- operations sequence: ordered list of operation steps for this routing.

## 3. Operations Sequence (P0-B)

Minimum sequence structure per operation item:
- operation_id
- operation_code
- operation_name
- sequence_no
- standard_cycle_time (optional)
- required_resource_type (optional)

Extended structure per operation item (v1.2 boundary patch, all optional/nullable):
- setup_time (optional)
- run_time_per_unit (optional)
- work_center_code (optional)

Field intent (extended fields):
- setup_time: time required to prepare the operation before run begins (e.g., tooling change, fixture install, machine warm-up). Numeric, in seconds. Independent of `standard_cycle_time`.
- run_time_per_unit: time per produced unit during steady-state run. Numeric, in seconds. Used for OEE benchmarking and APS planning. Independent of `standard_cycle_time` (may equal it in simple cases; may differ when standard_cycle_time captures full cycle including setup spread).
- work_center_code: identifier of the work center to which this operation is assigned. String code, tenant-scoped. Not yet a foreign-key reference — work_centers entity is master-data debt deferred to a future slice. For P0-B, treated as free-text code with display semantics; downstream code-to-record validation is non-blocking.

Cycle time semantics clarification (v1.2):
- `standard_cycle_time` remains the authoritative composite cycle target as today.
- `setup_time` + `run_time_per_unit` are decomposition fields. They do not replace `standard_cycle_time`; they enrich it.
- If both decomposition and composite are populated and inconsistent, `standard_cycle_time` is the authoritative target for OEE / planning until cycle time decomposition is governed in a future slice.

P0-B sequence rules:
- sequence_no must be unique within a routing.
- sequence_no ordering is authoritative for operation order.
- no parallel branch semantics in P0-B.
- extended fields (setup_time, run_time_per_unit, work_center_code) are nullable; absence is not an error.

## 4. Allowed Commands

- create_routing
- update_routing
- add_routing_operation
- update_routing_operation
- remove_routing_operation
- release_routing
- retire_routing

## 5. Lifecycle States

Canonical P0-B states:
- DRAFT
- RELEASED
- RETIRED

State semantics:
- DRAFT: routing and operation sequence are editable.
- RELEASED: routing is consumable by downstream linkage/read models; structural edits are restricted.
- RETIRED: routing is no longer available for new downstream linkage.

## 6. State Transition Contract

- create_routing: creates routing in DRAFT.
- update_routing: allowed in DRAFT; restricted in RELEASED; rejected in RETIRED.
- add/update/remove operation: allowed in DRAFT; rejected in RELEASED and RETIRED for P0-B.
- release_routing: DRAFT to RELEASED.
- retire_routing: DRAFT or RELEASED to RETIRED.

## 7. Event Contract (Candidate for P0-B)

Event naming status for routing in this draft:
- CANDIDATE_FOR_P0_B

Candidate events:
- ROUTING.CREATED
- ROUTING.UPDATED
- ROUTING.OPERATION_ADDED
- ROUTING.OPERATION_UPDATED
- ROUTING.OPERATION_REMOVED
- ROUTING.RELEASED
- ROUTING.RETIRED

Minimum event payload:
- tenant_id
- actor_user_id
- routing_id
- routing_code
- product_id
- lifecycle_status
- changed_fields
- occurred_at

## 8. Invariants

Mandatory invariants:
- routing_code must be unique per tenant.
- routing is tenant-owned and tenant-scoped for all reads/writes.
- product_id must reference a product in the same tenant.
- operations sequence_no values are unique within routing.
- RELEASED routing structural updates are rejected in P0-B.
- RETIRED routing cannot be newly linked downstream.

Structural fields for RELEASED immutability in P0-B:
- routing_code
- product_id
- operations sequence

Extended-field invariants (v1.2, soft):
- setup_time (when populated): expected non-negative numeric. P0-B does not enforce DB-level CHECK constraint; validation deferred to write-path slice (post MMD-BE-01).
- run_time_per_unit (when populated): expected non-negative numeric. Same deferral as above.
- work_center_code (when populated): expected non-empty string after trim. Reference integrity to a future work_centers entity not enforced in P0-B.

Note: extended fields are read-only in MMD-BE-01. Write-path support (POST/PATCH for these fields) is a separate slice and must convert these soft invariants into enforced rules.

## 9. API Surface (P0-B Minimum)

Read:
- GET /routings
- GET /routings/{routing_id}

Write:
- POST /routings
- PATCH /routings/{routing_id}
- POST /routings/{routing_id}/operations
- PATCH /routings/{routing_id}/operations/{operation_id}
- DELETE /routings/{routing_id}/operations/{operation_id}
- POST /routings/{routing_id}/release
- POST /routings/{routing_id}/retire

API behavior notes:
- All endpoints are tenant-scoped.
- Cross-tenant detail reads return 404 to avoid existence leakage.
- Lifecycle transitions are server-governed.

## 10. Explicit Exclusions

Excluded from this contract:
- BOM
- recipe/ISA-88
- advanced versioning
- APS
- Backflush
- ERP sync
- Acceptance Gate
- plant-specific execution dispatch logic

### 10.1 Boundary deferrals (v1.2)

The following candidate fields were considered for RoutingOperation in MMD-BE-01 evaluation and **deferred to other domains**:

- `required_skill` — operator skill requirement. **Deferred to ResourceRequirement domain.** Rationale: `resource_requirement_service.py` already supports `required_resource_type="OPERATOR_SKILL"` with `required_capability_code` and `quantity_required`. Adding a parallel inline path on RoutingOperation would create dual sources of truth for skill requirements. Routing operations needing skill governance must use ResourceRequirement records.
- `required_skill_level` — qualification level for the required skill. **Deferred to ResourceRequirement domain.** Rationale: same as above; expressed as part of ResourceRequirement's capability semantics, not as a RoutingOperation column.

### 10.2 Boundary rejections (v1.2)

The following candidate field was considered for RoutingOperation in MMD-BE-01 evaluation and **rejected as RoutingOperation source-of-truth**:

- `qc_checkpoint_count` — number of QC checkpoints linked to this operation. **Rejected as RoutingOperation column.** Rationale: Quality Lite domain owns checkpoint definitions and lifecycle. Storing a count on RoutingOperation creates "perceived truth" that is divorced from the canonical Quality Lite record. If a count is needed for UI summary, it should appear as a derived/read-only projection sourced from Quality Lite, not as a column on RoutingOperation.

### 10.3 Future re-entry path

A field deferred or rejected here may be reconsidered in a future contract revision. Re-entry requires:
- update to this contract with the new boundary rationale, or
- a separate domain contract (Quality Lite, ResourceRequirement) explicitly governing the new field, plus a derived projection back into the routing UI surface.

## 11. Coverage Review Verdict

Coverage check against requested minimums:
- routing identity: covered
- product linkage: covered
- lifecycle states: covered
- operation sequence model: covered
- release/retire commands: covered
- event candidates: covered
- invariants: covered
- API surface: covered
- explicit exclusions: covered

Verdict: READY_FOR_HUMAN_REVIEW_BEFORE_IMPLEMENTATION.

## 12. Implementation Boundary

This file is a design draft contract only.

No routing code implementation, migration, or API delivery is included by this document.

## 13. Implementation Authorization (v1.2)

After An merges branch `master-data-hardening/mmd-be-01-pre-routing-contract-v1-2-boundary-patch`:

- Slice **MMD-BE-01 — Routing Operation Extended Schema + Read API** is authorized to implement read-side support for the 3 v1.2 extended fields (`setup_time`, `run_time_per_unit`, `work_center_code`).
- Implementation scope: Alembic migration adding 3 nullable columns; model + schema + service projection update; extend GET `/v1/routings/{id}` response; tests.
- Out of scope for MMD-BE-01: write-path support (POST/PATCH for new fields), `required_skill` / `required_skill_level` / `qc_checkpoint_count` (per Section 10).
- Cross-domain note: implementations of skill or QC checkpoint UI fields on routing screens must be backed by ResourceRequirement records (skill) or Quality Lite read-model (QC checkpoint count), not by RoutingOperation columns.

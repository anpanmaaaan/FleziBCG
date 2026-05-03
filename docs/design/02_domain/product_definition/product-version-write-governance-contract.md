# Product Version Write Governance Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Added Product Version write governance and minimal mutation contract (documentation-only). |

## Routing

- Selected brain: MOM Brain
- Selected mode: Product governance mode + Backend command-boundary design mode + Authorization/action-code governance mode + Lifecycle governance mode + Architecture boundary guardian mode + Source audit/evidence mode + Critical reviewer mode + PR gate/verification mode
- Hard Mode MOM: v3 ON
- Reason: Product Version mutation governance must be locked before any write API implementation.

## 1. Purpose

Define the governance contract for future Product Version write commands.

This document is authoritative for Product Version write-path boundaries in the current phase.

This document is not implementation. No runtime code, migration, endpoint, or action-code registry change is performed by this contract.

## 2. Scope

In scope:
- Product Version write command boundary
- lifecycle transition governance
- action-code requirement for mutation authorization
- audit/event expectation for privileged mutations
- cross-domain boundary guardrails
- minimal future API contract proposal
- future test matrix for implementation gate

Out of scope:
- backend write route implementation
- frontend write UI implementation
- DB schema changes
- runtime action-code registration
- BOM/Routing/ProductVersion binding implementation
- ERP/PLM sync

## 3. Baseline Evidence Extract

### 3.1 Source docs read

| Doc | Why used |
|---|---|
| docs/audit/mmd-write-gov-01-command-boundary.md | Upstream write-governance matrix and sequence selecting MMD-BE-08 next |
| docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md | Frozen read baseline and phase boundaries |
| docs/audit/mmd-be-03-product-version-foundation-read-model.md | ProductVersion read model invariants and deferred items |
| docs/audit/mmd-fullstack-06-product-version-fe-read-integration.md | FE read integration state and read-only guardrails |
| docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md | Command/lifecycle/action-code baseline decisions |
| docs/design/02_domain/product_definition/product-version-foundation-contract.md | ProductVersion entity and read-path contract |
| docs/design/02_registry/action-code-registry.md | Current runtime action-code registry truth |

### 3.2 Source files inspected

| File | Evidence |
|---|---|
| backend/app/api/v1/products.py | ProductVersion has only GET list/detail routes; no write routes |
| backend/app/services/product_version_service.py | Read-only service functions (`list_product_versions`, `get_product_version`) |
| backend/app/repositories/product_version_repository.py | Read-only repository access |
| backend/app/models/product_version.py | Lifecycle and `is_current` fields exist for future governance |
| backend/app/schemas/product.py | `ProductVersionItem` read schema and lifecycle set |
| backend/app/security/rbac.py | No `admin.master_data.product_version.manage` in runtime registry |
| frontend/src/app/pages/ProductDetail.tsx | Product versions rendered read-only |
| frontend/src/app/api/productApi.ts | ProductVersion API helper is read-only |

## 4. Current Product Version Read Baseline Summary

| Area | Current State | Governance Meaning |
|---|---|---|
| Data model | `product_versions` exists with `lifecycle_status` and `is_current` | Write lifecycle can be governed without new base table |
| API | `GET /api/v1/products/{product_id}/versions`, `GET /api/v1/products/{product_id}/versions/{version_id}` | Read contract is stable and tenant-scoped |
| Service/repository | Read-only methods | Write path must be explicitly introduced, not inferred |
| Frontend | ProductDetail versions section is read-only | FE cannot mutate ProductVersion in current phase |
| RBAC | No ProductVersion action code currently registered | Dedicated code is a precondition for write APIs |

## 5. Product Version Write Command Inventory

Decision values:
- READY_FOR_FUTURE_SLICE
- DEFERRED_REQUIRES_CONTRACT
- FORBIDDEN
- NOT_APPLICABLE

| Command | Decision | Contract Rule |
|---|---|---|
| create_product_version | READY_FOR_FUTURE_SLICE | Allowed as explicit command; parent product must exist in tenant |
| update_product_version_metadata | READY_FOR_FUTURE_SLICE | Allowed for DRAFT; RELEASED allows non-structural metadata only |
| release_product_version | READY_FOR_FUTURE_SLICE | Explicit command only; DRAFT -> RELEASED |
| retire_product_version | READY_FOR_FUTURE_SLICE | Explicit command only; RELEASED or DRAFT -> RETIRED by policy |
| set_current_product_version | READY_FOR_FUTURE_SLICE | Explicit command only; enforce at-most-one-current per product |
| reactivate_product_version | DEFERRED_REQUIRES_CONTRACT | Requires SoD/approval extension and reactivation policy |
| clone_product_version | DEFERRED_REQUIRES_CONTRACT | Requires lineage and copy-semantics contract |
| copy_from_existing_product_version | DEFERRED_REQUIRES_CONTRACT | Requires lineage and copy-semantics contract |
| bulk_import_product_versions | DEFERRED_REQUIRES_CONTRACT | Requires per-row validation and audit ledger |
| bulk_retire_product_versions | DEFERRED_REQUIRES_CONTRACT | Requires dependency and replacement policy |
| delete_product_version | FORBIDDEN | Hard delete forbidden for governed master data |
| bind_to_product_version | NOT_APPLICABLE | Self-binding command is invalid |
| unbind_from_product_version | NOT_APPLICABLE | Self-binding command is invalid |

## 6. Product Version Lifecycle Transition Map

| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test |
|---|---|---|---:|---|---|---|
| ProductVersion | DRAFT | release_product_version | Yes | PRODUCT_VERSION.RELEASED | RELEASED | release from RETIRED denied |
| ProductVersion | DRAFT | retire_product_version | Yes | PRODUCT_VERSION.RETIRED | RETIRED | retire with wrong tenant denied |
| ProductVersion | DRAFT | update_product_version_metadata | Yes | PRODUCT_VERSION.UPDATED | DRAFT | invalid field payload denied |
| ProductVersion | RELEASED | update_product_version_metadata (non-structural only) | Yes | PRODUCT_VERSION.UPDATED | RELEASED | structural update on RELEASED denied |
| ProductVersion | RELEASED | set_current_product_version | Yes | PRODUCT_VERSION.SET_CURRENT | RELEASED (is_current=true target; others false) | second-current invariant violation denied |
| ProductVersion | RELEASED | retire_product_version | Yes | PRODUCT_VERSION.RETIRED | RETIRED | retire without policy checks denied |
| ProductVersion | RELEASED | release_product_version | No | none_required | RELEASED | duplicate release denied |
| ProductVersion | RETIRED | update_product_version_metadata | No | none_required | RETIRED | retired update denied |
| ProductVersion | RETIRED | release_product_version | No | none_required | RETIRED | reopen without reactivation contract denied |
| ProductVersion | RETIRED | set_current_product_version | No | none_required | RETIRED | set current on retired denied |

Notes:
- State mutation must be command-driven and server-side.
- Projection update cannot be the only fact; the mutation event is canonical for command outcome.

## 7. Authorization / Action-Code Map

| Command Family | Current Runtime Code | Candidate Code | Decision |
|---|---|---|---|
| ProductVersion mutation commands | none | admin.master_data.product_version.manage | Required before implementation |
| ProductVersion read commands | require_authenticated_identity | N/A | Keep read behavior unchanged |

Rules:
1. Do not reuse `admin.user.manage` for ProductVersion write commands.
2. Do not route ProductVersion writes under `admin.master_data.product.manage` in this phase.
3. Register the new action code in both runtime registry (`rbac.py`) and design registry before enabling write routes.

## 8. Audit / Event Expectation Map

| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact |
|---|---|---|---|---|
| create_product_version | PRODUCT_VERSION.CREATED | audit_event + domain_event | tenant_id, actor_user_id, product_id, product_version_id, version_code, lifecycle_status, occurred_at | add row in ProductVersion read model |
| update_product_version_metadata | PRODUCT_VERSION.UPDATED | audit_event + domain_event | ids + changed_fields + occurred_at | update mutable fields |
| release_product_version | PRODUCT_VERSION.RELEASED | audit_event + domain_event | ids + previous_status + new_status + occurred_at | lifecycle_status to RELEASED |
| retire_product_version | PRODUCT_VERSION.RETIRED | audit_event + domain_event | ids + previous_status + new_status + occurred_at | lifecycle_status to RETIRED |
| set_current_product_version | PRODUCT_VERSION.SET_CURRENT | audit_event + domain_event | ids + previous_current_id + new_current_id + occurred_at | enforce single current view |
| rejected/forbidden mutation | PRODUCT_VERSION.MUTATION_REJECTED | security_event | ids + reason + actor + occurred_at | no projection mutation |

## 9. Cross-Domain Boundary Map

| Boundary | Allowed | Forbidden |
|---|---|---|
| ProductVersion vs Execution | Execution may reference RELEASED versions | ProductVersion mutation triggers execution transitions |
| ProductVersion vs Quality | Quality may reference version metadata | ProductVersion mutation decides quality pass/fail |
| ProductVersion vs Inventory/Material | Inventory may consume released definitions as reference | ProductVersion mutation posts stock movement/backflush |
| ProductVersion vs ERP/PLM | Explicit integration slice may map version metadata | ProductVersion treated as ERP/PLM source-of-record |
| ProductVersion vs Authorization truth | FE can show action availability hints | FE authorizes mutation or decides allowed actions |
| ProductVersion vs Routing/BOM binding | Future explicit binding slice only | Implicit binding side effects inside version mutation |

## 10. Future API Contract Proposal (Minimal)

Proposed routes (not implemented in this slice):

| Method | Path | Intent | Authorization |
|---|---|---|---|
| POST | /api/v1/products/{product_id}/versions | create_product_version | require_action("admin.master_data.product_version.manage") |
| PATCH | /api/v1/products/{product_id}/versions/{version_id} | update_product_version_metadata | require_action("admin.master_data.product_version.manage") |
| POST | /api/v1/products/{product_id}/versions/{version_id}/release | release_product_version | require_action("admin.master_data.product_version.manage") |
| POST | /api/v1/products/{product_id}/versions/{version_id}/retire | retire_product_version | require_action("admin.master_data.product_version.manage") |
| POST | /api/v1/products/{product_id}/versions/{version_id}/set-current | set_current_product_version | require_action("admin.master_data.product_version.manage") |

Request contract notes:
- `PATCH` must enforce field-level policy by lifecycle state.
- `set-current` must atomically clear previous current version for the same `(tenant_id, product_id)`.
- Cross-tenant and cross-product references must resolve as 404 to avoid entity existence leakage.

## 11. Future Test Matrix

| Test ID | Scenario | Type | Given | When | Then | Event Assertion | Invariant Assertion |
|---|---|---|---|---|---|---|---|
| PVW-01 | create draft version | happy_path | valid tenant/product | create command | 201 + DRAFT | CREATED emitted | tenant/product scoping |
| PVW-02 | duplicate version_code same product | db_invariant | existing code | create command | 409/422 | rejection event emitted | unique `(tenant, product, version_code)` |
| PVW-03 | release draft | state_transition | DRAFT version | release command | RELEASED | RELEASED emitted | valid transition |
| PVW-04 | release retired denied | invalid_state | RETIRED version | release command | 409 | rejected event | no reopen |
| PVW-05 | update released structural denied | invalid_state | RELEASED version | PATCH structural field | 409/422 | rejected event | released structural immutability |
| PVW-06 | update released metadata allowed | happy_path | RELEASED version | PATCH metadata | 200 | UPDATED emitted | metadata-only policy |
| PVW-07 | set current enforces single current | projection_consistency | two released versions | set-current | target current only | SET_CURRENT emitted | at-most-one-current per product |
| PVW-08 | wrong tenant denied | wrong_tenant | tenant A actor, tenant B version | any mutation | 404/403 | security rejection event | tenant isolation |
| PVW-09 | missing permission denied | missing_permission | authenticated without action | mutation | 403 | security rejection event | server-side authorization |
| PVW-10 | retire released | happy_path | RELEASED version | retire command | RETIRED | RETIRED emitted | lifecycle policy |
| PVW-11 | delete forbidden | invalid_input | any version | DELETE attempt | 405/403 | rejection event | no hard delete |
| PVW-12 | audit payload completeness | event_payload | successful mutation | mutate | payload has ids/actor/timestamps | event fields complete | auditability |

## 12. Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required |
|---|---|---|---:|---|
| Tenant isolation for all mutations | tenant | route + service + repository | No (query filter) | Yes |
| Parent product ownership validation | scope | service | No | Yes |
| Single current version per product | state_machine | service + transaction | Yes (future partial unique index recommended) | Yes |
| RELEASED structural immutability | state_machine | service validation | No | Yes |
| RETIRED no mutation | state_machine | service validation | No | Yes |
| Write requires dedicated action code | authorization | route dependency (`require_action`) | No | Yes |
| Write commands auditable | auditability | event/audit layer | No | Yes |
| No implicit cross-domain side effects | integration_boundary | service boundary + tests | No | Yes |

## 13. Verdict Before Writing

Verdict: ALLOW_CONTRACT_ONLY

Reason:
- Design evidence for ProductVersion write governance is sufficient to lock command, lifecycle, authorization, and audit expectations.
- Runtime implementation remains blocked until a dedicated implementation slice introduces routes, service mutations, action code registration, and tests under this contract.

Implementation gate for next slice:
1. Register `admin.master_data.product_version.manage` in runtime and design registries.
2. Introduce mutation routes/services/repositories with server-side invariant enforcement.
3. Add tests from the Future Test Matrix before enabling FE write intents.

## 14. Explicit Exclusions

This contract does not authorize:
- ProductVersion delete API
- ProductVersion reactivation API
- implicit BOM/Routing/ERP/Inventory side effects
- frontend-only authorization decisions

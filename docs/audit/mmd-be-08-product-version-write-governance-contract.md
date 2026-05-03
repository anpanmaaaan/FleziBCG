# MMD-BE-08 — Product Version Write Governance Contract Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Completed Product Version write governance and minimal mutation contract (documentation-only). |

## Routing

- Selected brain: MOM Brain
- Selected mode: Product governance mode + Backend command-boundary design mode + Authorization/action-code governance mode + Lifecycle governance mode + Architecture boundary guardian mode + Source audit/evidence mode + Critical reviewer mode + PR gate/verification mode
- Hard Mode MOM: v3 ON
- Reason: Product Version write governance is the next required lock after MMD-WRITE-GOV-01 before any ProductVersion mutation API is implemented.

## 1. Scope

This slice is documentation-only.

In scope:
- Product Version write governance contract
- command/lifecycle/action-code/audit expectations
- minimal future API and test matrix proposal

Out of scope:
- backend runtime changes
- frontend runtime changes
- DB migration changes
- action-code runtime registration changes
- test implementation

## 2. Baseline Evidence Extract

### 2.1 Mandatory baseline inputs inspected

| Input | Status | Notes |
|---|---|---|
| docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md | Inspected | Confirms frozen MMD read baseline |
| docs/audit/mmd-write-gov-01-command-boundary.md | Inspected | Selects MMD-BE-08 as next write-governance slice |
| docs/audit/mmd-be-03-product-version-foundation-read-model.md | Inspected | Confirms ProductVersion read model and deferred write items |
| docs/audit/mmd-fullstack-06-product-version-fe-read-integration.md | Inspected | Confirms FE ProductVersion section is read-only |
| docs/audit/mmd-be-02-rbac-action-code-fix.md | Inspected | Confirms current MMD mutation action-code baseline |

### 2.2 Design/governance inputs inspected

| Input | Status | Notes |
|---|---|---|
| docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md | Inspected | ProductVersion write commands marked deferred/contract-required |
| docs/design/02_domain/product_definition/product-version-foundation-contract.md | Inspected | Current ProductVersion state and invariants |
| docs/design/02_registry/action-code-registry.md | Inspected | ProductVersion action code not yet present |
| docs/design/00_platform/product-business-truth-overview.md | Inspected | Backend truth and governance principles |
| docs/design/02_domain/product_definition/manufacturing-master-data-and-product-definition-domain.md | Inspected | MMD domain boundaries |

### 2.3 Source evidence summary

| File | Finding |
|---|---|
| backend/app/api/v1/products.py | ProductVersion routes are read-only GET list/detail only |
| backend/app/services/product_version_service.py | Service is read-only |
| backend/app/repositories/product_version_repository.py | Repository is read-only |
| backend/app/security/rbac.py | No ProductVersion-specific mutation action code exists |
| frontend/src/app/pages/ProductDetail.tsx | ProductVersion section is read-only |
| frontend/src/app/api/productApi.ts | ProductVersion API helper is read-only |

## 3. Current Product Version Read Baseline Summary

| Dimension | Current Baseline | Decision Impact |
|---|---|---|
| Data | `product_versions` table exists with lifecycle and current flags | Mutation contract can be defined without schema invention |
| API | GET list/detail only | Write routes must be explicit new contract routes |
| FE | Read-only section in ProductDetail | FE write actions remain disabled |
| RBAC | No ProductVersion mutation code | New action code is required before implementation |

## 4. Product Version Write Command Inventory

| Command | Decision | Rationale |
|---|---|---|
| create_product_version | READY_FOR_FUTURE_SLICE | Explicit bounded command with parent-product existence check |
| update_product_version_metadata | READY_FOR_FUTURE_SLICE | DRAFT mutable; RELEASED metadata-only policy |
| release_product_version | READY_FOR_FUTURE_SLICE | Canonical lifecycle transition command |
| retire_product_version | READY_FOR_FUTURE_SLICE | Canonical lifecycle transition command |
| set_current_product_version | READY_FOR_FUTURE_SLICE | Required command to enforce single-current invariant |
| reactivate_product_version | DEFERRED_REQUIRES_CONTRACT | Needs SoD and reactivation policy |
| clone/copy_from_existing | DEFERRED_REQUIRES_CONTRACT | Needs lineage and copy-semantics contract |
| bulk_import/bulk_retire | DEFERRED_REQUIRES_CONTRACT | Needs batch governance and audit ledger |
| delete_product_version | FORBIDDEN | Hard delete forbidden for governed master data |

## 5. Product Version Lifecycle Transition Map

| Current State | Command | Decision | Target State | Guardrail |
|---|---|---|---|---|
| DRAFT | release_product_version | ALLOW | RELEASED | command-only transition, server-governed |
| DRAFT | retire_product_version | ALLOW | RETIRED | command-only transition, server-governed |
| DRAFT | update_product_version_metadata | ALLOW | DRAFT | payload validation required |
| RELEASED | update_product_version_metadata (non-structural) | ALLOW | RELEASED | structural fields immutable |
| RELEASED | set_current_product_version | ALLOW | RELEASED | atomic single-current enforcement |
| RELEASED | retire_product_version | ALLOW | RETIRED | lifecycle command required |
| RELEASED | release_product_version | FORBID | RELEASED | duplicate release denied |
| RETIRED | update/release/set_current | FORBID | RETIRED | no reopen in current contract |

## 6. Authorization / Action-Code Map

| Scope | Current | Required Future | Decision |
|---|---|---|---|
| ProductVersion write commands | no dedicated code | admin.master_data.product_version.manage | REQUIRED_BEFORE_IMPLEMENTATION |
| ProductVersion read commands | require_authenticated_identity | unchanged | KEEP |

Hard rule:
- Do not use `admin.user.manage` or piggyback ProductVersion writes onto `admin.master_data.product.manage`.

## 7. Audit / Event Expectation Map

| Command Type | Minimum Event/Audit Expectation |
|---|---|
| create | audit + governed/domain event with ids, actor, tenant, lifecycle |
| update metadata | audit + changed_fields |
| release | audit + lifecycle transition record |
| retire | audit + lifecycle transition record |
| set current | audit + previous/current pointer change |
| denied mutation | security/audit rejection event with reason |

Forbidden side effects:
- no execution command/event mutation
- no quality pass/fail mutation
- no material/inventory posting
- no backflush/ERP posting

## 8. Cross-Domain Boundary Map

| Boundary | Allowed | Forbidden |
|---|---|---|
| ProductVersion vs Execution | execution reads released definitions | ProductVersion write changes execution state |
| ProductVersion vs Quality | quality references metadata | ProductVersion write decides quality outcomes |
| ProductVersion vs Inventory/Material | inventory references definitions | ProductVersion write posts stock transactions |
| ProductVersion vs ERP/PLM | explicit later bridge | ProductVersion used as ERP/PLM source-of-record |
| ProductVersion vs FE auth | FE sends intent only | FE decides authorization or lifecycle truth |

## 9. Future API Contract Proposal

Proposed minimal endpoints (not implemented):

- POST /api/v1/products/{product_id}/versions
- PATCH /api/v1/products/{product_id}/versions/{version_id}
- POST /api/v1/products/{product_id}/versions/{version_id}/release
- POST /api/v1/products/{product_id}/versions/{version_id}/retire
- POST /api/v1/products/{product_id}/versions/{version_id}/set-current

All mutation endpoints must require:
- require_action("admin.master_data.product_version.manage")
- tenant and product scoping checks
- invariant enforcement and auditable outcome

## 10. Future Test Matrix

| Test ID | Scenario | Expected |
|---|---|---|
| PVW-01 | create version happy path | 201 + DRAFT + audit event |
| PVW-02 | duplicate version code same product | reject with invariant violation |
| PVW-03 | release DRAFT | RELEASED transition recorded |
| PVW-04 | release RETIRED denied | state-transition rejection |
| PVW-05 | structural update on RELEASED denied | immutability enforcement |
| PVW-06 | metadata update on RELEASED allowed | non-structural update accepted |
| PVW-07 | set current enforces single current | exactly one current version remains |
| PVW-08 | wrong tenant mutation denied | 404/403 with no leak |
| PVW-09 | missing permission denied | 403 |
| PVW-10 | retire RELEASED | RETIRED transition recorded |
| PVW-11 | delete attempt denied | forbidden/not allowed |
| PVW-12 | event payload completeness | all required audit fields present |

## 11. Verdict Before Writing

Verdict: PASS (contract creation) / BLOCKED (runtime implementation)

Interpretation:
- PASS for MMD-BE-08 scope because this slice is contract-only and all required governance maps are now defined.
- Runtime implementation remains blocked until a follow-up implementation slice registers action code, adds mutation routes/services, and implements test matrix coverage.

## 12. Files Produced in This Slice

- docs/design/02_domain/product_definition/product-version-write-governance-contract.md
- docs/audit/mmd-be-08-product-version-write-governance-contract.md

No other files were modified.

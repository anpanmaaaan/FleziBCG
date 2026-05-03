# MMD Write-Path Governance Matrix

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Added MMD write-path governance matrix and command boundary after complete read integration baseline. |

## 1. Scope
This document defines the write-path governance matrix for Manufacturing Master Data (MMD) and Product Definition.

It is a governance contract, not an implementation slice.

In scope:
- domain-by-domain write command eligibility
- lifecycle transition governance
- authorization and action-code expectations
- audit and event expectations for future mutations
- cross-domain boundary guardrails
- frontend and backend write readiness gates
- stop conditions for future agents

Out of scope:
- backend write API implementation
- frontend write UI implementation
- schema or migration changes
- runtime action-code registry changes
- route or screenStatus changes

## 2. Baseline Read Integration State
Read baseline is frozen by MMD-READ-BASELINE-02 and remains the prerequisite for all write-path work.

| Domain | Read API | FE Screen | Status | Evidence |
|---|---|---|---|---|
| Product | GET /api/v1/products, GET /api/v1/products/{id} | /products, /products/:productId | PARTIAL/BACKEND_API | MMD-READ-BASELINE-02, products.py, ProductDetail.tsx |
| Product Version | GET /api/v1/products/{product_id}/versions, GET /api/v1/products/{product_id}/versions/{version_id} | ProductDetail versions section | PARTIAL/BACKEND_API | MMD-BE-03, MMD-FULLSTACK-06 |
| Routing | GET /api/v1/routings, GET /api/v1/routings/{id} | /routes, /routes/:routeId | PARTIAL/BACKEND_API | MMD-READ-BASELINE-02, routings.py |
| Routing Operation | read via routing detail operations[] | /routes/:routeId/operations/:operationId | PARTIAL/BACKEND_API | routing.py, routing schemas, MMD-FULLSTACK-02 |
| Resource Requirement | GET nested list/detail under routings operations | /resource-requirements | PARTIAL/BACKEND_API | resource-requirement contract, routings.py |
| BOM | GET /api/v1/products/{product_id}/boms, GET /api/v1/products/{product_id}/boms/{bom_id} | /bom, /bom/:id | PARTIAL/BACKEND_API | MMD-BE-05, MMD-FULLSTACK-07 |
| BOM Item | included in BomDetail.items | /bom/:id components | PARTIAL/BACKEND_API | bom.py, bom schema |
| Reason Code | GET /api/v1/reason-codes, GET /api/v1/reason-codes/{id} | /reason-codes | PARTIAL/BACKEND_API | MMD-BE-07, MMD-FULLSTACK-08 |

## 3. Write-Path Governance Principles
1. Backend remains source of truth for lifecycle, authorization, and audit.
2. Frontend may send intent only; frontend cannot authorize or derive mutation eligibility.
3. No write command is implementation-ready without owner, schema boundary, lifecycle rule, action code, tenant/scope rule, audit expectation, and stop conditions.
4. Read API existence does not imply write readiness.
5. MMD write paths must not leak into execution, quality, material/inventory, backflush, ERP/PLM, or traceability ownership.
6. Privileged write commands must remain explicitly auditable.
7. For this phase, hard delete of governed master data is forbidden unless a dedicated exception contract is approved.

## 4. Domain Write-Path Inventory
| Domain | Current Write API | Current Action Code | Governance State | Notes |
|---|---|---|---|---|
| Product | Yes | admin.master_data.product.manage | PARTIAL_GOVERNED_RUNTIME_EXISTS | create/update/release/retire exist; matrix unification added here |
| Product Version | No | none | DEFERRED_REQUIRES_CONTRACT | read-only foundation only |
| Routing | Yes | admin.master_data.routing.manage | PARTIAL_GOVERNED_RUNTIME_EXISTS | create/update/release/retire exist |
| Routing Operation | Yes (nested under routing) | admin.master_data.routing.manage | PARTIAL_GOVERNED_RUNTIME_EXISTS | add/update/remove exist |
| Resource Requirement | Yes (nested) | admin.master_data.resource_requirement.manage | PARTIAL_GOVERNED_RUNTIME_EXISTS | create/update/delete exist; parent lifecycle-gated |
| BOM | No | none | DEFERRED_REQUIRES_CONTRACT | read-only implemented |
| BOM Item | No | none | DEFERRED_REQUIRES_CONTRACT | read-only via bom detail |
| Reason Code | No | none | DEFERRED_REQUIRES_CONTRACT | read-only implemented; separate from downtime_reason |

## 5. Command Boundary Matrix
Decision values:
- READY_FOR_FUTURE_SLICE
- DEFERRED_REQUIRES_CONTRACT
- FORBIDDEN
- NOT_APPLICABLE
- UNKNOWN_NEEDS_EVIDENCE

| Domain | Command | Decision | Required Future Guardrails |
|---|---|---|---|
| Product | create | READY_FOR_FUTURE_SLICE | explicit command owner, tenant-scoped uniqueness, audit/security record |
| Product | update | READY_FOR_FUTURE_SLICE | structural-vs-metadata guard by lifecycle |
| Product | release | READY_FOR_FUTURE_SLICE | explicit release command path only |
| Product | retire | READY_FOR_FUTURE_SLICE | explicit retire command path only |
| Product | reactivate | DEFERRED_REQUIRES_CONTRACT | explicit reactivation policy and SoD review |
| Product | delete | FORBIDDEN | governed identity retention and linkage safety |
| Product | set_current | NOT_APPLICABLE | version concept |
| Product | clone | DEFERRED_REQUIRES_CONTRACT | lineage, copied fields policy, audit payload |
| Product | copy_from_existing | DEFERRED_REQUIRES_CONTRACT | same as clone |
| Product | bind_to_product_version | NOT_APPLICABLE | inverse relation |
| Product | unbind_from_product_version | NOT_APPLICABLE | inverse relation |
| Product | bulk_import | DEFERRED_REQUIRES_CONTRACT | per-row validation and audit trace |
| Product | bulk_retire | DEFERRED_REQUIRES_CONTRACT | per-entity lifecycle and dependency checks |
| Product Version | create | DEFERRED_REQUIRES_CONTRACT | candidate action code + is_current invariant |
| Product Version | update | DEFERRED_REQUIRES_CONTRACT | released immutability policy |
| Product Version | release | DEFERRED_REQUIRES_CONTRACT | explicit lifecycle command |
| Product Version | retire | DEFERRED_REQUIRES_CONTRACT | explicit lifecycle command |
| Product Version | reactivate | DEFERRED_REQUIRES_CONTRACT | explicit reactivation contract |
| Product Version | delete | FORBIDDEN | version/audit integrity |
| Product Version | set_current | DEFERRED_REQUIRES_CONTRACT | single-current invariant |
| Product Version | clone | DEFERRED_REQUIRES_CONTRACT | lineage and binding policy |
| Product Version | copy_from_existing | DEFERRED_REQUIRES_CONTRACT | lineage and binding policy |
| Product Version | bind_to_product_version | NOT_APPLICABLE | self-binding invalid |
| Product Version | unbind_from_product_version | NOT_APPLICABLE | self-binding invalid |
| Product Version | bulk_import | DEFERRED_REQUIRES_CONTRACT | uniqueness and current-version conflict control |
| Product Version | bulk_retire | DEFERRED_REQUIRES_CONTRACT | protected against retiring active current version without replacement |
| Routing | create | READY_FOR_FUTURE_SLICE | tenant/product linkage invariant |
| Routing | update | READY_FOR_FUTURE_SLICE | released structural immutability guard |
| Routing | release | READY_FOR_FUTURE_SLICE | explicit release command path |
| Routing | retire | READY_FOR_FUTURE_SLICE | explicit retire command path |
| Routing | reactivate | DEFERRED_REQUIRES_CONTRACT | no contract exists |
| Routing | delete | FORBIDDEN | operation/resource requirement integrity |
| Routing | set_current | NOT_APPLICABLE | version concept |
| Routing | clone | DEFERRED_REQUIRES_CONTRACT | op/resource requirement copy semantics |
| Routing | copy_from_existing | DEFERRED_REQUIRES_CONTRACT | op/resource requirement copy semantics |
| Routing | bind_to_product_version | DEFERRED_REQUIRES_CONTRACT | binding contract deferred |
| Routing | unbind_from_product_version | DEFERRED_REQUIRES_CONTRACT | binding contract deferred |
| Routing | bulk_import | DEFERRED_REQUIRES_CONTRACT | sequence and uniqueness validation |
| Routing | bulk_retire | DEFERRED_REQUIRES_CONTRACT | dependency and impact checks |
| Routing Operation | create | READY_FOR_FUTURE_SLICE | parent routing must be DRAFT |
| Routing Operation | update | READY_FOR_FUTURE_SLICE | parent routing must be DRAFT |
| Routing Operation | retire | NOT_APPLICABLE | parent lifecycle governs |
| Routing Operation | release | NOT_APPLICABLE | parent lifecycle governs |
| Routing Operation | reactivate | NOT_APPLICABLE | parent lifecycle governs |
| Routing Operation | delete | READY_FOR_FUTURE_SLICE | parent routing must be DRAFT |
| Routing Operation | set_current | NOT_APPLICABLE | version concept |
| Routing Operation | clone | DEFERRED_REQUIRES_CONTRACT | sequence and copied sub-links |
| Routing Operation | copy_from_existing | DEFERRED_REQUIRES_CONTRACT | sequence and copied sub-links |
| Routing Operation | bind_to_product_version | DEFERRED_REQUIRES_CONTRACT | deferred relation policy |
| Routing Operation | unbind_from_product_version | DEFERRED_REQUIRES_CONTRACT | deferred relation policy |
| Routing Operation | bulk_import | DEFERRED_REQUIRES_CONTRACT | sequence collision control |
| Routing Operation | bulk_retire | NOT_APPLICABLE | parent lifecycle governs |
| Resource Requirement | create | READY_FOR_FUTURE_SLICE | parent routing state gate, uniqueness key |
| Resource Requirement | update | READY_FOR_FUTURE_SLICE | parent routing state gate |
| Resource Requirement | retire | NOT_APPLICABLE | parent lifecycle governs |
| Resource Requirement | release | NOT_APPLICABLE | parent lifecycle governs |
| Resource Requirement | reactivate | NOT_APPLICABLE | parent lifecycle governs |
| Resource Requirement | delete | READY_FOR_FUTURE_SLICE | allowed only with parent DRAFT |
| Resource Requirement | set_current | NOT_APPLICABLE | version concept |
| Resource Requirement | clone | DEFERRED_REQUIRES_CONTRACT | copied capability semantics |
| Resource Requirement | copy_from_existing | DEFERRED_REQUIRES_CONTRACT | copied capability semantics |
| Resource Requirement | bind_to_product_version | DEFERRED_REQUIRES_CONTRACT | deferred binding policy |
| Resource Requirement | unbind_from_product_version | DEFERRED_REQUIRES_CONTRACT | deferred binding policy |
| Resource Requirement | bulk_import | DEFERRED_REQUIRES_CONTRACT | duplicate prevention and state gate |
| Resource Requirement | bulk_retire | NOT_APPLICABLE | parent lifecycle governs |
| BOM | create | DEFERRED_REQUIRES_CONTRACT | new action code and write contract required |
| BOM | update | DEFERRED_REQUIRES_CONTRACT | released immutability policy required |
| BOM | release | DEFERRED_REQUIRES_CONTRACT | explicit lifecycle command required |
| BOM | retire | DEFERRED_REQUIRES_CONTRACT | explicit lifecycle command required |
| BOM | reactivate | DEFERRED_REQUIRES_CONTRACT | no reactivation policy defined |
| BOM | delete | FORBIDDEN | definition history and traceability risk |
| BOM | set_current | NOT_APPLICABLE | version concept |
| BOM | clone | DEFERRED_REQUIRES_CONTRACT | item copy lineage + audit |
| BOM | copy_from_existing | DEFERRED_REQUIRES_CONTRACT | item copy lineage + audit |
| BOM | bind_to_product_version | DEFERRED_REQUIRES_CONTRACT | explicitly deferred by baseline |
| BOM | unbind_from_product_version | DEFERRED_REQUIRES_CONTRACT | explicitly deferred by baseline |
| BOM | bulk_import | DEFERRED_REQUIRES_CONTRACT | per-item validation + referential checks |
| BOM | bulk_retire | DEFERRED_REQUIRES_CONTRACT | downstream dependency checks |
| BOM Item | create | DEFERRED_REQUIRES_CONTRACT | parent BOM state gate and quantity policy |
| BOM Item | update | DEFERRED_REQUIRES_CONTRACT | parent BOM state gate |
| BOM Item | retire | NOT_APPLICABLE | parent lifecycle governs |
| BOM Item | release | NOT_APPLICABLE | parent lifecycle governs |
| BOM Item | reactivate | NOT_APPLICABLE | parent lifecycle governs |
| BOM Item | delete | DEFERRED_REQUIRES_CONTRACT | parent BOM state gate |
| BOM Item | set_current | NOT_APPLICABLE | version concept |
| BOM Item | clone | DEFERRED_REQUIRES_CONTRACT | line_no collision handling |
| BOM Item | copy_from_existing | DEFERRED_REQUIRES_CONTRACT | line_no collision handling |
| BOM Item | bind_to_product_version | DEFERRED_REQUIRES_CONTRACT | deferred product version binding |
| BOM Item | unbind_from_product_version | DEFERRED_REQUIRES_CONTRACT | deferred product version binding |
| BOM Item | bulk_import | DEFERRED_REQUIRES_CONTRACT | quantity/UOM validation |
| BOM Item | bulk_retire | NOT_APPLICABLE | parent lifecycle governs |
| Reason Code | create | DEFERRED_REQUIRES_CONTRACT | candidate action code + lifecycle contract required |
| Reason Code | update | DEFERRED_REQUIRES_CONTRACT | released immutability and category policy |
| Reason Code | release | DEFERRED_REQUIRES_CONTRACT | explicit lifecycle command required |
| Reason Code | retire | DEFERRED_REQUIRES_CONTRACT | explicit lifecycle command required |
| Reason Code | reactivate | DEFERRED_REQUIRES_CONTRACT | no reactivation policy defined |
| Reason Code | delete | FORBIDDEN | operational historical classification risk |
| Reason Code | set_current | NOT_APPLICABLE | version concept |
| Reason Code | clone | DEFERRED_REQUIRES_CONTRACT | code uniqueness and lineage policy |
| Reason Code | copy_from_existing | DEFERRED_REQUIRES_CONTRACT | code uniqueness and lineage policy |
| Reason Code | bind_to_product_version | NOT_APPLICABLE | unrelated aggregate |
| Reason Code | unbind_from_product_version | NOT_APPLICABLE | unrelated aggregate |
| Reason Code | bulk_import | DEFERRED_REQUIRES_CONTRACT | domain/category validation and duplicates |
| Reason Code | bulk_retire | DEFERRED_REQUIRES_CONTRACT | usage impact and audit policy |

## 6. Lifecycle Transition Matrix
Decision values:
- ALLOW
- FORBID
- DEFER
- N/A

| Domain | Transition | Decision | Reason |
|---|---|---|---|
| Product | DRAFT -> RELEASED | ALLOW | explicit release command exists |
| Product | RELEASED -> RETIRED | ALLOW | explicit retire command exists |
| Product | DRAFT -> RETIRED | ALLOW | retire path currently allows this |
| Product | RETIRED -> DRAFT | FORBID | no reopen contract |
| Product | RETIRED -> RELEASED | FORBID | no reactivation contract |
| Product | RELEASED -> DRAFT | FORBID | release should be one-way in current governance |
| Product Version | DRAFT -> RELEASED | DEFER | write contract not defined |
| Product Version | RELEASED -> RETIRED | DEFER | write contract not defined |
| Product Version | DRAFT -> RETIRED | DEFER | usage safeguard contract needed |
| Product Version | RETIRED -> DRAFT | FORBID | no reopen contract |
| Product Version | RETIRED -> RELEASED | FORBID | no reactivation contract |
| Product Version | RELEASED -> DRAFT | FORBID | release immutability direction |
| Routing | DRAFT -> RELEASED | ALLOW | explicit release command exists |
| Routing | RELEASED -> RETIRED | ALLOW | explicit retire command exists |
| Routing | DRAFT -> RETIRED | ALLOW | retire path currently allows this |
| Routing | RETIRED -> DRAFT | FORBID | no reopen contract |
| Routing | RETIRED -> RELEASED | FORBID | no reactivation contract |
| Routing | RELEASED -> DRAFT | FORBID | release should be one-way |
| Resource Requirement | all transitions | N/A | lifecycle governed by parent routing |
| Routing Operation | all transitions | N/A | lifecycle governed by parent routing |
| BOM | DRAFT -> RELEASED | DEFER | write path not defined |
| BOM | RELEASED -> RETIRED | DEFER | write path not defined |
| BOM | DRAFT -> RETIRED | DEFER | operation-usage guard not yet defined |
| BOM | RETIRED -> DRAFT | FORBID | no reopen contract |
| BOM | RETIRED -> RELEASED | FORBID | no reactivation contract |
| BOM | RELEASED -> DRAFT | FORBID | release should be one-way |
| BOM Item | all transitions | N/A | lifecycle governed by parent BOM |
| Reason Code | DRAFT -> RELEASED | DEFER | write path not defined |
| Reason Code | RELEASED -> RETIRED | DEFER | write path not defined |
| Reason Code | DRAFT -> RETIRED | DEFER | usage and harmonization guards not yet defined |
| Reason Code | RETIRED -> DRAFT | FORBID | no reopen contract |
| Reason Code | RETIRED -> RELEASED | FORBID | no reactivation contract |
| Reason Code | RELEASED -> DRAFT | FORBID | release should be one-way |

## 7. Authorization / Action-Code Matrix
| Domain | Current Code | Candidate Code | Decision |
|---|---|---|---|
| Product | admin.master_data.product.manage | admin.master_data.product.manage | keep |
| Routing | admin.master_data.routing.manage | admin.master_data.routing.manage | keep |
| Routing Operation | admin.master_data.routing.manage | admin.master_data.routing.manage (or split later) | keep for now |
| Resource Requirement | admin.master_data.resource_requirement.manage | admin.master_data.resource_requirement.manage | keep |
| Product Version | none | admin.master_data.product_version.manage | required for future write slice |
| BOM | none | admin.master_data.bom.manage | required for future write slice |
| BOM Item | none | admin.master_data.bom.manage | required for future write slice |
| Reason Code | none | admin.master_data.reason_code.manage | required for future write slice |

Additional notes:
- Read endpoints stay on require_authenticated_identity.
- Mutation endpoints require require_action(action_code).
- Future SoD risk exists for release/retire and potential reactivation commands; phase extension may split manage into command-specific action codes.

## 8. Audit / Event Expectation Matrix
| Command Type | Future Audit/Event Expectation | Forbidden Side Effects |
|---|---|---|
| create | audit log + security event + lifecycle record | no execution command, no material movement |
| update | audit log with changed_fields + security event | no quality decision mutation |
| release | audit log + lifecycle transition record + canonical domain/governed event | no production completion, no ERP post |
| retire | audit log + lifecycle transition record + canonical domain/governed event | no backflush, no inventory transaction |
| reactivate (if later approved) | explicit audit + explicit approval/SoD extension + transition record | no silent state rollback |
| delete (exception only) | high-severity audit + retention policy + explicit authorization | no hard-delete of historical operational references |
| bind/unbind product version | audit + invariant checks + transition record | no implicit external sync |
| bulk_import / bulk_retire | batch audit + per-item result logs + error ledger | no bypass of auth/tenant/scope rules |
| read/list/get | no domain event required | no mutation side effects |

## 9. Cross-Domain Boundary Guardrails
| Boundary | Current Decision | Allowed Future Behavior | Forbidden Behavior | Risk if Violated |
|---|---|---|---|---|
| MMD vs Execution | separated | execution references released MMD definitions | MMD write path triggers execution transitions | operational truth corruption |
| MMD vs Quality | separated | quality may reference MMD reason/category metadata | MMD write path decides quality pass/fail | quality governance breach |
| MMD vs Material / Inventory | separated | inventory consumes released definitions as reference | MMD write path posts stock movement | inventory truth drift |
| MMD vs Backflush | separated | none in MMD layer | MMD triggers backflush | financial/material misstatement |
| MMD vs ERP / PLM | separated | explicit integration slices only | implicit ERP/PLM posting from MMD mutation | external SoT conflict |
| MMD vs Traceability / Genealogy | separated | traceability may reference definitions | MMD writes genealogy links | genealogy contamination |
| MMD vs Maintenance | separated | maintenance may classify with reason codes | MMD executes maintenance workflow | ownership confusion |
| MMD vs Planning / APS | separated | APS may read released definitions | MMD mutation directly schedules operations | planning inconsistency |
| MMD vs Digital Twin | separated | digital twin consumes released definitions | MMD treated as simulation runtime authority | model drift |
| MMD vs Authorization Truth | server-side | frontend shows availability hints only | frontend authorizes writes | privilege escalation |
| Frontend UI vs Backend Truth | backend truth | frontend intent + backend validation | frontend state as authoritative mutation truth | unsafe client bypass |
| Reason Codes vs Downtime Reasons | separate entities | explicit harmonization slice may map them | silent merge/replacement | downtime regression |
| BOM vs Material Consumption | separated | BOM remains definition only | BOM write triggers consumption | inventory/accounting error |
| Product Version vs ERP/PLM Revision | separated | explicit bridge later | treating product_version as ERP revision authority | SoR conflict |
| Resource Requirement vs Routing Operation | RR owns capability requirement details | routing references RR associations | duplicated skill/checkpoint truth in routing op columns | dual source-of-truth defects |

## 10. Frontend Write UI Readiness Gate
Frontend write UI is NOT ready until all conditions pass:

1. backend write contract slice for target domain is approved
2. target command lifecycle transition is explicitly governed in this matrix or successor contract
3. target action code exists in runtime registry and design registry
4. backend mutation API exists and is tenant/scoped/authorized server-side
5. audit/event expectation is implemented or explicitly deferred with tracked follow-up
6. regression checks are extended to ensure write UI does not bypass backend truth
7. disabled-state fallback remains for unauthorized or unsupported commands

## 11. Backend Implementation Readiness Gate
A domain-specific write API slice is ready only when all are present:

1. command owner defined (route -> service -> repository)
2. request schema boundary and field-level invariants documented
3. lifecycle transition map completed for target domain
4. action code selected and registered (runtime + documentation)
5. tenant/scope enforcement path explicitly validated
6. audit and security event expectations defined
7. no-cross-domain side effect guarantees documented
8. test matrix defined (happy path, invalid state, wrong tenant, missing permission, regression)
9. stop conditions cleared (no conflicting docs, no missing source truth)

## 12. Testing Requirements for Future Write Slices
Each future write slice must include minimum tests:

1. happy path per command
2. invalid lifecycle transition rejections
3. wrong tenant isolation behavior
4. missing/invalid action code behavior
5. required-field and schema validation errors
6. duplicate and uniqueness invariant handling
7. audit/security event emission assertions
8. no-cross-domain side effect assertions
9. regression tests for read baseline stability

## 13. Recommended Write-Path Sequence
| Sequence | Slice | Reason |
|---|---|---|
| 1 | MMD-BE-08 — Product Version Write Governance / Minimal Mutation Contract | safest first governance domain; read-connected and low operational side effects |
| 2 | MMD-BE-11 — Product Version Write API Foundation | implement governed commands from MMD-BE-08 |
| 3 | MMD-BE-09 — BOM Write Governance / Minimal Mutation Contract | lock item mutation and lifecycle boundaries after version governance |
| 4 | MMD-BE-12 — BOM Write API Foundation | implement BOM write path under explicit governance |
| 5 | MMD-BE-10 — Reason Code Write Governance / Minimal Mutation Contract | resolve downtime harmonization risk before mutation |
| 6 | MMD-BE-13 — Reason Code Write API Foundation | implement reason code write path only after governance lock |
| 7 | MMD-FE-QA-02 — Browser Screenshot Runtime QA / Visual Evidence Pack | FE write UX validation only after backend write governance/API are in place |

## 14. Explicit Non-Goals
This matrix does not:
- implement any mutation endpoint
- enable any frontend write action
- modify migrations or schemas
- alter runtime RBAC mappings
- define approval or e-signature workflows for this phase
- define ERP/PLM integration behavior

## 15. Stop Conditions for Future Agents
Future agents must stop and report if any is true:

1. read baseline evidence is missing or contradictory
2. target domain contract lacks lifecycle ownership clarity
3. required action code cannot be mapped to runtime registry strategy
4. proposed write command crosses into execution/quality/material/ERP ownership
5. implementation would require immediate unrelated runtime refactor
6. expected doc files for the slice are already modified by unrelated uncommitted work
7. repo has unresolved merge conflicts

Stop report format to use:
- Stop Condition Triggered
- Evidence
- Why Continuing Is Unsafe
- Options
- Recommended Decision

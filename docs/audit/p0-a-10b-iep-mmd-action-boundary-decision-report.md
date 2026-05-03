# P0-A-10B Report
# IEP MMD Action Boundary Decision / Create-Update vs Release-Retire Split

**Slice:** P0-A-10B  
**Date:** 2026-05-03  
**Status:** COMPLETE  
**Decision Type:** Design contract — MMD action boundary decision (Option B: document future split, no runtime change)

---

## Summary

P0-A-10B decides the future action-code boundary between IEP and ADM/PMG for MMD
create/update (draft authoring) versus release/retire (governed lifecycle transitions).

**Option B** is selected: define candidate future split, no runtime change.

Evidence shows that the current `admin.master_data.*.manage` codes are coarse-grained,
collapsing both draft mutations (create/update) and governed lifecycle transitions
(release/retire) under a single ADMIN-family code. This is acceptable for the current
foundation state — no release/approval workflow is implemented — but the split must be
planned before Phase C (Mutation Enablement) of the MMD hardening track proceeds.

The critical blocker for IEP participation is that **IEP has no ADMIN family** in
`SYSTEM_ROLE_FAMILIES`, and `SYSTEM_ROLE_FAMILIES` is frozen per Phase 6 governance.
Any change to IEP's family set requires a Phase 7+ design gate.

No runtime action code was added. No route guard was changed. No MMD service was changed.
No migration was added.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Architecture + Strict (design-first boundary decision, no runtime code)
- **Hard Mode MOM:** v3
- **Reason:** Touches role/action/scope assignment, MMD governance boundary, future
  action-code semantics, critical authorization invariant, and future DB/API governance
  contract. Hard Mode MOM v3 is mandatory.

---

## Hard Mode MOM v3 Gate

### 1. Design Evidence Extract

| Evidence Item | Source | Finding |
|---|---|---|
| `admin.master_data.*.manage` maps to ADMIN family | `backend/app/security/rbac.py` L56–60 | All 4 MMD codes are ADMIN family; coarse-grained |
| `release` and `retire` guarded by same code as `create`/`update` | `backend/app/api/v1/products.py` L74, L113, L152 | No separation at route level between draft and lifecycle transitions |
| `release` and `retire` on routing all use `admin.master_data.routing.manage` | `backend/app/api/v1/routings.py` L75, L87, L111, L118, L133, L165, L174 | Same — coarse guard covers all routing mutations |
| `IEP`: `{"VIEW", "CONFIGURE"}` | `backend/app/security/rbac.py` L27 | IEP has NO ADMIN family → zero current MMD mutation access |
| `ADM`: `{"VIEW", "ADMIN"}` | `backend/app/security/rbac.py` L32 | ADM has ADMIN → can use all MMD mutation codes |
| `PMG`: `{"VIEW", "APPROVE"}` | `backend/app/security/rbac.py` L31 | PMG has APPROVE but not ADMIN → cannot use MMD mutation codes |
| `SYSTEM_ROLE_FAMILIES` frozen per Phase 6 governance | `backend/app/security/rbac.py` L22–24 comment | Phase 7+ gate required for any family change |
| Proposal A.5 calls for per-operation split | `docs/proposals/2026-05-01-master-data-hardening-proposal.md` §A.5 | IEP/PMG get create/update; ADM gets release/retire — but the proposal is REJECTED v1.0 |
| Proposal is REJECTED | `docs/proposals/2026-05-01-master-data-hardening-proposal.md` header | "REJECTED v1.0 — superseded by PO-SA review" |
| No release/approval workflow implemented yet | Source scan of services | `product_service.release_product` calls lifecycle check but no approval gate |
| P0-A-10 defines CONFIGURE as process parameter/threshold semantics | `docs/design/01_foundation/iep-configuration-action-contract.md` | CONFIGURE ≠ MMD draft authoring (routing/BOM structure ≠ process parameters) |
| P0-A-10A defers CONFIGURE entity design to Phase 11 | `docs/design/01_foundation/process-configuration-entity-contract.md` | No CONFIGURE codes in runtime; Phase 11 trigger required |
| MMD domain owns routing/BOM/product definitions | `docs/design/00_platform/domain-boundary-map.md` §1 | MMD/Admin family is the correct owner — not CONFIGURE |
| 58 tests pass | Verification run | Registry alignment + MMD action code tests all pass |

### 2. Event Map

This is a design-only slice. No runtime events are emitted.

For record:
- MMD lifecycle actions currently emit security/audit events via `security_event_service`
  with `resource_type="product"`, `"routing"`, etc.
- Future lifecycle split (when implemented) must NOT trigger execution, material, ERP,
  quality disposition, or genealogy side effects.
- Security events for release/retire are already emitted separately from create/update
  (by service-level routing, not by action code) — this is correct regardless of split.

### 3. Invariant Map

| Invariant | Evidence Source | Test / Contract Lock |
|---|---|---|
| IEP CONFIGURE remains reserved for Phase 11 process configuration | P0-A-10 contract; P0-A-10A entity contract | `test_rbac_configure_family_boundary.py` — 0 CONFIGURE codes |
| MMD product/BOM/routing/version truth remains ADMIN-family | rbac.py ACTION_CODE_REGISTRY | `test_mmd_rbac_action_codes.py`, `test_rbac_action_registry_alignment.py` |
| `SYSTEM_ROLE_FAMILIES` frozen | rbac.py L22–24 comment | Phase 7+ gate; no test currently but invariant documented in code comment |
| No new action code added in this slice | This report | `test_action_code_registry_contains_exactly_canonical_set` — exact count |
| No route guard changed | Source review | `test_mmd_rbac_action_codes.py` route-level checks |
| No MMD service behavior changed | This report | All MMD service tests unaffected |

### 4. State Transition Map

MMD entity lifecycle (current implementation):

```
DRAFT → [release] → RELEASED → [retire] → RETIRED
              ↑
         [create new version]
         (creates new DRAFT with supersedes_id → prior RELEASED)
```

- **DRAFT state**: created by `create_*` and mutated by `update_*`.
- **RELEASED state**: entered by `release_*`. RELEASED entities cannot be structurally mutated.
- **RETIRED state**: entered by `retire_*`. Terminal state.
- **New version flow**: a new DRAFT is created referencing the superseded RELEASED entity.

This slice does NOT implement state changes. State map is documented for Phase C planning.

### 5. Test Matrix

| Future Test Area | Required Test | Priority |
|---|---|---|
| Draft action code present in registry | `test_rbac_action_registry_alignment.py` equivalent | P0 when codes are added |
| Lifecycle action code present in registry | Same | P0 when codes are added |
| Draft code is ADMIN family | Registry alignment test | P0 |
| Lifecycle code is ADMIN family | Registry alignment test | P0 |
| IEP can create/update (draft) if given draft binding | Route-level auth test | P1 — needs approval workflow first |
| IEP cannot release/retire (lifecycle promotion) | Route-level 403 test | P0 when split is implemented |
| ADM can release/retire | Route-level auth test | P0 when split is implemented |
| PMG can create/update MMD if given draft binding | Route-level auth test | P1 |
| Release/retire requires SoD (requester ≠ approver) | Approval integration test | P0 — Phase C |
| RELEASED entity cannot be structurally mutated | Service-level invariant test | Already present in product_service tests |
| Audit event on release/retire | Security event test | P1 — when workflow exists |
| configure.process.manage absent from runtime | `test_rbac_configure_family_boundary.py` | P0 — already locked |

### 6. Verdict

**ALLOW_P0A10B_IEP_MMD_ACTION_BOUNDARY_DECISION**

Option B selected. Evidence is clear. Semantics are defined. No stop condition hit.
No runtime code change required.

---

## Selected Option

**Option B — Define candidate future split, no runtime change.**

Reasons:
1. **Semantics ARE clear enough**: draft create/update and governed release/retire are
   fundamentally different operations with different SoD requirements.
2. **Proposal was REJECTED** — implementation waits for v1.1 slice plan after foundation evidence.
3. **No release/approval workflow** — a split without SoD enforcement would be incomplete.
4. **IEP ADMIN family gap** — IEP cannot use ADMIN codes today; fixing this requires Phase 7+ gate.
5. **CONFIGURE contract scope mismatch** — P0-A-10's CONFIGURE semantics cover process
   parameters/thresholds, NOT routing/BOM structural authoring.

---

## MMD Action Boundary Decision

### Current State (correct for foundation phase)

All MMD mutation routes — create, update, release, retire — are gated by a single ADMIN-family
code per entity group. This is correct for the current foundation:

- No approval workflow exists.
- No SoD gate on release/retire is implemented.
- The current implementation is pre-Phase-C.
- The current codes prevent unauthorized mutation (only ADM/OTS can mutate MMD today).

### Gap

IEP (Industrial Engineering Process role) has `{"VIEW", "CONFIGURE"}` only — no ADMIN family.
IEP cannot currently create, update, release, or retire any MMD entity. This is a known gap
that was identified in the REJECTED proposal and deferred to Phase C (Mutation Enablement).

PMG (Process/Manufacturing Governance) has `{"VIEW", "APPROVE"}` — no ADMIN family.
PMG can participate in approval decisions but cannot directly author MMD definitions today.

### Future Boundary (to implement in Phase C)

When the MMD mutation enablement track resumes (after P0 foundation is solid and approval
workflow is ready), the action split should be:

| Action Type | Operations | Candidate Code Pattern | Family | Who |
|---|---|---|---|---|
| Draft authoring | create, update | `admin.master_data.{entity}.draft_manage` | ADMIN | IEP, PMG (via binding), ADM |
| Lifecycle promotion | release, retire | `admin.master_data.{entity}.lifecycle_manage` | ADMIN | ADM only (with SoD approval gate) |

**Critical pre-condition:** IEP/PMG participation in `draft_manage` requires a Phase 7+ design gate
to either (a) add ADMIN family to IEP/PMG `SYSTEM_ROLE_FAMILIES`, or (b) create a dedicated
sub-family with narrower semantics (see §Future Action Split Decision below).

---

## IEP vs ADM/PMG Responsibility Map

| Role | Family | Current MMD Access | Intended Future MMD Access |
|---|---|---|---|
| IEP | VIEW, CONFIGURE | None (no ADMIN) | draft_manage codes for product/routing/BOM/resource_requirement authoring (Phase C) |
| PMG | VIEW, APPROVE | None (no ADMIN) | draft_manage codes for co-authoring (Phase C); approval.decide for release/retire approval gate |
| ADM | VIEW, ADMIN | Full current access (all *.manage codes) | lifecycle_manage codes for release/retire; draft_manage codes optionally |
| OTS | VIEW, ADMIN | Full current access | Same as ADM in lifecycle dimension |
| QAL | VIEW, APPROVE | None on MMD | approval.decide on quality-governed transitions |
| QCI | VIEW | None on MMD | No change planned |

---

## Current MMD Action Usage Map

| Source / Route | Method | Path | Current Action Code | Operation Type | Lifecycle Impact |
|---|---|---|---|---|---|
| `products.py` | POST | `/products` | `admin.master_data.product.manage` | create DRAFT | None (stays DRAFT) |
| `products.py` | PATCH | `/products/{id}` | `admin.master_data.product.manage` | update DRAFT | None |
| `products.py` | POST | `/products/{id}/release` | `admin.master_data.product.manage` | **lifecycle transition** | DRAFT → RELEASED |
| `products.py` | POST | `/products/{id}/retire` | `admin.master_data.product.manage` | **lifecycle transition** | RELEASED → RETIRED |
| `products.py` | POST | `/products/{id}/versions` | `admin.master_data.product_version.manage` | create DRAFT version | None |
| `products.py` | PATCH | `/products/{id}/versions/{vid}` | `admin.master_data.product_version.manage` | update DRAFT version | None |
| `products.py` | POST | `/products/{id}/versions/{vid}/release` | `admin.master_data.product_version.manage` | **lifecycle transition** | DRAFT → RELEASED |
| `products.py` | POST | `/products/{id}/versions/{vid}/retire` | `admin.master_data.product_version.manage` | **lifecycle transition** | RELEASED → RETIRED |
| `routings.py` | POST | `/routings` | `admin.master_data.routing.manage` | create DRAFT | None |
| `routings.py` | PATCH | `/routings/{id}` | `admin.master_data.routing.manage` | update DRAFT | None |
| `routings.py` | POST | `/routings/{id}/operations` | `admin.master_data.routing.manage` | add operation to DRAFT | None |
| `routings.py` | PATCH | `/routings/{id}/operations/{opid}` | `admin.master_data.routing.manage` | update operation | None |
| `routings.py` | DELETE | `/routings/{id}/operations/{opid}` | `admin.master_data.routing.manage` | remove operation | None |
| `routings.py` | POST | `/routings/{id}/release` | `admin.master_data.routing.manage` | **lifecycle transition** | DRAFT → RELEASED |
| `routings.py` | POST | `/routings/{id}/retire` | `admin.master_data.routing.manage` | **lifecycle transition** | RELEASED → RETIRED |
| `routings.py` | POST | `…/resource-requirements` | `admin.master_data.resource_requirement.manage` | create requirement | None |
| `routings.py` | PATCH | `…/resource-requirements/{rid}` | `admin.master_data.resource_requirement.manage` | update requirement | None |
| `routings.py` | DELETE | `…/resource-requirements/{rid}` | `admin.master_data.resource_requirement.manage` | delete requirement | None |

**Key Finding:** Release/retire operations on products, product versions, and routings are
gated by the SAME action code as create/update. No SoD distinction at the action layer today.

---

## Future Action Split Decision

### Candidate Pattern

When Phase C (Mutation Enablement) is implemented, split current codes as follows:

#### Option B-1 — ADMIN-family split (recommended)

```
admin.master_data.{entity}.draft_manage   → ADMIN → create + update DRAFT entities
admin.master_data.{entity}.lifecycle_manage → ADMIN → release + retire (governed transition)
```

All codes remain ADMIN-family. Role bindings are narrowed at the DB level — IEP/PMG would
receive `draft_manage` bindings, ADM retains both `draft_manage` and `lifecycle_manage`.

**Precondition:** `SYSTEM_ROLE_FAMILIES["IEP"]` must include ADMIN. This requires a Phase 7+
design gate (`SYSTEM_ROLE_FAMILIES` is frozen per Phase 6 governance).

#### Option B-2 — Family split (higher complexity, not recommended now)

```
configure.master_data.{entity}.draft_manage   → CONFIGURE → IEP/PMG draft authoring
admin.master_data.{entity}.lifecycle_manage    → ADMIN → ADM lifecycle promotion
```

This would allow IEP to use CONFIGURE-family codes for draft authoring without touching
`SYSTEM_ROLE_FAMILIES`. However, this extends the CONFIGURE family semantic from
"process parameters/thresholds" (P0-A-10 contract) to "structural manufacturing
definitions" (BOM/routing/product). This is a material semantic extension that requires
a new CONFIGURE contract — **not in scope without explicit governance approval**.

#### Naming Convention (for Option B-1, when implemented)

```text
admin.master_data.product.draft_manage
admin.master_data.product.lifecycle_manage
admin.master_data.product_version.draft_manage
admin.master_data.product_version.lifecycle_manage
admin.master_data.routing.draft_manage
admin.master_data.routing.lifecycle_manage
admin.master_data.resource_requirement.draft_manage
admin.master_data.resource_requirement.lifecycle_manage
```

Existing codes (`admin.master_data.*.manage`) would be deprecated/removed once split
is implemented and all routes are updated.

### Implementation Gate (Phase C preconditions)

Before implementing the split:

1. Approval workflow (`approval_service.py`) is verified to support generic resource type
   for MMD entities (product, routing, BOM, resource_requirement).
2. SoD gate is designed: requester of release/retire ≠ approver.
3. `SYSTEM_ROLE_FAMILIES` change (IEP gets ADMIN) is approved via Phase 7+ gate — OR
   Option B-2 CONFIGURE semantic extension is approved via a separate governance slice.
4. All 4 lifecycle transition routes on products, product_versions, and routings are
   updated atomically.
5. Backward compatibility: existing role bindings using `*.manage` must be migrated.
6. Registry doc and `rbac.py` updated together (atomic governance rule).
7. Regression tests cover both old callers (204-period backward compat) and new boundary.
8. MMD current-state evidence document (`mmd-be-00-evidence-and-contract-lock.md`) exists
   and is current.

---

## Files Inspected

| File | Status |
|---|---|
| `.github/copilot-instructions.md` | Read |
| `.github/agent/AGENT.md` | Read |
| `.github/copilot-instructions-hard-mode-mom-v3-addendum.md` | Read |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | Read |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | Read |
| `docs/audit/p0-a-10a-process-configuration-entity-contract-report.md` | Read |
| `docs/audit/p0-a-10-iep-configuration-contract-definition-report.md` | Read |
| `docs/design/01_foundation/iep-configuration-action-contract.md` | Consulted (P0-A-10 via summary) |
| `docs/design/01_foundation/process-configuration-entity-contract.md` | Consulted (P0-A-10A via summary) |
| `docs/design/02_registry/action-code-registry.md` | Read + updated (small note) |
| `docs/proposals/2026-05-01-master-data-hardening-proposal.md` | Read §A.5, §header, §goals |
| `docs/design/00_platform/domain-boundary-map.md` | Read |
| `docs/design/00_platform/authorization-model-overview.md` | Read |
| `docs/design/01_foundation/role-model-and-scope-resolution.md` | Read |
| `backend/app/security/rbac.py` | Read — full ACTION_CODE_REGISTRY + SYSTEM_ROLE_FAMILIES |
| `backend/app/security/dependencies.py` | Consulted |
| `backend/app/api/v1/products.py` | Read — all route guards |
| `backend/app/api/v1/routings.py` | Read — all route guards |
| `backend/app/api/v1/reason_codes.py` | Read — read-only, no action guard |
| `backend/tests/test_rbac_action_registry_alignment.py` | Read |
| `backend/tests/test_mmd_rbac_action_codes.py` | Read — full |

---

## Files Changed

| File | Change |
|---|---|
| `docs/audit/p0-a-10b-iep-mmd-action-boundary-decision-report.md` | **Created** — this report |
| `docs/design/02_registry/action-code-registry.md` | **Updated** — small coarse-grain note in MMD section + history row |

No runtime source files were changed. No tests were changed.

---

## Verification Commands Run

```powershell
cd g:\Work\FleziBCG
git status --short

cd g:\Work\FleziBCG\backend
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_mmd_rbac_action_codes.py
```

---

## Results

```
58 passed, 1 warning in 2.84s
```

- `test_rbac_action_registry_alignment.py` — 20 tests passed
- `test_rbac_seed_alignment.py` — 20 tests passed
- `test_mmd_rbac_action_codes.py` — 18 tests passed

No regressions. Design-only changes only.

---

## Existing Gaps / Known Debts

| Gap | Severity | Owner | Phase |
|---|---|---|---|
| IEP has no ADMIN family → cannot create/update any MMD entity | High | Phase 7+ design gate | Phase C |
| PMG has no ADMIN family → cannot create/update any MMD entity | High | Phase 7+ design gate | Phase C |
| `admin.master_data.*.manage` covers both draft and lifecycle — no SoD separation | Medium | Phase C MMD split slice | Phase C |
| No approval workflow gate on release/retire | High | Approval integration | Phase C |
| Proposal v1.1 not yet authored | Medium | PO/SA | After P0 foundation |
| `mmd-be-00-evidence-and-contract-lock.md` may not exist | Medium | MMD track lead | Pre-Phase-A |
| `admin.master_data.*.manage` codes have no per-operation granularity | Medium | Phase C split | Phase C |

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
| Decision is evidence-based | ✅ |

---

## Risks

| Risk | Status |
|---|---|
| IEP cannot author MMD definitions today | Known gap — documented; no immediate operational risk (ADM can create all MMD) |
| PMG cannot co-author MMD definitions today | Known gap — same |
| Phase C split implementation touches frozen `SYSTEM_ROLE_FAMILIES` | Must use Phase 7+ gate; documented as precondition |
| Option B-2 (CONFIGURE-family extension) semantic drift | Risk mitigated — explicitly listed as "not recommended without governance approval" |
| Split without SoD approval workflow would be incomplete | Documented in Phase C preconditions (item 2) |
| Existing `*.manage` bindings in DB must be migrated when split is done | Documented in Phase C preconditions (item 5) |

---

## Recommended Next Slice

### Immediate: MMD-BE-00 Evidence and Contract Lock

If `docs/audit/mmd-be-00-evidence-and-contract-lock.md` does not exist, create it before
any Phase A implementation begins. This document should verify current source state for
all 4 MMD sub-domains and produce the "contract lock" that the REJECTED proposal's review
required.

### Near term: MMD proposal v1.1 authoring

Re-author `docs/proposals/2026-05-01-master-data-hardening-proposal.md` as v1.1 after the
P0 foundation audit is complete. v1.1 must address:
- Logical consistency: approval workflow gate on Phase A or Phase C?
- Foundation dependency P0-A verified.
- Reason Code unification risk to downtime path.
- IEP/PMG family gap decision.

### Phase C: MMD action split implementation

When Phase C begins, trigger:
1. Phase 7+ design gate for `SYSTEM_ROLE_FAMILIES["IEP"]` + `["PMG"]` changes.
2. `admin.master_data.{entity}.draft_manage` + `lifecycle_manage` split.
3. Approval workflow integration for release/retire.
4. SoD enforcement.
5. Route guard update across products.py + routings.py.

---

## Stop Conditions Hit

None. Verdict was `ALLOW_P0A10B_IEP_MMD_ACTION_BOUNDARY_DECISION`.
Option B selected cleanly. No authority conflict. No product scope invented.
No runtime code changed.

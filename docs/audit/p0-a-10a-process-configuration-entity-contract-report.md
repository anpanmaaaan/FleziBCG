# P0-A-10A Process Configuration Entity Contract Report

**Slice:** P0-A-10A  
**Date:** 2026-05-03  
**Status:** COMPLETE  
**Decision Type:** Design contract — entity scope decision (Option B: defer)

---

## Summary

P0-A-10A defines whether concrete process configuration entities can be named and designed
for the reserved `configure.process.manage` action code established in P0-A-10.

**Option B** is selected: entity contract is deferred.

Evidence shows process parameter entities are explicitly a Phase 11 (P2-A) item per the
roadmap, and the domain boundary map assigns "procedure/phase-ready definitions" to the MMD
domain — creating entity names now would invent product scope the roadmap has not authorized.

- `docs/design/01_foundation/process-configuration-entity-contract.md` — Created (17 sections)
- `docs/design/02_registry/action-code-registry.md` — Updated (entity contract reference + history row)
- `configure.process.manage` remains reserved — runtime registry unchanged
- All 46 RBAC boundary/alignment tests pass

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Architecture + Strict (design-first contract, no runtime code)
- **Hard Mode MOM:** v3
- **Reason:** Touches future CONFIGURE-family action semantics, IEP role/action boundary, future DB/API governance contract, and critical boundary between process configuration and MMD/Execution/Quality domains.

---

## Hard Mode MOM v3 Gate

### Verdict

**ALLOW_P0A10A_PROCESS_CONFIGURATION_ENTITY_CONTRACT**

Option B selected — entity design deferred. Evidence is clear. No stop condition hit.

### Key Evidence Items

| Finding | Source | Decision Impact |
|---|---|---|
| Process parameter is Phase 11 (P2-A) | `flezibcg-overall-roadmap-latest.md` | Cannot name entities in P0 |
| MMD owns "procedure/phase-ready definitions" | `domain-boundary-map.md` | Work instruction overlap risk |
| IEP current concrete actions are ADMIN-family | `master-data-hardening-proposal.md` L196 | IEP's actual current scope = ADMIN create/update on MMD |
| No backend process config model exists | Full source scan | No anchor for entity names |
| 7 open questions unresolved | `iep-configuration-action-contract.md` §14 | Preconditions not met |

### Invariants Confirmed

| Invariant | Status |
|---|---|
| Zero CONFIGURE action codes in runtime | ✅ Confirmed by boundary tests |
| `configure.process.manage` remains reserved | ✅ Not added to `ACTION_CODE_REGISTRY` |
| No runtime code changed | ✅ |
| No entity/schema added | ✅ |
| No migration added | ✅ |

---

## Selected Option

**Option B — Defer entity contract.**

Reasons:

1. **Phase 11 gate**: Process parameters are `flezibcg-overall-roadmap-latest.md` Phase 11 (P2-A) items — explicitly deferred.
2. **MMD boundary overlap**: `domain-boundary-map.md` places "recipe/formula/procedure/phase-ready definitions" in MMD domain, overlapping candidate process configuration entities.
3. **No existing backend source**: No process configuration model, table, service, or route exists.
4. **IEP concrete actions are ADMIN-family**: Per `master-data-hardening-proposal.md`, IEP operates on MMD entities via ADMIN-family actions (create/update on routing, BOM, resource requirement) — not through a separate CONFIGURE entity.
5. **7 open questions unresolved**: Entity design, SoD, scope level, approval loop, and domain boundary all require Phase 11 design authority.

---

## Process Configuration Contract Decision

| Field | Value |
|---|---|
| Entity model | NOT defined — deferred to Phase 11 |
| Action code runtime status | Reserved — `configure.process.manage` not in `ACTION_CODE_REGISTRY` |
| Phase gate | Phase 11 (P2-A) — process/batch/ISA-88 depth |
| Phase 11 trigger | Customer is food/pharma/chemical/batch/process-heavy/regulated |
| Contract authority | `docs/design/01_foundation/process-configuration-entity-contract.md` |
| Entity design preconditions | §14 of entity contract (9 preconditions) |
| Open questions | 7 open questions in entity contract §16 |

---

## Files Inspected

| File | Status |
|---|---|
| `.github/agent/AGENT.md` | Read |
| `.github/copilot-instructions-hard-mode-mom-v3-addendum.md` | Read |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | Read |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | Read |
| `docs/audit/p0-a-10-iep-configuration-contract-definition-report.md` | Read |
| `docs/design/01_foundation/iep-configuration-action-contract.md` | Read (full) |
| `docs/design/00_platform/domain-boundary-map.md` | Read — MMD boundary evidence |
| `docs/design/00_platform/product-scope-and-phase-boundary.md` | Read |
| `docs/design/00_platform/product-business-truth-overview.md` | Read |
| `docs/design/00_platform/master-data-strategy.md` | Read |
| `docs/design/00_platform/system-overview-and-target-state.md` | Read |
| `docs/design/00_platform/authorization-model-overview.md` | Read |
| `docs/design/01_foundation/role-model-and-scope-resolution.md` | Read |
| `docs/design/02_registry/action-code-registry.md` | Read + Updated |
| `docs/governance/ENGINEERING_DECISIONS.md` | Read |
| `docs/governance/CODING_RULES.md` | Read |
| `docs/roadmap/flezibcg-overall-roadmap-latest.md` Phase 11 | Read — Phase 11 explicit |
| `docs/proposals/2026-05-01-master-data-hardening-proposal.md` L196 | Read — IEP ADMIN-family actions |
| `docs/system/mes-business-logic-v1.md` L483 | Read — CONFIGURE semantics |
| `backend/app/security/rbac.py` | Scanned — no process config entities |
| `backend/app/security/dependencies.py` | Read — `_AUDITED_FAMILIES` |

---

## Files Changed

| File | Change |
|---|---|
| `docs/design/01_foundation/process-configuration-entity-contract.md` | **Created** — 17-section entity contract (Option B decision) |
| `docs/design/02_registry/action-code-registry.md` | **Updated** — entity contract reference + P0-A-10A history row |
| `docs/audit/p0-a-10a-process-configuration-entity-contract-report.md` | **Created** — this report |

No runtime source files were changed.

---

## Verification Commands Run

```
cd g:\Work\FleziBCG
git status --short

cd g:\Work\FleziBCG\backend
python -m pytest -q tests/test_rbac_configure_family_boundary.py tests/test_rbac_seed_alignment.py tests/test_rbac_action_registry_alignment.py
```

---

## Results

```
46 passed, 1 warning in 3.42s
```

- `test_rbac_configure_family_boundary.py` → **6 passed** — zero CONFIGURE codes confirmed
- `test_rbac_seed_alignment.py` → **20 passed**
- `test_rbac_action_registry_alignment.py` → **20 passed**

No regressions. Design-only changes only.

---

## Existing Gaps / Known Debts

| Item | Status |
|---|---|
| `configure.process.manage` entity model undefined | Deferred to Phase 11 (P2-A) |
| Open questions Q1–Q7 in entity contract | Blocked on Phase 11 design gate |
| IEP ADMIN-family create/update actions | IEP may need ADMIN-family codes for routing/BOM create/update per `master-data-hardening-proposal.md` — separate slice needed |
| Work instruction boundary (MMD vs IEP CONFIGURE) | Requires explicit domain boundary decision in Phase 11 |

---

## Scope Compliance

| Constraint | Compliant? |
|---|---|
| No `configure.process.manage` added to runtime | ✅ |
| No `ACTION_CODE_REGISTRY` change | ✅ |
| No `SYSTEM_ROLE_FAMILIES` change | ✅ |
| No `seed_rbac_core` change | ✅ |
| No route guard change | ✅ |
| No migration added | ✅ |
| No entity/model schema added | ✅ |
| No frontend/Admin UI/API added | ✅ |
| No product scope invented | ✅ — Option B explicitly defers entity names |
| Naming convention consistent | ✅ — `configure.process.manage` confirmed per registry convention |

---

## Risks

| Risk | Status |
|---|---|
| Inventing Phase 11 entity scope | Mitigated — Option B defers; no entity names defined |
| MMD/process config boundary confusion | Mitigated — domain boundary map explicitly cited; boundary decision documented in contract §7 |
| IEP ADMIN-family action gap (create/update on MMD) | Identified as separate debt — not in scope of this slice |
| Future over-granting IEP CONFIGURE | `SYSTEM_ROLE_FAMILIES` frozen per Phase 6 governance invariant |

---

## Recommended Next Slice

### Near term: IEP MMD action alignment

`docs/proposals/2026-05-01-master-data-hardening-proposal.md` shows IEP/PMG should have
create/update actions on routing, BOM, resource requirement — currently all gated by single
`admin.master_data.*.manage` codes. A separate slice may be needed to split these codes or
define whether IEP gets the full `admin.master_data.*` code or a narrower one.

This is an **ADMIN-family** concern (not CONFIGURE) and should be a separate P0-A slice.

### Phase 11 trigger

`configure.process.manage` entity design should proceed when:
- A customer requires process parameter management (food/pharma/chemical/batch)
- Phase 11 design gate is initiated
- All 9 preconditions in entity contract §14 are satisfied

---

## Stop Conditions Hit

None. Verdict was `ALLOW_P0A10A_PROCESS_CONFIGURATION_ENTITY_CONTRACT`.
Option B selected cleanly — no conflict, no invented scope.

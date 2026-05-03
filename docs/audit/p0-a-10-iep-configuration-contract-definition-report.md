# P0-A-10 IEP Configuration Contract Definition Report

**Slice:** P0-A-10  
**Date:** 2026-05-03  
**Status:** COMPLETE  
**Decision Type:** Design contract definition (no runtime behavior change)

---

## Summary

P0-A-10 defines the design authority for future IEP CONFIGURE-family action(s).

- A canonical contract document now exists at
  `docs/design/01_foundation/iep-configuration-action-contract.md`.
- **Option A** is selected: a CONFIGURE-family action code is needed in a future slice.
- The reserved future action code is **`configure.process.manage`** (CONFIGURE family, IEP only).
- A short reserved-posture note was added to `docs/design/02_registry/action-code-registry.md`.
- No runtime code was changed.
- No action code was added to `ACTION_CODE_REGISTRY`.
- No route guard was changed.
- No migration was added.
- All 46 RBAC boundary/alignment tests still pass.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Architecture + Strict (design-first authorization contract, no-runtime-code)
- **Hard Mode MOM:** v3
- **Reason:** Task touches future CONFIGURE-family action semantics, IEP role/action boundary, system role permission seeding implications, authorization registry governance, and future admin/governance API readiness.

---

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Source | Evidence |
|---|---|
| `backend/app/security/rbac.py` | `"IEP": {"VIEW", "CONFIGURE"}` — IEP is the sole CONFIGURE-family role |
| `backend/app/security/rbac.py` — aliases | `"IE": "IEP"`, `"PROCESS": "IEP"` |
| `backend/app/security/dependencies.py` | `_AUDITED_FAMILIES` includes `CONFIGURE` |
| `docs/system/mes-business-logic-v1.md` L167 | `IEP (IE / Process) — Configure; process improvement focus` |
| `docs/system/mes-business-logic-v1.md` L483 | `CONFIGURE | IEP | Modify parameters (standards, thresholds, process definitions)` |
| `docs/design/00_platform/product-business-truth-overview.md` L463 | `IEP: engineering / process / operational improvement actor` |
| `docs/design/00_platform/master-data-strategy.md` L20 | `manufacturing mode and process configuration` as master-data family |
| `docs/design/02_registry/action-code-registry.md` | No CONFIGURE entries — reserved-family posture confirmed |
| P0-A-09 report | Zero CONFIGURE codes, no route usage, boundary tests locked |

### Verdict

**ALLOW_P0A10_IEP_CONFIGURATION_CONTRACT_DEFINITION**

Design authority exists. CONFIGURE family has explicit semantics in `mes-business-logic-v1.md`. 
IEP role has explicit CONFIGURE assignment. Naming convention is resolvable. 
No runtime code change is required in this slice.

---

## Selected Option

**Option A — CONFIGURE action is needed in a future implementation slice.**

Evidence supports: IEP is "Configure; process improvement focus"; CONFIGURE means "Modify parameters (standards, thresholds, process definitions)". The role alias `PROCESS → IEP` reinforces this scope.

No runtime code was added. The future action code `configure.process.manage` is reserved and named in the contract only.

---

## IEP CONFIGURE Contract Decision

| Field | Value |
|---|---|
| Reserved future action code | `configure.process.manage` |
| Family | `CONFIGURE` |
| Authorized role | IEP (sole CONFIGURE-family role) |
| Gate semantics | Modify process parameters, standards, thresholds, process definitions |
| Naming rationale | `configure.*` prefix for CONFIGURE family; `process` sub-domain per design sources; `manage` verb per registry convention |
| Runtime status | NOT added to `ACTION_CODE_REGISTRY` in P0-A-10 |
| Authority document | `docs/design/01_foundation/iep-configuration-action-contract.md` |

### Explicitly Out of Scope for IEP CONFIGURE

- Routing/BOM/Product/Product Version/Resource Requirement lifecycle (ADMIN codes)
- Downtime reason master data (ADMIN code)
- IAM/impersonation management (ADMIN codes)
- Quality hold / approval decisions (APPROVE lane)
- Execution state mutations (EXECUTE lane)
- Security/audit event access (ADMIN code)

---

## Files Inspected

| File | Status |
|---|---|
| `.github/agent/AGENT.md` | Read |
| `.github/copilot-instructions-hard-mode-mom-v3-addendum.md` | Read |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | Read |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | Read |
| `docs/audit/p0-a-09-iep-configure-family-gap-decision-report.md` | Read |
| `docs/design/00_platform/authorization-model-overview.md` | Read |
| `docs/design/00_platform/product-business-truth-overview.md` | Read (IEP role definition at L463) |
| `docs/design/00_platform/product-scope-and-phase-boundary.md` | Read |
| `docs/design/00_platform/master-data-strategy.md` | Read |
| `docs/design/01_foundation/role-model-and-scope-resolution.md` | Read |
| `docs/design/01_foundation/identity-access-session-governance.md` | Read |
| `docs/design/02_registry/action-code-registry.md` | Read + Updated |
| `docs/system/mes-business-logic-v1.md` | Read (CONFIGURE semantics at L167, L483) |
| `backend/app/security/rbac.py` | Read (SYSTEM_ROLE_FAMILIES, ACTION_CODE_REGISTRY, aliases) |
| `backend/app/security/dependencies.py` | Read (_AUDITED_FAMILIES) |
| `backend/tests/test_rbac_configure_family_boundary.py` | Read (P0-A-09 lock confirmed) |
| `backend/tests/test_rbac_seed_alignment.py` | Referenced (tests run) |
| `backend/tests/test_rbac_action_registry_alignment.py` | Referenced (tests run) |

---

## Files Changed

| File | Change |
|---|---|
| `docs/design/01_foundation/iep-configuration-action-contract.md` | **Created** — IEP CONFIGURE-family action contract (15 sections) |
| `docs/design/02_registry/action-code-registry.md` | **Updated** — Added "Reserved — CONFIGURE Family" section with reserved posture note and future code name |
| `docs/audit/p0-a-10-iep-configuration-contract-definition-report.md` | **Created** — This report |

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
46 passed, 1 warning in 4.47s
```

- `test_rbac_configure_family_boundary.py` → **6 passed** (P0-A-09 boundary lock still holds)
- `test_rbac_seed_alignment.py` → **20 passed**
- `test_rbac_action_registry_alignment.py` → **20 passed**
- Zero CONFIGURE action codes confirmed by boundary test

No regressions.

---

## Existing Gaps / Known Debts

| Item | Status |
|---|---|
| Zero CONFIGURE action codes in runtime | Intentional reserved posture; unlocked by this contract |
| `configure.process.manage` not yet in `ACTION_CODE_REGISTRY` | Deferred to future implementation slice (see §12 of contract) |
| Process configuration entities/schema not designed | Future design slice |
| SoD/approval requirement for process config changes not decided | Open question Q2 in contract |
| Equipment-level configuration scope for IEP unclear | Open question Q4 in contract |
| Scope level for `configure.process.manage` not defined | Open question Q5 in contract |

---

## Scope Compliance

| Constraint | Compliant? |
|---|---|
| No runtime action code added | ✅ |
| No `ACTION_CODE_REGISTRY` change | ✅ |
| No `SYSTEM_ROLE_FAMILIES` change | ✅ |
| No `seed_rbac_core` change | ✅ |
| No route guard change | ✅ |
| No migration added | ✅ |
| No frontend/Admin UI/API added | ✅ |
| No product scope invented | ✅ — all evidence is from existing design docs |
| Naming convention consistent | ✅ — `configure.process.manage` follows `<top_domain>.<sub_domain>.<verb>` |

---

## Risks

| Risk | Status |
|---|---|
| Inventing IEP scope | Mitigated — all scoping grounded in `mes-business-logic-v1.md` and `product-business-truth-overview.md` |
| Overlap with MMD ADMIN codes | Explicitly excluded in §6 of contract |
| Overlap with Execution | IEP has no EXECUTE; structural exclusion |
| Action naming inconsistency | `configure.*` prefix enforced; `admin.*` is ADMIN-family-only |
| Future over-granting | `SYSTEM_ROLE_FAMILIES` frozen per Phase 6 governance invariant |

---

## Recommended Next Slice

**P0-A-11 (or future design slice):** Process Configuration Entity Design

Prerequisites before runtime adoption of `configure.process.manage`:

1. Define which entities/tables are "process parameters / standards / thresholds / process definitions" in the FleziBCG schema.
2. Design route/API for IEP to modify these entities.
3. Determine SoD/approval requirement (open question Q2).
4. Create migration for process configuration entities.
5. Then: add `configure.process.manage` to `ACTION_CODE_REGISTRY`, add route guard, add seed + registry + route tests.

---

## Stop Conditions Hit

None. Verdict was `ALLOW_P0A10_IEP_CONFIGURATION_CONTRACT_DEFINITION`.

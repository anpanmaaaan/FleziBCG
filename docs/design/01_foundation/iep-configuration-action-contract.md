# IEP Configuration Action Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Defined IEP CONFIGURE-family action boundary and future runtime adoption conditions. |

**Status:** Active — design contract only. No runtime action code added.

---

## 1. Purpose

This document defines the design authority for future IEP CONFIGURE-family action(s).

P0-A-09 locked the current posture:

- `IEP` has `{"VIEW", "CONFIGURE"}` in `SYSTEM_ROLE_FAMILIES`.
- `ACTION_CODE_REGISTRY` has zero CONFIGURE-family action codes.
- No current API route uses a CONFIGURE action guard.

This contract creates the missing naming authority and scope definition so that a future
implementation slice can safely add a CONFIGURE action code without inventing product scope.

---

## 2. Source Evidence

| Source | Evidence |
|---|---|
| `backend/app/security/rbac.py` | `PermissionFamily = Literal[..., "CONFIGURE", ...]`; `"IEP": {"VIEW", "CONFIGURE"}` |
| `backend/app/security/rbac.py` — aliases | `"IE": "IEP"`, `"PROCESS": "IEP"` — role stands for Industrial Engineering / Process |
| `backend/app/security/dependencies.py` | `_AUDITED_FAMILIES = frozenset({"EXECUTE", "APPROVE", "CONFIGURE"})` — CONFIGURE is designed to be audit-logged under impersonation |
| `docs/system/mes-business-logic-v1.md` L167 | `IEP (IE / Process) — Configure; process improvement focus` |
| `docs/system/mes-business-logic-v1.md` L483 | `CONFIGURE \| IEP \| Modify parameters (standards, thresholds, process definitions)` |
| `docs/design/00_platform/product-business-truth-overview.md` L463 | `IEP: engineering / process / operational improvement actor` |
| `docs/design/00_platform/master-data-strategy.md` L20 | `manufacturing mode and process configuration` listed as master-data family |
| `docs/design/02_registry/action-code-registry.md` | No CONFIGURE entries in registry |
| P0-A-09 report | Boundary locked with 6 tests; zero CONFIGURE codes; no route usage |

---

## 3. IEP Role Definition

IEP is the **Industrial Engineering / Process** role.

- Primary non-VIEW capability: **CONFIGURE**
- Broad intent: engineering/process/operational improvement actor
- Role aliases recognized: `IE`, `PROCESS`
- SoD position: IEP does **not** have EXECUTE (cannot start/complete operations)
- SoD position: IEP does **not** have ADMIN (cannot manage users, IAM, or MMD lifecycle releases)
- SoD position: IEP does **not** have APPROVE (cannot approve/reject governed decisions)

IEP occupies the engineering configuration lane:

```
OPR/SUP  → EXECUTE lane (shopfloor execution)
QAL/PMG  → APPROVE lane (governed decisions)
ADM/OTS  → ADMIN lane (platform administration)
IEP      → CONFIGURE lane (process/engineering parameters)
```

---

## 4. CONFIGURE Family Semantics

CONFIGURE permission family means:

> **Modify parameters — standards, thresholds, process definitions.**

(Source: `docs/system/mes-business-logic-v1.md` §7.1)

CONFIGURE is explicitly **different** from:

| Family | Difference from CONFIGURE |
|---|---|
| `ADMIN` | ADMIN owns platform administration, IAM, and master-data lifecycle governance (create/release/retire) |
| `EXECUTE` | EXECUTE is shopfloor execution state transitions |
| `APPROVE` | APPROVE is governed sign-off with SoD |
| `VIEW` | VIEW is read-only access with no mutation permitted |

CONFIGURE actions should be audited when executed under impersonation (already included in `_AUDITED_FAMILIES`).

---

## 5. In Scope

IEP CONFIGURE scope is limited to:

- **Process parameter configuration**: modifying process standards, cycle time targets, thresholds
- **Process definition management**: defining or updating work instructions, process instructions, or process parameter definitions at the engineering level
- **Engineering improvement operations**: actions that support process improvement (IEP's stated focus)

These are parameters and definitions that:
- are authored by engineering/IE roles
- affect how production operations are expected to run
- are not manufacturing master-data lifecycle events (no release/retire governance)
- are not execution-state mutations
- are not quality sign-offs or approval decisions

---

## 6. Explicitly Out of Scope

IEP CONFIGURE must **never** be used for:

| Domain | Reason |
|---|---|
| Routing / BOM master data lifecycle (create, release, retire) | Already covered by `admin.master_data.routing.manage` (ADMIN family) |
| Product / Product Version lifecycle | Already covered by `admin.master_data.product*.manage` (ADMIN family) |
| Resource requirement lifecycle | Already covered by `admin.master_data.resource_requirement.manage` (ADMIN family) |
| Downtime reason master data | Already covered by `admin.downtime_reason.manage` (ADMIN family) |
| IAM user management | ADMIN lane — `admin.user.manage` |
| Impersonation management | ADMIN lane — `admin.impersonation.*` |
| Quality hold / QC approval | APPROVE lane — QAL/PMG |
| Execution state changes | EXECUTE lane — OPR/SUP |
| Station execution session control | EXECUTE lane |
| Security/audit event access | ADMIN lane — `admin.security_event.read` |
| Scheduling/dispatch decisions | PLN has VIEW only; no configure scope for PLN |

---

## 7. Future Action Code Decision

### Decision: Option A — One action code is needed in a future implementation slice.

**Proposed future action code:**

```
configure.process.manage
```

| Field | Value |
|---|---|
| Code | `configure.process.manage` |
| Family | `CONFIGURE` |
| Description | Modify process parameters, standards, thresholds, and process definitions |
| Authorized role | IEP |
| Naming rationale | Top domain = `configure` (matches CONFIGURE family, not `admin`); sub domain = `process` (process engineering scope); verb = `manage` (aligned with registry convention) |

### Naming rationale in detail

Registry naming convention: `<top_domain>.<sub_domain>[.<entity>].<verb>`

- `configure` as top domain: All CONFIGURE-family codes should use `configure.*` prefix (not `admin.*`, which maps exclusively to ADMIN family).
- `process` as sub domain: "Process definitions", "process improvement focus", "process/operational improvement actor" — all design sources use "process" to describe IEP's engineering scope.
- `manage` as verb: Consistent with other mutation verbs in the registry (`*.manage`).

### What this action code gates (future)

When a route requires `configure.process.manage`, it means:

- The caller must be an authenticated user with IEP role (or impersonating IEP under ADM/OTS).
- The mutation touches process parameters, standards, thresholds, or process definitions.
- The action is audit-logged if executed under impersonation (by existing `_AUDITED_FAMILIES` rule).

### Sub-domain scope to resolve before runtime adoption

Before `configure.process.manage` is added to `ACTION_CODE_REGISTRY`, the following must be specified in a dedicated design slice:

1. Which specific entities/endpoints this code guards (e.g., work instruction records, process parameter tables, standard time records).
2. Whether one broad `configure.process.manage` code is sufficient or whether multiple narrow CONFIGURE codes are needed.
3. Whether any SoD rule applies (e.g., IEP cannot approve their own process definition change).
4. Schema and migration plan for the process configuration entities.

---

## 8. Future Route Guard Contract

When a route implementing IEP process configuration is added:

```python
# Example — not yet implemented
@router.post("/process-parameters/{id}", ...)
async def update_process_parameter(
    ...,
    identity: RequestIdentity = Depends(require_action("configure.process.manage")),
):
    ...
```

- The guard must use `require_action("configure.process.manage")`, not `require_permission(PermissionFamily.CONFIGURE)`.
- `require_action` performs both family check (CONFIGURE) and action-level DB check.
- READ endpoints for the same domain must use `require_authenticated_identity` (no action code — VIEW family is not action-gated).

---

## 9. Seed / RolePermission Implication

When `configure.process.manage` is added to `ACTION_CODE_REGISTRY`:

- `seed_rbac_core()` will automatically create a `Permission` row with `action_code="configure.process.manage"` and `family="CONFIGURE"`.
- `seed_rbac_core()` will automatically create a `RolePermission` row linking the IEP role to this permission (because `SYSTEM_ROLE_FAMILIES["IEP"]` includes `CONFIGURE`).
- No manual seed logic is required. The dynamic loop in `seed_rbac_core()` handles all registered action codes automatically.

No seed code change is needed in this slice or the future implementation slice.

---

## 10. Audit / Security Event Expectations

- CONFIGURE actions performed under impersonation must be logged by `_AUDITED_FAMILIES` (already includes CONFIGURE).
- Direct IEP-user CONFIGURE actions are not currently auto-audited at the action level (consistent with current execution EXECUTE actions — impersonation path is audited, direct action is not separately logged unless explicitly added).
- Future: If process configuration changes require a mandatory audit trail regardless of impersonation, a dedicated security event may be added — this is not required now.

---

## 11. SoD / Authorization Boundary

| Constraint | Rule |
|---|---|
| IEP cannot execute operations | `SYSTEM_ROLE_FAMILIES["IEP"]` does not include `EXECUTE` |
| IEP cannot approve governed decisions | `SYSTEM_ROLE_FAMILIES["IEP"]` does not include `APPROVE` |
| IEP cannot manage users or IAM | `SYSTEM_ROLE_FAMILIES["IEP"]` does not include `ADMIN` |
| IEP cannot release/retire MMD | ADMIN-family codes gate MMD lifecycle; IEP has no ADMIN |
| ADM/OTS impersonating IEP is audited | `_AUDITED_FAMILIES` includes CONFIGURE |
| IEP cannot impersonate | IEP is not in impersonation-allowed roles |
| SoD for process config approval | To be defined in future slice if process definitions require approval before activation |

---

## 12. Implementation Preconditions

Before `configure.process.manage` may be added to `ACTION_CODE_REGISTRY`, all of the following must be met:

1. **Process configuration API design**: At least one route exists or is ready to be added that requires this action guard.
2. **Schema design**: The entity/table being configured exists in DB schema (migration ready).
3. **Scope definition**: The exact sub-entity scope of `configure.process.manage` is documented (not invented here).
4. **SoD review**: Whether process parameter changes require approval (IEP as requester, PMG/QAL as approver) is evaluated.
5. **This contract is reviewed**: No amendment to this contract's Out of Scope section is needed.
6. **P0-A-09 boundary tests still pass**: `test_rbac_configure_family_boundary.py` must still confirm 0 CONFIGURE codes before the new code is added (the test will then be updated).

---

## 13. Tests Required Before Runtime Adoption

| Test | Purpose |
|---|---|
| `test_rbac_action_registry_alignment.py` — add `configure.process.manage` | Lock the new code in the canonical set |
| `test_rbac_seed_alignment.py` — add CONFIGURE code assertion | Verify seed creates Permission + RolePermission for IEP |
| New route-level guard test | Verify `configure.process.manage` guard returns 403 for non-IEP roles |
| SoD test if approval needed | Verify IEP cannot approve their own process config change |
| Update `test_rbac_configure_family_boundary.py` | Remove the "zero CONFIGURE codes" assertion and replace with exact count |

---

## 14. Open Questions

| # | Question | Owner |
|---|---|---|
| Q1 | Is one `configure.process.manage` code sufficient, or are multiple narrower codes needed (e.g., `configure.standard_time.manage`, `configure.work_instruction.manage`)? | Future design slice |
| Q2 | Does process parameter configuration require an approval loop (SoD)? | Future design slice |
| Q3 | What is the exact schema for process configuration entities? | Future DB design slice |
| Q4 | Does equipment-level configuration belong to IEP CONFIGURE or a separate ADMIN code? | Future design slice |
| Q5 | What scope level does `configure.process.manage` operate at — tenant, plant, line, or station? | Future scope design slice |

---

## 15. Final Decision

**Option A — CONFIGURE action is needed in a future implementation slice.**

Design authority exists for the CONFIGURE family assigned to IEP.
The future action code `configure.process.manage` is reserved and named.
No runtime code is added in this slice (P0-A-10).

Implementation may proceed when the preconditions in §12 are satisfied.

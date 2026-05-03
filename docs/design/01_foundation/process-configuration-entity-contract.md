# Process Configuration Entity Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Defined process configuration entity boundary for future IEP CONFIGURE runtime adoption. Option B selected: entity contract deferred — Phase 11 (P2-A) gate. |

**Status:** Active — decision record only. No entities designed. No runtime code added.

---

## 1. Purpose

This document defines whether concrete entity model and API scope can be assigned to the
reserved future action code `configure.process.manage` (established in P0-A-10).

P0-A-10 reserved the action code name and proved design authority exists.
This slice (P0-A-10A) answers: **What exact entities does `configure.process.manage` gate?**

After this contract:

- The entity scope decision is documented with evidence.
- Candidate entities are evaluated against domain boundaries and roadmap phase gates.
- The conditions required to unlock entity design are explicit.
- No runtime code is changed.
- No entities are added to the schema.
- No migration is created.
- `configure.process.manage` remains reserved in `docs/design/02_registry/action-code-registry.md`.

---

## 2. Source Evidence

| Source | Evidence |
|---|---|
| `docs/roadmap/flezibcg-overall-roadmap-latest.md` Phase 11 (P2-A) | `Process parameter: temperature/pressure/pH/speed` is explicitly a Phase 11 item |
| `docs/design/00_platform/domain-boundary-map.md` | MMD domain owns `recipe / formula / procedure / phase-ready definitions` and `versioned manufacturing definitions` |
| `docs/system/mes-business-logic-v1.md` L483 | `CONFIGURE \| IEP \| Modify parameters (standards, thresholds, process definitions)` — conceptually clear, no entity model |
| `docs/design/01_foundation/iep-configuration-action-contract.md` §12 | Open questions Q1–Q5 remain unresolved; entity schema named as precondition |
| `docs/proposals/2026-05-01-master-data-hardening-proposal.md` L196 | IEP/PMG get create/update on routing, BOM, resource requirement via ADMIN-family action codes |
| `docs/design/00_platform/product-scope-and-phase-boundary.md` | P0 scope = Station Execution as discrete-first app; IEP process configuration not in current phase |
| `docs/design/00_platform/master-data-strategy.md` | `manufacturing mode and process configuration` listed as master-data family intent — no entity design exists |
| `backend/app/` (full source scan) | No process configuration model, table, service, route, or schema exists |

---

## 3. Relationship to IEP CONFIGURE Contract (P0-A-10)

`docs/design/01_foundation/iep-configuration-action-contract.md` (P0-A-10) established:

1. IEP is the sole CONFIGURE-family role.
2. CONFIGURE family semantics = "Modify parameters (standards, thresholds, process definitions)".
3. Reserved future action code = `configure.process.manage`.
4. Implementation preconditions (§12) include: entity/table design must exist before runtime adoption.

This document (P0-A-10A) attempts to fulfill precondition 4 — and concludes that entity design
cannot safely proceed yet (see §17 Final Decision).

---

## 4. Definition of Process Configuration

Based on all available design evidence:

> **Process configuration** is the engineering-managed layer of manufacturing parameters,
> standards, and definitions that govern **how** production operations should be performed.

This is distinct from:

- **Manufacturing Master Data** (MMD): what operations exist and in what structure (routing, BOM, product version).
- **Execution**: runtime state transitions (start/complete/report) driven by OPR/SUP.
- **Quality**: measurement, evaluation, hold/disposition driven by QAL.
- **Planning**: scheduling proposals driven by PLN.

Process configuration lives **between** MMD definition and execution runtime:

```
MMD (ADM lane)            → defines structure (routing, product, BOM)
Process Configuration     → defines target parameters for running that structure
Execution (OPR/SUP lane)  → executes against those parameters at runtime
```

In a mature MOM platform, typical process configuration entities include:

- Standard cycle time targets per operation/product
- Process parameter specifications (temperature, pressure, speed ranges)
- Work instruction / process instruction documents linked to operations
- Quality threshold targets (pass criteria before quality domain evaluates)
- Tool/fixture configuration standards

However, the precise entity scope for FleziBCG is **not yet designed** for the current phase.

---

## 5. Candidate Entity Model

### Evaluation

| Candidate Entity | Evidence | Domain Ownership Risk | Phase Gate | Decision |
|---|---|---|---|---|
| `ProcessParameter` (e.g., temperature, pressure, pH, speed) | Roadmap Phase 11 explicit | Low — clearly IEP scope | **Phase 11 (P2-A)** | Defer to Phase 11 |
| `WorkInstruction` / `ProcessInstruction` | `iep-configuration-action-contract.md` mentions it; no schema evidence | Medium — overlaps MMD "procedure/phase-ready definitions" | Phase unknown | Defer — boundary unclear |
| `StandardTime` / `CycleTimeTarget` | `mes-business-logic-v1.md` "standards, thresholds" — conceptual only | Low — IEP scope | Phase unknown | Defer — no schema authority |
| `ProcessThreshold` | Conceptual from `mes-business-logic-v1.md` | Medium — may overlap Quality templates | Phase unknown | Defer — boundary unclear |
| `ProcessConfiguration` (generic parent) | Naming only — not in any design doc | High — invented scope | Not in any phase | Rejected |
| Routing / BOM / Product / Resource Requirement | MMD ADMIN-family codes already exist | **HIGH** — already covered by ADM lane | Already implemented | **OUT** |

### Conclusion

**No entity can be safely named and designed in this slice.**

All concrete process parameter types either:
- Are explicitly Phase 11 items per the roadmap, or
- Risk overlap with MMD domain (which owns "procedure/phase-ready definitions"), or
- Lack sufficient schema/API design authority in current docs.

---

## 6. In Scope (Future)

When the future Phase 11 design slice is executed, the following **may** be in scope:

- Process parameters scoped to operation/routing-step context (numeric ranges with unit of measure).
- Standard time / cycle time targets per routing operation and product context.
- Work instructions or process instruction documents attached to routing operations.
- Process configuration version management (Draft → Active → Retired lifecycle).

These are **not designed here**. They require a Phase 11 design gate.

---

## 7. Explicitly Out of Scope

The following must **never** be gated by `configure.process.manage`:

| Entity / Domain | Reason |
|---|---|
| Routing (structure, steps, sequence) | `admin.master_data.routing.manage` — ADMIN family |
| BOM (bill of materials) | ADMIN family |
| Product / Product Version lifecycle | `admin.master_data.product*.manage` — ADMIN family |
| Resource Requirements | `admin.master_data.resource_requirement.manage` — ADMIN family |
| Downtime Reason codes | `admin.downtime_reason.manage` — ADMIN family |
| IAM user management | `admin.user.manage` — ADMIN family |
| Quality inspection templates and rule sets | QAL/Quality domain; APPROVE lane |
| Quality evaluation / hold / disposition | Quality domain |
| Execution state transitions | EXECUTE lane — OPR/SUP |
| Station session / operator context | EXECUTE lane |
| Planning/scheduling sequences | PLN VIEW-only; Planning domain |
| Security/audit event access | `admin.security_event.read` — ADMIN family |
| Recipe / phase / ISA-88 models | Phase 11 — not current scope |

---

## 8. Domain Boundary Map

```
┌─────────────────────────────────────────────────────────────────┐
│  MMD Domain (ADMIN lane)                                        │
│  Product, Product Version, Routing, BOM, Resource Req          │
│  admin.master_data.*.manage codes                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │ references
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Process Configuration Domain (CONFIGURE lane — IEP)            │
│  configure.process.manage (RESERVED — no entity yet)           │
│  Future: process parameters, standard times, work instructions │
│  Phase 11 gate                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ governs
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Execution Domain (EXECUTE lane — OPR/SUP)                      │
│  Start, Complete, Report, Downtime, Close, Reopen              │
│  execution.* codes                                             │
└─────────────────────────────────────────────────────────────────┘
```

Key boundary rules:

- Process configuration does not own MMD lifecycle (create/release/retire) — that is ADMIN.
- Process configuration does not own execution state transitions — that is EXECUTE.
- Process configuration does not own quality evaluation — that is Quality domain.
- Process configuration entities reference MMD entities (routing operations) but do not replace them.

---

## 9. Future Action Code Usage

When entity design is complete:

```
configure.process.manage   → CONFIGURE family → IEP role
```

This code gates all IEP-authored mutations to process configuration entities.

READ access to process configuration data: `require_authenticated_identity` (VIEW family — no action code needed).

If future design shows distinct process configuration sub-domains requiring separate actions, additional CONFIGURE-family codes may be defined — naming convention: `configure.<sub_domain>.manage`.

---

## 10. Future API / Command Boundary

No API design is possible without entity design. The following **principles** apply when implemented:

- Mutation routes use `require_action("configure.process.manage")`.
- Read routes use `require_authenticated_identity`.
- All mutations are tenant-scoped.
- Commands are idempotent where possible.
- No mutation bypasses scope isolation.

**Prohibited route designs:**

- Routes that also accept routing structure mutations (MMD boundary).
- Routes that trigger execution state changes.
- Routes that evaluate quality hold/pass/fail.

---

## 11. Future Event / Audit Boundary

When implemented:

- Process configuration changes are **not** execution events (no `ExecutionEvent` row).
- Process configuration changes **are** audit-relevant:
  - Under impersonation: automatically logged by `_AUDITED_FAMILIES` (includes CONFIGURE).
  - Direct mutations: may require explicit security event if process configuration is governance-sensitive.
- Process configuration events must not trigger: execution state changes, ERP postings, quality disposition, or backflush consumption.

---

## 12. SoD / Authorization Boundary

| Constraint | Rule |
|---|---|
| IEP authors process configuration | IEP role has CONFIGURE family |
| ADM/OTS cannot perform process config without IEP impersonation | FORBIDDEN_ACTING_ROLES excludes ADM/OTS as targets — they cannot impersonate ADM/OTS |
| IEP cannot start/complete execution | No EXECUTE in `SYSTEM_ROLE_FAMILIES["IEP"]` |
| IEP cannot approve governed decisions | No APPROVE in `SYSTEM_ROLE_FAMILIES["IEP"]` |
| IEP cannot manage IAM or MMD release | No ADMIN in `SYSTEM_ROLE_FAMILIES["IEP"]` |
| SoD for process config approval | To be defined in Phase 11 design slice (open question) |
| Process config SoD posture | If process parameter changes affect safety/regulatory compliance, an APPROVE loop may be required; this is Phase 11 decision |

---

## 13. Data Ownership and Source of Truth

| Data | Owner | Source of Truth |
|---|---|---|
| Process configuration entities (future) | IEP (CONFIGURE action) | Backend DB (process config tables) |
| Routing structure | ADM (ADMIN action) | Backend DB (MMD tables) |
| Execution events | OPR/SUP (EXECUTE action) | Backend DB (execution_events — append-only) |
| Quality evaluation | QAL (APPROVE action) | Backend DB (quality tables) |
| Auth / permission | Backend only | Backend DB — never derived by frontend |

Process configuration is **not** a projection or read model. It is operational master data
authored by IEP and consumed by execution processes.

---

## 14. Implementation Preconditions

Before `configure.process.manage` is added to `ACTION_CODE_REGISTRY` **and** before any
process configuration entity is added to the schema:

1. **Phase 11 design gate**: The Phase 11 (P2-A) process/batch/ISA-88 depth slice is
   initiated or its relevant sub-scope is pulled forward by customer demand.
2. **Entity design authority**: A dedicated design document defines the exact entity model
   (table names, fields, relationships to MMD routing operations).
3. **MMD boundary confirmation**: Process configuration entities are confirmed to NOT
   duplicate or replace any existing MMD entity (product, routing, BOM, resource requirement).
4. **Quality boundary confirmation**: Process thresholds/targets do not duplicate quality
   template/rule-set entities owned by the Quality domain.
5. **SoD decision**: Whether process parameter changes require an approval loop is decided
   (open question from P0-A-10 §14 Q2).
6. **Scope level decision**: Whether `configure.process.manage` operates at tenant, plant,
   line, or station scope level is decided (P0-A-10 §14 Q5).
7. **API route ready**: At least one mutation route exists or is ready to be added.
8. **Migration ready**: Alembic migration for process configuration entities is designed.
9. **P0-A-10 IEP contract reviewed**: No §6 Out of Scope boundary was crossed.

---

## 15. Tests Required Before Runtime Adoption

| Test | File | Purpose |
|---|---|---|
| Update `_EXPECTED_CONFIGURE_CODES` set | `test_rbac_action_registry_alignment.py` | Lock `configure.process.manage` in canonical set |
| Add CONFIGURE code seed assertion | `test_rbac_seed_alignment.py` | Verify seed creates Permission + IEP RolePermission row |
| Process config route returns 403 for non-IEP | New route test | Verify CONFIGURE guard |
| Non-IEP cannot mutate process configuration | Negative boundary test | OPR/QAL/ADM direct attempts return 403 |
| Process config mutation does not affect execution status | Isolation test | No `ExecutionEvent` row created |
| Process config mutation does not affect MMD routing | Negative boundary test | Routing version unchanged |
| Update `test_rbac_configure_family_boundary.py` | Boundary lock update | Remove "zero CONFIGURE codes" assertion, replace with exact count |

---

## 16. Open Questions

| # | Question | Owner | Phase Gate |
|---|---|---|---|
| Q1 | Which specific entity types are in scope — process parameters only, or also work instructions, standard times? | Phase 11 design | Phase 11 |
| Q2 | Does process parameter configuration require an approval loop (SoD)? | Phase 11 design | Phase 11 |
| Q3 | Is one `configure.process.manage` code sufficient, or are multiple narrower CONFIGURE codes needed? | Phase 11 design | Phase 11 |
| Q4 | What is the exact schema and lifecycle for process configuration entities? | Phase 11 design | Phase 11 |
| Q5 | Does equipment-level configuration (maintenance-adjacent) belong to IEP CONFIGURE or a separate admin scope? | Phase 10/11 design | Phase 10/11 |
| Q6 | What scope level — tenant, plant, line, or station — does `configure.process.manage` operate at? | Phase 11 design | Phase 11 |
| Q7 | Do work instructions belong to IEP CONFIGURE domain or to MMD "procedure/phase-ready definitions"? | MMD + IEP boundary review | Phase 11 |

---

## 17. Final Decision

**Option B — Defer entity contract.**

Entity design cannot proceed safely in this slice because:

1. **Process parameters are Phase 11 (P2-A)** — explicitly deferred per `flezibcg-overall-roadmap-latest.md`.
2. **MMD domain boundary overlap** — `docs/design/00_platform/domain-boundary-map.md` assigns "recipe / formula / procedure / phase-ready definitions" to MMD, which overlaps candidate process configuration entities.
3. **No backend source evidence** — no process configuration model, table, service, or route exists in `backend/app/`.
4. **IEP current concrete actions are ADMIN-family** — per `2026-05-01-master-data-hardening-proposal.md`, IEP's create/update operations on routing/BOM/resource requirement are ADMIN-family codes, not a separate CONFIGURE entity scope.
5. **7 open questions remain** — none of which can be answered without Phase 11 design authority.

**`configure.process.manage` remains reserved** per `docs/design/02_registry/action-code-registry.md`.

**Next required action**: Initiate Phase 11 (P2-A) design gate or pull a sub-scope forward based
on customer demand (food/pharma/chemical/batch/process-heavy trigger per roadmap).

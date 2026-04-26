# Hardening Action Register — FleziBCG MOM Platform

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.1 | Synced register with actual Task 3 ADR filenames, upgraded HRD-026 Timezone/Localization from WATCH to P1-HARDENING ADR, added HRD-027 current phase rule and HRD-028 BLOCKED reason projection fields, and added Task 4.1 housekeeping patch. |
| 2026-04-26 | v1.0 | Created hardening action register from architecture review after the 2026-04-26 latest design baseline. |

## Status

**Canonical hardening backlog derived from post-baseline design reviews.**

This file does not replace the baseline. It sits on top of the baseline and tracks hardening/alignment tasks required before broad production-grade implementation.

Baseline assumptions remain:

- Function List v2.1
- Screen UI Inventory v2.2
- Database Design v1.2
- Product Business Truth v1.2
- Domain Boundary Map v2.2
- API/Event/Reporting catalogs v2.1
- Integration docs v2.1
- Hardening v1 package completed
- Hardening Housekeeping v1.1 completed before Task 5

---

## 1. Severity Scale

| Severity | Meaning | Action rule |
|---|---|---|
| `P0-HARDENING` | Must patch before implementation from broad design docs. | Patch immediately. |
| `P1-HARDENING` | Important before production-grade expansion; can follow immediate consistency patch. | Add ADR/decision note and update related docs. |
| `P2-HARDENING` | Important for later scale/regulatory/advanced capability. | Document as roadmap/ADR; do not overbuild now. |
| `WATCH` | Valid concern but not current blocker. | Track and revisit when scope/customer/deployment changes. |

---

## 2. Hardening Summary

| ID | Area | Severity | Type | Short Description | Status / Decision |
|---|---|---|---|---|---|
| HRD-001 | Execution / Function List | `P0-HARDENING` | Consistency fix | Rework mismatch: Function List implied good/scrap/rework reporting, but Station Execution v4 contract supports good/scrap only. | Fixed in Task 2. P0 report production remains good/scrap. Rework becomes P1 via Quality/Rework flow. |
| HRD-002 | Execution State | `P0-HARDENING` | Consistency fix | `ABORTED` state appeared but had no reachable transition. | Fixed in Task 2. `ABORTED` is reserved/future-only in P0. |
| HRD-003 | Quality / Execution | `P0-HARDENING` | Clarification | Quality-gated execution exists in target design, but P0 Station Execution does not enforce full quality gate guard. | Fixed in Task 2. Full Acceptance Gate guard is P1. |
| HRD-004 | Quality | `P0-HARDENING` | Clarification | Pre-Acceptance Check naming could look like separate aggregate. | Fixed in Task 2. It is `gate_type = pre_acceptance` under Quality Gate aggregate. |
| HRD-005 | Quality | `P0-HARDENING` | Mapping gap | Quality Lite summary states and Quality Gate lifecycle states needed mapping. | Fixed in Task 2. |
| HRD-006 | Backflush / Material | `P0-HARDENING` | Consistency fix | Relationship between `inv.backflush_consumption_records` and `inv.material_consumption_events` was unclear. | Fixed in Task 2. Backflush record is enriched transaction; material consumption event is append-only fact. |
| HRD-007 | Backflush / Material | `P0-HARDENING` | Consistency fix | Backflush trigger timing differed across docs. | Fixed in Task 2. Canonical triggers: `quantity_reported`, `operation_completed`, `operation_closed`. |
| HRD-008 | Engineering / Security | `P0-HARDENING` | Security doc fix | CloudBeaver appeared in runtime/tooling context without dev-only restriction. | Fixed in Task 2. CloudBeaver is local/dev-only, not production runtime surface. |
| HRD-009 | Governance Docs | `P0-HARDENING` | Documentation hygiene | Cross-review report could be mistaken as canonical truth. | Fixed in Task 2. Review reports are audit artifacts only. |
| HRD-010 | ISA-95 Semantics | `P1-HARDENING` | Architecture clarification | `line/station` can look discrete-biased vs ISA-95 work center/work unit vocabulary. | Addressed in Task 3 via semantic mapping/alias decision. Keep P0 names. |
| HRD-011 | ISA-88 Batch | `P1-HARDENING` | Architecture clarification | Batch/process ISA-88 model is not detailed enough for batch-first plants. | Addressed in Task 3. Defer unless first vertical is batch/process/pharma/food/chemical. |
| HRD-012 | Eventing | `P1-HARDENING` | ADR | Internal event schema not explicitly CloudEvents-compatible. | Addressed in Task 3: internal FleziBCG schema, external/brokered CloudEvents-compatible. |
| HRD-013 | API | `P1-HARDENING` | ADR | API versioning and error format needed production-grade standard. | Addressed in Task 3: `/api/v1` and RFC 9457-compatible error shape. |
| HRD-014 | Traceability | `P1-HARDENING` | ADR | EPCIS compatibility not documented. | Addressed in Task 3; detailed EPCIS 2.0/GS1 CBV deferred until needed. |
| HRD-015 | Security / Multi-tenancy | `P1-HARDENING` | ADR | PostgreSQL RLS strategy not documented. | Addressed in Task 3: app-layer mandatory, RLS P1 defense-in-depth. |
| HRD-016 | Shopfloor Connectivity | `P1-HARDENING` | ADR | OPC UA / MQTT / Sparkplug B / edge buffering / time sync not designed. | Addressed in Task 3 as direction; exact versions/config deferred until connectivity scope. |
| HRD-017 | Reporting / KPI | `P1-HARDENING` | Spec patch | OEE formula and source fields not explicit enough. | Addressed in Task 3. |
| HRD-018 | Performance | `P1-HARDENING` | ADR | Performance/capacity assumptions were thin. | Addressed in Task 3 with initial SLO/capacity targets. |
| HRD-019 | Database Ops | `P1-HARDENING` | ADR | Partition/archive/snapshot strategy not defined. | Addressed in Task 3. |
| HRD-020 | Architecture Wording | `P1-HARDENING` | Architecture correction | “Extraction-ready” overpromised while cross-domain FK exists. | Addressed in Task 3: modular monolith, extraction-aware. |
| HRD-021 | Event Publishing | `P1-HARDENING` | ADR | Broker/publisher abstraction not documented. | Addressed in Task 3: EventPublisher, OutboxPublisher, ProjectionDispatcher, IntegrationMessagePublisher. |
| HRD-022 | Authorization | `P1-HARDENING` | ADR | Policy engine path not decided. | Addressed in Task 3: typed internal service P0, evaluate OPA/Casbin/custom P1. |
| HRD-023 | Cache | `P2-HARDENING` | ADR | Cache strategy not documented. | Addressed in Task 3: DB-first P0, Redis optional P1/P2. |
| HRD-024 | Observability | `P1-HARDENING` | ADR | Observability stack not explicit. | Addressed in Task 3. |
| HRD-025 | AI Guardrails | `P2-HARDENING` | ADR | AI technical guardrails not detailed. | Addressed in Task 3. |
| HRD-026 | Timezone / Localization | `P1-HARDENING` | ADR | Timezone/localization handling needed clearer guidance for multi-country/Japan-aware plants. | Fixed in Task 4.1. Added `timezone-and-localization-strategy.md`. |
| HRD-027 | Execution Current Phase | `P0-HARDENING` | Documentation hygiene | Current phase rule in execution v4 remained vague. | Fixed in Task 4.1. Added explicit P0/P1/P2 phase rule to execution docs. |
| HRD-028 | BLOCKED Reason Projection | `P0-HARDENING` | Contract clarity | BLOCKED state lacked block source/reason fields to distinguish downtime, quality, material, equipment, approval, etc. | Fixed in Task 4.1. Added canonical projection fields. |
| HRD-029 | Infrastructure Decisions | `WATCH` | Decision backlog | K8s/bare VM, secrets manager, backup tooling, CI/CD, first customer vertical not known. | Track. Do not block Task 5 P0-A Foundation DB. |

---

## 3. Task Execution Order

### Task 1 — Create Hardening Action Register

Status: `DONE`

Output:

```text
docs/design/10_hardening/hardening-action-register.md
```

### Task 2 — Immediate Consistency Patch

Status: `DONE`

Covered HRD-001 to HRD-009.

### Task 3 — Hardening ADR Pack

Status: `DONE`

Actual output files:

```text
docs/design/10_hardening/event-format-and-cloudevents-boundary.md
docs/design/10_hardening/api-versioning-and-error-format.md
docs/design/10_hardening/tenant-isolation-and-rls-strategy.md
docs/design/10_hardening/performance-capacity-slo.md
docs/design/10_hardening/database-partition-archive-strategy.md
docs/design/10_hardening/shopfloor-connectivity-strategy.md
docs/design/10_hardening/observability-stack.md
docs/design/10_hardening/authorization-policy-engine-adr.md
docs/design/10_hardening/oee-formula-and-kpi-definition.md
docs/design/10_hardening/traceability-epcis-alignment.md
docs/design/10_hardening/isa88-batch-alignment.md
docs/design/10_hardening/modular-monolith-extraction-aware-architecture.md
docs/design/10_hardening/cache-strategy.md
docs/design/10_hardening/ai-guardrails-and-operational-safety.md
```

Note: the earlier planned names `isa95-and-isa88-alignment.md` and `ai-guardrails.md` are superseded by the actual filenames above. `timezone-and-localization-strategy.md` is created in Task 4.1.

### Task 4 — Latest Hardening Package Export

Status: `DONE`

Output:

```text
FleziBCG_latest_design_package_2026-04-26_hardening-v1.zip
FleziBCG_hardening_v1_overlay_patch.zip
```

### Task 4.1 — Hardening Housekeeping Patch v1.1

Status: `DONE`

Covered:

- governance docs lag;
- register/file drift;
- timezone ADR;
- current phase rule;
- BLOCKED reason projection fields;
- CD Review 1 response.

Output:

```text
FleziBCG_hardening_housekeeping_v1_1_patch.zip
```

### Task 5 — Implementation Slicing Prompt

Status: `NEXT`

Recommended first implementation slice:

```text
P0-A Foundation Database Slice:
- tenant
- IAM
- sessions
- role/action/scope
- audit
- plant hierarchy
- scope nodes
```

Explicit exclusions:

```text
ERP integration
Acceptance Gate
Backflush
APS
AI
Digital Twin
Compliance/e-record
```

---

## 4. Decisions That Should Not Be Reopened During Hardening

| Decision | Keep? | Reason |
|---|---:|---|
| Backend is source of truth | Yes | Core platform invariant. |
| Persona is not permission | Yes | Security/governance invariant. |
| JWT proves identity only | Yes | Authorization must be checked per backend request. |
| AI advisory by default | Yes | Prevents unsafe autonomous mutation. |
| Execution target is session-owned | Yes | Claim is migration debt only. |
| Acceptance Gate is canonical; LAT is display label | Yes | Keeps product manufacturing-mode-neutral. |
| Backflush is cross-domain | Yes | Prevents execution-only material/ERP coupling. |
| ERP is not replaced by FleziBCG | Yes | Correct MOM boundary. |
| Digital Twin is derived | Yes | Prevents twin becoming source of truth. |
| Reporting/KPI is deterministic before AI | Yes | Keeps KPI reliable. |

---

## 5. Non-Goals

This hardening register does not authorize:

- implementing all P1/P2/P3 modules;
- adding Kafka/Redis/OPA/OPC UA immediately;
- changing all `line/station` naming to `work_center/work_unit` now;
- rewriting internal event schema to CloudEvents-only;
- turning Quality Lite into full QMS;
- turning maintenance into full CMMS;
- turning material context into full WMS;
- turning integration into ERP replacement.

---

## 6. Final Verdict

The baseline remains valid. Hardening v1 + Housekeeping v1.1 closes review-driven documentation drift and allows Task 5 to proceed with a narrow P0-A implementation prompt.

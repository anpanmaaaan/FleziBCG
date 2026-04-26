# Product Business Truth — FleziBCG MOM Platform

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v1.1 | Revised to align role taxonomy, ownership direction, eventing note, and domain boundaries. |

## Status

**Authoritative product business truth for overall platform shape**

## Scope

This document is authoritative for:
- overall product definition of FleziBCG
- platform-level MOM scope and module shape
- product-level principles and boundaries
- standards alignment at product level
- platform extension rules
- current engineering baseline summary at product level

This document is not:
- a sprint plan
- a screen specification
- an API transport contract
- a DB schema specification
- a route inventory
- a detailed implementation matrix for any single domain

Those belong to domain, application, and governance documents.

## Depends on

- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`

---

## 1. Purpose

This document exists so that any reader can understand, quickly and consistently:
- what FleziBCG is
- what business problem it solves
- what modules belong to the platform
- what principles the platform must always follow
- what FleziBCG does not try to replace
- how future contributors should extend the platform without distorting its shape

This is the product-level truth document that should anchor future design and discussion.

---

## 2. Product Definition

## 2.1 What FleziBCG is

**FleziBCG** is an **AI-driven Manufacturing Operations Management (MOM) platform** aligned with **ISA-95**, designed to manage, coordinate, monitor, and improve manufacturing operations across the factory.

It sits between:
- enterprise planning and transaction systems
- shopfloor execution reality
- equipment and control-layer data sources

FleziBCG turns day-to-day manufacturing activity into:
- operational truth
- governed action context
- supervisory visibility
- cross-domain operational coordination
- a foundation for AI-driven insight and future digital twin capabilities

In one sentence:

> **FleziBCG is the MOM platform that transforms manufacturing operations into trusted, structured, actionable operational truth.**

## 2.2 What FleziBCG is not

FleziBCG is not:
- an ERP replacement
- a PLC / SCADA / control system replacement
- a pure dashboard product
- a full enterprise QMS replacement
- a full CMMS replacement
- a generic AI chatbot for factories

FleziBCG is a MOM platform focused on operational truth, execution-adjacent management, and cross-domain manufacturing operations visibility.

---

## 3. Standards Alignment

## 3.1 ISA-95 alignment

FleziBCG is designed to be **aligned with ISA-95**.

That means the platform is shaped as a **manufacturing operations layer**, rather than as:
- enterprise business planning software
- machine control software
- ad hoc shopfloor screens without domain boundaries

ISA-95 alignment in FleziBCG means:
- production operations are managed at MOM level
- quality operations are managed as operational quality, not as enterprise document control
- maintenance interaction is recognized as part of operations context
- inventory/material/WIP context is handled at operational level where required
- plant hierarchy and operational context are modeled explicitly

## 3.2 Hierarchical scope alignment

FleziBCG is designed for hierarchical scope, not tenant-only flat scope.

Canonical scope hierarchy:
- tenant
- plant
- area
- line
- station
- equipment

This hierarchy is foundational to product behavior, not just implementation detail.

## 3.3 Manufacturing-mode-neutral direction

FleziBCG must remain **manufacturing-mode-neutral** at platform level.

The platform must be able to evolve for:
- discrete manufacturing
- batch manufacturing
- continuous manufacturing
- hybrid manufacturing

This means platform-level vocabulary should remain broad enough to support:
- production request / order / batch context
- resource / work center / station / equipment context
- material / lot / genealogy context
- execution and planning truth without locking the platform to one plant model only

The canonical hierarchy remains stable, but plant-specific semantics may be mapped onto it through equipment/resource typing and level aliases. See `manufacturing-mode-hierarchy-mapping.md`.

---

## 4. Core Mission

FleziBCG exists to help a manufacturer answer, reliably and in context:
- what is being produced
- where it is happening
- by whom it is being executed
- on which resource or equipment it is happening
- what the runtime situation is now
- whether operations are blocked, delayed, held, or disrupted
- how quality, material, and maintenance conditions affect execution
- what supervisors and managers need to do next
- what operational insight can be derived from the underlying facts

---

## 5. Platform Principles

## 5.1 Backend is the source of truth

Backend owns:
- execution truth
- status truth
- authorization truth
- approval truth
- audit truth

Frontend owns:
- UX composition
- navigation
- interaction state
- visualization
- display formatting

Frontend must never become the final authority for execution or permission truth.

## 5.2 Execution is event-driven

Important operational facts are represented in an event-driven manner.

The platform assumes:
- execution facts must be auditable
- status should be derived from operational history
- projections support visibility, but are not the source of truth

### Implementation note
Current implementation direction uses a **DB-backed append-only event log with derived projections/read models**.
A broker, workflow engine, or distributed event backbone may be added later where justified, but is **not required by default** to satisfy the product's event-driven principle.

## 5.3 Governance is first-class

FleziBCG is not only about operational capability.
It is also about governed capability.

The platform must preserve:
- explicit identity
- explicit scope
- auditable privileged actions
- approval where required
- separation of duties where required
- reviewable support/admin actions

## 5.4 Persona is not permission

Visible screens, menus, and personas are UX constructs.
They are not the authoritative source of permission truth.

## 5.5 JWT proves identity only

Identity tokens prove who the actor is.
They do not by themselves decide whether the action is allowed.

## 5.6 AI is advisory by default

AI in FleziBCG may:
- summarize
- explain
- predict
- recommend
- detect anomalies

AI must not by default:
- silently mutate operational truth
- bypass auth, approval, or SoD
- present uncertain output as deterministic system fact

---

## 6. Product Scope and Module Model

FleziBCG is a platform composed of multiple operational modules.

## 6.1 Foundation & Governance

This module family includes:
- identity
- authentication
- session lifecycle
- user lifecycle
- role assignment
- scope assignment
- approval and delegation
- impersonation / support mode
- audit
- plant hierarchy
- master data governance

This is foundational to all other platform modules.

## 6.2 Manufacturing Master Data & Product Definition

This module family includes the shared manufacturing definitions used across the platform.

It includes:
- product structure
- BOM
- routing
- recipe / formula / procedure / phase-ready definitions
- versioned manufacturing definitions
- product-resource requirements
- quality-definition linkage where needed

This module is the canonical home for:
- BOM
- product structure
- recipe-like manufacturing definitions

It is intentionally separate from traceability, because these definitions are shared by:
- execution
- quality
- traceability
- planning & scheduling
- digital twin

## 6.3 Execution Management

This is the execution core of the platform.

It includes:
- work execution
- execution context
- runtime state
- quantity reporting
- event history
- downtime
- completion and closure
- operator activity in execution context
- resource/equipment-bound execution visibility
- backend-derived operational action truth

### Ownership direction
Target execution ownership is **session-based**, not claim-based.

For discrete-first Station Execution, the governing ownership context is:
- active station session
- identified operator
- bound equipment/resource context when required

`claim` is deprecated from the target model and treated only as migration compatibility debt where still present in source code or legacy docs.

## 6.4 Supervisory Operations

This module family includes:
- global operations visibility
- operation detail
- progress and blockage visibility
- line / area / plant monitoring views
- timelines and Gantt-style operational views
- supervisory coordination support

## 6.5 Quality Operations

This module family includes operational quality functions that directly affect manufacturing execution.

It includes:
- quality applicability
- inspection / measurement flow
- backend evaluation
- pass / fail / hold semantics
- review / disposition interaction
- quantity acceptance implications
- quality-to-execution interaction rules

### Boundary with QMS

FleziBCG Quality Operations is **not** a full enterprise QMS.

It is focused on **shopfloor-operational quality truth**.
It does not aim, by default, to replace enterprise-wide capabilities such as:
- full CAPA
- enterprise document control
- supplier quality suites
- broad compliance-management platforms

## 6.6 Traceability & Material Operations

This module family includes:
- material context
- lot / batch context
- genealogy foundation
- consumption / production linkage
- accepted-good / reported-good context
- traceability across execution, material, and quality

This module consumes manufacturing definitions from Manufacturing Master Data & Product Definition.

## 6.7 Inventory / WIP / Material Flow Context

This module family includes:
- WIP visibility
- queue / buffer / handoff context
- operational material movement visibility
- issue / consume / return context where needed
- shopfloor inventory interactions with execution

It does not replace ERP inventory or a full WMS.

See `material-traceability-vs-inventory-boundary.md` for the explicit source-of-truth split between Inventory/WIP and Traceability.

## 6.8 Maintenance Operations

This module family includes operational maintenance interaction relevant to MOM.

It includes:
- maintenance-related operational context
- equipment availability context
- planned vs unplanned maintenance interaction with production
- maintenance-driven downtime visibility
- production-maintenance coordination context
- future predictive / condition-based maintenance support path

### Early-stage role model for maintenance

Maintenance is **not yet modeled as a first-class independent persona family**.

In the current product shape, early maintenance interaction is covered by:
- IEP
- SUP
- PMG

Maintenance-related governed decisions still inherit the same SoD and approval rules as other governed operational actions.

## 6.9 Planning & Scheduling (APS)

Planning & Scheduling is a **first-class FleziBCG module**.

It includes:
- sequencing support
- dispatch recommendation
- finite-capacity-aware planning support
- resource-aware prioritization
- disruption-aware replanning hints
- planning/execution alignment support

### APS principle

APS manages:
- planning truth
- scheduling truth
- optimization proposals

APS does **not** replace execution truth.

> **APS proposes and optimizes plans; Execution confirms operational reality.**

### AI and APS

AI may later improve APS by increasing:
- prediction accuracy
- responsiveness to live disruption
- dispatch quality
- schedule adaptation quality

But AI-enhanced APS still must not overwrite execution truth by default.
Advanced optimizers or scheduling engines may run as adjunct services where scale or latency requires it.

## 6.10 Operational Intelligence / AI

This module family includes:
- shift summaries
- anomaly detection
- OEE deep-dive insight
- bottleneck explanation
- delay risk insight
- natural-language operational insight
- recommendation support for execution, supervisory, and APS modules

## 6.11 Digital Twin

FleziBCG digital twin direction is **operational digital twin first**, not 3D-first.

It includes:
- operational visibility of lines, work centers, stations, and equipment
- work-state visibility
- WIP / queue / blockage / delay context
- relationship modeling across operational entities
- what-if analysis foundation

---

## 7. Roles and Operating Personas

FleziBCG uses MOM/MES role thinking.

Primary MOM business role families include:
- OPR
- SUP
- IEP
- QAL
- PMG
- PLN
- INV
- ADM

Specialized / compatibility / support roles may also exist, including:
- QCI
- OTS

Broad role intent:
- **OPR**: execution actor
- **SUP**: supervisory and coordination actor
- **IEP**: engineering / process / operational improvement actor
- **QAL**: primary quality business actor
- **QCI**: optional specialized inspection compatibility role where needed
- **PMG**: management and broader operational decision actor
- **PLN**: planning and scheduling actor
- **INV**: inventory / WIP / material-flow actor
- **ADM**: system administration actor
- **OTS**: support / break-glass actor, **not** a default production persona

Maintenance interaction in the early platform shape is covered by:
- IEP
- SUP
- PMG

---

## 8. Overall Operating Model

At a high level, FleziBCG connects these layers of truth:
- authenticated user
- acting operational context
- production request / order / batch context
- resource / work center / station / equipment context
- runtime execution state
- quantity and event history
- downtime / blockage / quality interaction
- maintenance interaction
- material / lot / genealogy context
- supervisory visibility
- planning and scheduling context
- intelligence outputs

The purpose of the platform is not only to answer what has happened, but also:
- what is happening now
- where it is happening
- why it is blocked or delayed
- what context is affecting it
- what should happen next

---

## 9. Product Boundaries vs Adjacent Systems

## 9.1 ERP

ERP holds:
- enterprise planning
- financial/commercial truth
- enterprise transaction truth

FleziBCG holds:
- operational truth
- execution reality
- operator/resource/equipment context
- MOM-level visibility and governance

## 9.2 PLC / SCADA / Historian

Control-layer systems hold:
- machine control
- sensor signals
- control-loop behavior
- raw telemetry / historian data

FleziBCG holds:
- operational meaning
- production context
- execution truth
- supervisory and cross-domain operational coordination

## 9.3 QMS / CMMS / WMS

FleziBCG may integrate with:
- QMS
- CMMS
- WMS

But FleziBCG remains centered on MOM-level operational truth and does not try to collapse every enterprise system into one domain.

---

## 10. Current Engineering Baseline

This section describes the **current engineering baseline**, not the product essence.

## 10.1 Runtime architecture

Current runtime direction:
- modular monolith
- boundary-clean
- extraction-ready
- no premature microservice-only assumptions
- no cloud-only mandatory dependency by default

## 10.2 Tech stack

Current engineering baseline stack:
- backend: Python 3.12 + FastAPI
- frontend: React 18 + TypeScript + Vite + Tailwind CSS
- database: PostgreSQL
- authentication: JWT + Argon2
- deployment direction: local / Docker / on-prem friendly, cloud adaptable
- system direction: multi-tenant, hierarchical-scope-ready

## 10.3 Practical architecture note

The current engineering baseline is optimized first for:
- operational truth
- governance
- deterministic execution behavior
- modular platform growth

High-frequency telemetry, advanced optimization, and specialized analytics may later be integrated through adjunct services or specialized components, rather than being forced directly into the core OLTP path.

This avoids over-promising a single-stack answer for every operational and analytical workload.

---

## 11. Extension Rules

If FleziBCG is extended, all contributors must preserve the following truths.

## 11.1 Do not violate core truth

Do not extend the platform in ways that make:
- frontend the source of execution truth
- JWT the final source of permission truth
- AI a silent operational controller
- persona the same thing as authorization
- tenant/scope isolation optional

## 11.2 Add modules without breaking boundaries

New modules must:
- have clear domain boundaries
- reuse shared truths where appropriate
- avoid contradictory duplicate vocabulary
- stay compatible with platform principles

## 11.3 Keep manufacturing definitions shared

BOM, routing, recipe, formula, and related product/resource definitions must remain shared manufacturing definitions, not be trapped inside one narrow downstream module.

## 11.4 Planning must not overwrite reality

Planning, APS, and optimization may recommend and propose.
Execution confirms what is operationally real.

## 11.5 Execution-adjacent domains must stay linked to consequences

Quality, maintenance, material flow, and inventory/WIP context should remain execution-adjacent in platform logic, rather than drifting into disconnected side applications.

## 11.6 Stay manufacturing-mode-neutral at platform level

Future growth must not accidentally reduce FleziBCG into a discrete-only platform model.

---

## 12. Platform Roadmap Shape

The overall platform shape grows in this broad order:
1. Foundation & Governance
2. Manufacturing Master Data & Product Definition
3. Execution Management
4. Supervisory Operations
5. Quality Operations + Traceability & Material Operations
6. Inventory / WIP / Material Flow Context
7. Maintenance Operations
8. Planning & Scheduling (APS)
9. Operational Intelligence / AI
10. Digital Twin and broader MOM expansion

This is a product-shape roadmap, not a sprint backlog.

---

## 13. Final Product Definition

**FleziBCG is an ISA-95-aligned MOM platform that manages execution truth, operational context, governance, planning support, visibility, and intelligence across manufacturing operations. It connects people, work, resources, quality, material, maintenance, planning, and operational insight into one backend-authoritative, event-driven platform ready to evolve into a broader MOM ecosystem.**

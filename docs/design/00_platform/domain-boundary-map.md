# Domain Boundary Map

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.1 | Added product definition and explicit traceability vs inventory boundary clarification. |

Status: Canonical domain boundary note.

## 1. Platform-level bounded contexts

### Foundation / IAM / Governance
Owns:
- identity
- access control
- user lifecycle
- session governance
- approvals and SoD
- impersonation / support governance
- audit and observability foundations

### Manufacturing Master Data & Product Definition
Owns:
- product structure
- BOM
- routing
- recipe / formula / procedure / phase-ready definitions
- versioned manufacturing definitions
- product/resource requirements

### Execution
Owns:
- production request / execution run / execution step abstractions
- runtime execution mutation
- operator context inside execution
- equipment/resource context inside execution
- quantity and downtime mutation
- closure / reopen foundation
- allowed action derivation

### Quality
Owns:
- QC applicability
- templates and rule sets
- measurement submission
- evaluation / pass / fail / hold truth
- disposition path
- accepted-good implications

### Traceability
Owns:
- serial / lot / batch / genealogy truth
- material consumption/production trace edges
- query views for backward/forward trace
- linkage between execution facts, material identity, and quality outcomes

### Inventory / WIP / Material Flow
Owns:
- stock/WIP position
- material movement transactions
- issue / consume / return / transfer semantics
- queue/buffer/container movement semantics where in scope

### Maintenance / Equipment Context
Owns:
- equipment master and capability context
- maintenance adjacency and operational availability context

### Planning & Scheduling (APS)
Owns:
- planning truth
- schedule proposals
- sequencing / dispatch recommendations
- replanning logic where in scope

### Supervisory Operations
Owns:
- operational visibility
- intervention views where policy allows
- Gantt and broader queue/monitoring surfaces

### AI / Digital Twin
Owns:
- advisory insight, prediction, and recommendation
- operational twin projections
- what-if support later

## 2. Key boundary decisions

- Foundation never depends on Station Execution UI semantics.
- Quality is execution-adjacent but owns quality truth.
- Manufacturing definitions are shared assets, not traceability-only artifacts.
- Traceability must not be reduced to discrete serial-only assumptions.
- Inventory/WIP owns movement and position truth; Traceability owns genealogy and trace linkage.
- Equipment context belongs to execution and maintenance boundaries, not to user identity.
- Station Execution is a discrete-first execution application over the broader execution domain.

# Quality Domain Contracts

Status: Authoritative domain contract  
Scope: Quality domain baseline for FleziBCG MOM Platform  
Depends on:
- `../../00_platform/product-business-truth-overview.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`

This document defines the canonical domain contract for the Quality domain.

It is authoritative for:
- quality-owned domain vocabulary
- quality dimensions and domain entities
- quality action ownership intent
- quality event intent at domain level
- quality-specific invariants
- separation between current Quality Lite scope and broader future quality scope

This document is not:
- the current implementation matrix
- the UI specification
- the API transport contract
- the policy/master-data configuration file

Those belong to:
- `quality-lite-state-matrix.md`
- `quality-lite-screen-pack-canonical.md`
- `canonical-api-contract.md`
- `quality-lite-policy-and-master-data.md`

---

## 1. Purpose

The Quality domain exists to answer these questions:

1. Does quality control apply to this operation context?
2. What inspection or measurement is required?
3. How is pass/fail/hold truth decided?
4. When failure matters, who owns the next decision?
5. How does quality truth affect execution truth and accepted-good truth?

The Quality domain is built as:
- execution-adjacent
- policy-driven
- backend-authoritative
- audit-first

---

## 2. Current domain scope

### 2.1 Current implemented / design-now baseline
The current domain work is **Quality Lite**, focused on:
- operation-level QC applicability
- inspection template-driven measurement entry
- backend evaluation
- pass/fail/hold semantics
- review/disposition when hold exists
- quantity acceptance implications

### 2.2 Explicitly out of current scope
Not part of the current Quality Lite baseline:
- SPC / control chart lifecycle
- statistical sample plans
- laboratory workflow
- genealogy-heavy defect trace analysis
- CAPA workflow
- supplier quality workflow
- enterprise document control / audit system replacement

---

## 3. Domain principles

### QD-001 — Backend decides quality truth
Frontend never authoritatively determines:
- pass/fail
- hold
- accepted quantity release
- disposition effects

### QD-002 — Operator records inputs, not final quality outcome
The operator or inspection actor records:
- measurements
- observations
- inspection inputs

The backend evaluates what those inputs mean.

### QD-003 — Quality-owned decisions stay separated from operator actions
Measurement submission and disposition decision are different concerns.

### QD-004 — Quality state is orthogonal to execution state
Quality must not be modeled by mutating execution state names.
Quality uses its own dimensions and affects execution progression through policy and gating.

### QD-005 — Accepted-good truth is derived
Reported good is not automatically accepted good when a QC gate exists.

### QD-006 — Auditability is mandatory
Important quality facts must remain traceable:
- who submitted measurements
- what was submitted
- what the backend evaluated
- who decided disposition
- what quantity effect followed

---

## 4. Canonical quality domain entities

## 4.1 Inspection Template
Defines the structure of inspection/measurement input for a quality-controlled operation context.

Typical identity:
- `inspection_template_id`
- `code`
- `name`
- `version`

### Responsibility
Defines:
- what fields exist
- field type
- requiredness
- display order

It does not define final runtime state.

---

## 4.2 Inspection Template Item
A single input item inside an inspection template.

Examples:
- WIDTH
- HEIGHT
- VISUAL_OK
- TORQUE

Typical attributes:
- `item_code`
- `label`
- `input_type`
- `required`
- `unit`

---

## 4.3 Quality Rule Set
Defines how inspection values are evaluated.

Typical identity:
- `quality_rule_set_id`
- `code`
- `name`
- `version`

---

## 4.4 Quality Rule
A rule bound to one or more inspection items.

Examples:
- range check
- equality check
- boolean required true

---

## 4.5 QC Measurement Record
Represents one submitted inspection/measurement record for one operation execution context.

Typical attributes:
- `qc_measurement_record_id`
- `operation_execution_id`
- `inspection_template_id`
- `submitted_by`
- `submitted_at`

---

## 4.6 QC Measurement Value
One submitted value inside a measurement record.

Typical attributes:
- `item_code`
- typed value field(s)
- raw observation value

---

## 4.7 Quality Review Target
Represents the review/disposition target created when a quality-owned decision is required.

In Quality Lite this may be represented through a shared exception/review model rather than a standalone quality-only aggregate.

---

## 4.8 Disposition Decision
Represents the authorized decision on a quality hold/review target.

Examples:
- release hold
- accept with deviation
- require recheck
- confirm scrap

---

## 5. Canonical quality dimensions

## 5.1 Quality applicability
Whether QC applies to the operation context.

This is primarily policy-derived.

Canonical conceptual values:
- not required
- required

This does not need to be a separate persisted runtime enum in all implementations.

---

## 5.2 Quality status
Canonical runtime quality status vocabulary:

- `QC_NOT_REQUIRED`
- `QC_PENDING`
- `QC_PASSED`
- `QC_FAILED`
- `QC_HOLD`

### Meaning
- `QC_NOT_REQUIRED`: no quality gate applies
- `QC_PENDING`: quality gate applies and is not yet satisfied
- `QC_PASSED`: current quality gate is satisfied
- `QC_FAILED`: submitted/evaluated result failed but is not yet represented as hold
- `QC_HOLD`: quality hold is active and quality-owned decision path is required

---

## 5.3 Review status
Canonical review vocabulary reused across governed flows:

- `NO_REVIEW`
- `REVIEW_REQUIRED`
- `DECISION_PENDING`
- `DISPOSITION_DONE`

---

## 5.4 Quantity acceptance state
This may be represented through derived quantity fields rather than a single persisted enum.

Conceptually the domain distinguishes:
- reported good
- reported scrap / NG
- accepted good
- held/pending quantity where policy requires deferred release

---

## 6. Canonical quality event intent

These are domain event intents, not necessarily current storage names in every phase.

### Measurement / evaluation events
- `qc_measurement_submitted`
- `qc_result_recorded`
- `qc_hold_applied`

### Review / decision events
- `exception_raised`
- `disposition_decision_recorded`

### Optional derived/projection-facing event intents
- `qc_hold_released`
- `qc_recheck_requested`
- `qc_scrap_confirmed`
- `qc_accepted_with_deviation`

Implementation may derive projection-level effects from canonical decision events instead of storing all optional derived event names.

---

## 7. Canonical quality action ownership intent

### 7.1 OPR
Normal role intent:
- submit QC measurement where policy allows
- observe QC outcome
- continue only when backend allows

### 7.2 QAL / QCI
Normal role intent:
- `QAL` is the primary quality business role family
- `QCI` may exist as a specialized inspection compatibility role where needed
- review failed/held quality context
- record quality disposition decision
- own quality hold resolution path by default

### 7.3 SUP
Supervisor role intent:
- monitor
- coordinate escalation
- act only where policy explicitly grants fallback rights

### 7.4 ADM / OTS
Not default quality production actors.
Any intervention must remain governed, explicit, and auditable.

---

## 8. Canonical disposition vocabulary

Domain-approved disposition codes for Quality Lite baseline:

- `RELEASE_QC_HOLD`
- `ACCEPT_WITH_DEVIATION`
- `REQUIRE_RECHECK`
- `CONFIRM_SCRAP`

These codes are domain vocabulary, not UI labels.

---

## 9. Quality-to-execution interaction contract

### QD-INT-001 — Quality does not overwrite execution truth directly
Quality affects execution progression through:
- gating
- allowed action derivation
- quantity acceptance derivation

Not by renaming execution runtime statuses into quality-specific statuses.

### QD-INT-002 — Quality hold may block progression
When policy requires it, `QC_HOLD` blocks:
- resume
- complete
- other progression paths as defined by state matrix / policy

### QD-INT-003 — Accepted good release may be deferred
If a QC gate exists, accepted-good derivation may be deferred until:
- QC pass
- or authorized disposition

---

## 10. Current phase split: Quality Lite vs broader Quality domain

## 10.1 Quality Lite baseline
Must remain intentionally small:
- one operation context
- one inspection template
- one rule set
- one measurement submission flow
- one review/disposition path
- no advanced sampling/SPC/lab flow

## 10.2 Broader future domain
Designed later:
- SPC / limits / control charts
- multi-lot release
- genealogy-aware defect flow
- lab/test request lifecycle
- CAPA / NCR / supplier-quality workflows

---

## 11. Invariants

### QD-INV-001 — FE never decides pass/fail
### QD-INV-002 — QC status must use canonical vocabulary
### QD-INV-003 — Accepted good must never exceed reported good
### QD-INV-004 — Hold requires explicit authorized decision path
### QD-INV-005 — Same requester must not become decider where governed review applies
### QD-INV-006 — Missing required QC configuration fails closed

---

## 12. Forbidden patterns

- using dynamic DB-defined runtime status names for quality truth
- mixing operator submit and quality disposition in one command boundary
- manually editing accepted-good truth from frontend
- treating quality pass/fail as a frontend-derived display-only concept
- bypassing hold through undocumented backend shortcut
- letting admin/support become normal shopfloor quality actors by default

---

## 13. Extension rules

Future quality features must:
- reuse canonical quality status vocabulary where still valid
- add orthogonal dimensions rather than overload existing state names
- preserve event/audit truth
- keep backend authoritative
- remain compatible with execution truth and governance rules

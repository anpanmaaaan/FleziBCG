# Manufacturing-Mode Hierarchy Mapping

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v1.0 | Added hierarchy mapping note to support manufacturing-mode-neutral platform language. |
| 2026-04-23 | v1.1 | Added formal ISA-95-aligned mapping guideline and type-driven interpretation note. |
| 2026-05-04 | v1.2 | Added tenant default vs plant/scope manufacturing profile resolution and change-governance rules. |

Status: Canonical platform mapping note.

## 1. Purpose

This document explains how the canonical hierarchy:
- tenant
- plant
- area
- line
- station
- equipment

remains compatible with:
- discrete
- batch
- continuous
- hybrid manufacturing

## 2. Principle

The canonical hierarchy is stable.
Plant-specific semantics may be mapped onto it through:
- equipment/resource typing
- level aliases
- app-specific labels
- explicit `level_type` or equivalent classification metadata

This keeps backend scope/governance stable while allowing plant-model flexibility.

## 2.1 Manufacturing profile resolution

Manufacturing mode is resolved through configuration, not through a product fork.

Tenant-level configuration may provide default behavior and enabled capabilities, but it must not permanently classify the whole tenant as only discrete, batch, process, or continuous.

Resolution order:

1. tenant default manufacturing profile
2. plant manufacturing profile
3. area / line / station / equipment override where applicable
4. manufacturing definition type
5. backend runtime execution profile

This allows one tenant to operate a hybrid manufacturing footprint, such as:
- discrete final assembly
- batch material preparation
- process-oriented paint or coating
- continuous or semi-continuous equipment runs

## 3. Examples

### Discrete
- line = production line
- station = workstation/cell
- equipment = machine/tooling asset

### Batch / process
- line may map to process train or production train
- station may map to process cell, unit, vessel group, or operator-facing work context
- equipment may map to reactor, mixer, tank, filler, utility asset, or instrumented equipment

### Continuous
- line may map to continuous production line / train
- station may act as an operator-facing control/work context alias
- equipment may map to process unit or equipment asset

## 4. Formal mapping guideline

The canonical hierarchy is intentionally product-stable, but its operational meaning may be interpreted through ISA-95-aligned level semantics.

### Typical interpretation
- `line` **typically maps to** a work-center-like production grouping
  - examples: production line, process train, packaging train, campaign train
- `station` **typically maps to** a work-unit-like or operator-facing execution context
  - examples: workstation, work cell, process cell, unit, filling point, manual work context
- `equipment` represents the concrete asset or equipment instance participating in execution
  - examples: machine, vessel, reactor, mixer, filler, utility asset, instrumented equipment

### Important note
This is a **default mapping guideline**, not a rigid one-to-one ontology.
Different plant models may interpret:
- `line` closer to a work center / production grouping
- `station` closer to a work unit / process cell / execution point
- `equipment` as the concrete asset instance beneath that context

The key design rule is:
- keep the canonical hierarchy stable for governance, scope, and product consistency
- use typing, aliasing, and plant-model semantics to preserve manufacturing-mode neutrality

## 5. Rule

Do not treat `line` and `station` as exclusively discrete-manufacturing vocabulary.
Treat them as canonical hierarchy anchors whose user-facing meaning may be adapted by plant model.


## 6. Configuration ownership rules

### Tenant level

Tenant configuration owns:
- default manufacturing profile
- enabled manufacturing capabilities
- default hierarchy aliases
- default governance / audit posture
- onboarding templates

Tenant configuration does not own:
- final execution behavior for every plant
- irreversible classification of all operations as discrete or process
- runtime allowed actions
- execution state truth

### Plant level

Plant configuration owns the primary manufacturing mode for a plant.

Examples:
- automotive final assembly plant: `DISCRETE`
- paint / coating plant: `PROCESS` or `HYBRID`
- battery mixing plant: `BATCH`
- multi-area automotive plant: `HYBRID`

### Area / line / station / equipment level

Lower scope levels may override or refine the plant profile where the physical or operational model differs.

Example:
- plant = `HYBRID`
- final assembly area = `DISCRETE`
- paint shop area = `PROCESS`
- battery mixing area = `BATCH`

### Manufacturing definition level

Manufacturing definitions influence execution behavior.

Examples:
- MBOM + routing → routing-operation execution
- formula + recipe → batch/process execution
- procedure + phase → phase execution
- continuous run definition → continuous monitoring/execution context

### Runtime level

Backend runtime profile determines:
- allowed commands
- required context
- state transitions
- event types
- validation rules
- audit requirements

Frontend may render the appropriate workflow, but it must not decide manufacturing truth or execution truth.

## 7. Change policy

Before execution data exists, manufacturing profile configuration may be changed through normal governed admin configuration.

After execution data exists, manufacturing profile changes must be treated as governed changes because they may affect:
- production orders
- execution events
- quantity reports
- quality records
- material / lot genealogy
- reporting projections
- audit interpretation

A scope with existing execution history must not be freely changed from one manufacturing mode to another without:
- explicit authorization
- audit record
- migration or compatibility assessment
- clear effective date/versioning rule where required

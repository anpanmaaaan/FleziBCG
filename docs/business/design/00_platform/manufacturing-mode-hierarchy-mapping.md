# Manufacturing-Mode Hierarchy Mapping

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v1.0 | Added hierarchy mapping note to support manufacturing-mode-neutral platform language. |
| 2026-04-23 | v1.1 | Added formal ISA-95-aligned mapping guideline and type-driven interpretation note. |

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

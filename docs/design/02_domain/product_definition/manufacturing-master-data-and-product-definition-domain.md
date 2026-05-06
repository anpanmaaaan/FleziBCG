# Manufacturing Master Data and Product Definition Domain

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v1.0 | Added canonical domain overview for shared manufacturing definitions. |
| 2026-05-04 | v1.1 | Clarified manufacturing definition role in discrete, batch, process, continuous, and hybrid execution behavior. |

Status: Canonical domain overview.

## 1. Purpose

This domain owns the manufacturing definitions consumed by multiple FleziBCG modules.

## 2. Scope

It includes:
- product structure
- BOM
- routing
- recipe / formula / procedure / phase-ready definitions
- product/resource requirements
- versioned manufacturing definitions

## 2.1 Manufacturing-mode relevance

Manufacturing Master Data and Product Definition is the canonical domain for definitions that influence manufacturing-mode behavior.

Discrete manufacturing typically uses:
- product structure
- manufacturing BOM
- routing
- routing operation
- resource / station / equipment requirements

Batch or process manufacturing may use:
- formula
- recipe
- procedure
- phase-ready definitions
- material / lot transformation context
- equipment unit or process context

Continuous manufacturing may use:
- continuous run definition
- equipment / line context
- process segment context
- quantity or flow-based measurement context

The domain must remain compatible with `DISCRETE`, `BATCH`, `CONTINUOUS`, and `HYBRID` manufacturing modes.

## 3. Boundary note

This domain is intentionally separate from:
- Traceability (which owns genealogy/trace linkage)
- Inventory/WIP (which owns movement and position truth)
- Execution (which owns runtime operational mutation)

## 3.1 Explicit non-goals for current phase

The current roadmap remains automotive discrete-first.

This document does not imply current-phase implementation of:
- full ISA-88 recipe execution
- Unit Procedure model
- Equipment Module / Control Module model
- phase state machine
- batch campaign management
- continuous process orchestration

Those capabilities are future extensions unless explicitly pulled forward by customer scope.

## 4. Why it exists

Without this domain, BOM/recipe truth tends to get trapped inside downstream modules such as traceability or planning, which creates duplication and drift.

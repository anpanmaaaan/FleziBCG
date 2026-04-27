# Manufacturing Master Data and Product Definition Domain

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v1.0 | Added canonical domain overview for shared manufacturing definitions. |

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

## 3. Boundary note

This domain is intentionally separate from:
- Traceability (which owns genealogy/trace linkage)
- Inventory/WIP (which owns movement and position truth)
- Execution (which owns runtime operational mutation)

## 4. Why it exists

Without this domain, BOM/recipe truth tends to get trapped inside downstream modules such as traceability or planning, which creates duplication and drift.

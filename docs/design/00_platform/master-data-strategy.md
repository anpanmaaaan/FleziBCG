# Master Data Strategy

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Expanded master-data scope for operator, equipment, material, and manufacturing modes. |

Status: Canonical master-data strategy note.

## 1. Master-data families

- tenant/plant hierarchy
- users and access configuration
- operators and workforce-facing production identity
- equipment/resource master
- material/product/lot-related master
- downtime reason master
- quality template/rule master
- manufacturing mode and process configuration

## 2. Execution-related master-data rule

Target execution behavior must draw on backend master data for:
- operator lookup and eligibility
- equipment eligibility at station/resource context
- downtime reasons
- quality applicability and rule sets
- material/lot configuration later

## 3. Enum vs master-data stance

Use code-first enums for small, locked, platform-wide vocabularies.
Use backend-governed master data for site/plant/domain-controlled semantics.

## 4. Important warning

Do not let frontend hardcode execution, quality, or downtime semantics that belong to backend master data.

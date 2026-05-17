---
name: design-system-enforcer
description: Enforces FleziBCG DESIGN.md for UI generation and frontend implementation.
---

# Design System Enforcer

## Required Reading
1. DESIGN.md
2. docs/design/DESIGN.md if root unavailable
3. docs/audit/frontend-source-alignment-snapshot.md if present
4. relevant UI/screen inventory docs

## Reject UI if
- frontend becomes source of business truth
- permission truth hardcoded in UI
- execution state derived in UI
- quality pass/fail faked
- ERP posting faked
- backflush faked
- AI shown as deterministic authority
- status colors inconsistent
- operator usability ignored

## Required UI Output
1. screen purpose
2. primary user
3. layout structure
4. component list
5. status behavior
6. empty/loading/error states
7. backend dependency
8. mock vs real data declaration
9. accessibility/touch considerations

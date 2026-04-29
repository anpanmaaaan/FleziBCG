---
name: design-system-enforcer
description: Enforces FleziBCG DESIGN.md for UI generation and frontend implementation.
---

# Design System Enforcer

## Required Reading

1. `DESIGN.md`
2. `docs/design/DESIGN.md` if root file is unavailable
3. `docs/audit/frontend-source-alignment-snapshot.md` if present
4. relevant UI/screen inventory docs

## Reject UI if

- frontend becomes source of business truth
- permission truth is hardcoded in UI
- execution state is derived in UI
- quality pass/fail is faked
- ERP posting is faked
- backflush is faked
- AI is shown as deterministic authority
- status colors are inconsistent
- operator usability is ignored

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

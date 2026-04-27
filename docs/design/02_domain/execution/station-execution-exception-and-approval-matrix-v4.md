# Station Execution Exception and Approval Matrix

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Clarified that exception/disposition remains deferred but must fit the new ownership model. |

Status: Canonical target policy note; not current executable backend behavior.

## 1. Current truth

Station-specific exception and disposition lifecycle is still deferred from the current execution core.

## 2. Alignment rule for future implementation

When exception/disposition is later implemented:
- it must not reintroduce claim-centric ownership
- it must attach to the effective execution session / operator / resource context as needed
- it must preserve approval and SoD rules
- it must remain quality/review-orthogonal rather than overloading execution state names

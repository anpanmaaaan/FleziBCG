# Frontend–Backend Responsibility Map

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Added session/operator/equipment responsibility clarity. |

Status: FE/BE responsibility note.

## Backend owns
- execution truth
- status truth
- session validity
- effective operator/resource resolution
- authz and approval truth
- audit truth

## Frontend owns
- visibility and navigation
- input collection for operator identification / equipment selection
- display composition
- i18n

## Forbidden FE patterns
- deriving execution legality from visible state text alone
- inventing claim/ownership semantics locally
- treating operator/equipment selection as final truth without backend confirmation

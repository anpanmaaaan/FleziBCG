# Migration and Versioning Strategy

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Added transition strategy for claim deprecation and session introduction. |

Status: Migration/versioning note.

## Main rule

The move from claim-centric execution to session-owned execution is an Architecture / Contract migration.

## Preferred sequence
1. lock docs/design truth
2. add station session/operator/equipment foundations
3. cut execution guards to session ownership
4. simplify UI away from claim
5. remove remaining claim compatibility debt

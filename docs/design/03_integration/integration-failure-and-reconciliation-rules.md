# Integration Failure and Reconciliation Rules

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Minor strengthening of reconciliation principles. |

Status: Integration failure/reconciliation note.

## Rules

- external failures must not silently corrupt internal execution truth
- reconciliations must be auditable
- replay/retry behavior must be explicit for command-like adapters
- external interface lag must not push frontend into inventing business truth locally

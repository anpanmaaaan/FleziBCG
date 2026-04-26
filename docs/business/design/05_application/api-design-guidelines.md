# API Design Guidelines

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Added execution-session and compatibility guidance. |

Status: API design guideline note.

## Guidelines
- keep routes thin and business logic in services
- prefer explicit command-style mutation routes for governed actions
- use machine-readable error codes
- document idempotency and concurrency where relevant
- when deprecating claim-centric routes, provide a clear migration note rather than silent behavior drift

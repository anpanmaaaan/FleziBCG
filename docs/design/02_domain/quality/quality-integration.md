# Quality Integration Rules

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Expanded minimal rule note into integration guidance. |

Status: Quality-to-execution integration note.

## 1. Core integration rules

- Quality is a sub-process of execution, not a separate truth for runtime ownership.
- Quality check may be allowed only when execution context is in a policy-allowed state.
- Execution completion may require quality satisfaction or authorized disposition depending policy.
- Accepted-good derivation may be deferred until QC pass or disposition.

## 2. Ownership rule

Execution remains session-owned.
Quality submission/disposition must respect the effective execution and governance context but must not redefine execution ownership primitives.

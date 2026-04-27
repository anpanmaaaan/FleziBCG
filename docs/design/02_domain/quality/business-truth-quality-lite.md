# Business Truth — Quality Lite

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Replaced placeholder with minimal business-truth baseline. |

Status: Authoritative Quality Lite business-truth note.

## 1. Scope now

Quality Lite currently focuses on:
- operation-context QC applicability
- template-driven measurement submission
- backend evaluation
- pass/fail/hold semantics
- disposition-driven release where policy requires it

## 2. Core rules

- frontend does not decide pass/fail
- quality state is orthogonal to execution state
- accepted good may differ from reported good when QC gating exists
- hold requires explicit authorized resolution path

## 3. Execution interaction

Quality must integrate with execution through allowed-actions and derived quantity effects.
Quality does not replace execution ownership semantics.

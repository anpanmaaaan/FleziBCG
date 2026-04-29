---
name: qa-e2e-layer
description: QA and E2E testing layer for FleziBCG. Simulates real user/operator behavior, edge cases, regression risks, and release verification.
---

# QA / E2E Layer

## Use When

- writing test cases
- E2E tests
- regression tests
- release verification
- “try to break this” reviews

## Generic simulations

- duplicate submit
- refresh mid-flow
- network loss
- stale UI/cache
- concurrent action
- wrong role/scope
- invalid state/data
- partial backend failure
- retry after timeout

## MOM simulations

- stale tablet UI
- wrong station
- wrong operator/session
- concurrent operators
- pause/resume misuse
- duplicate production report
- complete without conditions
- event/projection mismatch
- tenant leakage across plant/scope

## Hard Mode QA Requirements

For MOM/governance actions, QA must validate:

- required event emitted
- event payload correct
- invariant enforced
- invalid scenario rejected
- tenant/scope violation rejected
- permission violation rejected
- duplicate request safe/rejected
- projection/read model consistent

## Test output format

```markdown
## Test objective
## Business scenario
## Actor/persona
## Preconditions
## Test data
## Steps
## Expected backend/system state
## Expected UI/API behavior
## Negative/edge cases
## Regression risk
## Automation priority
```

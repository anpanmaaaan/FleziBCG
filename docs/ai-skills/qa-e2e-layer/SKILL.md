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

## Assertion Failure Discipline

QA scripts, screenshot harnesses, and E2E checks must fail hard when required
assertions fail.

Allowed:

- Playwright/test assertions that fail the test;
- `throw new Error(...)`;
- returning a rejected promise;
- collecting failures and exiting non-zero after printing a failure summary.

Forbidden:

- only setting `process.exitCode = 1` while continuing to save artifacts and
  print pass-like output;
- reporting a command as PASS when stdout/stderr contains assertion failures;
- treating screenshot capture as validation when the target-state assertions
  failed;
- claiming E2E/user-flow coverage from visual mocks only.

If a command exits 0 but assertion failures are printed, report the verification
as failed and fix the harness before claiming pass.

## Visual QA Evidence Rules

For frontend screenshot QA:

- assert the target state is reached before screenshot;
- assert important negative conditions when removing/replacing UI;
- assert the business state claimed in the report, not only generic badges,
  route presence, or screen status labels;
- make the screenshot show the changed area, scrolling or taking an additional
  focused screenshot if needed;
- list only current-run screenshots in the report;
- state whether screenshots use mocked API data or real backend data.

For Station Execution, Station Session, operator, equipment, quality, material,
or other MES workflow screenshots, include assertions for the actual business
state under review. Examples:

- open session shows the session as `Open` and exposes `End session`, not the
  `Open session` action;
- blocked or hold state shows the blocker/hold surface and does not expose the
  blocked progression CTA as enabled;
- ready-to-queue state only enables the queue/progression CTA when the required
  station, session, operator, and equipment readiness conditions are satisfied;
- quality pass/fail/hold screenshots assert the displayed status and the allowed
  next action.

If the harness only checks a `CONNECTED` badge, route load, or absence of a
`PARTIAL` badge, report it as smoke coverage only. Do not claim it validates the
business state.

## Coverage Class Rules

- `service`: direct service/domain/repository call; no HTTP/auth boundary.
- `API`: HTTP endpoint plus status/error mapping and auth dependency behavior.
- `frontend`: route/component/API-client/i18n behavior without full user-flow.
- `E2E`: realistic user flow crossing frontend and backend/API boundary.

Do not call a test E2E unless it crosses the frontend/API boundary. Do not call a
test API/RBAC coverage unless endpoint/auth dependencies are exercised.

## DB Fixture Hygiene

For DB-backed automated tests:

- seed deterministic minimum data;
- purge before and after each test when writing persistent rows;
- call rollback before teardown purge;
- delete child rows before parent rows;
- verify cleanup by rerunning the same test file twice;
- treat unique prefixes as collision avoidance only, not cleanup.

## Test output format

```markdown
## Test objective
## Coverage class
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
## Assertion failure behavior
## Screenshot / artifact evidence
## Not covered
## Report export
- Canonical report file: docs/agent-reports/latest-agent-report.md
- Written before completion: yes/no
```

For non-trivial QA/test tasks, overwrite
`docs/agent-reports/latest-agent-report.md` with the final test report before
marking done.

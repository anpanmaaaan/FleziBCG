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
- login or list/queue landing auto-selects the first operation, hold, work
  order, production order, material, WIP item, or dispatch item without explicit
  user intent

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
- scope selectors to the panel, dialog, row, or region under test when labels
  are duplicated on the page;
- after clicking an action, assert the intended side effect: target network
  request, state text, alert, modal close/open, enabled/disabled transition, or
  URL change. Do not rely on the click completing without proving the state
  changed.
- regenerate screenshots after the final UI/source edit. Artifact timestamps
  must be newer than the touched UI files they are used to verify;
- make the screenshot show the changed area, scrolling or taking an additional
  focused screenshot if needed;
- list only current-run screenshots in the report;
- state whether screenshots use mocked API data or real backend data.
- treat harness scripts/specs/mocks as source/test files. They are not generated
  artifacts; include them in files intended for commit when they are added or
  updated to reproduce the evidence.

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

## Navigation Intent Regression Requirements

For any route, list, queue, selected-entity, detail, cockpit, or action-entry
change, QA must test the navigation intent invariant:

- default role landing does not auto-enter a detail/cockpit/action surface;
- list/queue routes do not auto-select the first item on initial load;
- initial load does not mutate the URL with an entity id from the first item;
- explicit row/queue click or explicit deep link still enters the target detail
  or cockpit;
- backend active-context auto-resume is tested separately from the "items exist"
  case and must prove ownership/session context.

Minimum cross-feature matrix when practical:

- OPR login to Station Execution: no implicit first operation selection;
- SUP/PMG operations list: no implicit operation detail;
- QC quality hold list: no implicit first hold resolution;
- Production Orders / Work Orders: no implicit first order/work order detail;
- Material/WIP/Dispatch: no implicit first item action panel.

Screenshot-only mocks are acceptable as frontend regression evidence only if
they assert URL, selected state, and absence of cockpit/action UI. They are not
backend E2E proof unless the flow crosses a real API/backend boundary.

Report the source-search evidence behind the navigation claim. If any touched
route/list/queue/detail/cockpit/action file still contains `items[0]`,
`data.items[0]`, `queueItems[0]`, `preferred ??`, `setSearchParams`,
`navigate(`, or route-param setter hits, classify them as `yes - existing` or
`yes - introduced`. Do not report `no` unless the search output supports it.

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
## Navigation intent evidence (if routing/list/queue/detail/action is touched)
- Screen intent:
- Default route selected entity:
- URL entity id after initial load:
- Explicit selection/deep-link check:
- Backend active-context exception check:
## Not covered
## Report export
- Canonical report file: docs/agent-reports/latest-agent-report.md
- Written before completion: yes/no
```

For non-trivial QA/test tasks, overwrite
`docs/agent-reports/latest-agent-report.md` with the final test report before
marking done.

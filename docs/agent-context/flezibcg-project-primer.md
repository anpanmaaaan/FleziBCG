# FleziBCG Project Primer For Coding Agents

Status: active orientation document for implementation agents.

Purpose: give agents enough product and architecture context to code safely before
they dive into detailed design docs. This file does not replace authoritative
domain contracts. When this file conflicts with a more specific design or
governance document, stop and reconcile instead of guessing.

## Product Direction

FleziBCG is a manufacturing operations product, not a generic dashboard.

The current pilot path is a discrete MES/MOM execution flow:

1. Seeded user logs in.
2. Operator prepares station context.
3. Operator opens a station session.
4. Operator identifies themselves.
5. Operator binds equipment when required.
6. Operator views a station queue.
7. Operator explicitly selects or deep-links to an operation.
8. Operator starts, pauses/resumes, reports quantity, starts/ends downtime, and completes operation using backend-allowed actions.
9. Quality gates and holds block completion when backend rules require it.
10. Supervisor/QA views or resolves operational truth from backend APIs.

The long-term product must support both:

- `DISCRETE` manufacturing execution; and
- future `BATCH_PROCESS` execution.

The active runtime is discrete-first. Do not build fake batch runtime, recipe
runtime, ISA-88 phase execution, weighing/dispensing, eBR, APS, AI advisor,
digital twin, or ERP posting unless the task explicitly asks for that stage.
Use generic naming where practical so discrete-first does not become
discrete-only.

## Source Of Truth Rules

Backend truth wins.

- Frontend does not decide authorization.
- Frontend does not invent allowed actions.
- Frontend does not fake execution state, quality pass/fail, ERP posting, backflush, or deterministic AI decisions.
- Frontend route/persona behavior is UX only. Backend remains authorization truth.
- Execution commands must be auditable backend facts/events where the backend supports events.
- Missing `allowed_actions` means no client command affordance.

When documents disagree, use this order:

1. Specific design/business truth under `docs/design/**`.
2. `docs/governance/CODING_RULES.md`.
3. `docs/governance/ENGINEERING_DECISIONS.md`.
4. `docs/governance/SOURCE_STRUCTURE.md`.
5. Active task prompt.
6. Inline comments.

Do not average conflicting docs. Stop and report the conflict.

## MES Operator UX Rules

Station/operator screens are work surfaces, not admin explainers.

- Keep the first screen operational and task-focused.
- Do not expose internal implementation stage labels such as STX rails to operators unless a task explicitly asks for diagnostic UI.
- Do not add large marketing/hero sections to shopfloor screens.
- Do not use cards inside cards for core operator workflow.
- Prefer compact context, clear next action, and large touch targets for operator actions.
- Status must explain what the operator can do next, not just display internal state.

Navigation intent is a hard product rule:

- `LANDING`, `LIST`, and `QUEUE` routes must not auto-select the first item.
- Do not mutate URL params from `items[0]`, `data.items[0]`, or `queueItems[0]`.
- Enter `DETAIL`, `COCKPIT`, or `ACTION` only from explicit deep link, explicit user selection/scan/typed id, or backend-confirmed active owned context.
- If backend active context is used, add `NAV_INTENT_EXCEPTION:` near the code and name the backend field proving ownership.

## Station Execution Current Direction

Current Station Execution direction:

- `/station` default is a queue/selection landing, not an implicit cockpit.
- `/station?operationId=...` is an explicit deep link to cockpit/detail.
- Queue row click is explicit operator selection.
- `AllowedActionZone` renders backend `operation.allowed_actions`, then applies session ownership and closure gates.
- Action hierarchy may reorder which backend-allowed action is primary, but must not add actions that backend did not allow.
- Paused and downtime states should make recovery action obvious:
  - PAUSED without open downtime: primary `resume_execution` when backend allows it.
  - BLOCKED or `downtime_open`: primary `end_downtime` when backend allows it.
- Reporting is secondary/disabled guidance when interrupted and backend does not allow `report_production`.

## Quality And Pilot Scope

Pilot-critical flows are execution, station session, operator/equipment context,
quantity reporting, downtime, completion, quality gates, and supervisor/QA
visibility.

Do not prioritize:

- AI insight screens;
- digital twin screens;
- APS scheduling;
- ERP integration;
- compliance/e-signature/eBR;
- full material backflush;
- batch/process runtime.

These can be designed later, but pilot execution and quality must be stable
first.

## Evidence Expectations

A passing build is not enough.

For frontend workflow changes, provide:

- screenshot harness evidence for changed states;
- business-state assertions, not only "screen loaded" or badge existence;
- negative assertions for forbidden actions or mock data when relevant;
- route/navigation assertions for landing/list/queue changes;
- `screenStatus.ts` updates when connection status changes.

For backend/API changes, provide:

- targeted tests at the correct coverage class;
- tenant isolation and RBAC checks when touched;
- event/audit behavior where applicable;
- blocked-path tests for fail-closed behavior.

Reports must classify coverage honestly:

- `service`: direct service/repository/domain tests;
- `API`: HTTP endpoint/auth dependency tests;
- `frontend`: route/component/API-client/i18n/screenshot behavior;
- `E2E`: user flow crossing frontend and backend/API boundary.

Do not claim API, RBAC, E2E, or pilot golden path from service-only or mocked
frontend tests.

## Worktree And Artifact Rules

- Do not stage, commit, push, switch branches, or edit history unless the active task explicitly asks.
- Never use `git add .`.
- Screenshots/videos under `docs/audit/**` are review artifacts, not commit payload, unless explicitly requested.
- Harness scripts/specs used to reproduce evidence are source/test files and may be commit payload.
- `docs/agent-reports/latest-agent-report.md` is the fixed report path.
- Every dirty file in `git status --short` must be classified as in-scope, parent/existing, artifact, or out-of-scope.

## Before Coding Checklist

Before implementation, the agent must be able to answer:

- What exact slice id and goal did the latest user prompt request?
- Which business truth file governs this slice?
- Which backend API/service owns the truth?
- Which frontend files are only UX around backend truth?
- What must not be built in this slice?
- What screenshots/tests will prove the exact business state?
- What dirty files are unrelated and must not be included?

If any answer is unclear, stop and report instead of guessing.

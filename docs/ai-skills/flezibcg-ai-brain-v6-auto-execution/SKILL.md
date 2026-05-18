---
name: flezibcg-ai-brain-v6-auto-execution
description: Main auto-routing engineering brain for FleziBCG. Selects Generic/MOM brain, adaptive mode, and Hard Mode v3 when needed.
---

# FleziBCG AI Brain v6 — Auto-Execution

## Purpose

This skill automatically selects:

1. Brain:
   - Generic Brain
   - MOM Brain

2. Mode:
   - Fast
   - Strict
   - QA
   - Architecture
   - Product
   - Refactor
   - Debug/Triage
   - Release

3. Enforcement:
   - Hard Mode MOM v3 for autonomous/risky MOM implementation
   - Hard Mode MOM v2 for focused review

## Required Output

For every non-trivial task:

```markdown
## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Selected skills read:
- Coverage class: service | API | frontend | E2E | docs-only
- Hard Mode kept from parent slice: yes/no
- Reason:
```

## Brain Selection

### Use MOM Brain if task touches

- MOM / MES / manufacturing
- station / line / plant / area / equipment
- operator / station session
- production order / work order / operation
- execution / downtime / quantity reporting
- quality hold affecting execution
- material / WIP / traceability / backflush
- manufacturing ERP integration
- OEE / shopfloor / Andon / APS / operational Digital Twin
- IAM/scope/audit foundation for FleziBCG

If ambiguous in the FleziBCG repo, prefer MOM Brain.

### Use Generic Brain if

Task is general software engineering and does not touch MOM-specific logic.

## Mode Selection

### Fast Mode

Small low-risk edits only: copy, formatting, low-risk docs.

Never use for DB/auth/permission/state/workflow/event/data-integrity/migration/integration/production behavior.

### Strict Mode

Use for DB, schema, migration, auth, permission, access control, workflow, state, data integrity, events, integration contracts, concurrency, idempotency, or production-facing behavior.

### QA Mode

Use for test cases, E2E, regression, release verification, user-flow validation, or “try to break this”.

### Architecture Mode

Use for system design, module boundaries, source structure, API/data contract, technology choices, or integration boundary.

### Product Mode

Use for unclear requirements, MVP slicing, roadmap, scope decision, or “should we build this?”.

### Refactor Mode

Use for restructuring without intentional behavior change.

### Debug/Triage Mode

Use for bugs, failing tests, logs, unexpected behavior, or incident-style analysis.

### Release Mode

Use for final readiness, rollout, rollback, migration release, changelog, and go/no-go.


### UI / UX Mode Add-on

If the task touches frontend UI, UX, React, Tailwind, screen packs, Figma Make, Google Stitch, or `DESIGN.md`, also invoke:

```text
docs/ai-skills/design-md-ui-governor/SKILL.md
```

This add-on is compatible with both Generic Brain and MOM Brain.

If UI work touches execution state, station/session/operator/equipment, quality hold, material impact, allowed actions, tenant/scope/auth, or governed actions, Hard Mode MOM v3 still applies.

Do not let UI implementation fake backend truth, authorization truth, execution state, quality result, ERP posting, backflush completion, or AI deterministic decisions.

## Hard Mode Selection

Use Hard Mode MOM v3 if:

- autonomous implementation
- risky MOM/governance slice
- task touches state/event/invariant/tenant/auth/execution
- agent is expected to code and test

### Routing Lock

If the parent/original slice required Hard Mode MOM v3, every follow-up bugfix,
test repair, fixture repair, review, or verification pass on the same slice keeps
Hard Mode MOM v3 unless the change is purely text/comment-only and cannot affect
tests, DB state, runtime behavior, contracts, or reports.

Station, station session, station execution, operator identification, equipment
binding, execution cockpit, quality gate, report-honesty, screenshot harness, and
UI readiness follow-ups keep MOM Brain + Hard Mode MOM v3 when they continue a
Hard Mode slice. Do not mark Hard Mode `N/A` just because the current edit is
frontend, cleanup, prop wiring, screenshot evidence, or report correction.

Only mark Hard Mode `N/A` for a follow-up when the diff is truly docs/text-only
and cannot affect runtime behavior, tests, reports, harnesses, command results,
state, contracts, or UI progression.

Test fixture changes touching DB cleanup, tenant data, execution, quality, auth,
state, events, projections, or governed workflows remain MOM Brain + Hard Mode
MOM v3. Do not silently downgrade these follow-ups to Fast or ordinary Strict
Mode.

Use Hard Mode MOM v2 if:

- reviewing a small PR
- manually checking existing implementation
- no new behavior coding is requested

## Coverage Claim Discipline

Report only the coverage actually proven:

- `service`: direct service/repository/domain function tests only.
- `API`: endpoint tests, HTTP status/error mapping, and auth dependency behavior.
- `frontend`: rendered UI, route, component, API-client, or i18n behavior.
- `E2E`: user-flow coverage through frontend + backend/API boundary.
- `docs-only`: documentation, prompt, skill, or planning changes.

Service-level tests must not be reported as API, RBAC, E2E, or full pilot golden
path coverage. API/RBAC coverage can only be claimed when endpoint/auth
dependency tests run. E2E or pilot golden path coverage can only be claimed when
the validation crosses the frontend/API/user-flow boundary.

Every implementation or review report must include:

```markdown
## Selected skills read
...

## Coverage class
service | API | frontend | E2E | docs-only

## Hard Mode kept from parent slice
yes/no

## Limitations / not covered
...
```

## Public Reasoning Discipline

Before implementation, produce a short public reasoning packet. Do not expose raw
chain-of-thought; summarize the decision basis in concrete engineering terms:

```markdown
## Work Packet
- User goal:
- Slice boundary:
- Files expected to change:
- Files intentionally not changed:
- Source-of-truth docs/code read:
- Current evidence:
- Main risks:
- Validation plan:
- Stop conditions:
```

If evidence contradicts the original assumption, stop and re-route before
editing. Do not continue coding under a stale hypothesis.

## Evidence Gate And Report Honesty

The final report is not evidence by itself. Evidence is the combination of:

- the actual diff;
- tracked and untracked file state;
- command exit codes;
- assertion logs;
- screenshots or artifacts when UI is involved;
- tests that exercise the claimed boundary.

Before declaring completion, run a self-review and include the result in
`docs/agent-reports/latest-agent-report.md`:

```markdown
## Evidence Self-Review
- `git status --short` checked:
- Expected files changed:
- Unexpected files changed:
- OUT OF SCOPE dirty files:
- Required new files tracked or explicitly reported as untracked:
- Acceptance criteria mapped to diff/tests/screenshots:
- Report claims match actual diff:
- Commands failed, skipped, or not trusted:
```

Rules:

- Do not claim a file/component/harness is implemented unless it is present in
  the actual diff or tracked workspace state.
- Do not claim a command passed unless the command exited 0 and no assertion
  failure was printed.
- A non-zero exit code is a failed verification. If failures are baseline, write
  `FAIL - baseline failures` and classify baseline vs introduced/fixed errors;
  never write PASS for that command.
- If `git diff --check` reports any issue, the diff check failed and the slice is
  not clean until fixed or explicitly reported as blocked.
- Do not treat screenshots as valid evidence unless they show the target state
  named in the report.
- Do not reuse stale screenshots as proof of a new change.
- If `git status --short` shows untracked implementation files, the report must
  name them and say whether they are intentionally untracked or must be added.
- If `git status --short` shows any out-of-scope modified, staged, deleted, or
  untracked file, the report must list it as `OUT OF SCOPE`. Do not write
  "not touched" or "intentionally not changed" for a file that is dirty.
- If a required verification cannot run, mark the slice incomplete or blocked;
  do not silently replace it with a weaker check.

## Dirty Worktree Gate

Before marking a task complete, run `git status --short` and classify every dirty
path:

- `IN SCOPE`: changed by this slice and intended to be reviewed with it.
- `OUT OF SCOPE`: pre-existing or unrelated dirty path that must not be claimed
  as this slice's work.

If any dirty path is `OUT OF SCOPE`, keep it out of `Files intended for commit`
and name it in the report. If any unrelated file is staged, report a blocker
until it is unstaged or explicitly authorized.

## Artifact Policy Gate

Generated UI evidence is required for UI work, but generated binary artifacts
are not automatically commit payload.

Required behavior:

- Save UI screenshots or videos under `docs/audit/**` for reviewer inspection.
- Report them under `Generated artifact paths`.
- Report code/docs/test files separately under `Files intended for commit`.
- Do not stage or commit PNG, JPG, JPEG, GIF, WebP, MP4, or WebM artifacts under
  `docs/audit/**` unless the prompt explicitly says to commit generated
  artifacts.
- If such artifacts are already tracked, staged, or committed contrary to the
  task policy, report a blocker and do not claim a clean pass.
- Do not present artifact generation as E2E/API/backend proof unless the command
  actually exercised that boundary.

## Assertion Failure Discipline

Verification scripts must fail hard when a required assertion fails.

Required pattern:

- throw an error, reject the test, or otherwise exit non-zero immediately;
- print the failed assertion and the state/viewport/input that failed;
- do not continue to a final "PASS" summary after a required assertion failed.

Forbidden pattern:

- only setting `process.exitCode = 1` while continuing to save screenshots and
  print pass-like summaries;
- reporting a script as PASS when assertion failures appear anywhere in stdout
  or stderr;
- counting visual screenshot capture as successful validation when state
  assertions failed.

## Git Operation Policy

Do not run `git add`, `git commit`, `git push`, branch changes, or history edits
unless the user or task prompt explicitly asks for that git operation.

Default behavior for implementation agents:

- edit files;
- run verification;
- write `docs/agent-reports/latest-agent-report.md`;
- leave changes unstaged for review.

If a git operation was accidentally performed before review, the report must
say so, include the commit hash if any, and treat the slice as needing reviewer
approval before further work.

If staging or committing is explicitly requested:

- Never use `git add .`.
- Stage only explicit paths that belong to the requested commit.
- Run `git diff --cached --stat` and include the output summary in the report.
- Run `git diff --cached --name-status` and include the output summary in the
  report.
- Include `No unrelated staged files: yes/no`.
- If unrelated staged files exist, stop and report a blocker before committing.

## Coding Quality Discipline

For every code-changing task:

- Inspect existing patterns before adding new helpers, abstractions, or fixtures.
- Prefer the smallest behavior-preserving edit that satisfies the slice.
- Keep refactors separate from behavior changes unless the refactor is required
  for the requested behavior.
- Treat test code as production-maintained code: deterministic data, explicit
  cleanup, clear assertions, and no hidden dependency on previous runs.
- For DB-backed tests, cleanup must not rely on unique prefixes alone. Use
  rollback plus purge before and after the test when persistent rows are created.
- If a validation command uses a container, confirm whether the container sees
  live workspace source. If the compose image is baked, bind-mount the live
  source or rebuild before trusting the result.
- If command output is truncated/noisy, capture a reliable exit code or log
  before reporting pass/fail.
- Before final report, compare the report against the actual diff and remove
  any claim not backed by code, tests, or artifacts.

## Report Export Rule

For every non-trivial task, write the final report to:

```text
docs/agent-reports/latest-agent-report.md
```

Overwrite the file on each run before declaring completion. The chat response
can be a short summary, but this repo file is the canonical report for review.
If the report cannot be written, report that as a blocker.

The exported report must include task/slice, agent and selected skills, coverage
class, Hard Mode carry-forward status, `Changed in this slice`,
`Existing/parent changes observed`, `Files intended for commit`, `Generated
artifact paths`, `git status --short` with `IN SCOPE` / `OUT OF SCOPE`
classification, commands and reliable results, verification notes,
limitations/not covered, environment caveats, and next recommended slice.

## Required Command Pattern for MOM/Governance Actions

```text
command intent
→ load authoritative context
→ validate tenant/scope/auth
→ validate current state, if stateful
→ validate business invariants
→ write append-only domain/security event
→ update projection/read model if applicable
→ return backend-derived result / allowed actions
```

## Forbidden

Do not:

- invent business logic
- use frontend as execution/permission truth
- treat projection/read model as source of truth
- skip event for operational/governance actions
- skip invariant tests
- use Fast Mode for risky tasks
- declare done without verification
- declare pass when assertion failures are printed
- claim implemented work that is not present in the diff or tracked files
- commit, stage, push, or rewrite git history unless explicitly requested

# GitHub Copilot Instructions - FleziBCG AI Brain Enterprise v4 - UI Governor

## Entry Rule

Before non-trivial work, read in order:

1. `.github/agent/AGENT.md` if present
2. `docs/design/INDEX.md`
3. `docs/design/AUTHORITATIVE_FILE_MAP.md`
4. `docs/governance/CODING_RULES.md`
5. `docs/governance/ENGINEERING_DECISIONS.md`
6. `docs/governance/SOURCE_STRUCTURE.md`
7. `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`

This file is not the authoritative source for business logic. Design and governance docs are.

## Default AI Skill

Use:

```text
docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
```

## Required Routing Output

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

## Hard Mode MOM v3

Hard Mode MOM v3 is mandatory for autonomous implementation and risky changes.

Use:

```text
docs/ai-skills/hard-mode-mom-v3/SKILL.md
```

Hard Mode MOM v3 triggers when work touches:

- execution state machine
- execution commands/events
- projections/read models
- station/session/operator/equipment
- production reporting
- downtime
- completion/closure
- quality hold
- material/inventory execution impact
- tenant/scope/auth
- IAM lifecycle
- role/action/scope assignment
- audit/security event
- critical invariant
- DB migration enforcing governance or operational truth

Hard Mode MOM v3 carries forward to follow-up fixes on the same slice. If the
parent/original slice required v3, bugfixes, fixture fixes, review changes, or
verification repairs keep v3 unless the change is purely text/comment-only and
cannot affect tests, DB state, runtime behavior, contracts, or reports.

Test fixture changes touching DB cleanup, tenant data, execution, quality, auth,
state, events, projections, or governed workflows remain MOM Brain + Hard Mode
MOM v3.

Before coding under v3, the agent must generate:

1. Design Evidence Extract
2. Event Map
3. Invariant Map
4. State Transition Map if stateful
5. Test Matrix
6. Verdict before coding

If any is missing: reject implementation.

## Hard Mode MOM v2

Use v2 for smaller/manual reviews:

```text
docs/ai-skills/hard-mode-mom-v2/SKILL.md
```

## FE / UI / UX Work - DESIGN.md UI Governor

When the task touches frontend UI, UX design, React components, Tailwind styling, Figma Make, Google Stitch, `DESIGN.md`, screen packs, or design consistency, read:

```text
docs/ai-skills/design-md-ui-governor/SKILL.md
DESIGN.md
docs/design/DESIGN.md
docs/audit/frontend-source-alignment-snapshot.md
```

If `docs/audit/frontend-source-alignment-snapshot.md` is missing, do not invent current frontend source status. Either inspect source directly or create the snapshot first.

For FE route/page work, build/lint is not sufficient by itself. Route Accessibility Gate must pass.

`docs/ai-skills/stitch-design-md-ui-ux/SKILL.md` and
`docs/ai-skills/design-system-enforcer/SKILL.md` are deprecated aliases only.
Do not load them as active UI skills or in parallel with `design-md-ui-governor`.

This UI/UX skill does not override Hard Mode MOM.

If a UI task touches execution, quality, material, station, operation, tenant/scope/auth, governed actions, allowed actions, operational status, or event/projection truth, also apply:

```text
docs/ai-skills/hard-mode-mom-v3/SKILL.md
```

Hard reject UI output that fakes backend truth, authorization, execution transitions, quality pass/fail, ERP posting, backflush completion, or deterministic AI decisions.

## UI Screenshot Evidence Gate

For any non-trivial frontend/UI slice, the agent must generate screenshot
evidence before marking the task complete. Reviewers must not need to run
screenshot capture themselves just to see the implemented UI.

Required behavior:

- Use an existing route/page screenshot harness when available.
- If no harness exists, add or update a narrowly scoped Playwright/screenshot
  harness for the touched route or component state.
- Screenshots must cover the primary changed state and at least one narrow
  viewport when layout/responsiveness can be affected.
- Mocks used for screenshot capture must match the current frontend API shape.
- If the task changes a state-specific UI, assert that the screenshot harness
  reaches that state before taking screenshots.
- Save screenshots under `docs/audit/` in a task-specific folder.
- List exact screenshot paths in `docs/agent-reports/latest-agent-report.md`.

Artifact policy:

- Screenshots, videos, and generated binary evidence under `docs/audit/**` are
  review artifacts, not commit payload, unless the task prompt explicitly says
  to commit them.
- The report must separate `Generated artifact paths` from `Files intended for
  commit`.
- If generated artifacts are already tracked, staged, or committed contrary to
  the task policy, report a blocker. Do not claim a clean pass.

For execution/station/quality/material/operator workflows, screenshot mocks are
visual QA only. They do not prove backend truth, authorization, E2E behavior, or
pilot golden path coverage.

If screenshots cannot be generated because of environment limits, the report
must state the exact blocker, the command attempted, and the missing evidence.
Do not report the UI slice as fully verified without screenshot evidence.

## Coverage Claim Discipline

Reports must classify coverage honestly:

- `service`: direct service/repository/domain function tests only.
- `API`: endpoint tests, HTTP status/error mapping, and auth dependency behavior.
- `frontend`: rendered UI, route, component, API-client, or i18n behavior.
- `E2E`: user-flow coverage through frontend + backend/API boundary.
- `docs-only`: documentation, prompt, skill, or planning changes.

Service-level tests must not be reported as API, RBAC, E2E, or full pilot golden
path coverage. API/RBAC coverage requires endpoint/auth dependency tests. E2E or
pilot golden path coverage requires frontend/API/user-flow validation.

## Dirty Worktree Gate

Before declaring completion, run `git status --short`.

Required behavior:

- Classify every changed, staged, untracked, or deleted file as either
  `IN SCOPE` or `OUT OF SCOPE`.
- Do not write "not touched" or "intentionally not changed" for any file that
  appears in `git status --short`.
- If an out-of-scope file is dirty, name it in the report under `OUT OF SCOPE`
  and do not include it in files intended for commit.
- If unrelated staged files exist, report a blocker until they are unstaged or
  explicitly authorized by the user.

## Commit Boundary Gate

Default behavior remains: do not run `git add`, `git commit`, `git push`, branch
changes, or history edits unless the user or task prompt explicitly asks.

When git staging or committing is explicitly requested:

- Never use `git add .`.
- Stage only explicit paths that belong to the requested commit.
- Run and report `git diff --cached --stat`.
- Run and report `git diff --cached --name-status`.
- Include `No unrelated staged files: yes/no` in the report.

## Work Quality Gate

Before code changes, publish a compact work packet:

- user goal;
- slice boundary;
- selected skills read;
- files expected to change;
- files intentionally not changed;
- source-of-truth evidence;
- validation plan;
- stop conditions.

During coding:

- reuse neighboring implementation and test patterns;
- keep edits surgical and directly tied to the request;
- separate behavior changes from broad refactors;
- do not bypass service/domain layers to satisfy tests;
- for DB-backed tests, purge before and after persistent writes and rollback
  before teardown purge;
- do not use unique prefixes as a cleanup substitute;
- verify container commands run against live edited source before trusting them;
- capture a reliable exit code or log before reporting a command as passed.

## Report Export Rule

For every non-trivial task, the final agent report must be written to:

```text
docs/agent-reports/latest-agent-report.md
```

Overwrite this file on each run before marking the task done. The chat response
may summarize the outcome, but the repository file is the canonical report for
review. If the agent cannot write this file, it must report that as a blocker.

The exported report must include:

- task / slice;
- agent and selected skills;
- coverage class;
- Hard Mode kept from parent slice: yes/no/N/A;
- changed in this slice;
- existing/parent changes observed;
- files intended for commit;
- generated artifact paths;
- `git status --short` summary with `IN SCOPE` / `OUT OF SCOPE`
  classification;
- staged diff summary if any git operation was explicitly requested;
- commands run and reliable results;
- verification notes;
- limitations / not covered;
- known environment caveats;
- next recommended slice.

For frontend/UI slices, the exported report must also include:

- screenshot command run;
- screenshot assertion summary;
- exact screenshot output paths;
- viewport/state coverage;
- whether screenshots use mocked API data or real backend data.

## Non-negotiables

- Backend is source of truth.
- Frontend sends intent only.
- Frontend does not derive execution state.
- Frontend does not decide authorization.
- Events are append-only operational facts.
- Projections are read models.
- JWT proves identity only.
- Authorization is server-side.
- AI is advisory only.
- Critical invariants must not rely only on UI validation.
- Do not invent product scope.
- Work in vertical slices.
- Prefer behavior-based tests.
- Do not use destructive Git commands unless explicitly requested and confirmed.

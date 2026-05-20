# Copilot Agent Handoff And Review Workflow

## Purpose

Use this workflow when Codex acts as PO/SA/reviewer and GitHub Copilot Agent
does the implementation inside VS Code.

The operating loop is:

1. Codex writes clear implementation direction.
2. User runs GitHub Copilot Agent in VS Code.
3. Copilot Agent implements and exports the fixed report file.
4. User tells Codex the agent finished.
5. Codex reviews the report, diff, verification, and evidence.
6. Codex reviews the agent behavior/process failure mode.
7. Codex either accepts the slice, writes a correction prompt, or patches the
   active skills/instructions when the failure should be prevented globally.

Codex cannot directly control the VS Code Copilot chat. The repository files are
the handoff contract between Codex, the user, and Copilot Agent.

## Fixed File Contract

Use these paths consistently:

- Task prompt:
  - Preferred: `docs/prompts/active-copilot-agent-task.md`
  - Alternative for archived prompts: `docs/prompts/<slice-name>-agent-prompt.md`
- Agent report:
  - `docs/agent-reports/latest-agent-report.md`
- UI screenshot evidence:
  - `docs/audit/<slice-name>/`
  - Generated images/videos are review artifacts by default; do not commit them
    unless the prompt explicitly says to commit artifacts.
- Existing persistent instructions:
  - `.github/copilot-instructions.md`

`docs/agent-reports/latest-agent-report.md` is overwritten on every non-trivial
agent run. It is the canonical review input.

## Step 1 - Codex Creates Direction

Codex should create or update the task prompt file with:

- a unique task/slice id and one-line goal;
- an explicit instruction that the agent must stop with `RED - task identity
  mismatch` if the report title, screenshot folder, or implemented files match a
  different/older slice id;
- mandatory read of `docs/agent-context/flezibcg-project-primer.md` before
  design/domain docs so the agent starts from product context, not stale
  reports;
- user goal;
- business slice boundary;
- mandatory files and skills to read before coding;
- selected mode and Hard Mode decision;
- files expected to change;
- files intentionally not changed;
- source-of-truth evidence required before coding;
- exact implementation goals;
- verification commands;
- screenshot requirements for UI/frontend slices;
- navigation intent classification and explicit-selection requirements when the
  slice touches login landing, routing, menus, list/queue/table selection,
  detail pages, cockpit pages, or action panels;
- artifact policy: generated screenshots/videos are evidence, not default commit
  payload;
- report fields for `Changed in this slice`, `Existing/parent changes observed`,
  `Files intended for commit`, and `Generated artifact paths`;
- dirty worktree policy: every dirty path must be classified as `IN SCOPE` or
  `OUT OF SCOPE`;
- final report template;
- stop conditions.

For UI/frontend slices, the prompt must require screenshots and exact screenshot
paths in `docs/agent-reports/latest-agent-report.md`.

For routing/list/queue/detail/cockpit/action slices, the prompt must require the
Navigation Intent Gate:

- classify touched screens as `LANDING`, `LIST`, `QUEUE`, `SETUP`, `DETAIL`,
  `COCKPIT`, or `ACTION`;
- forbid initial auto-selection of the first item on `LANDING`/`LIST`/`QUEUE`;
- forbid initial URL mutation with an entity id from the first item;
- allow detail/cockpit/action entry only from explicit deep link, explicit user
  selection/scan/typed id, or backend-confirmed active owned context;
- require source-search evidence on every touched route/list/queue/detail/
  cockpit/action file for `items[0]`, `data.items[0]`, `queueItems[0]`,
  `preferred ??`, `setSearchParams`, `navigate(`, and route-param setters;
- require remaining suspicious hits to be classified as `yes - existing` or
  `yes - introduced`, never hidden behind a plain `no`;
- require evidence that default landing/list/queue state stays unselected and
  explicit selection/deep link still works.

The prompt should also state whether the agent is allowed to perform git
operations. Default: no `git add`, `git commit`, `git push`, branch switching,
or history edits unless explicitly requested.

If git operations are allowed, the prompt must forbid `git add .` and require
`git diff --cached --stat`, `git diff --cached --name-status`, and
`No unrelated staged files: yes/no` in the report before committing.

## Step 2 - User Runs Copilot Agent

In VS Code Copilot Agent, paste this:

```text
Read and execute docs/prompts/active-copilot-agent-task.md.
Follow .github/copilot-instructions.md.
Before coding, output routing, selected skills read, source evidence, files to patch, validation plan, and stop conditions.
After implementation, overwrite docs/agent-reports/latest-agent-report.md with the final report.
In the report, classify every dirty path from git status as IN SCOPE or OUT OF SCOPE.
Do not say a file was not touched if it appears in git status.
Separate Generated artifact paths from Files intended for commit.
Do not mark the task complete until required verification and, for UI work, screenshots are generated and listed in the report.
```

If using an archived prompt instead of the active prompt, replace the first path
with the specific prompt path.

## Step 3 - Copilot Agent Executes

Copilot Agent should:

- read the mandatory files first;
- publish the pre-coding routing/work packet;
- keep implementation scoped to the prompt;
- preserve backend truth and authorization truth;
- run the required verification commands;
- generate UI screenshots when applicable;
- export `docs/agent-reports/latest-agent-report.md`;
- list limitations honestly.

For frontend/UI work, screenshots are visual QA only unless the prompt also
requires real backend/E2E validation.

## Step 4 - User Returns To Codex

After Copilot Agent finishes, tell Codex:

```text
Agent finished. Please review docs/agent-reports/latest-agent-report.md and the diff.
```

For UI work, optionally add:

```text
Please also inspect the screenshots listed in the report.
```

## Step 5 - Codex Reviews

Codex should review in this order:

1. Read `docs/agent-reports/latest-agent-report.md`.
2. Inspect `git status --short`.
3. Inspect the relevant diff and new files.
4. Re-run or spot-check critical verification commands when practical.
5. For UI work, open the screenshot paths listed in the report.
6. Check whether report claims match actual diff, tracked/untracked files, and artifacts.
7. Inspect staged files with `git diff --cached --stat` and
   `git diff --cached --name-status` if anything is staged.
8. Confirm generated artifacts are not staged/committed unless explicitly
   requested.
9. Compare implementation against the original prompt acceptance criteria.
10. For routing/list/queue/detail/cockpit/action work, check navigation intent:
    no implicit first-item selection, no first-item URL entity-id mutation, and
    any `NAV_INTENT_EXCEPTION:` is backed by backend active-owned context.
11. Classify any failure as product/code, prompt ambiguity, harness weakness, or skill/process gap.
12. Report findings first, ordered by severity.
13. Complete the Review Closeout Gate.
14. Decide: accept, accept with minor follow-up, reject and write correction prompt, or patch skills/instructions.

Review output should include:

- blocking findings;
- verification results;
- report honesty issues;
- product/UX acceptance gaps;
- agent behavior/process issues;
- whether skill/instruction updates are needed;
- correction prompt if needed.
- review closeout with skill-improvement decision and next plan.

## Review Closeout Gate

Every Codex review response must end with a compact closeout decision. Do not
stop after findings only.

Required closeout fields:

```markdown
## Skill Improvement Decision
- Needed: yes/no
- Reason:
- Action: none / patch skill now / create correction prompt / defer with rationale
- Files to patch or re-read next:

## Next Plan
- Decision: accept / cleanup first / correction agent prompt / next product slice
- Next action owner: user / Copilot Agent / Codex
- Exact next step:
- Expected files in scope:
- Verification required:
```

Use `Needed: yes` when the agent failure is reusable, systemic, or likely to
recur. Use `Needed: no` only when the issue is clearly a one-off local mistake,
already covered by active instructions, or caused by user-controlled commit
selection.

The `Next Plan` must be operational enough that the user can either run the next
agent prompt or make the next commit without asking what to do next.

## Acceptance Rules

Do not accept an agent slice as complete when:

- the report claims a command passed but the command fails when checked;
- coverage class is inflated;
- UI work has no screenshot evidence;
- screenshots do not actually reach the changed state;
- frontend fakes backend truth, authorization, state transitions, quality, or status;
- required Hard Mode carry-forward was downgraded without justification;
- product code changed outside the declared slice without explanation.
- the agent committed/staged/pushed changes without explicit permission;
- the agent used `git add .` or left unrelated staged files;
- generated binary artifacts under `docs/audit/**` are staged or committed
  without explicit artifact-commit permission;
- the report says a dirty file was not touched;
- dirty files are not classified as `IN SCOPE` or `OUT OF SCOPE`;
- the report claims a component/file was implemented but it is not imported,
  rendered, tracked, or present in the diff;
- assertion failures are printed even if the command exits 0.
- a landing/list/queue route auto-selects the first item, mutates the URL with a
  first-item entity id, or enters detail/cockpit/action state without explicit
  user intent or backend-confirmed active owned context.

## Step 6 - Continuous Skill Improvement

After every review, Codex should decide whether the agent's failure mode should
be fixed at the skill/instruction level.

Patch skills/instructions when the issue is reusable, systemic, or likely to
recur, for example:

- report claims do not match the diff;
- command PASS is claimed despite assertion failures;
- screenshot evidence does not reach the target state;
- required new files are left untracked or unintegrated;
- agent commits/stages/pushes without permission;
- coverage class is inflated;
- Hard Mode carry-forward is silently downgraded;
- frontend treats backend truth, authorization, execution, quality, or status as client-owned;
- frontend treats list/queue membership as implicit user selection or enters a
  detail/cockpit/action screen from the first item without explicit user intent;
- prompt instructions are followed cosmetically but not evidenced by code/artifacts.

Prefer updating the most specific active skill first:

- UI/frontend behavior: `docs/ai-skills/design-md-ui-governor/SKILL.md`
- execution/MOM routing and report discipline:
  `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- implementation-loop behavior:
  `docs/ai-skills/autonomous-implementation-agent/SKILL.md`
- test, E2E, screenshot, and assertion behavior:
  `docs/ai-skills/qa-e2e-layer/SKILL.md`
- cross-agent persistent rules: `.github/copilot-instructions.md`

Do not patch skills for every one-off mistake. Patch skills when the rule should
apply to future agents beyond the current slice.

Skill/instruction patches should be small and behaviorally explicit:

- name the failure mode;
- state required behavior;
- state forbidden behavior;
- add required report/evidence fields when useful;
- keep product-specific examples only when they clarify a general rule.
- add gates that compare the report against `git status`, staged diff, and
  generated artifact policy when the failure is worktree hygiene.

## Correction Loop

If Codex rejects the slice, Codex writes a correction prompt that:

- names the failed acceptance criteria;
- lists exact files and lines to inspect;
- distinguishes bugs from missing verification;
- requires the agent to correct the prior report;
- preserves valid work already done;
- requires updated verification and report export.

The user then runs Copilot Agent again with the correction prompt, and the same
review loop repeats.

If Codex patched skills/instructions during review, the correction prompt should
tell the agent to re-read the updated active skills before making further edits.

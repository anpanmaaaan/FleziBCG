# FleziBCG AI Brain — Enterprise-ready Unified Pack v3

## Purpose

This pack makes FleziBCG AI/Copilot agents operate like a disciplined software engineering organization:

```text
Route → Select Brain → Select Mode → Read Design → Generate Maps → Test First → Code → Build → Test → Verify → Report
```

It is designed for the FleziBCG MOM platform, but includes a generic brain for non-MOM tasks.

## Included

```text
.github/copilot-instructions.md
.github/copilot-instructions-hard-mode-mom-v3-addendum.md
.github/pull_request_template.md
.github/workflows/pr-gate.yml

.copilot/prompts/
  autonomous-implementation-v3.prompt.md
  hard-mode-mom-v3.prompt.md
  hard-mode-mom-v2.prompt.md
  pr-gate-review.prompt.md
  ui-design-follow-design-md.prompt.md
  slice-strategy-executor.prompt.md
  source-audit.prompt.md

docs/ai-skills/
  README.md
  flezibcg-ai-brain-v6-auto-execution/SKILL.md
  hard-mode-mom-v3/SKILL.md
  hard-mode-mom-v3/*
  hard-mode-mom-v2/SKILL.md
  qa-e2e-layer/SKILL.md
  pr-gate-reviewer/SKILL.md
  design-system-enforcer/SKILL.md
  autonomous-implementation-agent/SKILL.md
  slice-strategy/SKILL.md
  skill-authoring-standard/SKILL.md
  generic-brain-core/SKILL.md
  mom-brain-core/SKILL.md

docs/design/DESIGN.md
DESIGN.md

docs/implementation/
  slice-strategy-for-flezibcg.md
  autonomous-agent-operating-manual.md

docs/review/
  pr-hard-mode-checklist.md
```

## Install

From repo root:

```bash
unzip flezibcg-ai-brain-enterprise-ready-v3.zip -d .
```

If files already exist, merge manually and prefer this pack for AI skill files.

## Recommended first prompt

```text
Follow .copilot/prompts/autonomous-implementation-v3.prompt.md.

Continue autonomous implementation from the current repo state.
Use Hard Mode MOM v3 for P0-A/P0-B/P0-C slices.
Do not invent business logic.
```

## Version rule

- Hard Mode MOM v3 = autonomous implementation
- Hard Mode MOM v2 = manual review / smaller PR review
- Hard Mode MOM v1 = deprecated

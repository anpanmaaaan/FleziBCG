# Prompt — Integrate DESIGN.md UI Governor into FleziBCG Internal Repo

You are a senior repository maintainer and AI-skill integration agent.

Your task is to integrate the DESIGN.md UI Governor pack into the FleziBCG internal repo.

This is a documentation / agent-skill integration task only.

# Required Context

FleziBCG is a MOM platform. UI work must respect:

- backend is source of truth;
- frontend is UX/display only;
- persona is not permission;
- JWT proves identity only;
- backend checks authorization;
- execution status and allowed_actions come from backend when connected;
- AI is advisory;
- Digital Twin is derived;
- ERP/QMS/CMMS/WMS/SCADA are not replaced;
- Acceptance Gate is canonical; LAT/Pre-LAT are display labels only;
- Backflush is cross-domain orchestration, not a simple UI button;
- Station Execution target is session-owned; claim is migration debt.

# Files to Add / Update

Add or update only these files:

```text
DESIGN.md
docs/design/DESIGN.md
docs/ai-skills/design-md-ui-governor/SKILL.md
docs/ai-skills/design-md-ui-governor/references/design-md-format-rules.md
docs/ai-skills/design-md-ui-governor/references/flezibcg-mom-ui-guardrails.md
docs/ai-skills/design-md-ui-governor/references/source-alignment-rules.md
.copilot/prompts/design-md-ui-pack.prompt.md
.copilot/prompts/design-md-review.prompt.md
.copilot/prompts/design-md-source-alignment-refresh.prompt.md
.github/copilot-instructions-design-md-addendum.md
docs/evals/design-md-ui-governor-evals.json
```

Patch `.github/copilot-instructions.md` only if it exists and only by adding a short FE/UI/UX DESIGN.md routing section. Do not rewrite unrelated instructions.

If an older `stitch-design-md-ui-ux` or `design-system-enforcer` skill exists, do not delete it. Add a note that `design-md-ui-governor` is the preferred UI governance skill going forward, while older skills remain compatibility references.

# Strict Rules

Do NOT modify production source code.
Do NOT modify backend.
Do NOT modify frontend TS/TSX source.
Do NOT modify database or migrations.
Do NOT change routes.
Do NOT install dependencies.
Do NOT format unrelated files.
Do NOT commit changes.
Do NOT import third-party brand DESIGN.md files.
Do NOT copy a public brand's visual identity into FleziBCG.

# Implementation Steps

1. Inspect existing `DESIGN.md`, `docs/design/DESIGN.md`, `docs/ai-skills/`, `.github/copilot-instructions.md`, and `.copilot/prompts/`.
2. Add the new `design-md-ui-governor` skill and references.
3. Replace or upgrade `DESIGN.md` only if the current file is less complete. Preserve FleziBCG-specific naming and MOM safety rules.
4. Mirror root `DESIGN.md` into `docs/design/DESIGN.md` unless the repo has an explicit different policy.
5. Add prompt templates.
6. Add eval JSON.
7. Patch `.github/copilot-instructions.md` with the addendum, preserving existing Hard Mode MOM routing.
8. Report whether older UI skills exist and how they relate.

# Verification

Run only lightweight checks that do not require dependency install:

```bash
find docs/ai-skills/design-md-ui-governor -maxdepth 3 -type f -print
find .copilot/prompts -maxdepth 1 -type f -name 'design-md*.md' -print
find docs/evals -maxdepth 1 -type f -name 'design-md-ui-governor-evals.json' -print
```

If frontend dependencies already exist and no install is needed, optionally run:

```bash
cd frontend && npm run build
```

Do not fail the task solely because optional frontend build is unavailable.

# Final Report Format

```markdown
# DESIGN.md UI Governor Integration Report

## Routing
- Selected skill:
- Mode:
- Hard Mode MOM required: Yes/No + why

## Files Added / Updated

## Existing UI Skills Found

## How This Integrates With Existing Skills

## What Was Not Changed

## Verification Run

## Risks / Notes

## Recommended Next Step
```

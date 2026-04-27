# AI Skills Pack for GitHub Copilot

This pack converts the public `mattpocock/skills` idea into repository-local Markdown instructions that GitHub Copilot Chat can read and follow.

> Important: GitHub Copilot in VSCode does not install or execute Claude-style skills. Use these files as prompt templates by referencing them in Copilot Chat.

## How to use

Ask Copilot Chat:

```text
Follow docs/ai-skills/tdd.md.
Implement <feature>.
Respect .github/copilot-instructions.md.
```

Or:

```text
Use docs/ai-skills/to-issues.md to break this PRD into implementation slices.
```

## Included skills

### Planning & Design
- `to-prd.md`
- `to-issues.md`
- `grill-me.md`
- `design-an-interface.md`
- `request-refactor-plan.md`
- `domain-model.md`
- `zoom-out.md`

### Development
- `tdd.md`
- `triage-issue.md`
- `improve-codebase-architecture.md`
- `migrate-to-shoehorn.md`
- `scaffold-exercises.md`
- `qa.md`

### Tooling & Setup
- `setup-pre-commit.md`
- `git-guardrails.md`

### Writing & Knowledge
- `write-a-skill.md`
- `edit-article.md`
- `ubiquitous-language.md`
- `obsidian-vault.md`

## Copilot usage pattern

For best results, mention:
1. The skill file.
2. The target files/folders.
3. The scope and exclusions.
4. The expected output format.
5. Whether Copilot may edit files or should only propose a plan.

Example:

```text
Follow docs/ai-skills/tdd.md.
Target: backend/app/execution.
Implement only the smallest vertical slice for starting a station session.
Do not touch ERP, AI, scheduling, or UI.
Return tests first, then implementation, then refactor notes.
```

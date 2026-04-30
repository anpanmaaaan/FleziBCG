# Prompt — DESIGN.md-Governed UI Pack Implementation

You are a senior frontend engineer and MOM-aware UI implementation agent.

Your task is to implement one small FleziBCG UI slice using the DESIGN.md UI system.

Read first:

```text
.github/copilot-instructions.md
DESIGN.md
docs/design/DESIGN.md
docs/ai-skills/design-md-ui-governor/SKILL.md
docs/ai-skills/design-md-ui-governor/references/design-md-format-rules.md
docs/ai-skills/design-md-ui-governor/references/flezibcg-mom-ui-guardrails.md
docs/ai-skills/design-md-ui-governor/references/source-alignment-rules.md
docs/audit/frontend-source-alignment-snapshot.md
```

If the UI touches execution, quality, material, integration, IAM, scope, audit, allowed actions, status truth, or governed actions, also read:

```text
docs/ai-skills/hard-mode-mom-v3/SKILL.md
```

# Strict Rules

Do not redesign the whole app.
Do not change backend.
Do not change database/migrations.
Do not invent API fields.
Do not hardcode permission truth.
Do not derive execution truth in frontend.
Do not fake quality pass/fail.
Do not fake ERP posting.
Do not fake backflush.
Do not present AI as deterministic authority.
Do not make future screens look active.
Do not mix mock data into production API paths.

# Scope

Implement only this UI slice:

```text
[PASTE UI SLICE NAME AND EXACT SCOPE HERE]
```

# Required Output

After implementation, reply with:

```markdown
# UI/UX Implementation Report
## Selected Skill
## Source Inputs Read
## Scope
## Design System Alignment
## Source Alignment
## Files Changed
## Screens Affected
## Components Added / Updated
## Data Source Status
## MOM Safety Check
## Responsive / Accessibility Check
## Tests / Build Run
## Known Limitations
## Next Recommended FE Slice
```

# FleziBCG DESIGN.md Integration Pack v1

## Purpose

This pack integrates the `awesome-design-md` / `DESIGN.md` pattern into the FleziBCG internal AI skill repo without importing a third-party visual identity.

It adds:

- a FleziBCG-native `DESIGN.md`;
- a repo skill: `docs/ai-skills/design-md-ui-governor/SKILL.md`;
- references for DESIGN.md format, MOM UI guardrails, and source alignment;
- Copilot prompt templates for UI pack generation and review;
- a Copilot instruction addendum;
- lightweight eval cases for UI output quality.

## Integration Stance

Use `awesome-design-md` as a **format and workflow inspiration**, not as a design authority.

Do not copy a public brand's DESIGN.md into FleziBCG as-is. FleziBCG needs its own manufacturing-operations visual language.

## Recommended Placement

Copy these files into the repo root:

```text
DESIGN.md
docs/design/DESIGN.md
docs/ai-skills/design-md-ui-governor/SKILL.md
docs/ai-skills/design-md-ui-governor/references/*.md
.copilot/prompts/design-md-ui-pack.prompt.md
.copilot/prompts/design-md-review.prompt.md
.copilot/prompts/design-md-source-alignment-refresh.prompt.md
.github/copilot-instructions-design-md-addendum.md
docs/evals/design-md-ui-governor-evals.json
```

Then patch `.github/copilot-instructions.md` manually by adding the addendum content under the FE/UI/UX section.

## Safe Integration Rule

This pack changes agent guidance and design-system docs only. It must not change production source code, runtime behavior, backend APIs, database migrations, or routes.

## Recommended First Agent Task

Run `PROMPT_TO_SOURCE_AGENT.md` from this pack. It asks the source agent to integrate the files safely and report exact changes.

# Skill: write-a-skill

## Purpose
Create a reusable AI skill as a Markdown instruction file.

## Use when
- A repeated workflow should become a reusable prompt.
- You want consistent agent behavior.
- You want to encode project rules into a skill.

## Skill structure
```md
# Skill: <name>

## Purpose
## Use when
## Inputs
## Process
## Output format
## Rules
## Examples
```

## Process
1. Name the skill with a short kebab-case name.
2. Define when to use it.
3. Define inputs and outputs.
4. Define a step-by-step process.
5. Add guardrails and anti-patterns.
6. Add examples.

## Rules
- Keep instructions operational.
- Avoid vague principles without actions.
- Include output templates.
- Include “do not” rules for common mistakes.

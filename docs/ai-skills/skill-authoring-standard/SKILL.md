---
name: skill-authoring-standard
description: Standard for writing FleziBCG-native skills using folder-based SKILL.md pattern.
---

# FleziBCG Skill Authoring Standard

## Folder Format

```text
docs/ai-skills/<skill-name>/SKILL.md
```

Use kebab-case names.

## SKILL.md Structure

```markdown
---
name: skill-name
description: One sentence explaining when to use the skill.
---

# Skill Name

## When to use
## Required reading
## Rules
## Workflow
## Output format
## Reject / stop conditions
```

Rules:

- keep skill focused
- state trigger conditions clearly
- state reject/stop conditions explicitly
- prefer output templates
- avoid vague “best practice” wording

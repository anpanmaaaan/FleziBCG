# Skill: design-an-interface

## Purpose
Generate multiple interface designs for a module, screen, API, or developer-facing abstraction.

## Use when
- The team is unsure what the best interface should look like.
- You want several radically different options.
- You need trade-offs before committing.

## Process
1. Define the user of the interface:
   - End user
   - Frontend developer
   - Backend service
   - External integration
   - Operator/admin
2. Define the job-to-be-done.
3. Propose 3–5 different designs.
4. For each design, show:
   - Shape / signature / screen layout
   - Strengths
   - Weaknesses
   - Best-fit context
5. Recommend one option.

## Output format
```md
# Interface Design Options: <Name>

## Context
## Constraints

## Option A: <Name>
### Shape
### Pros
### Cons
### Best For

## Option B: <Name>
...

## Recommendation
## Why
## Migration Notes
```

## Rules
- Make options meaningfully different, not superficial variations.
- Optimize for clarity, testability, and long-term maintainability.
- Prefer small, deep interfaces over broad shallow ones.

# Skill: grill-me

## Purpose
Interrogate a plan, architecture, design, or implementation proposal until hidden assumptions, trade-offs, and edge cases are clarified.

## Use when
- A design feels plausible but not fully stress-tested.
- You need decision-quality questions before implementation.
- You want to avoid rushing into coding.

## Process
1. Restate the plan in one paragraph.
2. Identify the most fragile assumptions.
3. Ask questions in batches.
4. Group questions by theme:
   - Product scope
   - Domain model
   - Data consistency
   - UX / workflow
   - Security / authorization
   - Integration
   - Testing
   - Migration / rollout
5. After user answers, update the decision summary.
6. Repeat until no major unresolved branch remains.

## Output format
```md
# Grill Review: <Topic>

## Current Understanding
## Critical Assumptions
## Questions

### Product Scope
1. ...

### Domain / Data
1. ...

### Architecture
1. ...

## Preliminary Risks
## Decisions Already Stable
## Decisions Still Needed
```

## Rules
- Ask pointed questions, not generic ones.
- Do not overwhelm with irrelevant theoretical questions.
- Challenge decisions respectfully.
- If a decision is already supported by docs, do not re-litigate it.

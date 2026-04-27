# Skill: request-refactor-plan

## Purpose
Create a safe refactor plan broken into tiny commits.

## Use when
- Code works but structure is becoming hard to change.
- You need to reduce risk before changing behavior.
- You want a refactor plan before implementation.

## Process
1. Identify the refactor goal.
2. Identify behavior that must remain unchanged.
3. Identify safety tests needed before refactor.
4. Propose small commits.
5. Each commit should be reversible and reviewable.
6. Separate behavior-changing commits from pure refactor commits.

## Output format
```md
# Refactor Plan: <Area>

## Goal
## Non-goals
## Current Pain Points
## Behavior That Must Not Change
## Safety Tests Needed

## Commit Plan
1. <Commit title>
   - Purpose:
   - Files:
   - Validation:

2. ...

## Risks
## Rollback Plan
```

## Rules
- Do not mix refactor and feature work unless explicitly required.
- Do not recommend broad rewrites by default.
- Prefer extraction, renaming, and boundary clarification.
- Always include validation steps.

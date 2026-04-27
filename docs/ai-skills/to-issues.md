# Skill: to-issues

## Purpose
Break a plan, PRD, spec, or design document into independently implementable issues using vertical slices.

## Core principle
Prefer thin tracer-bullet slices over horizontal technical layers.

A good issue should be:
- Small enough to implement independently.
- Demoable or verifiable on its own.
- Connected to a user/system behavior.
- Testable with clear acceptance criteria.

## Process
1. Read the source plan/spec.
2. Identify the smallest useful end-to-end behaviors.
3. Split work into vertical slices.
4. Mark each slice as:
   - `AFK`: can be implemented without a human decision.
   - `HITL`: requires human-in-the-loop decision or review.
5. Identify dependencies.
6. Produce an issue list first.
7. Only create GitHub issues if the user explicitly asks.

## Output format
```md
# Issue Breakdown

## Slice 1: <Title>
Type: AFK / HITL
Blocked by: None / <Slice>
User stories covered:
- ...

What to build:
- ...

Acceptance criteria:
- [ ] ...
- [ ] ...

Test notes:
- ...

Out of scope:
- ...
```

## Rules
- Do not make one issue for “database”, one for “backend”, one for “frontend” unless explicitly requested.
- Each slice should cut across the layers needed for one behavior.
- Prefer many small issues over one large vague issue.
- Do not close, modify, or create remote issues unless explicitly asked.

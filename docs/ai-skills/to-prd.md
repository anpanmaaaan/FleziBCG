# Skill: to-prd

## Purpose
Turn the current context, conversation notes, design decision, or feature request into a Product Requirements Document.

## Use when
- A feature idea is still vague.
- A design discussion needs to become a stable product spec.
- You need a PRD before creating issues.

## Inputs
- Existing conversation context or pasted notes.
- Relevant docs, if available.
- Constraints, non-goals, and assumptions.

## Process
1. Summarize the problem.
2. Identify users/personas.
3. Define goals and non-goals.
4. Define scope boundaries.
5. Extract functional requirements.
6. Extract non-functional requirements.
7. Define acceptance criteria.
8. List risks, open questions, and dependencies.
9. Keep implementation details out unless needed for feasibility.

## Output format
```md
# PRD: <Feature Name>

## Background
## Problem
## Users / Personas
## Goals
## Non-goals
## Scope
## Functional Requirements
## Non-functional Requirements
## User Stories
## Acceptance Criteria
## Dependencies
## Risks
## Open Questions
```

## Rules
- Do not invent scope not supported by the input.
- Mark assumptions explicitly.
- Prefer clear requirements over vague “improve” language.
- Separate product behavior from implementation choices.

# Skill: domain-model

## Purpose
Model the domain concepts, relationships, invariants, and lifecycle behind a product area.

## Use when
- A feature touches complex business rules.
- Entities and states are unclear.
- You need domain clarity before database/API design.

## Process
1. Identify core entities.
2. Identify value objects.
3. Identify aggregates or ownership boundaries.
4. Define state/lifecycle.
5. Define invariants.
6. Define commands/events.
7. Identify read models.
8. List unresolved domain questions.

## Output format
```md
# Domain Model: <Area>

## Core Concepts
## Entity / Value Object Table
## Relationships
## State Lifecycle
## Invariants
## Commands
## Events
## Read Models
## Open Questions
```

## Rules
- Domain model first, database second.
- Do not confuse UI labels with canonical domain terms.
- Separate derived state from stored state.
- Mark tenant-specific labels as aliases, not canonical terms.

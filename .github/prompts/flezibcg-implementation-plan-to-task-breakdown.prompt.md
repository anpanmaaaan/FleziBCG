---
name: "FleziBCG Implementation Plan To Task Breakdown"
description: "Convert a FleziBCG implementation plan into an execution-ready task breakdown with vertical-slice tasks, dependencies, validation, and done criteria. Use when planning needs to become assignable engineering work."
argument-hint: "Paste the implementation plan or approved execution plan to break down."
agent: "FleziBCG PO-SA"
---
Convert the following FleziBCG implementation plan into a task breakdown.

Input:
{{input}}

Instructions:

- Treat the input as the planning baseline.
- Produce task breakdown only. Do not write code.
- Use FleziBCG routing first.
- Follow authoritative design and governance documents before proposing task structure.
- Prefer vertical slices over layer-by-layer decomposition.
- Keep each task small enough to implement and validate independently.
- Separate required tasks from optional hardening or follow-up tasks.
- For any task touching execution, auth, audit, tenant, quality, material, invariant-sensitive behavior, or contract surfaces, call out Hard Mode MOM requirements and mandatory validation.
- Include dependencies only where they materially affect execution order.

Output in this format:

## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:

## Task Breakdown
### Objective
### Assumptions
### Required Tasks
For each task include:
- Task name
- Purpose
- Scope
- Dependencies
- Primary files or surfaces likely affected
- Validation
- Done criteria

### Optional Follow-up Tasks
### Risks and Coordination Notes
### Recommended Delivery Order
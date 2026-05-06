---
name: "FleziBCG Spec To Implementation Plan"
description: "Turn a FleziBCG feature spec or approved requirement into a vertical-slice implementation plan with routing, invariants, affected surfaces, validation, and slice order. Use when you want execution planning before coding."
argument-hint: "Paste the spec, approved requirement, or feature brief to plan from."
agent: "FleziBCG PO-SA"
---
Convert the following FleziBCG spec or approved requirement into an implementation plan.

Input:
{{input}}

Instructions:

- Treat the input as the planning source.
- Produce implementation plan only. Do not write code.
- Use FleziBCG routing first.
- Follow authoritative design and governance documents before proposing changes.
- Prefer the smallest viable vertical slice that preserves backend truth, governance, and testability.
- If the work touches execution, auth, audit, tenant, quality, material, invariant-sensitive behavior, or contract surfaces, explicitly call out Hard Mode MOM requirements.
- Separate required work from optional follow-up.
- Keep the plan concrete enough that an engineer can implement it without re-discovering the scope.

Output in this format:

## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:

## Implementation Plan
### Objective
### Assumptions
### Authoritative Design Evidence
### Invariants and Constraints
### Affected Backend Surfaces
### Affected Frontend Surfaces
### API, Schema, and Data Changes
### Event and State Impact
### Vertical Slice Plan
### Validation Plan
### Risks and Open Questions
### Recommended Execution Order

---
name: "FleziBCG Spec From Request"
description: "Generate a FleziBCG standard hybrid PO plus SA spec from a one-line feature request, problem statement, or change request. Use when you want fast scope framing, invariants, acceptance criteria, and test matrix before coding."
argument-hint: "Paste one sentence describing the requested feature, issue, or change."
agent: "FleziBCG PO-SA"
---
Convert the following request into a FleziBCG standard spec.

Request:
{{input}}

Instructions:

- Treat the input as an initial request, not approved truth.
- Produce spec only. Do not implement code.
- Use FleziBCG routing first.
- Follow authoritative design and governance documents before making assumptions.
- If the request touches MOM-governed execution, auth, audit, tenant, quality, material, or invariant-sensitive behavior, keep the spec strict and call out the required Hard Mode MOM level.
- Prefer the smallest viable vertical slice.
- If critical details are missing, state assumptions and list only the minimum open questions.

Output in this format:

## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:

## Spec
### Problem
### Business Outcome
### In Scope
### Out of Scope
### Actors and Permissions
### Authoritative Design Evidence
### Domain Invariants
### State and Event Impact
### API, Schema, and Data Impact
### UX Intent and Backend-Truth Boundaries
### Acceptance Criteria
### Test Matrix
### Risks and Open Questions
### Recommended Next Slice
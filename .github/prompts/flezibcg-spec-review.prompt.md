---
name: "FleziBCG Spec Review"
description: "Review a FleziBCG spec for scope gaps, domain-truth conflicts, invariant issues, missing acceptance criteria, and implementation risk. Use when a spec needs architecture and product scrutiny before planning or coding."
argument-hint: "Paste the spec, RFC, feature brief, or design note to review."
agent: "FleziBCG PO-SA"
---
Review the following FleziBCG spec.

Input:
{{input}}

Instructions:

- Treat this as a review task, not a rewrite unless a correction is needed for clarity.
- Use FleziBCG routing first.
- Follow authoritative design and governance documents before judging the spec.
- Prioritize findings that would cause wrong behavior, governance violations, contract mistakes, or slice planning failures.
- Be explicit when the spec conflicts with backend-truth boundaries, authorization truth, event truth, or domain invariants.
- If no major findings exist, say so and note residual risks or missing verification detail.

Output in this format:

## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:

## Review Findings
### Critical Issues
### Major Issues
### Minor Issues
### Missing Design Evidence
### Missing Invariants or Acceptance Criteria
### Implementation Risks
### Recommendation
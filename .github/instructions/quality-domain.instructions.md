---
name: "FleziBCG Quality Domain"
description: "Use when working on FleziBCG quality, QC applicability, inspections, measurements, quality evaluation, pass fail hold behavior, accepted-good derivation, disposition, quality review, or quality-related specs and plans."
applyTo: ["frontend/src/app/pages/QualityDashboard.tsx", "frontend/src/app/pages/QualityHolds.tsx", "frontend/src/app/pages/QCCheckpoints.tsx", "frontend/src/app/pages/MeasurementEntry.tsx", "frontend/src/app/pages/QualityPerformanceReport.tsx", "frontend/src/app/pages/DefectManagement.tsx"]
---
# Quality Domain Guidance

Primary truth:

- `docs/design/02_domain/quality/quality-domain-contracts.md`
- `docs/design/02_domain/quality/business-truth-quality-lite.md`

Supporting truth when quality affects execution:

- `docs/design/02_domain/execution/business-truth-station-execution-v4.md`

## Load This When

- The task changes quality inputs, measurement submission, backend evaluation, pass/fail/hold semantics, disposition, accepted-good handling, or quality gating against execution.
- The task writes quality specs, implementation plans, or reviews.

## Non-Negotiables

- Backend decides quality truth.
- Operators record inputs; they do not decide final quality outcome.
- Quality-owned decisions remain separate from operator actions.
- Quality state is orthogonal to execution state.
- Reported good is not automatically accepted good when QC gates exist.
- Auditability is mandatory for measurement submission, evaluation, and disposition.

## Required Modeling Rules

- Keep inspection template structure, submitted values, evaluation logic, and disposition decisions separate.
- Do not encode quality hold by inventing execution status names.
- When quality affects execution progression, model it as a gate or policy effect, not as frontend-only behavior.
- When quality affects quantities, describe whether the change applies to reported good, accepted good, scrap, or hold quantity.
- Quality Lite scope is narrow: do not invent SPC, laboratory workflows, CAPA, or supplier quality behavior unless explicitly requested and backed by design truth.

## Hard Mode Trigger

- If the change affects disposition authority, quality-to-execution gates, accepted-good truth, or audit/event semantics, escalate to Hard Mode MOM v3.

## Implementation Boundaries

- Frontend may capture measurements and render results, but must not authoritatively compute pass/fail/hold or accepted release.
- Avoid folding quality rules into generic UI helpers or presentation-only mappings.
- Keep policy, evaluation, and disposition logic server-side.

## Validation Focus

- Test measurement submission separately from evaluation outcomes.
- Test hold/disposition paths with explicit actor ownership.
- Verify quantity implications whenever quality status changes accepted-good truth.

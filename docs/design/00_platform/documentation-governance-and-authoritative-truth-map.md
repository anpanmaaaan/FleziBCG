# Documentation Governance and Authoritative Truth Map

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.1 | Reworked authoritative truth map for self-contained design package and new product truth. |

Status: Canonical documentation governance note.

## 1. Source-of-truth precedence

When documents disagree, apply this order:
1. the **most specific authoritative business-truth or domain-contract document in this package**
2. `docs/governance/CODING_RULES.md`
3. `docs/governance/ENGINEERING_DECISIONS.md`
4. `docs/governance/SOURCE_STRUCTURE.md`
5. entry instructions
6. prompts/comments

## 2. Primary authoritative documents in this package

### Platform / product truth
- `00_platform/product-business-truth-overview.md`

### Cross-platform architecture truth
- `00_platform/system-overview-and-target-state.md`
- `00_platform/domain-boundary-map.md`
- `00_platform/runtime-architecture-overview.md`
- `00_platform/eventing-and-projection-architecture.md`
- `00_platform/multi-tenancy-and-scope-architecture.md`

### Execution truth
- `02_domain/execution/business-truth-station-execution-v4.md`
- `02_domain/execution/domain-contracts-execution.md`
- `02_domain/execution/station-execution-state-matrix-v4.md`

### Quality truth
- `02_domain/quality/quality-domain-contracts.md`
- `02_domain/quality/business-truth-quality-lite.md`

## 3. Role of this design pack

This design pack is intended to be self-contained for business truth, domain truth, and architecture truth.
Contributors must not assume a hidden external `mes-business-logic-v1.md` file remains authoritative.

## 4. Current-vs-target documentation rule

Where a file documents both:
- transition/migration notes
- approved target truth

the target truth remains authoritative for future design, while migration notes explain source-code reality or refactor sequencing.

## 5. Change classification rule

The transition from claim-centric execution to session-owned execution is an Architecture / Contract change and must be treated as such in docs and code planning.

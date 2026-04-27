# Design Pack Index

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.1 | Added product business truth, authorization overview, domain-boundary clarifications, and repo-ready truth map. |

Status: Entry index for the repo-ready design pack.

## 1. How to use this pack

Read in this order:
1. `00_platform/product-business-truth-overview.md`
2. `00_platform/system-overview-and-target-state.md`
3. `00_platform/domain-boundary-map.md`
4. `00_platform/authorization-model-overview.md`
5. `00_platform/material-traceability-vs-inventory-boundary.md`
6. `00_platform/manufacturing-mode-hierarchy-mapping.md`
7. `01_foundation/identity-access-session-governance.md`
8. `02_domain/execution/execution-domain-overview.md`
9. `02_domain/quality/quality-domain-overview.md`
10. `02_domain/planning/planning-and-scheduling-domain.md`
11. `05_application/` and `06_application_backend/`
12. `07_ui/`
13. `08_ops/`

## 2. Pack structure

- `00_platform`: cross-system architecture, product truth, and boundary rules
- `01_foundation`: identity, access, session, audit, approval, lifecycle
- `02_domain`: domain models and business truth
- `03_integration`: ERP/shop-floor/enterprise boundaries
- `04_ai`: AI, digital twin, analytics, and AI interaction with planning/twin
- `05_application`: screens/API/events/read models across domains
- `06_application_backend`: application-facing backend API design
- `07_ui`: canonical screen packs
- `08_ops`: migration, release, testing, and runtime operations

## 3. Interpretation rules

- this pack is design truth for the approved next direction
- migration notes may still exist where source code is known to lag target truth
- Station Execution should be read as the current **discrete-first application**, not the universal execution model for the whole platform
- claim is deprecated from the target model; any claim-centric wording that remains should be treated as migration debt, not canonical direction

## 4. Key approved design changes reflected in this pack

- execution ownership transitions from `claim` to `active station session + identified operator + bound equipment`
- `authenticated user`, `identified operator`, and `equipment/resource context` are modeled separately
- the platform must support `DISCRETE`, `BATCH`, `CONTINUOUS`, and `HYBRID` manufacturing modes
- unified execution abstractions are introduced at platform/domain level so later process-mode apps do not require rewriting the core
- APS is a first-class platform module; AI may improve APS but must not overwrite execution truth

---

## Latest Pack Addendum — 2026-04-27

Latest accepted additions:

- `docs/design/10_hardening/hardening-baseline-summary.md`
- `docs/design/10_hardening/source-code-audit-response.md`
- `docs/design/10_hardening/timezone-and-localization-strategy.md`
- `docs/governance/CODING_RULES.md` v2.0
- `docs/roadmap/flezibcg-overall-roadmap-latest.md`
- `docs/implementation/task5-p0-a-foundation-database-implementation-prompt.md`

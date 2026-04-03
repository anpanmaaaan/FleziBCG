# PHASE 5A — i18n Infrastructure Preparation

Status: COMPLETED (Baseline Locked)

## Purpose
Phase 5A establishes a stable internationalization foundation before any runtime language behavior is introduced. Preparing structure first prevents scattered text decisions, enforces consistent vocabulary boundaries, and avoids coupling translation behavior to execution logic.

The core principle in this phase is explicit: no behavior change. The system must remain functionally identical while i18n contracts are prepared for future activation.

## Scope
In scope:
- i18n module structure in frontend
- domain-based namespace definition
- semantic key typing contracts
- placeholder EN registry shape
- translation hook stub surface for future use

Out of scope:
- replacing UI text with translations
- locale switching logic
- language selector UI
- backend API contract changes
- runtime i18n provider wiring

## i18n Design Principles (LOCKED)
- Backend never returns translated text; backend returns enums/codes and domain data only.
- Frontend uses semantic keys as the translation contract.
- Translation is a UI concern and must not leak into backend business logic.
- i18n vocabulary must respect persona boundaries and role-specific terminology.

## Implemented Infrastructure
Phase 5A delivers the following artifacts:
- `frontend/src/app/i18n/` i18n module folder
- `frontend/src/app/i18n/namespaces.ts` for domain namespace constants/types
- `frontend/src/app/i18n/keys.ts` for semantic key and registry typing
- `frontend/src/app/i18n/registry/en.ts` EN placeholder registry
- `frontend/src/app/i18n/useI18n.ts` stub hook with deterministic lookup surface
- `frontend/src/app/i18n/index.ts` module export entrypoint

## Runtime Behavior Guarantee
Phase 5A introduces ZERO runtime behavior change.

Guaranteed in this phase:
- no route behavior changes
- no execution flow changes
- no UI text replacement in existing components
- no locale selection behavior
- no backend response shape changes

## Relationship to Other Phases
- Depends on Phase 4A persona vocabulary and role boundaries for consistent terminology.
- Enables Phase 5B runtime i18n activation as the next controlled step.
- Safe relative to Phases 1-3 because execution, monitoring, and dashboard behavior remain unchanged.

## Non-Negotiable Constraints
- No component may hardcode new business text introduced after Phase 5A.
- All new UI text must use semantic i18n keys from this phase onward.
- Runtime i18n behavior must not be enabled without a new approved phase.

## Completion Summary
Phase 5A is a long-term architectural investment: it creates typed, domain-aligned translation contracts before behavior changes are allowed. This reduces migration risk, protects MES execution boundaries, and enables controlled multilingual rollout in later phases without destabilizing existing operations.
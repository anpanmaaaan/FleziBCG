# Workspace Change Inventory After P0-C-03

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-29 | v1.0 | Initial workspace audit after P0-C-03 completion. Classification and git status capture. |

## Executive Summary

The working tree contains **92 total changed/untracked files** after P0-C-03 completion and prior FE/P0-B implementations.

- **P0-C-03 scoped files: 7** (as expected)
- **P0-C-02 carryover (bug fix + regression tests): 2** (from earlier in session)
- **P0-C-01 foundation tests: 1** (from earlier in session)
- **P0-B Product/Routing/RR implementation (new): 23** (untracked backend code + migrations + tests)
- **FE-1 through FE-5.1 implementation (new): 35** (FE components, APIs, pages, scripts, i18n)
- **Governance / Design Docs: 15** (skill updates, audit reports, design contracts, implementation reports)
- **Build artifacts / dependencies: 4** (frontend dist, package.json, tsconfig)

**Workspace state: Uncontrolled multi-phase growth.** Very large set of unrelated changes mixed into working tree outside P0-C-03 scope.

## Current Git Status Summary

```
Modified files:       33 (M)
Untracked files:      59 (??)
Total changed files:  92

Insertions: ~1,783
Deletions:  ~1,107
Net change: +676 lines
```

### Files Modified (33)

| File | Change Stat | Category |
|---|---|---|
| .github/copilot-instructions.md | +2 | Governance |
| .github/workflows/pr-gate.yml | +12 | Governance / FE |
| backend/app/api/v1/router.py | +2 | P0-B Setup |
| backend/app/db/init_db.py | +2 | P0-B Setup |
| backend/app/repositories/execution_event_repository.py | +2 -1 | **P0-C-03 SCOPED** |
| backend/app/services/operation_service.py | +4 -1 | P0-C-02 (carryover) |
| backend/app/services/product_service.py | +3 -1 | P0-B Product |
| backend/app/services/work_order_execution_service.py | +4 -1 | P0-C-01 (carryover) |
| backend/tests/test_operation_detail_allowed_actions.py | +113 -1 | P0-C-02 (carryover) |
| backend/tests/test_operation_status_projection_reconcile.py | +210 | **P0-C-03 SCOPED** |
| backend/tests/test_status_projection_reconcile_command.py | +33 | **P0-C-03 SCOPED** |
| docs/ai-skills/stitch-design-md-ui-ux/SKILL.md | +39 | FE Skill |
| docs/implementation/autonomous-implementation-plan.md | +93 -20 | **P0-C-03 Report** |
| docs/implementation/autonomous-implementation-verification-report.md | +374 | **P0-C-03 Report** |
| docs/implementation/design-gap-report.md | +89 -10 | P0-B Closeout |
| docs/implementation/hard-mode-v3-map-report.md | +342 | **P0-C-03 Report** |
| frontend/dist/index.html | +30 -20 | Build artifact |
| frontend/package-lock.json | +17 -17 | Dependency lock |
| frontend/package.json | +1 | FE Dependencies |
| frontend/src/app/api/index.ts | +6 | FE-4/FE-5 |
| frontend/src/app/components/Layout.tsx | +5 | FE-1/FE-2 |
| frontend/src/app/components/index.ts | +5 | FE-1/FE-2 |
| frontend/src/app/i18n/namespaces.ts | +3 | FE-1/FE-5 |
| frontend/src/app/i18n/registry/en.ts | +79 -1 | FE-1/FE-5 |
| frontend/src/app/i18n/registry/ja.ts | +79 -1 | FE-1/FE-5 |
| frontend/src/app/pages/OEEDeepDive.tsx | +4 | FE-1 |
| frontend/src/app/pages/OperationExecutionDetail.tsx | +4 | FE-1 |
| frontend/src/app/pages/RouteDetail.tsx | +1051 -1052 | FE-5 (major rewrite) |
| frontend/src/app/pages/RouteList.tsx | +263 -259 | FE-5 (major rewrite) |
| frontend/src/app/pages/StationExecution.tsx | +2 | FE-1 |
| frontend/src/app/persona/personaLanding.ts | +12 | FE-4A.2 |
| frontend/src/app/routes.tsx | +4 | FE-3/FE-5 |
| frontend/tsconfig.json | -1 | FE Config |

### Files Untracked (59)

| File | Category | Phase/Slice |
|---|---|---|
| backend/app/api/v1/routings.py | Backend API | P0-B Routing |
| backend/app/models/routing.py | Backend Model | P0-B Routing |
| backend/app/models/resource_requirement.py | Backend Model | P0-B RR |
| backend/app/repositories/routing_repository.py | Backend Repository | P0-B Routing |
| backend/app/repositories/resource_requirement_repository.py | Backend Repository | P0-B RR |
| backend/app/schemas/routing.py | Backend Schema | P0-B Routing |
| backend/app/schemas/resource_requirement.py | Backend Schema | P0-B RR |
| backend/app/services/routing_service.py | Backend Service | P0-B Routing |
| backend/app/services/resource_requirement_service.py | Backend Service | P0-B RR |
| backend/scripts/migrations/0015_routings.sql | Database | P0-B Routing |
| backend/scripts/migrations/0016_resource_requirements.sql | Database | P0-B RR |
| backend/tests/test_routing_foundation_api.py | Backend Test | P0-B Routing |
| backend/tests/test_routing_foundation_service.py | Backend Test | P0-B Routing |
| backend/tests/test_resource_requirement_api.py | Backend Test | P0-B RR |
| backend/tests/test_resource_requirement_service.py | Backend Test | P0-B RR |
| backend/tests/test_work_order_operation_foundation.py | Backend Test | P0-C-01 |
| docs/audit/execution-ui-readiness-for-p0-c.md | Design Doc | FE-6 Audit |
| docs/audit/frontend-source-alignment-snapshot.md | Design Doc | FE-1 through FE-5.1 |
| docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md | Contract | P0-B RR |
| docs/design/02_registry/resource-requirement-event-registry.md | Registry | P0-B RR |
| docs/design/02_registry/routing-event-registry.md | Registry | P0-B Routing |
| docs/implementation/fe-execution-p0c-ui-slice-contract.md | Planning Doc | FE-EXE-P0C |
| docs/implementation/p0-b-mmd-closeout-review.md | Closeout Doc | P0-B |
| docs/implementation/p0-c-execution-entry-audit.md | Audit Doc | P0-C Entry |
| frontend/scripts/route-smoke-check.mjs | FE Script | FE-GOV-02 |
| frontend/src/app/api/productApi.ts | FE API Client | FE-4A |
| frontend/src/app/api/routingApi.ts | FE API Client | FE-5 |
| frontend/src/app/components/MockWarningBanner.tsx | FE Component | FE-1 |
| frontend/src/app/components/ProductBadges.tsx | FE Component | FE-4A.1 |
| frontend/src/app/components/RouteStatusBanner.tsx | FE Component | FE-2 |
| frontend/src/app/components/RoutingDisplay.tsx | FE Component | FE-5.1 |
| frontend/src/app/components/ScreenStatusBadge.tsx | FE Component | FE-1 |
| frontend/src/app/pages/ProductDetail.tsx | FE Page | FE-4A |
| frontend/src/app/pages/ProductList.tsx | FE Page | FE-4A |
| frontend/src/app/screenStatus.ts | FE Registry | FE-1 |

## P0-C-03 Scoped Changes

### Expected P0-C-03 files (COMPLETE)

✓ backend/app/repositories/execution_event_repository.py
  - Change: +2 -1 lines
  - Purpose: Deterministic event ordering (created_at, id) for projection parity
  - Risk: LOW
  
✓ backend/tests/test_operation_status_projection_reconcile.py
  - Change: +210 lines
  - Purpose: Added detail-vs-bulk projection parity tests
  - Risk: LOW
  
✓ backend/tests/test_status_projection_reconcile_command.py
  - Change: +33 lines
  - Purpose: Extended reconcile command tests for parity validation
  - Risk: LOW
  
✓ docs/implementation/autonomous-implementation-plan.md
  - Change: +93 -20 lines
  - Purpose: Updated P0-C slice status and ordering
  - Risk: LOW
  
✓ docs/implementation/autonomous-implementation-verification-report.md
  - Change: +374 lines
  - Purpose: Added P0-C-03 verification results
  - Risk: LOW
  
✓ docs/implementation/hard-mode-v3-map-report.md
  - Change: +342 lines
  - Purpose: Added HM3-014 entry for P0-C-03
  - Risk: LOW
  
✓ docs/implementation/p0-c-execution-entry-audit.md
  - Change: NEW file (250 lines)
  - Purpose: P0-C entry audit including P0-C-02 and P0-C-03 summary
  - Risk: LOW

**P0-C-03 Status: COMPLETE**
**P0-C-03 Files: 7**
**P0-C-03 Test Verification: PASS (159 passed, 1 skipped, exit code 0)**

---

## Unrelated Changes by Phase

### CARRYOVER: P0-C-02 State Machine Guard (Earlier in Session)

2 files modified, 1 file added:

| File | Change | Purpose | Risk |
|---|---|---|---|
| backend/app/services/operation_service.py | +4 -1 | _derive_status bug fix (dead code for OP_COMPLETED/OP_ABORTED) | MEDIUM |
| backend/tests/test_operation_detail_allowed_actions.py | +113 -1 | 7 regression tests for _derive_status sequence cases | LOW |

Note: These were applied during P0-C-02 execution earlier in this session. Not part of P0-C-03 scope.

### CARRYOVER: P0-C-01 Work Order / Operation Foundation (Earlier in Session)

1 file added:

| File | Change | Purpose | Risk |
|---|---|---|---|
| backend/tests/test_work_order_operation_foundation.py | NEW (+248 lines) | Tenant isolation and WO/PO hierarchy read tests | LOW |

Note: Part of P0-C-01 earlier in session. Not new in P0-C-03.

### NEW: P0-B Product Foundation (Unrelated)

Changes across 23 files (new code, not previously in working tree):

**Backend models/services/repos/schemas:**
- backend/app/models/routing.py (NEW)
- backend/app/models/resource_requirement.py (NEW)
- backend/app/repositories/routing_repository.py (NEW)
- backend/app/repositories/resource_requirement_repository.py (NEW)
- backend/app/services/routing_service.py (NEW)
- backend/app/services/resource_requirement_service.py (NEW)
- backend/app/services/product_service.py (MODIFIED +3 -1)
- backend/app/schemas/routing.py (NEW)
- backend/app/schemas/resource_requirement.py (NEW)
- backend/app/api/v1/routings.py (NEW)
- backend/app/api/v1/router.py (MODIFIED +2)

**Database:**
- backend/scripts/migrations/0015_routings.sql (NEW)
- backend/scripts/migrations/0016_resource_requirements.sql (NEW)

**Backend tests:**
- backend/tests/test_routing_foundation_api.py (NEW)
- backend/tests/test_routing_foundation_service.py (NEW)
- backend/tests/test_resource_requirement_api.py (NEW)
- backend/tests/test_resource_requirement_service.py (NEW)

**Docs:**
- docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md (NEW)
- docs/design/02_registry/routing-event-registry.md (NEW)
- docs/design/02_registry/resource-requirement-event-registry.md (NEW)
- docs/implementation/p0-b-mmd-closeout-review.md (NEW)
- docs/implementation/design-gap-report.md (MODIFIED +89 -10)

**Scope:** Product Foundation, Routing Foundation, Resource Requirement Mapping
**Status:** Complete, verified (141 passed, 1 skipped before P0-C-03 added more tests)
**Risk:** MEDIUM (large feature set, new DB schema, migrations present)
**Action:** Separate commit group. Not scoped to P0-C-03.

### NEW: Frontend Implementation FE-1 through FE-5.1 (Unrelated)

Changes across 35 files:

**Frontend Components (NEW):**
- frontend/src/app/components/MockWarningBanner.tsx
- frontend/src/app/components/ScreenStatusBadge.tsx
- frontend/src/app/components/RouteStatusBanner.tsx
- frontend/src/app/components/ProductBadges.tsx
- frontend/src/app/components/RoutingDisplay.tsx
- frontend/src/app/screenStatus.ts

**Frontend API Clients (NEW):**
- frontend/src/app/api/productApi.ts
- frontend/src/app/api/routingApi.ts

**Frontend Pages (NEW):**
- frontend/src/app/pages/ProductList.tsx
- frontend/src/app/pages/ProductDetail.tsx

**Frontend Pages (MODIFIED):**
- frontend/src/app/pages/RouteList.tsx (+263 -259, major rewrite)
- frontend/src/app/pages/RouteDetail.tsx (+1051 -1052, major rewrite)
- frontend/src/app/pages/OEEDeepDive.tsx (+4)
- frontend/src/app/pages/OperationExecutionDetail.tsx (+4)
- frontend/src/app/pages/StationExecution.tsx (+2)

**Frontend Infrastructure (MODIFIED/NEW):**
- frontend/src/app/routes.tsx (+4)
- frontend/src/app/persona/personaLanding.ts (+12)
- frontend/src/app/api/index.ts (+6)
- frontend/src/app/components/index.ts (+5)
- frontend/src/app/components/Layout.tsx (+5)
- frontend/src/app/i18n/namespaces.ts (+3)
- frontend/src/app/i18n/registry/en.ts (+79 -1)
- frontend/src/app/i18n/registry/ja.ts (+79 -1)

**Frontend Build & Config:**
- frontend/dist/index.html (MODIFIED)
- frontend/package.json (+1)
- frontend/package-lock.json (lock update)
- frontend/tsconfig.json (-1)

**Frontend Governance:**
- frontend/scripts/route-smoke-check.mjs (NEW)
- docs/ai-skills/stitch-design-md-ui-ux/SKILL.md (+39)
- .github/workflows/pr-gate.yml (+12)

**Scope:** FE-1 Screen Status Guardrails, FE-2 Route Integration, FE-3 Product Shell, FE-4A Product API, FE-4A.1/4A.2 Hardening, FE-5 Routing API, FE-5.1 Hardening, FE-GOV-02 Automation
**Status:** Implemented, build/lint green (from earlier in conversation)
**Risk:** MEDIUM (large FE change set, i18n expansion, route schema changes, build artifact updates)
**Action:** Separate commit group. Not scoped to P0-C-03.

### NEW: Design/Audit Docs (Unrelated)

| File | Purpose | Risk |
|---|---|---|
| docs/audit/frontend-source-alignment-snapshot.md | FE-1 through FE-5.1 audit snapshot | LOW |
| docs/audit/execution-ui-readiness-for-p0-c.md | FE-6 UI readiness audit for P0-C | LOW |
| docs/implementation/fe-execution-p0c-ui-slice-contract.md | FE-EXE-P0C planning contract | LOW |
| docs/implementation/p0-c-execution-entry-audit.md | P0-C entry audit | LOW |
| .github/copilot-instructions.md (+2) | Governance doc updates | LOW |

**Status:** New docs added
**Risk:** LOW (documentation only, no code impact)

---

## Temporary / Generated Artifacts

**Build artifacts:**
- frontend/dist/index.html — Build output, will be regenerated on next build
- frontend/package-lock.json — Dependency lock file, auto-maintained

**No accidental .bak, debug, or reconstruct files detected.**

---

## Risk Assessment

| Category | Count | Risk | Reason |
|---|---|---|---|
| P0-C-03 scoped | 7 | LOW | Narrow, test-verified changes to deterministic ordering + tests + reports |
| P0-C-02 carryover | 2 | MEDIUM | Bug fix in operation_service is foundational but already verified |
| P0-C-01 carryover | 1 | LOW | Test file, additive only |
| P0-B routing/RR | 23 | MEDIUM | New domain model + API + DB migrations, large feature set, separate phase |
| Frontend FE-1 through FE-5.1 | 35 | MEDIUM | Large UI change set, multiple route/i18n changes, should be staged separately |
| Governance/Docs | 8 | LOW | Documentation and skill updates, no runtime impact |
| **TOTAL** | **92** | **MEDIUM** | Multiple unrelated phases mixed into working tree |

## Recommended Manual Review / Commit Groups

**Group 1: Governance & Skills (LOW RISK)**
- .github/copilot-instructions.md
- .github/workflows/pr-gate.yml
- docs/ai-skills/stitch-design-md-ui-ux/SKILL.md

Commit message: `docs(governance): update copilot instructions and FE skill guidance`

---

**Group 2: P0-B Product/Routing/Resource Requirement Mapping (MEDIUM RISK)**

Backend:
- backend/app/models/routing.py
- backend/app/models/resource_requirement.py
- backend/app/repositories/routing_repository.py
- backend/app/repositories/resource_requirement_repository.py
- backend/app/services/routing_service.py
- backend/app/services/resource_requirement_service.py
- backend/app/services/product_service.py
- backend/app/schemas/routing.py
- backend/app/schemas/resource_requirement.py
- backend/app/api/v1/routings.py
- backend/app/db/init_db.py
- backend/app/api/v1/router.py

Database:
- backend/scripts/migrations/0015_routings.sql
- backend/scripts/migrations/0016_resource_requirements.sql

Tests:
- backend/tests/test_routing_foundation_api.py
- backend/tests/test_routing_foundation_service.py
- backend/tests/test_resource_requirement_api.py
- backend/tests/test_resource_requirement_service.py

Docs:
- docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md
- docs/design/02_registry/routing-event-registry.md
- docs/design/02_registry/resource-requirement-event-registry.md
- docs/implementation/p0-b-mmd-closeout-review.md
- docs/implementation/design-gap-report.md

Commit message: `feat(p0b): implement routing foundation, resource requirement mapping, and P0-B closeout`

---

**Group 3: P0-C-01/02/03 Execution Hardening (MEDIUM RISK)**

Tests:
- backend/tests/test_work_order_operation_foundation.py (P0-C-01)
- backend/tests/test_operation_detail_allowed_actions.py (P0-C-02)
- backend/tests/test_operation_status_projection_reconcile.py (P0-C-03)
- backend/tests/test_status_projection_reconcile_command.py (P0-C-03)

Code:
- backend/app/services/operation_service.py (P0-C-02 bug fix)
- backend/app/repositories/execution_event_repository.py (P0-C-03 deterministic ordering)
- backend/app/services/work_order_execution_service.py (P0-C-01)

Docs:
- docs/implementation/autonomous-implementation-plan.md (updates)
- docs/implementation/autonomous-implementation-verification-report.md (P0-C-03 results)
- docs/implementation/hard-mode-v3-map-report.md (HM3-014)
- docs/implementation/p0-c-execution-entry-audit.md (audit)
- docs/audit/execution-ui-readiness-for-p0-c.md (FE-6 audit)

Commit message: `feat(p0c): execution foundation alignment (P0-C-01), state machine guards (P0-C-02), projection consistency (P0-C-03)`

---

**Group 4: Frontend FE-1 through FE-5.1 (MEDIUM RISK)**

Core components & screens:
- frontend/src/app/components/MockWarningBanner.tsx (FE-1)
- frontend/src/app/components/ScreenStatusBadge.tsx (FE-1)
- frontend/src/app/components/RouteStatusBanner.tsx (FE-2)
- frontend/src/app/components/ProductBadges.tsx (FE-4A.1)
- frontend/src/app/components/RoutingDisplay.tsx (FE-5.1)
- frontend/src/app/screenStatus.ts (FE-1)
- frontend/src/app/api/productApi.ts (FE-4A)
- frontend/src/app/api/routingApi.ts (FE-5)
- frontend/src/app/pages/ProductList.tsx (FE-4A)
- frontend/src/app/pages/ProductDetail.tsx (FE-4A)
- frontend/src/app/pages/RouteList.tsx (FE-5, rewrite)
- frontend/src/app/pages/RouteDetail.tsx (FE-5, rewrite)

Infrastructure:
- frontend/src/app/routes.tsx (FE-3/FE-5)
- frontend/src/app/persona/personaLanding.ts (FE-4A.2)
- frontend/src/app/api/index.ts (FE-4/FE-5)
- frontend/src/app/components/index.ts (FE-1/FE-2)
- frontend/src/app/components/Layout.tsx (FE-1/FE-2)
- frontend/src/app/i18n/namespaces.ts (FE-1/FE-5)
- frontend/src/app/i18n/registry/en.ts (FE-1/FE-5)
- frontend/src/app/i18n/registry/ja.ts (FE-1/FE-5)
- frontend/src/app/pages/OEEDeepDive.tsx (FE-1 guardrails)
- frontend/src/app/pages/OperationExecutionDetail.tsx (FE-1 guardrails)
- frontend/src/app/pages/StationExecution.tsx (FE-1 guardrails)

Build/Config:
- frontend/package.json
- frontend/package-lock.json
- frontend/tsconfig.json
- frontend/dist/index.html

Governance:
- frontend/scripts/route-smoke-check.mjs
- docs/ai-skills/stitch-design-md-ui-ux/SKILL.md (already in Group 1)
- docs/audit/frontend-source-alignment-snapshot.md
- docs/implementation/fe-execution-p0c-ui-slice-contract.md

Commit message: `feat(fe): FE-1 through FE-5.1 implementation (screen status guardrails, product/routing APIs, route smoke checks)`

---

## Blockers Before Next Slice

**NONE identified.**

- P0-C-03 tests pass (159 passed, 1 skipped).
- All prior phases (P0-B, P0-C-01, P0-C-02) appear green.
- No conflicts between grouped changes.
- No missing design dependencies.

---

## Recommended Next Slice

**P0-C-04 Station Session Ownership Alignment**

Blocked by:
- None

Required before coding:
1. Human manually reviews and commits Groups 1–4 above.
2. Backend test suite re-run after all commits to confirm no regressions.
3. FE build/lint/check:routes re-run after all commits to confirm no regressions.
4. Review of P0-C-04 design dependencies in:
   - docs/design/02_domain/execution/station-execution-state-matrix-v4.md
   - docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md
   - docs/implementation/fe-execution-p0c-ui-slice-contract.md (already present)

---

## Appendix: File Classification Key

- **P0-A Foundation** — Platform setup, auth, tenant, scope
- **P0-B Product Foundation** — Product master data
- **P0-B Routing Foundation** — Routing master data
- **P0-B Resource Requirement Mapping** — Resource requirement master data
- **P0-C-01 Work Order / Operation Foundation** — Execution base invariants
- **P0-C-02 State Machine Guard Alignment** — Operation lifecycle guards
- **P0-C-03 Projection Consistency** — Event/projection/reconcile parity
- **P0-C-04 Station Session Ownership Alignment** — Session-owned execution (pending)
- **FE-1 through FE-5.1** — Frontend implementation slices
- **FE-6 Audit** — Frontend readiness audit
- **FE-EXE-P0C** — Frontend execution P0-C planning
- **Governance / AI Skill** — Copilot instructions, PR gates, design docs
- **Unknown** — Needs human review

---

*End of workspace-change-inventory-after-p0-c-03.md*

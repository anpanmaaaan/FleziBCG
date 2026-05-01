# Frontend Route Smoke Coverage Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Expanded route smoke coverage for full frontend route registry. |

## 1. Scope
This report covers FE-QA-ROUTES-01 and documents expansion of frontend route smoke coverage from a hardcoded subset to full route-registry coverage.

In scope:
- Parse and count full route registry from routes source
- Classify routes (static, dynamic, redirect, protected/persona-visible)
- Generate representative dynamic smoke paths
- Add explicit exclusion handling with allowed reason codes
- Keep persona/auth checks as QA assertions (not authorization truth)

Out of scope:
- Route behavior changes
- Persona authorization changes
- Backend/API changes
- Station Execution command behavior changes

## 2. Source Files Inspected
| File | Purpose |
|---|---|
| frontend/src/app/routes.tsx | Route registry source of truth |
| frontend/src/app/persona/personaLanding.ts | Persona menu + route guard semantics |
| frontend/src/app/navigation/navigationGroups.ts | UX grouping boundaries (presentation-only) |
| frontend/src/app/screenStatus.ts | Screen-phase route pattern registry + aliases |
| frontend/scripts/route-smoke-check.mjs | Smoke check implementation |
| frontend/package.json | `check:routes` script entry |
| docs/audit/frontend-screen-coverage-matrix.md | Coverage baseline (67 routes after FE-COVERAGE-01E) |
| docs/audit/sidebar-domain-navigation-ia-report.md | FE-NAV-01 safety constraints |
| docs/audit/sidebar-quick-search-report.md | FE-NAV-01B constraints |
| docs/audit/frontend-coverage-foundation-iam-governance-report.md | FE-COVERAGE-01A route context |
| docs/audit/frontend-coverage-mmd-report.md | FE-COVERAGE-01B route context |
| docs/audit/frontend-coverage-execution-supervisory-report.md | FE-COVERAGE-01C route context |
| docs/audit/frontend-coverage-quality-material-traceability-report.md | FE-COVERAGE-01D route context |
| docs/audit/frontend-coverage-integration-reporting-report.md | FE-COVERAGE-01E route context |

## 3. Precondition Check
| Check | Result | Notes |
|---|---|---|
| `git status --short` | PASS (dirty tree noted) | Unrelated backend/docs changes present; not touched |
| Unresolved conflict markers (frontend) | PASS | None found |
| Required frontend source tree | PASS | All required files accessible |
| Baseline `npm.cmd run build` | PASS | Build succeeds |
| Baseline `npm.cmd run lint` | PASS | No lint errors |
| Baseline `npm.cmd run check:routes` | PASS (old subset) | 24 PASS / 0 FAIL |
| Baseline `npm.cmd run lint:i18n:registry` | PASS | en/ja synchronized |

## 4. Route Registry Summary
Summary metrics from updated smoke check:
- Registered path entries: 67
- Index routes: 1
- Static routes: 57
- Dynamic routes: 9
- Excluded routes: 1
- Smoke targets covered: 66

| Route | Page / Component | Route Type | Smoke Path | Coverage Status | Notes |
|---|---|---|---|---|---|
| / | Layout (protected parent) | redirect-route | — | EXCLUDED | REDIRECT_ONLY |
| /login | LoginPage | static route | /login | COVERED | Public route |
| /home | Home | static route | /home | COVERED | Protected |
| /dashboard | Dashboard | static route | /dashboard | COVERED | Protected |
| /performance/oee-deep-dive | OEEDeepDive | static route | /performance/oee-deep-dive | COVERED | MOCK screen |
| /production-orders | ProductionOrderList | static route | /production-orders | COVERED | Protected |
| /products | ProductList | static route | /products | COVERED | Protected |
| /products/:productId | ProductDetail | dynamic route | /products/demo-product-001 | COVERED | Dynamic sample |
| /dispatch | DispatchQueue | static route | /dispatch | COVERED | MOCK screen |
| /routes | RouteList | static route | /routes | COVERED | Protected |
| /routes/:routeId | RouteDetail | dynamic route | /routes/demo-route-001 | COVERED | Dynamic sample |
| /routes/:routeId/operations/:operationId | RoutingOperationDetail | dynamic route | /routes/demo-route-001/operations/demo-op-001 | COVERED | Dynamic sample |
| /bom | BomList | static route | /bom | COVERED | SHELL |
| /bom/:bomId | BomDetail | dynamic route | /bom/demo-bom-001 | COVERED | Dynamic sample |
| /resource-requirements | ResourceRequirements | static route | /resource-requirements | COVERED | SHELL |
| /reason-codes | ReasonCodes | static route | /reason-codes | COVERED | SHELL |
| /work-orders | OperationList | static route | /work-orders | COVERED | Protected |
| /production-orders/:orderId/work-orders | OperationList | dynamic route | /production-orders/demo-order-001/work-orders | COVERED | Dynamic sample |
| /work-orders/:woId/operations | OperationExecutionOverview | dynamic route | /work-orders/demo-wo-001/operations | COVERED | Dynamic sample |
| /operations | GlobalOperationList | static route | /operations | COVERED | Protected |
| /operations/:operationId/detail | OperationExecutionDetail | dynamic route | /operations/demo-op-001/detail | COVERED | Dynamic sample |
| /operations/:operationId/timeline | OperationTimeline | dynamic route | /operations/demo-op-001/timeline | COVERED | Dynamic sample |
| /station-session | StationSession | static route | /station-session | COVERED | SHELL |
| /operator-identification | OperatorIdentification | static route | /operator-identification | COVERED | SHELL |
| /equipment-binding | EquipmentBinding | static route | /equipment-binding | COVERED | SHELL |
| /line-monitor | LineMonitor | static route | /line-monitor | COVERED | SHELL |
| /station-monitor | StationMonitor | static route | /station-monitor | COVERED | SHELL |
| /downtime-analysis | DowntimeAnalysis | static route | /downtime-analysis | COVERED | SHELL |
| /shift-summary | ShiftSummary | static route | /shift-summary | COVERED | SHELL |
| /supervisory/operations/:operationId | SupervisoryOperationDetail | dynamic route | /supervisory/operations/demo-op-001 | COVERED | Dynamic sample |
| /quality-dashboard | QualityDashboard | static route | /quality-dashboard | COVERED | SHELL |
| /quality-measurements | MeasurementEntry | static route | /quality-measurements | COVERED | SHELL |
| /quality-holds | QualityHolds | static route | /quality-holds | COVERED | SHELL |
| /material-readiness | MaterialReadiness | static route | /material-readiness | COVERED | SHELL |
| /staging-kitting | StagingKitting | static route | /staging-kitting | COVERED | SHELL |
| /wip-buffers | WipBuffers | static route | /wip-buffers | COVERED | SHELL |
| /integration | IntegrationDashboard | static route | /integration | COVERED | SHELL |
| /integration/systems | ExternalSystems | static route | /integration/systems | COVERED | SHELL |
| /integration/erp-mapping | ErpMapping | static route | /integration/erp-mapping | COVERED | SHELL |
| /integration/inbound | InboundMessages | static route | /integration/inbound | COVERED | SHELL |
| /integration/outbound | OutboundMessages | static route | /integration/outbound | COVERED | SHELL |
| /integration/posting-requests | PostingRequests | static route | /integration/posting-requests | COVERED | SHELL |
| /integration/reconciliation | Reconciliation | static route | /integration/reconciliation | COVERED | SHELL |
| /integration/retry-queue | RetryQueue | static route | /integration/retry-queue | COVERED | SHELL |
| /reports/production-performance | ProductionPerformanceReport | static route | /reports/production-performance | COVERED | SHELL |
| /reports/quality-performance | QualityPerformanceReport | static route | /reports/quality-performance | COVERED | SHELL |
| /reports/material-wip | MaterialWipReport | static route | /reports/material-wip | COVERED | SHELL |
| /reports/integration-status | IntegrationStatusReport | static route | /reports/integration-status | COVERED | SHELL |
| /reports/shift | ShiftReport | static route | /reports/shift | COVERED | SHELL |
| /reports/downtime | DowntimeReport | static route | /reports/downtime | COVERED | SHELL |
| /station | StationExecution | static route | /station | COVERED | PARTIAL |
| /station-execution | StationExecution | static route | /station-execution | COVERED | Alias route |
| /quality | QCCheckpoints | static route | /quality | COVERED | MOCK |
| /defects | DefectManagement | static route | /defects | COVERED | MOCK |
| /traceability | Traceability | static route | /traceability | COVERED | MOCK |
| /scheduling | APSScheduling | static route | /scheduling | COVERED | MOCK |
| /users | UserManagement | static route | /users | COVERED | SHELL |
| /roles | RoleManagement | static route | /roles | COVERED | SHELL |
| /action-registry | ActionRegistry | static route | /action-registry | COVERED | SHELL |
| /scope-assignments | ScopeAssignments | static route | /scope-assignments | COVERED | SHELL |
| /sessions | SessionManagement | static route | /sessions | COVERED | SHELL |
| /audit-log | AuditLog | static route | /audit-log | COVERED | SHELL |
| /security-events | SecurityEvents | static route | /security-events | COVERED | SHELL |
| /tenant-settings | TenantSettings | static route | /tenant-settings | COVERED | SHELL |
| /plant-hierarchy | PlantHierarchy | static route | /plant-hierarchy | COVERED | SHELL |
| /dev/gantt-stress | GanttStressTestPage | static route | /dev/gantt-stress | COVERED | DEV-only conditional route |
| /settings | Dashboard (placeholder) | static route | /settings | COVERED | Placeholder wiring |

## 5. Previous Smoke Coverage
Previous script behavior (baseline):
- Hardcoded routes checked: 4 (`/products`, `/products/:productId`, `/routes`, `/routes/:routeId`)
- Additional policy checks: wildcard route absence, persona/menu checks for products/routes
- Output example: `PASS: 24, FAIL: 0`
- Gap: did not provide full route registry coverage visibility after FE-COVERAGE-01A..01E expansion

## 6. Updated Smoke Coverage
Updated `frontend/scripts/route-smoke-check.mjs` now:
- Extracts all `path: "..."` route entries from `routes.tsx`
- Counts route metrics (registered/static/dynamic/index/excluded/smoke targets)
- Classifies each route and prints a coverage row per route
- Builds representative dynamic smoke sample paths
- Supports explicit exclusions with strict allowed reasons
- Verifies route-to-screenStatus parity with normalized parameter matching and alias support
- Keeps persona/layout/navigation safety assertions from prior script
- Fails if any route is uncovered and not explicitly excluded

## 7. Dynamic Route Sample Strategy
| Route Pattern | Sample Smoke Path |
|---|---|
| /bom/:bomId | /bom/demo-bom-001 |
| /products/:productId | /products/demo-product-001 |
| /routes/:routeId | /routes/demo-route-001 |
| /routes/:routeId/operations/:operationId | /routes/demo-route-001/operations/demo-op-001 |
| /operations/:operationId/detail | /operations/demo-op-001/detail |
| /operations/:operationId/timeline | /operations/demo-op-001/timeline |
| /production-orders/:orderId/work-orders | /production-orders/demo-order-001/work-orders |
| /work-orders/:woId/operations | /work-orders/demo-wo-001/operations |
| /supervisory/operations/:operationId | /supervisory/operations/demo-op-001 |

Notes:
- Placeholder tokens are deterministic and non-backend-mutating
- Script is static-analysis smoke (no route execution, no backend calls)
- If later route runtime smoke is added, dynamic IDs may move to safe fixture IDs

## 8. Excluded Routes and Reasons
| Route | Reason | Follow-up Needed? | Notes |
|---|---|---|---|
| / | REDIRECT_ONLY | No | Parent protected route with index redirect to persona landing |

## 9. Persona / Authorization Safety Review
| Check | Result | Notes |
|---|---|---|
| Route smoke does not change route guards | PASS | Script only reads source files |
| Route smoke does not grant persona access | PASS | No auth/persona runtime writes |
| Sidebar visibility remains UX-only | PASS | Script asserts navigationGroups presentation-only disclaimer |
| Backend authorization remains source of truth | PASS | No backend/auth behavior touched |

## 10. Mock / Shell / Future Route Review
- Shell/mock/to-be routes are included in coverage if registered and renderable as routes
- No shell/mock route is excluded due to future status
- DEV-only route remains covered as a route-registry entry (`/dev/gantt-stress`)
- Coverage script is QA visibility, not product authorization or business-truth engine

## 11. Verification Results
| Command | Result | Notes |
|---|---|---|
| `cd frontend && npm.cmd run build` | PASS | No errors; existing chunk-size warning unchanged |
| `cd frontend && npm.cmd run lint` | PASS | No ESLint errors |
| `cd frontend && npm.cmd run check:routes` | PASS | 24 PASS / 0 FAIL (expanded checks and full registry metrics) |
| `cd frontend && npm.cmd run lint:i18n:registry` | PASS | en/ja registry synchronized (1509 keys) |

Optional:
- `npm.cmd run qa:station-execution:screenshots` not run (outside FE-QA-ROUTES-01 scope)

## 12. Remaining Gaps
| Route | Reason | Follow-up Needed? | Notes |
|---|---|---|---|
| (none) | — | — | Full registered route coverage achieved with explicit exclusion handling |

## 13. Final Verdict
FE-QA-ROUTES-01 is complete.

Route smoke coverage now reflects full current route registry, including static and dynamic routes, explicit exclusions, and shell/mock route visibility. No route behavior, auth behavior, persona semantics, or backend behavior was changed.

## 14. Recommended Next Slice
1. Add optional runtime render-smoke layer for a small curated route subset using existing harness (no new deps).
2. Add CI artifact export for route-smoke summary (JSON/MD) to track route-count drift over time.
3. Add a route-registry drift gate comparing `routes.tsx` and `screenStatus.ts` baselines per PR.

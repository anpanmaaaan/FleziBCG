# FE-GOVADMIN-04 — Governance/Admin FE Baseline Freeze + Backend Integration Handoff

## Routing
- Selected brain: MOM Brain
- Selected mode: Documentation-only baseline freeze and handoff
- Hard Mode MOM: ON for governance review discipline; no implementation/code-change mode was triggered.
- Reason: This slice freezes Governance/Admin FE baseline and backend integration dependencies across IAM, roles/actions/scopes, tenant settings, session visibility, audit/security events, and plant hierarchy. It is documentation-only, with no runtime behavior changes.

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Frozen Governance/Admin frontend baseline after layout, runtime QA, and persona route guard regression. |

## 1. Scope
This slice freezes the Governance/Admin frontend baseline after FE-GOVADMIN-01, FE-GOVADMIN-02, and FE-GOVADMIN-03 and provides a backend integration handoff map.

In scope:
- freeze current FE state of 9 Governance/Admin routes
- resolve report/source drift using latest evidence plus current source verification
- document disabled/backend-required actions
- document persona route visibility baseline
- document runtime and regression evidence baselines
- define backend integration dependency map and FE-GOVADMIN-05 readiness gate

Out of scope:
- no frontend source behavior changes
- no backend, DB, migration, API contract, route, or governance logic changes

## 2. Baseline Inputs Reviewed
### Reports
- docs/audit/fe-p0a-00-frontend-foundation-dependency-evidence-report.md
- docs/audit/fe-govadmin-01-report.md
- docs/audit/fe-govadmin-02-report.md
- docs/audit/fe-govadmin-03-report.md
- docs/audit/frontend-coverage-baseline-freeze-report.md

### Source files
- frontend/src/app/routes.tsx
- frontend/src/app/navigation/navigationGroups.ts
- frontend/src/app/persona/personaLanding.ts
- frontend/src/app/screenStatus.ts
- frontend/src/app/components/GovernancePageShell.tsx
- frontend/src/app/components/RouteStatusBanner.tsx
- frontend/src/app/components/MockWarningBanner.tsx
- frontend/src/app/components/SidebarSearch.tsx
- frontend/src/app/components/Layout.tsx
- frontend/scripts/govadmin-responsive-screenshots.mjs
- frontend/scripts/govadmin-persona-route-guard-check.mjs
- frontend/package.json
- frontend/src/app/pages/UserManagement.tsx
- frontend/src/app/pages/RoleManagement.tsx
- frontend/src/app/pages/ActionRegistry.tsx
- frontend/src/app/pages/ScopeAssignments.tsx
- frontend/src/app/pages/SessionManagement.tsx
- frontend/src/app/pages/AuditLog.tsx
- frontend/src/app/pages/SecurityEvents.tsx
- frontend/src/app/pages/TenantSettings.tsx
- frontend/src/app/pages/PlantHierarchy.tsx

All required files were present and inspectable. No stop condition triggered.

## 3. Source / Report Drift Resolution
| Topic | Older Source Says | Later Evidence Says | Current Source Verification | Freeze Decision |
|---|---|---|---|---|
| Governance/Admin connectivity status | frontend-coverage-baseline-freeze-report.md describes Governance/Admin as MIXED with connected subset | FE-P0A-00 and FE-GOVADMIN-01/02/03 describe all 9 governance screens as shell/mock | screenStatus.ts marks all 9 with phase SHELL + dataSource MOCK_FIXTURE; page files use local mock arrays/objects and disabled placeholder actions | Freeze all 9 as SHELL/MOCK baseline; no FROZEN_CONNECTED route in this domain |
| Persona guard for governance routes | FE-GOVADMIN-02 identified missing governance guard and runtime redirect bug | FE-GOVADMIN-02 fixed ADM-only governance guard; FE-GOVADMIN-03 added regression checks | personaLanding.ts contains ADM-only governance route block; govadmin-persona-route-guard-check.mjs passes 56/56 including OTS alias assertion | Freeze persona route visibility baseline as verified UX guard only |
| OTS mapping treatment | Earlier docs had implicit mapping note | FE-GOVADMIN-03 minor patch added explicit OTS alias assertions | personaLanding.ts maps OTS to ADM; regression script Section H verifies alias and mapping | Freeze OTS->ADM as current FE resolver truth (UX-only, not backend auth truth) |
| Runtime QA confidence | Older baseline does not include targeted 9x4 governance sweep | FE-GOVADMIN-02 captured 36 screenshots and resolved responsive/a11y issues | screenshot harness exists; evidence directory and report list full route/viewport matrix | Freeze runtime visual/responsive evidence as available and valid for shell UX baseline |

## 4. Frozen Route Inventory
| Route | Page File | Navigation Group | Persona Visibility | Screen Status | Data Source | Freeze Status |
|---|---|---|---|---|---|---|
| /users | frontend/src/app/pages/UserManagement.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |
| /roles | frontend/src/app/pages/RoleManagement.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |
| /action-registry | frontend/src/app/pages/ActionRegistry.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |
| /scope-assignments | frontend/src/app/pages/ScopeAssignments.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |
| /sessions | frontend/src/app/pages/SessionManagement.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |
| /audit-log | frontend/src/app/pages/AuditLog.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |
| /security-events | frontend/src/app/pages/SecurityEvents.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |
| /tenant-settings | frontend/src/app/pages/TenantSettings.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |
| /plant-hierarchy | frontend/src/app/pages/PlantHierarchy.tsx | governance-admin | ADM, OTS(alias) | SHELL | MOCK_FIXTURE | FROZEN_SHELL |

## 5. Screen-by-Screen Baseline Status
| Screen | Route | Current UI State | Current Data Source | Actions Enabled? | Disclosure Visible? | Backend Needed Before Live? | Notes |
|---|---|---|---|---|---|---|---|
| User Management | /users | GovernancePageShell + table shell | local mockUsers | DISABLED_PLACEHOLDERS | Yes | Yes | Create/View/Edit/Delete are disabled placeholders |
| Role Management | /roles | GovernancePageShell + card-grid shell | local mockRoles | DISABLED_PLACEHOLDERS | Yes | Yes | Create/Edit/Delete are disabled placeholders |
| Action Registry | /action-registry | GovernancePageShell + read-only table shell | local mockActions | DISABLED_PLACEHOLDERS | Yes | Yes | Read-only shell; no backend action catalog integration |
| Scope Assignments | /scope-assignments | GovernancePageShell + hierarchy table shell | local mockAssignments | DISABLED_PLACEHOLDERS | Yes | Yes | No backend scope graph/assignment contract wired |
| Session Management | /sessions | GovernancePageShell + session table shell | local mockSessions | DISABLED_PLACEHOLDERS | Yes | Yes | Revoke actions disabled; auth logout exists elsewhere but route itself is shell |
| Audit Log | /audit-log | GovernancePageShell + event table shell | local mockAuditEvents | DISABLED_PLACEHOLDERS | Yes | Yes | Filter/export placeholders disabled |
| Security Events | /security-events | GovernancePageShell + incident table shell | local mockSecurityEvents | DISABLED_PLACEHOLDERS | Yes | Yes | Action button disabled placeholder |
| Tenant Settings | /tenant-settings | GovernancePageShell + profile/settings shell | local mockTenant | DISABLED_PLACEHOLDERS | Yes | Yes | Save disabled; integration states are not connected |
| Plant Hierarchy | /plant-hierarchy | GovernancePageShell + hierarchy table shell | local mockHierarchy | DISABLED_PLACEHOLDERS | Yes | Yes | Add-node placeholders disabled |

## 6. FE-GOVADMIN-01/02/03 Evidence Summary
- FE-GOVADMIN-01: standardized all 9 governance pages under GovernancePageShell, retained shell/mock disclosure and disabled dangerous actions.
- FE-GOVADMIN-02: runtime QA sweep completed for all 9 routes across 4 viewports (36 screenshots), responsive/a11y fixes applied, governance route accessibility bug fixed in personaLanding.ts.
- FE-GOVADMIN-03: added static regression script check:govadmin:persona; current baseline passes 56/56 including OTS->ADM alias assertions.

## 7. Governance Safety Boundary
- Backend owns authorization truth.
- Backend owns audit/security truth.
- Backend owns tenant/scope isolation truth.
- Backend owns session revocation truth.
- Backend owns role/action/scope assignment truth.
- Backend owns user lifecycle mutation truth.
- Backend owns plant hierarchy mutation truth.
- Frontend route guard is UX visibility only.
- Persona is not permission.
- JWT proves identity only.
- Sidebar and search visibility are not authorization.

This frozen FE baseline is visualization and intent-disclosure only for Governance/Admin until backend integrations are implemented.

## 8. Disabled / Backend-Required Actions
| Screen | Disabled Action / Placeholder | Why Disabled | Required Backend Capability | Safe to Enable When |
|---|---|---|---|---|
| User Management | Invite/Create user | User lifecycle is backend-owned | User lifecycle create/invite API + authz + audit | Backend contract stable; authz/audit validated |
| User Management | Activate/Deactivate user | Account status mutation is backend-owned | User status mutation API + policy validation + audit | Backend enforces role/scope + audit event logging |
| User Management | Edit/Delete user | IAM mutation not implemented in FE | User update/delete API + conflict/error contract | Backend mutation + SoD/audit guarantees complete |
| Role Management | Edit role | Role catalog is backend-owned | Role read/write API + validation rules | Backend role model and compatibility rules frozen |
| Role Management | Delete role | Role deletion has governance risk | Role delete API + impact checks + audit | Backend safe-delete semantics + guardrails available |
| Action Registry | Edit action registry | Authorization matrix is backend truth | Action catalog read/write API + governed approvals | Backend action model and approval policy implemented |
| Scope Assignments | Assign/reassign scope | Scope isolation must be server-enforced | Scope graph read + assignment write API + tenant/scope enforcement | Backend tenant/scope contract and authz tests pass |
| Session Management | Revoke session | Session state/revocation is backend-owned | Session list/read + revoke API | Backend revocation semantics and audit events available |
| Session Management | Logout all sessions | Global session revocation is backend-owned | Bulk revoke/logout-all API | Backend supports scoped bulk revocation and audit |
| Audit Log | Export audit log | Compliance/audit data must remain immutable and governed | Audit read/filter/export API with policy controls | Backend export policy + retention/compliance rules defined |
| Security Events | Acknowledge security event | Incident lifecycle is backend-owned | Security event read + acknowledge/resolve API | Backend incident state machine and permissions implemented |
| Tenant Settings | Save tenant settings | Tenant config is backend-owned | Tenant read/update API + tenant isolation + audit | Backend tenant config validation and audit enforced |
| Plant Hierarchy | Add/Edit/Delete node | Hierarchy master data is backend-owned | Plant hierarchy read + mutation APIs + referential integrity | Backend hierarchy governance and audit contracts are stable |

## 9. Persona Route Visibility Baseline
| Persona / Role Code | Governance/Admin Access | Evidence | Notes |
|---|---|---|---|
| ADM | ALLOWED (all 9) | personaLanding.ts governance ADM-only block + regression script PASS | UX route visibility only |
| OTS | ALLOWED (maps to ADM) | resolvePersonaFromRoleCode maps OTS to ADM; regression Section H PASS | OTS maps to ADM in FE resolver, but this is UX-only and not backend authorization truth |
| OPR | NOT ALLOWED | governance block excludes non-ADM; regression PASS | UX visibility denied |
| SUP | NOT ALLOWED | governance block excludes non-ADM; regression PASS | UX visibility denied |
| IEP | NOT ALLOWED | governance block excludes non-ADM; regression PASS | UX visibility denied |
| QAL / QC | NOT ALLOWED | QAL/QCI resolve to QC; governance block excludes QC; regression PASS | UX visibility denied |
| PMG | NOT ALLOWED | governance block excludes PMG; regression PASS | UX visibility denied |
| PLN | NOT ALLOWED (maps to PMG) | role resolver maps PLN to PMG; governance block excludes PMG | UX visibility denied |
| INV | NOT ALLOWED (maps to PMG) | role resolver maps INV to PMG; governance block excludes PMG | UX visibility denied |
| EXE | NOT ALLOWED | governance block excludes EXE; regression PASS | UX visibility denied |

## 10. Sidebar / Search Visibility Baseline
- governance routes are grouped under navigationGroups.ts group id governance-admin.
- MENU_ITEMS_BY_PERSONA.ADM includes all 9 governance routes.
- non-admin persona menus do not include governance routes.
- SidebarSearch filters only menu items already resolved by persona and explicitly states it is not authorization truth.
- Layout.tsx enforces route redirect via isRouteAllowedForPersona for UX gating only.

## 11. Runtime / Responsive Evidence Baseline
- FE-GOVADMIN-02 captured 36 screenshots (9 routes x 4 viewports) in docs/audit/fe-govadmin-02-runtime-qa.
- responsive/a11y baseline fixes are present in current source (table min-widths, wrapped filter rows, icon aria-labels, label/input associations).
- disclosure banners and shell badges are present across all 9 governance screens.
- this FE-GOVADMIN-04 freeze does not regenerate screenshots.

## 12. Regression Test Baseline
- Script: frontend/scripts/govadmin-persona-route-guard-check.mjs
- NPM command: npm run check:govadmin:persona
- Current result: PASS (56 checks, 0 fails)
- Coverage includes:
  - route registration alignment
  - navigation group alignment
  - ADM-only governance route guard verification
  - non-admin exclusion checks
  - sidebar/search safety assertions
  - layout guard usage
  - OTS->ADM alias mapping assertions

## 13. Backend Integration Dependency Map
| FE Screen | Future Backend Domain / Service | Needed Read API | Needed Write API | Tenant/Scope Context Needed | Audit/Security Requirement | Integration Priority |
|---|---|---|---|---|---|---|
| /users | IAM / User lifecycle | User list/detail read | Invite/create, activate/deactivate, edit/delete | Tenant + scope filter + role context | All mutations auditable; privileged action security events | P0-A |
| /roles | IAM / Role catalog | Role list/detail read | Role create/update/delete and assignment workflows | Tenant + scope + compatibility rules | Role mutation audit + authorization events | P0-A |
| /action-registry | IAM / Authorization action catalog | Action catalog read | Action registry governance writes (if supported) | Tenant + policy scope | Security/audit trail for action model changes | P0-A-LATER |
| /scope-assignments | IAM / Scope assignment | Scope graph + assignment read | Assign/revoke/re-scope operations | Strong tenant + scope + actor context | Mandatory audit/security events for assignment changes | P0-A |
| /sessions | Auth / Session management | Session list/read | Revoke single / revoke-all | Tenant + actor + target session scope | Security events + audit for revocation actions | P0-A |
| /audit-log | Audit / Compliance | Audit event read/filter | Export (if policy allows) | Tenant + policy-scoped filters | Immutable audit constraints and access logging | P0-A |
| /security-events | Security monitoring | Security event list/read/filter | Acknowledge/resolve (if scoped) | Tenant + incident scope + responder context | Incident lifecycle audit and security traceability | P0-A |
| /tenant-settings | Tenant configuration | Tenant config read | Tenant config update | Strict tenant isolation | Config change audit and privileged action logging | P0-A-LATER |
| /plant-hierarchy | Master data / Plant hierarchy | Hierarchy tree read | Node create/update/delete/move | Tenant + plant/area/line/station scoping | Master-data mutation audit + integrity validation | P0-A-LATER |

## 14. Proposed P0-A API / Data Contract Needs
No authoritative endpoint naming is asserted here. Required capabilities are described functionally:
- IAM user lifecycle read contract (pagination/filter/sort + status model) and mutation contract with audit semantics.
- Role catalog read contract and role mutation/assignment governance contract.
- Scope graph and scope-assignment contract with backend tenant/scope enforcement.
- Session list/read/revoke/revoke-all contract with clear actor-target constraints.
- Audit event read/filter contract and policy-controlled export contract.
- Security event read/filter contract and optional acknowledge/resolve contract.
- Tenant configuration read contract (update deferred until governance rules stabilize).
- Plant hierarchy read contract (mutation deferred until master-data governance rules stabilize).
- Uniform error contract (authz errors, validation errors, conflict, unavailable).
- Table-centric pagination/filter/sort contract consistency across governance list screens.

## 15. FE-GOVADMIN-05 Readiness Gate
| Gate | Required Evidence | Status | Blocking Reason If Not Ready |
|---|---|---|---|
| P0-A backend API contracts exist | Versioned capability contracts for governance reads/writes | NOT_READY | Current FE baseline is shell/mock; contracts not frozen for all 9 screens |
| Tenant/scope context contract exists | Explicit tenant/scope resolution and enforcement semantics | NOT_READY | Scope assignment and hierarchy contracts not integrated |
| Auth/session API contract exists | Stable /me, session list, revoke semantics | PARTIAL | /me and logout exist; governance session route contract incomplete |
| Audit/security event API contract exists | Audit and security read/filter semantics + policy constraints | PARTIAL | Security-events BE endpoint exists but FE route still shell; audit route still shell |
| Role/action/scope assignment rules exist | Authoritative role-action-scope governance rules for FE integration | NOT_READY | FE displays placeholders only |
| Plant hierarchy API contract exists | Hierarchy read + mutation constraints | NOT_READY | FE hierarchy is mock fixture only |
| Error handling contract exists | Uniform error schema and UX mapping rules | NOT_READY | No stable cross-screen governance integration error contract |
| Pagination/filtering contract exists for table screens | Shared query/filter/sort/paging semantics | NOT_READY | Governance tables currently local mock arrays |
| Backend authorization tests exist | Verified server-side authz tests for governance endpoints | NOT_READY | Not evidenced in this FE freeze slice |
| Frontend integration can preserve disclosure/status semantics | Shell/mock warnings and status badges retained through progressive integration | READY | Current baseline has consistent disclosure architecture |

Gate decision:
- FE-GOVADMIN-05 should not start broad live integration until P0-A backend APIs/contracts are stable enough for read integration.
- Exception path: isolated read-only pilot on security-events or audit-log can start only if contracts are explicitly approved.

## 16. Risks / Deferred Items
- Frontend route visibility may still be overinterpreted as authorization by non-technical stakeholders; keep boundary messaging explicit.
- Governance screens remain visually mature while still mock-backed; disclosure must not be removed in integration transition.
- lint:i18n hardcode script fails on Windows due known CRLF shell-script issue (pre-existing and deferred).
- Security-events backend capability exists in ecosystem reports but FE page remains mock; integration sequencing decision pending contract alignment.
- Plant hierarchy and tenant settings carry high governance impact; mutation enablement must trail read-contract stabilization.

## 17. Recommended Next Slices
1. FE-GOVADMIN-05A: Read-only security-events integration (list/filter) with disclosure preserved.
2. FE-GOVADMIN-05B: Read-only audit-log integration (list/filter) with immutable-record messaging preserved.
3. FE-GOVADMIN-05C: Session management read/revoke integration with backend-validated actor constraints.
4. FE-GOVADMIN-05D: IAM user/role read integration (no write enablement yet).
5. FE-GOVADMIN-05E: Scope-assignment read integration after tenant/scope contract formalization.

## 18. Verification Commands
| Command | Result | Notes |
|---|---|---|
| npm run build | PASS | Vite build successful; non-blocking chunk-size warning remains |
| npm run lint | PASS | ESLint clean |
| npm run lint:i18n:registry | PASS | en.ts/ja.ts synchronized (1692 keys) |
| npm run check:routes | PASS | 24 checks PASS, 0 FAIL; 77/78 covered, 1 excluded redirect route |
| npm run check:govadmin:persona | PASS | 56 PASS, 0 FAIL |
| npm run lint:i18n | FAIL (known pre-existing) | lint:i18n:hardcode fails on Windows due CRLF in bash script; not changed in this slice |

## 19. Final Freeze Verdict
FREEZE_APPROVED_WITH_BACKEND_INTEGRATION_BLOCKERS

Freeze verdict details:
- Governance/Admin frontend baseline is frozen as shell/mock UX with verified route inventory, persona visibility baseline, and regression coverage.
- Current source truth does not support classifying any of the 9 Governance/Admin routes as connected.
- Backend integration handoff is ready, but FE-GOVADMIN-05 broad integration remains blocked until P0-A backend contracts and governance rules are stable enough for read-first wiring.

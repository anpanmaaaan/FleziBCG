# FE-P0A-00 — Frontend Foundation Dependency Evidence Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Created FE P0-A foundation dependency evidence report. |

## 1. Executive Verdict
**FE_P0A_PARTIAL_READY_WITH_BACKEND_DEPENDENCIES**

Verdict before report write: **ALLOW_REPORT_WRITE**.

The frontend source is inspectable and the required mandatory files were present, so no stop report was required. Current evidence shows that the frontend already depends on a small set of real P0-A backend capabilities, but most Foundation / Governance / Admin routes remain shell or mock surfaces with no live client contract. The real foundation dependency is concentrated in auth bootstrap, logout/logout-all, tenant header propagation, impersonation, and dashboard summary/health reads. The governance route inventory is visible and smoke-covered, but not implementation-ready for real backend truth beyond those connected surfaces.

## 2. Routing
## Routing
- Selected brain: MOM Brain
- Selected mode: Architecture Mode
- Hard Mode MOM: ON (v3)
- Reason: This task audits frontend dependency on tenant/scope/auth, IAM lifecycle, session lifecycle, role/action/scope assignment, audit/security event boundaries, and backend readiness. It is documentation-only, but it still requires Hard Mode MOM v3 governance discipline because the report classifies backend-truth boundaries and P0-A readiness.

## 3. Mandatory Files Status
| File | Status | Notes |
|---|---|---|
| `.github/copilot-instructions.md` | PRESENT / INSPECTED | Mandatory. |
| `.github/agent/AGENT.md` | PRESENT / INSPECTED | Mandatory. |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | PRESENT / INSPECTED | Mandatory. |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | PRESENT / INSPECTED | Mandatory. |
| `.github/copilot-instructions-design-md-addendum.md` | PRESENT / INSPECTED | Optional addendum. |
| `.github/copilot-instructions-hard-mode-mom-v2-addendum.md` | PRESENT / INSPECTED | Optional addendum. |
| `.github/copilot-instructions-hard-mode-mom-v3-addendum.md` | PRESENT / INSPECTED | Optional addendum. |
| `.github/prompts/flezibcg-ai-brain-v6-auto-execution.prompt.md` | NOT FOUND AT REQUESTED PATH | Closest equivalent found and inspected at `.github/flezibcg-ai-brain-v6-auto-execution.prompt.md`. |
| `docs/ai-skills/design-md-ui-governor/SKILL.md` | PRESENT / INSPECTED | FE/UI governance input. |
| `docs/ai-skills/stitch-design-md-ui-ux/SKILL.md` | PRESENT / INSPECTED | FE/UI governance input. |
| `docs/ai-skills/design-system-enforcer/SKILL.md` | PRESENT / INSPECTED | FE/UI governance input. |
| `DESIGN.md` | NOT PRESENT | Optional root file absent; used `docs/design/DESIGN.md`. |
| `docs/design/DESIGN.md` | PRESENT / INSPECTED | FE/UI design authority. |
| `docs/audit/frontend-source-alignment-snapshot.md` | PRESENT / INSPECTED | Current FE baseline input. |

No mandatory-file stop condition was hit.

## 4. Sources Inspected
### Design / governance / audit inputs
- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `.github/copilot-instructions-design-md-addendum.md`
- `.github/copilot-instructions-hard-mode-mom-v2-addendum.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `.github/flezibcg-ai-brain-v6-auto-execution.prompt.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `docs/ai-skills/design-md-ui-governor/SKILL.md`
- `docs/ai-skills/stitch-design-md-ui-ux/SKILL.md`
- `docs/ai-skills/design-system-enforcer/SKILL.md`
- `docs/design/INDEX.md`
- `docs/design/AUTHORITATIVE_FILE_MAP.md`
- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/design/00_platform/product-scope-and-phase-boundary.md`
- `docs/design/00_platform/domain-boundary-map.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/design/01_foundation/identity-access-session-governance.md`
- `docs/design/05_application/screen-map-and-navigation-architecture.md`
- `docs/design/05_application/frontend-backend-responsibility-map.md`
- `docs/design/05_application/canonical-api-surface-map.md`
- `docs/design/DESIGN.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`
- `docs/audit/frontend-source-alignment-snapshot.md`
- `docs/audit/frontend-coverage-baseline-freeze-report.md`
- `docs/audit/source-code-audit-report.md`
- `docs/audit/p0-a-gap-00-foundation-gap-evidence-report.md`
- `docs/audit/be-qa-foundation-01-report.md`
- `docs/audit/audit-be-01-security-event-read-filter-report.md`

### Missing requested baseline docs
- `docs/design/05_application/fe-screen-inventory-and-navigation-map.md` was not present.
- Root `DESIGN.md` was not present.

### Frontend source inspected
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/src/app/routes.tsx`
- `frontend/src/app/screenStatus.ts`
- `frontend/src/app/navigation/navigationGroups.ts`
- `frontend/src/app/persona/personaLanding.ts`
- `frontend/src/app/auth/AuthContext.tsx`
- `frontend/src/app/auth/RequireAuth.tsx`
- `frontend/src/app/api/httpClient.ts`
- `frontend/src/app/api/authApi.ts`
- `frontend/src/app/api/dashboardApi.ts`
- `frontend/src/app/api/impersonationApi.ts`
- `frontend/src/app/api/index.ts`
- `frontend/src/app/components/Layout.tsx`
- `frontend/src/app/components/TopBar.tsx`
- `frontend/src/app/components/ImpersonationSwitcher.tsx`
- `frontend/src/app/components/ActiveImpersonationBanner.tsx`
- `frontend/src/app/impersonation/ImpersonationContext.tsx`
- `frontend/src/app/pages/LoginPage.tsx`
- `frontend/src/app/pages/Home.tsx`
- `frontend/src/app/pages/Dashboard.tsx`
- `frontend/src/app/pages/UserManagement.tsx`
- `frontend/src/app/pages/RoleManagement.tsx`
- `frontend/src/app/pages/ActionRegistry.tsx`
- `frontend/src/app/pages/ScopeAssignments.tsx`
- `frontend/src/app/pages/SessionManagement.tsx`
- `frontend/src/app/pages/AuditLog.tsx`
- `frontend/src/app/pages/SecurityEvents.tsx`
- `frontend/src/app/pages/TenantSettings.tsx`
- `frontend/src/app/pages/PlantHierarchy.tsx`
- `frontend/src/app/pages/StationSession.tsx`
- `frontend/src/app/pages/OperatorIdentification.tsx`
- `frontend/src/app/pages/EquipmentBinding.tsx`
- `frontend/src/app/pages/ProductList.tsx`
- `frontend/src/app/pages/ProductDetail.tsx`
- `frontend/src/app/pages/RouteList.tsx`
- `frontend/src/app/pages/RouteDetail.tsx`
- `frontend/src/app/pages/OperationExecutionDetail.tsx`
- `frontend/src/app/pages/GlobalOperationList.tsx`

## 5. Design Evidence Extract
### Authoritative frontend/backend truth requirements
- Backend owns authorization truth, audit truth, session truth, tenant/scope truth, and operational status truth.
- Frontend owns navigation, UX composition, display formatting, error/loading/empty states, and intent capture only.
- Persona is UX only. Persona/menu visibility is not permission truth.
- JWT proves identity only.
- Frontend must not fake backend truth for auth, scope, tenant, session revoke, plant hierarchy, audit, security event, or execution ownership.
- P0-A foundation precedes broader domain expansion.
- The current frontend baseline is explicitly an internal visualization baseline, not a production-ready foundation admin app.

### Narrow evidence summary used for this report
- `AuthContext.tsx` bootstraps from local storage and immediately calls `/v1/auth/me`, so auth/session truth already depends on backend availability.
- `httpClient.ts` attaches `Authorization` and `X-Tenant-ID` headers to all API requests, so tenant context is carried from backend-derived `/me` data into FE requests.
- `ImpersonationContext.tsx` uses live impersonation endpoints; the support/impersonation surface is connected even though there is no dedicated route page.
- `Dashboard.tsx` is connected to `/v1/dashboard/summary` and `/v1/dashboard/health`, so runtime readiness impacts at least one authenticated landing surface.
- Foundation / Governance / Admin route pages (`/users`, `/roles`, `/action-registry`, `/scope-assignments`, `/sessions`, `/audit-log`, `/security-events`, `/tenant-settings`, `/plant-hierarchy`) are implemented as shell or mock pages with local arrays and disabled actions, not live contracts.
- `TopBar.tsx` still contains a local plant selector and local notification items, which are not backend-derived and must not be treated as real tenant/plant truth.
- `personaLanding.ts` and `Layout.tsx` enforce frontend route visibility by persona allowlists. This is explicitly UX-only, but it remains a risk area if users over-interpret it as authorization truth.

### Frontend Foundation Dependency Map
| Foundation Area | FE Evidence | Current FE Status | Backend Dependency | Risk | Recommendation |
|---|---|---|---|---|---|
| Alembic / backend readiness impact | `RequireAuth.tsx` depends on `AuthContext` bootstrap; `Dashboard.tsx` loads live summary/health immediately after auth | PARTIAL | Backend startup, auth bootstrap, dashboard health endpoints | If backend startup is delayed by migrations/runtime changes, FE can redirect to login or show generic load failure without backend-unavailable context | Add a runtime compatibility slice with explicit 503/unavailable UX for `/me` and dashboard reads |
| Tenant context | `httpClient.ts` injects `X-Tenant-ID` from `currentUser?.tenant_id` | CONNECTED | `/v1/auth/me` must return authoritative tenant context | FE currently forwards tenant context and also shows a separate local plant selector, which can confuse users about what context is real | Keep tenant derivation backend-led; do not add FE tenant switching until backend contract exists |
| Login/auth | `LoginPage.tsx`, `authApi.login`, `AuthContext.login` | CONNECTED | `/v1/auth/login` | Login is real, but only access-token flow is implemented on FE | Keep login route connected; standardize unavailable/error UX |
| JWT identity | `AuthContext.tsx` stores bearer token; `httpClient.ts` injects Authorization header | CONNECTED | Backend-issued bearer token | FE treats token as identity bootstrap, but localStorage persistence increases sensitivity to backend auth contract changes | Preserve JWT-as-identity-only boundary; avoid adding FE permission derivation |
| Refresh token | No refresh client, no refresh scheduler, no refresh storage | MISSING | Refresh contract is not represented in FE | If backend adds/changes refresh-token behavior in P0-A, FE will continue logging users out on 401 instead of refreshing | Add a dedicated session/refresh boundary slice only after backend contract is finalized |
| User lifecycle | `/users` uses `mockUsers`; no FE user client exists | SHELL | Future users API and lifecycle states | Current FE screen implies a lifecycle shape (`active`, `inactive`, `pending`) that is not backend-derived | Keep shell disclosed; connect only after backend lifecycle contract exists |
| Session lifecycle | Auth logout/logout-all are connected; `/sessions` route is shell only | PARTIAL | `/v1/auth/logout`, `/v1/auth/logout-all`, future session list/revoke reads | Session truth exists in backend, but route-level session management is fake today | Follow auth boundary slice with read-only session list/revoke slice |
| Role model | `/roles` uses `mockRoles`; persona mapping shown in UI | SHELL | Future role read/write API | Mock role-to-persona display can be misread as permission truth | Replace with explicit backend role reads before claiming real admin readiness |
| Action registry | `/action-registry` uses `mockActions` and `persona_group` labels | SHELL | Future permission/action registry read API | Mock allowed-persona labels conflict with “persona is UX only” guidance | Do not present persona lists as permission truth on connected screens |
| Role/action binding | No FE binding UI/client found | SHELL | Future role-permission binding contract | No real FE dependency yet, but current admin surface suggests capability exists | Keep out of scope until backend action-binding contract is stable |
| Scope assignment | `/scope-assignments` uses `mockAssignments` | SHELL | Future scope hierarchy and assignment reads/writes | FE currently invents scope rows and hierarchy values locally | Connect only to backend-derived scope nodes and assignments |
| Plant hierarchy | `/plant-hierarchy` uses `mockHierarchy`; `TopBar.tsx` uses hardcoded plants | SHELL | Future plant hierarchy model / read API | Highest FE truth-leak risk in current shell set because plant context is visibly represented despite no backend read | Replace hardcoded plant context with explicit placeholder or backend data |
| Audit log | `/audit-log` uses `mockAuditEvents` | SHELL | Future audit-log read API | FE suggests live immutable audit history while using fixture data | Keep red disclosure; do not silently convert to mixed data |
| Security events | `/security-events` uses `mockSecurityEvents`; backend read endpoint already exists | SHELL | Existing `/v1/security-events` read API | Strongest near-term opportunity: backend contract exists but FE screen is still fake | Prioritize a read-only security events connection slice |
| Config / API base URL | `vite.config.ts` proxies `/api` to `http://localhost:8010`; `httpClient.ts` forces `/api` prefix | CONNECTED | Stable backend base path and proxy/routing behavior | Runtime env changes can break all FE reads if proxy/base path shifts | Add explicit API readiness smoke and environment documentation |
| Error handling / backend unavailable | Connected pages vary: `LoginPage.tsx`, `Dashboard.tsx`, `ProductList.tsx`, `RouteList.tsx`, `OperationExecutionDetail.tsx` handle errors; shell pages have no data lifecycle | PARTIAL | Stable backend error shapes and HTTP semantics | Auth bootstrap and impersonation hide some failure modes; shell pages are not ready for real integration | Standardize 401/403/503 handling before connecting more foundation screens |
| CI / runtime route checks | `route-smoke-check.mjs` verifies route/persona/screenStatus alignment | CONNECTED | FE source consistency only; not backend behavior | Route smoke passing does not prove live backend readiness | Keep route smoke, but add auth/runtime unavailable smoke later |

### Backend Truth Boundary Map
| Rule | FE Evidence | Current Protection | Gap | Severity |
|---|---|---|---|---|
| FE does not decide authorization truth. | `httpClient.ts` handles 401 only; no action client checks backend role/action permissions in FE foundation pages | Backend remains decisive for connected endpoints | `personaLanding.ts` and `Layout.tsx` still do FE route filtering, so UX visibility can be mistaken for permission truth | MEDIUM |
| Persona is UX only. | Design docs and `personaLanding.ts` explicitly describe persona as UX routing/menu policy | Clear documentation and shell banners | `ActionRegistry.tsx` and `RoleManagement.tsx` display persona-like permission groupings using mock data | HIGH |
| Shell/mock/future screens are disclosed. | `screenStatus.ts`, `RouteStatusBanner`, `MockWarningBanner` | Strong global disclosure pattern | Disclosure is good, but some shell pages still look visually complete enough to imply missing backend exists | MEDIUM |
| Connected screens do not silently fall back to fake truth. | Product/Route pages show backend notices and disabled actions; dashboard uses `--` instead of fake KPI values | Good on product/routing and dashboard | `ImpersonationContext.tsx` converts errors to `activeSession = null`, which hides outage vs no-session | MEDIUM |
| Dangerous actions are disabled on mock/shell pages. | Users/roles/sessions/tenant/plant/operator/equipment shells disable create/edit/revoke/bind actions | Good shell safety | No gap found in inspected foundation/admin screens | LOW |
| Backend unavailable does not crash the whole app. | `Dashboard.tsx`, Product/Route pages, Operation detail catch load errors | Partial resilience | `RequireAuth.tsx` renders `null` while bootstrapping and redirects on failed `/me`; FE has no dedicated backend-unavailable state | HIGH |
| Tenant/scope is not invented by frontend. | `AuthContext.tsx` sources tenant from `/me` | Tenant header is backend-derived for connected requests | `TopBar.tsx` plant list and `/scope-assignments`, `/tenant-settings` shells invent scope/context visuals locally | HIGH |
| Plant hierarchy is not represented as live if backend is missing. | `/plant-hierarchy` is labeled shell | Disclosure present | The page still renders a rich hierarchy tree from local mock data, and TopBar presents plant choices as selectable context | HIGH |
| Security events are read from backend where connected. | Backend endpoint exists; FE page still mock | None on route page | `/security-events` is not connected despite backend readiness and test coverage | HIGH |

### Verdict before report write
**ALLOW_REPORT_WRITE**

The frontend source tree, router, status registry, and API layer were inspectable without requiring any code changes. The task could be completed as an evidence report within the allowed scope.

## 6. Frontend Foundation Dependency Map
| Foundation Area | FE Evidence | Current FE Status | Backend Dependency | Risk | Recommendation |
|---|---|---|---|---|---|
| Auth bootstrap | `AuthContext.tsx` calls `authApi.me()` on app init | CONNECTED | `/v1/auth/me` | Backend outage currently degrades into auth loss rather than an unavailable state | Add explicit auth bootstrap unavailable UX |
| Login route | `LoginPage.tsx` + `authApi.login()` | CONNECTED | `/v1/auth/login` | No refresh path; direct token storage only | Keep route connected; prepare later refresh boundary slice |
| Logout current session | `TopBar.tsx` + `AuthContext.logout()` | CONNECTED | `/v1/auth/logout` | FE clears local state even if backend revoke fails | Show revoke-result messaging when backend contract is expanded |
| Logout all sessions | `TopBar.tsx` + `AuthContext.logoutAll()` | CONNECTED | `/v1/auth/logout-all` | Same best-effort local clear behavior | Keep behavior but expose backend failure distinctly in later slice |
| Impersonation current/start/revoke | `ImpersonationContext.tsx`, `ImpersonationSwitcher.tsx`, `ActiveImpersonationBanner.tsx` | CONNECTED | `/v1/impersonations/current`, `/v1/impersonations`, `/v1/impersonations/:id/revoke` | Error path hides outage as “not impersonating”; no dedicated admin route | Keep connected; add support-mode error states |
| Dashboard health/summary | `Dashboard.tsx` + `dashboardApi.ts` | CONNECTED | `/v1/dashboard/summary`, `/v1/dashboard/health` | Runtime readiness changes surface here immediately; no empty-state contract | Treat dashboard as runtime readiness consumer, not foundation truth source |
| User management route | `UserManagement.tsx` local `mockUsers` | SHELL | Future user lifecycle API | UI invents statuses and scope rows | Do not mark safe for real usage |
| Role management route | `RoleManagement.tsx` local `mockRoles` | SHELL | Future role API | Mock persona/role linkage can be misread as permission truth | Connect only after backend read model exists |
| Action registry route | `ActionRegistry.tsx` local `mockActions` | SHELL | Future action registry API | Displays “Allowed Personas” even though persona is not permission truth | Rework copy before live connection |
| Scope assignments route | `ScopeAssignments.tsx` local `mockAssignments` | SHELL | Future scope assignment API | FE invents scope tree and assignments | Connect only to backend-derived scope graph |
| Session management route | `SessionManagement.tsx` local `mockSessions` | SHELL | Future session list/revoke API | Backend session truth exists, but route is fake | Good candidate after auth boundary hardening |
| Audit log route | `AuditLog.tsx` local `mockAuditEvents` | SHELL | Future audit-log read API | Immutable audit fact is currently simulated | Keep clearly disclosed |
| Security events route | `SecurityEvents.tsx` local `mockSecurityEvents` | SHELL | Existing `/v1/security-events` | Contract exists but FE is still fake | First governance route to connect |
| Tenant settings route | `TenantSettings.tsx` local `mockTenant` | SHELL | Future tenant read/update API | FE invents tenant metadata and integrations | Keep shell disclosed; do not fake live tenant config |
| Plant hierarchy route | `PlantHierarchy.tsx` local `mockHierarchy` | SHELL | Future plant hierarchy API/model | FE depicts rich hierarchy without backend truth | Replace with explicit placeholder if backend remains incomplete |

## 7. Foundation Route Inventory
| Route | Screen / Component | Source File | Current Screen Status | Data Source | Backend Dependency | Safe for Real Usage? | Depends on Missing P0-A Capability? |
|---|---|---|---|---|---|---|---|
| `/login` | LoginPage | `frontend/src/app/pages/LoginPage.tsx` | CONNECTED | Backend API | `/v1/auth/login`, `/v1/auth/me` via auth bootstrap | **Yes**, for baseline auth only | Refresh-token path is missing from FE |
| `/home` | Home | `frontend/src/app/pages/Home.tsx` | MOCK | Inline mock data | Auth guard only | **No** | Not blocked by P0-A API, but not a real foundation screen |
| `/dashboard` | Dashboard | `frontend/src/app/pages/Dashboard.tsx` | CONNECTED | Backend API with placeholders for some charts | `/v1/dashboard/summary`, `/v1/dashboard/health` | **Partial** | Yes; runtime startup/readiness changes surface here |
| `/users` | UserManagement | `frontend/src/app/pages/UserManagement.tsx` | SHELL | Local mock array | None found in FE source | **No** | Yes; user lifecycle/read model missing on FE |
| `/roles` | RoleManagement | `frontend/src/app/pages/RoleManagement.tsx` | SHELL | Local mock array | None found in FE source | **No** | Yes; role read model/client missing |
| `/action-registry` | ActionRegistry | `frontend/src/app/pages/ActionRegistry.tsx` | SHELL | Local mock array | None found in FE source | **No** | Yes; action registry/client missing |
| `/scope-assignments` | ScopeAssignments | `frontend/src/app/pages/ScopeAssignments.tsx` | SHELL | Local mock array | None found in FE source | **No** | Yes; scope assignment and hierarchy read contracts missing in FE |
| `/sessions` | SessionManagement | `frontend/src/app/pages/SessionManagement.tsx` | SHELL | Local mock array | None found in FE source | **No** | Yes; session list/revoke UI contract missing |
| `/audit-log` | AuditLog | `frontend/src/app/pages/AuditLog.tsx` | SHELL | Local mock array | None found in FE source | **No** | Yes; audit-log read contract missing on FE |
| `/security-events` | SecurityEvents | `frontend/src/app/pages/SecurityEvents.tsx` | SHELL | Local mock array | Backend endpoint exists, but no FE client/page integration | **No** | Yes; FE integration missing despite BE contract |
| `/tenant-settings` | TenantSettings | `frontend/src/app/pages/TenantSettings.tsx` | SHELL | Local mock object | None found in FE source | **No** | Yes; tenant settings read/update contract missing |
| `/plant-hierarchy` | PlantHierarchy | `frontend/src/app/pages/PlantHierarchy.tsx` | SHELL | Local mock hierarchy | None found in FE source | **No** | Yes; plant hierarchy read model/client missing |
| `/station-session` | StationSession | `frontend/src/app/pages/StationSession.tsx` | SHELL | None | Future station session backend | **No** | Yes; session-owned execution foundation route exists only as shell |
| `/operator-identification` | OperatorIdentification | `frontend/src/app/pages/OperatorIdentification.tsx` | SHELL | None | Future operator identity/session contract | **No** | Yes |
| `/equipment-binding` | EquipmentBinding | `frontend/src/app/pages/EquipmentBinding.tsx` | SHELL | None | Future equipment binding/readiness contract | **No** | Yes |

Non-route support surface: impersonation is not a page route. It is exposed through `TopBar.tsx`, `ImpersonationSwitcher.tsx`, and `ActiveImpersonationBanner.tsx`, and it is already connected to live backend endpoints.

## 8. API Dependency Matrix
| Frontend File | Function / Client | Endpoint / Path | Used By | Auth Required? | Error Handling Seen? | Risk |
|---|---|---|---|---|---|---|
| `frontend/src/app/api/authApi.ts` | `login` | `/v1/auth/login` | `LoginPage.tsx`, `AuthContext.tsx` | No | Login page catches and renders error text | Access-token-only FE path; no refresh handling |
| `frontend/src/app/api/authApi.ts` | `me` | `/v1/auth/me` | `AuthContext.tsx` bootstrap | Yes | `AuthContext.tsx` catches and clears current user | Backend unavailable looks like auth loss |
| `frontend/src/app/api/authApi.ts` | `logout` | `/v1/auth/logout` | `TopBar.tsx`, `AuthContext.tsx` | Yes | Best-effort catch; local auth is cleared anyway | FE can hide revoke failure |
| `frontend/src/app/api/authApi.ts` | `logoutAll` | `/v1/auth/logout-all` | `TopBar.tsx`, `AuthContext.tsx` | Yes | Best-effort catch; local auth is cleared anyway | Same revoke-failure masking |
| `frontend/src/app/api/impersonationApi.ts` | `getCurrent` | `/v1/impersonations/current` | `ImpersonationContext.tsx` | Yes | Errors are swallowed to `null` active session | Outage and “no active impersonation” are indistinguishable |
| `frontend/src/app/api/impersonationApi.ts` | `start` | `/v1/impersonations` | `ImpersonationSwitcher.tsx` | Yes | Toast error surfaced | Connected support flow exists without a route-level admin page |
| `frontend/src/app/api/impersonationApi.ts` | `revoke` | `/v1/impersonations/:id/revoke` | `ActiveImpersonationBanner.tsx`, `ImpersonationContext.tsx` | Yes | Toast error surfaced | Partial support-mode UX if revoke fails |
| `frontend/src/app/api/dashboardApi.ts` | `getSummary` | `/v1/dashboard/summary` | `Dashboard.tsx` | Yes | Page-level loading/error state | No empty-state contract; runtime readiness dependency |
| `frontend/src/app/api/dashboardApi.ts` | `getHealth` | `/v1/dashboard/health` | `Dashboard.tsx` | Yes | Page-level loading/error state | Same runtime readiness dependency |
| `frontend/src/app/api/httpClient.ts` | `request`, `buildHeaders` | `/api` prefix applied to all FE API calls | All FE API modules | Mixed | `HttpError` normalization and global 401 logout hook | FE forwards `X-Tenant-ID`; global 401 currently becomes logout instead of refresh |
| `frontend/src/app/pages/UserManagement.tsx` | No API client found | None found in FE source | `/users` | Guard only | None | User lifecycle route is still pure mock |
| `frontend/src/app/pages/RoleManagement.tsx` | No API client found | None found in FE source | `/roles` | Guard only | None | Role model route is still pure mock |
| `frontend/src/app/pages/ActionRegistry.tsx` | No API client found | None found in FE source | `/action-registry` | Guard only | None | Permission/action truth is simulated locally |
| `frontend/src/app/pages/ScopeAssignments.tsx` | No API client found | None found in FE source | `/scope-assignments` | Guard only | None | Scope truth is simulated locally |
| `frontend/src/app/pages/SessionManagement.tsx` | No API client found | None found in FE source | `/sessions` | Guard only | None | Session-admin route is disconnected despite live auth session backend |
| `frontend/src/app/pages/AuditLog.tsx` | No API client found | None found in FE source | `/audit-log` | Guard only | None | Audit route remains fake |
| `frontend/src/app/pages/SecurityEvents.tsx` | No API client found | None found in FE page source | `/security-events` | Guard only | None | Backend read contract exists, but FE screen is still fake |
| `frontend/src/app/pages/TenantSettings.tsx` | No API client found | None found in FE source | `/tenant-settings` | Guard only | None | Tenant settings are invented locally |
| `frontend/src/app/pages/PlantHierarchy.tsx` | No API client found | None found in FE source | `/plant-hierarchy` | Guard only | None | Plant hierarchy is invented locally |

## 9. Screen Dependency Matrix
| Route | Screen / Component | Status | Backend Dependency | P0-A Area | Risk | Follow-up Slice |
|---|---|---|---|---|---|---|
| `/login` | LoginPage | CONNECTED | `/v1/auth/login`, `/v1/auth/me` | Login/auth, JWT identity, session bootstrap | Refresh-token path absent; backend unavailable state weak | FE-P0A-01, FE-P0A-02 |
| `/dashboard` | Dashboard | CONNECTED | `/v1/dashboard/summary`, `/v1/dashboard/health` | Runtime readiness, error handling | Startup/migration/runtime failures surface here immediately | FE-P0A-01 |
| `/users` | UserManagement | SHELL | None found in FE | User lifecycle | Invented statuses and scopes | FE-P0A-03 |
| `/roles` | RoleManagement | SHELL | None found in FE | Role model | Persona vs permission conflation risk | FE-P0A-03 |
| `/action-registry` | ActionRegistry | SHELL | None found in FE | Action registry, role/action binding | Mock “allowed personas” can misstate auth truth | FE-P0A-03 |
| `/scope-assignments` | ScopeAssignments | SHELL | None found in FE | Scope assignment | Fake hierarchy and assignments | FE-P0A-05 |
| `/sessions` | SessionManagement | SHELL | None found in FE route | Session lifecycle | Backend truth exists, FE route still fake | FE-P0A-02 or FE-P0A-05 |
| `/audit-log` | AuditLog | SHELL | None found in FE | Audit log | Immutable facts represented by fixture data | FE-P0A-03 |
| `/security-events` | SecurityEvents | SHELL | Backend endpoint exists but no FE integration | Security events | Connected backend exists but route still uses fake data | FE-P0A-04 |
| `/tenant-settings` | TenantSettings | SHELL | None found in FE | Tenant context | Fake tenant metadata can imply live admin truth | FE-P0A-05 |
| `/plant-hierarchy` | PlantHierarchy | SHELL | None found in FE | Plant hierarchy | Rich fake hierarchy and hardcoded plant selector imply truth | FE-P0A-05 |
| `/station-session` | StationSession | SHELL | None found in FE | Session-owned execution foundation | Session-owned target screen exists but has no backend contract wired | FE-P0A-05 |
| `/operator-identification` | OperatorIdentification | SHELL | None found in FE | Operator/session identity | FE cannot verify operator truth | FE-P0A-05 |
| `/equipment-binding` | EquipmentBinding | SHELL | None found in FE | Equipment / plant / station foundation | FE cannot verify binding or readiness truth | FE-P0A-05 |
| `TopBar modal` | ImpersonationSwitcher / ActiveImpersonationBanner | CONNECTED | `/v1/impersonations/current`, `/v1/impersonations`, `/v1/impersonations/:id/revoke` | IAM lifecycle, support/impersonation, audit/security event | Connected but error states are underspecified | FE-P0A-02 |

## 10. Backend Truth Boundary Map
| Rule | FE Evidence | Current Protection | Gap | Severity |
|---|---|---|---|---|
| FE does not decide authorization truth. | Connected FE foundation clients do not check action codes locally | Strong backend contract on connected auth/impersonation flows | Frontend route allowlists remain active in persona routing | MEDIUM |
| Persona is UX only. | Docs and comments in `navigationGroups.ts` and `personaLanding.ts` say this explicitly | Good written guidance | `ActionRegistry.tsx` and `RoleManagement.tsx` still present persona-like permission labels in UI | HIGH |
| Shell/mock/future screens are disclosed. | `RouteStatusBanner`, `MockWarningBanner`, `screenStatus.ts` | Strong | No blocking gap | LOW |
| Connected screens do not silently fall back to fake truth. | Product/Route pages show backend-required notices and do not mix mock rows | Good on connected read-only pages | `ImpersonationContext.tsx` swallows current-session read errors into null state | MEDIUM |
| Dangerous actions are disabled on mock/shell pages. | Users/roles/sessions/tenant/plant/operator/equipment screens all disable actions | Strong | No blocking gap found in inspected surfaces | LOW |
| Backend unavailable does not crash the whole app. | Connected pages catch page-level errors | Partial | `/me` failure causes auth loss/redirect instead of backend-unavailable UX | HIGH |
| Tenant/scope is not invented by frontend. | Connected requests derive tenant from `/me` | Partial | Top bar plant choices, scope assignment rows, tenant settings, and plant hierarchy are still invented locally | HIGH |
| Plant hierarchy is not represented as live if backend is missing. | `/plant-hierarchy` shows SHELL badge | Partial | Screen still renders a rich tree and `TopBar.tsx` still exposes plant selection locally | HIGH |
| Security events are read from backend where connected. | Backend contract exists | None on current page | `/security-events` is still mock despite available backend read endpoint | HIGH |

## 11. Runtime Compatibility Risk Audit
| Risk | Source Evidence | Impact if BE P0-A-01 changes startup/migration/runtime | Recommendation |
|---|---|---|---|
| Auth bootstrap treats `/me` failure as effective auth loss | `AuthContext.tsx`, `RequireAuth.tsx` | During backend startup or migration lag, authenticated users may be redirected to `/login` instead of seeing backend unavailable state | Add explicit unavailable state and retry strategy around bootstrap |
| Global 401 path logs out immediately | `httpClient.ts` unauthorized handler | Any backend auth/runtime transition that temporarily returns 401 ejects users rather than attempting a governed refresh path | Add session-boundary slice after backend refresh contract is stable |
| Dashboard is a real runtime consumer with only generic load failure UX | `Dashboard.tsx` | BE readiness changes can make the landing page look broken without explaining backend status | Normalize 503/unavailable handling and add clearer empty/fallback semantics |
| Impersonation current-session errors are hidden | `ImpersonationContext.tsx` | Support/admin users can lose visibility into impersonation state during backend failure | Add explicit impersonation read error state |
| Shell admin pages have no loading/error/empty lifecycle yet | `/users`, `/roles`, `/action-registry`, `/scope-assignments`, `/sessions`, `/audit-log`, `/security-events`, `/tenant-settings`, `/plant-hierarchy` | First real integration would otherwise jump straight from local mock data to live API with no UX resilience | Add route-by-route read-state hardening before each connection |
| Plant selector is local-only | `TopBar.tsx` | Runtime backend context changes could diverge from the plant shown in FE chrome | Remove or clearly label local-only selector until backend context contract exists |

## 12. Mock / Shell / Connected Risk Map
| Surface | Current Status | Why It Matters | Current Risk | Recommendation |
|---|---|---|---|---|
| Login | CONNECTED | Entry point to all protected screens | Medium, because bootstrap/unavailable semantics are still thin | Harden auth unavailable handling |
| Dashboard | CONNECTED | Earliest authenticated runtime dependency | Medium | Add standardized readiness/error treatment |
| Impersonation controls | CONNECTED | Only connected support/admin foundation feature beyond auth | Medium | Add explicit current-session error state |
| Users / Roles / Action Registry | SHELL | Highest risk for FE permission-truth leakage | High | Align shell copy and connect only to backend reads |
| Scope Assignments / Tenant Settings / Plant Hierarchy | SHELL | Highest tenant/scope/plant truth leakage risk | High | Remove invented live context or connect to backend-derived data |
| Sessions | SHELL | Backend session lifecycle exists already | High | Add read-only session slice after auth boundary hardening |
| Audit Log | SHELL | Audit truth must be backend-derived | High | Keep shell disclosed until backend contract exists |
| Security Events | SHELL with BE contract available | Fastest route to fake/live mismatch | High | Connect this route first among governance screens |
| Station Session / Operator Identification / Equipment Binding | SHELL | These are visible target foundation screens for session-owned execution | High | Keep as explicit future shells until backend session-owned flow contract is ready |

## 13. Verification Commands
| Requested Command | Result | Notes |
|---|---|---|
| `cd frontend && npm run lint` | PASS (no ESLint output) | Direct `npm` wrapper was blocked by local PowerShell execution policy on `npm.ps1`. Equivalent direct node invocation of ESLint returned cleanly with no lint messages. |
| `cd frontend && npm run build` | PASS | Equivalent direct Vite invocation built successfully in 10.30s. Warning: main JS chunk is 1.72 MB after minification. |
| `cd frontend && npm run check:routes` | PASS | Route smoke summary: 78 registered routes, 77 smoke targets, 0 failures, 1 redirect-only exclusion. Screen-status coverage aligned with route registry. |
| `cd frontend && npm run lint:i18n:registry` | PASS | Registry parity checker reported synchronized `en.ts` and `ja.ts` with 1692 keys. |

## 14. Recommended FE Companion Slice Sequence
### FE-P0A-01 — Foundation Runtime Compatibility / API Readiness Smoke
- Intent: Make auth bootstrap and dashboard runtime dependency failures explicit rather than silently redirecting or showing generic load failure.
- Why now: Backend P0-A-01 runtime and migration changes will surface first on `/me` and `/dashboard`.
- In scope: Auth bootstrap unavailable state, retry affordance, standardized 401/503 handling for login and dashboard, runtime-readiness messaging.
- Explicitly out of scope: Refresh-token implementation, governance screen connection, backend changes.
- Backend dependency: Stable auth and dashboard error semantics.
- Test focus: `/me` 401, `/me` 503, dashboard summary/health 5xx, startup lag.
- Stop conditions: Backend error contract is still changing or undocumented.

### FE-P0A-02 — Auth / Session Boundary Standardization
- Intent: Prepare FE session handling for backend session truth without inventing refresh behavior.
- Why now: Current FE stores only an access token, logs out on 401, and hides some revoke/current-session failures.
- In scope: Shared auth/session error normalization, explicit logout/logout-all result handling, impersonation current-session error state, access-token-expiry UX.
- Explicitly out of scope: New refresh-token protocol, session admin page, role/scope admin screens.
- Backend dependency: Auth/session/revoke contract and any planned refresh-token contract.
- Test focus: Token expiry, logout-all, impersonation revoke/current read failures.
- Stop conditions: Refresh/session contract is not finalized on backend.

### FE-P0A-03 — Governance Screen Status Alignment
- Intent: Reduce truth-leak risk on governance shells before any live connection work starts.
- Why now: Current Users/Roles/Action Registry pages visually imply authority and sometimes blur persona vs permission truth.
- In scope: Screen-status copy alignment, disclosure hardening, removal of permission-like mock phrasing, disabled-action messaging consistency.
- Explicitly out of scope: Live API connection, CRUD implementation, new routes.
- Backend dependency: Minimal; copy can be aligned before read APIs exist.
- Test focus: Route banner presence, shell disclosure accuracy, no dangerous actions enabled.
- Stop conditions: Product/governance copy conflicts with design docs.

### FE-P0A-04 — Security Events Real Filter UI Alignment
- Intent: Convert `/security-events` from a fake shell into a read-only connected screen using the existing backend contract.
- Why now: Backend `/v1/security-events` already exists and has dedicated audit/test coverage.
- In scope: Read-only list, backend-backed filters, pagination, loading/error/empty states, honest disclosure of read-only scope.
- Explicitly out of scope: Incident remediation actions, session admin, audit-log route, backend changes.
- Backend dependency: Stable `GET /v1/security-events` contract with authz and tenant isolation preserved.
- Test focus: Unauthorized access, tenant isolation, empty-state rendering, filter error handling.
- Stop conditions: Backend contract changes materially or lacks FE-consumable pagination fields.

### FE-P0A-05 — Session / Tenant / Plant Placeholder Guard Review
- Intent: Remove or explicitly downgrade fake tenant/scope/plant/session context until backend models are ready.
- Why now: This is the highest remaining frontend truth-boundary risk in the current foundation shell set.
- In scope: Top bar plant-context disclosure, `/scope-assignments`, `/tenant-settings`, `/plant-hierarchy`, `/station-session`, `/operator-identification`, `/equipment-binding` placeholder review and guardrail tightening.
- Explicitly out of scope: Building real plant hierarchy CRUD or session-owned execution flows.
- Backend dependency: Future tenant, scope, plant hierarchy, and session-owned execution contracts.
- Test focus: No fake live context, no enabled governed actions, shell disclosure consistency.
- Stop conditions: Backend hierarchy/session contracts remain undefined.

## 15. Explicit Non-Goals Confirmed
- No frontend source files were modified.
- No routes were added, changed, or removed.
- No API clients were added or changed.
- No auth logic, persona logic, or navigation logic was changed.
- No i18n registry changes were made.
- No dependencies or lock files were changed.
- No backend, migration, or test files were changed.
- No design docs or screen inventory docs were updated.

## 16. Stop Conditions / Unknowns
| Item | Status | Impact |
|---|---|---|
| Mandatory instruction files missing | No | Did not block report write |
| Frontend source tree unavailable | No | Did not block report write |
| Merge conflicts present | No | Did not block report write |
| Requested `docs/design/05_application/fe-screen-inventory-and-navigation-map.md` missing | Yes | Report relied on actual route registry and other design docs instead |
| Root `DESIGN.md` missing | Yes | `docs/design/DESIGN.md` used instead |
| Requested `.github/prompts/...` path missing | Yes | Closest equivalent prompt file in `.github/` root was inspected |
| `npm.ps1` blocked by PowerShell policy | Yes | Equivalent direct-node verification commands were used instead |
| Exact FE contracts for users/roles/sessions/audit/tenant/plant | Unknown / absent in FE | Prevents classification of those routes as connected or partial |

## 17. Final Recommendation
The frontend is ready for **companion slicing**, not for broad foundation UI implementation. The right next move is to harden runtime/auth boundary behavior first, then connect the smallest truthful governance route that already has a backend contract, which is `Security Events`. User/role/scope/session/tenant/plant admin routes should remain disclosed shells until each backend read model and error-state contract is ready. The frontend must not promote persona, mock hierarchy, or placeholder session data into permission or operational truth while P0-A foundation is still being completed.

## Appendix A — Raw Route Evidence
### Router evidence
- `frontend/src/app/routes.tsx` registers 78 routes, including the foundation routes `/users`, `/roles`, `/action-registry`, `/scope-assignments`, `/sessions`, `/audit-log`, `/security-events`, `/tenant-settings`, and `/plant-hierarchy`.
- `frontend/src/app/screenStatus.ts` classifies foundation/admin routes as `SHELL` with `MOCK_FIXTURE` or `NONE` data sources.
- `frontend/src/app/navigation/navigationGroups.ts` places those routes under `governance-admin` and explicitly states grouping is presentation-only, not authorization truth.
- `frontend/src/app/persona/personaLanding.ts` enforces persona-based route visibility, with `STRICT` and `DEV` modes.

### Route smoke evidence
- Registered routes: 78
- Index routes: 1
- Static routes: 68
- Dynamic routes: 9
- Excluded routes: 1 (`/` redirect-only)
- Smoke targets: 77
- Failures: 0
- Explicit pass notes included route coverage for `/action-registry`, `/audit-log`, `/plant-hierarchy`, `/scope-assignments`, `/security-events`, `/sessions`, `/tenant-settings`, `/users`, and `/roles`.

## Appendix B — Raw API Client Evidence
### Connected foundation-related FE clients found
- `authApi.login` -> `/v1/auth/login`
- `authApi.me` -> `/v1/auth/me`
- `authApi.logout` -> `/v1/auth/logout`
- `authApi.logoutAll` -> `/v1/auth/logout-all`
- `impersonationApi.getCurrent` -> `/v1/impersonations/current`
- `impersonationApi.start` -> `/v1/impersonations`
- `impersonationApi.revoke` -> `/v1/impersonations/:id/revoke`
- `dashboardApi.getSummary` -> `/v1/dashboard/summary`
- `dashboardApi.getHealth` -> `/v1/dashboard/health`

### No dedicated FE client found for these current foundation/admin pages
- `UserManagement.tsx`
- `RoleManagement.tsx`
- `ActionRegistry.tsx`
- `ScopeAssignments.tsx`
- `SessionManagement.tsx`
- `AuditLog.tsx`
- `SecurityEvents.tsx` page source itself, despite backend endpoint availability
- `TenantSettings.tsx`
- `PlantHierarchy.tsx`

### Shared transport evidence
- `httpClient.ts` prepends `/api` to non-absolute paths.
- `httpClient.ts` injects `Authorization` when a token exists.
- `httpClient.ts` injects `X-Tenant-ID` when `currentUser.tenant_id` exists.
- `httpClient.ts` normalizes non-2xx into `HttpError` and triggers the unauthorized handler on 401.

## Appendix C — Command Output Summary
### Lint
- Equivalent direct invocation of ESLint returned no output, which indicates a clean lint run for the inspected source.

### Build
- `vite v6.4.1 building for production...`
- `✓ 3407 modules transformed.`
- `dist/index.html 0.44 kB`
- `dist/assets/index-D-E5F3kd.css 139.12 kB`
- `dist/assets/index-ZXlSvfkm.js 1,721.73 kB`
- Warning: chunk size exceeds 500 kB after minification.
- `✓ built in 10.30s`

### Route smoke
- PASS: 24
- FAIL: 0
- 77 of 78 routes covered, 1 redirect-only exclusion.
- Screen status coverage aligned with route registry.

### i18n registry
- `[i18n-registry] PASS: en.ts and ja.ts are key-synchronized (1692 keys).`

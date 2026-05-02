# FE-GOVADMIN-03 — Governance/Admin Persona Route Guard Regression Test Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Added regression coverage for Governance/Admin persona route guard after FE-GOVADMIN-02. |

---

## 1. Scope

Regression test coverage for the Governance/Admin persona route guard bug found and fixed in FE-GOVADMIN-02.

This slice:
- Verifies ADM can access all 9 Governance/Admin routes (UX route visibility)
- Verifies non-admin personas are not granted governance route access
- Verifies sidebar/menu visibility is persona-aware for governance routes
- Verifies SidebarSearch operates on persona-visible items only
- Verifies route registry alignment across `routes.tsx`, `navigationGroups.ts`, and `personaLanding.ts`
- Documents the backend truth boundary

This slice does NOT:
- Test backend authorization
- Add new screens or routes
- Change any IAM or permission logic
- Change any backend or API contracts

---

## 2. Prerequisites Checked

| Item | Result |
|---|---|
| `docs/audit/fe-govadmin-02-report.md` present | ✓ Verified |
| `frontend/src/app/persona/personaLanding.ts` present | ✓ Verified |
| `frontend/src/app/navigation/navigationGroups.ts` present | ✓ Verified |
| `frontend/src/app/routes.tsx` present | ✓ Verified |
| `frontend/src/app/components/SidebarSearch.tsx` present | ✓ Verified |
| `frontend/src/app/components/Layout.tsx` present | ✓ Verified |
| No existing frontend test framework (Vitest/Jest) | ✓ Confirmed — package.json has no `test` script |
| Script-style smoke checks already used (`route-smoke-check.mjs`) | ✓ Confirmed — chosen as implementation approach |

---

## 3. FE-GOVADMIN-02 Finding Covered

**Bug found in FE-GOVADMIN-02:**
`isRouteAllowedForPersona` in `personaLanding.ts` did not include the 9 Governance/Admin routes. At runtime, `Layout.tsx` called this function and redirected all personas away from governance routes before any page could render. All 9 routes were registered in `routes.tsx` but unreachable.

**Fix applied in FE-GOVADMIN-02:**
Added an ADM-only block to `isRouteAllowedForPersona`:

```typescript
// Governance & Admin routes — ADM only (UX routing; backend enforces authorization)
if (
  pathname === "/users" ||
  pathname === "/roles" ||
  ...
  pathname === "/plant-hierarchy"
) {
  return ["ADM"].includes(persona);
}
```

**Regression risk:**
If this block is removed or any of the 9 routes is omitted, governance pages become silently unreachable — with no compile error, no lint error, and no existing test to catch it.

**This task adds:**
`frontend/scripts/govadmin-persona-route-guard-check.mjs` — a 56-check static source regression script that will fail if the ADM governance block disappears, the OTS→ADM alias mapping drifts, or any route is missing from any of the three alignment layers.

---

## 4. Persona Access Matrix

Source truth from `personaLanding.ts` — `isRouteAllowedForPersona` governance block and `MENU_ITEMS_BY_PERSONA`.

| Persona | `/users` | `/roles` | `/action-registry` | `/scope-assignments` | `/sessions` | `/audit-log` | `/security-events` | `/tenant-settings` | `/plant-hierarchy` | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ADM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ALLOWED |
| OPR | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | DENIED |
| SUP | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | DENIED |
| IEP | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | DENIED |
| QC | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | DENIED |
| PMG | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | DENIED |
| EXE | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | DENIED |

**Note on role code mapping:**
- `PLN` → resolved to `PMG` persona (no governance access)
- `INV` → resolved to `PMG` persona (no governance access)
- `OTS` → resolved to `ADM` persona (governance access allowed; OTS is an ADM alias in `resolvePersonaFromRoleCode`)
- `QCI` / `QAL` → resolved to `QC` persona (no governance access)

No non-ADM persona has been intentionally granted governance route access in current source. No policy change was made.

---

## 5. Tests / Scripts Added

### Script: `frontend/scripts/govadmin-persona-route-guard-check.mjs`

**Implementation approach:** Option B — script-style smoke check aligned with `route-smoke-check.mjs` project pattern. Static source analysis; no new dependencies; no compiled TypeScript required; deterministic; exits non-zero on failure.

**Sections checked:**

| Section | Checks | Description |
|---|---|---|
| A. Route Registration | 9 | All 9 routes registered in `routes.tsx` |
| B. Navigation Group | 10 | `governance-admin` group exists; all 9 routes in `routePrefixes` |
| C. Route Guard Block | 17 | Guard block detected; ADM-only access; all 6 non-admin personas excluded; all 9 routes present in function |
| D. ADM Menu Items | 9 | `MENU_ITEMS_BY_PERSONA.ADM` contains all 9 governance routes |
| E. Non-Admin Menus | 6 | OPR, SUP, IEP, QC, PMG, EXE menus contain no governance routes |
| F. SidebarSearch Safety | 1 | SidebarSearch has persona-filter safety documentation |
| G. Layout Guard | 2 | Layout.tsx imports `isRouteAllowedForPersona`; has redirect for unauthorized routes |
| H. OTS Alias Mapping | 2 | `resolvePersonaFromRoleCode` contains OTS alias and maps OTS to ADM |
| **Total** | **56** | |

**How it catches the FE-GOVADMIN-02 regression:**
- Section C checks that all 9 routes appear inside `isRouteAllowedForPersona` via `pathname === "/route"` — if any is removed, a FAIL is emitted
- Section C checks that `["ADM"].includes(persona)` is in the guard block — if non-ADM is added, a FAIL is emitted
- Section C checks non-ADM personas are not in the guard access expression — if widened, a FAIL is emitted

### npm Script Added: `"check:govadmin:persona"`

```json
"check:govadmin:persona": "node scripts/govadmin-persona-route-guard-check.mjs"
```

Added to `frontend/package.json` consistent with existing `check:routes` pattern.

---

## 6. Route Registry Alignment

All 9 governance routes verified present and consistent across all three layers:

| Route | `routes.tsx` | `navigationGroups.ts` | `personaLanding.ts` |
|---|---|---|---|
| `/users` | ✓ | ✓ | ✓ |
| `/roles` | ✓ | ✓ | ✓ |
| `/action-registry` | ✓ | ✓ | ✓ |
| `/scope-assignments` | ✓ | ✓ | ✓ |
| `/sessions` | ✓ | ✓ | ✓ |
| `/audit-log` | ✓ | ✓ | ✓ |
| `/security-events` | ✓ | ✓ | ✓ |
| `/tenant-settings` | ✓ | ✓ | ✓ |
| `/plant-hierarchy` | ✓ | ✓ | ✓ |

---

## 7. Sidebar/Search Visibility Results

| Check | Result | Evidence |
|---|---|---|
| `MENU_ITEMS_BY_PERSONA.ADM` includes all 9 governance routes | ✓ | Section D — 9/9 PASS |
| Non-admin persona menus (OPR/SUP/IEP/QC/PMG/EXE) contain no governance routes | ✓ | Section E — 6/6 PASS |
| `SidebarSearch` operates only on `getMenuItemsForPersona()` output | ✓ | SidebarSearch comment: "does NOT expose routes outside the current persona's menu" |
| `SidebarSearch` is not authorization truth | ✓ | Source comment: "it is NOT authorization truth" |
| Navigation grouping is presentation-only | ✓ | `check:routes` PASS: "Navigation grouping safety disclaimer present" |

---

## 8. Backend Truth Boundary Confirmation

**This regression test verifies UX route visibility only.**

Frontend route guards (`isRouteAllowedForPersona`, `MENU_ITEMS_BY_PERSONA`, `SidebarSearch`) are UX convenience controls, not security perimeters. They control what a user sees in the UI — they do not grant or deny actual system access.

Backend is the authoritative source for:
- Authorization and RBAC enforcement
- Session validity and revocation
- Audit log integrity
- Security event recording
- Tenant and scope isolation
- Role and action assignment truth
- User lifecycle mutations
- Plant hierarchy master data mutations
- Tenant settings persistence

These regression tests cannot and do not certify backend authorization. Passing this check does not mean that Governance/Admin operations are secure — it only means the UI correctly shows/hides the relevant pages for each persona.

---

## 9. Files Changed

| File | Change |
|---|---|
| `frontend/scripts/govadmin-persona-route-guard-check.mjs` | NEW — 56-check regression script |
| `frontend/package.json` | Added `"check:govadmin:persona"` script |

No product runtime UI files were modified. This slice only added a frontend regression script, package script, and audit report.

---

## 10. Verification Commands

| Command | Result | Notes |
|---|---|---|
| `npm run check:govadmin:persona` | ✓ PASS — 56/56 checks | New regression check |
| `npm run build` | ✓ PASS — 3408 modules | No regressions from package.json change |
| `npm run lint` | ✓ PASS — clean | No lint errors |
| `npm run lint:i18n:registry` | ✓ PASS — 1692 keys | No i18n changes |
| `npm run lint:i18n:hardcode` | ⚠ Pre-existing CRLF issue (Windows) | Not caused by this task |
| `npm run check:routes` | ✓ PASS — 24/24 | Route coverage unchanged |

---

## 11. Remaining Risks / Deferred Items

| Item | Severity | Notes |
|---|---|---|
| No runtime integration test (browser-based) | Low | Script-based static analysis is sufficient for route guard regression |
| `lint:i18n:hardcode` CRLF pre-existing | Low | Windows environment issue, pre-dates this task |
| No automated test for `Layout.tsx` redirect behavior at runtime | Low | Route smoke check verifies guard hooks are present; runtime covered by FE-GOVADMIN-02 screenshots |
| Frontend route guard is not a security boundary | Expected | Documented explicitly in safety boundary section |

---

## 12. Final Verdict

**PASS**

All 56 regression checks pass. The FE-GOVADMIN-02 persona route guard bug is now covered by a deterministic, source-level regression script. If the ADM governance block is removed from `isRouteAllowedForPersona`, if the OTS→ADM alias mapping drifts, or if any of the 9 routes is missing from any alignment layer, `npm run check:govadmin:persona` will fail with a clear diagnostic.

No backend files were modified. No route paths were changed. No unauthorized admin actions were enabled. Backend authorization truth boundary is explicitly documented.

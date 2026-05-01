# Responsive App Shell QA / Implementation Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Added responsive app shell / mobile sidebar drawer review and implementation notes. |

## 1. Scope

Global frontend app-shell responsiveness only.

In scope:
- responsive sidebar shell behavior
- mobile drawer overlay behavior
- topbar responsiveness for narrow/tablet widths

Out of scope:
- backend/API/auth changes
- route contract changes
- persona/authorization model changes
- Station Execution domain/action logic changes

## 2. Source Files Inspected

- frontend/src/app/components/Layout.tsx
- frontend/src/app/components/TopBar.tsx
- frontend/src/app/routes.tsx
- frontend/src/app/persona/personaLanding.ts
- docs/design/07_ui/station-execution-responsive-contract-v1.md
- docs/audit/station-execution-responsive-qa/station-execution-responsive-qa-report.md

## 3. Problem Confirmed

From FE-SE-UX-03B screenshot QA:

- 430 x 932: persistent sidebar consumed ~288px and squeezed page content to unusable width.
- 820 x 1180: topbar heading/subtitle area could clip/wrap awkwardly.

Root cause was app shell layout behavior in Layout/TopBar, not Station Execution component internals.

## 4. Implementation Summary

Implemented global shell responsiveness in Layout + TopBar:

1. Desktop sidebar remains persistent at lg+.
2. Mobile/tablet-narrow sidebar is removed from layout flow and opened as overlay drawer.
3. Added mobile menu trigger in TopBar (visible below lg).
4. Drawer supports close via backdrop, close button, and route selection.
5. Added route-change auto-close for the mobile drawer.
6. TopBar now supports narrow-width wrapping and responsive visibility for non-critical controls.

No route/persona/auth logic was modified.

## 5. Responsive Behavior

### Desktop / Tablet landscape (lg+)

- Persistent left sidebar remains visible.
- Existing collapse behavior (`w-72` / `w-20`) remains.

### Tablet portrait / narrow (<lg)

- Persistent sidebar is hidden from flow.
- Sidebar opens via drawer overlay (`fixed inset-0`, drawer width `w-[min(20rem,85vw)]`).
- Main content receives almost full viewport width.
- Backdrop click and close button dismiss the drawer.
- Selecting a nav link dismisses drawer.

### TopBar behavior

- Mobile menu button appears below lg.
- Header allows wrapping without destructive overflow.
- Subtitle is hidden on very narrow screens.
- Plant/language controls are hidden at smallest width; user identity/time remain visible.

## 6. Product / MOM Safety Review

- Backend truth respected: Yes.
- Route definitions changed: No.
- Auth behavior changed: No.
- Persona landing/enforcement changed: No.
- Authorization behavior changed: No.
- Impersonation behavior changed: No.
- Station Execution command/action behavior changed: No.
- `allowed_actions` semantics changed: No.

Navigation/persona logic remains UX-only and does not enforce backend authorization truth.

## 7. Viewports Checked

- 1440 x 900: desktop sidebar remains usable.
- 1180 x 820: layout remains usable with persistent sidebar.
- 820 x 1180: sidebar no longer crowds content (drawer behavior available).
- 430 x 932: content no longer squeezed by persistent sidebar.

## 8. Issues Fixed

- CRITICAL shell issue resolved: narrow/mobile viewport content squeeze due to persistent sidebar width.
- LOW shell issue improved: topbar heading/controls now adapt more gracefully at narrow widths.

## 9. Deferred Issues

- Additional topbar micro-polish (fine-grained typography/control density) can be handled in a separate FE-TOPBAR slice if needed.

## 10. Verification Results

Required frontend gates executed:

- build: pass
- lint: pass
- check:routes: pass
- lint:i18n:registry: pass

Git status captured and reported after change set.

## 11. Final Verdict

FE-LAYOUT-01 accepted.

Global app shell is now responsive for narrow and tablet portrait widths without changing product/domain behavior.

## 12. Recommended Next Slice

FE-TOPBAR-01 — optional topbar density/priority refinement for sub-900px layouts while preserving current behavior and contracts.

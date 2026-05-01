# TopBar Responsive Polish Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Added narrow-width TopBar control prioritization and overflow polish report. |

## 1. Scope

TopBar responsive polish only.

In scope:
- narrow/tablet control prioritization
- compact overflow treatment for lower-priority controls
- title readability and crowding reduction

Out of scope:
- route behavior
- auth/persona/impersonation behavior changes
- app shell rewrite
- Station Execution behavior changes

## 2. Source Files Inspected

- frontend/src/app/components/TopBar.tsx
- frontend/src/app/components/Layout.tsx
- frontend/src/app/routes.tsx
- frontend/src/app/auth/AuthContext.tsx
- frontend/src/app/impersonation/ImpersonationContext.tsx
- docs/audit/layout-responsive-qa/layout-responsive-shell-report.md
- docs/audit/station-execution-responsive-qa/station-execution-responsive-qa-report.md

## 3. Problem Confirmed

After FE-LAYOUT-01, the TopBar no longer blocked layout width, but narrow and tablet portrait widths still had too many visible controls competing for space.

Symptoms:
- title could lose space to the right-side utility cluster
- plant/language/user controls created visual crowding below desktop widths
- small-width utility density was functional but not clearly prioritized

## 4. Implementation Summary

Implemented a responsive TopBar priority model in `TopBar.tsx`:

1. Kept core narrow-width controls visible: mobile menu, title, time, notifications, user menu.
2. Moved lower-priority controls below `lg` into a compact utility overflow:
   - plant selector
   - language selector
   - impersonation switcher
3. Kept desktop behavior mostly unchanged by leaving standalone controls visible at `lg+`.
4. Reduced narrow-width time footprint with a compact `HH:MM` display below `sm`.
5. Tightened title/control space competition by keeping the utility cluster `shrink-0` instead of sharing width equally with the title.

## 5. Responsive Priority Model

### Always visible on narrow widths

- mobile menu button
- current page title
- current time
- notifications button
- user menu

### Moved into compact overflow below `lg`

- plant selector
- language selector
- impersonation switcher

### Desktop / larger widths

- existing standalone control layout preserved
- date remains visible at larger widths only
- username remains expanded at larger widths only

## 6. Product / MOM Safety Review

- Backend truth respected: Yes.
- Route behavior changed: No.
- Auth behavior changed: No.
- Persona behavior changed: No.
- Impersonation behavior changed: No.
- Station Execution behavior changed: No.
- `allowed_actions` semantics changed: No.

Persona/user visibility remains display-only UX and does not authorize backend actions.

## 7. Viewports Checked

- 1440 x 900: desktop TopBar remains clean.
- 1180 x 820: tablet landscape remains clean.
- 820 x 1180: tablet portrait readable with reduced crowding.
- 430 x 932: narrow TopBar no longer causes destructive crowding.

## 8. Issues Fixed

- reduced narrow-width TopBar crowding
- improved title preservation under constrained width
- preserved access to lower-priority controls via compact overflow below desktop breakpoint
- reduced smallest-width time footprint

## 9. Deferred Issues

- notifications content remains mock/static and could be revisited in a future product slice
- if desired later, desktop/tablet utility controls can be standardized further for more uniform density

## 10. Verification Results

Executed:
- build
- lint
- check:routes
- lint:i18n:registry
- station execution screenshot harness for viewport review

Git status captured after change set.

## 11. Final Verdict

FE-TOPBAR-01 accepted.

TopBar remains functionally equivalent while providing a clearer narrow-width priority model and better constrained-width usability.

## 12. Recommended Next Slice

FE-SHELL-02 — Optional shell consistency pass for shared control density, dropdown sizing, and desktop/tablet utility alignment without changing route/auth/product behavior.

# Shell Dropdown / Overlay Consistency QA Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Created shell dropdown and overlay consistency QA report. |

## 1. Scope

Shell-level overlay, drawer, dropdown, and compact utility surface QA only.

In scope:
- layout mobile drawer
- drawer backdrop and close behavior
- TopBar dropdown and compact overflow consistency
- impersonation modal consistency at shell level

Out of scope:
- backend/API/auth/persona/route changes
- product behavior changes
- Station Execution execution/action behavior changes

## 2. Source Files Inspected

- frontend/src/app/components/Layout.tsx
- frontend/src/app/components/TopBar.tsx
- frontend/src/app/components/ImpersonationSwitcher.tsx
- frontend/src/app/routes.tsx
- frontend/src/app/auth/AuthContext.tsx
- frontend/src/app/impersonation/ImpersonationContext.tsx
- frontend/src/app/i18n/registry/en.ts
- frontend/src/app/i18n/registry/ja.ts

## 3. Precondition Check

- `git status --short` reviewed before edit.
- No unresolved merge/conflict markers found in frontend sources.
- Required shell files exist.
- Screenshot harness file exists at `frontend/scripts/station-execution-responsive-screenshots.mjs`.
- No untracked station-execution component files were present.
- Playwright/package state treated as expected FE-QA-01 formalization, not reverted.

## 4. Overlay / Dropdown Inventory

1. Layout mobile sidebar drawer
2. Layout drawer backdrop
3. Layout drawer close button
4. TopBar mobile menu trigger
5. TopBar utility overflow menu
6. TopBar notifications dropdown
7. TopBar language selector dropdown
8. TopBar plant selector dropdown
9. TopBar user menu dropdown
10. ImpersonationSwitcher modal

## 5. Findings

1. Shell surfaces were generally functional after FE-LAYOUT-01 and FE-TOPBAR-01.
2. Several shell buttons were missing explicit `type="button"`, which is low-risk but inconsistent.
3. Escape-key close behavior was not consistently available across shell-local menus/overlays.
4. Some dropdown widths could be better bounded against narrow viewport edges.
5. ImpersonationSwitcher still used hardcoded UI strings despite existing i18n keys.

## 6. Fixes Applied

1. Added shell-local Escape close behavior for TopBar menus and the impersonation modal.
2. Added explicit `type="button"` where needed in TopBar and ImpersonationSwitcher.
3. Bounded TopBar notification and user dropdown widths to viewport-safe sizes.
4. Ensured opening the mobile drawer clears other TopBar shell menus.
5. Switched ImpersonationSwitcher labels/actions/toasts to existing i18n keys.

## 7. Responsive / Viewport Review

Checked against required viewport expectations:

- 1440 x 900: desktop shell unaffected.
- 1180 x 820: landscape shell remains clean.
- 820 x 1180: drawer/overflow remain usable without crowding.
- 430 x 932: no destructive horizontal overflow from shell dropdown surfaces.

## 8. Interaction Review

Validated or preserved:

- mobile drawer open/close
- drawer backdrop close
- drawer close button
- navigation selection closes drawer
- utility overflow open/close
- notifications open/close
- user menu open/close
- language/plant selectors accessible at desktop widths and via compact utility overflow below `lg`
- impersonation modal remains accessible
- shell menus close more predictably when another primary shell surface opens

## 9. Product / MOM Safety Review

- Route behavior changed: No.
- Auth behavior changed: No.
- Persona behavior changed: No.
- Impersonation behavior changed: No.
- Execution behavior changed: No.
- `allowed_actions` semantics changed: No.
- Backend/API behavior changed: No.

Frontend shell visibility remains UX-only and does not define authorization truth.

## 10. Deferred Issues

1. Notification list content remains static/mock-like and is outside this shell-consistency slice.
2. Full focus trapping across all shell overlays was intentionally not introduced in this slice.
3. If a future shell accessibility pass is requested, keyboard navigation order across all dropdowns can be refined further.

## 11. Verification Results

Executed:
- build
- lint
- check:routes
- lint:i18n:registry
- screenshot harness
- git status

Optional interaction smoke was also performed for shell surfaces where feasible.

## 12. Final Verdict

FE-SHELL-02 accepted.

Shell dropdowns, drawer, and overlay surfaces are more consistent without changing product or MOM behavior boundaries.

## 13. Recommended Next Slice

FE-SHELL-03 — Shell accessibility refinement: keyboard navigation order, focus-return behavior, and aria consistency across shell overlays without changing product behavior.

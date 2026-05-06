# FE-HEADER-01 Header Audit + Operational Context Header Redesign Report

## History
| Date | Version | Change |
|---|---|---|
| 2026-05-06 | v1.0 | Audited app-shell header/top area and implemented a narrow operational context header redesign with preserved route/sidebar/persona behavior. |

## Source Files Inspected
- .github/copilot-instructions.md
- .github/agent/AGENT.md
- .github/copilot-instructions-design-md-addendum.md
- .github/copilot-instructions-hard-mode-mom-v2-addendum.md
- .github/copilot-instructions-hard-mode-mom-v3-addendum.md
- .github/flezibcg-ai-brain-v6-auto-execution.prompt.md
- docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
- docs/ai-skills/hard-mode-mom-v3/SKILL.md
- docs/ai-skills/design-md-ui-governor/SKILL.md
- docs/ai-skills/stitch-design-md-ui-ux/SKILL.md
- docs/ai-skills/design-system-enforcer/SKILL.md
- .copilot/DESIGN.md
- docs/design/DESIGN.md
- docs/design/INDEX.md
- docs/design/AUTHORITATIVE_FILE_MAP.md
- docs/design/00_platform/product-business-truth-overview.md
- docs/governance/CODING_RULES.md
- docs/governance/ENGINEERING_DECISIONS.md
- docs/governance/SOURCE_STRUCTURE.md
- docs/audit/frontend-coverage-baseline-freeze-report.md
- docs/audit/frontend-source-alignment-snapshot.md
- frontend/src/app/components/Layout.tsx
- frontend/src/app/components/TopBar.tsx
- frontend/src/app/components/RouteStatusBanner.tsx
- frontend/src/app/components/MockWarningBanner.tsx
- frontend/src/app/components/SidebarSearch.tsx
- frontend/src/app/screenStatus.ts
- frontend/src/app/navigation/navigationGroups.ts
- frontend/src/app/persona/personaLanding.ts
- frontend/src/app/i18n/registry/en.ts
- frontend/src/app/i18n/registry/ja.ts
- frontend/package.json

## Current Header Audit Findings

### Visual hierarchy
- Existing header had mixed priorities: page title + plant selector + clock + notifications + language + impersonation + user menu in one row.
- Center of attention drifted to utility controls instead of operational context.

### Operational context and truth safety
- Header displayed a mutable plant selector with static options (DMES/Plant A/Plant B/Factory 1/Factory 2) not backed by backend context.
- No explicit tenant context display from authenticated source despite tenant_id being available.
- No explicit scope display, creating ambiguity about operational context readiness.

### Status/disclosure interaction
- RouteStatusBanner was already correctly rendered below header and remained visible.
- Screen phase badge existed in RouteStatusBanner top strip and should remain for MOCK/SHELL/PARTIAL/FUTURE disclosure.

### Responsiveness and focus behavior
- Mobile drawer open/close and focus return behavior in Layout was already implemented and should be preserved.
- Header utility density risked overflow and control crowding at narrow widths.

### Accessibility
- Existing top controls mostly had aria attributes and focus-visible styling.
- Some utility content (example notification items) used static copy and did not reflect operational truth.

### i18n and hardcoded strings
- Existing TopBar had several hardcoded user-facing labels and fake notification content.
- Existing i18n infrastructure and parity checks were already strong and should be extended for new header labels.

## Required MOM Safety Check (Pre-change)
- Header currently displays tenant/plant/scope: tenant not explicit; plant shown as static selector; scope not shown.
- Header infers persona/user permission: no backend authorization inference, but persona remains UX-layer routing policy.
- Screen status source: uses SCREEN_STATUS_REGISTRY via RouteStatusBanner.
- Header overlap with RouteStatusBanner: no overlap detected.
- Hardcoded mock/live claims in header: yes (sample notifications and static plant list).
- Dangerous operational actions present in header: none; actions were utility-level only.

## Redesign Decision
- Keep sidebar IA, route registry, persona enforcement, and banner behavior unchanged.
- Replace top utility-heavy header with a focused operational context header component:
  - Left: mobile drawer trigger + domain label + page title.
  - Center (desktop): safe context strip with tenant and role from current authenticated/impersonation context, and explicit scope pending placeholder.
  - Right: screen phase badge, time display, language picker, impersonation switcher, user menu.
  - Mobile secondary row: condensed tenant/role context.
- Remove fake plant mutation UI from header to avoid pretending context authority.
- Preserve RouteStatusBanner placement directly under header.

## Files Changed
- frontend/src/app/components/AppHeader.tsx (new)
- frontend/src/app/components/Layout.tsx
- frontend/src/app/i18n/registry/en.ts
- frontend/src/app/i18n/registry/ja.ts
- frontend/e2e/header-operational-context.spec.ts (new)

## Screens / Routes Sampled
- Source-level audit sampling: /dashboard, /operations, /station, /integration, /quality, /reports/*, /ai/*
- Focused runtime checks: /integration (SHELL disclosure + header context), mobile drawer on /integration

## Responsive / Accessibility Notes
- Desktop: context strip visible and non-overlapping with right-side controls.
- Tablet/mobile: title truncation preserved; compact context row shown below main header row.
- Mobile drawer behavior remains in Layout with preserved focus-return behavior.
- Keyboard coverage improved by focused Playwright checks for menu open/close and focus return.

## MOM Safety Check (Post-change)
- Backend truth respected: Yes
- Permission truth respected: Yes
- Execution state truth respected: Yes
- Quality truth respected: Yes
- Integration/ERP truth respected: Yes
- AI/Digital Twin truth respected: Yes
- Mock/Shell/Future disclosures remain visible: Yes

## Verification Commands and Results

### Pre-change baseline
- Command: cd frontend && npm.cmd run lint
- Result: PASS

- Command: cd frontend && npm.cmd run build
- Result: PASS (vite build completed; chunk-size warning unchanged)

- Command: cd frontend && npm.cmd run check:routes
- Result: PASS (REGISTERED 78, SMOKE_TARGETS 77, FAIL 0)

- Command: cd frontend && npm.cmd run lint:i18n:registry
- Result: PASS (1847 keys synchronized)

### Post-change required gates
- Command: cd frontend && npm.cmd run lint
- Result: PASS

- Command: cd frontend && npm.cmd run build
- Result: PASS (vite build completed; chunk-size warning unchanged)

- Command: cd frontend && npm.cmd run check:routes
- Result: PASS (REGISTERED 78, SMOKE_TARGETS 77, FAIL 0)

- Command: cd frontend && npm.cmd run lint:i18n:registry
- Result: PASS (1857 keys synchronized)

### Focused Playwright coverage
- Command: cd frontend && npx.cmd playwright test e2e/header-operational-context.spec.ts --project=chromium
- Result: PASS (2 passed)

## Remaining Gaps
- Existing TopBar component remains in source but is no longer used by Layout; this is intentional for narrow-slice safety.
- Header currently exposes tenant and role only from already-available frontend auth/impersonation context; no backend scope projection is yet integrated.
- Global notification backend integration remains out of scope and intentionally not introduced.

## Next Recommended Slice
- FE-HEADER-02: Remove or archive unused TopBar component, then add route-title/domain-title mapping from a centralized i18n-aware route metadata source to eliminate remaining title hardcoding in Layout.

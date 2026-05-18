---
name: design-md-ui-governor
description: |
  FleziBCG canonical UI/UX skill. ALWAYS use this skill before writing any frontend code,
  touching any React/Tailwind file, generating any screen pack, updating DESIGN.md,
  reviewing Figma/Stitch output, or making any visual/layout decision — even for "quick
  UI fix", "minor layout tweak", "small style change", or "just add a button". Use it
  when the task mentions: UI, UX, frontend, FE, React, Tailwind, shadcn, component,
  screen, page, route, layout, cockpit, operator, supervisor, dashboard, form, list,
  table, status badge, color, spacing, responsive, touch, persona navigation, mode A,
  station session, DESIGN.md, design tokens, Figma Make, Google Stitch, screen pack,
  visual hierarchy, or "this looks cluttered / rối / messy". Also use when reviewing
  whether existing UI is too generic, too decorative, or unsafe for MOM execution.
  Skill enforces backend-truth boundary, screen phase discipline, industrial UX
  numerics, anti-clutter diagnostic, and source-aligned implementation.
---

# Skill — DESIGN.md UI Governor for FleziBCG

> **Canonical UI skill.** This is the single source of truth for FleziBCG UI/UX work.
> The skills `stitch-design-md-ui-ux` and `design-system-enforcer` are deprecated
> stubs that point here.

## 1. Purpose

This skill makes FleziBCG UI output:

- **operationally clear** — operator/supervisor sees current state + next safe action without hunting;
- **source-aligned** — extends existing app shell/components instead of redesigning from zero;
- **MOM-safe** — never lets frontend become source of execution/permission/quality truth;
- **industrially fit** — sized for shopfloor distance, glove, lighting;
- **anti-cluttered** — fails fast against the "rối" pattern that drove this skill consolidation;
- **honest** — never presents future scope as active functionality.

This skill governs UI design and FE implementation guidance only. It does not
override domain, backend, authorization, event, API, or database contracts.

---

## 2. Stack (verified 2026-05-17)

FleziBCG frontend stack — your output MUST match this; do not propose alternative
libraries unless the user explicitly opens that scope:

| Layer | Technology |
|---|---|
| Framework | React 18.3 + Vite 6 |
| Styling | Tailwind v4 (CSS-first config via `@theme` in `frontend/src/styles/theme.css`) |
| Component primitives | Radix UI (full suite) — shadcn/ui pattern |
| Utility | `class-variance-authority`, `clsx`, `tailwind-merge` |
| Icons | `lucide-react` |
| Toaster | `sonner` |
| Command palette | `cmdk` |
| Drawer | `vaul` |
| Forms | `react-hook-form` |
| Routing | `react-router` v7 |
| Charts | `recharts` |
| Virtualization | `react-window` |
| i18n | local `useI18n()` hook + registry parity lint (`scripts/check_i18n_registry_parity.mjs`) |
| Animation | `motion` (Framer Motion successor) — use sparingly |

**Coexistence note (anti-pattern):** `@mui/material` is present as **legacy**.
New code MUST use shadcn/ui (Radix + cva) pattern. Do not introduce new MUI
components. If a screen mixes MUI and shadcn, flag it in the implementation report.

---

## 3. When to Use This Skill

Trigger on any of:

- writing or editing any file under `frontend/src/**`;
- creating, updating, or deleting any route in `frontend/src/app/routes*.tsx`;
- updating `DESIGN.md` or any file under `docs/design/**`;
- consuming Figma Make / Google Stitch / design-md output;
- reviewing whether existing UI is cluttered, decorative, or operationally unsafe;
- the user uses the word "rối", "messy", "cluttered", "looks off", "doesn't feel right";
- the user asks for "just a small UI change" — small UI changes break consistency more often than big ones;
- generating a coding-agent prompt that touches FE.

**Co-skills** — load alongside this skill:

- `hard-mode-mom-v3` — whenever UI touches execution state, commands/events, projections, station/session/operator/equipment, production reporting, downtime, quality hold, material/inventory execution, tenant/scope/auth, role/action/scope, audit, or any critical invariant.
- `slice-strategy` — when generating coding-agent prompts.
- `pr-gate-reviewer` — when reviewing a PR.

---

## 4. Mandatory Reading Order

Before any non-trivial UI work, read in this order; stop and ask if a file is
missing rather than guessing:

1. `.github/copilot-instructions.md` — engineering decisions
2. `DESIGN.md` (root or `docs/design/DESIGN.md`)
3. `docs/ai-skills/design-md-ui-governor/SKILL.md` — this file
4. `docs/ai-skills/design-md-ui-governor/references/industrial-ux-standards.md` — sizing/distance/contrast numerics
5. `docs/ai-skills/design-md-ui-governor/references/layout-templates.md` — operator cockpit / supervisor dashboard / form / list / single-screen wizard
6. `docs/ai-skills/design-md-ui-governor/references/anti-clutter-diagnostic.md` — fail-fast checklist
7. `docs/ai-skills/design-md-ui-governor/references/design-md-format-rules.md`
8. `docs/ai-skills/design-md-ui-governor/references/design-md-canonical-example.md` — full DESIGN.md exemplar
9. `docs/ai-skills/design-md-ui-governor/references/flezibcg-mom-ui-guardrails.md`
10. `docs/ai-skills/design-md-ui-governor/references/extended-guardrails.md` — offline/scanner/alert/multi-station/long-op
11. `docs/ai-skills/design-md-ui-governor/references/source-alignment-rules.md`
12. `docs/audit/frontend-source-alignment-snapshot.md` if present
13. relevant UI/screen inventory + domain contract docs (when UI touches execution/quality/material/integration/IAM/scope/audit).

If `docs/audit/frontend-source-alignment-snapshot.md` is missing and the task
depends on current frontend structure, inspect source directly or stop and
create the snapshot first.

---

## 5. Core Rules

### 5.1 Backend is source of truth

Frontend MUST NOT decide:

- execution state;
- authorization;
- allowed actions;
- quality pass/fail;
- acceptance gate result;
- ERP posting state;
- backflush completion;
- AI deterministic outcome;
- digital twin truth.

Frontend may only **display** backend-derived truth and **propose** commands
that the backend will accept, reject, or transform.

### 5.2 Persona is UX, not permission

Persona-based navigation may help users find screens; it MUST NOT be the
authorization mechanism. Sidebar/menu filtering by persona is acceptable as a
UX convenience as long as backend rejects unauthorized commands regardless of
UI state.

### 5.3 Screen phase discipline

Every screen must declare exactly one phase:

| Phase | Meaning |
|---|---|
| `ACTIVE` | Fully implemented, connected to live backend, safe to use in production |
| `PARTIAL` | Backend-connected for primary path, with mock or shell sections clearly labeled |
| `MOCK` | Render-only, no backend; for design review and feedback |
| `SHELL` | Route exists, navigation works, body is empty/placeholder |
| `FUTURE` | Roadmap placeholder; must be visually distinct (greyed/disabled) |
| `DISABLED` | Was previously available, now hidden behind flag — keep in screenStatus for audit |

Future functionality MUST NOT pretend to be implemented. Use the `ScreenStatusBadge`
component (already in app) to surface phase in the screen header.

### 5.4 Source alignment first

Do not redesign from zero when usable screens/components exist. Preserve and
extend current patterns unless the task explicitly authorizes migration.

### 5.5 Industrial UX discipline

Operator/shopfloor UI must be:

- **state-first** — current state visible within 2 seconds of glance;
- **action-singular** — at most one primary action per cognitive context;
- **blocker-visible** — anything preventing the next action is visible without scrolling;
- **distance-readable** — see `references/industrial-ux-standards.md` for size/contrast numerics;
- **touch-tolerant** — gloved tap targets, accidental-tap-resistant;
- **noise-tolerant** — readable under fluorescent / mixed lighting;
- **uncluttered** — passes the anti-clutter diagnostic before merge.

### 5.6 Responsive is mandatory

Every UI task must declare responsive behavior for:

- desktop (≥1280px);
- tablet landscape (1024–1279px) — primary shopfloor target;
- tablet portrait (768–1023px);
- narrow (<768px) — supervisor mobile glance only; not for operator workflow.

For Station Execution, **tablet landscape is the design primary**, not desktop.

### 5.7 i18n and status discipline

User-facing strings MUST go through `useI18n()` and be registered in the i18n
registry. `npm run lint:i18n` enforces this.

Status labels MUST map to stable codes from the status token system (see § 6),
not freeform color choices.

### 5.8 Color/token discipline

Use design tokens from `frontend/src/styles/theme.css`. Never use raw hex in
component code. New tokens require updating `theme.css` AND `DESIGN.md`
together; never one without the other.

### 5.9 Known DESIGN.md ↔ theme.css drift

As of 2026-05-17, `DESIGN.md` § 2 uses semantic roles (`status.success/info/warning/danger/neutral`)
while `theme.css` exposes operational tokens (`--status-pending/in-progress/completed/blocked/delayed/on-hold/cancelled`).

Until reconciled, **map** rather than rename:

| DESIGN.md role | theme.css token |
|---|---|
| `status.success` | `--status-completed` |
| `status.info` | `--status-in-progress` |
| `status.warning` | `--status-delayed` (near-breach) or `--status-on-hold` (hold) |
| `status.danger` | `--status-blocked` |
| `status.neutral` | `--status-pending` or `--status-cancelled` |

Flag this drift in your report. Reconciliation is a separate slice (UI-TOKEN-RECONCILE).

---

## 6. Anti-Clutter Gate (the "rối" fix)

Before finalizing any operator/supervisor screen, run the anti-clutter
diagnostic from `references/anti-clutter-diagnostic.md`. The screen must score
PASS on all required checks.

**Hard fails (any one rejects the slice):**

1. More than one primary CTA visible in the same cognitive frame.
2. More than 5 status indicators visible without aggregation.
3. Scroll required to see current state on the design primary breakpoint.
4. Hover-only controls on touch-primary screens.
5. Three or more simultaneous panels demanding equal user attention (the Mode A pattern).

**Pattern correction for Mode A (Station Session):** use the **Single-Screen
Wizard** pattern from `references/layout-templates.md` § 5. Render exactly one
of {Open / Identify Operator / Bind Equipment / Close} at a time, driven by
backend session state. Other panels collapse to a step indicator.

---

## 7. Route Accessibility Gate

For any new route/page, ALL must be verified:

1. Route registered in the actual router tree (`frontend/src/app/routes.tsx` or equivalent).
2. Route nested under correct layout boundary.
3. Route not swallowed by index/catch-all/fallback.
4. Auth guard behavior explicitly understood and documented.
5. Persona route enforcement updated if persona allowlist exists.
6. Sidebar/menu entry exists when screen is user-accessible.
7. `screenStatus` entry exists and matches the route pattern.
8. Direct URL smoke test passes (manual or `scripts/route-smoke-check.mjs`).

A passing build/lint is necessary but not sufficient.

---

## 8. Component Quality Checklist

Before finalizing a UI component, verify:

- follows `DESIGN.md` and uses tokens, not hex;
- works with existing app shell;
- uses shadcn/ui pattern (Radix + cva) — not new MUI;
- has loading state when data-driven (skeleton preferred over spinner for >300ms loads);
- has error state with retry affordance;
- has empty state with next-action hint;
- does not fake auth or backend-derived state;
- does not present future scope as active;
- has reasonable name (matches feature, not visual);
- is reusable when used >1 place;
- passes anti-clutter diagnostic when it composes a screen.

---

## 9. UI Screenshot Evidence Gate

For every non-trivial UI/frontend slice, screenshots are required evidence.
Build/lint alone is not enough.

### Required screenshot behavior

- Use an existing screenshot harness when available.
- If no harness exists, add a narrow Playwright/screenshot harness for the
  touched route, component state, or viewport.
- Save screenshots under `docs/audit/<slice-or-screen>/` or the existing
  screen-specific audit folder.
- List exact screenshot paths in `docs/agent-reports/latest-agent-report.md`.
- State whether screenshots use mocked API data or a real backend.
- Cover the changed UI state, not only a nearby route or the page top.
- Cover at least one narrow viewport whenever layout can be affected.

### Required negative assertions

When a UI slice removes clutter, replaces a shell, hides a warning, changes a
mode, or changes action hierarchy, screenshot QA must assert both presence and
absence:

- expected new component/state is visible;
- replaced or removed component is not visible;
- deprecated labels, debug shells, old banners, and mock/partial warnings are
  not visible in the target state;
- primary CTA count matches the expected cognitive frame;
- action hierarchy matches the business state being rendered.

Example for Station Execution Mode B:

- `station-execution-cockpit` visible;
- `Station Workflow Shell` not visible;
- `STX-` labels not visible;
- `Partial Data` banner not visible unless a specific section is truly partial;
- `Report Qty` visible when reporting is the next production action;
- `Complete Operation` not primary while remaining quantity is greater than 0.

### Required assertion failure behavior

Screenshot harness assertions must fail the command.

Allowed:

- `throw new Error(...)`;
- Playwright `expect(...)`;
- returning a rejected promise;
- explicit non-zero process exit after all failures are collected.

Not allowed:

- only setting `process.exitCode = 1` and continuing to print pass-like output;
- saving screenshots after assertion failures and reporting the command as pass;
- reporting screenshot capture as valid evidence when target-state assertions
  failed.

### Evidence quality rules

- Do not use stale screenshots from an earlier run as evidence.
- Prefer task-specific or timestamped output folders when old screenshots exist.
- If old screenshots remain in the folder, the report must list only the current
  run's screenshots.
- If the screenshot does not visually show the acceptance area, scroll or add a
  second focused screenshot for that area.
- The report must include an assertion summary and exact screenshot paths.

---

## 10. UI Implementation Report (required output)

Every UI/FE task MUST end with this report:

Before marking done, also overwrite the canonical repo report file:

```text
docs/agent-reports/latest-agent-report.md
```

The chat response may summarize the report, but this file is the source used for
follow-up review.

```markdown
# UI/UX Implementation Report

## Selected Skill
design-md-ui-governor (+ co-skills: <list>)

## Source Inputs Read
<bullet list of files read>

## Scope
- In scope:
- Out of scope:

## Design System Alignment
- Tokens used: <list of CSS variables / Tailwind theme tokens>
- New tokens introduced: <list, or "none">
- DESIGN.md updated: Yes/No (must be Yes if new token introduced)

## Source Alignment
- Existing components reused:
- Existing components extended:
- New components introduced:

## Files Changed
<list with line counts>

## Screens Affected
<screen name → phase>

## Density Mode
cockpit | dashboard | form | list | multi-station | wizard

## Data Source Status
ACTIVE / PARTIAL / MOCK / SHELL / FUTURE / DISABLED

## MOM Safety Check
- Backend truth respected:
- Permission truth respected:
- Execution state truth respected:
- Quality truth respected:
- Integration/ERP truth respected:
- AI/Digital Twin truth respected:

## Anti-Clutter Check
- Primary CTA count in cognitive frame:
- Status indicator count without aggregation:
- Scroll-to-state on design primary breakpoint:
- Hover-only controls on touch screen:
- Simultaneous demanding panels:
- Overall: PASS / FAIL

## Industrial UX Check
- Touch target min (dp):
- Body font min (px):
- Status font min (px):
- Primary metric font min (px):
- Color+icon+label 3-channel coding:
- WCAG AA contrast verified:

## Persona Viewing-Context Check
- Persona:
- Viewing distance:
- Lighting context:
- Gloved use:

## Offline / Degraded Check
- Behavior when API fails:
- Behavior when offline:
- Optimistic UI used: Yes/No (if Yes, explain reconciliation)

## Scanner Input Check (if applicable)
- Focus trap pattern:
- Scan-then-confirm UI:
- N/A reason if not applicable:

## Responsive / Accessibility Check
- Desktop ≥1280:
- Tablet landscape 1024–1279 (design primary for shopfloor):
- Tablet portrait 768–1023:
- Narrow <768:
- Keyboard nav:
- Screen reader labels:

## Route Accessibility Verification
- Route path:
- Registered in routes.tsx: Yes/No
- Nested under Layout: Yes/No
- Auth guard behavior:
- Persona allowlist updated: Yes/No/N/A
- Sidebar/menu entry added: Yes/No/N/A
- screenStatus entry added: Yes/No
- Direct URL checked:
- Detail route checked if applicable:

## Tests / Build Run
- `npm run build`:
- `npm run lint`:
- `npm run lint:i18n`:
- `npm run check:routes`:
- Playwright E2E (if route changed):

## Screenshot Evidence
- Screenshot command:
- Assertion summary:
- Screenshot paths:
- Viewports covered:
- UI states covered:
- Mocked API or real backend:
- Stale screenshots excluded from report: Yes/No

## Known Limitations

## Report Export
- Canonical report file: docs/agent-reports/latest-agent-report.md
- Written before completion: yes/no

## Next Recommended FE Slice
```

---

## 11. Hard Reject Conditions

Reject or stop the slice if UI:

- makes frontend the source of execution/permission/quality/acceptance/ERP/backflush truth;
- treats AI insight as deterministic authority (must show advisory label + source + uncertainty);
- makes digital twin visualization look authoritative without backend/twin state evidence;
- creates active screens for future scope without `FUTURE`/`DISABLED` label;
- redesigns app shell without explicit scope;
- mixes mock data into production API paths;
- ignores responsive/touch constraints for station/operator screens;
- copies third-party brand design language as FleziBCG identity;
- introduces new `@mui/material` components in new code;
- introduces raw hex colors instead of tokens;
- introduces user-facing strings without i18n registry entry;
- adds a primary CTA that competes with an existing primary CTA in the same frame;
- reports UI PASS while screenshot assertions fail;
- shows screenshots that do not reach the target state;
- leaves intended new UI files untracked or unintegrated;
- claims a component is used when it is not imported/rendered by the target route.

---

## 12. Versioning

- v3: consolidated canonical skill, dated 2026-05-17.
- v4 (current): added screenshot evidence hard gate, assertion failure
  discipline, and diff/report consistency rules after Station Execution cockpit
  review failures, dated 2026-05-18.
- Predecessor skills (`stitch-design-md-ui-ux`, `design-system-enforcer`) are
  now stub pointers and must not be loaded independently.

# DESIGN.md — FleziBCG Manufacturing Operations Platform

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v2.0 | Upgraded to DESIGN.md-style design-system guide for AI UI generation, aligned with FleziBCG MOM boundaries. |

## Status

Authoritative AI-readable design-system guide for FleziBCG frontend, Figma Make, and UI implementation agents.

This file defines how FleziBCG should look and behave at the UI level. It does **not** define backend truth, business rules, API contracts, authorization, or execution state transitions.

---

# 1. Visual Theme & Atmosphere

FleziBCG is a **Manufacturing Operations Platform** for industrial execution, governance, visibility, and operational intelligence.

The UI should feel:

- operational;
- trustworthy;
- precise;
- calm under pressure;
- enterprise-ready;
- manufacturing-aware;
- information-dense but not noisy.

The UI must **not** feel:

- playful consumer SaaS;
- generic admin template;
- speculative sci-fi dashboard;
- over-animated;
- decorative without operational consequence;
- AI-first before execution truth is stable.

Design language:

- industrial clarity;
- neutral base surfaces;
- strong semantic status language;
- clear hierarchy between current state, next action, and supporting context;
- minimum visual drama, maximum operational readability.

---

# 2. Color Palette & Roles

Use semantic color roles rather than arbitrary decorative colors.

| Token | Role | Usage |
|---|---|---|
| `surface.app` | App background | Main application shell background |
| `surface.panel` | Cards/panels | Primary content panels |
| `surface.raised` | Elevated panels | Modals, popovers, active detail panes |
| `border.subtle` | Structure | Card, table, section borders |
| `text.primary` | Primary text | Titles, key labels, operational state |
| `text.secondary` | Secondary text | Descriptions, metadata, helper text |
| `text.muted` | Low-emphasis text | Timestamps, inactive hints |
| `action.primary` | Primary action | Main command, selected nav, active CTA |
| `status.success` | Healthy / completed / passed | Completed operation, passed inspection, available resource |
| `status.info` | Running / informational | Running operation, advisory context |
| `status.warning` | Attention / delayed / pending | Paused, pending review, near breach |
| `status.danger` | Blocked / failed / critical | Blocked, failed, rejected, unsafe |
| `status.neutral` | Draft / unknown / inactive | Pending, planned, disabled, unknown |

Status mapping guidance:

| Operational Meaning | Recommended Semantic Role |
|---|---|
| `RUNNING` | `status.info` |
| `PAUSED` | `status.warning` |
| `BLOCKED` | `status.danger` |
| `COMPLETED` | `status.success` |
| `CLOSED` | `status.neutral` + locked treatment |
| `QC_PASSED` | `status.success` |
| `QC_FAILED` | `status.danger` |
| `QC_HOLD` | `status.warning` or `status.danger` depending severity |
| `ERP_POSTING_PENDING` | `status.warning` |
| `ERP_POSTING_FAILED` | `status.danger` |
| `AI_ADVISORY` | `status.info` with advisory label |

Rules:

- Never rely on color only. Pair status color with text, icon, or badge label.
- Do not invent new status colors in individual screens.
- Do not use red/orange/green decoratively; reserve them for operational meaning.

---

# 3. Typography Rules

Use modern sans-serif typography:

```text
font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

Type hierarchy:

| Role | Usage |
|---|---|
| Display | Operator current state, major KPI, critical station number |
| H1 | Page title |
| H2 | Section title |
| H3 | Card title / panel title |
| Body | Normal operational text |
| Body small | Metadata, timestamps, helper text |
| Mono | IDs, lot numbers, event codes, technical references |

Operator/station screens:

- Current state should be readable at distance.
- Primary action label should be large and unambiguous.
- Key quantities and timers should use large numeric treatment.
- Avoid tiny dense metadata in the primary operator cockpit.

Admin/supervisory screens:

- Use tighter density but preserve scannability.
- Tables should have clear headers and meaningful status badges.
- Do not bury risk/blockage status in low-contrast text.

---

# 4. Component Stylings

## 4.1 App Shell

Use:

- left sidebar for primary navigation;
- top header for tenant, plant, user/session, and global context;
- main content area for the active work screen;
- optional right detail panel for contextual drill-down.

The app shell must support domain grouping:

- Manufacturing Operations;
- Master Data;
- Quality;
- Material / Traceability;
- Supervisory;
- Integration;
- Reporting;
- Administration;
- Future / Advisory modules.

Navigation exposure is UX only. It is not authorization truth.

## 4.2 Page Header

Each page should include:

- title;
- domain/subtitle;
- phase/status badge where useful;
- primary action if active;
- contextual selectors only when needed.

## 4.3 Cards and Panels

Cards should be structured, not decorative.

Use cards for:

- operational context summary;
- KPI strip;
- current state;
- blocker panel;
- event summary;
- detail panel.

Avoid:

- too many equal-weight cards;
- dashboard clutter;
- cards that do not drive action or understanding.

## 4.4 Buttons

Rules:

- One dominant primary action per work area where possible.
- Destructive/governed actions require confirmation or clear contextual warning.
- Operator primary actions should be 48–56px+ high.
- Do not show enabled actions unless backend `allowed_actions` or connected contract supports them.
- Disabled actions should explain why when operationally important.

## 4.5 Tables / Data Grids

Use:

- sticky headers for long operational lists;
- filters above table;
- status/phase badges;
- row click for detail;
- empty/loading/error states;
- clear timestamp and ID display.

Do not:

- place critical actions in tiny icon-only cells;
- mix mock rows with real rows without clear isolation;
- hide blocked/held/delayed status in secondary columns.

## 4.6 Status Badges

Every status badge must map to a stable status code or explicitly declared placeholder state.

Badge types:

- runtime status;
- quality status;
- closure status;
- integration status;
- phase marker;
- future/placeholder marker;
- AI advisory marker.

## 4.7 Forms

Forms must show:

- required fields;
- validation errors;
- backend error code when returned;
- clear submit/cancel actions;
- confirmation for governed/destructive commands.

Forms must not:

- calculate authoritative business results client-side;
- decide pass/fail/approval/disposition client-side;
- submit hidden fake values to satisfy UI flow.

## 4.8 Modals / Dialogs

Use modals for:

- confirmation;
- bounded operator entry;
- reason capture;
- details that should not navigate away.

Avoid nested modal stacks.

## 4.9 Timeline / Event History

Event timeline must show:

- timestamp;
- actor;
- event type;
- entity context;
- payload summary;
- correlation/reference where relevant.

Do not make event history look like chat.

---

# 5. Layout Principles

## 5.1 Global Layout

Default page structure:

1. Page header
2. Context summary / KPI strip
3. Main work area
4. Detail or side panel if useful
5. Empty/loading/error states

## 5.2 Density Modes

| Screen Type | Density |
|---|---|
| Operator / station execution | Touch-first, low clutter |
| Supervisor monitor | Dense but structured |
| Admin / governance | Medium density |
| Reporting | Data-dense with clear filters |
| Future AI/Twin | Clearly marked advisory/future |

## 5.3 Operator Cockpit Layout

Operator cockpit should show at most:

1. Current station / operation context
2. Current state
3. Key quantities / elapsed time / target
4. Primary action zone
5. Blocker or warning panel

Avoid:

- multi-table cockpit;
- tiny dropdowns for critical actions;
- hidden hover-only controls;
- multiple competing primary actions;
- fake progress indicators not backed by backend truth.

## 5.4 Supervisor Layout

Supervisor screens should emphasize:

- current line/station state;
- blocked/delayed operations;
- work-in-progress;
- downtime and reason context;
- escalation/action need;
- drill-down to operation detail.

---

# 6. Depth & Elevation

Use elevation sparingly.

| Level | Usage |
|---|---|
| Base | App background |
| Panel | Cards and work areas |
| Raised | Active detail panel, popover |
| Modal | Dialog/confirmation |
| Critical overlay | Rare blocking warnings only |

Rules:

- Prefer border + spacing over heavy shadows.
- Avoid glassmorphism and neon glow.
- Critical warnings should be visually clear without overwhelming normal operation.

---

# 7. Do's and Don'ts

## Do

- Preserve backend truth boundary.
- Use backend `allowed_actions` when connected.
- Mark mock, shell, disabled, and future screens explicitly.
- Use semantic status badges.
- Use i18n keys for user-facing text.
- Keep operator screens readable and touch-friendly.
- Include loading, error, and empty states.
- Design by domain pack, not all screens at once.
- Keep future modules visually present but disabled where useful.

## Don't

- Do not fake authorization.
- Do not fake execution transitions.
- Do not fake quality pass/fail.
- Do not fake acceptance gate approval.
- Do not fake ERP posting success.
- Do not fake backflush completion.
- Do not present AI output as deterministic truth.
- Do not make Digital Twin look like real-time truth unless it is actually connected.
- Do not copy public brand design systems into FleziBCG.
- Do not redesign the whole app shell without explicit scope.

---

# 8. Responsive Behavior

## Breakpoint behavior

| Viewport | Expected Behavior |
|---|---|
| Desktop wide | Sidebar + main + optional right panel |
| Desktop standard | Sidebar + main; right panel collapsible |
| Tablet landscape | Sidebar may collapse; station actions remain touch-friendly |
| Tablet portrait | Navigation collapses; primary operator context remains visible |
| Mobile | Mostly supervisor/admin quick review only; not default for station operation unless explicitly designed |

## Touch targets

- Normal UI: 40–44px minimum.
- Operator / station UI: 48–56px+ minimum.
- Dangerous/governed actions need separation from routine actions.

## Responsive rules

- Do not hide critical execution state on smaller screens.
- Do not push primary operator action below dense secondary content.
- Do not make table-only layouts mandatory on tablet/operator screens.
- Prefer stacked cards for operator context on constrained widths.

---

# 9. Agent Prompt Guide

When generating UI, the agent must read:

1. `DESIGN.md`
2. `docs/design/DESIGN.md` if present
3. `docs/audit/frontend-source-alignment-snapshot.md` if present
4. relevant screen/domain docs
5. `.github/copilot-instructions.md`
6. `docs/ai-skills/design-md-ui-governor/SKILL.md`
7. `docs/ai-skills/hard-mode-mom-v3/SKILL.md` when touching execution/governance/quality/material truth

Prompt pattern:

```text
Use DESIGN.md as the UI design-system authority.
Do not invent backend truth, permission truth, execution transitions, quality results, ERP posting, backflush, AI deterministic decisions, or Digital Twin accuracy.
Preserve current source patterns where verified.
Label screens as ACTIVE / PARTIAL / MOCK / SHELL / FUTURE / DISABLED.
Implement only the requested UI slice.
```

Required output for UI work:

```markdown
# UI/UX Implementation Report
## Selected Skill
## Source Inputs Read
## Design System Alignment
## Files Changed
## Screens Affected
## Components Added / Updated
## Data Source Status
## MOM Safety Check
## Responsive / Accessibility Check
## Tests / Build Run
## Known Limitations
## Next Recommended FE Slice
```

---

# 10. FleziBCG-Specific UI Contracts

## Backend truth boundary

Frontend owns:

- layout;
- navigation;
- interaction state;
- visualization;
- display formatting.

Backend owns:

- execution truth;
- status truth;
- authorization truth;
- approval truth;
- audit truth;
- quality evaluation truth;
- integration/posting result truth.

## Mock / Future rules

Mock or future screens must be visibly classified in code/docs and must not look production-connected.

Accepted labels:

- `ACTIVE`
- `PARTIAL`
- `MOCK`
- `SHELL`
- `FUTURE`
- `DISABLED`

## Manufacturing Operations naming

Use:

- Brand: `FleziBCG`
- Category: `MOM`
- Full name: `FleziBCG Manufacturing Operations Platform`
- UI phrase: `Manufacturing Operations`

Do not use `MES Lite` in UI.

---

# 11. Review Checklist

Before approving UI output, check:

- Does it follow DESIGN.md?
- Does it preserve source alignment?
- Does it avoid frontend truth leakage?
- Are future screens marked as future/disabled?
- Are loading/error/empty states present where data-driven?
- Are operator actions touch-friendly?
- Are status colors semantic and consistent?
- Are user-facing strings i18n-ready?
- Does the report declare build/test results?

# DESIGN.md — FleziBCG Design System

## Purpose

This file defines the visual and interaction style for FleziBCG.

Use it when creating:

- frontend screens
- reusable components
- dashboard pages
- operator/shopfloor UI
- admin/governance UI
- design mockups
- Figma Make prompts
- React/Tailwind implementation

FleziBCG UI must feel:

- operational
- trustworthy
- calm
- precise
- industrial but modern
- information-dense without being noisy

Do not copy another brand's design system.

---

# 1. Product UI Personality

FleziBCG is a MOM / manufacturing operations platform.

The UI should communicate:

- execution truth
- operational confidence
- governed action
- real-time awareness
- cross-domain visibility
- enterprise readiness

Avoid:

- playful SaaS gimmicks
- consumer-app softness
- over-rounded toy-like cards
- colorful gradients everywhere
- fake futuristic AI visuals
- excessive glassmorphism
- excessive animation
- dashboard clutter

---

# 2. Layout Principles

## Global app shell

Use:

- left sidebar for primary navigation
- top header for tenant/plant/user/session/global status
- main content area for working screens
- optional right panel for contextual details
- stable page header with title, subtitle, primary action, status

## Page structure

Each page should use:

1. Page header
2. Context summary / KPI strip
3. Main work area
4. Detail or side panel if needed
5. Clear empty/loading/error states

## Density

- Admin/supervisory pages: medium density
- Operator/station pages: touch-friendly density

---

# 3. Visual Style

Use:

- neutral app background
- white panels/cards
- subtle borders
- minimal shadows
- high readability
- semantic colors only

Avoid heavy decorative visuals.

---

# 4. Semantic Colors

| Meaning | Usage |
|---|---|
| Primary | main action, selected nav, active command |
| Success | completed, passed, available, healthy |
| Warning | delayed, pending, attention required |
| Danger | blocked, failed, rejected, critical |
| Info | running, informational, advisory |
| Neutral | draft, inactive, disabled, unknown |

Status examples:

- RUNNING → info/blue
- PAUSED → warning/amber
- BLOCKED → danger/red
- COMPLETED → success/green
- PENDING → neutral/gray
- HOLD → warning or danger depending severity

---

# 5. Typography

Use modern sans-serif:

- Inter
- system-ui
- Segoe UI fallback

Operator screens may use larger type:

- status: very large
- primary action: large
- key numbers: readable at distance

---

# 6. Components

## Buttons

- One primary action per work area where possible.
- Danger button only for destructive/blocking actions.
- Operator primary action must be large, high contrast, and touch-friendly.

## Tables

- sticky header for long tables
- clear status badges
- row click opens detail
- filters above table
- empty state explains what to do

## Badges

Badges are semantic:

- status
- phase
- risk
- role
- scope
- source

## Timeline / events

Event timelines show:

- timestamp
- actor
- event type
- entity/context
- payload summary
- source

Do not make event history look like chat.

---

# 7. Shopfloor / Operator UI Rules

Operator UI must show at most:

1. Current operation / station context
2. Current state
3. Key quantities / timer
4. Primary action zone
5. Blocking/warning message if needed

Avoid:

- dense tables
- hidden dropdowns for critical actions
- small click targets
- ambiguous icons
- multiple competing primary buttons

Touch target:

- normal UI: 40–44px
- operator UI: 48–56px+

---

# 8. AI UI Rules

AI is advisory.

AI components must show:

- confidence/uncertainty where relevant
- source context
- clear advisory label
- no hidden mutation

Avoid:

- “AI decided”
- “AI approved”
- “AI completed”

---

# 9. Implementation Rules

When implementing in React/Tailwind:

- use shared components
- centralize semantic status styles
- avoid one-off styling
- keep business logic out of UI
- do not hardcode permission truth
- do not derive execution truth in frontend
- use backend-provided allowed actions where available
- isolate mocks clearly

---

# 10. Do Not Fake Rules

Do not fake:

- backend truth
- authorization
- execution transitions
- quality pass/fail
- ERP posting
- backflush
- AI deterministic decisions
- digital twin accuracy

---

# 12. FleziBCG UI Design System — AI Agent Rules

## Status

Authoritative UI design-system guide for AI-assisted frontend generation.

## Purpose

This section gives AI agents a stable UI/UX reference so generated frontend code remains visually consistent, operationally safe, and aligned with FleziBCG MOM principles.

## Product Feel

FleziBCG UI should feel:

- industrial
- clean
- operational
- trustworthy
- calm under pressure
- data-dense only where useful
- action-oriented for shopfloor users
- overview-oriented for supervisors

## Visual Direction

Use a modern industrial SaaS style:

- light neutral background
- strong hierarchy
- restrained color palette
- clear status chips
- cards for operational groupings
- tables for operational lists
- large state indicators for station/operator screens
- compact but readable supervisory dashboards

## Semantic UI Rules

### Status must be explicit

Do not rely on color alone.

Always pair color with text labels such as:

- `RUNNING`
- `PAUSED`
- `BLOCKED`
- `COMPLETED`
- `QC_HOLD`
- `RELEASED`
- `RETIRED`
- `DRAFT`

### Operational actions must be clear

Primary action should be visually dominant.

Dangerous or governed actions require confirmation.

### Future scope must be labelled

Screens for future phases must show one of:

- `FUTURE`
- `NOT ACTIVE`
- `PLACEHOLDER`
- `REQUIRES BACKEND`

They must not appear production-ready.

## Component Patterns

### Page shell

Every page should include:

- page title
- short context subtitle
- domain/status badge if relevant
- primary action area
- content region
- empty/loading/error state

### Data table

Tables should include:

- search/filter where useful
- status badge
- clear row action
- empty state
- pagination or limit indication if needed

### Operator cockpit

Operator cockpit should include:

- current station/session context
- current operation
- current state
- target vs actual where relevant
- blockers
- one primary next action
- event/history panel if useful

### Supervisor dashboard

Supervisor dashboard should include:

- plant/line/station filters
- current state summary
- exceptions first
- bottlenecks/blockers
- operational list
- timeline/event view where relevant

## Do-not-fake Rules

Frontend must not fake:

- authorization
- allowed actions
- execution state
- station ownership
- quality result
- acceptance decision
- backflush posting
- ERP posting
- AI deterministic decision
- digital twin accuracy

## Stitch / Figma Make Usage

When importing or generating from Google Stitch or Figma Make:

- preserve this `DESIGN.md` as the style authority
- preserve current source alignment from `docs/audit/frontend-source-alignment-snapshot.md`
- generate by domain pack, not the full product at once
- clearly mark connected, mock, shell, future, and disabled screens
- do not redesign the whole app shell without explicit approval

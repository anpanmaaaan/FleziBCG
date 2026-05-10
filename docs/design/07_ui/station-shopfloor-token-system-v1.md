# Station Shopfloor Token System v1

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-10 | v1.0 | Initial shopfloor token system contract. Codifies visual hierarchy, touch targets, typography, state patterns, and action hierarchy for Station Execution UI. Closes R2 gap from STATION-NONSTOP-RECONCILIATION-01. |

---

## Status

Authoritative token system for Station Execution UI (Setup, Queue, Cockpit, Interrupted Mode, Completion).

Not a Tailwind config override. Guidance document for future implementation slices.

---

## Routing

```markdown
## Auto-Route
- Selected brain: MOM Brain (Station Execution UI)
- Selected mode: Product / Architecture / Design token mode
- Hard Mode MOM: v3 ON (constrains execution-adjacent UI visual hierarchy)
- Reason: Token system governs operator visual hierarchy and backend-truth visibility in execution-owned surfaces.
```

---

## Scope

**In scope:**

- Visual hierarchy principles for shopfloor operators.
- Minimum touch target sizes and spacing rules (codifies responsive contract v1).
- Typography hierarchy (sizes and weights).
- State representation (color + icon + text patterns).
- Action hierarchy and operator-first CTA placement.
- KPI display hierarchy.
- Modal/dialog affordances.
- Focus and accessibility patterns.
- Density rules (information block limits).
- Responsive behavior by breakpoint class.
- Usage mapping by mode (Setup, Queue, Cockpit, Interrupted, Completion).

**Out of scope:**

- Tailwind config changes.
- CSS class refactoring.
- Component implementation.
- Backend contract changes.
- New execution behavior.
- Formal design tokens (CSS custom properties).
- Dark mode or theme switching.
- Internationalization (covered by i18n registry).
- Animation timing or curve specifications.

---

## Non-Goals

- Redefine screens or wireframes.
- Change backend truth visibility or ownership.
- Implement new features.
- Support use cases beyond discrete operator execution.
- Create a global design system outside Station.

---

## Source Evidence

### Design docs read

| Doc | Why used |
|---|---|
| docs/design/07_ui/station-execution-ui-contract-v4.md | Mode A/B/C/D definitions, screen ownership, backend truth boundaries |
| docs/design/07_ui/station-workflow-redesign-contract-v1.md | Three-screen operator flow, P0/P1 scope |
| docs/design/07_ui/station-execution-responsive-contract-v1.md | Touch target sizes, breakpoint rules, density limits |
| docs/design/07_ui/station-execution-andon-proposal-v1.md | Andon signal severity (info/warning/danger) and visual treatment |
| docs/design/07_ui/station-execution-screen-pack-v4.md | Screen list and primary data by screen |
| docs/design/02_domain/execution/business-truth-station-execution-v4.md | Session ownership, operator/equipment context, backend truth scope |
| docs/audit/station-nonstop-reconciliation-report.md | Gap analysis: R2 token system missing, responsive button sizing implemented but not formalized |

### Source code patterns observed

| Pattern | Location | Observation |
|---|---|---|
| Primary action button | AllowedActionZone.tsx | `min-h-14 ... bg-green-600 ... active:scale-[0.98]` (56px height, green for start) |
| Secondary action button | AllowedActionZone.tsx | `min-h-14 ... bg-amber-400 / bg-slate-600` (56px height, amber for pause, slate for downtime) |
| Stepper input label | StationExecution.tsx | `text-xl font-bold md:text-2xl lg:text-3xl` (responsive, bold) |
| Stepper value display | StationExecution.tsx | `text-3xl ... md:text-5xl` (large, centered, bold) |
| Quick-add buttons | StationExecution.tsx | `min-h-11 ... text-lg font-bold sm:text-xl md:text-2xl` (44px height, secondary weight) |
| Keypad display | StationExecution.tsx | `text-4xl font-bold` (large, centered) |
| Andon banner | StationAndonBanner.tsx | `rounded-2xl border px-4 py-3` (consistent corner radius and padding) |
| State badge | AllowedActionZone.tsx + StationWorkflowShell.tsx | Amber for pause, green for running, red for blocked, blue for completed |

---

## Shopfloor UX Principles

### 1. **Readable from Distance**
Operators may read displays from 1–3 meters away during operation. All primary actions must be legible at tablet landscape distances (1024px device, ~1.5 meter typical viewing distance).

- Primary action text: minimum 28px display size (text-xl or larger with responsive scaling).
- KPI numbers: 48–72px display size (text-3xl to text-6xl with responsive scaling).
- Status badges: icon + text always paired; never icon-only.

### 2. **Glove- and Tablet-Friendly**
Operators may wear gloves or touch with hands while holding tools. Touch targets must be large and well-spaced.

- Minimum tap target: 48px × 48px.
- Preferred tap target: 56px × 56px.
- Minimum gap between targets: 12px (preferred: 12–16px).
- No hover-only interactions or `title` tooltip dependencies.

### 3. **One Primary Action Per Mode**
Each operator screen mode should highlight exactly one primary next-step action.

- Mode A (Setup): Open/Resume Session → Identify Operator → Bind Equipment → Enter Queue.
- Station Queue: Select Operation → Enter Cockpit.
- Mode B (Active Cockpit): Start → Pause → Resume → Report → Complete.
- Mode C (Interrupted): Resolve Issue → Resume / End Downtime.
- Mode D (Completion): Return to Queue → End Session.

Secondary and supervisor actions remain visible but non-dominant.

### 4. **No Hover-Only Interaction**
Touchscreen-primary displays have no hover state. All affordances must be obvious without hover.

- Button text always visible.
- Icon + text always paired.
- State indicated by color + icon + text, never color alone.
- Disabled state: `disabled:opacity-40` + explanatory text nearby.

### 5. **State Always Uses Color + Icon + Text**
State must never rely on color alone. Operators with color blindness and distant viewing must understand state from icon and text.

- `IN_PROGRESS` → green icon + "Running" text.
- `PAUSED` → amber/yellow icon + "Paused" text.
- `BLOCKED` → red icon + "Blocked" text.
- `DOWNTIME_OPEN` → wrench or alert icon + "Downtime" text.
- `COMPLETED` → checkmark icon + "Completed" text.
- `CLOSED` → lock icon + "Closed" text.

### 6. **Operator-First Information Hierarchy**
Operator screens must lead the eye to the next required action. Supervisor-only actions and read-only context remain visible but secondary.

- Required action (CTA) first.
- Current state and metrics second.
- Contextual metadata third.
- Supervisor support links last.

### 7. **Backend Truth Visibility**
All state, metrics, and action legality remain backend-derived. Frontend must not invent status or hide backend-derived guidance.

- `allowed_actions` list is authoritative for button visibility.
- Session ownership context is backend-provided.
- Downtime reason options come from backend master data.
- No local state machine or fake UI-only transitions.

---

## Visual Hierarchy Model

Station Execution UI uses a four-level visual hierarchy:

### Level 1: State Hero (Dominant)
**Purpose:** Operator immediately understands the current operation identity and status.

**Where:** Top of cockpit or main screen.  
**Size:** 28–36px for operation name; 20–28px for status badge.  
**Weight:** Bold.  
**Color:** Status-driven (green for running, amber for paused, red for blocked).

**Example:**
- Operation name: `text-2xl font-bold md:text-3xl`
- Status badge: green circle icon + "Running" text

### Level 2: Primary Action (Urgent)
**Purpose:** Operator knows the next required step.

**Where:** Central, prominent placement in action zone.  
**Size:** 28–36px text.  
**Weight:** Bold, filled background.  
**Touch target:** 56px height minimum (`min-h-14`).  
**Color:** Operator primary intent (green for start, emerald for resume, amber for pause).  
**Feedback:** `active:scale-[0.98]` for touch confirmation.

**Example:**
```
bg-green-600 text-white text-2xl font-bold min-h-14
rounded-2xl active:scale-[0.98] transition
```

### Level 3: Secondary Metrics (Informational)
**Purpose:** Operator can monitor progress without losing focus from primary action.

**Where:** Visible alongside or below primary action.  
**Size:** 48–72px for KPI numbers; 16–18px for KPI labels.  
**Weight:** Bold for values, regular for labels.  
**Color:** Quantity neutral (gray for label, dark gray for value), or tone-specific (emerald for good, amber for scrap).  
**Touch target:** Display-only; not tap target.

**Example:**
```
KPI value: text-5xl font-bold text-gray-900
KPI label: text-sm font-medium text-gray-600
```

### Level 4: Support Context (Contextual)
**Purpose:** Operator can find additional information if needed (session context, supervisor support, detailed guidance).

**Where:** Collapsed, aside, or below-fold.  
**Size:** 12–14px minimum; prefer 13–16px.  
**Weight:** Regular.  
**Color:** Gray tones (slate-600 for secondary text, slate-400 for placeholder).

**Example:**
```
Operator: {operator_user_id}
Equipment: {equipment_name} [optional]
[Supervisor Support] [Details]
```

---

## Typography Tokens

### Font Stack
- Primary: System sans-serif stack (Tailwind default).
- Monospace (if needed for codes): `font-mono`.

### Size Tokens by Semantic Use

| Use | Target Intent | Tailwind Classes | Notes |
|---|---|---|---|
| State Hero (operation name) | Large, bold | `text-2xl font-bold sm:text-3xl md:text-4xl` | Must be readable from distance |
| Primary action label | Operator primary | `text-xl font-bold sm:text-2xl md:text-3xl` | CTA must be prominent |
| KPI value (remaining/current) | Hero number | `text-4xl font-bold sm:text-5xl md:text-6xl` | Absolute largest; dominates cockpit |
| KPI label (Remaining / Completed / Scrap) | KPI descriptor | `text-sm font-medium sm:text-base` | Pairs with KPI value |
| Secondary action label | Secondary affordance | `text-lg font-bold sm:text-xl md:text-2xl` | Visible but not dominant |
| Guidance text (next steps, warnings) | Informational | `text-base sm:text-lg` | Readable, not diminished |
| Metadata (session, equipment, timestamps) | Support | `text-sm text-gray-600` | Secondary; can be smaller |
| Help text, placeholders | Minimal | `text-xs sm:text-sm` | Smallest allowed; >12px preferred |
| Button text (header controls, modals) | Action affordance | `text-sm sm:text-base md:text-lg` | Minimum 44px tap target; 14px text |
| Stepper label (Good Qty, Scrap Qty) | Input prompt | `text-xl font-bold md:text-2xl lg:text-3xl` | Bold, responsive, prominent |
| Stepper value (current quantity) | Input output | `text-3xl font-bold sm:text-4xl md:text-5xl lg:text-6xl` | Largest secondary number; center-aligned |

### Weight Distribution
- **Bold (700):** Primary action text, KPI values, operation name, stepper labels.
- **Semibold (600):** Secondary action text, section headers, state badges.
- **Regular (400):** Guidance text, metadata, labels.
- **Light (300):** Avoid for operator-facing content; use only for disabled or very secondary text.

---

## Hit Target and Spacing Tokens

### Minimum Touch Targets

| Control Type | Min Height | Min Width | Tailwind | Notes |
|---|---|---|---|---|
| Primary action (Start, Complete, Clock On) | **56px** | Full width | `min-h-14` → `h-14 sm:h-16 md:h-18` | Primary execution buttons |
| Secondary action (Pause, Resume, Start Downtime) | **56px** | Full width or half-width | `min-h-14` → `h-14 sm:h-16 md:h-18` | Execution secondary buttons |
| Report Qty button | **56px** | Full width | `min-h-14` → `h-14 sm:h-16` | Large, deliberate action |
| Quick-add buttons (+1, +5, +10, +20) | **44px** | Auto (content-fit) | `min-h-11` → `h-11 sm:h-12 md:h-14` | Secondary input affordance |
| Stepper ±/reset buttons | **48px × 48px** | Square | `min-h-12 min-w-12` → `h-16 w-16` | Digital input controls |
| Numeric keypad keys | **56px × 56px** | Square | `h-14` | Modal numeric input |
| Header/control buttons (Back, Refresh, Queue, Release) | **44px** | Square or auto | `h-10 sm:h-11` | Secondary, not primary |
| Modal action buttons (OK, Cancel) | **44px** | Auto (content-fit) | `px-4 py-2.5` or `px-6 py-3` | Minimum touch size; padding-based |
| Status badge icon | **24–32px** | Icon size | `w-6 h-6` (24px) or `w-8 h-8` (32px) | Supporting visual, not primary |

### Spacing (Gap)

| Context | Gap | Tailwind | Notes |
|---|---|---|---|
| Between action buttons (primary row) | **12px** | `gap-3` | Minimum safe distance |
| Between action button pairs | **12px** | `gap-3` | Two-column grid: `grid-cols-2 gap-3` |
| Between action zones | **16px** | `gap-4` | Between distinct control groups |
| Header control row | **8–12px** | `gap-2 sm:gap-3` | Compact, secondary controls |
| Stepper group (label + input + quickadd) | **12px** | `gap-3` | Logical grouping |
| Card padding (internal) | **16px** | `p-4` | Inside bordered card |
| Card padding (large) | **20–24px** | `p-5 md:p-6` | Cockpit info cards |
| Section bottom margin | **16px** | `mb-4` | Vertical separation |

### Touch Feedback
- **Active (press):** `active:scale-[0.98]` on all tappable buttons (subtle shrink for confirmation).
- **Hover (desktop):** `hover:bg-{color}-700` (subtle shade change; hidden on touch-only devices).
- **Disabled:** `disabled:opacity-40 disabled:cursor-not-allowed` (faded appearance + cursor change).
- **Focus (keyboard):** `focus:outline-2 focus:outline-offset-2 focus:outline-blue-500` (for accessibility testing; browsers apply default).

---

## State Color / Icon / Text Tokens

All execution states must use **color + icon + text**. Never rely on color or icon alone.

### Execution State Patterns

| State | Color Intent | Icon | Text Label | Tailwind Example | Notes |
|---|---|---|---|---|---|
| `PLANNED` | Gray (neutral) | `clipboard` or `square` | "Planned" | `border-gray-300 bg-gray-50 text-gray-700` | Pre-execution, rarely visible to operator |
| `IN_PROGRESS` / Running | Green (success) | `play` or `activity` | "Running" | `bg-green-600 text-white` | Primary operator view |
| `PAUSED` | Amber (caution) | `pause` or `pause-circle` | "Paused" | `bg-amber-400 text-slate-900` | Waiting for operator action |
| `BLOCKED` | Red (danger) | `alert-triangle` or `stop-circle` | "Blocked" | `border-red-300 bg-red-50 text-red-950` | Issue preventing progress |
| `DOWNTIME_OPEN` | Red/Amber (danger/caution) | `wrench` or `alert` | "Downtime" | `border-red-200 bg-red-50 text-red-950` | Maintenance pause; same danger intent as BLOCKED |
| `COMPLETED` | Blue (success/done) | `check-circle` or `check-double` | "Completed" | `border-blue-300 bg-blue-50 text-blue-950` | Operation done; next step awaits |
| `ABORTED` | Gray (neutral) | `x-circle` | "Aborted" | `border-gray-300 bg-gray-50 text-gray-700` | Rare operator view |
| `CLOSED` | Slate (locked) | `lock` | "Closed" | `border-slate-300 bg-slate-50 text-slate-700` | Supervisor-only state |

### Quality Hold State

| State | Color Intent | Icon | Text | Tailwind | Notes |
|---|---|---|---|---|---|
| `quality_hold_open = true` | Amber (caution) | `alert-triangle` | "Quality Hold" | `border-amber-300 bg-amber-50 text-amber-800` | Blocks progression until resolved |

### Downtime Reason Badge (In-Progress Detail)

| Reason Type | Icon | Color Intent | Tailwind | Notes |
|---|---|---|---|---|
| Equipment maintenance | `wrench` | Slate/gray | `text-slate-600` | Neutral support |
| Quality issue | `alert-triangle` | Amber | `text-amber-600` | Caution-level downtime |
| Material shortage | `package` | Amber | `text-amber-600` | Supply-related pause |
| Operator break | `coffee` | Gray | `text-gray-600` | Personnel-related pause |
| Other | `help-circle` | Gray | `text-gray-600` | Unspecified reason |

---

## Action Hierarchy Tokens

Actions in Station Execution must follow a clear priority order. Operator primary actions dominate; supervisor actions are separated and secondary.

### Action Type Definitions

| Action Type | Weight | Placement | Tailwind Pattern | When Visible | Notes |
|---|---|---|---|---|---|
| **Primary operator action** (Start, Pause, Resume, Complete) | Highest | Central, top of zone | `bg-{color}-600 text-white min-h-14 text-2xl font-bold` | Always (when allowed) | Largest, filled, highest contrast |
| **Secondary operator action** (Report production, Start downtime) | High | Adjacent to primary | `bg-{color}-400 / bg-slate-600 text-white min-h-14` | Always (when allowed) | Similar size, different color |
| **Completion/progression action** (End session, Return to queue) | Medium | After completion | `bg-emerald-600 text-white` | In completion mode | Major affordance, tied to flow |
| **Interruption/escalation action** (Resolve, Request supervisor) | Medium | In interrupted mode | `border-2 border-red-500 bg-white text-red-700` | When blocked | Outlined style; not filled |
| **Destructive/supervisor action** (Close operation, Reopen) | Low-to-medium | Separate from operator lane | `bg-slate-600 text-white` or outlined | Supervisor context only | Never primary operator CTA; always confirmed |
| **Negative action** (Cancel, Dismiss) | Low | Modal/dialog footer | `border border-gray-300 bg-white text-gray-700` | In modal context | Light outline; non-destructive |

### Action Zone Layout by Status

#### Status: PLANNED
```
[Primary: Clock On / Start]
```
(Full-width, green, dominant)

#### Status: IN_PROGRESS
```
[Pause] [Start Downtime]
       or
[Primary column]  [Secondary column]
```
(Two-column grid when space allows; stack on narrow)

#### Status: IN_PROGRESS (with completion allowed)
```
[Pause] [Start Downtime]
[Complete (outline)]
```
(Completion as outline below pause/downtime pair)

#### Status: PAUSED (no downtime)
```
[Resume] [Start Downtime]
```
(Resume is green/primary; Start Downtime is slate/secondary)

#### Status: PAUSED (downtime open)
```
[End Downtime]
```
(Single primary action; resume blocked until downtime closed)

#### Status: BLOCKED / DOWNTIME_OPEN
```
[Primary: End Downtime]
(+ Andon banner above with blocker reason)
```
(Interruption affordance; reporting disabled)

#### Status: COMPLETED
```
(No execution actions; show completion summary + routes)
[Return to Queue] [End Session / Handoff]
```
(Progression-only; no execution state change)

#### Status: CLOSED
```
(All execution actions disabled with "CLOSED" explanation)
[Reopen] (supervisor-only, if authorized)
```
(Terminal state; reopen deferred to supervisor context)

---

## KPI Display Tokens

KPI (Key Performance Indicator) display hierarchy must allow operators to monitor progress at a glance.

### KPI Hierarchy by Status

#### Status: IN_PROGRESS (Primary Focus)
```
[Remaining]    ← Largest, most prominent
[Good] [Scrap] ← Supporting totals, secondary size
[Timer]        ← Tertiary; supports downtime tracking
```

**Remaining (Good) - Size:** `text-5xl sm:text-6xl font-bold`  
**Label:** `text-sm sm:text-base text-gray-600`  
**Color:** Dark gray, neutral (not colored by state).

**Good / Scrap - Size:** `text-3xl sm:text-4xl font-bold`  
**Label:** `text-xs sm:text-sm text-gray-600`  
**Color:** Emerald for good, amber for scrap (supportive context).

**Timer (if applicable) - Size:** `text-2xl sm:text-3xl font-bold`  
**Color:** Gray (neutral progress indicator).

#### Status: PAUSED or BLOCKED
```
[Remaining]     ← Still visible; no change
[Andon message] ← Banner replaces normal guidance
[Downtime reason / duration] ← If open downtime
```

**Same KPI display; guidance changes to interrupt recovery.**

#### Status: COMPLETED
```
[Final Summary]
[Good Produced] [Scrap] [Downtime Duration]
[Next Options]
```

**Summary cards, not live progress; supporting context only.**

---

## Modal / Dialog Tokens

Modals and dialogs in Station Execution must maintain touch-friendly and accessible design.

### Modal Template

```
[Modal title (bold, prominent)]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Form content / input area]
[Guidance text]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Primary Action] [Cancel/Dismiss]
```

### Modal Title
- **Size:** `text-xl sm:text-2xl font-bold`
- **Color:** Gray-900 (dark, readable)
- **Placement:** Top-left, inside modal; no separate header bar

### Modal Buttons
- **Primary action (OK, Confirm, Submit):**
  - Tailwind: `bg-blue-600 text-white min-h-11 px-6 font-bold`
  - Semantic: "Start Downtime", "Confirm Reopen", "OK"
- **Secondary action (Cancel, Dismiss):**
  - Tailwind: `border border-gray-300 bg-white text-gray-700 min-h-11 px-6`
  - Semantic: "Cancel"
- **Destructive action (if any):**
  - Tailwind: `border-2 border-red-500 bg-white text-red-700 min-h-11 px-6 font-bold`
  - Always paired with confirmation text: "This cannot be undone."

### Focus Management
- Focus starts on primary action (not cancel) unless confirmation text requires reading first.
- `Escape` key dismisses modal (standard).
- Focus returns to trigger button after modal closes.
- No focus trap; all interactive elements are reachable via Tab.

### Accessibility
- Modal has `role="dialog"` or `role="alertdialog"` (if critical warning).
- Modal title is `aria-labelledby`.
- Avoid nested modals.

---

## Focus and Accessibility Tokens

### Focus Visible (Keyboard Navigation)
All interactive elements must show focus state for keyboard users:

```
focus:outline-2 focus:outline-offset-2 focus:outline-blue-500
```

- **Outline width:** 2px
- **Offset:** 2px (gap between element and outline)
- **Color:** Blue (high contrast, distinct from element)

### Semantic Labeling
- All buttons have `aria-label` if text is not explicit.
- All form inputs have `<label>` paired with `htmlFor`.
- Status badges use `role="status"` for live updates (Andon/interruption banners).

### Color Contrast
- Text on background: WCAG AA minimum (4.5:1 for normal text, 3:1 for large text ≥18px).
- Current tokens meet this (green-600 on white, amber-400 on dark, red-950 on red-50, etc.).

### Motion Preferences
- `active:scale-[0.98]` and `transition` are safe for `prefers-reduced-motion: reduce`.
- Avoid animation on page load or automatic transitions.
- Use `motion-safe:` and `motion-reduce:` classes if implementing motion in future.

---

## Density Rules

Station Execution screens must remain operator-focused and not become information dashboards.

### Maximum Information Blocks per Screen State

| Mode | Max Blocks | Block Types | Notes |
|---|---|---|---|
| A (Setup) | 1–2 | Session card, operator card | Minimal; one step at a time |
| Station Queue | 3 | Queue summary, filter bar, operation list | List is scrollable; summary fixed |
| B (Cockpit Active) | 4 | State hero, KPIs, guidance, action zone | Vertical stacking; no sidebars in P0 |
| C (Interrupted) | 3 | Andon banner, KPIs, action zone | Reporting block collapses; focus on recovery |
| D (Completion) | 3 | Summary, metrics, next-step routes | Progression-focused; clean closure |
| E (Supervisor) | 4–5 | Header, detail, history, close/reopen, audit | Separate surface; not operator primary |

### Visibility Rules
- **Setup:** No full queue visible; no full cockpit visible.
- **Queue:** No full setup checklist; no full cockpit; compact next-work preview (future P1).
- **Cockpit:** No full queue visible; no full setup; back-to-queue affordance only.
- **Interrupted:** Reporting section collapses if reporting is unavailable; guidance dominates.
- **Completion:** Summary replaces execution controls; progression is next step.

### Sidebar / Support Content
- Secondary panels (supervisor support, audit history, equipment context) collapse into cards or modals.
- Do not consume primary screen real estate.
- Remain accessible via explicit "Details" or "Support" links.

---

## Responsive / Tablet Rules

Station Execution is tablet-first. Responsive behavior is defined by breakpoint class, not screen size.

### Breakpoint Classes

| Class | Min Width | Device | Primary Layout |
|---|---|---|---|
| `base` | 320px | Small (emergency) | Single-column stack; minimal layout |
| `sm:` | 640px | Narrow tablet | Two-column grid where layout allows |
| `md:` | 768px | Tablet portrait | Paired layout; grid wraps smartly |
| `lg:` | 1024px | Tablet landscape / Desktop | Side-by-side where content supports |
| `xl:` | 1280px+ | Desktop | Full multi-column layout |

### Typography Responsive Scaling

All text that communicates state or action must scale with breakpoint:

```
text-base sm:text-lg md:text-xl lg:text-2xl
```

**Stepper value** scales more aggressively:
```
text-3xl sm:text-4xl md:text-5xl lg:text-6xl
```

### Button Layout Responsive Scaling

**Two-button rows** (Pause + Start Downtime):
```
grid grid-cols-1 gap-3 sm:grid-cols-2
```
(Stack on small screens; pair on tablet+)

**Action zone buttons:**
```
w-full (always full-width)
min-h-14 sm:min-h-16 md:min-h-18 (height scales)
text-xl sm:text-2xl md:text-3xl (text scales)
```

### Stepper Layout

**On tablet portrait (768px+):**
```
grid gap-5 lg:grid-cols-2
(Good Qty stepper) (Scrap Qty stepper)
```

**On smaller (<768px):**
```
flex flex-col gap-5
(Good Qty stepper)
(Scrap Qty stepper) — stacked
```

### Queue Layout

**On tablet landscape (1024px+):**
```
Queue list: max-w-2xl centered
Queue summary: grid-cols-5 (five-stat grid)
```

**On tablet portrait (768px):**
```
Queue list: full-width
Queue summary: grid-cols-2 md:grid-cols-3
```

---

## Usage by Mode

### Mode A — Station Entry & Setup

**Primary information:** Station context, session state, operator readiness, equipment binding.  
**Hierarchy:** Setup checklist → required missing item → CTA to enter Queue.

| Component | Visual Token | Notes |
|---|---|---|
| Station context card | `bg-white border border-gray-200 rounded-2xl p-5` | Context display; no action yet |
| Session state badge | `bg-{state-color} text-white px-3 py-1 rounded-full` | Shows OPEN / CLOSED / missing |
| Primary CTA (Open Session / Identify Operator / Bind Equipment) | `bg-green-600 text-white min-h-14 text-xl font-bold` | Action-oriented; full-width |
| Primary CTA (Enter Queue) | `bg-emerald-600 text-white min-h-14 text-xl font-bold` | Progression; full-width |
| Guidance text | `text-base text-gray-700` | Explains what's needed |
| Error / warning | `border-l-4 border-red-500 bg-red-50 px-4 py-3 text-red-800` | Inline guidance; not modal |

### Station Queue — Work Selection Bridge

**Primary information:** Queue metrics, available operations, selection affordance.  
**Hierarchy:** Queue summary → operation cards → selection → route to cockpit.

| Component | Visual Token | Notes |
|---|---|---|
| Queue summary row (5-stat grid) | `grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3` | Metrics: Total, In Progress, Pending, Completed, Blocked |
| Stat card | `bg-white border border-gray-200 rounded-2xl p-4 text-center` | Number-focused; value prominent |
| Stat number | `text-3xl sm:text-4xl font-bold text-gray-900` | Large, readable |
| Stat label | `text-xs sm:text-sm text-gray-600 mt-1` | Supporting descriptor |
| Filter bar | `flex gap-2 overflow-x-auto pb-2` | Horizontally scrollable; pills |
| Operation card (list) | `bg-white border border-gray-200 rounded-2xl p-4 flex items-center gap-3` | Operation name (left), status (right) |
| Operation name | `text-lg font-semibold text-gray-900 flex-1 truncate` | Truncates on narrow; readable on 768px+ |
| Status badge (inline) | `badge: text-sm font-bold px-3 py-1 rounded-full` | Color + text; icon optional on narrow |
| Selection affordance | Implicit on tap / click | Row tap routes to cockpit; no separate button |

### Mode B — Active Execution Cockpit

**Primary information:** Operation identity, runtime status, KPI progress, allowed actions, guidance.  
**Hierarchy:** State hero → KPIs → primary action → secondary actions → metadata.

| Component | Visual Token | Notes |
|---|---|---|
| **State Hero Block** |  |  |
| Operation name | `text-2xl font-bold md:text-3xl lg:text-4xl text-gray-900` | Large, left-aligned; truncate if needed |
| Status badge + icon | `badge: bg-{status-color} text-white px-4 py-2 rounded-full` | Green/amber/red/blue based on state |
| **KPI Block** |  |  |
| Remaining quantity | `text-5xl sm:text-6xl font-bold text-gray-900 text-center` | Largest; dominates cockpit view |
| Remaining label | `text-base text-gray-600 mt-2 text-center` | "Remaining" |
| Good / Scrap totals | `grid grid-cols-2 gap-4 text-center` | Two-column; supporting metrics |
| Good value | `text-3xl sm:text-4xl font-bold text-emerald-700` | Green tone; success color |
| Scrap value | `text-3xl sm:text-4xl font-bold text-amber-700` | Amber tone; caution color |
| **Guidance Block** |  |  |
| Guidance message | `text-base sm:text-lg text-gray-700 p-4 bg-blue-50 rounded-xl` | Prompt for next step or explanation |
| **Action Zone Block** |  |  |
| Primary action button (Start/Pause/Resume/Complete) | `bg-{action-color} text-white min-h-14 text-xl font-bold w-full rounded-2xl active:scale-[0.98]` | Full-width; largest size |
| Secondary buttons (Pause + Downtime, Pause + Resume) | `grid grid-cols-2 gap-3 sm:grid-cols-2` | Paired; equal height and width |
| **Metadata Block** |  |  |
| Operator context | `text-sm text-gray-600` | "Operator: {name}" (optional) |
| Equipment context | `text-sm text-gray-600` | "Equipment: {name}" (optional) |
| Session ID | `text-xs text-gray-400` | Minimal; support only |

### Mode C — Interrupted / Andon Active

**Primary information:** Blocker reason, duration, recovery action, KPIs (read-only).  
**Hierarchy:** Andon banner → KPIs (static) → recovery action → guidance.

| Component | Visual Token | Notes |
|---|---|---|
| **Andon Banner Block** |  |  |
| Severity indicator | `border-l-4 border-{severity-color} bg-{severity-bg} text-{severity-text} px-4 py-3 rounded-xl` | Red for blocked, amber for paused |
| Banner title | `text-sm font-bold uppercase tracking-wide` | "Guidance / Blockers" or "Issue" |
| Banner message | `text-base mt-2` | Explains reason; guides recovery |
| **KPI Block** |  |  |
| Remaining quantity | `text-4xl sm:text-5xl font-bold text-gray-900 text-center` | Same as active; read-only (no input) |
| Downtime duration (if open) | `text-3xl sm:text-4xl font-bold text-gray-900` | Shows elapsed downtime time |
| **Action Zone Block** |  |  |
| Primary recovery action | `bg-emerald-600 text-white min-h-14 text-xl font-bold` | "Resume" or "End Downtime" based on state |
| Escalation hint | `text-sm text-gray-600 mt-2` | "Requires supervisor? [Support]" (link-only) |
| **Reporting Block (Collapsed)** |  |  |
| Collapsed info card | `bg-white border border-gray-200 rounded-xl p-4 text-gray-600` | Shows "Reporting unavailable during interruption" |
| (Steppers hidden / disabled) | —— | Reporting controls are not visible; no confusion |

### Mode D — Completion & Handover

**Primary information:** Completion summary, metrics, next-step routes.  
**Hierarchy:** Completion summary → final good/scrap → progression routes.

| Component | Visual Token | Notes |
|---|---|---|
| **Completion Summary** |  |  |
| Operation name | `text-2xl font-bold text-gray-900` | Same as active |
| "Completed" badge | `badge: bg-blue-600 text-white px-4 py-2 rounded-full` | Blue (done) |
| **Summary Metrics** |  |  |
| Good produced | `text-4xl font-bold text-emerald-700 text-center` | Final count |
| Scrap produced | `text-3xl font-bold text-amber-700 text-center` | Supporting count |
| Downtime (if any) | `text-3xl font-bold text-gray-700 text-center` | Duration of any interruptions |
| **Next-Step Routes** |  |  |
| "Return to Queue" button | `bg-emerald-600 text-white min-h-14 text-lg font-bold w-full` | Primary progression |
| "End Session" button (guidance) | `border border-gray-300 bg-white text-gray-700 min-h-12 text-base` | Secondary; end-session management |
| Supervisor review link | `text-sm text-blue-600 underline` | If supervisor context active |

---

## Implementation Mapping

This token system guides future implementation slices. Each slice should reference the relevant token sections.

| Future Slice ID | Purpose | Token Sections to Use |
|---|---|---|
| `FE-SE-SETUP-SCREENS-06` | Extract Setup panels (OpenSessionPanel, IdentifyOperatorPanel, BindEquipmentPanel, CloseSessionPanel) | Mode A + Hit Target + Typography + Action Hierarchy |
| `FE-STATION-THREE-SCREEN-QUEUE-01` | Simplify Queue as work selection screen | Station Queue + Responsive / Tablet Rules + Density Rules |
| `FE-SE-COCKPIT-REWORK-07-RECOVERY` | Polish cockpit layout, action hierarchy, KPI placement | Mode B + KPI Display + Action Hierarchy |
| `FE-SE-INTERRUPTED-MODE-08-POLISH` | Enhance interrupted mode UX, Andon prominence | Mode C + State Color / Icon / Text + Andon Banner |
| `FE-SE-COMPLETION-HANDOVER-POLISH` | Finalize completion summary and next-step routes | Mode D + Typography + Progression CTAs |
| `FE-SE-MODAL-AFFORDANCE-HARDENING-09` | Standardize modal focus, button layout, accessibility | Modal / Dialog Tokens + Focus and Accessibility |
| `FE-STATION-RESPONSIVE-REFINEMENT-10` | Audit responsive behavior at all breakpoints | Responsive / Tablet Rules + Density Rules |
| All future slices | Baseline for all Station UI work | Shopfloor UX Principles + Visual Hierarchy + Typography |

---

## P0 / P1 / Future Boundary

### P0 (Approved, Implemented or In-Flight)
- Three-screen operator flow (Setup, Queue, Cockpit).
- Touch targets and spacing (56px primary, 48px secondary, 12px gaps).
- State color + icon + text patterns.
- Typography hierarchy (responsive scaling).
- Primary action hierarchy (one per mode).
- Responsive breakpoint behavior (base → sm → md → lg).
- Backend-derived allowed actions.
- Andon visual-only signals (no new events).
- Density limits (4 blocks max per cockpit).

### P1 (Deferred; Future Slices)
- Formal Tailwind design token variables (`@apply` refactoring).
- Operator scan / QR input (Setup mode enhancement).
- Equipment eligibility constraints (Setup mode enhancement).
- Operator qualification / training checks (Setup mode enhancement).
- Separate Andon event family (backend domain work).
- Push notifications to supervisor consoles.
- Audible or hardware Andon integration (stack lights, buzzers).
- Handoff / shift-change workflows.
- Cross-station Andon aggregation dashboard.
- Dark mode or theme switching.

### Future (Post-Production)
- Advanced analytics dashboard (separate surface from operator).
- AI-driven decision support (advisory only; no auto-transitions).
- Multilingual typography support (beyond i18n keys).
- Animation system (motion profiles for transitions).
- Gesture-based controls (swipe, long-press).

---

## Open Questions

1. **Keypad location:** Should numeric keypad open as overlay (current) or inline in stepper UI? Current overlay prevents accidental taps and is suited to production kiosk use; inline would save two taps but consume space on narrow displays.

2. **Next-work preview in Cockpit:** Station Queue contract defers "compact next-work preview in cockpit" to P1. Should future refined cockpit include a persistent "up-next" card, or remain pure single-operation focus?

3. **Downtime reason as dropdown vs. list:** Current StartDowntimeDialog uses a native `<select>` for downtime reason. Should future slices upgrade to a button list (larger touch targets) or keep the select?

4. **Supervisor action placement:** Supervisor close/reopen are currently on a separate surface (StationSession or dedicated Supervisor Review page). Should they ever appear as secondary buttons in the cockpit, or remain strictly out-of-operator-band?

5. **Language-specific typography:** Japanese and RTL languages may require different size guidance. Should future i18n work define language-specific typography rules, or use current responsive scaling?

---

## Definition of Done

Token system v1 is DONE when:

1. ✅ Shopfloor UX principles are documented and justified.
2. ✅ Minimum hit target sizes and spacing rules are codified.
3. ✅ Typography hierarchy is defined by semantic use and breakpoint.
4. ✅ State representation rules (color + icon + text) are exhaustive.
5. ✅ Action hierarchy patterns are clear for each mode.
6. ✅ KPI display hierarchy prioritizes "remaining" as primary during execution.
7. ✅ Modal and dialog affordances are standardized.
8. ✅ Focus and accessibility patterns are defined.
9. ✅ Density rules limit information overload.
10. ✅ Responsive behavior is mapped to breakpoint classes.
11. ✅ Mode-specific usage examples are provided for each screen.
12. ✅ Implementation mapping guides future slices.
13. ✅ P0/P1/Future boundaries are explicit.
14. ✅ No conflicting guidance from UI contract v4 or responsive contract v1.
15. ✅ Document is in `docs/design/07_ui/station-shopfloor-token-system-v1.md`.

---

## Related Documents

- `docs/design/07_ui/station-execution-ui-contract-v4.md` — Mode A/B/C/D definitions
- `docs/design/07_ui/station-workflow-redesign-contract-v1.md` — Three-screen flow
- `docs/design/07_ui/station-execution-responsive-contract-v1.md` — Breakpoint rules
- `docs/design/07_ui/station-execution-andon-proposal-v1.md` — Andon signal hierarchy
- `docs/design/07_ui/station-execution-screen-pack-v4.md` — Screen inventory
- `docs/audit/station-nonstop-reconciliation-report.md` — Gap analysis that identified R2
- `frontend/src/app/pages/StationExecution.tsx` — Current implementation patterns
- `frontend/src/app/components/station-execution/*.tsx` — Component visual patterns

---

**Document Status:** Authoritative for Station Execution UI.  
**Date Created:** 2026-05-10  
**Slice ID:** `DOC-SE-SHOPFLOOR-TOKENS-07`  
**Approval:** PO review pending.

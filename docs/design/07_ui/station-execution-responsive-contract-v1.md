# Station Execution Responsive Contract v1

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Created Station Execution responsive and shopfloor UX contract. |

---

## 1. Device Targets

Station Execution must be usable on the following device classes:

| Class | Description | Min width | Typical use |
|---|---|---|---|
| Desktop workstation | Supervisor / operator support; wide monitor | 1280px+ | Office, production support, supervisor |
| Tablet landscape | Production kiosk or handheld tablet (iPad landscape) | 1024px | Operator shopfloor primary |
| Tablet portrait | Handheld tablet, wall-mounted panel | 768px | Operator shopfloor fallback |
| Constrained width | Smaller mounted display | 640px | Fixed kiosk panel |
| Small screen | Narrow mobile (emergency access) | 375px | Degraded / supervisor lookup |

**Primary target:** Tablet landscape (1024px) and tablet portrait (768px).  
**Secondary target:** Desktop (1280px+).  
**Degraded but functional:** Constrained width (640px) and small screen (375px).

---

## 2. Layout Rules by Breakpoint

### 2.1 Mode A — Station Session Entry (Future Placeholder)

| Breakpoint | Layout |
|---|---|
| ≥768px (tablet+) | Centered card, max-width 480px, vertically centered in viewport |
| <768px | Full-width card, padded, no centering |

Placeholder content: single-card layout with session-not-available banner. No complex layout needed.

### 2.2 Mode B — Station Queue

| Breakpoint | Layout |
|---|---|
| ≥1024px (desktop/tablet landscape) | Queue list max-width 720px centered; queue summary in 5-column grid |
| 768–1023px (tablet portrait) | Queue list full-width; queue summary in 2×3 grid (2 columns, wraps) |
| <768px | Queue list full-width; queue summary stacked 2-column |

**Queue summary stat cards:**
- ≥1024px: `grid-cols-5`
- 768–1023px: `grid-cols-2 md:grid-cols-3`
- <640px: `grid-cols-2`

**Queue filter bar:**
- Scroll horizontally if needed; do not truncate filter labels
- Active filter chip highlighted; no wrapping required (scrollable)

**Queue operation card:**
- Full width at all breakpoints
- Operation name: `truncate` on narrowest; readable at 768px+
- Status badge: always visible alongside name

### 2.3 Mode C — Execution Cockpit

#### Header / Controls row

| Breakpoint | Layout |
|---|---|
| ≥1024px | Single row: context info left, controls right (`lg:flex-row lg:justify-between`) |
| <1024px | Two stacked rows: context info row above, controls row below |

Controls row wraps with `flex-wrap gap-2 sm:gap-3`. No horizontal overflow.

#### Cockpit body (4 blocks)

| Breakpoint | Block order | Layout notes |
|---|---|---|
| ≥1280px (desktop) | 1 → 2 → 3 → 4 | Block 3 KPIs in 4-column grid; Block 4 side-by-side steppers |
| 1024–1279px (tablet landscape) | 1 → 2 → 3 → 4 | Block 3 KPIs in 4-column grid or 3+timer; Block 4 side-by-side steppers |
| 768–1023px (tablet portrait) | 1 → 2 → 3 → 4 | Block 3 KPIs in 2+2 or 3+timer grid; Block 4 steppers stacked vertically |
| 640–767px (constrained) | 1 → 2 → 3 → 4 | Block 3 KPIs 2-column; Block 4 steppers stacked; action buttons full-width |
| <640px (small) | 1 → 2 → 3 → 4 | All blocks full-width stacked; KPIs 2-column; action buttons full-width stacked |

**Block 1 (State Hero) rules:**
- Operation name: large (`font-bold text-base sm:text-lg md:text-xl lg:text-2xl`)
- Status badge: always visible, text + color
- Downtime banner: full-width red/amber block — never shrinks to a badge
- CLOSED badge: prominent, not dismissible

**Block 2 (Guidance) rules:**
- Positioned near top of scrollable body — should be visible above fold on tablet landscape
- Do not push below action zone

**Block 3 (KPIs + Timer) rules:**
- Remaining quantity card: always highlighted, `highlight=true`
- Numbers: `text-3xl sm:text-4xl md:text-5xl lg:text-6xl`
- Timer: never smaller than `text-2xl`

**Block 4 (Action Zone) rules:**
- Action buttons: full width at all breakpoints
- Two-button rows (Pause + Start Downtime): `grid-cols-2 gap-3` at all breakpoints
- Single-button rows: full width
- Report Qty button: full width, large
- Steppers: side-by-side at ≥768px; stacked at <768px

### 2.4 Mode D — Operation Detail (Partial Placeholder)

| Breakpoint | Layout |
|---|---|
| All | Single column; operation header card then placeholder notice |

---

## 3. Touch Target Rules

### 3.1 Minimum sizes

| Control category | Minimum height | Notes |
|---|---|---|
| Primary execution action (Clock On, End Downtime, Complete) | **56px** | `min-h-14` at base, `sm:min-h-16` (`64px`) on larger screens |
| Secondary execution action (Pause, Resume, Start Downtime) | **48px** | `min-h-12` at base |
| Report Qty button | **56px** | Same as primary |
| Stepper ± buttons | **48×48px** | `min-h-12 min-w-12` |
| Stepper quick-add buttons | **44px height** | `min-h-11` |
| Keypad keys | **56px height** | `h-14` (current: already `h-14`) |
| Header/control buttons (Back, Refresh, Queue, Release) | **44px** | `h-10 sm:h-11` (current: already met after FE-UI-03B) |
| Modal action buttons (Cancel, Submit) | **44px** | `px-4 py-2` minimum |

### 3.2 Touch spacing
- Minimum gap between adjacent tappable targets: `gap-3` (12px)
- Primary action zone: `gap-3 sm:gap-4`
- Header control row: `gap-2 sm:gap-3`

### 3.3 Touch feedback
- Primary actions: `active:scale-[0.98] transition`
- Header controls: `active:scale-95 transition`
- No critical control relies solely on `hover:` state for affordance

### 3.4 Disabled state clarity
- Disabled buttons: `disabled:opacity-40 disabled:cursor-not-allowed`
- Disabled inputs (steppers): `disabled:text-gray-400 disabled:border-gray-200`
- Do not hide disabled primary actions when the reason is meaningful (e.g., closed record)
- Guidance message must explain why primary action is unavailable

---

## 4. Density Rules

### 4.1 Maximum information blocks per screen state
- Maximum 4 information blocks visible at any time in Mode C
- Secondary panels (closure audit, reopen history) collapse inside their section card
- Do not show all closure audit fields as top-level content

### 4.2 Typography scale
| Element | Base | sm: | md: | lg: |
|---|---|---|---|---|
| Operation name (cockpit) | `text-base` | `text-lg` | `text-xl` | `text-2xl` |
| KPI numbers | `text-3xl` | `text-4xl` | `text-5xl` | `text-6xl` |
| Timer values | `text-2xl` | `text-3xl` | `text-4xl` | — |
| Action button labels | `text-xl` | `text-2xl` | `text-3xl` | — |
| Guidance message body | `text-sm` | `text-base` | `text-xl` | — |
| Section headers | `text-xs uppercase` | — | `text-sm uppercase` | — |
| Secondary context (WO/PO) | `text-sm` | `text-base` | `text-xl` | — |

### 4.3 Card spacing
- Cockpit body section cards: `p-4 sm:p-5 md:p-6`
- Card corner radius: `rounded-[28px]` for primary cockpit cards; `rounded-2xl` for inner cards
- Section card gap: `gap-3 sm:gap-4`

---

## 5. Queue Behavior

### 5.1 Queue panel location
- Mode B: full-screen queue list
- Mode C: queue accessible via overlay (`setQueueOverlayOpen`) — appears as a slide-in panel or dropdown anchored near the Queue button

### 5.2 Queue overlay
- Width: `sm:w-80` on tablets+; full-width `left-2 right-2` on small screens
- Max height: `max-h-[70vh]` with scroll
- Close via backdrop tap, X button, or selecting an operation

### 5.3 Queue operation card
- Full width, stacked layout
- Name truncates; operation number and status badge always visible
- Active operation: blue border (`border-blue-500 bg-blue-50`)
- Locked (claim=other): gray, opacity-60, `cursor-not-allowed`
- Downtime tag: red pill
- Blocked tag: red border/bg on card

### 5.4 Queue summary stats bar
- Visible at top of queue list
- Stat labels must fit at 375px width (use abbreviated keys if needed at XS)

---

## 6. Cockpit Behavior

### 6.1 Scroll behavior
- Cockpit body: `overflow-y-auto overflow-x-hidden overscroll-contain`
- Header: `shrink-0` — always visible, does not scroll
- Compatibility warning banner: `shrink-0` — always visible, does not scroll
- Primary action zone: within the scrollable body (operator may need to scroll to reach on very small screens — acceptable tradeoff vs keeping header fixed)

### 6.2 KPI priority
- Remaining quantity is always the visually dominant KPI (highlighted card)
- On very small screens where all 4 KPI cards cannot fit in one row, Remaining qty appears first

### 6.3 Action zone priority
- On tablet portrait (768px), action zone must be visible without scrolling past Block 3
- If Block 3 pushes action zone below fold, consider collapsing timer detail to secondary

### 6.4 Downtime state override
- When downtime_open: action zone collapses to single END DOWNTIME button
- Block 3 remains visible (KPIs are still relevant during downtime)
- Quantity input section is hidden during downtime

### 6.5 Closed state override
- When closure_status=CLOSED: runtime action zone collapses
- Only closure/reopen section remains visible
- KPIs remain visible (read-only for audit)

---

## 7. Dialog / Modal Behavior

### 7.1 Start Downtime Dialog
- Modal overlay: `fixed inset-0 bg-black/40 flex items-center justify-center z-50`
- Modal card: `w-96 max-w-[95vw]` — fits tablet portrait
- Reason dropdown: full-width, min 44px height
- Note input: min 3 visible rows
- Submit button: min 44px height; disabled until valid

### 7.2 Reopen Operation Modal
- Same overlay pattern
- Textarea: min 5 rows (`min-h-28`)
- Submit button: disabled until non-empty reason

### 7.3 Numeric Keypad
- Overlay: `fixed inset-0 bg-black/50 z-50`
- Keypad card: `w-72 max-w-[90vw]`
- Keys: `h-14` minimum
- Number display: large, readable (`text-4xl font-bold`)

### 7.4 Queue Overlay
- Not a full-screen modal — panel/popover attached near Queue button
- Backdrop: `bg-black/30` with click-to-dismiss
- Panel does not cover entire screen on tablet landscape (partial overlay)

---

## 8. Sticky / Fixed Areas

| Area | Behavior | Reason |
|---|---|---|
| Mode B header (queue page header with station scope + refresh) | Sticky within `PageHeader` component | Operator always knows which station they are viewing |
| Mode C controls header | `shrink-0` in flex column — stays at top | Operator always has access to Back / Refresh |
| Mode C compatibility warning banner | `shrink-0` below header | Always visible; cannot be scrolled away |
| Cockpit body | Scrollable | Allows access to all sections on small screens |

**Rule:** Primary action buttons are inside the scrollable body. This is intentional — on small screens, operators scroll once to reach them. The header always allows Back/Refresh/Queue access without scrolling.

---

## 9. Failure States

### 9.1 Queue load failure
- Replace queue list with: error card + Retry button
- Retry button: `h-11` minimum, full-width

### 9.2 Operation load failure
- In cockpit: replace cockpit body with error card + Retry + Back to Queue buttons
- Do not show stale previous operation data as current

### 9.3 Downtime reasons load failure
- Inside Start Downtime dialog: show inline error under dropdown + Retry link
- Submit button disabled

### 9.4 Command rejection
- Toast notification with rejection message
- Toast must be readable at 3m distance: minimum `text-sm font-semibold`
- Do not auto-dismiss critical rejections (e.g., SESSION_REQUIRED) before 6 seconds

### 9.5 Network offline / timeout
- Show generic error toast
- Do not leave action buttons in a loading spinner indefinitely
- Reset loading state after timeout/error

---

## 10. Acceptance Criteria

The responsive implementation is accepted when:

1. All primary execution buttons meet minimum 56px height on tablet and desktop.
2. All secondary buttons meet minimum 48px height on tablet and desktop.
3. All header/control buttons are at least 44px (`h-10 sm:h-11`).
4. Cockpit body does not overflow horizontally at any target breakpoint.
5. Queue summary stats render without overflow at 375px width.
6. Mode C header wraps cleanly without horizontal overflow at 768px.
7. KPI numbers remain readable (≥`text-3xl`) at all breakpoints.
8. Downtime banner is full-width and clearly visible — not collapsed to a badge.
9. CLOSED state visual override is readable at 3m distance.
10. Modals are usable at 375px width (`max-w-[95vw]`).
11. No action button relies solely on `hover:` for affordance.
12. Disabled states are visually unambiguous at all breakpoints.

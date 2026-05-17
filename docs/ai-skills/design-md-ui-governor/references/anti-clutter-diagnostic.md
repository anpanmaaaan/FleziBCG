# Anti-Clutter Diagnostic — FleziBCG

> Run this before merging any operator/supervisor screen. The diagnostic exists
> because user feedback (2026-05-01, Station Session Mode A) flagged "rối" —
> too many competing surfaces. This file converts that feedback into a
> repeatable test.

## 0. How to Use

1. Take a screenshot of the screen at the design primary breakpoint (tablet
   landscape 1024–1279 for operator screens; desktop ≥1280 for supervisor).
2. Walk through the checks below.
3. Record results in the UI Implementation Report under "Anti-Clutter Check".
4. Any **hard fail** rejects the slice and forces a redesign.

The diagnostic should take under 5 minutes per screen.

---

## 1. Hard Fails (any one rejects the slice)

| # | Check | Pass criterion |
|---|---|---|
| H1 | Primary CTA count in same cognitive frame | ≤1 |
| H2 | Status indicators visible without aggregation | ≤5 |
| H3 | Scroll required to see current state | None |
| H4 | Hover-only controls on touch-primary screen | None |
| H5 | Simultaneous panels demanding equal attention | ≤2 |
| H6 | Operator-critical text under 16px | None |
| H7 | Color-only status indicator (no icon + no label) | None |
| H8 | Decorative animation on operator screen | None |
| H9 | Tap target below 48dp for primary/secondary action | None |
| H10 | Density modes mixed in one screen | None |

**Definitions:**

- *Cognitive frame*: the visual area an operator naturally scans in <2 seconds
  from primary focus. On a tablet landscape, this is roughly the visible
  viewport minus the sidebar.
- *Primary CTA*: a button styled as `variant="default"` or with brand color
  fill that proposes the next forward state transition.
- *Status indicator*: a colored chip, badge, dot, or border that maps to a
  status token. Counting cards in a KPI strip is OK; counting badges
  individually inside cards is what we're protecting against.
- *Cognitive frame for status aggregation*: a station card in a grid is one
  status indicator (not 5), even if the card displays multiple sub-statuses.
  The aggregation requirement applies to peer-level indicators.

---

## 2. Soft Checks (warnings; 3+ warnings rejects the slice)

| # | Check | Pass criterion |
|---|---|---|
| S1 | Vertical visual rhythm consistent | spacing-scale aligned (4/8/12/16/24/32) |
| S2 | Headline hierarchy clear | only one screen-title-level heading |
| S3 | Color palette restraint | ≤3 status tokens visible in same view |
| S4 | Whitespace around primary action | ≥24px margin to next interactive element |
| S5 | Icon-text alignment | icons baseline-aligned with adjacent text |
| S6 | Empty states have next-action | every empty list/table/section |
| S7 | Loading uses skeleton not spinner for >300ms loads | skeleton |
| S8 | Toast use is bounded | ≤1 toast on screen at a time; danger toasts sticky |
| S9 | Drawer/Modal nesting | max depth 2 |
| S10 | Tab labels are single words or 2-word noun phrases | ≤20 chars per tab |

---

## 3. Information Density Score (advisory)

Estimate density:

```
density = (interactive_elements + status_indicators + visible_data_fields) / viewport_area_in_1000_dp²
```

Bands:

- **0–4**: sparse. OK for cockpit. Likely too sparse for dashboard.
- **4–8**: medium. Default target for cockpit and dashboard.
- **8–12**: dense. Acceptable for list and supervisor multi-line.
- **>12**: cluttered. Soft-fail unless explicitly multi-station mode.

The score is advisory; H1–H10 hard fails are the gate.

---

## 4. Mode A (Station Session) Specific Diagnostic

The current implementation renders 4 panels (Open / Identify / Bind / Close)
that can be visible simultaneously. Per layout-templates § 5, this is the
Single-Screen Wizard anti-pattern.

**Specific checks for Station Session:**

| Check | Pass |
|---|---|
| Only one of {Open, Identify, Bind, Running, Close} panel rendered | Yes |
| Step derivation function reads backend session state | Yes |
| StepIndicator present and matches derived step | Yes |
| Errors surfaced through single `BlockerBanner` | Yes |
| Primary action labeled with next forward verb (`Open session`, `Identify operator`, `Bind equipment`, `Close session`) | Yes |
| Secondary actions ≤2 in active panel | Yes |
| Optional context (operator history, lot info) in collapsible drawer | Yes |

If any "Yes" check is "No", the slice is rejected with reason: "Station Session
Mode A clutter anti-pattern; apply Single-Screen Wizard from layout-templates § 5".

---

## 5. Walkthrough Script (for design reviewers)

Read aloud while scanning the screenshot:

1. "I am an operator in nitrile gloves, standing 0.7m from the screen."
2. "Within 2 seconds, the current state of my work is …" — answer must be a single fact.
3. "The single thing I should do next is …" — answer must be one button.
4. "If I cannot proceed, the reason is …" — answer must be a single visible banner.
5. "Now I close my eyes and reopen them — the same answers come back without searching."

Failure of step 1, 2, 3, or 4 is a hard reject.

---

## 6. Don'ts (recurring patterns to flag)

- Two cards side-by-side with primary-style buttons — pick one.
- Status badges scattered across header, body, and footer — aggregate to a single status row.
- Charts on operator cockpit screens — operator does not interpret trends; supervisor does.
- Live-tickling indicators (pulsing dots, animated icons) for non-critical state.
- "Help" tooltips on operator-critical actions — if it needs explanation, the label is wrong.
- Generic "Loading…" spinner with no context — use a skeleton or labelled state.
- Modal opening another modal — split into separate steps.

---

## 7. Reporting Template (paste into Implementation Report)

```markdown
## Anti-Clutter Check

### Hard Fails
- H1 Primary CTA count in cognitive frame: <n> [PASS/FAIL]
- H2 Status indicators without aggregation: <n> [PASS/FAIL]
- H3 Scroll-to-state on design primary breakpoint: <yes/no> [PASS/FAIL]
- H4 Hover-only controls on touch screen: <yes/no> [PASS/FAIL]
- H5 Simultaneous demanding panels: <n> [PASS/FAIL]
- H6 Operator-critical text under 16px: <yes/no> [PASS/FAIL]
- H7 Color-only status indicator: <yes/no> [PASS/FAIL]
- H8 Decorative animation on operator screen: <yes/no> [PASS/FAIL]
- H9 Tap target below 48dp for primary/secondary: <yes/no> [PASS/FAIL]
- H10 Density modes mixed: <yes/no> [PASS/FAIL]

### Soft Checks
- Warnings: <list> (3+ → reject)

### Information Density Score
- Score: <n>
- Band: <sparse/medium/dense/cluttered>

### Walkthrough Script
- State visible in 2s: <fact or FAIL>
- Single next action: <button or FAIL>
- Blocker reason if any: <banner or FAIL>

### Overall
PASS / FAIL
```

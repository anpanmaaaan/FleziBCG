# Canonical DESIGN.md Example — FleziBCG

> A complete DESIGN.md exemplar for agents to learn the shape and depth of
> sections. The actual `DESIGN.md` at the repo root is the authoritative
> document; this file is the **shape reference** so new agents do not need to
> reverse-engineer the format.
>
> If a section in this example contradicts the live `DESIGN.md`, the live
> `DESIGN.md` wins.

---

```markdown
# DESIGN.md — FleziBCG Manufacturing Operations Platform

## Status
Authoritative AI-readable design-system guide for FleziBCG frontend.

## 1. Visual Theme & Atmosphere
FleziBCG is a Manufacturing Operations Platform. UI should feel: operational,
trustworthy, precise, calm under pressure, enterprise-ready, manufacturing-aware,
information-dense but not noisy. Avoid: playful consumer SaaS, generic admin
template, speculative sci-fi dashboard, over-animated, decorative without
operational consequence.

## 2. Color Palette & Roles

### 2.1 Semantic roles → token mapping
| Semantic role | CSS variable (theme.css) | Tailwind theme alias |
|---|---|---|
| surface.app | --background | bg-background |
| surface.panel | --card | bg-card |
| surface.raised | --popover | bg-popover |
| text.primary | --foreground | text-foreground |
| text.secondary | --muted-foreground | text-muted-foreground |
| action.primary | --primary | bg-primary text-primary-foreground |
| status.success | --status-completed | bg-status-completed-bg text-status-completed |
| status.info | --status-in-progress | … |
| status.warning | --status-delayed / --status-on-hold | … |
| status.danger | --status-blocked / --destructive | … |
| status.neutral | --status-pending / --status-cancelled | … |

### 2.2 Operational status → semantic mapping
| Operational meaning | Semantic role |
|---|---|
| RUNNING | status.info |
| PAUSED | status.warning |
| BLOCKED | status.danger |
| COMPLETED | status.success |
| CLOSED | status.neutral + locked treatment |
| QC_PASSED | status.success |
| QC_FAILED | status.danger |
| QC_HOLD | status.warning / status.danger by severity |
| ERP_POSTING_PENDING | status.warning |
| ERP_POSTING_FAILED | status.danger |
| AI_ADVISORY | status.info + advisory label |

### 2.3 Rules
- Never rely on color alone — use 3-channel coding (color + icon + text label).
- Never use red/orange/green decoratively.
- New tokens require updating both theme.css AND this DESIGN.md in the same PR.

## 3. Typography
Font family: Inter, system-ui, …
Type scale (minimums for operator/supervisor — see industrial-ux-standards.md):

| Role | Size | Tailwind |
|---|---|---|
| Headline | 24px | text-2xl |
| Primary metric | 32px+ | text-3xl |
| Current state | 20px | text-xl |
| Body | 16px | text-base |
| Status badge | 14px | text-sm |
| Meta/timestamp | 12px | text-xs |

Line height: 1.4 body, 1.2 headline/metric.

## 4. Component Stylings
[For each: Button, Badge, Card, Table, Dialog, Drawer, Tabs, Form Field,
Toast, Tooltip, Progress, Skeleton — describe variants, states, when to use.]

### 4.1 Button
Variants: default | secondary | ghost | destructive | outline.
Sizes: sm (h-9) | default (h-10) | lg (h-12) | xl (h-14, operator-primary).
States: rest, hover, active, focus, disabled, loading (spinner inline).
Rules: one primary per cognitive frame; destructive always confirms.

### 4.2 Badge
Use for status indicators. Always pair with icon + label.
Variants by status token (success | info | warning | danger | neutral).
Never use as a primary action surface.

### 4.3 Card
Container for grouped content. Padding default p-4; cockpit uses p-6.
Border subtle; no drop shadow on operator screens (causes glare on glossy
shopfloor tablets).

### 4.4 Table
Use shadcn Table primitives. Sticky header. Virtualize via react-window when
rows > 100. Row height 40–48px for list density, 56–64px for dashboard.

### 4.5 Dialog
Use Radix Dialog. Focus trap. Escape closes. Max one dialog open; never nest.
For governed actions, use AlertDialog with reason input + typed-confirm.

### 4.6 Drawer (vaul)
Use for context expansion (operator history, lot details). Default closed.
Opening must not shift the main StateBlock position.

### 4.7 Tabs
Max 5 visible tabs; rest in overflow. Tab labels ≤20 chars.

### 4.8 Form Field
Use react-hook-form + Radix Label/Description.
Inline error below field; never use toast for field-level error.

### 4.9 Toast (sonner)
Max 1 visible. Info 4s. Warning 6s. Danger sticky (operator must dismiss).

### 4.10 Tooltip
Avoid on operator-critical actions — labels should not need explanation.
Acceptable on supervisor/admin screens with helper info.

### 4.11 Progress
Use Radix Progress. Linear preferred. Show estimated time when >5s.

### 4.12 Skeleton
Use for content loads >300ms instead of spinner.

## 5. Layout Principles
- 12-column grid; gutter 16/24/32.
- Density modes: cockpit | dashboard | form | list | multi-station | wizard.
- One density mode per screen.
- Tablet landscape primary for shopfloor; desktop primary for office.
- See layout-templates.md for full skeletons.

## 6. Depth & Elevation
Flat by default. Use elevation only for:
- popover/dropdown (Radix-provided shadow);
- dialog (Radix-provided shadow);
- sticky footer (subtle top border, no shadow).
No layered cards. No "card on card on card".

## 7. Spacing Scale
4 / 8 / 12 / 16 / 24 / 32 / 48 / 64. Tailwind default. Never use arbitrary
values (`p-[17px]`) — pick from scale.

## 8. Responsive Behavior
Breakpoints:
- Narrow <768 — supervisor mobile glance only.
- Tablet portrait 768–1023 — secondary.
- Tablet landscape 1024–1279 — **design primary for shopfloor**.
- Desktop 1280+ — office primary.

Operator screens must function in tablet landscape without horizontal scroll.

## 9. Industrial UX Constraints
Touch target min 48dp (56dp for primary CTA on operator).
Body min 16px; primary metric min 32px.
WCAG AA min; AAA for operator-critical state labels.
3-channel coding (color + icon + label) for all status.
No drag-only or hold-only interactions on operator.
Respect prefers-reduced-motion.

## 10. Empty / Loading / Error States
Every data-driven component declares all three:
- Empty: icon + 1-line explanation + 1 next-action CTA.
- Loading: skeleton for content >300ms; inline button spinner for commands.
- Error: BlockerBanner with retry; never silent.

## 11. Do's and Don'ts

### Do
- Use design tokens, not hex.
- Use i18n for all user-facing strings.
- Use one primary action per cognitive frame.
- Make blockers visible without scrolling.
- Use single-screen wizard for sequential flows.
- Render based on backend-derived truth.

### Don't
- Hardcode permissions, execution state, quality results, or ERP posting status in FE.
- Render multiple equally-demanding panels simultaneously (Mode A anti-pattern).
- Use red/orange/green decoratively.
- Open modal from modal.
- Stack toasts.
- Use new MUI components in new code.
- Use raw hex colors.

## 12. Agent Prompt Guide
When prompting a coding agent to generate UI:

1. Specify the persona, density mode, and screen phase.
2. Reference DESIGN.md tokens by name.
3. Specify the layout template from layout-templates.md.
4. Specify backend-truth boundaries (what backend owns).
5. Specify required states (loading, empty, error).
6. Require anti-clutter diagnostic output in the implementation report.
7. Forbid raw hex, new MUI, decorative animation.

## 13. FleziBCG-Specific UI Contracts
- `ScreenStatusBadge` component is used on every screen header to declare phase.
- `screenStatus` registry entry per route.
- `useI18n()` hook for all user-facing text; i18n registry parity enforced by lint.
- `react-window` for any list/grid above 100 items or 12 cells.
- Sonner toaster mounted once in app shell.

## 14. Review Checklist
- [ ] Token-only colors (no hex)
- [ ] i18n keys registered
- [ ] Phase badge present
- [ ] Anti-clutter diagnostic PASS
- [ ] Industrial UX numerics met
- [ ] Responsive at all 4 breakpoints
- [ ] Loading/Empty/Error states
- [ ] Route accessibility verified
- [ ] MOM safety check passed
- [ ] No new MUI components
```

---

## Notes for Agents Using This Example

- The example above is illustrative. The live `DESIGN.md` at the repo root may
  have more or fewer sections. Always read the live file first.
- When introducing a new token, both files (live `DESIGN.md` and `theme.css`)
  must be updated in the same PR.
- This canonical example is updated when the design system structurally
  changes, not when individual tokens change.

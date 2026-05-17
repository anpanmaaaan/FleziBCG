# Layout Templates — FleziBCG

> Concrete layout skeletons. Pick exactly one template per screen; do not blend.
> Use these as the starting point; deviation requires justification.

## 0. How to Use This File

1. Identify the screen's primary purpose.
2. Pick the matching template below.
3. Copy the skeleton.
4. Fill from existing source-aligned components.
5. Run the anti-clutter diagnostic from `anti-clutter-diagnostic.md`.

Stack assumed: React 18 + Tailwind v4 + shadcn/ui (Radix) + tokens from `theme.css`.

---

## 1. Template — Operator Cockpit (single station)

**Use when:** one operator, one station, one focus task (e.g., run lot, log
defect, identify operator).

**Density:** `cockpit`. Tablet landscape primary.

**Layout slots (top → bottom):**

```
┌────────────────────────────────────────────────────────┐
│ HeaderBar: station name | session ID | ScreenStatusBadge │
├────────────────────────────────────────────────────────┤
│ StateBlock                                              │
│   • current state (text-xl)                             │
│   • primary metric (text-3xl)                           │
│   • elapsed/target (text-base)                          │
├────────────────────────────────────────────────────────┤
│ BlockerBanner (only when status.danger or hold)         │
├────────────────────────────────────────────────────────┤
│ ActionBar (1 primary CTA, ≤2 secondary, fixed bottom)  │
├────────────────────────────────────────────────────────┤
│ ContextDrawer (collapsed by default; lot/operator/QC)   │
└────────────────────────────────────────────────────────┘
```

**Skeleton:**

```tsx
<CockpitLayout density="cockpit">
  <CockpitHeader station={station} sessionId={s.id} phase={s.phase} />
  <StateBlock
    state={s.state}
    primaryMetric={{ label: t("lot.qty"), value: s.qty }}
    elapsed={s.elapsedMs}
    target={s.targetMs}
  />
  {s.blocker && <BlockerBanner blocker={s.blocker} />}
  <ActionBar>
    <PrimaryAction onClick={onAdvance} disabled={!s.canAdvance}>
      {t(s.nextAction.label)}
    </PrimaryAction>
    <SecondaryAction onClick={onPause}>{t("pause")}</SecondaryAction>
  </ActionBar>
  <ContextDrawer defaultOpen={false}>
    <OperatorContext />
    <LotContext />
    <QualityContext />
  </ContextDrawer>
</CockpitLayout>
```

**Rules:**

- Exactly **one** primary action visible.
- StateBlock occupies the visual centerline; no decoration competes with it.
- ContextDrawer is closed by default; opening it does not shift StateBlock.

---

## 2. Template — Supervisor Dashboard (multi-line)

**Use when:** supervisor watches multiple lines/stations and decides where to
intervene.

**Density:** `dashboard`. Desktop or tablet landscape.

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ HeaderBar: scope (plant/line) | time window | filters    │
├─────────────────────────────────────────────────────────┤
│ KPI strip (3–5 cards, no charts, just numbers + delta)   │
├─────────────────────────────────────────────────────────┤
│ Blocker queue (top, capped at 5; "View all" for rest)    │
├─────────────────────────────────────────────────────────┤
│ Station grid (virtualized via react-window if >12 cells) │
└─────────────────────────────────────────────────────────┘
```

**Rules:**

- KPI strip cap: 5. Above that, move to dedicated "Metrics" tab.
- Blocker queue is the only place with `status.danger` styling; do not echo
  blocker color in station cells (single-source highlight).
- Station cell shows: name, current state, last event time, blocker icon if any.
  No mini-charts in cells.
- Use `react-window` for >12 cells to keep tap latency under 100ms.

---

## 3. Template — Form / Admin

**Use when:** master data, configuration, IAM, governance setup.

**Density:** `form`. Desktop primary, tablet acceptable.

**Layout:**

```
┌────────────────────────────────────────┐
│ HeaderBar: title | breadcrumb           │
├────────────────────────────────────────┤
│ FormBody (single column, ≤640px wide)  │
│   • section 1                           │
│   • section 2                           │
│   • …                                   │
├────────────────────────────────────────┤
│ Sticky footer: Save | Cancel            │
└────────────────────────────────────────┘
```

**Skeleton:**

```tsx
<FormLayout density="form">
  <FormHeader title={t("user.edit")} breadcrumb={crumbs} />
  <FormBody>
    <Section title={t("user.basics")}>
      <Field name="email" />
      <Field name="displayName" />
    </Section>
    <Section title={t("user.roles")}>
      <RoleAssigner />
    </Section>
  </FormBody>
  <StickyFooter>
    <Button variant="ghost">{t("cancel")}</Button>
    <Button variant="default" type="submit">{t("save")}</Button>
  </StickyFooter>
</FormLayout>
```

**Rules:**

- Single column, max 640px wide. Multi-column forms cause field misalignment
  and accessibility issues.
- Errors inline, not in toast. Toast only for save success/failure.
- Use `react-hook-form` + Radix Label/Description.
- Save button is enabled only when form is dirty AND valid.

---

## 4. Template — List / Inventory

**Use when:** browse work orders, lots, materials, audit log.

**Density:** `list`. Desktop or tablet landscape.

**Layout:**

```
┌──────────────────────────────────────────────────────┐
│ HeaderBar: title | scope filter | search             │
├──────────────────────────────────────────────────────┤
│ ChipFilters (≤6 chips; rest in "More filters" menu)  │
├──────────────────────────────────────────────────────┤
│ Table (virtualized, sticky header, 40–48px row)      │
│   • sortable columns                                  │
│   • row click → detail route                          │
├──────────────────────────────────────────────────────┤
│ Footer: row count | pagination | export              │
└──────────────────────────────────────────────────────┘
```

**Rules:**

- Virtualize via `react-window` when rows >100.
- Sticky header. Body scrolls; outer page does not scroll within this template.
- Row click navigates to detail route; do not open inline edit.
- Bulk action: select via checkbox column + sticky bulk-action bar at top.
- Empty state shows: icon + 1-line explanation + 1 next-action CTA.

---

## 5. Template — Single-Screen Wizard (the Mode A pattern)

**Use when:** a workflow has a fixed sequence of steps driven by backend state
(e.g., Station Session: Open → Identify Operator → Bind Equipment → … → Close).

**Density:** `wizard`. Tablet landscape primary.

**Why this exists:** the current Mode A renders Open/Identify/Bind/Close panels
simultaneously, causing the "rối" (clutter) feedback. This template fixes that
by rendering exactly **one** step at a time, with backend session state as the
driver.

**Layout:**

```
┌────────────────────────────────────────────────────────┐
│ HeaderBar: station | session ID | ScreenStatusBadge    │
├────────────────────────────────────────────────────────┤
│ StepIndicator (top, horizontal, 4–6 steps)             │
│   ● Open  ─ ◐ Identify  ─ ○ Bind  ─ ○ … ─ ○ Close      │
├────────────────────────────────────────────────────────┤
│ ActivePanel (exactly one, full focus)                   │
│   • single primary action                               │
│   • single error surface (BlockerBanner if error)       │
├────────────────────────────────────────────────────────┤
│ Footer: "Back" only when backend permits backward step  │
└────────────────────────────────────────────────────────┘
```

**Skeleton:**

```tsx
function StationSession() {
  const { session, error } = useSessionState(stationId);
  const step = deriveStepFromSession(session); // backend-driven, not UI-driven

  return (
    <WizardLayout density="wizard">
      <WizardHeader station={station} sessionId={session?.id} phase={phase} />
      <StepIndicator steps={SESSION_STEPS} current={step} />
      {error && <BlockerBanner error={error} />}
      <ActivePanel>
        {step === "open" && <OpenSessionPanel onAdvance={refetch} />}
        {step === "identify" && <IdentifyOperatorPanel session={session} onAdvance={refetch} />}
        {step === "bind" && <BindEquipmentPanel session={session} onAdvance={refetch} />}
        {step === "running" && <RunningPanel session={session} />}
        {step === "close" && <CloseSessionPanel session={session} onAdvance={refetch} />}
      </ActivePanel>
      {canGoBack(session) && <WizardFooter onBack={onBack} />}
    </WizardLayout>
  );
}
```

**Rules:**

1. The step shown is **derived from backend session state**, never set
   independently in frontend.
2. Exactly **one** ActivePanel is rendered at a time.
3. Errors flow through a **single** `BlockerBanner` surface — no per-panel
   toast cluttering the screen.
4. StepIndicator is visual context; tapping a step does not navigate unless
   backend permits backward transition.
5. Each panel may have at most **one** primary CTA; secondary actions in panel
   footer at most 2.
6. The wizard layout never mixes with cockpit layout. Once the session enters
   `running` state, the screen MAY transition to Cockpit Template § 1, but
   only via an explicit route change, not in-place panel swap.

**Step derivation function (canonical):**

```ts
type WizardStep = "open" | "identify" | "bind" | "running" | "close" | "closed";

export function deriveStepFromSession(s: StationSession | null): WizardStep {
  if (!s) return "open";
  if (!s.operatorId) return "identify";
  if (!s.equipmentBound) return "bind";
  if (s.state === "RUNNING") return "running";
  if (s.state === "CLOSING") return "close";
  if (s.state === "CLOSED") return "closed";
  return "open";
}
```

The frontend MUST NOT decide step independently from backend session state.
The function above is a pure projection of backend truth into UI step.

---

## 6. Composition Rules

- Do not nest templates. A screen is exactly one template.
- A Cockpit screen may contain a Drawer that is itself a small Form — that is
  acceptable as long as the cockpit primary action remains the dominant focus.
- A List detail route uses the Form template, not List-inside-List.
- A wall display (TV) uses the Dashboard template scaled per
  `industrial-ux-standards.md` § 1 wall display row.

---

## 7. App Shell

All templates above sit inside the existing app shell:

- Top bar (global): brand | env | user menu.
- Sidebar (persona-filtered): primary navigation.
- Main: the chosen template.

Do not redesign the shell as part of a screen-level slice. Shell changes are a
separate slice (UI-SHELL-*).

---

## 8. Skeleton Components Status

The skeleton snippets above reference `CockpitLayout`, `WizardLayout`,
`StateBlock`, `BlockerBanner`, etc. Some of these may not exist yet in the
codebase.

- If a referenced component exists → import and use.
- If it does not exist → either implement it as a small wrapper (preferred) or
  inline the composition the first time it is needed and extract on second use.
- Do not introduce a "framework" component prematurely; let the second use
  case drive abstraction.

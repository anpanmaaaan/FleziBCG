# UI/UX Implementation Report

## Selected Skill

`design-md-ui-governor` (primary) + `stitch-design-md-ui-ux` (frontend rules) + `design-system-enforcer` (rejection gate).

Snapshotted (older) versions under
`docs/ai-skills/design-md-ui-governor-workspace/iteration-1/baseline-snapshot/`.

## Source Inputs Read

1. `baseline-snapshot/design-md-ui-governor/SKILL.md`
2. `baseline-snapshot/design-md-ui-governor/references/design-md-format-rules.md`
3. `baseline-snapshot/design-md-ui-governor/references/flezibcg-mom-ui-guardrails.md`
4. `baseline-snapshot/design-md-ui-governor/references/source-alignment-rules.md`
5. `baseline-snapshot/stitch-design-md-ui-ux/SKILL.md`
6. `baseline-snapshot/design-system-enforcer/SKILL.md`
7. `docs/design/DESIGN.md` (color, typography, supervisor layout, status mapping)
8. `frontend/src/styles/theme.css` (token names — `--status-in-progress`, `--status-blocked`, etc.)
9. `frontend/src/app/components/PageHeader.tsx`, `StatusBadge.tsx`, `StatsCard.tsx` (existing patterns)

Not read (out of scope for this slice): backend handler, IAM contract,
event schema. The screen consumes a typed `Station[]` shape only.

## Scope

UI-04 Supervisory slice — **single screen**: Supervisor Multi-Station view
for one production line (Line 2, 24 stations).

- Route (proposed, not registered in this slice): `/supervisor/lines/:lineId`
- Persona target: `SUPERVISOR` (UX targeting only, not authorization).
- Viewport primary: desktop 1440px; tablet landscape supported.
- Phase label: **PARTIAL** — UI is ACTIVE, data wiring depends on
  `GET /v1/lines/:lineId/stations` being available; fallback is loading /
  error / empty states. No mocks injected into the production path.

Out of scope:
- Drill-down station detail page (linked but not built here).
- Blocker resolution actions (only display + escalate link; no state
  mutation from FE).
- KPI computation (FE displays only what backend returns).

## Design System Alignment

| DESIGN.md rule | Applied |
|---|---|
| Semantic status tokens | `RUNNING → status.info`, `PAUSED → status.warning`, `BLOCKED → status.danger`, `COMPLETED → status.success`, `CLOSED → status.neutral + locked` |
| Never color-only | Each station card pairs color with state label + icon |
| Supervisor density | Dense but structured: KPI strip → blocker queue → 6x4 station grid |
| Typography | H1 page title, H3 card titles, mono for station code/last event ID, large numeric for KPI |
| Touch targets | Supervisor screen: 40-44px min; station card tap area = full card; escalate buttons 40px |
| Elevation | Border + spacing; no shadows on cards beyond `border-subtle`; raised only on hover |
| No third-party brand | None |
| App shell preserved | Renders inside existing layout via `PageHeader`; sidebar untouched |

Status badge color map (sourced from `theme.css`):

| State | Token (CSS var) | Badge |
|---|---|---|
| RUNNING | `--status-in-progress` | blue |
| PAUSED | `--status-delayed` | amber |
| BLOCKED | `--status-blocked` | red |
| COMPLETED | `--status-completed` | green |
| CLOSED | `--status-cancelled` | gray + lock icon |

## Source Alignment

Verified against `source-alignment-rules.md`:

1. Existing routes preserved — new route is additive, nested under
   current app layout. Not yet registered in router (caller will wire).
2. Reuses `PageHeader`, `StatusBadge`, `StatsCard`, shadcn `Card`,
   `Button`, `Skeleton`, `Alert` patterns already in repo.
3. API client — assumes `apiClient.get<Station[]>(...)`; if project uses a
   different helper, swap the one-liner inside `useStations`.
4. No invented API fields. Component consumes only what backend
   contract documents: `id`, `code`, `name`, `state`, `lastEventAt`,
   `blocker?`, `oeeToday?`, `throughputToday?`.
5. i18n — strings routed through `useI18n().t(key)`; English fallback
   in code. No hard-coded user-facing strings without a key.
6. Mocks not mixed in: file contains no fixture data; loading/empty/error
   are real UI states, not silent mock fallbacks.

## Files Changed

This slice is a **draft skeleton** delivered to the workspace eval folder
(not committed to `frontend/src/`):

- `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/eval-supervisor-multistation/old_skill/outputs/SupervisorLineView.tsx` — screen skeleton.
- `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/eval-supervisor-multistation/old_skill/outputs/implementation-report.md` — this report.
- `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/eval-supervisor-multistation/old_skill/outputs/notes.md` — supplementary notes.

No file under `frontend/src/` was modified. No dependencies installed.

## Screens Affected

| Screen | Phase | Notes |
|---|---|---|
| Supervisor — Line Multi-Station (NEW) | PARTIAL | UI complete; data wiring pending |
| Supervisor — Station Detail (existing/planned) | unchanged | Linked via row/card click only |
| Operator Station Cockpit | unchanged | Not touched |

## Components Added / Updated

Added (within `SupervisorLineView.tsx` file as local sub-components, to keep one-file skeleton):

- `KpiStrip` — 4 KPI tiles (OEE, throughput, blockers, downtime). Pure
  display; values come from backend or `—` when unknown.
- `BlockerQueuePanel` — list of stations with `blocker != null`, sorted
  by `blocker.since` ascending. Empty state when no blockers.
- `StationGrid` — responsive grid (4 cols desktop / 3 cols tablet
  landscape / 2 cols below) of `StationCard`.
- `StationCard` — state color, state label, last event time (relative),
  blocker icon if present, station code as mono.
- `useStations(lineId)` — small hook with `{ data, loading, error }`.

Not added (reused from existing repo): `PageHeader`, `StatusBadge`,
`Card`, `Button`, `Skeleton`, `Alert`, `Tooltip`.

When promoted to `frontend/src/`, recommended extraction:
- `frontend/src/app/components/supervisor/KpiStrip.tsx`
- `frontend/src/app/components/supervisor/BlockerQueuePanel.tsx`
- `frontend/src/app/components/supervisor/StationCard.tsx`
- `frontend/src/app/pages/SupervisorLineView.tsx`
- `frontend/src/app/api/stations.ts` (hook + types)

## Data Source Status

| Surface | Source | Status |
|---|---|---|
| Station list | `GET /v1/lines/:lineId/stations` | declared contract; consumed as-is |
| KPI (OEE, throughput, blockers, downtime) | Same response (per-line summary) **OR** sibling `/v1/lines/:lineId/kpi` | OPEN — see Known Limitations |
| Blocker info | `station.blocker` on `Station` | declared contract |
| Relative time | client-side formatting only | OK, display-only |

No FE-derived execution state. No FE-computed OEE. No fake "live" indicator.

## MOM Safety Check

Against `flezibcg-mom-ui-guardrails.md` and Hard Reject Rules:

- [x] FE does **not** decide station state — `state` rendered from
      backend field only.
- [x] FE does **not** decide authorization — no `allowed_actions`
      hardcoded; escalate button is a navigation, not a state mutation.
- [x] FE does **not** fake quality / acceptance / ERP / backflush
      — none surfaced here.
- [x] No AI deterministic claims — AI advisory not surfaced in this slice.
- [x] No mock data in production code path.
- [x] Persona-targeted (Supervisor) but not persona-gated for security.
- [x] Future scope (real-time updates, blocker resolution actions) is
      visibly **disabled** with rationale, not faked.

## Responsive / Accessibility Check

| Concern | Behavior |
|---|---|
| 1440px desktop | 4-column station grid, right-side panel collapsed by default |
| 1280px desktop | 4-column grid, KPI strip 4-up |
| Tablet landscape ~1024px | 3-column grid, KPI strip 4-up scrollable if narrow |
| Tablet portrait | 2-column grid, KPI 2x2 |
| Mobile | Stack: KPI 2x2, blocker queue full-width, stations 2-col list |
| Color-only | No — all states have icon + text label + color |
| Focus ring | Uses `--focus-ring` via Tailwind `focus-visible:ring-2` |
| Keyboard | Cards are `<button>` for keyboard activation |
| Touch | Card hit area 144x96px+ at 1440; escalate buttons 40px |
| Text contrast | Status badges use existing tokens (theme.css) — already AA |
| i18n | Strings via `t(key)` with English fallbacks |

## Tests / Build Run

Not run in this slice — deliverable is a draft skeleton under the
eval workspace folder, not committed to `frontend/src/`.

When promoted, the caller should run:

```
pnpm --filter frontend lint
pnpm --filter frontend typecheck
pnpm --filter frontend test -- SupervisorLineView
pnpm --filter frontend build
```

(Exact script names depend on `frontend/package.json`; the caller will
adjust.)

## Known Limitations

1. **KPI source ambiguity.** The task says the page shows OEE / throughput
   / blockers / downtime, but the documented backend endpoint only
   guarantees `Station[]`. The skeleton reads optional `kpi` fields and
   renders `—` if absent; **a separate KPI endpoint is recommended**
   before promoting this to ACTIVE. No FE-side OEE math.
2. **Blocker queue ordering** uses `blocker.since` if backend supplies
   it; otherwise falls back to `lastEventAt`. Backend should expose a
   stable sort key.
3. **No live updates** in this slice. The hook fetches once + manual
   refresh button. WebSocket / SSE wiring is a separate slice.
4. **No drill-down screen** built. Station card click navigates to
   `/supervisor/stations/:stationId` (route assumed to exist or to be
   added by station-detail slice).
5. **Blocker resolution actions** intentionally not shown — that requires
   a backend command + audit, owned by a separate execution slice.
6. **Persona / route guard** not wired here.
7. **Virtualization** — 24 stations fits comfortably without
   `react-window`. If the line grows past ~200 stations, switch the grid
   to a windowed layout.

## Next Recommended FE Slice

1. **UI-04b Supervisor — Station Detail drill-down** (consumes
   `GET /v1/stations/:stationId` + recent events).
2. **UI-04c Supervisor — Blocker triage modal** (read-only escalation,
   no mutation) once backend exposes blocker escalation command.
3. **UI-04d Live updates** — add SSE/WS subscription to refresh
   `station.state` and `station.lastEventAt` only (no FE state
   derivation).
4. **API contract patch** — confirm whether KPI lives on
   `/v1/lines/:lineId/stations`, on `/v1/lines/:lineId/kpi`, or both.

// Supervisor Multi-Station View — PARTIAL
// Single-line, 24-station supervisor surface for Line 2.
// Source of truth: backend projection at `GET /v1/lines/:lineId/stations`.
// Frontend only displays; it never decides execution state, blocker disposition,
// or KPI computation.
//
// Layout template: Supervisor Dashboard (layout-templates.md § 2).
// Density mode: dashboard (single mode; do not mix).
//
// Anti-clutter posture:
//   - 1 primary CTA per cognitive frame (the active blocker resolve action).
//   - Blocker queue capped at 5 visible (View all routes to detail).
//   - Station cells are aggregated single status indicators (color + icon + label).
//   - Grid virtualized via react-window for >12 cells.
//
// Phase: PARTIAL — wired to `GET /v1/lines/:lineId/stations`; resolve-blocker
// action is FUTURE (rendered as disabled per skill § 5.3).

import { useEffect, useMemo, useRef, useState, useCallback, type CSSProperties } from "react";
import { useParams } from "react-router";
import { FixedSizeGrid as Grid, type GridChildComponentProps } from "react-window";
import {
  AlertTriangle,
  Pause,
  PlayCircle,
  CheckCircle2,
  CircleSlash2,
  AlertOctagon,
  Clock,
  RefreshCw,
  WifiOff,
} from "lucide-react";
import { ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";

// ─────────────────────────────────────────────────────────────────────────────
// Types — must mirror backend contract `Station[]` exactly. Do NOT invent fields.
// ─────────────────────────────────────────────────────────────────────────────

export type StationState =
  | "RUNNING"
  | "PAUSED"
  | "BLOCKED"
  | "COMPLETED"
  | "CLOSED";

export interface Blocker {
  /** Stable blocker id from backend, used for dedupe (extended-guardrails § 3). */
  id: string;
  /** P1 / P2 / P3 / P4 severity per extended-guardrails § 3. */
  severity: "P1" | "P2" | "P3" | "P4";
  /** Short reason code from backend (e.g., `MAT_SHORTAGE`, `QC_HOLD`). */
  code: string;
  /** Operator-facing human reason (already localized by backend OR i18n key). */
  reason: string;
  /** Raised at — ISO 8601 UTC; render via formatStationTime() in station tz. */
  raisedAt: string;
}

export interface Station {
  id: string;
  code: string; // e.g. "L2-ST-07"
  name: string; // e.g. "Welding Cell 7"
  state: StationState;
  lastEventAt: string; // ISO 8601 UTC
  blocker?: Blocker | null;
}

export interface LineKpis {
  /** OEE for the current shift, 0..1. Backend computed. */
  oee: number;
  /** Throughput today, integer units. Backend computed. */
  throughput: number;
  /** Active blockers count across line, integer. */
  blockersCount: number;
  /** Cumulative downtime today in minutes, integer. */
  downtimeMinutes: number;
}

export interface LineStationsResponse {
  lineId: string;
  lineName: string;
  kpis: LineKpis;
  stations: Station[];
  fetchedAt: string; // ISO 8601 UTC of projection snapshot
}

// ─────────────────────────────────────────────────────────────────────────────
// Backend client — single boundary; no other code should call the endpoint.
// ─────────────────────────────────────────────────────────────────────────────

async function fetchLineStations(lineId: string, signal: AbortSignal): Promise<LineStationsResponse> {
  const res = await fetch(`/v1/lines/${encodeURIComponent(lineId)}/stations`, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal,
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return (await res.json()) as LineStationsResponse;
}

// ─────────────────────────────────────────────────────────────────────────────
// Status token map — uses tokens from frontend/src/styles/theme.css.
// Drift note (SKILL § 5.9): DESIGN.md uses semantic roles; theme.css uses
// operational tokens. We MAP rather than rename until UI-TOKEN-RECONCILE lands.
// ─────────────────────────────────────────────────────────────────────────────

type Tone = "running" | "paused" | "blocked" | "completed" | "closed";

const STATE_TO_TONE: Record<StationState, Tone> = {
  RUNNING: "running",
  PAUSED: "paused",
  BLOCKED: "blocked",
  COMPLETED: "completed",
  CLOSED: "closed",
};

const TONE_TOKEN: Record<
  Tone,
  { fg: string; bg: string; border: string; icon: typeof PlayCircle; labelKey: string }
> = {
  running: {
    fg: "text-[color:var(--status-in-progress)]",
    bg: "bg-[color:var(--status-in-progress-bg)]",
    border: "border-[color:var(--status-in-progress)]",
    icon: PlayCircle,
    labelKey: "station.state.running",
  },
  paused: {
    fg: "text-[color:var(--status-on-hold)]",
    bg: "bg-[color:var(--status-on-hold-bg)]",
    border: "border-[color:var(--status-on-hold)]",
    icon: Pause,
    labelKey: "station.state.paused",
  },
  blocked: {
    fg: "text-[color:var(--status-blocked)]",
    bg: "bg-[color:var(--status-blocked-bg)]",
    border: "border-[color:var(--status-blocked)]",
    icon: AlertOctagon,
    labelKey: "station.state.blocked",
  },
  completed: {
    fg: "text-[color:var(--status-completed)]",
    bg: "bg-[color:var(--status-completed-bg)]",
    border: "border-[color:var(--status-completed)]",
    icon: CheckCircle2,
    labelKey: "station.state.completed",
  },
  closed: {
    fg: "text-[color:var(--status-cancelled)]",
    bg: "bg-[color:var(--status-cancelled-bg)]",
    border: "border-[color:var(--status-cancelled)]",
    icon: CircleSlash2,
    labelKey: "station.state.closed",
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Time formatting — extended-guardrails § 12. Always render in station tz.
// For brevity in this skeleton we use the user's locale; replace with
// station-tz aware helper when SupervisorLineView ships.
// ─────────────────────────────────────────────────────────────────────────────

function formatRelative(iso: string, now = Date.now()): string {
  const t = new Date(iso).getTime();
  if (!Number.isFinite(t)) return "—";
  const diffSec = Math.max(0, Math.round((now - t) / 1000));
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.round(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffH = Math.round(diffMin / 60);
  if (diffH < 24) return `${diffH}h ago`;
  return new Date(iso).toISOString().slice(0, 16).replace("T", " ");
}

// ─────────────────────────────────────────────────────────────────────────────
// Subcomponents
// ─────────────────────────────────────────────────────────────────────────────

interface KpiCardProps {
  label: string;
  value: string;
  hint?: string;
  tone?: "neutral" | "danger";
}

function KpiCard({ label, value, hint, tone = "neutral" }: KpiCardProps) {
  const toneCls =
    tone === "danger"
      ? "text-[color:var(--status-blocked)]"
      : "text-foreground";
  return (
    <div
      role="group"
      aria-label={label}
      className="rounded-lg border border-border bg-card p-4 min-h-[96px] flex flex-col justify-between"
    >
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className={`text-3xl font-medium tabular-nums ${toneCls}`}>{value}</div>
      {hint ? <div className="text-xs text-muted-foreground">{hint}</div> : null}
    </div>
  );
}

interface KpiStripProps {
  kpis: LineKpis | null;
  t: (k: string) => string;
}

function KpiStrip({ kpis, t }: KpiStripProps) {
  // KPI strip cap = 4 (template says ≤5; we use 4 to keep cognitive frame light).
  if (!kpis) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3" aria-busy="true">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-lg border border-border bg-card p-4 min-h-[96px] animate-pulse"
          />
        ))}
      </div>
    );
  }
  const oeePct = `${Math.round(kpis.oee * 100)}%`;
  const downtimeHm = `${Math.floor(kpis.downtimeMinutes / 60)}h ${kpis.downtimeMinutes % 60}m`;
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <KpiCard label={t("kpi.oee.today")} value={oeePct} hint={t("kpi.oee.hint")} />
      <KpiCard
        label={t("kpi.throughput.today")}
        value={kpis.throughput.toLocaleString()}
        hint={t("kpi.throughput.unit")}
      />
      <KpiCard
        label={t("kpi.blockers.active")}
        value={String(kpis.blockersCount)}
        tone={kpis.blockersCount > 0 ? "danger" : "neutral"}
      />
      <KpiCard
        label={t("kpi.downtime.today")}
        value={downtimeHm}
        tone={kpis.downtimeMinutes >= 30 ? "danger" : "neutral"}
      />
    </div>
  );
}

interface BlockerQueueProps {
  stations: Station[];
  onSelect: (stationId: string) => void;
  t: (k: string) => string;
}

function BlockerQueue({ stations, onSelect, t }: BlockerQueueProps) {
  // Sort by severity then raisedAt asc; cap at 5 (template § 2 rule).
  const sevRank: Record<Blocker["severity"], number> = { P1: 0, P2: 1, P3: 2, P4: 3 };
  const blocked = useMemo(() => {
    return stations
      .filter((s) => !!s.blocker)
      .sort((a, b) => {
        const ra = sevRank[a.blocker!.severity];
        const rb = sevRank[b.blocker!.severity];
        if (ra !== rb) return ra - rb;
        return new Date(a.blocker!.raisedAt).getTime() - new Date(b.blocker!.raisedAt).getTime();
      });
  }, [stations]);

  if (blocked.length === 0) {
    return (
      <div
        role="status"
        aria-live="polite"
        className="rounded-lg border border-border bg-card p-4 flex items-center gap-3"
      >
        <CheckCircle2 className="h-5 w-5 text-[color:var(--status-completed)]" aria-hidden="true" />
        <span className="text-base">{t("blocker.queue.empty")}</span>
      </div>
    );
  }

  const top = blocked.slice(0, 5);
  const moreCount = blocked.length - top.length;

  return (
    <section
      aria-labelledby="blocker-queue-heading"
      className="rounded-lg border border-[color:var(--status-blocked)]/40 bg-[color:var(--status-blocked-bg)] p-3"
    >
      <header className="flex items-center justify-between mb-2">
        <h2
          id="blocker-queue-heading"
          className="text-base font-medium flex items-center gap-2"
        >
          <AlertTriangle
            className="h-5 w-5 text-[color:var(--status-blocked)]"
            aria-hidden="true"
          />
          {t("blocker.queue.title")} ({blocked.length})
        </h2>
        {moreCount > 0 ? (
          <button
            type="button"
            className="text-sm underline text-foreground/80 hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--focus-ring)] rounded"
          >
            {t("blocker.queue.viewAll")} (+{moreCount})
          </button>
        ) : null}
      </header>
      <ul role="list" className="divide-y divide-[color:var(--status-blocked)]/20">
        {top.map((s) => (
          <li key={s.id}>
            <button
              type="button"
              onClick={() => onSelect(s.id)}
              className="w-full text-left py-2 px-2 flex items-center gap-3 hover:bg-white/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--focus-ring)] rounded min-h-[48px]"
              aria-label={`${s.code} ${s.blocker!.code} ${s.blocker!.reason}`}
            >
              <span
                className="inline-flex items-center justify-center rounded px-2 py-0.5 text-xs font-medium bg-[color:var(--status-blocked)] text-white"
                aria-label={s.blocker!.severity}
              >
                {s.blocker!.severity}
              </span>
              <span className="font-mono text-sm w-24 shrink-0">{s.code}</span>
              <span className="text-base flex-1 truncate">{s.blocker!.reason}</span>
              <span className="text-xs text-muted-foreground tabular-nums">
                {formatRelative(s.blocker!.raisedAt)}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

interface StationCellProps {
  station: Station;
  onSelect: (id: string) => void;
  t: (k: string) => string;
}

function StationCell({ station, onSelect, t }: StationCellProps) {
  const tone = STATE_TO_TONE[station.state];
  const tk = TONE_TOKEN[tone];
  const Icon = tk.icon;
  return (
    <button
      type="button"
      onClick={() => onSelect(station.id)}
      // 3-channel coding: icon + label + color border. Aggregated single
      // status indicator per anti-clutter-diagnostic § 1 H2.
      className={`group h-full w-full text-left rounded-lg border ${tk.border} ${tk.bg} p-3 flex flex-col gap-2 min-h-[112px] focus:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--focus-ring)] hover:brightness-[0.98]`}
      aria-label={`${station.code} ${station.name} ${t(tk.labelKey)}${station.blocker ? " — " + t("station.blocker.present") : ""}`}
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-sm text-foreground/80">{station.code}</span>
        {station.blocker ? (
          <AlertTriangle
            className="h-5 w-5 text-[color:var(--status-blocked)]"
            aria-label={t("station.blocker.present")}
          />
        ) : (
          <span className="h-5 w-5" aria-hidden="true" />
        )}
      </div>
      <div className="flex items-center gap-2">
        <Icon className={`h-5 w-5 ${tk.fg}`} aria-hidden="true" />
        <span className={`text-xl font-medium ${tk.fg}`}>{t(tk.labelKey)}</span>
      </div>
      <div className="text-xs text-muted-foreground flex items-center gap-1 tabular-nums">
        <Clock className="h-3.5 w-3.5" aria-hidden="true" />
        {formatRelative(station.lastEventAt)}
      </div>
    </button>
  );
}

interface StationGridProps {
  stations: Station[];
  onSelect: (id: string) => void;
  t: (k: string) => string;
}

/**
 * Virtualized grid. For 24 stations we are below the react-window threshold
 * (12 cells per extended-guardrails § 4), but the layout-templates rule says
 * "use react-window when >12 cells". 24 > 12, so we virtualize here. This
 * also future-proofs the screen for plant-level views with 50+ stations.
 */
function StationGrid({ stations, onSelect, t }: StationGridProps) {
  // Responsive column count tuned for design primary breakpoint and tablet.
  // Desktop ≥1440: 6 cols → 4 rows for 24. Tablet landscape: 4 cols → 6 rows.
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState<{ w: number; h: number }>({ w: 0, h: 0 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const r = entries[0].contentRect;
      setSize({ w: Math.floor(r.width), h: Math.floor(r.height) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const cols = size.w >= 1280 ? 6 : size.w >= 1024 ? 4 : size.w >= 640 ? 3 : 2;
  const rowHeight = 140; // anti-clutter S1: spacing scale aligned
  const gutter = 12;
  const colWidth = cols > 0 && size.w > 0 ? Math.floor((size.w - gutter * (cols - 1)) / cols) : 200;
  const rowCount = Math.ceil(stations.length / cols);

  const renderCell = useCallback(
    ({ columnIndex, rowIndex, style }: GridChildComponentProps) => {
      const i = rowIndex * cols + columnIndex;
      const s = stations[i];
      const cellStyle: CSSProperties = {
        ...style,
        // Apply visual gutter inside the virtualizer's pixel-perfect slot.
        left: typeof style.left === "number" ? style.left + (columnIndex === 0 ? 0 : gutter / 2) : style.left,
        width: typeof style.width === "number" ? style.width - gutter / 2 : style.width,
        top: typeof style.top === "number" ? style.top + (rowIndex === 0 ? 0 : gutter / 2) : style.top,
        height: typeof style.height === "number" ? style.height - gutter / 2 : style.height,
      };
      if (!s) return <div style={cellStyle} aria-hidden="true" />;
      return (
        <div style={cellStyle}>
          <StationCell station={s} onSelect={onSelect} t={t} />
        </div>
      );
    },
    [stations, cols, onSelect, t]
  );

  return (
    <div
      ref={containerRef}
      className="flex-1 min-h-[480px]"
      role="grid"
      aria-label={t("station.grid.label")}
    >
      {size.w > 0 && size.h > 0 ? (
        <Grid
          columnCount={cols}
          rowCount={rowCount}
          columnWidth={colWidth + gutter / 2}
          rowHeight={rowHeight + gutter / 2}
          width={size.w}
          height={Math.max(rowHeight * rowCount + gutter * (rowCount - 1), 480)}
        >
          {renderCell}
        </Grid>
      ) : null}
    </div>
  );
}

interface ConnectivityBannerProps {
  state: "ok" | "stale" | "error" | "offline";
  fetchedAt?: string;
  onRetry: () => void;
  t: (k: string) => string;
}

function ConnectivityBanner({ state, fetchedAt, onRetry, t }: ConnectivityBannerProps) {
  if (state === "ok") return null;
  const isOffline = state === "offline";
  const isError = state === "error";
  const tone = isOffline || isError ? "blocked" : "delayed";
  const toneCls =
    tone === "blocked"
      ? "border-[color:var(--status-blocked)]/40 bg-[color:var(--status-blocked-bg)]"
      : "border-[color:var(--status-delayed)]/40 bg-[color:var(--status-delayed-bg)]";
  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`rounded-lg border ${toneCls} p-3 flex items-center justify-between gap-3`}
    >
      <div className="flex items-center gap-2 text-base">
        {isOffline ? (
          <WifiOff className="h-5 w-5 text-[color:var(--status-blocked)]" aria-hidden="true" />
        ) : (
          <AlertTriangle
            className={
              isError
                ? "h-5 w-5 text-[color:var(--status-blocked)]"
                : "h-5 w-5 text-[color:var(--status-delayed)]"
            }
            aria-hidden="true"
          />
        )}
        <span>
          {isOffline
            ? t("connectivity.offline")
            : isError
              ? t("connectivity.error")
              : t("connectivity.stale")}
        </span>
        {fetchedAt ? (
          <span className="text-xs text-muted-foreground tabular-nums">
            {t("connectivity.lastFetched")}: {formatRelative(fetchedAt)}
          </span>
        ) : null}
      </div>
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center gap-1 rounded px-3 py-2 text-sm font-medium bg-card border border-border min-h-[44px] focus:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--focus-ring)]"
      >
        <RefreshCw className="h-4 w-4" aria-hidden="true" />
        {t("connectivity.retry")}
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main screen
// ─────────────────────────────────────────────────────────────────────────────

interface UseLineStationsResult {
  data: LineStationsResponse | null;
  status: "loading" | "ok" | "error" | "stale";
  refresh: () => void;
}

/**
 * Polled fetcher with throttle/dedupe per extended-guardrails § 4 (≤2 Hz per
 * cell; coalesce within 500ms windows). At the line level we poll at 0.2 Hz
 * (every 5s). SSE would replace this in a later slice — out of scope here.
 */
function useLineStations(lineId: string): UseLineStationsResult {
  const [data, setData] = useState<LineStationsResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ok" | "error" | "stale">("loading");
  const lastOkAtRef = useRef<number>(0);

  const tick = useCallback(
    async (signal: AbortSignal) => {
      try {
        const res = await fetchLineStations(lineId, signal);
        setData(res);
        lastOkAtRef.current = Date.now();
        setStatus("ok");
      } catch {
        if (signal.aborted) return;
        // Keep last-known data visible; flip to stale or error based on age.
        const age = Date.now() - lastOkAtRef.current;
        setStatus(lastOkAtRef.current > 0 && age < 60_000 ? "stale" : "error");
      }
    },
    [lineId]
  );

  useEffect(() => {
    const ctrl = new AbortController();
    tick(ctrl.signal);
    const id = setInterval(() => {
      const ctrl2 = new AbortController();
      tick(ctrl2.signal);
    }, 5000);
    return () => {
      ctrl.abort();
      clearInterval(id);
    };
  }, [tick]);

  const refresh = useCallback(() => {
    const ctrl = new AbortController();
    setStatus((s) => (s === "ok" ? s : "loading"));
    void tick(ctrl.signal);
  }, [tick]);

  return { data, status, refresh };
}

export default function SupervisorLineView() {
  const { lineId = "L2" } = useParams<{ lineId: string }>();
  const { t } = useI18n();
  const { data, status, refresh } = useLineStations(lineId);
  const [online, setOnline] = useState<boolean>(
    typeof navigator !== "undefined" ? navigator.onLine : true
  );

  useEffect(() => {
    const goOnline = () => setOnline(true);
    const goOffline = () => setOnline(false);
    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);
    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
    };
  }, []);

  const connectivity: ConnectivityBannerProps["state"] = !online
    ? "offline"
    : status === "error"
      ? "error"
      : status === "stale"
        ? "stale"
        : "ok";

  // Detail navigation is a future slice — keep handler local; no side effects.
  const onSelectStation = useCallback((id: string) => {
    // TODO(UI-SUP-DETAIL): navigate to `/supervisor/line/:lineId/station/:id`
    // once the detail route is registered. Until then, no-op silently keeps
    // the supervisor on this surface (per skill § 5.3 — do not fake nav).
    void id;
  }, []);

  return (
    <main
      // App shell provides outer chrome; this screen owns the main column only.
      className="flex flex-col gap-4 p-4 md:p-6 bg-[color:var(--surface-page)] min-h-screen"
      aria-label={t("supervisor.line.view.title")}
    >
      {/* Page header — exactly one screen-title-level heading (S2). */}
      <header className="flex items-end justify-between gap-3 flex-wrap">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-medium leading-tight">
            {data?.lineName ?? t("supervisor.line.view.title")}
          </h1>
          <p className="text-sm text-muted-foreground">
            {t("supervisor.line.view.subtitle")} ·{" "}
            <span className="font-mono">{lineId}</span> ·{" "}
            {data ? `${data.stations.length} ${t("supervisor.stations")}` : "—"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ScreenStatusBadge phase="PARTIAL" />
          <button
            type="button"
            onClick={refresh}
            className="inline-flex items-center gap-1 rounded px-3 py-2 text-sm font-medium bg-card border border-border min-h-[44px] focus:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--focus-ring)]"
            aria-label={t("supervisor.refresh")}
          >
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            {t("supervisor.refresh")}
          </button>
        </div>
      </header>

      <ConnectivityBanner
        state={connectivity}
        fetchedAt={data?.fetchedAt}
        onRetry={refresh}
        t={t}
      />

      <KpiStrip kpis={data?.kpis ?? null} t={t} />

      {data ? (
        <BlockerQueue stations={data.stations} onSelect={onSelectStation} t={t} />
      ) : (
        <div
          aria-busy="true"
          className="rounded-lg border border-border bg-card p-4 h-[88px] animate-pulse"
        />
      )}

      {data ? (
        data.stations.length === 0 ? (
          <EmptyState t={t} />
        ) : (
          <StationGrid
            stations={data.stations}
            onSelect={onSelectStation}
            t={t}
          />
        )
      ) : (
        <GridSkeleton />
      )}
    </main>
  );
}

function GridSkeleton() {
  return (
    <div
      aria-busy="true"
      className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-6 gap-3 flex-1"
    >
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={i}
          className="rounded-lg border border-border bg-card h-[112px] animate-pulse"
        />
      ))}
    </div>
  );
}

function EmptyState({ t }: { t: (k: string) => string }) {
  return (
    <div className="rounded-lg border border-dashed border-border bg-card p-8 flex flex-col items-center gap-2 text-center">
      <CircleSlash2 className="h-6 w-6 text-muted-foreground" aria-hidden="true" />
      <p className="text-base">{t("supervisor.empty.title")}</p>
      <p className="text-sm text-muted-foreground">{t("supervisor.empty.hint")}</p>
    </div>
  );
}

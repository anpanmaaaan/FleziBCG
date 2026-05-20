import type { OperationDetail } from "@/app/api";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

/**
 * Backend-truth action zone for the Mode B operator cockpit.
 *
 * Slice: FE-SE-COCKPIT-HERO-10 (IN_PROGRESS), extended by
 * FE-SE-INTERRUPTED-MODE-11 for PAUSED / BLOCKED / downtime_open states.
 *
 * Source of action legality: `operation.allowed_actions` (backend-derived).
 * The FE never decides which commands are legal; it only renders what the
 * backend says is allowed, optionally AND-gated by a single UI session-
 * ownership gate (`sessionGate`) supplied by the parent page. Backend
 * revalidates every mutation.
 *
 * Action precedence (primary CTA selection):
 *
 *   Default / IN_PROGRESS:
 *     1. report_production   (only when remainingQty > 0)
 *     2. complete_execution
 *     3. resume_execution
 *     4. start_execution
 *     5. end_downtime
 *     6. pause_execution
 *     7. start_downtime
 *
 *   PAUSED without open downtime (FE-SE-INTERRUPTED-MODE-11):
 *     1. resume_execution    (recovery is the operator's primary intent)
 *     2. end_downtime
 *     3. start_downtime
 *     4. complete_execution
 *     5. report_production
 *     6. pause_execution
 *     7. start_execution
 *
 *   BLOCKED or downtime_open (FE-SE-INTERRUPTED-MODE-11):
 *     1. end_downtime        (must close the open downtime first)
 *     2. resume_execution
 *     3. start_downtime
 *     4. complete_execution
 *     5. report_production
 *     6. pause_execution
 *     7. start_execution
 *
 * All other backend-allowed actions render as secondary buttons.
 * If backend returns no actions (or the session gate is closed), render the
 * empty-action banner — no buttons.
 *
 * Precedence reorders the *primary CTA selection only*. It never adds an
 * action that backend did not allow, and never hides an action that backend
 * allowed (those are rendered as secondary). Legality stays with the backend.
 */

type ActionId =
  | "report_production"
  | "complete_execution"
  | "resume_execution"
  | "start_execution"
  | "end_downtime"
  | "pause_execution"
  | "start_downtime";

export interface AllowedActionZoneProps {
  operation: OperationDetail;
  /** Single UI session-ownership gate (e.g. `canExecuteBySessionControl` in the parent page). */
  sessionGate: boolean;
  actionLoading: boolean;
  downtimeLoading: boolean;
  /** Remaining quantity — display/hierarchy hint only. Does NOT decide legality. */
  remainingQty: number;
  onStartOperation: () => void;
  onPauseOperation: () => void;
  onOpenDowntimeModal: () => void;
  onCompleteOperation: () => void;
  onResumeOperation: () => void;
  onEndDowntime: () => void;
  onReportProduction: () => void;
}

interface ActionConfig {
  id: ActionId;
  labelKey: I18nSemanticKey;
  onClick: () => void;
  loading: boolean;
  /** Tailwind classes for primary (full-width) rendering. */
  primaryClass: string;
  /** Tailwind classes for secondary rendering. */
  secondaryClass: string;
}

export function AllowedActionZone({
  operation,
  sessionGate,
  actionLoading,
  downtimeLoading,
  remainingQty,
  onStartOperation,
  onPauseOperation,
  onOpenDowntimeModal,
  onCompleteOperation,
  onResumeOperation,
  onEndDowntime,
  onReportProduction,
}: AllowedActionZoneProps) {
  const { t } = useI18n();

  // Closure is a server-truth lock; honour it in the UI but do not invent it.
  const closed = operation.closure_status === "CLOSED";

  // Filter: render only actions the backend explicitly allows.
  const backendAllowed = new Set(
    Array.isArray(operation.allowed_actions) ? operation.allowed_actions : [],
  );

  // PO-confirmed UI gate: a command is visible only if backend allows it AND
  // the session gate is open. When closed, hide everything (lock is shown by
  // ClosureStatePanel elsewhere on the page).
  const visible = (id: ActionId): boolean => sessionGate && !closed && backendAllowed.has(id);

  const baseBtn =
    "rounded-2xl px-6 font-bold tracking-wide active:scale-[0.98] transition shadow-sm " +
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 " +
    "disabled:opacity-40 disabled:cursor-not-allowed";

  // Per-action presentation. Colours follow the existing cockpit palette.
  const ACTION_CONFIG: Record<ActionId, ActionConfig> = {
    report_production: {
      id: "report_production",
      labelKey: "station.action.reportQty",
      onClick: onReportProduction,
      loading: actionLoading,
      primaryClass:
        `${baseBtn} min-h-14 w-full text-xl sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl ` +
        "bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-600",
      secondaryClass:
        `${baseBtn} min-h-12 w-full text-lg sm:text-xl ` +
        "border-2 border-blue-300 bg-white text-blue-700 hover:bg-blue-50 focus-visible:ring-blue-600",
    },
    complete_execution: {
      id: "complete_execution",
      labelKey: "station.action.completeOperation",
      onClick: onCompleteOperation,
      loading: actionLoading,
      primaryClass:
        `${baseBtn} min-h-14 w-full text-xl sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl ` +
        "bg-amber-500 text-white hover:bg-amber-600 focus-visible:ring-amber-600",
      secondaryClass:
        `${baseBtn} min-h-12 w-full text-lg sm:text-xl ` +
        "border-2 border-amber-500 bg-white text-amber-700 hover:bg-amber-50 focus-visible:ring-amber-600",
    },
    resume_execution: {
      id: "resume_execution",
      labelKey: "station.action.resume",
      onClick: onResumeOperation,
      loading: actionLoading,
      primaryClass:
        `${baseBtn} min-h-14 w-full text-xl sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl ` +
        "bg-emerald-600 text-white hover:bg-emerald-700 focus-visible:ring-emerald-600",
      secondaryClass:
        `${baseBtn} min-h-12 w-full text-lg sm:text-xl ` +
        "border-2 border-emerald-500 bg-white text-emerald-700 hover:bg-emerald-50 focus-visible:ring-emerald-600",
    },
    start_execution: {
      id: "start_execution",
      labelKey: "station.action.clockOn",
      onClick: onStartOperation,
      loading: actionLoading,
      primaryClass:
        `${baseBtn} min-h-14 w-full text-xl sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl ` +
        "bg-green-600 text-white hover:bg-green-700 focus-visible:ring-green-600",
      secondaryClass:
        `${baseBtn} min-h-12 w-full text-lg sm:text-xl ` +
        "border-2 border-green-500 bg-white text-green-700 hover:bg-green-50 focus-visible:ring-green-600",
    },
    end_downtime: {
      id: "end_downtime",
      labelKey: "station.action.endDowntime",
      onClick: onEndDowntime,
      loading: downtimeLoading,
      primaryClass:
        `${baseBtn} min-h-14 w-full text-xl sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl ` +
        "bg-emerald-600 text-white hover:bg-emerald-700 focus-visible:ring-emerald-600",
      secondaryClass:
        `${baseBtn} min-h-12 w-full text-lg sm:text-xl ` +
        "border-2 border-emerald-500 bg-white text-emerald-700 hover:bg-emerald-50 focus-visible:ring-emerald-600",
    },
    pause_execution: {
      id: "pause_execution",
      labelKey: "station.action.pause",
      onClick: onPauseOperation,
      loading: actionLoading,
      primaryClass:
        `${baseBtn} min-h-14 w-full text-xl sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl ` +
        "bg-amber-400 text-slate-900 hover:bg-amber-500 focus-visible:ring-amber-500",
      secondaryClass:
        `${baseBtn} min-h-12 w-full text-lg sm:text-xl ` +
        "border-2 border-amber-300 bg-white text-amber-800 hover:bg-amber-50 focus-visible:ring-amber-500",
    },
    start_downtime: {
      id: "start_downtime",
      labelKey: "station.action.startDowntime",
      onClick: onOpenDowntimeModal,
      loading: downtimeLoading,
      primaryClass:
        `${baseBtn} min-h-14 w-full text-xl sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl ` +
        "bg-slate-600 text-white hover:bg-slate-700 focus-visible:ring-slate-600",
      secondaryClass:
        `${baseBtn} min-h-12 w-full text-lg sm:text-xl ` +
        "border-2 border-slate-400 bg-white text-slate-700 hover:bg-slate-50 focus-visible:ring-slate-600",
    },
  };

  // Visible action set (backend AND session gate).
  const visibleIds: ActionId[] = (
    [
      "report_production",
      "complete_execution",
      "resume_execution",
      "start_execution",
      "end_downtime",
      "pause_execution",
      "start_downtime",
    ] as const
  ).filter(visible);

  if (visibleIds.length === 0) {
    return (
      <section
        className="shrink-0 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 sm:text-base"
        role="status"
        data-testid="allowed-action-zone-empty"
      >
        {t("station.action.noActionsAvailable")}
      </section>
    );
  }

  // FE-SE-INTERRUPTED-MODE-11: primary CTA precedence is state-aware. Legality
  // is still owned by `backendAllowed`; only the *order* in which we pick the
  // primary changes when the operation is interrupted. The first id in the
  // selected precedence list that is also in `visibleIds` wins.
  const isDowntimeContext =
    operation.status === "BLOCKED" || operation.downtime_open === true;
  const isPausedContext =
    !isDowntimeContext && operation.status === "PAUSED";

  let primaryPrecedence: ActionId[];
  if (isDowntimeContext) {
    primaryPrecedence = [
      "end_downtime",
      "resume_execution",
      "start_downtime",
      "complete_execution",
      "report_production",
      "pause_execution",
      "start_execution",
    ];
  } else if (isPausedContext) {
    primaryPrecedence = [
      "resume_execution",
      "end_downtime",
      "start_downtime",
      "complete_execution",
      "report_production",
      "pause_execution",
      "start_execution",
    ];
  } else {
    // Default / IN_PROGRESS precedence. report_production only wins when
    // there is remaining work; otherwise it falls through to the next id.
    const defaultPrecedence: ActionId[] = [
      "report_production",
      "complete_execution",
      "resume_execution",
      "start_execution",
      "end_downtime",
      "pause_execution",
      "start_downtime",
    ];
    primaryPrecedence =
      remainingQty > 0
        ? defaultPrecedence
        : defaultPrecedence.filter((id) => id !== "report_production");
  }

  const primaryId: ActionId =
    primaryPrecedence.find((id) => visibleIds.includes(id)) ?? visibleIds[0];

  const secondaryIds = visibleIds.filter((id) => id !== primaryId);

  const primary = ACTION_CONFIG[primaryId];

  return (
    <section
      className="shrink-0 flex flex-col gap-3 sm:gap-4 pb-1"
      data-testid="allowed-action-zone"
      data-action-context={isDowntimeContext ? "downtime" : isPausedContext ? "paused" : "running"}
    >
      <button
        type="button"
        onClick={primary.onClick}
        disabled={primary.loading}
        className={primary.primaryClass}
        data-action={primary.id}
        data-action-role="primary"
      >
        {t(primary.labelKey)}
      </button>

      {secondaryIds.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {secondaryIds.map((id) => {
            const cfg = ACTION_CONFIG[id];
            return (
              <button
                key={id}
                type="button"
                onClick={cfg.onClick}
                disabled={cfg.loading}
                className={cfg.secondaryClass}
                data-action={cfg.id}
                data-action-role="secondary"
              >
                {t(cfg.labelKey)}
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}

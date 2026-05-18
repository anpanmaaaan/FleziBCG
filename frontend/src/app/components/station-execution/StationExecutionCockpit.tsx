import { useState } from "react";
import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

interface StationExecutionCockpitProps {
  /** Compact context strip values -- derived from session ownership state. */
  stationScope: string;
  sessionId?: string | null;
  operatorUserId?: string | null;
  /**
   * Collapsed support disclosure below the scrollable body.
   * Use this for the StationEntryHandoff summary and any developer-facing
   * diagnostics that are not part of the normal operator workflow.
   */
  supportDetails?: ReactNode;
  /** Main execution body -- scrollable. */
  children: ReactNode;
}

/**
 * Layout wrapper for the Mode B operator execution cockpit.
 *
 * Provides:
 * 1. A compact one-line context strip (station / session / operator).
 * 2. A scrollable execution body (children) with consistent padding.
 * 3. A "Support details" collapsed disclosure for diagnostics and entry context.
 *
 * Presentation-only. No backend calls or action logic.
 * All execution state, allowed actions, and session truth are owned by the
 * parent page and passed via children and the context strip props.
 *
 * Note: equipment_id is not present in SessionOwnershipSummary (backend schema).
 * It is available on StationSessionItem via the /sessions/current endpoint
 * if a future slice needs to display it.
 */
export function StationExecutionCockpit({
  stationScope,
  sessionId,
  operatorUserId,
  supportDetails,
  children,
}: StationExecutionCockpitProps) {
  const { t } = useI18n();
  const [supportOpen, setSupportOpen] = useState(false);

  return (
    <div className="flex-1 min-h-0 flex flex-col overflow-hidden" data-testid="station-execution-cockpit">
      {/* Compact context strip */}
      <div className="shrink-0 flex flex-wrap items-center gap-x-5 gap-y-1 border-b border-slate-100 bg-white px-3 py-2 text-xs sm:px-4" data-testid="cockpit-context-strip">
        <span className="flex items-center gap-1.5">
          <span className="text-slate-400">
            {t("station.workflow.context.station" as I18nSemanticKey)}
          </span>
          <span className="font-semibold text-slate-700">{stationScope}</span>
        </span>

        <span className="flex items-center gap-1.5">
          <span className="text-slate-400">
            {t("station.workflow.context.session" as I18nSemanticKey)}
          </span>
          {sessionId ? (
            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700">
              {t("station.ownership.ownedBadge" as I18nSemanticKey)}
            </span>
          ) : (
            <span className="text-slate-400">
              {t("station.workflow.value.notSelected" as I18nSemanticKey)}
            </span>
          )}
        </span>

        <span className="flex items-center gap-1.5">
          <span className="text-slate-400">
            {t("station.workflow.context.operator" as I18nSemanticKey)}
          </span>
          <span
            className={`font-semibold ${operatorUserId ? "text-slate-700" : "text-slate-400"}`}
          >
            {operatorUserId ?? t("station.workflow.value.notIdentified" as I18nSemanticKey)}
          </span>
        </span>

      </div>

      {/* Scrollable execution body */}
      <div className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden overscroll-contain bg-slate-50 p-3 sm:p-4 flex flex-col gap-3 sm:gap-4">
        {children}

        {/* Support details -- collapsed by default */}
        {supportDetails && (
          <div className="mt-1 border-t border-slate-100 pt-2">
            <button
              type="button"
              onClick={() => setSupportOpen((prev) => !prev)}
              className="flex items-center gap-1 text-xs text-slate-400 transition hover:text-slate-600 select-none"
              aria-expanded={supportOpen}
            >
              <ChevronDown
                className={`h-3.5 w-3.5 transition-transform duration-150 ${supportOpen ? "rotate-180" : ""}`}
                aria-hidden="true"
              />
              {t("station.cockpit.supportDetails" as I18nSemanticKey)}
            </button>
            {supportOpen && <div className="mt-3">{supportDetails}</div>}
          </div>
        )}
      </div>
    </div>
  );
}

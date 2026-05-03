import { ArrowLeft, ChevronDown, RefreshCw } from "lucide-react";
import { StatusBadge } from "@/app/components";
import {
  mapExecutionStatusBadgeVariant,
  mapExecutionStatusText,
  type OperationClosureStatus,
  type OperationExecutionStatus,
} from "@/app/api";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";
import { DowntimeStatusPanel } from "./DowntimeStatusPanel";

export interface StationExecutionHeaderProps {
  stationScope: string;
  operationName: string;
  operationStatus: OperationExecutionStatus;
  closureStatus: OperationClosureStatus;
  downtimeOpen: boolean;
  /** True while the queue refresh API call is in-flight. Disables refresh button. */
  queueLoading: boolean;
  /** Navigate back to Mode A (operation selection). */
  onBackToSelection: () => void;
  /** Trigger a queue + operation refresh. */
  onRefresh: () => void;
  /** Toggle the queue overlay open/closed. */
  onToggleQueue: () => void;
}

/**
 * Mode B execution cockpit header.
 *
 * Renders station scope, operation identity, status badges, and navigation /
 * control buttons. All data is passed as props — no data fetching inside this
 * component. Execution action legality is backend-derived by the parent and
 * passed in as `canExecute` (ownership/session-derived).
 */
export function StationExecutionHeader({
  stationScope,
  operationName,
  operationStatus,
  closureStatus,
  downtimeOpen,
  queueLoading,
  onBackToSelection,
  onRefresh,
  onToggleQueue,
}: StationExecutionHeaderProps) {
  const { t } = useI18n();

  const statusLabel = t(mapExecutionStatusText(operationStatus) as I18nSemanticKey);

  return (
    <div className="flex flex-col gap-3 px-3 py-3 bg-white border-b shadow-sm shrink-0 sm:px-4 lg:flex-row lg:items-center lg:justify-between">
      {/* Context row: station / operation name / status badges */}
      <div className="flex min-w-0 flex-wrap items-center gap-2 sm:gap-3">
        <span className="text-sm text-gray-500 shrink-0 whitespace-nowrap">
          {t("station.workstation.label")} {stationScope}
        </span>
        <span className="shrink-0 h-5 w-px bg-gray-300" aria-hidden="true" />
        <span className="font-bold text-base text-gray-900 truncate">{operationName}</span>
        <StatusBadge
          variant={mapExecutionStatusBadgeVariant(operationStatus)}
          size="sm"
        >
          {statusLabel}
        </StatusBadge>
        {closureStatus === "CLOSED" && (
          <span className="shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-900 text-white text-xs font-semibold">
            {t("station.closure.closedBadge")}
          </span>
        )}
        <DowntimeStatusPanel downtimeOpen={downtimeOpen} />
      </div>

      {/* Control row: ownership badge + nav/view controls + release command */}
      <div className="flex w-full flex-wrap items-center gap-2 sm:gap-3 shrink-0 lg:w-auto lg:flex-nowrap lg:justify-end">
        {/* Ownership indicator (H2+: session ownership) */}
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-green-100 text-green-800 text-sm font-semibold order-first sm:order-none">
          {t("station.ownership.ownedBadge")}
        </span>

        {/* Nav / view controls */}
        <button
          onClick={onBackToSelection}
          className="h-10 sm:h-11 px-3 sm:px-4 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 active:scale-95 transition flex items-center gap-1.5"
        >
          <ArrowLeft className="w-4 h-4 shrink-0" />
          {t("station.action.backToSelection")}
        </button>
        <button
          onClick={onRefresh}
          disabled={queueLoading}
          className="h-10 sm:h-11 px-3 sm:px-4 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 active:scale-95 transition disabled:opacity-50 flex items-center gap-1.5"
        >
          <RefreshCw className="w-4 h-4 shrink-0" />
          {t("station.action.refresh")}
        </button>
        <button
          onClick={onToggleQueue}
          className="h-10 sm:h-11 px-3 sm:px-4 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 active:scale-95 transition flex items-center gap-1.5"
        >
          {t("station.tab.queue")}
          <ChevronDown className="w-4 h-4 shrink-0" />
        </button>

      </div>
    </div>
  );
}

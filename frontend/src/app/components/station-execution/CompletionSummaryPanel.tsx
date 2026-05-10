import { StatusBadge } from "@/app/components";
import {
  mapExecutionStatusBadgeVariant,
  mapExecutionStatusText,
  type OperationDetail,
} from "@/app/api";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";
import { DowntimeStatusPanel } from "./DowntimeStatusPanel";

interface CompletionSummaryPanelProps {
  operation: OperationDetail;
  queuedWorkCount: number;
  downtimeTotalLabel: string;
  onReturnToQueue: () => void;
  onGoToStationSession: () => void;
}

export function CompletionSummaryPanel({
  operation,
  queuedWorkCount,
  downtimeTotalLabel,
  onReturnToQueue,
  onGoToStationSession,
}: CompletionSummaryPanelProps) {
  const { t } = useI18n();
  const hasQueuedWork = queuedWorkCount > 0;

  return (
    <section className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm sm:p-5 md:p-6 shrink-0">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-base font-semibold uppercase tracking-wide text-slate-500 md:text-lg">
            {t("station.completion.summaryTitle")}
          </p>
          <p className="mt-2 truncate text-lg font-semibold text-slate-900 sm:text-xl">
            {operation.name}
          </p>
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-600">
            <span>
              <span className="text-slate-500">{t("station.context.workOrder")}:</span>{" "}
              <span className="font-medium text-slate-900">{operation.work_order_number}</span>
            </span>
            <span>
              <span className="text-slate-500">{t("station.context.productionOrder")}:</span>{" "}
              <span className="font-medium text-slate-900">{operation.production_order_number}</span>
            </span>
            <span>
              <span className="text-slate-500">#{operation.operation_number}</span>
            </span>
          </div>
        </div>

        <StatusBadge variant={mapExecutionStatusBadgeVariant(operation.status)}>
          {t(mapExecutionStatusText(operation.status) as I18nSemanticKey)}
        </StatusBadge>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            {t("station.qty.completed")}
          </p>
          <p className="mt-2 text-2xl font-bold text-slate-900">{operation.completed_qty}</p>
        </div>
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">
            {t("station.qty.totalGood")}
          </p>
          <p className="mt-2 text-2xl font-bold text-emerald-800">{operation.good_qty}</p>
        </div>
        <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-amber-700">
            {t("station.qty.totalScrap")}
          </p>
          <p className="mt-2 text-2xl font-bold text-amber-800">{operation.scrap_qty}</p>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3 text-sm text-slate-600">
        <span>
          <span className="text-slate-500">{t("station.timer.downtimeTotal")}</span>: {downtimeTotalLabel}
        </span>
        {operation.downtime_open ? <DowntimeStatusPanel downtimeOpen={operation.downtime_open} /> : null}
      </div>

      <div className="mt-5 rounded-2xl border border-blue-200 bg-blue-50 px-4 py-4 sm:px-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-700">
          {t("station.completion.nextStepLabel")}
        </p>
        <p className="mt-2 text-sm leading-snug text-blue-950 sm:text-base">
          {t(hasQueuedWork ? "station.completion.nextStepQueue" : "station.completion.nextStepEndSession")}
        </p>
        <p className="mt-2 text-xs text-blue-800">{t("station.completion.sessionCloseGuardHint")}</p>
        {operation.closure_status === "OPEN" ? (
          <p className="mt-2 text-xs text-blue-800">{t("station.completion.supervisorReviewHint")}</p>
        ) : null}
        <p className="mt-2 text-xs text-blue-800">{t("station.completion.reviewCurrentHint")}</p>

        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={onReturnToQueue}
            className={`min-h-10 rounded-lg px-3 text-sm font-medium transition active:scale-95 ${
              hasQueuedWork
                ? "border border-blue-600 bg-blue-600 text-white hover:bg-blue-700"
                : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
            }`}
          >
            {t("station.supportQueue.viewFullQueue")}
          </button>
          <button
            type="button"
            onClick={onGoToStationSession}
            className={`min-h-10 rounded-lg px-3 text-sm font-medium transition active:scale-95 ${
              hasQueuedWork
                ? "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                : "border border-blue-600 bg-blue-600 text-white hover:bg-blue-700"
            }`}
          >
            {t("station.completion.endSessionCta")}
          </button>
        </div>
      </div>
    </section>
  );
}
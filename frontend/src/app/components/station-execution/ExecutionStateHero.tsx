import type { OperationDetail } from "@/app/api";
import { useI18n } from "@/app/i18n";
import { QuantitySummaryPanel } from "./QuantitySummaryPanel";

export interface ExecutionStateHeroProps {
  operation: OperationDetail;
  remainingQty: number;
  targetTimeLabel: string;
  elapsedLabel: string;
  overByLabel: string | null;
  pausedTotalLabel: string;
  downtimeTotalLabel: string;
}

export function ExecutionStateHero({
  operation,
  remainingQty,
  targetTimeLabel,
  elapsedLabel,
  overByLabel,
  pausedTotalLabel,
  downtimeTotalLabel,
}: ExecutionStateHeroProps) {
  const { t } = useI18n();

  return (
    <section className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm sm:p-5 md:p-6 shrink-0">
      <div className="mb-4 border-b border-slate-200 pb-4">
        <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm sm:text-base md:text-xl">
          <span className="whitespace-nowrap">
            <span className="text-slate-500">{t("station.context.workOrder")}:</span>{" "}
            <span className="font-semibold text-slate-900">{operation.work_order_number}</span>
          </span>
          <span className="whitespace-nowrap">
            <span className="text-slate-500">{t("station.context.productionOrder")}:</span>{" "}
            <span className="font-semibold text-slate-900">{operation.production_order_number}</span>
          </span>
          <span className="whitespace-nowrap">
            <span className="text-slate-500">{t("station.context.startedAt")}:</span>{" "}
            <span className="font-semibold text-slate-900">
              {operation.actual_start
                ? new Date(operation.actual_start).toLocaleString()
                : t("station.context.notStarted")}
            </span>
          </span>
        </div>
      </div>

      <QuantitySummaryPanel
        quantity={operation.quantity}
        completedQty={operation.completed_qty}
        remainingQty={remainingQty}
        targetTimeLabel={targetTimeLabel}
        elapsedLabel={elapsedLabel}
        overByLabel={overByLabel}
        goodQty={operation.good_qty}
        scrapQty={operation.scrap_qty}
        showPausedTotals={operation.status === "PAUSED" || operation.status === "BLOCKED"}
        pausedTotalLabel={pausedTotalLabel}
        downtimeTotalLabel={downtimeTotalLabel}
      />

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div className={`rounded-2xl border px-4 py-3 ${operation.closure_status === "CLOSED" ? "border-slate-300 bg-slate-100" : "border-slate-200 bg-slate-50"}`}>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t("station.closure.sectionTitle")}</p>
          <p className="mt-1 text-sm font-semibold text-slate-900">{t(operation.closure_status === "CLOSED" ? "station.closure.closedState" : "station.closure.openState")}</p>
          <p className="mt-1 text-xs text-slate-600">
            {t(operation.closure_status === "CLOSED" ? "station.closed.executionBlocked" : "station.closure.openHelper")}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t("station.reopen.audit.title")}</p>
          <p className="mt-1 text-sm text-slate-900">
            {t("station.reopen.audit.count", { count: operation.reopen_count ?? 0 })}
          </p>
          {operation.last_closed_at && (
            <p className="mt-1 text-xs text-slate-600">
              {t("station.reopen.audit.lastClosed", {
                at: new Date(operation.last_closed_at).toLocaleString(),
                by: operation.last_closed_by ?? "-",
              })}
            </p>
          )}
          {operation.last_reopened_at && (
            <p className="mt-1 text-xs text-slate-600">
              {t("station.reopen.audit.lastReopened", {
                at: new Date(operation.last_reopened_at).toLocaleString(),
                by: operation.last_reopened_by ?? "-",
              })}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
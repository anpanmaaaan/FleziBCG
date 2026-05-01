import { useI18n } from "@/app/i18n";

function KpiCard({ label, value, highlight = false }: { label: string; value: string | number; highlight?: boolean }) {
  return (
    <div className={`rounded-2xl border p-4 text-center md:p-5 ${highlight ? "border-blue-200 bg-blue-50/50 ring-2 ring-blue-100" : "border-slate-200 bg-white"}`}>
      <div className={`text-base font-medium sm:text-lg md:text-xl ${highlight ? "text-blue-700" : "text-slate-700"}`}>{label}</div>
      <div className={`mt-3 text-3xl leading-none sm:text-4xl md:text-5xl lg:text-6xl ${highlight ? "font-bold text-blue-700" : "font-bold text-slate-900"}`}>
        {value}
      </div>
    </div>
  );
}

function TimeCluster({
  targetTime,
  elapsed,
  overBy,
}: {
  targetTime: string;
  elapsed: string;
  overBy?: string | null;
}) {
  const { t } = useI18n();

  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 md:p-5">
      <div className="grid grid-cols-2 gap-3 sm:gap-5">
        <div>
          <div className="text-sm font-medium text-slate-600 sm:text-base md:text-lg">{t("station.timer.targetTime")}</div>
          <div className="mt-2 text-2xl font-semibold text-slate-900 sm:text-3xl md:text-4xl">{targetTime}</div>
        </div>
        <div>
          <div className="text-sm font-medium text-slate-600 sm:text-base md:text-lg">{t("station.timer.elapsed")}</div>
          <div className="mt-2 text-2xl font-semibold text-slate-900 sm:text-3xl md:text-4xl">{elapsed}</div>
          {overBy ? <div className="mt-2 text-xs font-medium text-amber-600 sm:text-sm md:text-base">{t("station.timer.overBy", { duration: overBy })}</div> : null}
        </div>
      </div>
    </div>
  );
}

export interface QuantitySummaryPanelProps {
  quantity: number;
  completedQty: number;
  remainingQty: number;
  targetTimeLabel: string;
  elapsedLabel: string;
  overByLabel: string | null;
  goodQty: number;
  scrapQty: number;
  showPausedTotals: boolean;
  pausedTotalLabel: string;
  downtimeTotalLabel: string;
}

export function QuantitySummaryPanel({
  quantity,
  completedQty,
  remainingQty,
  targetTimeLabel,
  elapsedLabel,
  overByLabel,
  goodQty,
  scrapQty,
  showPausedTotals,
  pausedTotalLabel,
  downtimeTotalLabel,
}: QuantitySummaryPanelProps) {
  const { t } = useI18n();

  return (
    <>
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-[1fr_1fr_1fr_minmax(280px,360px)]">
        <KpiCard label={t("station.qty.target")} value={quantity} />
        <KpiCard label={t("station.qty.completed")} value={completedQty} />
        <KpiCard label={t("station.qty.remaining")} value={remainingQty} highlight />
        <TimeCluster targetTime={targetTimeLabel} elapsed={elapsedLabel} overBy={overByLabel} />
      </div>

      <div className="mt-4 flex flex-wrap gap-x-4 sm:gap-x-8 gap-y-2 text-sm sm:text-base md:text-xl text-slate-700">
        <span><span className="text-slate-500">{t("station.qty.totalGood")}</span>: <span className="font-semibold text-emerald-700">{goodQty}</span></span>
        <span><span className="text-slate-500">{t("station.qty.totalScrap")}</span>: <span className="font-semibold text-rose-600">{scrapQty}</span></span>
        {showPausedTotals && (
          <span>
            <span className="text-slate-500">{t("station.timer.pausedTotal")}</span>: {pausedTotalLabel}
          </span>
        )}
        {showPausedTotals && (
          <span>
            <span className="text-slate-500">{t("station.timer.downtimeTotal")}</span>: {downtimeTotalLabel}
          </span>
        )}
      </div>
    </>
  );
}
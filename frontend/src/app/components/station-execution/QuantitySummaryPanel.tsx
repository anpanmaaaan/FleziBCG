import { useI18n } from "@/app/i18n";

function KpiCard({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: string | number;
  tone?: "neutral" | "primary" | "good" | "scrap";
}) {
  const wrapClass =
    tone === "primary"
      ? "border-blue-200 bg-blue-50/50 ring-2 ring-blue-100"
      : tone === "good"
      ? "border-emerald-200 bg-emerald-50/60"
      : tone === "scrap"
      ? "border-rose-200 bg-rose-50/60"
      : "border-slate-200 bg-white";
  const labelClass =
    tone === "primary"
      ? "text-blue-700"
      : tone === "good"
      ? "text-emerald-700"
      : tone === "scrap"
      ? "text-rose-600"
      : "text-slate-700";
  const valueClass =
    tone === "primary"
      ? "font-bold text-blue-700"
      : tone === "good"
      ? "font-bold text-emerald-700"
      : tone === "scrap"
      ? "font-bold text-rose-600"
      : "font-bold text-slate-900";
  return (
    <div className={`rounded-2xl border p-4 text-center md:p-5 ${wrapClass}`}>
      <div className={`text-base font-medium sm:text-lg md:text-xl ${labelClass}`}>{label}</div>
      <div className={`mt-3 text-3xl leading-none sm:text-4xl md:text-5xl lg:text-6xl ${valueClass}`}>
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
      {/* Primary KPI row: Target, Remaining, Good, Scrap */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-4">
        <KpiCard label={t("station.qty.target")} value={quantity} />
        <KpiCard label={t("station.qty.remaining")} value={remainingQty} tone="primary" />
        <KpiCard label={t("station.qty.totalGood")} value={goodQty} tone="good" />
        <KpiCard label={t("station.qty.totalScrap")} value={scrapQty} tone="scrap" />
      </div>

      {/* Time row + completed qty */}
      <div className="mt-3 grid grid-cols-1 gap-3 sm:gap-4 lg:grid-cols-[1fr_minmax(280px,360px)]">
        <KpiCard label={t("station.qty.completed")} value={completedQty} />
        <TimeCluster targetTime={targetTimeLabel} elapsed={elapsedLabel} overBy={overByLabel} />
      </div>

      {/* Interruption totals -- only when relevant */}
      {showPausedTotals && (
        <div className="mt-3 flex flex-wrap gap-x-4 sm:gap-x-8 gap-y-2 text-sm sm:text-base text-slate-700">
          <span>
            <span className="text-slate-500">{t("station.timer.pausedTotal")}</span>:{" "}
            {pausedTotalLabel}
          </span>
          <span>
            <span className="text-slate-500">{t("station.timer.downtimeTotal")}</span>:{" "}
            {downtimeTotalLabel}
          </span>
        </div>
      )}
    </>
  );
}
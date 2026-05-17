import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

interface IdentifyOperatorPanelProps {
  operatorUserId: string | null;
  sessionOpen: boolean;
  onIdentifyOperator: () => void;
}

export function IdentifyOperatorPanel({
  operatorUserId,
  sessionOpen,
  onIdentifyOperator,
}: IdentifyOperatorPanelProps) {
  const { t } = useI18n();
  const identified = Boolean(operatorUserId);
  const statusClass = !sessionOpen
    ? "bg-slate-50 text-slate-600"
    : identified
    ? "bg-emerald-50 text-emerald-800"
    : "bg-amber-50 text-amber-900";
  const statusSymbol = !sessionOpen ? "○" : identified ? "●" : "○";
  const statusKey = !sessionOpen
    ? ("stationSession.row.status.notConfirmed" as I18nSemanticKey)
    : identified
    ? ("stationSession.row.status.identified" as I18nSemanticKey)
    : ("stationSession.row.status.notYet" as I18nSemanticKey);
  const subtextKey = !sessionOpen
    ? ("stationSession.row.operator.subtext.sessionFirst" as I18nSemanticKey)
    : identified
    ? ("stationSession.row.operator.subtext.identified" as I18nSemanticKey)
    : ("stationSession.row.operator.subtext.missing" as I18nSemanticKey);

  return (
    <div className="flex items-center gap-3 border-t border-slate-200 p-4 sm:p-5">
      <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${identified ? "bg-emerald-50 text-emerald-900" : sessionOpen ? "bg-slate-100 text-slate-700" : "bg-slate-50 text-slate-400"}`}>
        2
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-900">
            {t("stationSession.row.operator.title" as I18nSemanticKey)}
          </h2>
          <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${statusClass}`}>
            <span aria-hidden="true">{statusSymbol}</span>
            <span>{t(statusKey)}</span>
          </span>
        </div>
        <p className="mt-1 truncate text-xs text-slate-600">
          {subtextKey === "stationSession.row.operator.subtext.identified"
            ? t(subtextKey, { operatorId: operatorUserId ?? "-" })
            : t(subtextKey)}
        </p>
      </div>

      {sessionOpen && !identified ? (
        <button
          type="button"
          onClick={onIdentifyOperator}
          className="min-h-11 shrink-0 rounded-lg border border-blue-600 bg-blue-600 px-3 text-sm font-semibold text-white transition hover:bg-blue-700 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
        >
          {t("stationSession.row.operator.action.identify" as I18nSemanticKey)}
        </button>
      ) : null}
    </div>
  );
}

import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

// Per FE-SE-MODEA-SIMPLIFY-09 IR-03:
// Renders as an inline row inside the parent 3-row card (a <div>, not its own <section>).
// Drops the User icon, the section border, and the standalone hint paragraph.
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

  const identified = sessionOpen && Boolean(operatorUserId);
  const needsAction = sessionOpen && !operatorUserId;

  const statusClass = identified
    ? "bg-emerald-50 text-emerald-800"
    : needsAction
    ? "bg-amber-50 text-amber-900"
    : "bg-slate-100 text-slate-700";
  const statusSymbol = identified ? "●" : needsAction ? "○" : "○";
  const statusKey: I18nSemanticKey = identified
    ? ("stationSession.row.status.identified" as I18nSemanticKey)
    : needsAction
    ? ("stationSession.row.status.notYet" as I18nSemanticKey)
    : ("stationSession.row.status.notConfirmed" as I18nSemanticKey);

  const subtext = identified && operatorUserId
    ? t("stationSession.row.operator.subtext.identified" as I18nSemanticKey, {
        operatorId: operatorUserId,
      })
    : sessionOpen
    ? t("stationSession.row.operator.subtext.missing" as I18nSemanticKey)
    : t("stationSession.row.operator.subtext.sessionFirst" as I18nSemanticKey);

  return (
    <div className="flex items-center gap-3 p-4 sm:p-5">
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
          identified ? "bg-emerald-50 text-emerald-900" : "bg-slate-100 text-slate-700"
        }`}
        aria-hidden="true"
      >
        2
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-900">
            {t("stationSession.row.operator.title" as I18nSemanticKey)}
          </h2>
          <span
            className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${statusClass}`}
          >
            <span aria-hidden="true">{statusSymbol}</span>
            <span>{t(statusKey)}</span>
          </span>
        </div>
        <p className="mt-1 text-xs text-slate-600">{subtext}</p>
      </div>
      {needsAction ? (
        <button
          type="button"
          onClick={onIdentifyOperator}
          className="min-h-11 shrink-0 rounded-lg border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
        >
          {t("stationSession.row.operator.action.identify" as I18nSemanticKey)}
        </button>
      ) : null}
    </div>
  );
}

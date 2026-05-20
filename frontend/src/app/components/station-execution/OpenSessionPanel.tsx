import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

// Per FE-SE-MODEA-SIMPLIFY-09 IR-02:
// - `stationId` and `commandError` removed from props (parent owns banner; navigation guarded upstream).
// - `onEndSessionClick` added so the Session row only TRIGGERS close intent.
//   Close lifecycle (dialog, closing state, stationApi.closeSession call) is owned by
//   <CloseSessionPanel /> rendered as a sibling of the 3-row card.
interface OpenSessionPanelProps {
  sessionId: string | null;
  openedAt: string | null;
  isOpen: boolean;
  loading: boolean;
  opening: boolean;
  onOpenSession: () => void;
  onEndSessionClick: () => void;
}

export function OpenSessionPanel({
  sessionId,
  openedAt,
  isOpen,
  loading,
  opening,
  onOpenSession,
  onEndSessionClick,
}: OpenSessionPanelProps) {
  const { t } = useI18n();

  const statusClass = isOpen
    ? "bg-emerald-50 text-emerald-800"
    : "bg-amber-50 text-amber-900";
  const statusSymbol = isOpen ? "●" : "○";
  const statusKey = isOpen
    ? ("stationSession.row.status.open" as I18nSemanticKey)
    : ("stationSession.row.status.notYet" as I18nSemanticKey);
  const subtext =
    isOpen && sessionId
      ? t("stationSession.row.session.subtext.open" as I18nSemanticKey, {
          sessionId,
          openedAt: openedAt ? new Date(openedAt).toLocaleString() : "-",
        })
      : t("stationSession.row.session.subtext.missing" as I18nSemanticKey);

  return (
    <div className="flex items-center gap-3 p-4 sm:p-5">
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
          isOpen ? "bg-emerald-50 text-emerald-900" : "bg-slate-100 text-slate-700"
        }`}
        aria-hidden="true"
      >
        1
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-900">
            {t("stationSession.row.session.title" as I18nSemanticKey)}
          </h2>
          <span
            className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${statusClass}`}
          >
            <span aria-hidden="true">{statusSymbol}</span>
            <span>{t(statusKey)}</span>
          </span>
        </div>
        <p className="mt-1 text-xs text-slate-600">
          {loading
            ? t("stationSession.label.loading_session" as I18nSemanticKey)
            : subtext}
        </p>
      </div>
      {isOpen ? (
        <button
          type="button"
          onClick={onEndSessionClick}
          disabled={loading}
          className="min-h-11 shrink-0 rounded-lg border border-red-200 bg-red-50 px-3 text-sm font-medium text-red-700 transition hover:bg-red-100 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {t("stationSession.row.session.action.endSession" as I18nSemanticKey)}
        </button>
      ) : (
        <button
          type="button"
          onClick={onOpenSession}
          disabled={loading || opening}
          className="min-h-11 shrink-0 rounded-lg border border-blue-600 bg-blue-600 px-3 text-sm font-semibold text-white transition hover:bg-blue-700 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {opening
            ? t("stationSession.action.openingSession" as I18nSemanticKey)
            : t("stationSession.row.session.action.open" as I18nSemanticKey)}
        </button>
      )}
    </div>
  );
}

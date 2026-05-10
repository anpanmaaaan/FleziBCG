import { Power } from "lucide-react";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";
import type { StationCommandErrorMessage } from "./stationCommandErrorMessages";

interface OpenSessionPanelProps {
  sessionId: string | null;
  openedAt: string | null;
  isOpen: boolean;
  loading: boolean;
  opening: boolean;
  stationId: string | null;
  commandError: StationCommandErrorMessage | null;
  onOpenSession: () => void;
  onRefresh: () => void;
}

export function OpenSessionPanel({
  sessionId,
  openedAt,
  isOpen,
  loading,
  opening,
  stationId,
  commandError,
  onOpenSession,
  onRefresh,
}: OpenSessionPanelProps) {
  const { t } = useI18n();

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <div className="flex items-center gap-2">
        <Power className="h-4 w-4 text-slate-500" />
        <h2 className="text-sm font-semibold text-slate-900">
          {t("stationSession.setup.section.session" as I18nSemanticKey)}
        </h2>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        {t("stationSession.setup.section.sessionHint" as I18nSemanticKey)}
      </p>

      {loading ? (
        <p className="mt-4 text-sm text-gray-400">{t("stationSession.label.loading_session" as I18nSemanticKey)}</p>
      ) : (
        <>
          <dl className="mt-3 space-y-2 text-sm">
            <div className="flex items-center justify-between gap-2">
              <dt className="text-slate-500">{t("stationSession.label.session_id" as I18nSemanticKey)}</dt>
              <dd className="font-mono text-xs text-slate-700">{sessionId || t("stationSession.state.missing" as I18nSemanticKey)}</dd>
            </div>
            <div className="flex items-center justify-between gap-2">
              <dt className="text-slate-500">{t("common.status" as I18nSemanticKey)}</dt>
              <dd className="text-slate-700">
                {!sessionId
                  ? t("stationSession.state.missing" as I18nSemanticKey)
                  : isOpen
                  ? t("stationSession.state.open" as I18nSemanticKey)
                  : t("stationSession.state.closed" as I18nSemanticKey)}
              </dd>
            </div>
            {openedAt && (
              <div className="flex items-center justify-between gap-2">
                <dt className="text-slate-500">{t("stationSession.label.opened_at" as I18nSemanticKey)}</dt>
                <dd className="text-xs text-slate-700">{new Date(openedAt).toLocaleString()}</dd>
              </div>
            )}
          </dl>

          {commandError && (
            <div
              className={`mt-3 rounded-lg border px-3 py-2 text-sm ${commandError.severity === "danger" ? "border-red-200 bg-red-50 text-red-800" : "border-amber-200 bg-amber-50 text-amber-800"}`}
              role="alert"
            >
              <p className="font-semibold">{t(commandError.titleKey as I18nSemanticKey)}</p>
              <p className="mt-1 text-xs">{t(commandError.messageKey as I18nSemanticKey)}</p>
              <p className="mt-1 text-xs">{t(commandError.recoveryKey as I18nSemanticKey)}</p>
            </div>
          )}

          <div className="mt-3 flex flex-wrap gap-2">
            {!isOpen && (
              <button
                type="button"
                onClick={onOpenSession}
                disabled={opening || !stationId}
                className="min-h-11 rounded-lg border border-blue-600 bg-blue-600 px-4 text-sm font-semibold text-white transition hover:bg-blue-700 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {opening ? t("stationSession.action.openingSession" as I18nSemanticKey) : t("stationSession.action.openSession" as I18nSemanticKey)}
              </button>
            )}
            <button
              type="button"
              onClick={onRefresh}
              disabled={loading}
              className="min-h-11 rounded-lg border border-slate-300 bg-white px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {t("stationSession.action.viewSession" as I18nSemanticKey)}
            </button>
          </div>
        </>
      )}
    </section>
  );
}

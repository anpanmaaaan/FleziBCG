import { AlertTriangle, Power } from "lucide-react";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";
import type { StationCommandErrorMessage } from "./stationCommandErrorMessages";

interface CloseSessionPanelProps {
  isSessionOpen: boolean;
  showCloseConfirm: boolean;
  closing: boolean;
  commandError: StationCommandErrorMessage | null;
  onClose: () => void;
  onConfirmClose: () => void;
  onCancelClose: () => void;
}

export function CloseSessionPanel({
  isSessionOpen,
  showCloseConfirm,
  closing,
  commandError,
  onClose,
  onConfirmClose,
  onCancelClose,
}: CloseSessionPanelProps) {
  const { t } = useI18n();

  if (!isSessionOpen) {
    return null;
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Power className="h-4 w-4 text-slate-500" />
            <h2 className="text-base font-semibold text-slate-900">
              {t("stationSession.endSession.title" as I18nSemanticKey)}
            </h2>
          </div>
          <p className="mt-2 text-sm text-slate-700">
            {t("stationSession.endSession.description" as I18nSemanticKey)}
          </p>
          <p className="mt-2 text-xs text-slate-500">
            {t("stationSession.endSession.guardHint" as I18nSemanticKey)}
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={closing}
        >
          {t("stationSession.setup.continue.cta" as I18nSemanticKey)}
        </button>
      </div>

      <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        <div className="flex items-start gap-2">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
          <div className="min-w-0">
            <p className="font-medium">{t("stationSession.endSession.closeConfirmHint" as I18nSemanticKey)}</p>
            <p className="mt-1 text-xs text-amber-800">
              {t("stationSession.endSession.blockedRecovery" as I18nSemanticKey)}
            </p>
          </div>
        </div>
      </div>

      {commandError && (
        <div
          className={`mt-4 rounded-lg border px-4 py-3 text-sm ${commandError.severity === "danger" ? "border-red-200 bg-red-50 text-red-800" : "border-amber-200 bg-amber-50 text-amber-800"}`}
          role="alert"
        >
          <p className="font-semibold">{t(commandError.titleKey as I18nSemanticKey)}</p>
          <p className="mt-1">{t(commandError.messageKey as I18nSemanticKey)}</p>
          <p className="mt-1 text-xs">{t(commandError.recoveryKey as I18nSemanticKey)}</p>
        </div>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        {showCloseConfirm ? (
          <>
            <button
              type="button"
              onClick={onConfirmClose}
              disabled={closing}
              className="min-h-11 rounded-lg bg-red-600 px-4 text-sm font-semibold text-white transition hover:bg-red-700 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {t("stationSession.action.closeSession" as I18nSemanticKey)}
            </button>
            <button
              type="button"
              onClick={onCancelClose}
              disabled={closing}
              className="min-h-11 rounded-lg border border-slate-300 bg-white px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {t("common.action.cancel" as I18nSemanticKey)}
            </button>
          </>
        ) : (
          <button
            type="button"
            onClick={() => onClose()}
            disabled={closing}
            className="min-h-11 rounded-lg border border-red-200 bg-red-50 px-4 text-sm font-medium text-red-700 transition hover:bg-red-100 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {t("stationSession.action.closeSession" as I18nSemanticKey)}
          </button>
        )}
      </div>
    </section>
  );
}

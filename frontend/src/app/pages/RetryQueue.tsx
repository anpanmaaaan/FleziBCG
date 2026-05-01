// Retry / Failure Queue — SHELL
// To-be visualization of failed integration message retry queue.
// Real retry execution, skip, and dead-letter operations are managed
// by the backend integration fault-tolerance module.
// DO NOT use as source of integration failure truth.

import { RefreshCw, SkipForward, Archive } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_FAILURES = [
  { id: "FAIL-0019", target: "SAP ERP", errorCode: "IDOC_CONN_TIMEOUT", type: "ProductionConfirmation", retries: 3, lastAttempt: "2026-05-01 09:52" },
  { id: "FAIL-0018", target: "QMS", errorCode: "AUTH_TOKEN_EXPIRED", type: "QualityResultPost", retries: 5, lastAttempt: "2026-05-01 09:30" },
  { id: "FAIL-0017", target: "CMMS", errorCode: "HTTP_503", type: "DowntimeNotification", retries: 2, lastAttempt: "2026-05-01 09:01" },
  { id: "FAIL-0016", target: "WMS", errorCode: "INVALID_PAYLOAD", type: "StockMovement", retries: 8, lastAttempt: "2026-05-01 08:14" },
];

export function RetryQueue() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("retryQueue.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("retryQueue.notice.shell")} />

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <RefreshCw className="w-4 h-4 text-red-400" />
          {t("retryQueue.section.failures")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("retryQueue.col.id")}</th>
                <th className="px-4 py-2 text-left">{t("retryQueue.col.type")}</th>
                <th className="px-4 py-2 text-left">{t("retryQueue.col.target")}</th>
                <th className="px-4 py-2 text-left">{t("retryQueue.col.errorCode")}</th>
                <th className="px-4 py-2 text-left">{t("retryQueue.col.retries")}</th>
                <th className="px-4 py-2 text-left">{t("retryQueue.col.lastAttempt")}</th>
                <th className="px-4 py-2 text-left">{t("retryQueue.col.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_FAILURES.map((f) => (
                <tr key={f.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-600">{f.id}</td>
                  <td className="px-4 py-2 text-gray-800">{f.type}</td>
                  <td className="px-4 py-2 text-gray-600">{f.target}</td>
                  <td className="px-4 py-2">
                    <span className="text-xs font-mono px-2 py-0.5 bg-red-50 text-red-700 rounded border border-red-100">{f.errorCode}</span>
                  </td>
                  <td className="px-4 py-2 text-center">
                    <span className={`text-xs font-bold ${f.retries >= 5 ? "text-red-600" : "text-orange-600"}`}>{f.retries}</span>
                  </td>
                  <td className="px-4 py-2 text-xs text-gray-500">{f.lastAttempt}</td>
                  <td className="px-4 py-2">
                    <div className="flex gap-1">
                      <button type="button" disabled title={t("retryQueue.hint.disabled")} className="inline-flex items-center gap-1 text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">
                        <RefreshCw className="w-3 h-3" />
                        {t("retryQueue.action.retry")}
                      </button>
                      <button type="button" disabled title={t("retryQueue.hint.disabled")} className="inline-flex items-center gap-1 text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">
                        <SkipForward className="w-3 h-3" />
                        {t("retryQueue.action.skip")}
                      </button>
                      <button type="button" disabled title={t("retryQueue.hint.disabled")} className="inline-flex items-center gap-1 text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">
                        <Archive className="w-3 h-3" />
                        {t("retryQueue.action.deadLetter")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("retryQueue.hint.backend")}</p>
      </div>
    </div>
  );
}

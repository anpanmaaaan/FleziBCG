// Posting Requests — SHELL
// To-be visualization of ERP posting request queue.
// Real ERP posting, retry, and cancel operations are managed
// by the backend integration and ERP adapter modules.
// DO NOT use as source of ERP posting truth.

import { RefreshCw, XCircle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_REQUESTS = [
  { id: "POST-0031", type: "GoodsReceipt", source: "WO-1042 / OP-020", status: "Queued", retries: 0, created: "2026-05-01 09:45" },
  { id: "POST-0030", type: "ProductionConfirmation", source: "WO-1041 / OP-030", status: "Posted", retries: 0, created: "2026-05-01 09:22" },
  { id: "POST-0029", type: "GoodsMovement", source: "WO-1040 / Staging", status: "Failed", retries: 2, created: "2026-05-01 08:55" },
  { id: "POST-0028", type: "QualityPost", source: "WO-1039 / QC-01", status: "Failed", retries: 3, created: "2026-05-01 08:31" },
];

const STATUS_COLORS: Record<string, string> = {
  Queued: "bg-yellow-50 text-yellow-700 border-yellow-100",
  Posted: "bg-green-50 text-green-700 border-green-100",
  Failed: "bg-red-50 text-red-700 border-red-100",
};

export function PostingRequests() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("postingRequests.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("postingRequests.notice.shell")} />

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <RefreshCw className="w-4 h-4 text-slate-400" />
          {t("postingRequests.section.queue")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("postingRequests.col.id")}</th>
                <th className="px-4 py-2 text-left">{t("postingRequests.col.type")}</th>
                <th className="px-4 py-2 text-left">{t("postingRequests.col.source")}</th>
                <th className="px-4 py-2 text-left">{t("postingRequests.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("postingRequests.col.retries")}</th>
                <th className="px-4 py-2 text-left">{t("postingRequests.col.created")}</th>
                <th className="px-4 py-2 text-left">{t("postingRequests.col.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_REQUESTS.map((req) => (
                <tr key={req.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-600">{req.id}</td>
                  <td className="px-4 py-2 text-gray-800">{req.type}</td>
                  <td className="px-4 py-2 text-gray-600 text-xs">{req.source}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${STATUS_COLORS[req.status] ?? "bg-slate-50 text-slate-500 border-slate-100"}`}>{req.status}</span>
                  </td>
                  <td className="px-4 py-2 text-center text-gray-500">{req.retries}</td>
                  <td className="px-4 py-2 text-xs text-gray-500">{req.created}</td>
                  <td className="px-4 py-2">
                    <div className="flex gap-1">
                      <button type="button" disabled title={t("postingRequests.hint.disabled")} className="inline-flex items-center gap-1 text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">
                        <RefreshCw className="w-3 h-3" />
                        {t("postingRequests.action.retry")}
                      </button>
                      <button type="button" disabled title={t("postingRequests.hint.disabled")} className="inline-flex items-center gap-1 text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">
                        <XCircle className="w-3 h-3" />
                        {t("postingRequests.action.cancel")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("postingRequests.hint.backend")}</p>
      </div>
    </div>
  );
}

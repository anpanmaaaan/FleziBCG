// Outbound Messages — SHELL
// To-be visualization of outbound integration message queue.
// Real message sending, resending, and delivery confirmation
// are managed by the backend integration event bus.

import { ArrowUpRight, Send } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_MESSAGES = [
  { id: "MSG-OUT-0087", type: "GoodsMovement", target: "SAP ERP", status: "Sent", created: "2026-05-01 09:21", correlationId: "CORR-5511" },
  { id: "MSG-OUT-0086", type: "ProductionConfirmation", target: "SAP ERP", status: "Sent", created: "2026-05-01 09:10", correlationId: "CORR-5510" },
  { id: "MSG-OUT-0085", type: "QualityResultPost", target: "QMS", status: "Failed", created: "2026-05-01 08:58", correlationId: "CORR-5509" },
  { id: "MSG-OUT-0084", type: "DowntimeNotification", target: "CMMS", status: "Pending", created: "2026-05-01 08:43", correlationId: "CORR-5508" },
];

const STATUS_COLORS: Record<string, string> = {
  Sent: "bg-green-50 text-green-700 border-green-100",
  Failed: "bg-red-50 text-red-700 border-red-100",
  Pending: "bg-yellow-50 text-yellow-700 border-yellow-100",
};

export function OutboundMessages() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("outboundMessages.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("outboundMessages.notice.shell")} />

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <ArrowUpRight className="w-4 h-4 text-slate-400" />
          {t("outboundMessages.section.queue")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("outboundMessages.col.id")}</th>
                <th className="px-4 py-2 text-left">{t("outboundMessages.col.type")}</th>
                <th className="px-4 py-2 text-left">{t("outboundMessages.col.target")}</th>
                <th className="px-4 py-2 text-left">{t("outboundMessages.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("outboundMessages.col.created")}</th>
                <th className="px-4 py-2 text-left">{t("outboundMessages.col.correlationId")}</th>
                <th className="px-4 py-2 text-left">{t("outboundMessages.col.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_MESSAGES.map((msg) => (
                <tr key={msg.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-600">{msg.id}</td>
                  <td className="px-4 py-2 text-gray-800">{msg.type}</td>
                  <td className="px-4 py-2 text-gray-600">{msg.target}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${STATUS_COLORS[msg.status] ?? "bg-slate-50 text-slate-500 border-slate-100"}`}>{msg.status}</span>
                  </td>
                  <td className="px-4 py-2 text-xs text-gray-500">{msg.created}</td>
                  <td className="px-4 py-2 font-mono text-xs text-gray-500">{msg.correlationId}</td>
                  <td className="px-4 py-2">
                    <button type="button" disabled title={t("outboundMessages.hint.disabled")} className="inline-flex items-center gap-1 text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">
                      <Send className="w-3 h-3" />
                      {t("outboundMessages.action.resend")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("outboundMessages.hint.backend")}</p>
      </div>
    </div>
  );
}

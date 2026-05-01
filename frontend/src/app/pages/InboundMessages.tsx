// Inbound Messages — SHELL
// To-be visualization of inbound integration message queue.
// Real message processing, acceptance, and replay are managed
// by the backend integration event bus.

import { ArrowDownLeft, Play } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_MESSAGES = [
  { id: "MSG-IN-0042", type: "MaterialMasterUpdate", source: "SAP ERP", status: "Pending", received: "2026-05-01 08:14", correlationId: "CORR-4421" },
  { id: "MSG-IN-0041", type: "ProductionOrderCreate", source: "SAP ERP", status: "Processed", received: "2026-05-01 08:03", correlationId: "CORR-4420" },
  { id: "MSG-IN-0040", type: "StockMovement", source: "WMS", status: "Failed", received: "2026-05-01 07:52", correlationId: "CORR-4419" },
  { id: "MSG-IN-0039", type: "QualityNotification", source: "QMS", status: "Processed", received: "2026-05-01 07:31", correlationId: "CORR-4418" },
];

const STATUS_COLORS: Record<string, string> = {
  Pending: "bg-yellow-50 text-yellow-700 border-yellow-100",
  Processed: "bg-green-50 text-green-700 border-green-100",
  Failed: "bg-red-50 text-red-700 border-red-100",
};

export function InboundMessages() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("inboundMessages.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("inboundMessages.notice.shell")} />

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <ArrowDownLeft className="w-4 h-4 text-slate-400" />
          {t("inboundMessages.section.queue")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("inboundMessages.col.id")}</th>
                <th className="px-4 py-2 text-left">{t("inboundMessages.col.type")}</th>
                <th className="px-4 py-2 text-left">{t("inboundMessages.col.source")}</th>
                <th className="px-4 py-2 text-left">{t("inboundMessages.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("inboundMessages.col.received")}</th>
                <th className="px-4 py-2 text-left">{t("inboundMessages.col.correlationId")}</th>
                <th className="px-4 py-2 text-left">{t("inboundMessages.col.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_MESSAGES.map((msg) => (
                <tr key={msg.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-600">{msg.id}</td>
                  <td className="px-4 py-2 text-gray-800">{msg.type}</td>
                  <td className="px-4 py-2 text-gray-600">{msg.source}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${STATUS_COLORS[msg.status] ?? "bg-slate-50 text-slate-500 border-slate-100"}`}>{msg.status}</span>
                  </td>
                  <td className="px-4 py-2 text-xs text-gray-500">{msg.received}</td>
                  <td className="px-4 py-2 font-mono text-xs text-gray-500">{msg.correlationId}</td>
                  <td className="px-4 py-2">
                    <button type="button" disabled title={t("inboundMessages.hint.disabled")} className="inline-flex items-center gap-1 text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">
                      <Play className="w-3 h-3" />
                      {t("inboundMessages.action.replay")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("inboundMessages.hint.backend")}</p>
      </div>
    </div>
  );
}

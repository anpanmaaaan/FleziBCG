// Integration Status Report — SHELL
// To-be visualization of integration health and message throughput reporting.
// Real integration monitoring, failure rates, and system health
// are managed by the backend integration and observability modules.
// DO NOT use as source of real integration monitoring truth.

import { Activity, AlertCircle, Download } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SUMMARY = [
  { label: "Messages Today", value: "—" },
  { label: "Failure Rate", value: "—" },
  { label: "Posting Success Rate", value: "—" },
  { label: "Systems Active", value: "—" },
];

const MOCK_SYSTEMS_STATUS = [
  { system: "SAP ERP", direction: "Both", messagesIn: "—", messagesOut: "—", failures: "—", postingRate: "—" },
  { system: "WMS", direction: "Inbound", messagesIn: "—", messagesOut: "N/A", failures: "—", postingRate: "N/A" },
  { system: "QMS", direction: "Both", messagesIn: "—", messagesOut: "—", failures: "—", postingRate: "—" },
  { system: "CMMS", direction: "Outbound", messagesIn: "N/A", messagesOut: "—", failures: "—", postingRate: "—" },
];

export function IntegrationStatusReport() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("integrationStatusReport.title")}</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <button
          type="button"
          disabled
          title={t("integrationStatusReport.hint.disabled")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          {t("integrationStatusReport.action.export")}
        </button>
      </div>

      <BackendRequiredNotice message={t("integrationStatusReport.notice.shell")} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {MOCK_SUMMARY.map((kpi) => (
          <div key={kpi.label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
              <Activity className="w-3 h-3" />
              {kpi.label}
            </div>
            <div className="text-2xl font-bold text-slate-600">{kpi.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <AlertCircle className="w-4 h-4 text-slate-400" />
          {t("integrationStatusReport.section.bySystem")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("integrationStatusReport.col.system")}</th>
                <th className="px-4 py-2 text-left">{t("integrationStatusReport.col.direction")}</th>
                <th className="px-4 py-2 text-left">{t("integrationStatusReport.col.messagesIn")}</th>
                <th className="px-4 py-2 text-left">{t("integrationStatusReport.col.messagesOut")}</th>
                <th className="px-4 py-2 text-left">{t("integrationStatusReport.col.failures")}</th>
                <th className="px-4 py-2 text-left">{t("integrationStatusReport.col.postingRate")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_SYSTEMS_STATUS.map((row) => (
                <tr key={row.system} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 font-medium text-gray-800">{row.system}</td>
                  <td className="px-4 py-2 text-gray-600">{row.direction}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.messagesIn}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.messagesOut}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.failures}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.postingRate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("integrationStatusReport.hint.backend")}</p>
      </div>
    </div>
  );
}

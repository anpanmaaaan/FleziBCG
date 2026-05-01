// Integration Dashboard — SHELL
// To-be visualization of enterprise integration health and message flow.
// Integration state, posting status, and reconciliation truth
// are managed by backend integration and ERP systems.

import { AlertCircle, ArrowDownLeft, ArrowUpRight, RefreshCw, XCircle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SYSTEMS = [
  { name: "SAP ERP", type: "ERP", direction: "Both", status: "Unknown", env: "Production" },
  { name: "WMS", type: "WMS", direction: "Inbound", status: "Unknown", env: "Production" },
  { name: "QMS", type: "QMS", direction: "Both", status: "Unknown", env: "Production" },
  { name: "SCADA", type: "SCADA", direction: "Inbound", status: "Unknown", env: "Shop Floor" },
];

export function IntegrationDashboard() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("integrationDashboard.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("integrationDashboard.notice.shell")} />

      {/* Summary KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="flex items-center gap-1 text-xs text-slate-600 mb-1">
            <ArrowDownLeft className="w-3 h-3" />
            {t("integrationDashboard.metric.inbound")}
          </div>
          <div className="text-2xl font-bold text-slate-700">—</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="flex items-center gap-1 text-xs text-slate-600 mb-1">
            <ArrowUpRight className="w-3 h-3" />
            {t("integrationDashboard.metric.outbound")}
          </div>
          <div className="text-2xl font-bold text-slate-700">—</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="flex items-center gap-1 text-xs text-slate-600 mb-1">
            <RefreshCw className="w-3 h-3" />
            {t("integrationDashboard.metric.posting")}
          </div>
          <div className="text-2xl font-bold text-slate-700">—</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="flex items-center gap-1 text-xs text-red-500 mb-1">
            <XCircle className="w-3 h-3" />
            {t("integrationDashboard.metric.failures")}
          </div>
          <div className="text-2xl font-bold text-slate-700">—</div>
        </div>
      </div>

      {/* External system health cards */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <AlertCircle className="w-4 h-4 text-slate-400" />
          {t("integrationDashboard.section.systems")}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4">
          {MOCK_SYSTEMS.map((sys) => (
            <div key={sys.name} className="rounded-lg border border-slate-200 p-3 bg-slate-50">
              <div className="flex justify-between items-start mb-1">
                <span className="text-sm font-medium text-slate-800">{sys.name}</span>
                <span className="text-xs px-2 py-0.5 bg-slate-200 text-slate-600 rounded-full">{sys.type}</span>
              </div>
              <div className="text-xs text-slate-500">{sys.direction} · {sys.env}</div>
              <div className="mt-2 text-xs text-slate-400 italic">{t("integrationDashboard.system.statusUnknown")}</div>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-400 italic px-4 pb-3">{t("integrationDashboard.hint.backend")}</p>
      </div>
    </div>
  );
}

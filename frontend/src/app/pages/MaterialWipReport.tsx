// Material / WIP Report — SHELL
// To-be visualization of material and WIP status reporting.
// Real WIP position, inventory truth, and material consumption
// are managed by the backend inventory and material modules.
// DO NOT use as source of inventory or WIP truth.

import { Package, Clock, Download } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SUMMARY = [
  { label: "Total WIP", value: "—" },
  { label: "Material Shortages", value: "—" },
  { label: "Avg WIP Age (min)", value: "—" },
  { label: "Buffers Near Capacity", value: "—" },
];

const MOCK_WIP = [
  { workOrder: "WO-1041", material: "SEMI-A-001", location: "Buffer-02", qty: "—", ageMin: "—", status: "In Progress" },
  { workOrder: "WO-1040", material: "PROD-B-002", location: "Station-03", qty: "—", ageMin: "—", status: "Waiting" },
  { workOrder: "WO-1039", material: "SEMI-C-003", location: "Buffer-01", qty: "—", ageMin: "—", status: "In Progress" },
];

export function MaterialWipReport() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("materialWipReport.title")}</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <button
          type="button"
          disabled
          title={t("materialWipReport.hint.disabled")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          {t("materialWipReport.action.export")}
        </button>
      </div>

      <BackendRequiredNotice message={t("materialWipReport.notice.shell")} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {MOCK_SUMMARY.map((kpi) => (
          <div key={kpi.label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
              <Package className="w-3 h-3" />
              {kpi.label}
            </div>
            <div className="text-2xl font-bold text-slate-600">{kpi.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Clock className="w-4 h-4 text-slate-400" />
          {t("materialWipReport.section.wip")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("materialWipReport.col.workOrder")}</th>
                <th className="px-4 py-2 text-left">{t("materialWipReport.col.material")}</th>
                <th className="px-4 py-2 text-left">{t("materialWipReport.col.location")}</th>
                <th className="px-4 py-2 text-left">{t("materialWipReport.col.qty")}</th>
                <th className="px-4 py-2 text-left">{t("materialWipReport.col.ageMin")}</th>
                <th className="px-4 py-2 text-left">{t("materialWipReport.col.status")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_WIP.map((row) => (
                <tr key={row.workOrder} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-600">{row.workOrder}</td>
                  <td className="px-4 py-2 text-gray-800">{row.material}</td>
                  <td className="px-4 py-2 text-gray-600">{row.location}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.qty}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.ageMin}</td>
                  <td className="px-4 py-2">
                    <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded border border-slate-200">{row.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("materialWipReport.hint.backend")}</p>
      </div>
    </div>
  );
}

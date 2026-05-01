// Production Performance Report — SHELL
// To-be visualization of production output and performance reporting.
// Real production metrics, KPI calculations, and report exports
// are managed by the backend reporting and analytics modules.
// DO NOT use as source of deterministic production performance truth.

import { TrendingUp, BarChart2, Download } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SUMMARY = [
  { label: "Orders Completed", value: "—" },
  { label: "On-Time Rate", value: "—" },
  { label: "Plan vs Actual", value: "—" },
  { label: "Avg Cycle Time", value: "—" },
];

const MOCK_ROWS = [
  { order: "WO-1041", product: "PROD-A-001", line: "Line-01", planned: "100", actual: "—", completion: "—", shift: "Morning" },
  { order: "WO-1040", product: "PROD-B-002", line: "Line-02", planned: "50", actual: "—", completion: "—", shift: "Morning" },
  { order: "WO-1039", product: "PROD-A-001", line: "Line-01", planned: "80", actual: "—", completion: "—", shift: "Night" },
];

export function ProductionPerformanceReport() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("productionPerfReport.title")}</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <button
          type="button"
          disabled
          title={t("productionPerfReport.hint.disabled")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          {t("productionPerfReport.action.export")}
        </button>
      </div>

      <BackendRequiredNotice message={t("productionPerfReport.notice.shell")} />

      {/* Summary KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {MOCK_SUMMARY.map((kpi) => (
          <div key={kpi.label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
              <TrendingUp className="w-3 h-3" />
              {kpi.label}
            </div>
            <div className="text-2xl font-bold text-slate-600">{kpi.value}</div>
          </div>
        ))}
      </div>

      {/* Filters row (disabled) */}
      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-slate-400">{t("productionPerfReport.filter.label")}:</span>
        {["Plant", "Line", "Shift", "Product"].map((f) => (
          <span key={f} className="text-xs px-2 py-0.5 bg-slate-100 text-slate-400 rounded border border-slate-200">{f}</span>
        ))}
        <span className="text-xs text-slate-400 italic">{t("productionPerfReport.filter.hint")}</span>
      </div>

      {/* Data table placeholder */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <BarChart2 className="w-4 h-4 text-slate-400" />
          {t("productionPerfReport.section.details")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("productionPerfReport.col.order")}</th>
                <th className="px-4 py-2 text-left">{t("productionPerfReport.col.product")}</th>
                <th className="px-4 py-2 text-left">{t("productionPerfReport.col.line")}</th>
                <th className="px-4 py-2 text-left">{t("productionPerfReport.col.planned")}</th>
                <th className="px-4 py-2 text-left">{t("productionPerfReport.col.actual")}</th>
                <th className="px-4 py-2 text-left">{t("productionPerfReport.col.completion")}</th>
                <th className="px-4 py-2 text-left">{t("productionPerfReport.col.shift")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_ROWS.map((row) => (
                <tr key={row.order} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-600">{row.order}</td>
                  <td className="px-4 py-2 text-gray-800">{row.product}</td>
                  <td className="px-4 py-2 text-gray-600">{row.line}</td>
                  <td className="px-4 py-2 text-gray-600">{row.planned}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.actual}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.completion}</td>
                  <td className="px-4 py-2 text-gray-600">{row.shift}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("productionPerfReport.hint.backend")}</p>
      </div>
    </div>
  );
}

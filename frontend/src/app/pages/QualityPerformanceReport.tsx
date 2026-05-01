// Quality Performance Report — SHELL
// To-be visualization of quality performance reporting.
// Real defect rates, quality metrics, and official quality reports
// are managed by the backend quality and reporting modules.
// DO NOT use as source of official quality metrics.

import { ShieldCheck, AlertTriangle, Download } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SUMMARY = [
  { label: "Defect Rate", value: "—" },
  { label: "Quality Holds", value: "—" },
  { label: "Inspection Pass Rate", value: "—" },
  { label: "NCRs Open", value: "—" },
];

const MOCK_ISSUES = [
  { category: "Dimension Out of Spec", count: "—", trend: "—", operation: "OP-010" },
  { category: "Surface Finish Fail", count: "—", trend: "—", operation: "OP-020" },
  { category: "Assembly Defect", count: "—", trend: "—", operation: "OP-030" },
];

export function QualityPerformanceReport() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("qualityPerfReport.title")}</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <button
          type="button"
          disabled
          title={t("qualityPerfReport.hint.disabled")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          {t("qualityPerfReport.action.export")}
        </button>
      </div>

      <BackendRequiredNotice message={t("qualityPerfReport.notice.shell")} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {MOCK_SUMMARY.map((kpi) => (
          <div key={kpi.label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
              <ShieldCheck className="w-3 h-3" />
              {kpi.label}
            </div>
            <div className="text-2xl font-bold text-slate-600">{kpi.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <AlertTriangle className="w-4 h-4 text-slate-400" />
          {t("qualityPerfReport.section.issues")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("qualityPerfReport.col.category")}</th>
                <th className="px-4 py-2 text-left">{t("qualityPerfReport.col.operation")}</th>
                <th className="px-4 py-2 text-left">{t("qualityPerfReport.col.count")}</th>
                <th className="px-4 py-2 text-left">{t("qualityPerfReport.col.trend")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_ISSUES.map((row) => (
                <tr key={row.category} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-800">{row.category}</td>
                  <td className="px-4 py-2 text-gray-600">{row.operation}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.count}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.trend}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("qualityPerfReport.hint.backend")}</p>
      </div>
    </div>
  );
}

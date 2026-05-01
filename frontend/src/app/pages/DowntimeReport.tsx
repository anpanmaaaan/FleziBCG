// Downtime Report — SHELL
// Reporting-focused downtime summary (separate from operational /downtime-analysis).
// Official downtime metrics, root cause analysis, and report export
// are managed by the backend reporting and analytics modules.
// DO NOT use as source of deterministic downtime truth.

import { Clock, AlertTriangle, Download } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SUMMARY = [
  { label: "Total Downtime (min)", value: "—" },
  { label: "Events", value: "—" },
  { label: "MTTR (min)", value: "—" },
  { label: "Top Reason", value: "—" },
];

const MOCK_ROWS = [
  { date: "2026-05-01", line: "Line-01", reason: "Equipment Failure", category: "Unplanned", duration: "—", root: "—" },
  { date: "2026-05-01", line: "Line-02", reason: "Material Shortage", category: "Planned", duration: "—", root: "—" },
  { date: "2026-04-30", line: "Line-01", reason: "Changeover", category: "Planned", duration: "—", root: "—" },
];

export function DowntimeReport() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("downtimeReport.title")}</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <button
          type="button"
          disabled
          title={t("downtimeReport.hint.disabled")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          {t("downtimeReport.action.export")}
        </button>
      </div>

      <BackendRequiredNotice message={t("downtimeReport.notice.shell")} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {MOCK_SUMMARY.map((kpi) => (
          <div key={kpi.label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
              <Clock className="w-3 h-3" />
              {kpi.label}
            </div>
            <div className="text-2xl font-bold text-slate-600">{kpi.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <AlertTriangle className="w-4 h-4 text-slate-400" />
          {t("downtimeReport.section.events")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("downtimeReport.col.date")}</th>
                <th className="px-4 py-2 text-left">{t("downtimeReport.col.line")}</th>
                <th className="px-4 py-2 text-left">{t("downtimeReport.col.reason")}</th>
                <th className="px-4 py-2 text-left">{t("downtimeReport.col.category")}</th>
                <th className="px-4 py-2 text-left">{t("downtimeReport.col.duration")}</th>
                <th className="px-4 py-2 text-left">{t("downtimeReport.col.rootCause")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_ROWS.map((row, i) => (
                <tr key={i} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 text-xs text-gray-600">{row.date}</td>
                  <td className="px-4 py-2 text-gray-600">{row.line}</td>
                  <td className="px-4 py-2 text-gray-800">{row.reason}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded border ${row.category === "Planned" ? "bg-blue-50 text-blue-700 border-blue-100" : "bg-orange-50 text-orange-700 border-orange-100"}`}>{row.category}</span>
                  </td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.duration}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.root}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("downtimeReport.hint.backend")}</p>
      </div>
    </div>
  );
}

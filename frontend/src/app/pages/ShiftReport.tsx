// Shift Report — SHELL
// To-be visualization of official shift close report.
// Official shift report data, KPIs, and closure are managed
// by the backend reporting and shift management modules.
// DO NOT use as source of official shift close truth.

import { Clock, FileText, Download, Lock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SHIFTS = [
  { shift: "Morning — 2026-05-01", line: "Line-01", operator: "—", orders: "—", downtime: "—", quality: "—", status: "Open" },
  { shift: "Night — 2026-04-30", line: "Line-01", operator: "—", orders: "—", downtime: "—", quality: "—", status: "Open" },
  { shift: "Morning — 2026-04-30", line: "Line-02", operator: "—", orders: "—", downtime: "—", quality: "—", status: "Open" },
];

export function ShiftReport() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("shiftReport.title")}</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            disabled
            title={t("shiftReport.hint.disabled")}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
          >
            <Lock className="w-4 h-4" />
            {t("shiftReport.action.close")}
          </button>
          <button
            type="button"
            disabled
            title={t("shiftReport.hint.disabled")}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            {t("shiftReport.action.export")}
          </button>
        </div>
      </div>

      <BackendRequiredNotice message={t("shiftReport.notice.shell")} />

      {/* Summary KPI row (to-be) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[t("shiftReport.metric.orders"), t("shiftReport.metric.downtime"), t("shiftReport.metric.quality"), t("shiftReport.metric.blockers")].map((label) => (
          <div key={label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
              <Clock className="w-3 h-3" />
              {label}
            </div>
            <div className="text-2xl font-bold text-slate-600">—</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <FileText className="w-4 h-4 text-slate-400" />
          {t("shiftReport.section.shifts")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("shiftReport.col.shift")}</th>
                <th className="px-4 py-2 text-left">{t("shiftReport.col.line")}</th>
                <th className="px-4 py-2 text-left">{t("shiftReport.col.orders")}</th>
                <th className="px-4 py-2 text-left">{t("shiftReport.col.downtime")}</th>
                <th className="px-4 py-2 text-left">{t("shiftReport.col.quality")}</th>
                <th className="px-4 py-2 text-left">{t("shiftReport.col.status")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_SHIFTS.map((row) => (
                <tr key={row.shift + row.line} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-800 text-xs">{row.shift}</td>
                  <td className="px-4 py-2 text-gray-600">{row.line}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.orders}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.downtime}</td>
                  <td className="px-4 py-2 text-slate-400 italic">{row.quality}</td>
                  <td className="px-4 py-2">
                    <span className="text-xs px-2 py-0.5 bg-yellow-50 text-yellow-700 rounded border border-yellow-100">{row.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("shiftReport.hint.backend")}</p>
      </div>
    </div>
  );
}

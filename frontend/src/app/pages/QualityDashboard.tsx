// Quality Lite Dashboard — SHELL
// To-be visualization of quality performance summary.
// Quality evaluation and disposition are managed by the backend quality domain.

import { AlertCircle, CheckCircle, Clock, TrendingUp } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_QC_DATA = [
  { characteristic: "Dimension A", operation: "OP-010", value: "25.4", spec: "25±0.5", status: "PASS", evaluator: "QC-001", timestamp: "2026-05-01 10:32" },
  { characteristic: "Dimension B", operation: "OP-010", value: "15.2", spec: "15±0.3", status: "PASS", evaluator: "QC-001", timestamp: "2026-05-01 10:34" },
  { characteristic: "Surface Finish", operation: "OP-020", value: "1.8", spec: "<2.0", status: "PASS", evaluator: "QC-002", timestamp: "2026-05-01 11:05" },
];

export function QualityDashboard() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("qualityDashboard.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("qualityDashboard.notice.shell")} />

      {/* Summary KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-green-50 rounded-lg border border-green-200 p-3">
          <div className="flex items-center gap-1 text-xs text-green-600 mb-1">
            <CheckCircle className="w-3 h-3" />
            {t("qualityDashboard.metric.checks")}
          </div>
          <div className="text-2xl font-bold text-green-800">18</div>
        </div>
        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-3">
          <div className="flex items-center gap-1 text-xs text-yellow-600 mb-1">
            <Clock className="w-3 h-3" />
            {t("qualityDashboard.metric.pending")}
          </div>
          <div className="text-2xl font-bold text-yellow-800">3</div>
        </div>
        <div className="bg-red-50 rounded-lg border border-red-200 p-3">
          <div className="flex items-center gap-1 text-xs text-red-600 mb-1">
            <AlertCircle className="w-3 h-3" />
            {t("qualityDashboard.metric.defects")}
          </div>
          <div className="text-2xl font-bold text-red-800">1</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3">
          <div className="flex items-center gap-1 text-xs text-gray-600 mb-1">
            <AlertCircle className="w-3 h-3" />
            {t("qualityDashboard.metric.holds")}
          </div>
          <div className="text-2xl font-bold text-gray-800">0</div>
        </div>
      </div>

      {/* Recent Checks table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <CheckCircle className="w-4 h-4 text-green-500" />
          {t("qualityDashboard.section.recent")}
        </div>
        {MOCK_QC_DATA.length === 0 ? (
          <p className="text-sm text-gray-400 italic p-4">{t("qualityDashboard.empty")}</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("qualityDashboard.col.operation")}</th>
                <th className="px-4 py-2 text-left">{t("qualityDashboard.col.result")}</th>
                <th className="px-4 py-2 text-left">{t("qualityDashboard.col.evaluator")}</th>
                <th className="px-4 py-2 text-left">{t("qualityDashboard.col.time")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {MOCK_QC_DATA.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-800">{row.operation}</div>
                    <div className="text-xs text-gray-500">{row.characteristic}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                      <CheckCircle className="w-3 h-3" />
                      {row.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{row.evaluator}</td>
                  <td className="px-4 py-3 text-xs text-gray-500">{row.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Quality Trends placeholder */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          <TrendingUp className="w-4 h-4 text-blue-500" />
          {t("qualityDashboard.section.trends")}
        </div>
        <div className="h-24 border-2 border-dashed border-gray-100 rounded-lg flex items-center justify-center text-sm text-gray-400">
          Quality trend chart — backend evaluation history required
        </div>
      </div>

      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ⚠ Quality evaluation and disposition results shown above are static demonstration data. Real quality decisions require backend quality domain integration.
      </p>
    </div>
  );
}

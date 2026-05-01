// Quality Holds — SHELL
// To-be visualization for supervisory review of quality holds.
// Quality hold release and approval are managed by the backend quality domain.

import { Lock, AlertTriangle, Clock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_HOLDS = [
  {
    id: "QH-001",
    item: "OP-010 (Turning) — WO-2026-001",
    reason: "DIM-A out of specification (25.8 vs 25±0.5)",
    status: "PENDING_REVIEW",
    placedAt: "2026-05-01 09:15",
    reviewedBy: null,
  },
];

export function QualityHolds() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("qualityHolds.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("qualityHolds.notice.shell")} />

      {/* Summary KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-red-50 rounded-lg border border-red-200 p-3">
          <div className="text-xs text-red-600 mb-1">{t("qualityHolds.metric.active")}</div>
          <div className="text-2xl font-bold text-red-800">{MOCK_HOLDS.filter((h) => h.status === "ACTIVE").length}</div>
        </div>
        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-3">
          <div className="text-xs text-yellow-600 mb-1">{t("qualityHolds.metric.pending")}</div>
          <div className="text-2xl font-bold text-yellow-800">{MOCK_HOLDS.filter((h) => h.status === "PENDING_REVIEW").length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3">
          <div className="text-xs text-gray-600 mb-1">Total Holds</div>
          <div className="text-2xl font-bold text-gray-800">{MOCK_HOLDS.length}</div>
        </div>
      </div>

      {/* Held Items table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <AlertTriangle className="w-4 h-4 text-red-500" />
          {t("qualityHolds.section.held")}
        </div>
        {MOCK_HOLDS.length === 0 ? (
          <p className="text-sm text-gray-400 italic p-4">{t("qualityHolds.empty")}</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.item")}</th>
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.reason")}</th>
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.timestamp")}</th>
                <th className="px-4 py-2 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {MOCK_HOLDS.map((hold) => (
                <tr key={hold.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-800">{hold.item}</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{hold.reason}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">
                      <Clock className="w-3 h-3" />
                      {hold.status === "PENDING_REVIEW" ? "Pending Review" : "Active"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">{hold.placedAt}</td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex justify-center gap-2">
                      <button
                        disabled
                        className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-gray-300 text-gray-600 cursor-not-allowed"
                        title={t("qualityHolds.hint.disabled")}
                      >
                        <Lock className="w-3 h-3" />
                        Release
                      </button>
                      <button
                        disabled
                        className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-gray-300 text-gray-600 cursor-not-allowed"
                        title={t("qualityHolds.hint.disabled")}
                      >
                        <Lock className="w-3 h-3" />
                        Approve
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ⚠ Quality hold status shown above is demonstration data. Real hold release and approval require backend quality hold management system.
      </p>
    </div>
  );
}

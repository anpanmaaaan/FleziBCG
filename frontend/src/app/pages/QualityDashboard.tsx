// Quality Lite Dashboard — PARTIAL (backend-connected)
// Connects to quality holds, deviations, and nonconformances APIs.
// Quality evaluation and disposition are managed by the backend quality domain.

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle, Clock, AlertTriangle, FileWarning } from "lucide-react";
import { toast } from "sonner";
import { ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { qualityApi } from "@/app/api/qualityApi";
import type { QualityHoldItem, QualityDeviationRequestItem, QualityNonconformanceItem } from "@/app/api/qualityApi";

function deviationStatusKey(status: string) {
  switch (status) {
    case "OPEN":
      return "qualityDashboard.status.open";
    case "APPROVED":
      return "qualityDashboard.status.approved";
    case "REJECTED":
      return "qualityDashboard.status.rejected";
    case "CLOSED":
      return "qualityDashboard.status.closed";
    default:
      return null;
  }
}

export function QualityDashboard() {
  const { t } = useI18n();
  const [holds, setHolds] = useState<QualityHoldItem[]>([]);
  const [deviations, setDeviations] = useState<QualityDeviationRequestItem[]>([]);
  const [nonconformances, setNonconformances] = useState<QualityNonconformanceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      qualityApi.listHolds(),
      qualityApi.listDeviations(),
      qualityApi.listNonconformances(),
    ])
      .then(([h, d, nc]) => {
        setHolds(h);
        setDeviations(d);
        setNonconformances(nc);
      })
      .catch(() => toast.error(t("qualityDashboard.error.loadFailed")))
      .finally(() => setLoading(false));
  }, [t]);

  const openHolds = holds.filter((h) => h.status === "ACTIVE");
  const pendingDeviations = deviations.filter((d) => d.status === "OPEN");

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("qualityDashboard.title")}
        </h1>
        <ScreenStatusBadge phase="PARTIAL" />
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-400 text-sm">{t("qualityDashboard.state.loading")}</div>
      ) : (
        <>
          {/* Summary KPI cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-red-50 rounded-lg border border-red-200 p-3">
              <div className="flex items-center gap-1 text-xs text-red-600 mb-1">
                <AlertCircle className="w-3 h-3" />
                {t("qualityDashboard.metric.holds")}
              </div>
              <div className="text-2xl font-bold text-red-800">{openHolds.length}</div>
            </div>
            <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-3">
              <div className="flex items-center gap-1 text-xs text-yellow-600 mb-1">
                <Clock className="w-3 h-3" />
                {t("qualityDashboard.metric.pending")}
              </div>
              <div className="text-2xl font-bold text-yellow-800">{pendingDeviations.length}</div>
            </div>
            <div className="bg-orange-50 rounded-lg border border-orange-200 p-3">
              <div className="flex items-center gap-1 text-xs text-orange-600 mb-1">
                <FileWarning className="w-3 h-3" />
                {t("qualityDashboard.metric.nonconformances")}
              </div>
              <div className="text-2xl font-bold text-orange-800">{nonconformances.length}</div>
            </div>
            <div className="bg-gray-50 rounded-lg border border-gray-200 p-3">
              <div className="flex items-center gap-1 text-xs text-gray-600 mb-1">
                <AlertTriangle className="w-3 h-3" />
                {t("qualityDashboard.metric.deviationsTotal")}
              </div>
              <div className="text-2xl font-bold text-gray-800">{deviations.length}</div>
            </div>
          </div>

          {/* Open Quality Holds */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
              <AlertCircle className="w-4 h-4 text-red-500" />
              {t("qualityDashboard.section.openHolds")} ({openHolds.length})
            </div>
            {openHolds.length === 0 ? (
              <p className="text-sm text-gray-400 italic p-4">{t("qualityDashboard.empty")}</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.operation")}</th>
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.reason")}</th>
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.status")}</th>
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.qtyHeld")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {openHolds.map((hold) => (
                    <tr key={hold.hold_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono text-xs">{hold.operation_id}</td>
                      <td className="px-4 py-3 text-gray-700">{hold.reason}</td>
                      <td className="px-4 py-3">
                        <span className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                          {hold.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-700">{t("common.na")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Deviations */}
          {deviations.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
                <Clock className="w-4 h-4 text-yellow-500" />
                {t("qualityDashboard.section.deviations")} ({deviations.length})
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.operation")}</th>
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.justification")}</th>
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.status")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {deviations.map((dev) => (
                    <tr key={dev.deviation_request_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono text-xs">{dev.hold_id}</td>
                      <td className="px-4 py-3 text-gray-700 max-w-xs truncate">{dev.reason}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${dev.status === "OPEN" ? "bg-yellow-100 text-yellow-700" : dev.status === "APPROVED" ? "bg-green-100 text-green-700" : dev.status === "REJECTED" ? "bg-red-100 text-red-700" : "bg-gray-100 text-gray-600"}`}>
                          {deviationStatusKey(dev.status) !== null ? t(deviationStatusKey(dev.status)!) : dev.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Nonconformances */}
          {nonconformances.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
                <FileWarning className="w-4 h-4 text-orange-500" />
                {t("qualityDashboard.section.nonconformances")} ({nonconformances.length})
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.operation")}</th>
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.description")}</th>
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.status")}</th>
                    <th className="px-4 py-2 text-left">{t("qualityDashboard.col.qty")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {nonconformances.map((nc) => (
                    <tr key={nc.nonconformance_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono text-xs">{nc.operation_id}</td>
                      <td className="px-4 py-3 text-gray-700 max-w-xs truncate">{nc.description}</td>
                      <td className="px-4 py-3">
                        <span className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
                          {nc.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-700">{nc.severity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {holds.length === 0 && deviations.length === 0 && nonconformances.length === 0 && (
            <div className="p-8 text-center text-gray-400 text-sm">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-400" />
              {t("qualityDashboard.state.noActiveIssues")}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// Material Readiness — SHELL
// To-be visualization for execution readiness planning based on material availability.
// Inventory truth and material availability are managed by backend inventory/material system.

import { Package, AlertTriangle, CheckCircle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_READINESS_DATA = [
  { operation: "OP-010", component: "Raw Material Steel", status: "READY", qty: "OK", daysSupply: "5" },
  { operation: "OP-010", component: "Cutting Tool — Insert A", status: "READY", qty: "OK", daysSupply: "3" },
  { operation: "OP-020", component: "Raw Material Steel", status: "SHORT", qty: "INSUFFICIENT", daysSupply: "1" },
  { operation: "OP-020", component: "Coolant", status: "READY", qty: "OK", daysSupply: "10" },
  { operation: "OP-030", component: "Fastener M8", status: "PENDING", qty: "ON_ORDER", daysSupply: "0" },
];

export function MaterialReadiness() {
  const { t } = useI18n();

  const readyCount = MOCK_READINESS_DATA.filter((r) => r.status === "READY").length;
  const shortCount = MOCK_READINESS_DATA.filter((r) => r.status === "SHORT").length;
  const pendingCount = MOCK_READINESS_DATA.filter((r) => r.status === "PENDING").length;

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("materialReadiness.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("materialReadiness.notice.shell")} />

      {/* Summary KPI cards */}
      <div className="grid grid-cols-3 md:grid-cols-3 gap-3">
        <div className="bg-green-50 rounded-lg border border-green-200 p-3">
          <div className="flex items-center gap-1 text-xs text-green-600 mb-1">
            <CheckCircle className="w-3 h-3" />
            {t("materialReadiness.metric.ready")}
          </div>
          <div className="text-2xl font-bold text-green-800">{readyCount}</div>
        </div>
        <div className="bg-red-50 rounded-lg border border-red-200 p-3">
          <div className="flex items-center gap-1 text-xs text-red-600 mb-1">
            <AlertTriangle className="w-3 h-3" />
            {t("materialReadiness.metric.short")}
          </div>
          <div className="text-2xl font-bold text-red-800">{shortCount}</div>
        </div>
        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-3">
          <div className="text-xs text-yellow-600 mb-1">{t("materialReadiness.metric.pending")}</div>
          <div className="text-2xl font-bold text-yellow-800">{pendingCount}</div>
        </div>
      </div>

      {/* Material Status table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Package className="w-4 h-4 text-purple-500" />
          {t("materialReadiness.section.byOperation")}
        </div>
        {MOCK_READINESS_DATA.length === 0 ? (
          <p className="text-sm text-gray-400 italic p-4">{t("materialReadiness.empty")}</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("materialReadiness.col.operation")}</th>
                <th className="px-4 py-2 text-left">{t("materialReadiness.col.component")}</th>
                <th className="px-4 py-2 text-left">{t("materialReadiness.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("materialReadiness.col.qty")}</th>
                <th className="px-4 py-2 text-right">Days Supply</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {MOCK_READINESS_DATA.map((row, idx) => {
                let statusColor = "gray";
                if (row.status === "READY") statusColor = "green";
                if (row.status === "SHORT") statusColor = "red";
                if (row.status === "PENDING") statusColor = "yellow";

                return (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-800">{row.operation}</td>
                    <td className="px-4 py-3 text-gray-600">{row.component}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-${statusColor}-100 text-${statusColor}-700`}>
                        {row.status === "READY" && <CheckCircle className="w-3 h-3 mr-1" />}
                        {row.status === "SHORT" && <AlertTriangle className="w-3 h-3 mr-1" />}
                        {row.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{row.qty}</td>
                    <td className="px-4 py-3 text-right text-sm font-mono text-gray-700">{row.daysSupply}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <p className="text-xs text-blue-700 bg-blue-50 border border-blue-200 rounded px-3 py-2">
        ℹ {t("materialReadiness.hint.backend")}
      </p>
    </div>
  );
}

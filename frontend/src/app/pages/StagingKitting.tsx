// Staging & Kitting — SHELL
// To-be visualization for material preparation and staging workflows.
// WMS transactions and material movements are managed by backend inventory/material system.

import { useState } from "react";
import { Lock, Box, AlertTriangle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_KITS = [
  { kitId: "KIT-001", workOrder: "WO-2026-001", station: "Machining Center 1", status: "STAGED", components: 5 },
  { kitId: "KIT-002", workOrder: "WO-2026-002", station: "Assembly Line 1", status: "IN_PROGRESS", components: 3 },
  { kitId: "KIT-003", workOrder: "WO-2026-003", station: "Grinding Station", status: "PENDING", components: 4 },
];

export function StagingKitting() {
  const { t } = useI18n();
  const [stationFilter, setStationFilter] = useState<string>("ALL");

  const stations = ["ALL", ...Array.from(new Set(MOCK_KITS.map((k) => k.station)))];
  const filtered = stationFilter === "ALL" ? MOCK_KITS : MOCK_KITS.filter((k) => k.station === stationFilter);

  const getStatusColor = (status: string) => {
    if (status === "STAGED") return "bg-green-100 text-green-700";
    if (status === "IN_PROGRESS") return "bg-blue-100 text-blue-700";
    if (status === "PENDING") return "bg-yellow-100 text-yellow-700";
    return "bg-gray-100 text-gray-700";
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("stagingKitting.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("stagingKitting.notice.shell")} />

      {/* Filter */}
      <div className="flex items-center gap-3">
        <select
          value={stationFilter}
          onChange={(e) => setStationFilter(e.target.value)}
          className="text-sm border border-gray-200 rounded px-3 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
          aria-label={t("stagingKitting.col.station")}
        >
          {stations.map((s) => (
            <option key={s} value={s}>
              {s === "ALL" ? "All Stations" : s}
            </option>
          ))}
        </select>
      </div>

      {/* Kit List table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Box className="w-4 h-4 text-purple-500" />
          {t("stagingKitting.section.kits")}
        </div>
        {filtered.length === 0 ? (
          <p className="text-sm text-gray-400 italic p-4">{t("stagingKitting.empty")}</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("stagingKitting.col.kit")}</th>
                <th className="px-4 py-2 text-left">{t("stagingKitting.col.workOrder")}</th>
                <th className="px-4 py-2 text-left">{t("stagingKitting.col.station")}</th>
                <th className="px-4 py-2 text-left">{t("stagingKitting.col.status")}</th>
                <th className="px-4 py-2 text-center">Components</th>
                <th className="px-4 py-2 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((kit) => (
                <tr key={kit.kitId} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">{kit.kitId}</td>
                  <td className="px-4 py-3 text-gray-600">{kit.workOrder}</td>
                  <td className="px-4 py-3 text-gray-600">{kit.station}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(kit.status)}`}>
                      {kit.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center text-gray-700">{kit.components}</td>
                  <td className="px-4 py-3 text-center">
                    <button
                      disabled
                      className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-gray-300 text-gray-600 cursor-not-allowed mx-auto"
                      title="Backend WMS required"
                    >
                      <Lock className="w-3 h-3" />
                      Confirm
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ⚠ Kit staging status and material transactions shown above are static demonstration data. Real material movement requires backend WMS and material flow integration.
      </p>
    </div>
  );
}

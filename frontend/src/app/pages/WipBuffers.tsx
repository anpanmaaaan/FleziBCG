// WIP Queue & Buffers — SHELL
// To-be visualization of work-in-progress queue and buffer status.
// WIP position and flow are managed by backend inventory/material system.

import { useState } from "react";
import { Activity, AlertTriangle, Clock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_WIP_DATA = [
  { buffer: "Pre-Machining", workOrder: "WO-2026-001", qty: "45", status: "QUEUED", ageMin: "125" },
  { buffer: "Pre-Machining", workOrder: "WO-2026-002", qty: "30", status: "IN_WORK", ageMin: "45" },
  { buffer: "Post-Machining", workOrder: "WO-2026-001", qty: "45", status: "QUEUED", ageMin: "15" },
  { buffer: "Quality Hold", workOrder: "WO-2026-003", qty: "20", status: "HELD", ageMin: "180" },
  { buffer: "Assembly", workOrder: "WO-2026-002", qty: "28", status: "IN_WORK", ageMin: "20" },
];

export function WipBuffers() {
  const { t } = useI18n();
  const [bufferFilter, setBufferFilter] = useState<string>("ALL");

  const buffers = ["ALL", ...Array.from(new Set(MOCK_WIP_DATA.map((w) => w.buffer)))];
  const filtered = bufferFilter === "ALL" ? MOCK_WIP_DATA : MOCK_WIP_DATA.filter((w) => w.buffer === bufferFilter);

  const totalWip = MOCK_WIP_DATA.reduce((sum, w) => sum + parseInt(w.qty, 10), 0);
  const queuedWip = MOCK_WIP_DATA.filter((w) => w.status === "QUEUED").reduce((sum, w) => sum + parseInt(w.qty, 10), 0);
  const inBufferWip = MOCK_WIP_DATA.filter((w) => w.status === "IN_WORK" || w.status === "HELD").reduce((sum, w) => sum + parseInt(w.qty, 10), 0);

  const getStatusColor = (status: string) => {
    if (status === "IN_WORK") return "bg-green-100 text-green-700";
    if (status === "QUEUED") return "bg-blue-100 text-blue-700";
    if (status === "HELD") return "bg-red-100 text-red-700";
    return "bg-gray-100 text-gray-700";
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("wipBuffers.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("wipBuffers.notice.shell")} />

      {/* Summary KPI cards */}
      <div className="grid grid-cols-3 md:grid-cols-3 gap-3">
        <div className="bg-white rounded-lg border border-gray-200 p-3">
          <div className="flex items-center gap-1 text-xs text-gray-600 mb-1">
            <Activity className="w-3 h-3" />
            {t("wipBuffers.metric.total")}
          </div>
          <div className="text-2xl font-bold text-gray-800">{totalWip}</div>
        </div>
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-3">
          <div className="flex items-center gap-1 text-xs text-blue-600 mb-1">
            <Clock className="w-3 h-3" />
            {t("wipBuffers.metric.queued")}
          </div>
          <div className="text-2xl font-bold text-blue-800">{queuedWip}</div>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-3">
          <div className="text-xs text-green-600 mb-1">{t("wipBuffers.metric.inBuffer")}</div>
          <div className="text-2xl font-bold text-green-800">{inBufferWip}</div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-3">
        <select
          value={bufferFilter}
          onChange={(e) => setBufferFilter(e.target.value)}
          className="text-sm border border-gray-200 rounded px-3 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
          aria-label={t("wipBuffers.col.buffer")}
        >
          {buffers.map((b) => (
            <option key={b} value={b}>
              {b === "ALL" ? "All Buffers" : b}
            </option>
          ))}
        </select>
      </div>

      {/* WIP table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Activity className="w-4 h-4 text-purple-500" />
          {t("wipBuffers.section.byBuffer")}
        </div>
        {filtered.length === 0 ? (
          <p className="text-sm text-gray-400 italic p-4">{t("wipBuffers.empty")}</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("wipBuffers.col.buffer")}</th>
                <th className="px-4 py-2 text-left">{t("wipBuffers.col.workOrder")}</th>
                <th className="px-4 py-2 text-right">{t("wipBuffers.col.qty")}</th>
                <th className="px-4 py-2 text-left">{t("wipBuffers.col.status")}</th>
                <th className="px-4 py-2 text-right">{t("wipBuffers.col.ageMin")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-600">{row.buffer}</td>
                  <td className="px-4 py-3 font-medium text-gray-800">{row.workOrder}</td>
                  <td className="px-4 py-3 text-right font-mono font-bold text-gray-800">{row.qty}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(row.status)}`}>
                      {row.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600">{row.ageMin}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <p className="text-xs text-blue-700 bg-blue-50 border border-blue-200 rounded px-3 py-2">
        ℹ {t("wipBuffers.hint.backend")}
      </p>
    </div>
  );
}

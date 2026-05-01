// Line Monitor — SHELL
// To-be visualization of production line station states.
// Live line/station state is provided by the backend execution projection system.

import { useState } from "react";
import { MonitorCheck, AlertTriangle, Clock, CheckCircle, Pause } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface MockStationCard {
  id: string;
  name: string;
  line: string;
  status: "RUNNING" | "IDLE" | "DOWNTIME" | "BLOCKED";
  operator?: string;
  currentOp?: string;
  wipCount: number;
  downtimeMin: number;
}

const MOCK_STATIONS: MockStationCard[] = [
  {
    id: "ST-01",
    name: "Machining Center 1",
    line: "LINE-A",
    status: "RUNNING",
    operator: "J. Smith",
    currentOp: "OP-010 Bore Drilling",
    wipCount: 3,
    downtimeMin: 0,
  },
  {
    id: "ST-02",
    name: "Machining Center 2",
    line: "LINE-A",
    status: "DOWNTIME",
    operator: "K. Tanaka",
    currentOp: "OP-010 Bore Drilling",
    wipCount: 0,
    downtimeMin: 22,
  },
  {
    id: "ST-03",
    name: "Assembly Line 1",
    line: "LINE-B",
    status: "RUNNING",
    operator: "M. Lee",
    currentOp: "OP-020 Gear Assembly",
    wipCount: 5,
    downtimeMin: 0,
  },
  {
    id: "ST-04",
    name: "Grinding Station",
    line: "LINE-B",
    status: "BLOCKED",
    operator: "A. Chen",
    currentOp: "OP-030 Surface Grind",
    wipCount: 2,
    downtimeMin: 0,
  },
  {
    id: "ST-05",
    name: "QC Station 1",
    line: "LINE-A",
    status: "IDLE",
    wipCount: 0,
    downtimeMin: 0,
  },
  {
    id: "ST-06",
    name: "Welding Station",
    line: "LINE-C",
    status: "RUNNING",
    operator: "R. Singh",
    currentOp: "OP-015 Frame Weld",
    wipCount: 1,
    downtimeMin: 0,
  },
];

function getStatusColor(status: MockStationCard["status"]): string {
  switch (status) {
    case "RUNNING":
      return "border-green-300 bg-green-50";
    case "IDLE":
      return "border-gray-200 bg-gray-50";
    case "DOWNTIME":
      return "border-amber-300 bg-amber-50";
    case "BLOCKED":
      return "border-red-300 bg-red-50";
  }
}

function getStatusBadge(status: MockStationCard["status"], labels: Record<string, string>) {
  switch (status) {
    case "RUNNING":
      return (
        <span className="flex items-center gap-1 text-xs font-medium text-green-700 bg-green-100 px-2 py-0.5 rounded-full">
          <CheckCircle className="w-3 h-3" />
          {labels.running}
        </span>
      );
    case "IDLE":
      return (
        <span className="flex items-center gap-1 text-xs font-medium text-gray-600 bg-gray-100 px-2 py-0.5 rounded-full">
          <Pause className="w-3 h-3" />
          {labels.idle}
        </span>
      );
    case "DOWNTIME":
      return (
        <span className="flex items-center gap-1 text-xs font-medium text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">
          <Clock className="w-3 h-3" />
          {labels.downtime}
        </span>
      );
    case "BLOCKED":
      return (
        <span className="flex items-center gap-1 text-xs font-medium text-red-700 bg-red-100 px-2 py-0.5 rounded-full">
          <AlertTriangle className="w-3 h-3" />
          {labels.blocked}
        </span>
      );
  }
}

export function LineMonitor() {
  const { t } = useI18n();
  const [lineFilter, setLineFilter] = useState<string>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const lines = ["ALL", ...Array.from(new Set(MOCK_STATIONS.map((s) => s.line)))];
  const statuses = ["ALL", "RUNNING", "IDLE", "DOWNTIME", "BLOCKED"];

  const filtered = MOCK_STATIONS.filter((s) => {
    const lineMatch = lineFilter === "ALL" || s.line === lineFilter;
    const statusMatch = statusFilter === "ALL" || s.status === statusFilter;
    return lineMatch && statusMatch;
  });

  const statusLabels = {
    running: t("lineMonitor.legend.running"),
    idle: t("lineMonitor.legend.idle"),
    downtime: t("lineMonitor.legend.downtime"),
    blocked: t("lineMonitor.legend.blocked"),
  };

  const runningCount = MOCK_STATIONS.filter((s) => s.status === "RUNNING").length;
  const downtimeCount = MOCK_STATIONS.filter((s) => s.status === "DOWNTIME").length;
  const blockedCount = MOCK_STATIONS.filter((s) => s.status === "BLOCKED").length;

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("lineMonitor.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("lineMonitor.notice.shell")} />

      {/* Overview summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-white rounded-lg border border-gray-200 p-3 text-center">
          <div className="text-2xl font-bold text-gray-800">{MOCK_STATIONS.length}</div>
          <div className="text-xs text-gray-500 mt-1">Total Stations</div>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-3 text-center">
          <div className="text-2xl font-bold text-green-700">{runningCount}</div>
          <div className="text-xs text-green-600 mt-1">{t("lineMonitor.legend.running")}</div>
        </div>
        <div className="bg-amber-50 rounded-lg border border-amber-200 p-3 text-center">
          <div className="text-2xl font-bold text-amber-700">{downtimeCount}</div>
          <div className="text-xs text-amber-600 mt-1">{t("lineMonitor.legend.downtime")}</div>
        </div>
        <div className="bg-red-50 rounded-lg border border-red-200 p-3 text-center">
          <div className="text-2xl font-bold text-red-700">{blockedCount}</div>
          <div className="text-xs text-red-600 mt-1">{t("lineMonitor.legend.blocked")}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <select
          value={lineFilter}
          onChange={(e) => setLineFilter(e.target.value)}
          className="text-sm border border-gray-200 rounded px-3 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
          aria-label={t("lineMonitor.filter.line")}
        >
          {lines.map((l) => (
            <option key={l} value={l}>
              {l === "ALL" ? t("lineMonitor.filter.line") : l}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="text-sm border border-gray-200 rounded px-3 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
          aria-label={t("lineMonitor.filter.status")}
        >
          {statuses.map((s) => (
            <option key={s} value={s}>
              {s === "ALL" ? t("lineMonitor.filter.status") : s}
            </option>
          ))}
        </select>
      </div>

      {/* Station cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.length === 0 ? (
          <p className="text-sm text-gray-400 italic col-span-full">{t("lineMonitor.empty")}</p>
        ) : (
          filtered.map((station) => (
            <div
              key={station.id}
              className={`rounded-lg border-2 p-4 flex flex-col gap-2 ${getStatusColor(station.status)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <MonitorCheck className="w-4 h-4 text-gray-600" />
                  <span className="font-medium text-gray-800 text-sm">{station.name}</span>
                </div>
                {getStatusBadge(station.status, statusLabels)}
              </div>
              <div className="text-xs text-gray-500">{station.line}</div>
              <div className="grid grid-cols-2 gap-1 text-xs mt-1">
                <div>
                  <span className="text-gray-500">{t("lineMonitor.col.operator")}: </span>
                  <span className="text-gray-700">{station.operator ?? "—"}</span>
                </div>
                <div>
                  <span className="text-gray-500">{t("lineMonitor.col.wip")}: </span>
                  <span className="text-gray-700">{station.wipCount}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-500">{t("lineMonitor.col.currentOp")}: </span>
                  <span className="text-gray-700">{station.currentOp ?? "—"}</span>
                </div>
                {station.downtimeMin > 0 && (
                  <div className="col-span-2">
                    <span className="text-amber-600">{t("lineMonitor.col.downtime")}: {station.downtimeMin} min</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ⚠ The station data shown above is static demonstration data. Live station state requires backend execution projection integration.
      </p>
    </div>
  );
}

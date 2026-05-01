// Station Monitor — SHELL
// To-be visualization of a single station's execution state, queue, and metrics.
// Live station state is provided by the backend execution projection system.

import { useState } from "react";
import { MonitorCheck, Clock, AlertTriangle, CheckCircle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_STATION_LIST = [
  { id: "ST-01", name: "Machining Center 1" },
  { id: "ST-02", name: "Machining Center 2" },
  { id: "ST-03", name: "Assembly Line 1" },
  { id: "ST-04", name: "Grinding Station" },
  { id: "ST-05", name: "QC Station 1" },
];

interface MockQueueItem {
  operationId: string;
  operationCode: string;
  operationName: string;
  workOrderNumber: string;
  priority: "High" | "Normal" | "Low";
  plannedStart: string;
  status: "WAITING" | "IN_PROGRESS" | "BLOCKED";
}

const MOCK_QUEUE: MockQueueItem[] = [
  {
    operationId: "OP-001",
    operationCode: "OP-010",
    operationName: "Bore Drilling",
    workOrderNumber: "WO-2026-001",
    priority: "High",
    plannedStart: "2026-05-01 08:00",
    status: "IN_PROGRESS",
  },
  {
    operationId: "OP-002",
    operationCode: "OP-020",
    operationName: "Surface Milling",
    workOrderNumber: "WO-2026-002",
    priority: "Normal",
    plannedStart: "2026-05-01 10:00",
    status: "WAITING",
  },
  {
    operationId: "OP-003",
    operationCode: "OP-010",
    operationName: "Bore Drilling",
    workOrderNumber: "WO-2026-003",
    priority: "Low",
    plannedStart: "2026-05-01 12:00",
    status: "WAITING",
  },
];

function getPriorityBadge(priority: MockQueueItem["priority"]) {
  const map = {
    High: "text-red-700 bg-red-100",
    Normal: "text-blue-700 bg-blue-100",
    Low: "text-gray-600 bg-gray-100",
  };
  return <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${map[priority]}`}>{priority}</span>;
}

function getQueueStatusIcon(status: MockQueueItem["status"]) {
  switch (status) {
    case "IN_PROGRESS":
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    case "BLOCKED":
      return <AlertTriangle className="w-4 h-4 text-red-500" />;
    default:
      return <Clock className="w-4 h-4 text-gray-400" />;
  }
}

export function StationMonitor() {
  const { t } = useI18n();
  const [selectedStation, setSelectedStation] = useState<string>("");

  const station = MOCK_STATION_LIST.find((s) => s.id === selectedStation);

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("stationMonitor.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("stationMonitor.notice.shell")} />

      {/* Station selector */}
      <div className="flex items-center gap-3">
        <select
          value={selectedStation}
          onChange={(e) => setSelectedStation(e.target.value)}
          className="text-sm border border-gray-200 rounded px-3 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
          aria-label={t("stationMonitor.filter.station")}
        >
          <option value="">{t("stationMonitor.filter.station")}</option>
          {MOCK_STATION_LIST.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </div>

      {!selectedStation ? (
        <p className="text-sm text-gray-400 italic">{t("stationMonitor.empty")}</p>
      ) : (
        <>
          {/* Station overview */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
              <MonitorCheck className="w-4 h-4 text-blue-500" />
              {t("stationMonitor.section.station")}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div>
                <span className="text-gray-500 text-xs">Station</span>
                <div className="text-gray-800 font-medium">{station?.name}</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs">ID</span>
                <div className="text-gray-800">{selectedStation}</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs">Status</span>
                <div className="text-green-700 font-medium">RUNNING</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs">Operator</span>
                <div className="text-gray-800">J. Smith</div>
              </div>
            </div>
          </div>

          {/* Metrics */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
              {t("stationMonitor.section.metrics")}
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-xl font-bold text-gray-800">82%</div>
                <div className="text-xs text-gray-500">{t("stationMonitor.metrics.utilization")}</div>
              </div>
              <div>
                <div className="text-xl font-bold text-amber-700">22 min</div>
                <div className="text-xs text-gray-500">{t("stationMonitor.metrics.downtime")}</div>
              </div>
              <div>
                <div className="text-xl font-bold text-blue-700">18 pcs</div>
                <div className="text-xs text-gray-500">{t("stationMonitor.metrics.throughput")}</div>
              </div>
            </div>
          </div>

          {/* Operation Queue */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
              {t("stationMonitor.section.queue")}
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                  <th className="px-4 py-2 text-left">{t("stationMonitor.col.operation")}</th>
                  <th className="px-4 py-2 text-left">{t("stationMonitor.col.priority")}</th>
                  <th className="px-4 py-2 text-left">{t("stationMonitor.col.plannedStart")}</th>
                  <th className="px-4 py-2 text-left">{t("stationMonitor.col.status")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {MOCK_QUEUE.map((item) => (
                  <tr key={item.operationId} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-800">{item.operationCode}</div>
                      <div className="text-xs text-gray-500">{item.operationName}</div>
                      <div className="text-xs text-gray-400">{item.workOrderNumber}</div>
                    </td>
                    <td className="px-4 py-3">{getPriorityBadge(item.priority)}</td>
                    <td className="px-4 py-3 text-gray-600 font-mono text-xs">{item.plannedStart}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        {getQueueStatusIcon(item.status)}
                        <span className="text-xs text-gray-600">{item.status}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ⚠ The station data and queue shown above is static demonstration data. Live station state requires backend execution projection integration.
      </p>
    </div>
  );
}

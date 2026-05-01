// Downtime Analysis — SHELL
// To-be visualization of downtime breakdown by reason, station, and trend.
// Downtime truth is recorded by the backend execution system.

import { useState } from "react";
import { AlertTriangle, BarChart3, Clock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface MockDowntimeRow {
  reasonCode: string;
  reasonName: string;
  station: string;
  durationMin: number;
  occurrences: number;
  percentageOfTotal: number;
}

const MOCK_DOWNTIME_DATA: MockDowntimeRow[] = [
  {
    reasonCode: "DT-TOOL",
    reasonName: "Tool Change",
    station: "Machining Center 1",
    durationMin: 45,
    occurrences: 3,
    percentageOfTotal: 31.0,
  },
  {
    reasonCode: "DT-MAINT",
    reasonName: "Scheduled Maintenance",
    station: "Machining Center 2",
    durationMin: 60,
    occurrences: 1,
    percentageOfTotal: 41.4,
  },
  {
    reasonCode: "DT-SETUP",
    reasonName: "Setup / Changeover",
    station: "Assembly Line 1",
    durationMin: 20,
    occurrences: 2,
    percentageOfTotal: 13.8,
  },
  {
    reasonCode: "DT-WAIT",
    reasonName: "Waiting for Material",
    station: "Grinding Station",
    durationMin: 20,
    occurrences: 2,
    percentageOfTotal: 13.8,
  },
];

const TOTAL_DOWNTIME_MIN = MOCK_DOWNTIME_DATA.reduce((a, r) => a + r.durationMin, 0);
const TOP_REASON = MOCK_DOWNTIME_DATA.reduce((a, b) => (a.durationMin > b.durationMin ? a : b));

export function DowntimeAnalysis() {
  const { t } = useI18n();
  const [stationFilter, setStationFilter] = useState<string>("ALL");

  const stations = ["ALL", ...Array.from(new Set(MOCK_DOWNTIME_DATA.map((r) => r.station)))];
  const filtered = stationFilter === "ALL"
    ? MOCK_DOWNTIME_DATA
    : MOCK_DOWNTIME_DATA.filter((r) => r.station === stationFilter);

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("downtimeAnalysis.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("downtimeAnalysis.notice.shell")} />

      {/* Summary KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-white rounded-lg border border-amber-200 p-3">
          <div className="text-xs text-gray-500">{t("downtimeAnalysis.metric.totalDowntime")}</div>
          <div className="text-2xl font-bold text-amber-700 mt-1">{TOTAL_DOWNTIME_MIN} min</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3">
          <div className="text-xs text-gray-500">{t("downtimeAnalysis.metric.avgPerEvent")}</div>
          <div className="text-2xl font-bold text-gray-800 mt-1">
            {Math.round(TOTAL_DOWNTIME_MIN / MOCK_DOWNTIME_DATA.reduce((a, r) => a + r.occurrences, 0))} min
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3">
          <div className="text-xs text-gray-500">{t("downtimeAnalysis.metric.topReason")}</div>
          <div className="text-sm font-bold text-gray-800 mt-1 truncate">{TOP_REASON.reasonName}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3">
          <div className="text-xs text-gray-500">{t("downtimeAnalysis.metric.affectedStations")}</div>
          <div className="text-2xl font-bold text-gray-800 mt-1">
            {new Set(MOCK_DOWNTIME_DATA.map((r) => r.station)).size}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <select
          value={stationFilter}
          onChange={(e) => setStationFilter(e.target.value)}
          className="text-sm border border-gray-200 rounded px-3 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
          aria-label={t("downtimeAnalysis.filter.station")}
        >
          {stations.map((s) => (
            <option key={s} value={s}>
              {s === "ALL" ? t("downtimeAnalysis.filter.station") : s}
            </option>
          ))}
        </select>
        <div className="text-xs text-gray-500 italic">
          Date range and reason code filters — Backend analytics API required
        </div>
      </div>

      {/* By Reason Code table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <AlertTriangle className="w-4 h-4 text-amber-500" />
          {t("downtimeAnalysis.section.byReason")}
        </div>
        {filtered.length === 0 ? (
          <p className="text-sm text-gray-400 italic p-4">{t("downtimeAnalysis.empty")}</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("downtimeAnalysis.col.reason")}</th>
                <th className="px-4 py-2 text-left">{t("downtimeAnalysis.col.station")}</th>
                <th className="px-4 py-2 text-right">{t("downtimeAnalysis.col.duration")}</th>
                <th className="px-4 py-2 text-right">{t("downtimeAnalysis.col.count")}</th>
                <th className="px-4 py-2 text-right">{t("downtimeAnalysis.col.percentage")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((row) => (
                <tr key={`${row.reasonCode}-${row.station}`} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-800">{row.reasonCode}</div>
                    <div className="text-xs text-gray-500">{row.reasonName}</div>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">{row.station}</td>
                  <td className="px-4 py-3 text-right font-mono text-gray-700">{row.durationMin}</td>
                  <td className="px-4 py-3 text-right text-gray-700">{row.occurrences}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-16 bg-gray-100 rounded-full h-1.5">
                        <div
                          className="bg-amber-400 h-1.5 rounded-full"
                          style={{ width: `${row.percentageOfTotal}%` }}
                        />
                      </div>
                      <span className="text-gray-700 text-xs font-mono">{row.percentageOfTotal.toFixed(1)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Trend placeholder */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          <BarChart3 className="w-4 h-4 text-blue-500" />
          {t("downtimeAnalysis.section.trend")}
        </div>
        <div className="h-24 border-2 border-dashed border-gray-100 rounded-lg flex items-center justify-center text-sm text-gray-400">
          Downtime trend chart — backend analytics projection required
        </div>
      </div>

      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ⚠ The downtime data shown above is static demonstration data. Real downtime analysis requires backend execution event and analytics API integration.
      </p>
    </div>
  );
}

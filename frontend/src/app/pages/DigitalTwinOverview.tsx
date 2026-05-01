// Operational Digital Twin Overview — SHELL
// Static demo visualization of plant/line/station twin objects.
// Live twin sync requires backend deterministic projection and validated twin model.
// This screen does NOT show live operational state. All cards are static demo placeholders.

import { Layers, MapPin, Activity, RefreshCw, Lock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_TWIN_OBJECTS = [
  { id: "TW-PLANT-01", type: "Plant", name: "Plant A", children: 2, syncStatus: "Not Live" },
  { id: "TW-LINE-01", type: "Line", name: "Line A", children: 4, syncStatus: "Not Live" },
  { id: "TW-LINE-02", type: "Line", name: "Line B", children: 3, syncStatus: "Not Live" },
  { id: "TW-STATION-01", type: "Station", name: "WS-01", children: 0, syncStatus: "Not Live" },
  { id: "TW-STATION-02", type: "Station", name: "WS-02", children: 0, syncStatus: "Not Live" },
  { id: "TW-STATION-03", type: "Station", name: "QC-01", children: 0, syncStatus: "Not Live" },
];

export function DigitalTwinOverview() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("digitalTwinOverview.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("digitalTwinOverview.notice.shell")} />

      {/* Not Live banner */}
      <div className="rounded-lg border border-slate-300 bg-slate-100 px-4 py-3 flex items-center gap-3">
        <Activity className="w-4 h-4 text-slate-500 flex-shrink-0" />
        <span className="text-sm font-medium text-slate-700">{t("digitalTwinOverview.sync.notLive")}</span>
        <span className="ml-2 text-xs text-slate-500 italic">{t("digitalTwinOverview.sync.staticDemo")}</span>
        <button
          disabled
          className="ml-auto text-xs px-3 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-white flex items-center gap-1"
          title={t("digitalTwinOverview.action.sync.disabled")}
        >
          <Lock className="w-3 h-3" />
          <RefreshCw className="w-3 h-3" />
          {t("digitalTwinOverview.action.sync")}
        </button>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {[
          { icon: Layers, label: t("digitalTwinOverview.metric.twinObjects"), value: "—" },
          { icon: MapPin, label: t("digitalTwinOverview.metric.stations"), value: "—" },
          { icon: Activity, label: t("digitalTwinOverview.metric.syncHealth"), value: "—" },
        ].map(({ icon: Icon, label, value }) => (
          <div key={label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="flex items-center gap-1 text-xs text-slate-600 mb-1">
              <Icon className="w-3 h-3" />
              {label}
            </div>
            <div className="text-2xl font-bold text-slate-700">{value}</div>
          </div>
        ))}
      </div>

      {/* Twin object cards */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Layers className="w-4 h-4 text-teal-500" />
          {t("digitalTwinOverview.section.objects")}
          <span className="ml-2 text-xs font-normal text-slate-400 italic">({t("digitalTwinOverview.label.staticDemo")})</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 p-4">
          {MOCK_TWIN_OBJECTS.map((obj) => (
            <div key={obj.id} className="rounded-lg border border-slate-200 p-3 bg-slate-50">
              <div className="flex justify-between items-start mb-1">
                <span className="text-sm font-medium text-slate-800">{obj.name}</span>
                <span className="text-xs px-2 py-0.5 bg-slate-200 text-slate-600 rounded-full">{obj.type}</span>
              </div>
              <div className="text-xs text-slate-500 font-mono">{obj.id}</div>
              <div className="mt-2 flex items-center gap-1 text-xs text-slate-400">
                <Activity className="w-3 h-3" />
                <span className="italic">{obj.syncStatus}</span>
              </div>
              <div className="flex gap-1 mt-2">
                <button disabled className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-white flex items-center gap-1" title={t("digitalTwinOverview.action.refresh.disabled")}>
                  <Lock className="w-3 h-3" />{t("digitalTwinOverview.action.refresh")}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      <p className="text-xs text-slate-400">{t("digitalTwinOverview.hint.backend")}</p>
    </div>
  );
}

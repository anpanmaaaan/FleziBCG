// Twin State Graph — SHELL
// Static demo graph of equipment/station/operation/material relationships.
// Real twin state requires backend projection and validated equipment/material binding.
// Graph reflects static demo structure only — not validated operational state.

import { GitBranch, Lock, Info } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_NODES = [
  { id: "N-PLANT-01", type: "Plant", label: "Plant A", depth: 0 },
  { id: "N-LINE-01", type: "Line", label: "Line A", depth: 1 },
  { id: "N-LINE-02", type: "Line", label: "Line B", depth: 1 },
  { id: "N-WC-01", type: "WorkCenter", label: "WC-01", depth: 2 },
  { id: "N-WC-02", type: "WorkCenter", label: "WC-02", depth: 2 },
  { id: "N-WS-01", type: "Station", label: "WS-01", depth: 3 },
  { id: "N-WS-02", type: "Station", label: "WS-02", depth: 3 },
  { id: "N-QC-01", type: "Station", label: "QC-01", depth: 3 },
];

const TYPE_COLORS: Record<string, string> = {
  Plant: "bg-indigo-100 text-indigo-800 border-indigo-200",
  Line: "bg-teal-100 text-teal-800 border-teal-200",
  WorkCenter: "bg-sky-100 text-sky-800 border-sky-200",
  Station: "bg-slate-100 text-slate-700 border-slate-200",
};

export function TwinStateGraph() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("twinStateGraph.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("twinStateGraph.notice.shell")} />

      {/* Static demo notice */}
      <div className="rounded-lg border border-slate-300 bg-slate-100 px-4 py-3 flex items-start gap-3">
        <Info className="w-4 h-4 text-slate-500 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-slate-700">
          <span className="font-semibold">{t("twinStateGraph.label.staticDemo")}: </span>
          {t("twinStateGraph.staticDemo.description")}
        </div>
        <div className="ml-auto flex gap-1">
          <button disabled className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-white flex items-center gap-1" title={t("twinStateGraph.action.refresh.disabled")}>
            <Lock className="w-3 h-3" />{t("twinStateGraph.action.refresh")}
          </button>
          <button disabled className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-white flex items-center gap-1" title={t("twinStateGraph.action.validate.disabled")}>
            <Lock className="w-3 h-3" />{t("twinStateGraph.action.validate")}
          </button>
        </div>
      </div>

      {/* Graph placeholder — tree layout by depth */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <GitBranch className="w-4 h-4 text-teal-500" />
          {t("twinStateGraph.section.graph")}
          <span className="ml-2 text-xs font-normal text-slate-400 italic">({t("twinStateGraph.label.staticDemo")})</span>
        </div>
        <div className="p-4 overflow-x-auto">
          {/* Grouped by depth level as a simple visual tree */}
          {[0, 1, 2, 3].map((depth) => {
            const levelNodes = MOCK_NODES.filter((n) => n.depth === depth);
            if (levelNodes.length === 0) return null;
            return (
              <div key={depth} className="mb-4">
                <div className="text-xs text-slate-400 uppercase tracking-wide mb-2 px-1">
                  {t("twinStateGraph.label.level")} {depth}
                </div>
                <div className="flex gap-3 flex-wrap">
                  {levelNodes.map((node) => (
                    <div
                      key={node.id}
                      className={`rounded-lg border px-3 py-2 text-sm ${TYPE_COLORS[node.type] ?? "bg-slate-50 text-slate-700 border-slate-200"}`}
                    >
                      <div className="font-medium">{node.label}</div>
                      <div className="text-xs opacity-70">{node.type}</div>
                      <div className="text-xs font-mono opacity-50 mt-0.5">{node.id}</div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
          <p className="text-xs text-slate-400 mt-2 italic">{t("twinStateGraph.graph.placeholder")}</p>
        </div>
      </div>
    </div>
  );
}

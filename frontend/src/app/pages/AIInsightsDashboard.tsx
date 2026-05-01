// AI Insights Dashboard — SHELL
// Advisory intelligence visualization for internal product walkthrough.
// AI advisory outputs require validated ML models and backend AI inference service.
// This screen does NOT produce actionable AI decisions. Do not use for operational truth.

import { Brain, TrendingUp, AlertTriangle, Activity, Info } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_INSIGHTS = [
  {
    id: "INS-001",
    category: "Bottleneck",
    title: "Station WS-04 showing elevated cycle time deviation",
    confidence: "—",
    severity: "Medium",
    source: "Demo Advisory",
  },
  {
    id: "INS-002",
    category: "Anomaly",
    title: "Operator clock-off pattern outside expected window",
    confidence: "—",
    severity: "Low",
    source: "Demo Advisory",
  },
  {
    id: "INS-003",
    category: "Quality",
    title: "Defect rate trending upward on Line B",
    confidence: "—",
    severity: "High",
    source: "Demo Advisory",
  },
  {
    id: "INS-004",
    category: "OEE",
    title: "Planned vs actual throughput gap widening",
    confidence: "—",
    severity: "Medium",
    source: "Demo Advisory",
  },
];

export function AIInsightsDashboard() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("aiInsightsDashboard.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("aiInsightsDashboard.notice.shell")} />

      {/* Model status placeholder */}
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 flex items-start gap-3">
        <Info className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-amber-800">
          <span className="font-semibold">{t("aiInsightsDashboard.model.status.label")}: </span>
          <span className="italic">{t("aiInsightsDashboard.model.status.notReady")}</span>
          <span className="ml-2 text-xs text-amber-600">({t("aiInsightsDashboard.model.status.demo")})</span>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { icon: Brain, label: t("aiInsightsDashboard.metric.insights"), value: "—" },
          { icon: AlertTriangle, label: t("aiInsightsDashboard.metric.anomalies"), value: "—" },
          { icon: TrendingUp, label: t("aiInsightsDashboard.metric.bottlenecks"), value: "—" },
          { icon: Activity, label: t("aiInsightsDashboard.metric.modelScore"), value: "—" },
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

      {/* Advisory insight cards */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Brain className="w-4 h-4 text-violet-400" />
          {t("aiInsightsDashboard.section.insights")}
          <span className="ml-2 text-xs font-normal text-slate-400 italic">({t("aiInsightsDashboard.label.advisoryOnly")})</span>
        </div>
        <div className="divide-y divide-gray-50">
          {MOCK_INSIGHTS.map((ins) => (
            <div key={ins.id} className="px-4 py-3 flex items-start gap-3 bg-white hover:bg-slate-50">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-mono text-slate-400">{ins.id}</span>
                  <span className="text-xs px-1.5 py-0.5 bg-violet-100 text-violet-700 rounded">{ins.category}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    ins.severity === "High" ? "bg-red-100 text-red-700" :
                    ins.severity === "Medium" ? "bg-amber-100 text-amber-700" :
                    "bg-slate-100 text-slate-600"
                  }`}>{ins.severity}</span>
                </div>
                <div className="text-sm text-gray-800">{ins.title}</div>
                <div className="text-xs text-slate-400 mt-0.5 italic">{ins.source}</div>
              </div>
              <div className="text-right flex-shrink-0">
                <div className="text-xs text-slate-500">{t("aiInsightsDashboard.col.confidence")}</div>
                <div className="text-sm font-medium text-slate-600">{ins.confidence}</div>
              </div>
              <button
                disabled
                className="ml-2 text-xs px-3 py-1.5 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50"
                title={t("aiInsightsDashboard.action.apply.disabled")}
              >
                {t("aiInsightsDashboard.action.apply")}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Explanation placeholder */}
      <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
          <Activity className="w-4 h-4 text-slate-400" />
          {t("aiInsightsDashboard.section.explanation")}
        </div>
        <p className="text-sm text-slate-500 italic">{t("aiInsightsDashboard.explanation.placeholder")}</p>
        <p className="text-xs text-slate-400 mt-2">{t("aiInsightsDashboard.hint.backend")}</p>
      </div>
    </div>
  );
}

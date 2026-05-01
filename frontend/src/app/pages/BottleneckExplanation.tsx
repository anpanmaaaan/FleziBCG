// Bottleneck Explanation — SHELL
// Advisory bottleneck visualization for internal product walkthrough.
// Real bottleneck analysis requires backend execution projection and AI advisory service.
// AI may NOT influence execution directly. This screen is demo/advisory only.

import { Zap, MapPin, BarChart2, Lock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_BOTTLENECKS = [
  {
    id: "BTL-001",
    station: "WS-04",
    line: "Line A",
    rank: 1,
    likelyCause: "Insufficient operator availability",
    evidence: "Demo — cycle time data pending backend",
    affectedOrders: "—",
    impact: "Medium",
  },
  {
    id: "BTL-002",
    station: "QC-02",
    line: "Line B",
    rank: 2,
    likelyCause: "Measurement entry backlog",
    evidence: "Demo — QC throughput data pending backend",
    affectedOrders: "—",
    impact: "Low",
  },
];

export function BottleneckExplanation() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("bottleneckExplanation.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("bottleneckExplanation.notice.shell")} />

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {[
          { icon: Zap, label: t("bottleneckExplanation.metric.candidates"), value: "—" },
          { icon: MapPin, label: t("bottleneckExplanation.metric.affectedStations"), value: "—" },
          { icon: BarChart2, label: t("bottleneckExplanation.metric.avgImpact"), value: "—" },
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

      {/* Bottleneck candidate cards */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Zap className="w-4 h-4 text-orange-400" />
          {t("bottleneckExplanation.section.candidates")}
          <span className="ml-2 text-xs font-normal text-slate-400 italic">({t("bottleneckExplanation.label.demo")})</span>
        </div>
        <div className="divide-y divide-gray-50">
          {MOCK_BOTTLENECKS.map((b) => (
            <div key={b.id} className="px-4 py-4 flex flex-col gap-2">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-slate-400">{b.id}</span>
                    <span className="text-xs font-semibold text-orange-700 bg-orange-100 px-2 py-0.5 rounded">
                      #{b.rank} {t("bottleneckExplanation.label.rank")}
                    </span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      b.impact === "High" ? "bg-red-100 text-red-700" :
                      b.impact === "Medium" ? "bg-amber-100 text-amber-700" :
                      "bg-slate-100 text-slate-600"
                    }`}>{b.impact}</span>
                  </div>
                  <div className="text-sm font-medium text-slate-800">{b.station} — {b.line}</div>
                  <div className="text-sm text-slate-600 mt-0.5">{t("bottleneckExplanation.label.likelyCause")}: {b.likelyCause}</div>
                  <div className="text-xs text-slate-400 italic mt-0.5">{t("bottleneckExplanation.label.evidence")}: {b.evidence}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{t("bottleneckExplanation.col.affectedOrders")}: {b.affectedOrders}</div>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  <button
                    disabled
                    className="text-xs px-3 py-1.5 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1"
                    title={t("bottleneckExplanation.action.apply.disabled")}
                  >
                    <Lock className="w-3 h-3" />
                    {t("bottleneckExplanation.action.apply")}
                  </button>
                  <button
                    disabled
                    className="text-xs px-3 py-1.5 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1"
                    title={t("bottleneckExplanation.action.dispatch.disabled")}
                  >
                    <Lock className="w-3 h-3" />
                    {t("bottleneckExplanation.action.dispatch")}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      <p className="text-xs text-slate-400">{t("bottleneckExplanation.hint.backend")}</p>
    </div>
  );
}

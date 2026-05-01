// What-if Scenario — SHELL
// Demo scenario simulation layout for internal product walkthrough.
// Real scenario simulation requires backend APS/planning engine.
// Running scenarios here does NOT alter production plans.

import { FlaskConical, BarChart2, Lock, AlertTriangle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_ASSUMPTIONS = [
  { label: "Add 1 operator to WS-04 for shift", value: "Demo assumption" },
  { label: "Reduce batch size by 20%", value: "Demo assumption" },
  { label: "Extend shift by 2 hours", value: "Demo assumption" },
];

const MOCK_IMPACT_CARDS = [
  { label: "Throughput change", value: "—", positive: null },
  { label: "WIP reduction estimate", value: "—", positive: null },
  { label: "OEE change", value: "—", positive: null },
  { label: "Downtime change", value: "—", positive: null },
];

export function WhatIfScenario() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("whatIfScenario.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("whatIfScenario.notice.shell")} />

      {/* Future simulation notice */}
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-amber-800">{t("whatIfScenario.notice.futureSimulation")}</p>
      </div>

      {/* Scenario setup */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <FlaskConical className="w-4 h-4 text-blue-400" />
          {t("whatIfScenario.section.setup")}
        </div>
        <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">{t("whatIfScenario.setup.scenarioName")}</label>
            <input
              disabled
              className="w-full rounded border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
              placeholder={t("whatIfScenario.setup.scenarioName.placeholder")}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">{t("whatIfScenario.setup.baseline")}</label>
            <input
              disabled
              className="w-full rounded border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
              placeholder={t("whatIfScenario.setup.baseline.placeholder")}
            />
          </div>
        </div>
      </div>

      {/* Assumptions panel */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <FlaskConical className="w-4 h-4 text-slate-400" />
          {t("whatIfScenario.section.assumptions")}
          <span className="ml-2 text-xs font-normal text-slate-400 italic">({t("whatIfScenario.label.demo")})</span>
        </div>
        <div className="divide-y divide-gray-50">
          {MOCK_ASSUMPTIONS.map((a) => (
            <div key={a.label} className="px-4 py-2.5 flex items-center gap-3">
              <span className="text-sm text-slate-700 flex-1">{a.label}</span>
              <span className="text-xs text-slate-400 italic">{a.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Projected impact cards */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <BarChart2 className="w-4 h-4 text-blue-400" />
          {t("whatIfScenario.section.projectedImpact")}
          <span className="ml-2 text-xs font-normal bg-amber-100 text-amber-700 px-2 py-0.5 rounded">
            {t("whatIfScenario.label.demoProjection")}
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-4">
          {MOCK_IMPACT_CARDS.map((card) => (
            <div key={card.label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
              <div className="text-xs text-slate-600 mb-1">{card.label}</div>
              <div className="text-2xl font-bold text-slate-700">{card.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Disabled actions */}
      <div className="flex gap-2 flex-wrap">
        <button disabled className="flex items-center gap-1.5 text-sm px-4 py-2 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50" title={t("whatIfScenario.action.run.disabled")}>
          <Lock className="w-3.5 h-3.5" />{t("whatIfScenario.action.run")}
        </button>
        <button disabled className="flex items-center gap-1.5 text-sm px-4 py-2 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50" title={t("whatIfScenario.action.apply.disabled")}>
          <Lock className="w-3.5 h-3.5" />{t("whatIfScenario.action.apply")}
        </button>
      </div>
      <p className="text-xs text-slate-400">{t("whatIfScenario.hint.backend")}</p>
    </div>
  );
}

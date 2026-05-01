// AI Shift Summary — SHELL
// Advisory shift narrative visualization for internal product walkthrough.
// Official shift summary requires backend reporting, shift management modules, and
// supervisor approval workflows. AI narrative is advisory demo only.
// Do not use for operational truth, official handover, or compliance records.

import { FileText, CheckSquare, AlertCircle, Lock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SOURCE_CHECKLIST = [
  { label: "Production orders closed", status: false },
  { label: "Work order completions reconciled", status: false },
  { label: "Downtime events captured", status: false },
  { label: "Quality measurements submitted", status: false },
  { label: "Material consumption reconciled", status: false },
];

export function AIShiftSummary() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("aiShiftSummary.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("aiShiftSummary.notice.shell")} />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="text-xs text-slate-500 mb-1">{t("aiShiftSummary.meta.shift")}</div>
          <div className="text-sm font-medium text-slate-700">Morning — 2026-05-01</div>
          <div className="text-xs text-slate-400 italic">{t("aiShiftSummary.meta.demo")}</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="text-xs text-slate-500 mb-1">{t("aiShiftSummary.meta.line")}</div>
          <div className="text-sm font-medium text-slate-700">Line A — Demo</div>
          <div className="text-xs text-slate-400 italic">{t("aiShiftSummary.meta.demo")}</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="text-xs text-slate-500 mb-1">{t("aiShiftSummary.meta.status")}</div>
          <div className="text-sm font-medium text-amber-600">{t("aiShiftSummary.meta.statusPending")}</div>
        </div>
      </div>

      {/* AI narrative preview */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <FileText className="w-4 h-4 text-violet-400" />
          {t("aiShiftSummary.section.narrative")}
          <span className="ml-2 text-xs font-normal bg-amber-100 text-amber-700 px-2 py-0.5 rounded">
            {t("aiShiftSummary.label.demoAdvisory")}
          </span>
        </div>
        <div className="p-4">
          <p className="text-sm text-slate-500 italic leading-relaxed">
            {t("aiShiftSummary.narrative.placeholder")}
          </p>
          <p className="text-xs text-slate-400 mt-3">{t("aiShiftSummary.narrative.disclaimer")}</p>
        </div>
      </div>

      {/* Source data checklist */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <CheckSquare className="w-4 h-4 text-slate-400" />
          {t("aiShiftSummary.section.sourceChecklist")}
        </div>
        <div className="divide-y divide-gray-50">
          {MOCK_SOURCE_CHECKLIST.map((item) => (
            <div key={item.label} className="px-4 py-2.5 flex items-center gap-3">
              <div className={`w-4 h-4 rounded border ${item.status ? "bg-green-500 border-green-500" : "border-slate-300"} flex-shrink-0`} />
              <span className="text-sm text-slate-600">{item.label}</span>
              <span className="ml-auto text-xs text-slate-400 italic">{t("aiShiftSummary.source.pending")}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Review placeholder */}
      <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 flex items-start gap-3">
        <AlertCircle className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-slate-500 italic">{t("aiShiftSummary.review.placeholder")}</div>
      </div>

      {/* Disabled actions */}
      <div className="flex gap-2 flex-wrap">
        {[
          t("aiShiftSummary.action.publish"),
          t("aiShiftSummary.action.approve"),
          t("aiShiftSummary.action.export"),
        ].map((label) => (
          <button
            key={label}
            disabled
            className="flex items-center gap-1.5 text-sm px-4 py-2 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50"
            title={t("aiShiftSummary.action.disabled")}
          >
            <Lock className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>
      <p className="text-xs text-slate-400">{t("aiShiftSummary.hint.backend")}</p>
    </div>
  );
}

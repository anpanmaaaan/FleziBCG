// Natural Language Insight — SHELL
// AI-powered NL query visualization for internal product walkthrough.
// Real NL query requires backend LLM integration and operational data API.
// Demo queries must not be confused with live operational data.

import { Search, MessageSquare, Lock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const SUGGESTED_QUESTIONS = [
  "What was the OEE for Line A yesterday?",
  "Which stations had the most downtime this week?",
  "Show me quality defect trends for the last 7 days.",
  "What production orders are behind schedule?",
  "Which operators had the highest throughput last shift?",
];

export function NaturalLanguageInsight() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("naturalLanguageInsight.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("naturalLanguageInsight.notice.shell")} />

      {/* Prompt UI */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Search className="w-4 h-4 text-violet-400" />
          {t("naturalLanguageInsight.section.prompt")}
        </div>
        <div className="p-4">
          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 opacity-60 cursor-not-allowed">
            <Search className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <span className="text-sm text-slate-400 italic flex-1">{t("naturalLanguageInsight.prompt.placeholder")}</span>
            <button
              disabled
              className="text-xs px-3 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-white flex items-center gap-1"
              title={t("naturalLanguageInsight.action.query.disabled")}
            >
              <Lock className="w-3 h-3" />
              {t("naturalLanguageInsight.action.query")}
            </button>
          </div>
          <p className="text-xs text-slate-400 mt-2">{t("naturalLanguageInsight.prompt.hint")}</p>
        </div>
      </div>

      {/* Suggested questions */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <MessageSquare className="w-4 h-4 text-slate-400" />
          {t("naturalLanguageInsight.section.suggestions")}
        </div>
        <div className="divide-y divide-gray-50">
          {SUGGESTED_QUESTIONS.map((q) => (
            <div key={q} className="px-4 py-2.5 flex items-center gap-3">
              <Search className="w-3.5 h-3.5 text-slate-300 flex-shrink-0" />
              <span className="text-sm text-slate-600 italic">{q}</span>
              <button
                disabled
                className="ml-auto text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50"
                title={t("naturalLanguageInsight.action.query.disabled")}
              >
                {t("naturalLanguageInsight.action.ask")}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Demo answer preview */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <MessageSquare className="w-4 h-4 text-violet-400" />
          {t("naturalLanguageInsight.section.answer")}
          <span className="ml-2 text-xs font-normal bg-amber-100 text-amber-700 px-2 py-0.5 rounded">
            {t("naturalLanguageInsight.label.demo")}
          </span>
        </div>
        <div className="p-4">
          <p className="text-sm text-slate-500 italic">{t("naturalLanguageInsight.answer.placeholder")}</p>
          <div className="flex gap-2 mt-4">
            <button
              disabled
              className="text-xs px-3 py-1.5 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1"
              title={t("naturalLanguageInsight.action.execute.disabled")}
            >
              <Lock className="w-3 h-3" />
              {t("naturalLanguageInsight.action.execute")}
            </button>
            <button
              disabled
              className="text-xs px-3 py-1.5 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1"
              title={t("naturalLanguageInsight.action.export.disabled")}
            >
              <Lock className="w-3 h-3" />
              {t("naturalLanguageInsight.action.export")}
            </button>
          </div>
          <p className="text-xs text-slate-400 mt-2">{t("naturalLanguageInsight.hint.backend")}</p>
        </div>
      </div>
    </div>
  );
}

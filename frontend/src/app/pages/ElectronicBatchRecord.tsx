// Electronic Batch Record — SHELL
// Visualization of eBR package structure for internal product walkthrough.
// Real eBR requires backend quality, execution, and compliance record modules.
// Do NOT use as regulated eBR record. Not a compliant electronic batch record system.

import { BookOpen, FileCheck, Lock, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_EBR_SECTIONS = [
  { id: "EBR-BATCH", label: "Batch Master Data", status: "Pending", items: 0 },
  { id: "EBR-OPR", label: "Operation Execution Records", status: "Pending", items: 0 },
  { id: "EBR-QTY", label: "Quality Measurements & Dispositions", status: "Pending", items: 0 },
  { id: "EBR-MAT", label: "Material Usage & Lot Traceability", status: "Pending", items: 0 },
  { id: "EBR-DWN", label: "Downtime & Deviation Records", status: "Pending", items: 0 },
  { id: "EBR-REV", label: "Review & Approval Workflow", status: "Pending", items: 0 },
];

export function ElectronicBatchRecord() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("electronicBatchRecord.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("electronicBatchRecord.notice.shell")} />

      {/* Legal disclaimer — prominent */}
      <div className="rounded-lg border-2 border-red-300 bg-red-50 px-4 py-3 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm font-bold text-red-800">{t("electronicBatchRecord.notice.legal")}</p>
          <p className="text-xs text-red-700 mt-1">{t("electronicBatchRecord.notice.legalDetail")}</p>
        </div>
      </div>

      {/* eBR header metadata */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {[
          { label: t("electronicBatchRecord.meta.ebrId"), value: "EBR-DEMO-001" },
          { label: t("electronicBatchRecord.meta.batch"), value: "BATCH-DEMO-2026" },
          { label: t("electronicBatchRecord.meta.productionOrder"), value: "PO-DEMO-2026" },
          { label: t("electronicBatchRecord.meta.status"), value: t("electronicBatchRecord.meta.statusDraft") },
        ].map(({ label, value }) => (
          <div key={label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-500 mb-1">{label}</div>
            <div className="text-sm font-medium text-slate-700 italic">{value}</div>
          </div>
        ))}
      </div>

      {/* eBR sections */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <BookOpen className="w-4 h-4 text-indigo-400" />
          {t("electronicBatchRecord.section.package")}
          <span className="ml-2 text-xs font-normal text-slate-400 italic">({t("electronicBatchRecord.label.demo")})</span>
        </div>
        <div className="divide-y divide-gray-50">
          {MOCK_EBR_SECTIONS.map((sec) => (
            <div key={sec.id} className="px-4 py-3 flex items-center gap-3">
              {sec.status === "Complete" ? (
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-slate-300 flex-shrink-0" />
              )}
              <div className="flex-1">
                <div className="text-sm text-slate-800">{sec.label}</div>
                <div className="text-xs text-slate-400">{sec.items} {t("electronicBatchRecord.section.items")} — <span className="italic">{t("electronicBatchRecord.section.backendRequired")}</span></div>
              </div>
              <span className="text-xs text-amber-600 italic">{sec.status}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Review workflow placeholder */}
      <div className="bg-slate-50 rounded-lg border border-slate-200 p-4 flex items-start gap-3">
        <FileCheck className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-slate-500 italic">{t("electronicBatchRecord.review.placeholder")}</div>
      </div>

      {/* Disabled actions */}
      <div className="flex gap-2 flex-wrap">
        {[
          t("electronicBatchRecord.action.submit"),
          t("electronicBatchRecord.action.approve"),
          t("electronicBatchRecord.action.finalize"),
        ].map((label) => (
          <button
            key={label}
            disabled
            className="flex items-center gap-1.5 text-sm px-4 py-2 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50"
            title={t("electronicBatchRecord.action.disabled")}
          >
            <Lock className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>
      <p className="text-xs text-slate-400">{t("electronicBatchRecord.hint.backend")}</p>
    </div>
  );
}

// Compliance Record Package — SHELL
// Internal visualization of compliance record package structure.
// Official compliance records require backend quality, execution, and audit modules.
// Do NOT use as legally binding record. Do not export or present as official compliance record.

import { FolderOpen, CheckCircle, XCircle, Lock, AlertTriangle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SECTIONS = [
  { id: "SEC-OPR", label: "Operation Records", items: 0, complete: false },
  { id: "SEC-QTY", label: "Quality Evidence", items: 0, complete: false },
  { id: "SEC-MAT", label: "Material Traceability", items: 0, complete: false },
  { id: "SEC-AUD", label: "Audit Trail", items: 0, complete: false },
];

export function ComplianceRecordPackage() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("complianceRecordPackage.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("complianceRecordPackage.notice.shell")} />

      {/* Legal disclaimer */}
      <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-red-800 font-medium">{t("complianceRecordPackage.notice.legal")}</p>
      </div>

      {/* Package metadata */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="text-xs text-slate-500 mb-1">{t("complianceRecordPackage.meta.packageId")}</div>
          <div className="text-sm font-medium text-slate-700">PKG-DEMO-001</div>
          <div className="text-xs text-slate-400 italic">{t("complianceRecordPackage.meta.demo")}</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="text-xs text-slate-500 mb-1">{t("complianceRecordPackage.meta.productionOrder")}</div>
          <div className="text-sm font-medium text-slate-700">PO-DEMO-2026</div>
          <div className="text-xs text-slate-400 italic">{t("complianceRecordPackage.meta.demo")}</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="text-xs text-slate-500 mb-1">{t("complianceRecordPackage.meta.status")}</div>
          <div className="text-sm font-medium text-amber-600">{t("complianceRecordPackage.meta.statusDraft")}</div>
        </div>
      </div>

      {/* Record sections */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <FolderOpen className="w-4 h-4 text-indigo-400" />
          {t("complianceRecordPackage.section.records")}
        </div>
        <div className="divide-y divide-gray-50">
          {MOCK_SECTIONS.map((sec) => (
            <div key={sec.id} className="px-4 py-3 flex items-center gap-3">
              {sec.complete ? (
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-slate-300 flex-shrink-0" />
              )}
              <div className="flex-1">
                <div className="text-sm text-slate-800">{sec.label}</div>
                <div className="text-xs text-slate-400">{sec.items} {t("complianceRecordPackage.section.items")} — <span className="italic">{t("complianceRecordPackage.section.backendRequired")}</span></div>
              </div>
              <span className="text-xs text-amber-600 italic">{t("complianceRecordPackage.section.missingEvidence")}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Disabled actions */}
      <div className="flex gap-2 flex-wrap">
        {[
          t("complianceRecordPackage.action.generate"),
          t("complianceRecordPackage.action.finalize"),
          t("complianceRecordPackage.action.export"),
        ].map((label) => (
          <button
            key={label}
            disabled
            className="flex items-center gap-1.5 text-sm px-4 py-2 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50"
            title={t("complianceRecordPackage.action.disabled")}
          >
            <Lock className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>
      <p className="text-xs text-slate-400">{t("complianceRecordPackage.hint.backend")}</p>
    </div>
  );
}

// E-Signature — SHELL
// Visualization of e-signature request workflow for internal product walkthrough.
// Real e-signature requires backend signature workflow and compliance service.
// Do NOT use as legally binding signature. This screen is NOT an active e-signature system.

import { PenTool, User, Lock, AlertTriangle, Clock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SIGNATURE_REQUESTS = [
  {
    id: "SIG-001",
    document: "Compliance Record Package PKG-DEMO-001",
    requiredRole: "Quality Manager",
    signerName: "—",
    status: "Pending",
    dueDate: "Demo",
  },
  {
    id: "SIG-002",
    document: "Electronic Batch Record EBR-DEMO-001",
    requiredRole: "Production Manager",
    signerName: "—",
    status: "Pending",
    dueDate: "Demo",
  },
  {
    id: "SIG-003",
    document: "Deviation Report DEV-DEMO-001",
    requiredRole: "QA Lead",
    signerName: "—",
    status: "Pending",
    dueDate: "Demo",
  },
];

export function ESignature() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("eSignature.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("eSignature.notice.shell")} />

      {/* Legal disclaimer — prominent */}
      <div className="rounded-lg border-2 border-red-300 bg-red-50 px-4 py-3 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm font-bold text-red-800">{t("eSignature.notice.legal")}</p>
          <p className="text-xs text-red-700 mt-1">{t("eSignature.notice.legalDetail")}</p>
        </div>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {[
          { label: t("eSignature.metric.pending"), value: "—" },
          { label: t("eSignature.metric.completed"), value: "—" },
          { label: t("eSignature.metric.overdue"), value: "—" },
        ].map(({ label, value }) => (
          <div key={label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-600 mb-1">{label}</div>
            <div className="text-2xl font-bold text-slate-700">{value}</div>
          </div>
        ))}
      </div>

      {/* Signature request list */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <PenTool className="w-4 h-4 text-indigo-400" />
          {t("eSignature.section.requests")}
          <span className="ml-2 text-xs font-normal text-slate-400 italic">({t("eSignature.label.demo")})</span>
        </div>
        <div className="divide-y divide-gray-50">
          {MOCK_SIGNATURE_REQUESTS.map((req) => (
            <div key={req.id} className="px-4 py-3 flex items-start gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-mono text-slate-400">{req.id}</span>
                  <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded">{req.status}</span>
                </div>
                <div className="text-sm text-slate-800 truncate">{req.document}</div>
                <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-500">
                  <User className="w-3 h-3" />{req.requiredRole}
                  <Clock className="w-3 h-3 ml-2" />{req.dueDate}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">{t("eSignature.signer.label")}: <span className="italic">{req.signerName}</span></div>
              </div>
              <div className="flex gap-1 flex-shrink-0">
                <button disabled className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1" title={t("eSignature.action.sign.disabled")}>
                  <Lock className="w-3 h-3" />{t("eSignature.action.sign")}
                </button>
                <button disabled className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1" title={t("eSignature.action.approve.disabled")}>
                  <Lock className="w-3 h-3" />{t("eSignature.action.approve")}
                </button>
                <button disabled className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1" title={t("eSignature.action.reject.disabled")}>
                  <Lock className="w-3 h-3" />{t("eSignature.action.reject")}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      <p className="text-xs text-slate-400">{t("eSignature.hint.backend")}</p>
    </div>
  );
}

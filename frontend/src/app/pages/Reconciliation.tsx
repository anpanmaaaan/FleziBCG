// Reconciliation — SHELL
// To-be visualization of MOM vs ERP/WMS reconciliation status.
// Real reconciliation, discrepancy resolution, and approval
// are managed by the backend integration and ERP reconciliation modules.
// DO NOT use as source of reconciliation truth.

import { Scale, CheckCircle2, XCircle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_DISCREPANCIES = [
  { id: "REC-007", domain: "Goods Receipt", momValue: "100 PC", erpValue: "98 PC", delta: "-2 PC", status: "Open" },
  { id: "REC-006", domain: "Production Confirmation", momValue: "WO-1038 Closed", erpValue: "WO-1038 Confirmed", delta: "None", status: "Matched" },
  { id: "REC-005", domain: "Quality Result", momValue: "3 FAIL", erpValue: "2 FAIL", delta: "+1 FAIL", status: "Open" },
  { id: "REC-004", domain: "WIP Inventory", momValue: "50 PC at Station-03", erpValue: "Not in ERP", delta: "Location Missing", status: "Open" },
];

const STATUS_COLORS: Record<string, string> = {
  Open: "bg-red-50 text-red-700 border-red-100",
  Matched: "bg-green-50 text-green-700 border-green-100",
};

export function Reconciliation() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("reconciliation.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("reconciliation.notice.shell")} />

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="bg-red-50 rounded-lg border border-red-200 p-3">
          <div className="flex items-center gap-1 text-xs text-red-600 mb-1">
            <XCircle className="w-3 h-3" />
            {t("reconciliation.metric.open")}
          </div>
          <div className="text-2xl font-bold text-red-800">3</div>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-3">
          <div className="flex items-center gap-1 text-xs text-green-600 mb-1">
            <CheckCircle2 className="w-3 h-3" />
            {t("reconciliation.metric.matched")}
          </div>
          <div className="text-2xl font-bold text-green-800">1</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
            <Scale className="w-3 h-3" />
            {t("reconciliation.metric.total")}
          </div>
          <div className="text-2xl font-bold text-slate-700">4</div>
        </div>
      </div>

      {/* Discrepancy table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Scale className="w-4 h-4 text-slate-400" />
          {t("reconciliation.section.discrepancies")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("reconciliation.col.id")}</th>
                <th className="px-4 py-2 text-left">{t("reconciliation.col.domain")}</th>
                <th className="px-4 py-2 text-left">{t("reconciliation.col.momValue")}</th>
                <th className="px-4 py-2 text-left">{t("reconciliation.col.erpValue")}</th>
                <th className="px-4 py-2 text-left">{t("reconciliation.col.delta")}</th>
                <th className="px-4 py-2 text-left">{t("reconciliation.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("reconciliation.col.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_DISCREPANCIES.map((rec) => (
                <tr key={rec.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-600">{rec.id}</td>
                  <td className="px-4 py-2 text-gray-800">{rec.domain}</td>
                  <td className="px-4 py-2 text-xs text-gray-600">{rec.momValue}</td>
                  <td className="px-4 py-2 text-xs text-gray-600">{rec.erpValue}</td>
                  <td className="px-4 py-2 text-xs font-mono text-gray-600">{rec.delta}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${STATUS_COLORS[rec.status] ?? "bg-slate-50 text-slate-500 border-slate-100"}`}>{rec.status}</span>
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex gap-1">
                      <button type="button" disabled title={t("reconciliation.hint.disabled")} className="text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">{t("reconciliation.action.resolve")}</button>
                      <button type="button" disabled title={t("reconciliation.hint.disabled")} className="text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">{t("reconciliation.action.approve")}</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("reconciliation.hint.backend")}</p>
      </div>
    </div>
  );
}

// ERP Mapping — SHELL
// To-be visualization of ERP field mapping configuration.
// Real ERP mapping, validation, and publishing are managed
// by the backend integration and ERP adapter modules.

import { Link2, CheckCircle2 } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_MAPPINGS = [
  { domain: "Product", momField: "product_code", erpField: "MATNR", erpObject: "Material Master", status: "Draft" },
  { domain: "Product", momField: "description", erpField: "MAKTX", erpObject: "Material Master", status: "Draft" },
  { domain: "Work Center", momField: "work_center_id", erpField: "ARBPL", erpObject: "Work Center", status: "Draft" },
  { domain: "Production Order", momField: "production_order_id", erpField: "AUFNR", erpObject: "Production Order", status: "Draft" },
  { domain: "Downtime Reason", momField: "reason_code", erpField: "NOTIFTYPE", erpObject: "PM Notification", status: "Draft" },
  { domain: "Quality Result", momField: "inspection_lot", erpField: "PRUEFLOS", erpObject: "Inspection Lot", status: "Draft" },
];

export function ErpMapping() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("erpMapping.title")}</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            disabled
            title={t("erpMapping.hint.disabled")}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
          >
            <CheckCircle2 className="w-4 h-4" />
            {t("erpMapping.action.validate")}
          </button>
          <button
            type="button"
            disabled
            title={t("erpMapping.hint.disabled")}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
          >
            <Link2 className="w-4 h-4" />
            {t("erpMapping.action.publish")}
          </button>
        </div>
      </div>

      <BackendRequiredNotice message={t("erpMapping.notice.shell")} />

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Link2 className="w-4 h-4 text-slate-400" />
          {t("erpMapping.section.mappings")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("erpMapping.col.domain")}</th>
                <th className="px-4 py-2 text-left">{t("erpMapping.col.momField")}</th>
                <th className="px-4 py-2 text-left">{t("erpMapping.col.erpObject")}</th>
                <th className="px-4 py-2 text-left">{t("erpMapping.col.erpField")}</th>
                <th className="px-4 py-2 text-left">{t("erpMapping.col.status")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_MAPPINGS.map((m, i) => (
                <tr key={i} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2">
                    <span className="text-xs px-2 py-0.5 bg-purple-50 text-purple-700 rounded-full border border-purple-100">{m.domain}</span>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs text-gray-700">{m.momField}</td>
                  <td className="px-4 py-2 text-gray-600">{m.erpObject}</td>
                  <td className="px-4 py-2 font-mono text-xs text-gray-700">{m.erpField}</td>
                  <td className="px-4 py-2">
                    <span className="text-xs text-slate-400 italic">{m.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("erpMapping.hint.backend")}</p>
      </div>
    </div>
  );
}

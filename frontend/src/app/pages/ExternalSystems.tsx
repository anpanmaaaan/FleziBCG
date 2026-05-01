// External Systems Registry — SHELL
// To-be visualization of external system registry.
// Real system registration, configuration, and connection management
// are managed by the backend integration module.

import { Database, PlusCircle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_SYSTEMS = [
  { id: "ERP-001", name: "SAP ERP S/4HANA", type: "ERP", owner: "IT", direction: "Both", env: "Production", status: "Unknown" },
  { id: "WMS-001", name: "Warehouse Management System", type: "WMS", owner: "Logistics", direction: "Inbound", env: "Production", status: "Unknown" },
  { id: "QMS-001", name: "Quality Management System", type: "QMS", owner: "Quality", direction: "Both", env: "Production", status: "Unknown" },
  { id: "CMMS-001", name: "CMMS / Maintenance", type: "CMMS", owner: "Maintenance", direction: "Outbound", env: "Production", status: "Unknown" },
  { id: "SCADA-001", name: "SCADA / DCS", type: "SCADA", owner: "Engineering", direction: "Inbound", env: "Shop Floor", status: "Unknown" },
  { id: "HIST-001", name: "Process Historian", type: "Historian", owner: "Engineering", direction: "Inbound", env: "Shop Floor", status: "Unknown" },
];

export function ExternalSystems() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("externalSystems.title")}</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <button
          type="button"
          disabled
          title={t("externalSystems.hint.disabled")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-sm text-slate-400 cursor-not-allowed"
        >
          <PlusCircle className="w-4 h-4" />
          {t("externalSystems.action.add")}
        </button>
      </div>

      <BackendRequiredNotice message={t("externalSystems.notice.shell")} />

      {/* Systems table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <Database className="w-4 h-4 text-slate-400" />
          {t("externalSystems.section.registry")}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("externalSystems.col.id")}</th>
                <th className="px-4 py-2 text-left">{t("externalSystems.col.name")}</th>
                <th className="px-4 py-2 text-left">{t("externalSystems.col.type")}</th>
                <th className="px-4 py-2 text-left">{t("externalSystems.col.owner")}</th>
                <th className="px-4 py-2 text-left">{t("externalSystems.col.direction")}</th>
                <th className="px-4 py-2 text-left">{t("externalSystems.col.env")}</th>
                <th className="px-4 py-2 text-left">{t("externalSystems.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("externalSystems.col.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_SYSTEMS.map((sys) => (
                <tr key={sys.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 text-xs text-gray-500 font-mono">{sys.id}</td>
                  <td className="px-4 py-2 font-medium text-gray-800">{sys.name}</td>
                  <td className="px-4 py-2">
                    <span className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full border border-blue-100">{sys.type}</span>
                  </td>
                  <td className="px-4 py-2 text-gray-600">{sys.owner}</td>
                  <td className="px-4 py-2 text-gray-600">{sys.direction}</td>
                  <td className="px-4 py-2 text-gray-600">{sys.env}</td>
                  <td className="px-4 py-2">
                    <span className="text-xs text-slate-400 italic">{t("externalSystems.status.unknown")}</span>
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex gap-1">
                      <button type="button" disabled title={t("externalSystems.hint.disabled")} className="text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">{t("externalSystems.action.edit")}</button>
                      <button type="button" disabled title={t("externalSystems.hint.disabled")} className="text-xs text-slate-400 cursor-not-allowed px-2 py-0.5 border border-slate-200 rounded">{t("externalSystems.action.delete")}</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-400 italic px-4 py-3">{t("externalSystems.hint.backend")}</p>
      </div>
    </div>
  );
}

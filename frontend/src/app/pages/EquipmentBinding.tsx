// Equipment Binding — SHELL
// To-be visualization of station-to-equipment binding state.
// Equipment binding and readiness are managed by the backend execution and maintenance systems.

import { Lock, Cpu, MonitorCheck, Activity } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

export function EquipmentBinding() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4 max-w-3xl mx-auto">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("equipmentBinding.title")}
          </h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        <button
          disabled
          className="flex items-center gap-1 px-3 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
          title="Backend execution workflow required"
        >
          {t("equipmentBinding.action.checkStatus")}
          <Lock className="w-3 h-3 ml-1" />
        </button>
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("equipmentBinding.notice.shell")} />

      {/* Station ↔ Equipment layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Station Panel */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
            <MonitorCheck className="w-4 h-4 text-blue-500" />
            {t("equipmentBinding.section.station")}
          </div>
          <div className="flex flex-col gap-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Station ID</span>
              <span className="text-gray-400 italic">—</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Station Name</span>
              <span className="text-gray-400 italic">—</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Line</span>
              <span className="text-gray-400 italic">—</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Capability</span>
              <span className="text-gray-400 italic">—</span>
            </div>
          </div>
        </div>

        {/* Equipment Panel */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
            <Cpu className="w-4 h-4 text-purple-500" />
            {t("equipmentBinding.section.equipment")}
          </div>
          <p className="text-sm text-gray-400 italic mb-3">{t("equipmentBinding.unbound")}</p>
          <div className="flex flex-col gap-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Equipment ID</span>
              <span className="text-gray-400 italic">—</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Equipment Name</span>
              <span className="text-gray-400 italic">—</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Type</span>
              <span className="text-gray-400 italic">—</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Serial No.</span>
              <span className="text-gray-400 italic">—</span>
            </div>
          </div>
        </div>
      </div>

      {/* Readiness Status */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          <Activity className="w-4 h-4 text-gray-500" />
          {t("equipmentBinding.section.status")}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-500">
            {t("equipmentBinding.status.unbound")}
          </span>
          <span className="text-xs text-gray-500">Equipment readiness is determined by backend maintenance and execution systems.</span>
        </div>
      </div>

      {/* Bind / Unbind actions */}
      <div className="flex gap-3">
        <button
          disabled
          className="flex-1 flex items-center justify-center gap-1 px-4 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
          title="Backend execution workflow required"
        >
          {t("equipmentBinding.action.bind")}
          <Lock className="w-3 h-3 ml-1" />
        </button>
        <button
          disabled
          className="flex-1 flex items-center justify-center gap-1 px-4 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
          title="Backend execution workflow required"
        >
          {t("equipmentBinding.action.unbind")}
          <Lock className="w-3 h-3 ml-1" />
        </button>
      </div>

      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ⚠ Equipment binding, unbinding, and readiness verification are backend execution truths. Frontend cannot bind or unbind equipment.
      </p>
    </div>
  );
}

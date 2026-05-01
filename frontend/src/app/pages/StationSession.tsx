// Station Session — SHELL
// To-be visualization of station session state, operator assignment, and equipment binding.
// Session truth is managed by the backend execution system.

import { Lock, MonitorCheck, User, Cpu, Power } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

export function StationSession() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4 max-w-3xl mx-auto">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("stationSession.title")}
          </h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>
        {/* Disabled session actions */}
        <div className="flex items-center gap-2">
          <button
            disabled
            className="flex items-center gap-1 px-3 py-2 rounded-md bg-green-50 border border-green-200 text-green-400 text-sm cursor-not-allowed"
            title="Backend execution workflow required"
          >
            <Power className="w-4 h-4" />
            {t("stationSession.action.openSession")}
            <Lock className="w-3 h-3 ml-1" />
          </button>
          <button
            disabled
            className="flex items-center gap-1 px-3 py-2 rounded-md bg-red-50 border border-red-200 text-red-400 text-sm cursor-not-allowed"
            title="Backend execution workflow required"
          >
            <Power className="w-4 h-4" />
            {t("stationSession.action.closeSession")}
            <Lock className="w-3 h-3 ml-1" />
          </button>
        </div>
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("stationSession.notice.shell")} />

      {/* Three-panel layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Station Identity */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2">
            <MonitorCheck className="w-4 h-4 text-blue-500" />
            {t("stationSession.section.station")}
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
              <span className="text-gray-500">Type</span>
              <span className="text-gray-400 italic">—</span>
            </div>
          </div>
        </div>

        {/* Operator */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2">
            <User className="w-4 h-4 text-green-500" />
            {t("stationSession.section.operator")}
          </div>
          <div className="flex flex-col gap-2">
            <p className="text-sm text-gray-400 italic">
              {t("stationSession.operator.unassigned")}
            </p>
          </div>
          <button
            disabled
            className="mt-auto flex items-center justify-center gap-1 w-full px-3 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
            title="Backend execution workflow required"
          >
            {t("stationSession.action.assignOperator")}
            <Lock className="w-3 h-3 ml-1" />
          </button>
        </div>

        {/* Equipment */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2">
            <Cpu className="w-4 h-4 text-purple-500" />
            {t("stationSession.section.equipment")}
          </div>
          <div className="flex flex-col gap-2">
            <p className="text-sm text-gray-400 italic">
              {t("stationSession.equipment.unbound")}
            </p>
          </div>
          <button
            disabled
            className="mt-auto flex items-center justify-center gap-1 w-full px-3 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
            title="Backend execution workflow required"
          >
            {t("stationSession.action.bindEquipment")}
            <Lock className="w-3 h-3 ml-1" />
          </button>
        </div>
      </div>

      {/* Session State Panel */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          <Power className="w-4 h-4 text-gray-500" />
          {t("stationSession.section.session")}
        </div>
        <p className="text-sm text-gray-400 italic">{t("stationSession.session.noActive")}</p>
        <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded text-xs text-amber-700">
          Session state ownership, claim validity, and operator authorization are backend execution truths. Frontend cannot create or close sessions.
        </div>
      </div>
    </div>
  );
}

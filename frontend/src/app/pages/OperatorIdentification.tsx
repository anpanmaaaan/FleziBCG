// Operator Identification — SHELL
// To-be visualization of operator identity verification panel.
// Operator authorization is verified by the backend authentication and authorization system.

import { Lock, User, BadgeCheck, ShieldAlert } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

export function OperatorIdentification() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4 max-w-2xl mx-auto">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("operatorId.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("operatorId.notice.shell")} />

      {/* Operator Identity Panel */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-4">
          <User className="w-4 h-4 text-blue-500" />
          {t("operatorId.section.identity")}
        </div>
        <div className="flex flex-col items-center gap-4 py-4">
          <div className="w-20 h-20 rounded-full bg-gray-100 border-2 border-gray-200 flex items-center justify-center">
            <User className="w-10 h-10 text-gray-300" />
          </div>
          <p className="text-sm text-gray-400 italic">{t("operatorId.unidentified")}</p>
          <div className="grid grid-cols-2 gap-3 w-full mt-2">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-gray-500">Operator ID</span>
              <span className="text-sm text-gray-400 italic">—</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-xs text-gray-500">Name</span>
              <span className="text-sm text-gray-400 italic">—</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-xs text-gray-500">Role</span>
              <span className="text-sm text-gray-400 italic">—</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-xs text-gray-500">Station</span>
              <span className="text-sm text-gray-400 italic">—</span>
            </div>
          </div>
        </div>
      </div>

      {/* Badge / Scan Panel */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-4">
          <BadgeCheck className="w-4 h-4 text-purple-500" />
          {t("operatorId.section.scan")}
        </div>
        <div className="flex flex-col items-center gap-3 py-3">
          <div className="w-full h-16 border-2 border-dashed border-gray-200 rounded-lg flex items-center justify-center text-sm text-gray-400">
            Badge scan input — backend authentication required
          </div>
          <button
            disabled
            className="flex items-center gap-1 px-4 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed w-full justify-center"
            title="Backend authentication required"
          >
            <BadgeCheck className="w-4 h-4" />
            {t("operatorId.action.scanBadge")}
            <Lock className="w-3 h-3 ml-1" />
          </button>
        </div>
      </div>

      {/* Authorization Status */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-4">
          <ShieldAlert className="w-4 h-4 text-amber-500" />
          {t("operatorId.section.authorization")}
        </div>
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Status</span>
            <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-500">
              {t("operatorId.status.pending")}
            </span>
          </div>
          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2 mt-2">
            Authorization status is determined by the backend. Frontend cannot verify operator identity or authorization.
          </p>
        </div>
      </div>

      {/* Action buttons — all disabled */}
      <div className="flex gap-3">
        <button
          disabled
          className="flex-1 flex items-center justify-center gap-1 px-4 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
          title="Backend execution workflow required"
        >
          {t("operatorId.action.confirm")}
          <Lock className="w-3 h-3 ml-1" />
        </button>
        <button
          disabled
          className="flex-1 flex items-center justify-center gap-1 px-4 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
          title="Backend execution workflow required"
        >
          {t("operatorId.action.switch")}
          <Lock className="w-3 h-3 ml-1" />
        </button>
      </div>
    </div>
  );
}

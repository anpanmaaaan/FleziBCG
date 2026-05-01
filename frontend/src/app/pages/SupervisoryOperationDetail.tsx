// Supervisory Operation Detail — SHELL
// To-be visualization for supervisory review of operation state, blockers, and exception management.
// Supervisory authority, override actions, and execution truth are managed by the backend.

import { Link, useParams } from "react-router";
import {
  ArrowLeft,
  Lock,
  AlertTriangle,
  Package,
  ShieldAlert,
  History,
} from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

export function SupervisoryOperationDetail() {
  const { operationId } = useParams<{ operationId: string }>();
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4 max-w-4xl mx-auto">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <Link
            to="/operations"
            className="flex items-center gap-1 text-sm text-blue-600 hover:underline"
          >
            <ArrowLeft className="w-4 h-4" />
            {t("supervisoryOpDetail.back")}
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-gray-900">
              {t("supervisoryOpDetail.title")}
            </h1>
            <ScreenStatusBadge phase="SHELL" />
          </div>
          {operationId && (
            <p className="text-sm text-gray-500">Operation: {operationId}</p>
          )}
        </div>

        {/* Disabled supervisory action buttons */}
        <div className="flex flex-wrap items-center gap-2 mt-1">
          <button
            disabled
            className="flex items-center gap-1 px-3 py-1.5 rounded border border-gray-200 bg-gray-50 text-gray-400 text-xs cursor-not-allowed"
            title="Backend supervisory workflow required"
          >
            {t("supervisoryOpDetail.action.releaseBlock")}
            <Lock className="w-3 h-3" />
          </button>
          <button
            disabled
            className="flex items-center gap-1 px-3 py-1.5 rounded border border-gray-200 bg-gray-50 text-gray-400 text-xs cursor-not-allowed"
            title="Backend supervisory workflow required"
          >
            {t("supervisoryOpDetail.action.overrideStatus")}
            <Lock className="w-3 h-3" />
          </button>
          <button
            disabled
            className="flex items-center gap-1 px-3 py-1.5 rounded border border-gray-200 bg-gray-50 text-gray-400 text-xs cursor-not-allowed"
            title="Backend supervisory workflow required"
          >
            {t("supervisoryOpDetail.action.approveException")}
            <Lock className="w-3 h-3" />
          </button>
          <button
            disabled
            className="flex items-center gap-1 px-3 py-1.5 rounded border border-gray-200 bg-gray-50 text-gray-400 text-xs cursor-not-allowed"
            title="Backend supervisory workflow required"
          >
            {t("supervisoryOpDetail.action.reassignOperator")}
            <Lock className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("supervisoryOpDetail.notice.shell")} />

      {/* Operation Overview */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          {t("supervisoryOpDetail.section.overview")}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-xs text-gray-500">Operation Code</span>
            <div className="text-gray-400 italic">—</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Operation Name</span>
            <div className="text-gray-400 italic">—</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Work Order</span>
            <div className="text-gray-400 italic">—</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Status</span>
            <div className="text-gray-400 italic">— (backend)</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Station</span>
            <div className="text-gray-400 italic">—</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Operator</span>
            <div className="text-gray-400 italic">—</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Planned Qty</span>
            <div className="text-gray-400 italic">—</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Completed Qty</span>
            <div className="text-gray-400 italic">—</div>
          </div>
        </div>
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
          Operation status and quantity truth are backend execution read models. This panel shows backend-required placeholders.
        </div>
      </div>

      {/* Blocked Reason Panel */}
      <div className="bg-white rounded-lg border border-red-100 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          <AlertTriangle className="w-4 h-4 text-red-500" />
          {t("supervisoryOpDetail.section.blockedReason")}
        </div>
        <p className="text-sm text-gray-400 italic">{t("supervisoryOpDetail.noBlock")}</p>
        <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded text-xs text-amber-700">
          Blocker acknowledgement and release require backend supervisory command authorization. Frontend cannot release blocks.
        </div>
        <div className="mt-2 flex gap-2">
          <button
            disabled
            className="flex items-center gap-1 px-3 py-1.5 rounded border border-gray-200 bg-gray-50 text-gray-400 text-xs cursor-not-allowed"
            title="Backend supervisory workflow required"
          >
            {t("supervisoryOpDetail.action.acknowledgeBlocker")}
            <Lock className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Quality Context */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          <ShieldAlert className="w-4 h-4 text-indigo-500" />
          {t("supervisoryOpDetail.section.quality")}
        </div>
        <p className="text-sm text-gray-400 italic">Quality context — backend quality system required.</p>
      </div>

      {/* Material Context */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          <Package className="w-4 h-4 text-purple-500" />
          {t("supervisoryOpDetail.section.material")}
        </div>
        <p className="text-sm text-gray-400 italic">Material context — backend material/inventory system required.</p>
      </div>

      {/* Supervisory Actions History */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
          <History className="w-4 h-4 text-gray-500" />
          {t("supervisoryOpDetail.section.history")}
        </div>
        <p className="text-sm text-gray-400 italic">{t("supervisoryOpDetail.noHistory")}</p>
        <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
          Supervisory action history is an immutable audit record managed by the backend. Frontend cannot create or modify this record.
        </div>
      </div>
    </div>
  );
}

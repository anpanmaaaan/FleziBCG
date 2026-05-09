// Operation Execution Timeline — PARTIAL (backend-connected)
// Connects to GET /v1/work-orders/{wo_id}/execution-timeline.
// Loads operation detail first to resolve work_order_id from operationId param.

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { ArrowLeft, Activity, Clock, CheckCircle, AlertTriangle, History } from "lucide-react";
import { toast } from "sonner";
import { ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { operationApi } from "@/app/api/operationApi";
import { iamApi } from "@/app/api/iamApi";
import type { WorkOrderExecutionTimeline, ExecutionTimelineOperation } from "@/app/api/iamApi";

function timingBadge(status: string) {
  switch (status) {
    case "EARLY": return "bg-green-100 text-green-700";
    case "LATE": return "bg-red-100 text-red-700";
    default: return "bg-gray-100 text-gray-600";
  }
}

function statusBadge(status: string) {
  switch (status) {
    case "IN_PROGRESS": return "bg-blue-100 text-blue-700";
    case "COMPLETED": return "bg-green-100 text-green-700";
    case "CLOSED": return "bg-gray-100 text-gray-500";
    case "PENDING": return "bg-yellow-100 text-yellow-700";
    default: return "bg-gray-100 text-gray-600";
  }
}

export function OperationTimeline() {
  const { operationId } = useParams<{ operationId: string }>();
  const { t } = useI18n();
  const [timeline, setTimeline] = useState<WorkOrderExecutionTimeline | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!operationId) { setLoading(false); return; }
    setLoading(true);
    // Step 1: get operation detail to resolve work_order_id
    operationApi
      .get(Number(operationId))
      .then((op) => {
        // Step 2: fetch execution timeline for the work order
        return iamApi.getWorkOrderExecutionTimeline(op.work_order_id);
      })
      .then((tl) => setTimeline(tl))
      .catch((err) => {
        const msg = err?.message ?? "Failed to load execution timeline.";
        setError(msg);
        toast.error(msg);
      })
      .finally(() => setLoading(false));
  }, [operationId]);

  const focusedOp = timeline?.operations.find((o) => o.operation_id === Number(operationId));
  const otherOps = timeline?.operations.filter((o) => o.operation_id !== Number(operationId)) ?? [];

  return (
    <div className="flex flex-col gap-4 p-4 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <Link
            to={`/operations/${operationId}/detail`}
            className="flex items-center gap-1 text-sm text-blue-600 hover:underline"
          >
            <ArrowLeft className="w-4 h-4" />
            {t("operationTimeline.back")}
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-gray-900">
              {t("operationTimeline.title")}
            </h1>
            <ScreenStatusBadge phase="PARTIAL" />
          </div>
          {timeline && (
            <p className="text-sm text-gray-500">
              WO: <span className="font-medium">{timeline.work_order_number}</span>
              {" · "}PO: <span className="font-medium">{timeline.production_order_number}</span>
            </p>
          )}
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-400 text-sm">{t("operationTimeline.label.loading_execution_timeline")}</div>
      ) : error ? (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
      ) : !timeline ? (
        <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-500 text-center">
          No timeline data available.
        </div>
      ) : (
        <>
          {/* Focused operation highlight */}
          {focusedOp && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-blue-800 mb-2">
                <Activity className="w-4 h-4" />
                This Operation: {focusedOp.operation_number} — {focusedOp.name}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div>
                  <span className="text-blue-600">{t("common.status")}</span>
                  <div>
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(focusedOp.status)}`}>
                      {focusedOp.status}
                    </span>
                  </div>
                </div>
                <div>
                  <span className="text-blue-600">{t("operationTimeline.label.timing")}</span>
                  <div>
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${timingBadge(focusedOp.timing_status)}`}>
                      {focusedOp.timing_status}
                    </span>
                  </div>
                </div>
                {focusedOp.actual_start && (
                  <div>
                    <span className="text-blue-600">{t("operationTimeline.label.started")}</span>
                    <div className="text-gray-700">{new Date(focusedOp.actual_start).toLocaleString()}</div>
                  </div>
                )}
                {focusedOp.delay_minutes != null && (
                  <div>
                    <span className="text-blue-600">{t("operationTimeline.label.delay")}</span>
                    <div className="text-gray-700">{focusedOp.delay_minutes} min</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* All operations in WO */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
              <History className="w-4 h-4 text-gray-500" />
              Work Order Operations Timeline ({timeline.operations.length})
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                  <th className="px-4 py-2 text-left">{t("operationTimeline.label.seq")}</th>
                  <th className="px-4 py-2 text-left">{t("operationTimeline.label.operation")}</th>
                  <th className="px-4 py-2 text-left">{t("operationTimeline.label.workstation")}</th>
                  <th className="px-4 py-2 text-left">{t("common.status")}</th>
                  <th className="px-4 py-2 text-left">{t("operationTimeline.label.planned_start")}</th>
                  <th className="px-4 py-2 text-left">{t("operationTimeline.label.actual_start")}</th>
                  <th className="px-4 py-2 text-left">{t("operationTimeline.label.timing")}</th>
                  <th className="px-4 py-2 text-left">{t("operationTimeline.label.qc")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {timeline.operations.map((op) => (
                  <tr
                    key={op.operation_id}
                    className={`hover:bg-gray-50 ${op.operation_id === Number(operationId) ? "bg-blue-50/50" : ""}`}
                  >
                    <td className="px-4 py-3 text-xs text-gray-500">{op.sequence}</td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-800">{op.operation_number}</div>
                      <div className="text-xs text-gray-500">{op.name}</div>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">{op.workstation}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(op.status)}`}>
                        {op.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {op.planned_start ? new Date(op.planned_start).toLocaleString() : "—"}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">
                      {op.actual_start ? new Date(op.actual_start).toLocaleString() : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${timingBadge(op.timing_status)}`}>
                        {op.timing_status}
                        {op.delay_minutes != null && op.delay_minutes > 0 ? ` (+${op.delay_minutes}m)` : ""}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs">
                      {op.qc_required ? (
                        <span className="text-indigo-600 font-medium">{t("common.required")}</span>
                      ) : (
                        <span className="text-gray-400">{t("common.na")}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}



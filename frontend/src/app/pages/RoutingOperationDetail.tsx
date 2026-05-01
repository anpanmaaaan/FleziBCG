import { useState } from "react";
import { Link, useParams } from "react-router";
import { ArrowLeft, Lock, GitBranch } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice, RoutingLifecycleBadge, RoutingOperationSequenceBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface OperationDetail {
  operation_id: string;
  routing_id: string;
  routing_code: string;
  routing_name: string;
  operation_code: string;
  operation_name: string;
  sequence_no: number;
  lifecycle_status: string;
  work_center: string;
  standard_cycle_time: number;
  setup_time: number;
  run_time_per_unit: number;
  required_resource_type: string;
  required_skill: string | null;
  required_skill_level: string | null;
  qc_checkpoint_count: number;
  description: string;
}

const mockOperations: Record<string, OperationDetail> = {
  "OP-001": {
    operation_id: "OP-001",
    routing_id: "RT-001",
    routing_code: "RT-SHAFT-001",
    routing_name: "Shaft Machining Route",
    operation_code: "OP-TURN-01",
    operation_name: "CNC Turning",
    sequence_no: 10,
    lifecycle_status: "RELEASED",
    work_center: "WC-LATHE-01",
    standard_cycle_time: 45,
    setup_time: 15,
    run_time_per_unit: 30,
    required_resource_type: "CNC_LATHE",
    required_skill: "CNC_OPERATOR",
    required_skill_level: "LEVEL_2",
    qc_checkpoint_count: 2,
    description: "Turn outer diameter to 40mm h6 tolerance. Check surface finish Ra 1.6.",
  },
  "OP-002": {
    operation_id: "OP-002",
    routing_id: "RT-001",
    routing_code: "RT-SHAFT-001",
    routing_name: "Shaft Machining Route",
    operation_code: "OP-GRIND-01",
    operation_name: "Cylindrical Grinding",
    sequence_no: 20,
    lifecycle_status: "RELEASED",
    work_center: "WC-GRINDER-01",
    standard_cycle_time: 60,
    setup_time: 20,
    run_time_per_unit: 40,
    required_resource_type: "CYLINDRICAL_GRINDER",
    required_skill: "GRINDER_OPERATOR",
    required_skill_level: "LEVEL_3",
    qc_checkpoint_count: 3,
    description: "Grind to final dimension 40h6. Tolerance ±0.008mm. Measure at 3 points.",
  },
};

export function RoutingOperationDetail() {
  const { t } = useI18n();
  const { routeId, operationId } = useParams<{ routeId: string; operationId: string }>();
  const [operation] = useState<OperationDetail | null>(operationId ? (mockOperations[operationId] ?? null) : null);

  const resourceSection = operation ? [
    { label: "Required Resource Type", value: operation.required_resource_type },
    { label: "Required Skill", value: operation.required_skill ?? "—" },
    { label: "Skill Level", value: operation.required_skill_level ?? "—" },
  ] : [];

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="SHELL"
        note="Operation execution eligibility and resource applicability are determined by backend execution and MMD systems."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Back nav */}
        <div className="mb-4">
          <Link to={routeId ? `/routes/${routeId}` : "/routes"} className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
            <ArrowLeft className="w-4 h-4" />
            {t("routingOpDetail.back")}
          </Link>
        </div>

        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <GitBranch className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("routingOpDetail.title")}</h1>
            <ScreenStatusBadge phase="SHELL" />
          </div>
          <div className="flex items-center gap-2">
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("routingOpDetail.action.release")}
            </button>
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("routingOpDetail.action.edit")}
            </button>
          </div>
        </div>

        <BackendRequiredNotice message={t("routingOpDetail.notice.shell")} tone="blue" />

        {operation ? (
          <div className="space-y-6">
            {/* Identity section */}
            <div>
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">{t("routingOpDetail.section.identity")}</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.operationCode")}</div>
                  <div className="font-mono text-sm font-medium text-slate-700">{operation.operation_code}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.operationName")}</div>
                  <div className="text-sm text-slate-900">{operation.operation_name}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.routeCode")}</div>
                  <div className="font-mono text-sm text-slate-700">{operation.routing_code}</div>
                  <div className="text-xs text-gray-400">{operation.routing_name}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.sequence")}</div>
                  <RoutingOperationSequenceBadge sequence={operation.sequence_no} />
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.workCenter")}</div>
                  <div className="font-mono text-sm text-slate-700">{operation.work_center}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.status")}</div>
                  <RoutingLifecycleBadge status={operation.lifecycle_status} />
                </div>
              </div>
            </div>

            {/* Timing section */}
            <div>
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">{t("routingOpDetail.section.timing")}</h2>
              <div className="grid grid-cols-3 gap-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div>
                  <div className="text-xs text-blue-600 mb-1">{t("routingOpDetail.field.stdTime")}</div>
                  <div className="text-xl font-semibold text-blue-900">{operation.standard_cycle_time} min</div>
                </div>
                <div>
                  <div className="text-xs text-blue-600 mb-1">{t("routingOpDetail.field.setupTime")}</div>
                  <div className="text-xl font-semibold text-blue-900">{operation.setup_time} min</div>
                </div>
                <div>
                  <div className="text-xs text-blue-600 mb-1">{t("routingOpDetail.field.runTime")}</div>
                  <div className="text-xl font-semibold text-blue-900">{operation.run_time_per_unit} min</div>
                </div>
              </div>
            </div>

            {/* Resources section */}
            <div>
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">{t("routingOpDetail.section.resources")}</h2>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3">
                {resourceSection.map((r) => (
                  <div key={r.label} className="flex items-center gap-4">
                    <div className="w-48 text-xs text-gray-500">{r.label}</div>
                    <div className="font-mono text-sm text-slate-700">{r.value}</div>
                  </div>
                ))}
                <div className="flex items-center gap-4 pt-2 border-t border-gray-200">
                  <div className="text-xs text-gray-400 italic">Resource assignment and validation requires backend MMD and resource applicability check.</div>
                </div>
              </div>
            </div>

            {/* Quality section */}
            <div>
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">{t("routingOpDetail.section.quality")}</h2>
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="text-sm text-yellow-800">
                  <span className="font-medium">{operation.qc_checkpoint_count} checkpoint(s) configured</span>
                  <span className="text-yellow-600 ml-2">— QC checkpoint linkage is managed by backend quality domain.</span>
                </div>
              </div>
            </div>

            {/* Description */}
            {operation.description && (
              <div>
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Description</h2>
                <p className="text-sm text-slate-700 p-4 bg-gray-50 rounded-lg border border-gray-200">{operation.description}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 text-center text-gray-400">{t("routingOpDetail.notFound")} Connect to backend MMD API for live operation data.</div>
        )}

        <p className="mt-6 text-xs text-gray-400">
          Operation data is for visualization only. Backend execution system determines actual execution eligibility and routing applicability.
        </p>
      </div>
    </div>
  );
}

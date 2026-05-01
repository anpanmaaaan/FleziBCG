import { useState } from "react";
import { Lock, Server } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface ResourceRequirement {
  req_id: string;
  operation_code: string;
  operation_name: string;
  routing_code: string;
  resource_code: string;
  resource_name: string;
  resource_type: string;
  capability: string;
  qualification: string | null;
  setup_constraint: string | null;
  status: string;
}

const mockRequirements: ResourceRequirement[] = [
  {
    req_id: "RR-001",
    operation_code: "OP-TURN-01",
    operation_name: "CNC Turning",
    routing_code: "RT-SHAFT-001",
    resource_code: "ST-CNC-01",
    resource_name: "CNC Lathe Station 01",
    resource_type: "CNC_LATHE",
    capability: "TURNING_40MM",
    qualification: "ISO_TURNING_LVL2",
    setup_constraint: "Min 15 min setup, tool change required between jobs",
    status: "ACTIVE",
  },
  {
    req_id: "RR-002",
    operation_code: "OP-GRIND-01",
    operation_name: "Cylindrical Grinding",
    routing_code: "RT-SHAFT-001",
    resource_code: "ST-GRIND-01",
    resource_name: "Cylindrical Grinder Station 01",
    resource_type: "CYLINDRICAL_GRINDER",
    capability: "GRINDING_H6_TOLERANCE",
    qualification: "GRINDER_CERT_LVL3",
    setup_constraint: "Wheel dressing required before run",
    status: "ACTIVE",
  },
  {
    req_id: "RR-003",
    operation_code: "OP-MILL-01",
    operation_name: "Keyway Milling",
    routing_code: "RT-SHAFT-001",
    resource_code: "ST-MILL-01",
    resource_name: "Milling Station 01",
    resource_type: "CNC_MILL",
    capability: "KEYWAY_6MM",
    qualification: null,
    setup_constraint: null,
    status: "ACTIVE",
  },
  {
    req_id: "RR-004",
    operation_code: "OP-HEAT-01",
    operation_name: "Heat Treatment",
    routing_code: "RT-SHAFT-001",
    resource_code: "OUTSOURCE-HT",
    resource_name: "External Heat Treatment (Outsource)",
    resource_type: "OUTSOURCE",
    capability: "CASE_HARDENING_58HRC",
    qualification: "HT_SUPPLIER_CERT",
    setup_constraint: "3-day lead time, batch size min 10 pcs",
    status: "PENDING",
  },
];

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    ACTIVE: "bg-green-100 text-green-800 border-green-200",
    PENDING: "bg-yellow-100 text-yellow-800 border-yellow-200",
    INACTIVE: "bg-gray-100 text-gray-600 border-gray-200",
  };
  const cls = map[status.toUpperCase()] ?? "bg-gray-100 text-gray-600 border-gray-200";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}

export function ResourceRequirements() {
  const { t } = useI18n();
  const [reqs] = useState(mockRequirements);

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="SHELL"
        note="Resource applicability, capability, and qualification are managed by backend manufacturing master data system."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Server className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("resourceReqs.title")}</h1>
            <ScreenStatusBadge phase="SHELL" />
          </div>
          <button
            disabled
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
            title="Backend MMD governance workflow required"
          >
            <Lock className="w-3.5 h-3.5" />
            {t("resourceReqs.action.assign")}
          </button>
        </div>

        <BackendRequiredNotice message={t("resourceReqs.notice.shell")} tone="blue" />

        {/* Summary info */}
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
          <strong>Scope:</strong> This view shows the operation ↔ station/equipment resource requirement mapping. Capability, qualification, and setup constraints are visualized for product owner review. Backend MMD system remains source of truth for resource applicability.
        </div>

        {/* Table */}
        <div className="border border-gray-200 rounded-lg overflow-x-auto">
          <table className="w-full text-sm min-w-[900px]">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.operation")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.resource")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.capability")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.qualification")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.setupConstraint")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.status")}</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {reqs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-400">{t("resourceReqs.empty")}</td>
                </tr>
              ) : (
                reqs.map((r) => (
                  <tr key={r.req_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900">{r.operation_name}</div>
                      <div className="text-xs text-gray-400 font-mono">{r.operation_code}</div>
                      <div className="text-xs text-gray-400">{r.routing_code}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-slate-900">{r.resource_name}</div>
                      <div className="text-xs text-gray-400 font-mono">{r.resource_code}</div>
                      <div className="text-xs text-blue-600">{r.resource_type}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-0.5 rounded border text-xs bg-purple-50 text-purple-700 border-purple-200">{r.capability}</span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">{r.qualification ?? "—"}</td>
                    <td className="px-4 py-3 text-xs text-gray-600 max-w-[200px]">{r.setup_constraint ?? "—"}</td>
                    <td className="px-4 py-3"><StatusBadge status={r.status} /></td>
                    <td className="px-4 py-3">
                      <button disabled className="inline-flex items-center gap-1 text-xs text-gray-400 cursor-not-allowed" title="Backend MMD governance workflow required">
                        <Lock className="w-3 h-3" />
                        Edit
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <p className="mt-4 text-xs text-gray-400">
          Resource requirement data is for visualization only. Backend MMD system manages all resource-to-operation assignments, capability validation, and qualification checks.
        </p>
      </div>
    </div>
  );
}

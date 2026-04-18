// Operation Execution Detail - Tabs ONLY (No Gantt)
// Deep dive into a single operation execution

import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams, Link } from "react-router";
import {
  Clock,
  AlertTriangle,
  Package,
  Activity,
  FileText,
  History,
  Shield,
  CheckCircle,
  XCircle,
  TrendingUp,
  ExternalLink,
  ArrowLeft,
} from "lucide-react";
import { PageHeader } from "@/app/components";
import { StatusBadge } from "@/app/components";
import { StatsCard } from "@/app/components";
import { operationApi, type OperationDetail } from "@/app/api";
import {
  mapExecutionStatusText,
  mapExecutionStatusBadgeVariant,
  getProgressPercentage as calcProgressPercent,
  getYieldRate as calcYieldRate,
} from "@/app/api";
import { useI18n } from "@/app/i18n";

interface QCCheckpoint {
  id: string;
  name: string;
  type: "Dimensional" | "Visual" | "Functional" | "Material";
  status: "Pending" | "Passed" | "Failed" | "Skipped";
  result?: string;
  inspector?: string;
  timestamp?: string;
  specification: string;
  actualValue?: string;
}

interface MaterialItem {
  id: string;
  materialCode: string;
  materialName: string;
  requiredQty: number;
  consumedQty: number;
  unit: string;
  lotNumber?: string;
  status: "Available" | "In Use" | "Depleted" | "Overused";
}

interface TimelineEvent {
  id: string;
  timestamp: string;
  type: "Status Change" | "Operator Action" | "System Event" | "Quality Event" | "Material Event";
  description: string;
  user?: string;
  details?: string;
}

// Read-only placeholder data for tabs not yet backed by API endpoints.
const readOnlyQCCheckpoints: QCCheckpoint[] = [
  {
    id: "QC-001",
    name: "Bore Diameter Check",
    type: "Dimensional",
    status: "Passed",
    result: "Within tolerance",
    inspector: "Mary Johnson",
    timestamp: "2024-04-15 10:30",
    specification: "50.00mm +/- 0.01mm",
    actualValue: "50.005mm",
  },
  {
    id: "QC-002",
    name: "Surface Finish Inspection",
    type: "Visual",
    status: "Passed",
    result: "No defects",
    inspector: "Mary Johnson",
    timestamp: "2024-04-15 10:35",
    specification: "Ra 1.6um max",
    actualValue: "Ra 1.2um",
  },
  {
    id: "QC-003",
    name: "Perpendicularity Check",
    type: "Dimensional",
    status: "Pending",
    specification: "0.05mm per 100mm",
  },
];

const readOnlyMaterials: MaterialItem[] = [
  {
    id: "MAT-001",
    materialCode: "STL-4140",
    materialName: "Alloy Steel 4140",
    requiredQty: 50,
    consumedQty: 32,
    unit: "pcs",
    lotNumber: "LOT-2024-0415-001",
    status: "In Use",
  },
  {
    id: "MAT-002",
    materialCode: "TOOL-CB-10",
    materialName: "Carbide Drill Bit 10mm",
    requiredQty: 1,
    consumedQty: 1,
    unit: "pcs",
    lotNumber: "TOOL-2024-0401",
    status: "In Use",
  },
  {
    id: "MAT-003",
    materialCode: "COOL-SYN-5L",
    materialName: "Synthetic Coolant",
    requiredQty: 10,
    consumedQty: 6.5,
    unit: "L",
    status: "In Use",
  },
];

const readOnlyTimeline: TimelineEvent[] = [
  {
    id: "EVT-001",
    timestamp: "2024-04-15 08:35",
    type: "Status Change",
    description: "Operation started",
    user: "John Smith",
    details: "Status changed from Pending to In Progress",
  },
  {
    id: "EVT-002",
    timestamp: "2024-04-15 08:50",
    type: "Operator Action",
    description: "Setup completed",
    user: "John Smith",
    details: "Machine setup and calibration completed",
  },
  {
    id: "EVT-003",
    timestamp: "2024-04-15 09:00",
    type: "Material Event",
    description: "Material LOT-2024-0415-001 scanned",
    user: "John Smith",
  },
  {
    id: "EVT-004",
    timestamp: "2024-04-15 10:30",
    type: "Quality Event",
    description: "QC checkpoint passed",
    user: "Mary Johnson",
    details: "Bore Diameter Check - Passed",
  },
];

type TabType = "overview" | "quality" | "materials" | "timeline" | "documents";

export function OperationExecutionDetail() {
  const { operationId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [operation, setOperation] = useState<OperationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Gantt back-navigation context restored from URL params.
  const fromGantt = searchParams.get('from') === 'gantt';
  const ganttWoId = searchParams.get('woId');
  const ganttMode = searchParams.get('mode');
  const ganttGroupBy = searchParams.get('groupBy');
  const ganttSel = searchParams.get('sel');

  const handleBack = () => {
    if (fromGantt && ganttWoId) {
      const restoreParams = new URLSearchParams();
      if (ganttMode) restoreParams.set('mode', ganttMode);
      if (ganttGroupBy) restoreParams.set('groupBy', ganttGroupBy);
      if (ganttSel) restoreParams.set('sel', ganttSel);
      navigate(`/work-orders/${ganttWoId}/operations?${restoreParams.toString()}`);
    } else if (operation) {
      navigate(`/work-orders/${operation.work_order_id}/operations`);
    } else {
      navigate(-1);
    }
  };

  useEffect(() => {
    const loadOperation = async () => {
      if (!operationId) {
        setError(t("opDetail.error.missingId"));
        setOperation(null);
        setLoading(false);
        return;
      }

      const canonicalOperationId = operationId.trim();
      if (!/^\d+$/.test(canonicalOperationId)) {
        setError(t("opDetail.error.invalidId"));
        setOperation(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data = await operationApi.get(canonicalOperationId);
        setOperation(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : t("opDetail.error.loadFailed");
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    loadOperation();
  }, [operationId]);

  const tabs = [
    { id: "overview", label: t("opDetail.tab.overview"), icon: Activity },
    { id: "quality", label: t("opDetail.tab.quality"), icon: Shield },
    { id: "materials", label: t("opDetail.tab.materials"), icon: Package },
    { id: "timeline", label: t("opDetail.tab.timeline"), icon: History },
    { id: "documents", label: t("opDetail.tab.documents"), icon: FileText },
  ] as const;

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">{t("opDetail.loading")}</div>
      </div>
    );
  }

  if (error || !operation) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 p-6">
        <div className="max-w-xl w-full bg-white border border-red-200 rounded-lg p-6">
          <div className="flex items-center gap-2 text-red-700 font-semibold mb-2">
            <AlertTriangle className="w-5 h-5" />
            {t("opDetail.error.loadFailed")}
          </div>
          <div className="text-sm text-red-600">{error || t("opDetail.error.notFound")}</div>
        </div>
      </div>
    );
  }

  const statusText = mapExecutionStatusText(operation.status);
  const progressPercent = calcProgressPercent({
    completedQty: operation.completed_qty,
    targetQty: operation.quantity,
  });
  const yieldRate = calcYieldRate({
    goodQty: operation.good_qty,
    completedQty: operation.completed_qty,
  });
  const remainingQty = Math.max(0, operation.quantity - operation.completed_qty);

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <PageHeader
        title={
          <div className="flex items-center gap-4">
            <button
              onClick={handleBack}
              className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <ArrowLeft className="w-4 h-4" />
              {fromGantt ? t("opDetail.nav.backGantt") : t("opDetail.nav.backOverview")}
            </button>
            <div>
              <div className="text-sm text-gray-500">
                {t("opDetail.header.operationSeq", { seq: operation.sequence, number: operation.operation_number })}
              </div>
              <div className="text-2xl font-bold">{operation.name}</div>
            </div>
          </div>
        }
        showBackButton={false}
        actions={
          <>
            <StatusBadge variant={mapExecutionStatusBadgeVariant(operation.status)} size="lg">
              {statusText}
            </StatusBadge>
            <StatusBadge variant="info" size="lg">
              {t("opDetail.badge.readOnly")}
            </StatusBadge>
            <Link
              to={`/station-execution?operationId=${encodeURIComponent(String(operation.id))}`}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" />
              {t("opDetail.action.openStation")}
            </Link>
          </>
        }
      />

      <div className="flex-1 flex overflow-hidden">
        <div className="w-80 bg-white border-r border-gray-200 p-6 overflow-auto">
          <h3 className="text-lg font-bold mb-4">{t("opDetail.sidebar.title")}</h3>

          <div className="space-y-4">
            <div>
              <div className="text-sm text-gray-500">{t("opDetail.sidebar.operationId")}</div>
              <div className="font-mono font-bold text-lg text-blue-600">{operation.operation_number}</div>
            </div>

            <div>
              <div className="text-sm text-gray-500">{t("opDetail.sidebar.sequence")}</div>
              <div className="font-bold text-2xl">{operation.sequence}</div>
            </div>

            <div>
              <div className="text-sm text-gray-500">{t("opDetail.sidebar.station")}</div>
              <div className="font-medium">- / -</div>
            </div>

            <div>
              <div className="text-sm text-gray-500">{t("opDetail.sidebar.status")}</div>
              <StatusBadge variant={mapExecutionStatusBadgeVariant(operation.status)}>{statusText}</StatusBadge>
            </div>

            <div>
              <div className="text-sm text-gray-500">{t("opDetail.sidebar.progress")}</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all"
                    style={{ width: progressPercent + "%" }}
                  />
                </div>
                <span className="font-bold">{progressPercent}%</span>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="text-sm text-gray-500 mb-2">{t("opDetail.sidebar.plannedVsActual")}</div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">{t("opDetail.time.plannedStart")}</span>
                  <span className="font-medium">{operation.planned_start || "-"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">{t("opDetail.time.actualStart")}</span>
                  <span className="font-medium">{operation.actual_start || "-"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">{t("opDetail.time.plannedEnd")}</span>
                  <span className="font-medium">{operation.planned_end || "-"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">{t("opDetail.time.actualEnd")}</span>
                  <span className="font-medium">{operation.actual_end || "-"}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="bg-white border-b border-gray-200 px-6">
            <div className="flex gap-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as TabType)}
                    className={"flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2 " +
                      (activeTab === tab.id
                        ? "text-blue-600 border-blue-600"
                        : "text-gray-500 border-transparent hover:text-gray-700")}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex-1 overflow-auto p-6">
            {activeTab === "overview" && (
              <div className="space-y-6">
                <div className="grid grid-cols-5 gap-4">
                  <StatsCard
                    title={t("opDetail.kpi.completedQty")}
                    value={operation.completed_qty + "/" + operation.quantity}
                    color="blue"
                    icon={Package}
                  />
                  <StatsCard
                    title={t("opDetail.kpi.goodQty")}
                    value={operation.good_qty}
                    color="green"
                    icon={CheckCircle}
                  />
                  <StatsCard
                    title={t("opDetail.kpi.scrapQty")}
                    value={operation.scrap_qty}
                    color="red"
                    icon={XCircle}
                  />
                  <StatsCard title={t("common.progress")} value={progressPercent + "%"} color="purple" icon={TrendingUp} />
                  <StatsCard title={t("opDetail.kpi.yieldRate")} value={yieldRate.toFixed(1) + "%"} color="cyan" />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg border p-6">
                    <h3 className="text-lg font-bold mb-4">{t("opDetail.section.location")}</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.location.productionLine")}</span>
                        <span className="font-medium">-</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.location.workCenter")}</span>
                        <span className="font-medium">-</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.location.workstation")}</span>
                        <span className="font-medium">-</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.location.machine")}</span>
                        <span className="font-medium">-</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.location.machineId")}</span>
                        <span className="font-medium text-blue-600">-</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg border p-6">
                    <h3 className="text-lg font-bold mb-4">{t("opDetail.section.timeQty")}</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.timeQty.setupTime")}</span>
                        <span className="font-medium">-</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.timeQty.runTimePerUnit")}</span>
                        <span className="font-medium">-</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.timeQty.plannedQty")}</span>
                        <span className="font-medium">{operation.quantity} pcs</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.timeQty.completedQty")}</span>
                        <span className="font-medium text-blue-600">{operation.completed_qty} pcs</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t("opDetail.timeQty.remaining")}</span>
                        <span className="font-medium text-orange-600">{remainingQty} pcs</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">{t("opDetail.section.description")}</h3>
                  <p className="text-gray-700 leading-relaxed">
                    {t("opDetail.description.readOnly")}
                  </p>
                </div>
              </div>
            )}

            {activeTab === "quality" && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-blue-800">{t("opDetail.quality.readOnlyNotice")}</div>
                    <div className="text-sm text-blue-600 mt-1">
                      {t("opDetail.quality.readOnlyDesc")}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-4">
                  <StatsCard title={t("opDetail.quality.title")} value={readOnlyQCCheckpoints.length} color="blue" icon={Shield} />
                  <StatsCard
                    title={t("opDetail.quality.passed")}
                    value={readOnlyQCCheckpoints.filter((c) => c.status === "Passed").length}
                    color="green"
                    icon={CheckCircle}
                  />
                  <StatsCard
                    title={t("opDetail.quality.pending")}
                    value={readOnlyQCCheckpoints.filter((c) => c.status === "Pending").length}
                    color="orange"
                    icon={Clock}
                  />
                  <StatsCard title={t("opDetail.quality.fpYield")} value="93.8%" color="cyan" icon={TrendingUp} />
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">{t("opDetail.quality.listTitle")}</h3>
                  <div className="space-y-3">
                    {readOnlyQCCheckpoints.map((checkpoint) => (
                      <div key={checkpoint.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-bold">{checkpoint.name}</h4>
                              <StatusBadge
                                variant={
                                  checkpoint.status === "Passed"
                                    ? "success"
                                    : checkpoint.status === "Failed"
                                      ? "error"
                                      : checkpoint.status === "Pending"
                                        ? "warning"
                                        : "neutral"
                                }
                                size="sm"
                              >
                                {checkpoint.status}
                              </StatusBadge>
                              <span className="text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">{checkpoint.type}</span>
                            </div>
                            <div className="text-sm text-gray-500">ID: {checkpoint.id}</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">{t("opDetail.quality.spec")} </span>
                            <span className="font-medium">{checkpoint.specification}</span>
                          </div>
                          {checkpoint.actualValue && (
                            <div>
                              <span className="text-gray-500">{t("opDetail.quality.actual")} </span>
                              <span className="font-medium text-green-600">{checkpoint.actualValue}</span>
                            </div>
                          )}
                          {checkpoint.inspector && (
                            <div>
                              <span className="text-gray-500">{t("opDetail.quality.inspector")} </span>
                              <span className="font-medium">{checkpoint.inspector}</span>
                            </div>
                          )}
                          {checkpoint.timestamp && (
                            <div>
                              <span className="text-gray-500">{t("opDetail.quality.timestamp")} </span>
                              <span className="font-medium">{checkpoint.timestamp}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === "materials" && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-blue-800">{t("opDetail.materials.readOnlyNotice")}</div>
                    <div className="text-sm text-blue-600 mt-1">
                      {t("opDetail.materials.readOnlyDesc")}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-4">
                  <StatsCard title={t("opDetail.materials.totalMaterials")} value={readOnlyMaterials.length} color="blue" icon={Package} />
                  <StatsCard
                    title={t("opDetail.materials.inUse")}
                    value={readOnlyMaterials.filter((m) => m.status === "In Use").length}
                    color="green"
                  />
                  <StatsCard title={t("opDetail.materials.consumptionRate")} value="64%" color="purple" />
                  <StatsCard
                    title={t("common.status")}
                    value={readOnlyMaterials.some((m) => m.status === "Overused") ? "Alert" : "OK"}
                    color={readOnlyMaterials.some((m) => m.status === "Overused") ? "red" : "green"}
                  />
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">{t("opDetail.materials.bomTitle")}</h3>
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">{t("opDetail.materials.col.materialCode")}</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">{t("opDetail.materials.col.materialName")}</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">{t("opDetail.materials.col.required")}</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">{t("opDetail.materials.col.consumed")}</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">{t("opDetail.materials.col.remaining")}</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">{t("opDetail.materials.col.lotNumber")}</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">{t("opDetail.materials.col.status")}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {readOnlyMaterials.map((material) => {
                        const remaining = material.requiredQty - material.consumedQty;
                        const isOverused = remaining < 0;

                        return (
                          <tr key={material.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 font-mono text-sm">{material.materialCode}</td>
                            <td className="px-4 py-3">{material.materialName}</td>
                            <td className="px-4 py-3">
                              {material.requiredQty} {material.unit}
                            </td>
                            <td className="px-4 py-3 font-medium">
                              {material.consumedQty} {material.unit}
                            </td>
                            <td className={"px-4 py-3 font-medium " + (isOverused ? "text-red-600" : "text-orange-600")}>
                              {remaining} {material.unit}
                              {isOverused && <span className="ml-2 text-xs bg-red-100 px-2 py-0.5 rounded">Overused</span>}
                            </td>
                            <td className="px-4 py-3 font-mono text-xs">{material.lotNumber || "-"}</td>
                            <td className="px-4 py-3">
                              <StatusBadge
                                variant={
                                  material.status === "Overused"
                                    ? "error"
                                    : material.status === "In Use"
                                      ? "success"
                                      : "neutral"
                                }
                                size="sm"
                              >
                                {material.status}
                              </StatusBadge>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">{t("opDetail.materials.traceabilityTitle")}</h3>
                  <div className="space-y-4">
                    <div className="border rounded-lg p-4">
                      <div className="font-medium mb-2">Material: Alloy Steel 4140</div>
                      <div className="text-sm space-y-1 text-gray-600">
                        <div>
                          <span className="font-medium">Lot Number:</span> LOT-2024-0415-001
                        </div>
                        <div>
                          <span className="font-medium">Supplier:</span> ABC Steel Corp.
                        </div>
                        <div>
                          <span className="font-medium">Received Date:</span> 2024-04-10
                        </div>
                        <div>
                          <span className="font-medium">Heat Number:</span> H-45678-2024
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "timeline" && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-blue-800">{t("opDetail.quality.readOnlyNotice")}</div>
                    <div className="text-sm text-blue-600 mt-1">
                      {t("opDetail.timeline.readOnlyDesc")}
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">{t("opDetail.timeline.title")}</h3>
                  <div className="space-y-4">
                    {readOnlyTimeline.map((event, index) => (
                      <div key={event.id} className="flex gap-4">
                        <div className="flex flex-col items-center">
                          <div
                            className={
                              "w-3 h-3 rounded-full " +
                              (event.type === "Status Change"
                                ? "bg-blue-500"
                                : event.type === "Quality Event"
                                  ? "bg-green-500"
                                  : event.type === "Material Event"
                                    ? "bg-purple-500"
                                    : event.type === "System Event"
                                      ? "bg-red-500"
                                      : "bg-gray-500")
                            }
                          />
                          {index < readOnlyTimeline.length - 1 && <div className="w-0.5 h-full bg-gray-300 flex-1 mt-1" />}
                        </div>
                        <div className="flex-1 pb-4">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">{event.description}</span>
                            <span className="text-xs text-gray-500">{event.timestamp}</span>
                          </div>
                          {event.user && <div className="text-sm text-gray-600">By: {event.user}</div>}
                          {event.details && <div className="text-sm text-gray-500 mt-1">{event.details}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === "documents" && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-blue-800">{t("opDetail.quality.readOnlyNotice")}</div>
                    <div className="text-sm text-blue-600 mt-1">
                      {t("opDetail.documents.readOnlyDesc")}
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">{t("opDetail.documents.title")}</h3>
                  <div className="space-y-3">
                    <div className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-3">
                        <FileText className="w-10 h-10 text-blue-600" />
                        <div className="flex-1">
                          <div className="font-medium">Work Instruction - Bore Drilling</div>
                          <div className="text-sm text-gray-500">PDF - 2.4 MB - Updated 2024-04-10</div>
                        </div>
                      </div>
                    </div>
                    <div className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-3">
                        <FileText className="w-10 h-10 text-green-600" />
                        <div className="flex-1">
                          <div className="font-medium">Quality Control Procedure</div>
                          <div className="text-sm text-gray-500">PDF - 1.8 MB - Updated 2024-04-05</div>
                        </div>
                      </div>
                    </div>
                    <div className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-3">
                        <FileText className="w-10 h-10 text-purple-600" />
                        <div className="flex-1">
                          <div className="font-medium">Safety Guidelines</div>
                          <div className="text-sm text-gray-500">PDF - 0.9 MB - Updated 2024-03-20</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

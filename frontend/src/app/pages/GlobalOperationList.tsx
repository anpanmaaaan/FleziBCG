import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { AlertTriangle, CheckCircle, ChevronRight, Clock, Search } from "lucide-react";
import { toast } from "sonner";

import { operationMonitorApi } from "@/app/api";
import { mapExecutionStatusBadgeVariant, mapExecutionStatusText } from "@/app/api";
import type { OperationExecutionStatus } from "@/app/api/operationApi";
import { useAuth } from "@/app/auth";
import { PageHeader } from "@/app/components";
import { StatsCard } from "@/app/components";
import { StatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import {
  getAllowedOperationLenses,
  getFallbackOperationLens,
  resolvePersonaFromUser,
  type OperationLens,
} from "@/app/persona";

type SupervisorBucket = "BLOCKED" | "DELAYED" | "IN_PROGRESS" | "OTHER";
type MonitoringLens = "IE_PROCESS" | "SUPERVISOR" | "QC";
type GroupMode = "none" | "work_order" | "operation_number" | "work_center" | "route_step";

interface MonitorOperation {
  id: number;
  operationNumber: string;
  operationName: string;
  sequence: number;
  status: OperationExecutionStatus;
  supervisorBucket: SupervisorBucket;
  plannedStart: string | null;
  plannedEnd: string | null;
  quantity: number;
  completedQty: number;
  progress: number;
  productionOrderId: number;
  productionOrderNumber: string;
  workOrderId: number;
  workOrderNumber: string;
  workCenter: string | null;
  delayMinutes: number | null;
  blockReasonCode: string | null;
  qcRiskFlag: boolean;
  woBlockedOperations: number;
  woDelayedOperations: number;
  cycleTimeMinutes: number | null;
  cycleTimeDelta: number | null;
  delayCount: number;
  delayFrequency: number;
  repeatFlag: boolean;
  qcFailCount: number;
  highVarianceFlag: boolean;
  oftenLateFlag: boolean;
  routeStep: string | null;
}

interface ProductionOrderFilter {
  id: string;
  label: string;
}

const formatDateTime = (value: string | null): string => {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

function mapOperationLensToMonitoringLens(lens: OperationLens): MonitoringLens {
  if (lens === "ie") {
    return "IE_PROCESS";
  }
  if (lens === "qc") {
    return "QC";
  }
  return "SUPERVISOR";
}

function mapMonitoringLensToOperationLens(lens: MonitoringLens): OperationLens {
  if (lens === "IE_PROCESS") {
    return "ie";
  }
  if (lens === "QC") {
    return "qc";
  }
  return "supervisor";
}

export function GlobalOperationList() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { currentUser } = useAuth();
  const { t } = useI18n();
  const persona = resolvePersonaFromUser(currentUser);
  const allowedOperationLenses = getAllowedOperationLenses(persona);
  const fallbackOperationLens = getFallbackOperationLens(persona);
  const requestedLensParam = (searchParams.get("lens") ?? "").trim().toLowerCase();
  const activeOperationLens = allowedOperationLenses.includes(requestedLensParam as OperationLens)
    ? requestedLensParam as OperationLens
    : fallbackOperationLens;

  const [operations, setOperations] = useState<MonitorOperation[]>([]);
  const [productionOrderFilters, setProductionOrderFilters] = useState<ProductionOrderFilter[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState("");
  const [selectedLens, setSelectedLens] = useState<MonitoringLens>(() => mapOperationLensToMonitoringLens(activeOperationLens));
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [selectedProductionOrderId, setSelectedProductionOrderId] = useState("all");
  const [groupMode, setGroupMode] = useState<GroupMode>("operation_number");

  useEffect(() => {
    if (requestedLensParam !== activeOperationLens) {
      const nextSearchParams = new URLSearchParams(searchParams);
      nextSearchParams.set("lens", activeOperationLens);
      setSearchParams(nextSearchParams, { replace: true });
    }

    setSelectedLens(mapOperationLensToMonitoringLens(activeOperationLens));
  }, [activeOperationLens, requestedLensParam, searchParams, setSearchParams]);

  useEffect(() => {
    if (selectedLens === "SUPERVISOR" || selectedLens === "QC") {
      setSelectedStatus("SUPERVISOR_DEFAULT");
      setGroupMode("work_order");
      return;
    }

    setSelectedStatus("all");
    setGroupMode("operation_number");
  }, [selectedLens]);

  const getSupervisorBucket = (status: string, delayMinutes: number | null): SupervisorBucket => {
    if (status === "BLOCKED") {
      return "BLOCKED";
    }

    if (status === "LATE") {
      return "DELAYED";
    }

    if (delayMinutes !== null && delayMinutes > 0 && (status === "IN_PROGRESS" || status === "COMPLETED")) {
      return "DELAYED";
    }

    if (status === "IN_PROGRESS") {
      return "IN_PROGRESS";
    }

    return "OTHER";
  };

  useEffect(() => {
    const loadOperations = async () => {
      setLoading(true);
      setError(null);

      try {
        const productionOrders = await operationMonitorApi.listProductionOrders();
        const productionOrderDetails = await Promise.all(
          productionOrders.map((productionOrder) => operationMonitorApi.getProductionOrder(productionOrder.id)),
        );

        const allOperations: MonitorOperation[] = [];
        for (const productionOrder of productionOrderDetails) {
          const workOrders = productionOrder.workOrders || [];

          for (const workOrder of workOrders) {
            const workOrderOperations = await operationMonitorApi.getWorkOrderOperations(workOrder.id);
            allOperations.push(
              ...workOrderOperations.map((operation) => ({
                id: operation.id,
                operationNumber: operation.operationNumber ?? operation.operation_number ?? String(operation.id),
                operationName: operation.name,
                sequence: operation.sequence,
                status: operation.status as OperationExecutionStatus,
                supervisorBucket: operation.supervisorBucket
                  ?? operation.supervisor_bucket
                  ?? getSupervisorBucket(operation.status, operation.delayMinutes ?? operation.delay_minutes ?? null),
                plannedStart: operation.plannedStart ?? operation.planned_start ?? null,
                plannedEnd: operation.plannedEnd ?? operation.planned_end ?? null,
                quantity: operation.quantity,
                completedQty: operation.completedQty ?? operation.completed_qty ?? 0,
                progress: operation.progress,
                productionOrderId: productionOrder.id,
                productionOrderNumber: productionOrder.orderNumber,
                workOrderId: workOrder.id,
                workOrderNumber: operation.workOrderNumber ?? operation.work_order_number ?? workOrder.workOrderNumber,
                workCenter: operation.workCenter ?? operation.work_center ?? null,
                delayMinutes: operation.delayMinutes ?? operation.delay_minutes ?? null,
                blockReasonCode: operation.blockReasonCode ?? operation.block_reason_code ?? null,
                qcRiskFlag: Boolean(operation.qcRiskFlag ?? operation.qc_risk_flag),
                woBlockedOperations: operation.woBlockedOperations ?? operation.wo_blocked_operations ?? 0,
                woDelayedOperations: operation.woDelayedOperations ?? operation.wo_delayed_operations ?? 0,
                cycleTimeMinutes: operation.cycleTimeMinutes ?? operation.cycle_time_minutes ?? null,
                cycleTimeDelta: operation.cycleTimeDelta ?? operation.cycle_time_delta ?? null,
                delayCount: operation.delayCount ?? operation.delay_count ?? 0,
                delayFrequency: operation.delayFrequency ?? operation.delay_frequency ?? 0,
                repeatFlag: Boolean(operation.repeatFlag ?? operation.repeat_flag),
                qcFailCount: operation.qcFailCount ?? operation.qc_fail_count ?? 0,
                highVarianceFlag: Boolean(operation.highVarianceFlag ?? operation.high_variance_flag),
                oftenLateFlag: Boolean(operation.oftenLateFlag ?? operation.often_late_flag),
                routeStep: operation.routeStep ?? operation.route_step ?? null,
              })),
            );
          }
        }

        setOperations(allOperations);
        setProductionOrderFilters(
          productionOrderDetails
            .map((productionOrder) => ({
              id: String(productionOrder.id),
              label: productionOrder.orderNumber,
            }))
            .sort((a, b) => a.label.localeCompare(b.label)),
        );
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load operations.";
        setError(message);
        toast.error(message);
      } finally {
        setLoading(false);
      }
    };

    loadOperations();
  }, []);

  const filteredOperations = useMemo(() => {
    return operations.filter((operation) => {
      if ((selectedLens === "SUPERVISOR" || selectedLens === "QC") && selectedStatus === "SUPERVISOR_DEFAULT") {
        if (!["BLOCKED", "DELAYED", "IN_PROGRESS"].includes(operation.supervisorBucket)) {
          return false;
        }
      } else if ((selectedLens === "SUPERVISOR" || selectedLens === "QC") && selectedStatus === "DELAYED") {
        if (operation.supervisorBucket !== "DELAYED") {
          return false;
        }
      } else if (selectedStatus !== "all" && operation.status !== selectedStatus) {
        return false;
      }

      if (selectedProductionOrderId !== "all" && String(operation.productionOrderId) !== selectedProductionOrderId) {
        return false;
      }

      if (!searchValue.trim()) {
        return true;
      }

      const q = searchValue.trim().toLowerCase();
      return (
        operation.operationNumber.toLowerCase().includes(q)
        || operation.operationName.toLowerCase().includes(q)
        || operation.workOrderNumber.toLowerCase().includes(q)
        || operation.productionOrderNumber.toLowerCase().includes(q)
        || (operation.routeStep ?? "").toLowerCase().includes(q)
      );
    });
  }, [operations, searchValue, selectedStatus, selectedProductionOrderId, selectedLens]);

  const sortedOperations = useMemo(() => {
    if (selectedLens === "IE_PROCESS") {
      return [...filteredOperations].sort((a, b) => {
        const deltaA = a.cycleTimeDelta ?? Number.NEGATIVE_INFINITY;
        const deltaB = b.cycleTimeDelta ?? Number.NEGATIVE_INFINITY;
        if (deltaA !== deltaB) {
          return deltaB - deltaA;
        }

        if (a.delayFrequency !== b.delayFrequency) {
          return b.delayFrequency - a.delayFrequency;
        }

        if (a.operationNumber !== b.operationNumber) {
          return a.operationNumber.localeCompare(b.operationNumber);
        }

        return a.sequence - b.sequence;
      });
    }

    const bucketPriority: Record<SupervisorBucket, number> = {
      BLOCKED: 0,
      DELAYED: 1,
      IN_PROGRESS: 2,
      OTHER: 3,
    };

    return [...filteredOperations].sort((a, b) => {
      if (bucketPriority[a.supervisorBucket] !== bucketPriority[b.supervisorBucket]) {
        return bucketPriority[a.supervisorBucket] - bucketPriority[b.supervisorBucket];
      }

      const delayA = a.delayMinutes ?? 0;
      const delayB = b.delayMinutes ?? 0;
      if (delayA !== delayB) {
        return delayB - delayA;
      }

      if (a.workOrderNumber !== b.workOrderNumber) {
        return a.workOrderNumber.localeCompare(b.workOrderNumber);
      }

      return a.sequence - b.sequence;
    });
  }, [filteredOperations, selectedLens]);

  const groupedOperations = useMemo(() => {
    if (groupMode === "none") {
      return [] as Array<[string, MonitorOperation[]]>;
    }

    const groups = new Map<string, MonitorOperation[]>();

    const getGroupKey = (operation: MonitorOperation): string => {
      if (groupMode === "work_order") {
        return `${t("operations.group.label.work_order", "WO")}: ${operation.workOrderNumber}`;
      }
      if (groupMode === "operation_number") {
        return `${t("operations.group.label.operation_number", "OP")}: ${operation.operationNumber}`;
      }
      if (groupMode === "work_center") {
        return `${t("operations.group.label.work_center", "WC")}: ${operation.workCenter ?? t("operations.ie.group.unassigned", "Unassigned")}`;
      }
      return `${t("operations.group.label.route_step", "ROUTE")}: ${operation.routeStep ?? t("operations.ie.group.unassigned", "Unassigned")}`;
    };

    for (const operation of sortedOperations) {
      const key = getGroupKey(operation);
      const existing = groups.get(key) ?? [];
      existing.push(operation);
      groups.set(key, existing);
    }

    return Array.from(groups.entries());
  }, [sortedOperations, groupMode, t]);

  const stats = useMemo(() => {
    const blocked = operations.filter((operation) => operation.supervisorBucket === "BLOCKED").length;
    const delayed = operations.filter((operation) => operation.supervisorBucket === "DELAYED").length;
    const inProgress = operations.filter((operation) => operation.status === "IN_PROGRESS").length;
    const repeatIssues = operations.filter((operation) => operation.repeatFlag).length;
    const highVariance = operations.filter((operation) => operation.highVarianceFlag).length;
    const oftenLate = operations.filter((operation) => operation.oftenLateFlag).length;

    return {
      total: operations.length,
      blocked,
      delayed,
      inProgress,
      repeatIssues,
      highVariance,
      oftenLate,
    };
  }, [operations]);

  const subtitle = selectedLens === "IE_PROCESS"
    ? t("operations.ie.subtitle", "Global Operations - IE / Process Investigation Lens")
    : selectedLens === "QC"
    ? t("operations.qa.subtitle", "Global Operations - QC Lens")
    : t("operations.supervisor.subtitle", "Global Operations - Supervisor Investigation Lens");

  const lensNotice = selectedLens === "IE_PROCESS"
    ? t(
      "operations.ie.read_only_notice",
      "Read-only IE/Process investigation workspace for recurring delay and variability patterns. No execution actions are available on this screen.",
    )
    : selectedLens === "QC"
    ? t(
      "operations.qc.read_only_notice",
      "Read-only QC placeholder lens. QC status is visible, but no approval or execution actions are available in this phase.",
    )
    : t(
      "operations.supervisor.read_only_notice",
      "Read-only supervisor investigation workspace for blocked and delayed operations. No execution actions are available on this screen.",
    );

  const showGrouped = groupMode !== "none";

  const formatDelta = (value: number | null): string => {
    if (value === null) {
      return "-";
    }
    return `${value > 0 ? "+" : ""}${value}m`;
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title="Execution - Operations"
        subtitle={subtitle}
        breadcrumb={
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span>Execution</span>
            <span>{">"}</span>
            <span className="font-medium text-gray-700">Operations</span>
          </div>
        }
      />

      <div className="px-6 py-3 border-b border-gray-100 bg-slate-50">
        <div className="flex items-start gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
          <AlertTriangle className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
          <p>{lensNotice}</p>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {loading && (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 mx-auto mb-3 text-blue-500 animate-spin" style={{ animationDuration: "2s" }} />
            <div className="text-lg font-medium text-gray-600">Loading operations...</div>
          </div>
        )}

        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <div className="flex gap-3">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900">Failed to load operations</h3>
                <p className="text-red-700 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="grid grid-cols-4 gap-4 mb-6">
              <StatsCard title="Total Operations" value={stats.total} color="blue" />
              {selectedLens === "SUPERVISOR" || selectedLens === "QC" ? (
                <>
                  <StatsCard title={t("operations.supervisor.stats.blocked", "Blocked")} value={stats.blocked} color="red" icon={AlertTriangle} />
                  <StatsCard title={t("operations.supervisor.stats.delayed", "Delayed")} value={stats.delayed} color="yellow" icon={Clock} />
                  <StatsCard title="In Progress" value={stats.inProgress} color="purple" icon={CheckCircle} />
                </>
              ) : (
                <>
                  <StatsCard title={t("operations.ie.stats.repeat_issues", "Repeat Issues")} value={stats.repeatIssues} color="orange" icon={AlertTriangle} />
                  <StatsCard title={t("operations.ie.stats.high_variance", "High Variance")} value={stats.highVariance} color="yellow" icon={Clock} />
                  <StatsCard title={t("operations.ie.stats.often_late", "Often Late")} value={stats.oftenLate} color="purple" icon={CheckCircle} />
                </>
              )}
            </div>

            <div className="bg-gray-50 p-4 rounded-lg mb-6">
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-4">
                  <select
                    value={mapMonitoringLensToOperationLens(selectedLens)}
                    onChange={(event) => {
                      const nextLens = event.target.value as OperationLens;
                      const nextSearchParams = new URLSearchParams(searchParams);
                      nextSearchParams.set("lens", nextLens);
                      setSearchParams(nextSearchParams, { replace: true });
                    }}
                    className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                    disabled={allowedOperationLenses.length === 1}
                  >
                    {allowedOperationLenses.includes("ie") && (
                      <option value="ie">{t("operations.lens.ie_process", "IE / Process Lens")}</option>
                    )}
                    {allowedOperationLenses.includes("supervisor") && (
                      <option value="supervisor">{t("operations.lens.supervisor", "Supervisor Lens")}</option>
                    )}
                    {allowedOperationLenses.includes("qc") && (
                      <option value="qc">{t("operations.lens.qc", "QC Lens")}</option>
                    )}
                  </select>

                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      value={searchValue}
                      onChange={(event) => setSearchValue(event.target.value)}
                      placeholder="Search operation, work order, or production order"
                      className="pl-9 pr-3 py-2 border rounded-lg w-[360px] focus:outline-none focus:ring-2 focus:ring-focus-ring"
                    />
                  </div>

                  <select
                    value={selectedStatus}
                    onChange={(event) => setSelectedStatus(event.target.value)}
                    className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                  >
                    {(selectedLens === "SUPERVISOR" || selectedLens === "QC") && (
                      <option value="SUPERVISOR_DEFAULT">
                        {t("operations.supervisor.filter.default", "Supervisor Default (Blocked, Delayed, In Progress)")}
                      </option>
                    )}
                    <option value="all">All Statuses</option>
                    {(selectedLens === "SUPERVISOR" || selectedLens === "QC") && (
                      <option value="BLOCKED">{t("operations.supervisor.status.blocked", "Blocked")}</option>
                    )}
                    {(selectedLens === "SUPERVISOR" || selectedLens === "QC") && (
                      <option value="DELAYED">{t("operations.supervisor.status.delayed", "Delayed")}</option>
                    )}
                    <option value="PLANNED">{t("operations.status.planned", "Planned")}</option>
                    <option value="IN_PROGRESS">{t("operations.status.in_progress", "In Progress")}</option>
                    <option value="COMPLETED">{t("operations.status.completed", "Completed")}</option>
                    <option value="COMPLETED_LATE">{t("operations.status.completed_late", "Completed Late")}</option>
                  </select>

                  <select
                    value={selectedProductionOrderId}
                    onChange={(event) => setSelectedProductionOrderId(event.target.value)}
                    className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                  >
                    <option value="all">All Production Orders</option>
                    {productionOrderFilters.map((productionOrder) => (
                      <option key={productionOrder.id} value={productionOrder.id}>
                        {productionOrder.label}
                      </option>
                    ))}
                  </select>

                  <select
                    value={groupMode}
                    onChange={(event) => setGroupMode(event.target.value as GroupMode)}
                    className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                  >
                    <option value="none">{t("operations.group.none", "No Grouping")}</option>
                    <option value="work_order">{t("operations.group.work_order", "Group by Work Order")}</option>
                    <option value="operation_number">{t("operations.group.operation_number", "Group by Operation Number")}</option>
                    <option value="work_center">{t("operations.group.work_center", "Group by Work Center")}</option>
                    <option value="route_step">{t("operations.group.route_step", "Group by Route Step")}</option>
                  </select>
                </div>

                <div className="text-sm text-gray-600">
                  Showing <span className="font-semibold">{sortedOperations.length}</span> operations
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {!showGrouped && sortedOperations.map((operation) => (
                <button
                  type="button"
                  key={operation.id}
                  className="w-full text-left border rounded-lg p-5 hover:shadow-md transition-all bg-white group"
                  onClick={() => navigate(`/operations/${operation.id}/detail`)}
                >
                  <div className="flex items-center gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <span className="font-bold text-lg font-mono">{operation.operationNumber}</span>
                        <StatusBadge variant={mapExecutionStatusBadgeVariant(operation.status)}>
                          {mapExecutionStatusText(operation.status)}
                        </StatusBadge>
                        {operation.supervisorBucket === "DELAYED" && (
                          <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium">
                            {t("operations.supervisor.status.delayed", "Delayed")}
                          </span>
                        )}
                        {selectedLens === "IE_PROCESS" && operation.oftenLateFlag && (
                          <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium">
                            {t("operations.ie.cue.often_late", "Often Late")}
                          </span>
                        )}
                        {selectedLens === "IE_PROCESS" && operation.highVarianceFlag && (
                          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full font-medium">
                            {t("operations.ie.cue.high_variance", "High Variance")}
                          </span>
                        )}
                        {selectedLens === "IE_PROCESS" && operation.repeatFlag && (
                          <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full font-medium">
                            {t("operations.ie.cue.repeat_issue", "Repeat Issue")}
                          </span>
                        )}
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full font-medium">
                          Seq {operation.sequence}
                        </span>
                      </div>

                      <div className="text-sm text-gray-800 font-medium mb-2">{operation.operationName}</div>

                      <div className="flex items-center gap-6 text-sm text-gray-600 flex-wrap mb-2">
                        <span>PO: {operation.productionOrderNumber}</span>
                        <span>WO: {operation.workOrderNumber}</span>
                        <span>Qty: {operation.completedQty}/{operation.quantity}</span>
                        <span>Progress: {operation.progress}%</span>
                        <span>Planned End: {formatDateTime(operation.plannedEnd)}</span>
                        <span>Delay: {operation.delayMinutes ?? 0} min</span>
                        {selectedLens === "IE_PROCESS" && <span>{t("operations.ie.label.cycle", "Cycle")}: {operation.cycleTimeMinutes ?? "-"} min</span>}
                        {selectedLens === "IE_PROCESS" && <span>{t("operations.ie.label.cycle_delta", "Cycle Delta")}: {formatDelta(operation.cycleTimeDelta)}</span>}
                      </div>

                      <div className="flex items-center gap-3 text-xs text-gray-600 flex-wrap">
                        <span className="px-2 py-1 rounded-full bg-slate-100">WO Blocked Ops: {operation.woBlockedOperations}</span>
                        <span className="px-2 py-1 rounded-full bg-amber-100 text-amber-700">WO Delayed Ops: {operation.woDelayedOperations}</span>
                        {selectedLens === "IE_PROCESS" && (
                          <span className="px-2 py-1 rounded-full bg-slate-100">{t("operations.ie.label.delay_count", "Delay Count")}: {operation.delayCount}</span>
                        )}
                        {selectedLens === "IE_PROCESS" && (
                          <span className="px-2 py-1 rounded-full bg-slate-100">{t("operations.ie.label.delay_frequency", "Delay Frequency")}: {(operation.delayFrequency * 100).toFixed(1)}%</span>
                        )}
                        {selectedLens === "IE_PROCESS" && (
                          <span className="px-2 py-1 rounded-full bg-slate-100">{t("operations.ie.label.qc_fail_count", "QC Fail Count")}: {operation.qcFailCount}</span>
                        )}
                        {selectedLens === "IE_PROCESS" && operation.routeStep && (
                          <span className="px-2 py-1 rounded-full bg-indigo-100 text-indigo-700">{t("operations.ie.label.route_step", "Route Step")}: {operation.routeStep}</span>
                        )}
                        {operation.blockReasonCode && (
                          <span className="px-2 py-1 rounded-full bg-red-100 text-red-700">
                            Block Reason: {operation.blockReasonCode}
                          </span>
                        )}
                        {operation.qcRiskFlag && (
                          <span className="px-2 py-1 rounded-full bg-orange-100 text-orange-700">QC Risk</span>
                        )}
                        {operation.workCenter && (
                          <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-700">WC: {operation.workCenter}</span>
                        )}
                      </div>
                    </div>

                    <div className="flex-shrink-0">
                      <div className="flex items-center gap-2 text-gray-400 group-hover:text-blue-600 transition-colors">
                        <span className="text-sm font-medium">View Detail</span>
                        <ChevronRight className="w-4 h-4" />
                      </div>
                    </div>
                  </div>
                </button>
              ))}

              {showGrouped && groupedOperations.map(([groupKey, groupOperations]) => {
                const lead = groupOperations[0];
                return (
                  <div key={groupKey} className="border rounded-lg p-4 bg-white">
                    <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                      <div className="text-sm font-semibold text-gray-800">{groupKey} ({groupOperations.length} ops)</div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="px-2 py-1 rounded-full bg-slate-100">Blocked: {lead.woBlockedOperations}</span>
                        <span className="px-2 py-1 rounded-full bg-amber-100 text-amber-700">Delayed: {lead.woDelayedOperations}</span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {groupOperations.map((operation) => (
                        <button
                          type="button"
                          key={operation.id}
                          className="w-full text-left border rounded-lg p-3 hover:shadow-sm transition-all group"
                          onClick={() => navigate(`/operations/${operation.id}/detail`)}
                        >
                          <div className="flex items-center justify-between gap-3 flex-wrap">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-mono font-semibold">{operation.operationNumber}</span>
                              <StatusBadge variant={mapExecutionStatusBadgeVariant(operation.status)}>
                                {mapExecutionStatusText(operation.status)}
                              </StatusBadge>
                              <span className="text-xs text-gray-500">Seq {operation.sequence}</span>
                              <span className="text-xs text-gray-500">Delay {operation.delayMinutes ?? 0} min</span>
                              {selectedLens === "IE_PROCESS" && (
                                <span className="text-xs text-gray-500">{t("operations.ie.label.cycle_delta", "Cycle Delta")} {formatDelta(operation.cycleTimeDelta)}</span>
                              )}
                            </div>
                            <div className="text-sm text-gray-400 group-hover:text-blue-600 transition-colors flex items-center gap-1">
                              <span>View Detail</span>
                              <ChevronRight className="w-4 h-4" />
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            {sortedOperations.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <div className="text-lg font-medium mb-1">No operations found</div>
                <div className="text-sm">Try adjusting filters or search criteria</div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

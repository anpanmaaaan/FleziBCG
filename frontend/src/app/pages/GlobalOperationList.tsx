import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { AlertTriangle, CheckCircle, ChevronRight, Clock, Search } from "lucide-react";
import { toast } from "sonner";

import { operationMonitorApi } from "../api/operationMonitorApi";
import { mapExecutionStatusBadgeVariant, mapExecutionStatusText } from "../api/mappers/executionMapper";
import { PageHeader } from "../components/PageHeader";
import { StatsCard } from "../components/StatsCard";
import { StatusBadge } from "../components/StatusBadge";
import { useI18n } from "../i18n";

type SupervisorBucket = "BLOCKED" | "DELAYED" | "IN_PROGRESS" | "OTHER";

interface MonitorOperation {
  id: number;
  operationNumber: string;
  operationName: string;
  sequence: number;
  status: string;
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

export function GlobalOperationList() {
  const navigate = useNavigate();
  const { t } = useI18n();

  const [operations, setOperations] = useState<MonitorOperation[]>([]);
  const [productionOrderFilters, setProductionOrderFilters] = useState<ProductionOrderFilter[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("SUPERVISOR_DEFAULT");
  const [selectedProductionOrderId, setSelectedProductionOrderId] = useState("all");
  const [groupByWorkOrder, setGroupByWorkOrder] = useState(false);

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
                operationNumber: operation.operationNumber,
                operationName: operation.name,
                sequence: operation.sequence,
                status: operation.status,
                supervisorBucket: operation.supervisorBucket
                  ?? getSupervisorBucket(operation.status, operation.delayMinutes ?? null),
                plannedStart: operation.plannedStart,
                plannedEnd: operation.plannedEnd,
                quantity: operation.quantity,
                completedQty: operation.completedQty,
                progress: operation.progress,
                productionOrderId: productionOrder.id,
                productionOrderNumber: productionOrder.orderNumber,
                workOrderId: workOrder.id,
                workOrderNumber: operation.workOrderNumber ?? workOrder.workOrderNumber,
                workCenter: operation.workCenter ?? null,
                delayMinutes: operation.delayMinutes ?? null,
                blockReasonCode: operation.blockReasonCode ?? null,
                qcRiskFlag: Boolean(operation.qcRiskFlag),
                woBlockedOperations: operation.woBlockedOperations ?? 0,
                woDelayedOperations: operation.woDelayedOperations ?? 0,
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
      if (selectedStatus === "SUPERVISOR_DEFAULT") {
        if (!["BLOCKED", "DELAYED", "IN_PROGRESS"].includes(operation.supervisorBucket)) {
          return false;
        }
      } else if (selectedStatus === "DELAYED") {
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
      );
    });
  }, [operations, searchValue, selectedStatus, selectedProductionOrderId]);

  const sortedOperations = useMemo(() => {
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
  }, [filteredOperations]);

  const groupedByWorkOrder = useMemo(() => {
    const groups = new Map<string, MonitorOperation[]>();
    for (const operation of sortedOperations) {
      const key = `${operation.workOrderNumber}__${operation.workOrderId}`;
      const existing = groups.get(key) ?? [];
      existing.push(operation);
      groups.set(key, existing);
    }
    return Array.from(groups.entries());
  }, [sortedOperations]);

  const stats = useMemo(() => {
    const blocked = operations.filter((operation) => operation.supervisorBucket === "BLOCKED").length;
    const delayed = operations.filter((operation) => operation.supervisorBucket === "DELAYED").length;
    const inProgress = operations.filter((operation) => operation.status === "IN_PROGRESS").length;

    return {
      total: operations.length,
      blocked,
      delayed,
      inProgress,
    };
  }, [operations]);

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title="Execution - Operations"
        subtitle={t("operations.supervisor.subtitle", "Global Operations - Supervisor Investigation Lens")}
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
          <p>
            {t(
              "operations.supervisor.read_only_notice",
              "Read-only supervisor investigation workspace for blocked and delayed operations. No execution actions are available on this screen.",
            )}
          </p>
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
              <StatsCard title={t("operations.supervisor.stats.blocked", "Blocked")} value={stats.blocked} color="red" icon={AlertTriangle} />
              <StatsCard title={t("operations.supervisor.stats.delayed", "Delayed")} value={stats.delayed} color="yellow" icon={Clock} />
              <StatsCard title="In Progress" value={stats.inProgress} color="purple" icon={CheckCircle} />
            </div>

            <div className="bg-gray-50 p-4 rounded-lg mb-6">
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      value={searchValue}
                      onChange={(event) => setSearchValue(event.target.value)}
                      placeholder="Search operation, work order, or production order"
                      className="pl-9 pr-3 py-2 border rounded-lg w-[360px] focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <select
                    value={selectedStatus}
                    onChange={(event) => setSelectedStatus(event.target.value)}
                    className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="SUPERVISOR_DEFAULT">
                      {t("operations.supervisor.filter.default", "Supervisor Default (Blocked, Delayed, In Progress)")}
                    </option>
                    <option value="all">All Statuses</option>
                    <option value="BLOCKED">{t("operations.supervisor.status.blocked", "Blocked")}</option>
                    <option value="DELAYED">{t("operations.supervisor.status.delayed", "Delayed")}</option>
                    <option value="PENDING">Pending</option>
                    <option value="IN_PROGRESS">In Progress</option>
                    <option value="COMPLETED">Completed</option>
                  </select>

                  <select
                    value={selectedProductionOrderId}
                    onChange={(event) => setSelectedProductionOrderId(event.target.value)}
                    className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Production Orders</option>
                    {productionOrderFilters.map((productionOrder) => (
                      <option key={productionOrder.id} value={productionOrder.id}>
                        {productionOrder.label}
                      </option>
                    ))}
                  </select>

                  <button
                    type="button"
                    onClick={() => setGroupByWorkOrder((value) => !value)}
                    className={`px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${groupByWorkOrder
                      ? "bg-blue-50 text-blue-700 border-blue-300"
                      : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    {groupByWorkOrder
                      ? t("operations.supervisor.grouped.label", "Grouped by Work Order")
                      : t("operations.supervisor.group.label", "Group by Work Order")}
                  </button>
                </div>

                <div className="text-sm text-gray-600">
                  Showing <span className="font-semibold">{sortedOperations.length}</span> operations
                </div>
              </div>
            </div>

            {/* TODO(Phase 2C): Add IE/Process analytics lens in a separate monitoring mode. */}
            {/* TODO(Phase 2C): Add QA-focused risk lens with quality-specific filters. */}

            <div className="space-y-4">
              {!groupByWorkOrder && sortedOperations.map((operation) => (
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
                      </div>

                      <div className="flex items-center gap-3 text-xs text-gray-600 flex-wrap">
                        <span className="px-2 py-1 rounded-full bg-slate-100">WO Blocked Ops: {operation.woBlockedOperations}</span>
                        <span className="px-2 py-1 rounded-full bg-amber-100 text-amber-700">WO Delayed Ops: {operation.woDelayedOperations}</span>
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

              {groupByWorkOrder && groupedByWorkOrder.map(([groupKey, groupOperations]) => {
                const lead = groupOperations[0];
                return (
                  <div key={groupKey} className="border rounded-lg p-4 bg-white">
                    <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                      <div className="text-sm font-semibold text-gray-800">
                        WO: {lead.workOrderNumber} ({groupOperations.length} ops)
                      </div>
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

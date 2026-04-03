import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { AlertTriangle, CheckCircle, ChevronRight, Clock, Search } from "lucide-react";
import { toast } from "sonner";

import { operationMonitorApi } from "../api/operationMonitorApi";
import { mapExecutionStatusBadgeVariant, mapExecutionStatusText } from "../api/mappers/executionMapper";
import { PageHeader } from "../components/PageHeader";
import { StatsCard } from "../components/StatsCard";
import { StatusBadge } from "../components/StatusBadge";

interface MonitorOperation {
  id: number;
  operationNumber: string;
  operationName: string;
  sequence: number;
  status: string;
  plannedStart: string | null;
  plannedEnd: string | null;
  quantity: number;
  completedQty: number;
  progress: number;
  productionOrderId: number;
  productionOrderNumber: string;
  workOrderId: number;
  workOrderNumber: string;
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

  const [operations, setOperations] = useState<MonitorOperation[]>([]);
  const [productionOrderFilters, setProductionOrderFilters] = useState<ProductionOrderFilter[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [selectedProductionOrderId, setSelectedProductionOrderId] = useState("all");

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
                plannedStart: operation.plannedStart,
                plannedEnd: operation.plannedEnd,
                quantity: operation.quantity,
                completedQty: operation.completedQty,
                progress: operation.progress,
                productionOrderId: productionOrder.id,
                productionOrderNumber: productionOrder.orderNumber,
                workOrderId: workOrder.id,
                workOrderNumber: workOrder.workOrderNumber,
              })),
            );
          }
        }

        allOperations.sort((a, b) => {
          if (a.productionOrderNumber !== b.productionOrderNumber) {
            return a.productionOrderNumber.localeCompare(b.productionOrderNumber);
          }
          if (a.workOrderNumber !== b.workOrderNumber) {
            return a.workOrderNumber.localeCompare(b.workOrderNumber);
          }
          return a.sequence - b.sequence;
        });

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
      if (selectedStatus !== "all" && operation.status !== selectedStatus) {
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

  const stats = useMemo(() => {
    const completed = operations.filter((operation) => operation.status === "COMPLETED").length;
    const inProgress = operations.filter((operation) => operation.status === "IN_PROGRESS").length;
    const pending = operations.filter((operation) => operation.status === "PENDING").length;
    return {
      total: operations.length,
      completed,
      inProgress,
      pending,
    };
  }, [operations]);

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title="Execution - Operations"
        subtitle="Global Operation Monitoring"
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
            Read-only monitoring view. Operation execution state is loaded from backend data; no execution actions are available here.
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
              <StatsCard title="Completed" value={stats.completed} color="green" icon={CheckCircle} />
              <StatsCard title="In Progress" value={stats.inProgress} color="purple" icon={Clock} />
              <StatsCard title="Pending" value={stats.pending} color="gray" />
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
                    <option value="all">All Statuses</option>
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
                </div>

                <div className="text-sm text-gray-600">
                  Showing <span className="font-semibold">{filteredOperations.length}</span> operations
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {filteredOperations.map((operation) => (
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
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full font-medium">
                          Seq {operation.sequence}
                        </span>
                      </div>

                      <div className="text-sm text-gray-800 font-medium mb-2">{operation.operationName}</div>

                      <div className="flex items-center gap-6 text-sm text-gray-600 flex-wrap">
                        <span>PO: {operation.productionOrderNumber}</span>
                        <span>WO: {operation.workOrderNumber}</span>
                        <span>Qty: {operation.completedQty}/{operation.quantity}</span>
                        <span>Progress: {operation.progress}%</span>
                        <span>Planned Start: {formatDateTime(operation.plannedStart)}</span>
                        <span>Planned End: {formatDateTime(operation.plannedEnd)}</span>
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
            </div>

            {filteredOperations.length === 0 && (
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

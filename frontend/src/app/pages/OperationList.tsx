// Work Order Execution Status List
// Shows high-level WO execution status, not individual operations detail

import { useState, useMemo, useEffect } from "react";
import { useLocation, useParams, useNavigate } from "react-router";
import { Search, CheckCircle, Clock, AlertCircle, ChevronRight, AlertTriangle, Info } from "lucide-react";
import { PageHeader } from "@/app/components";
import { StatusBadge } from "@/app/components";
import { StatsCard } from "@/app/components";
import { toast } from "sonner";
import {
  productionOrderApi,
  type ProductionOrderDetailFromAPI,
  type ProductionOrderSummaryFromAPI,
  type WorkOrderSummaryFromAPI,
} from "@/app/api";

// Work Order Execution (aggregate status)
interface WorkOrderExecution {
  id: string | number;
  workOrderId: string;
  productionOrderId: string | number;
  productName: string;
  productionLine: string;
  status: 'Pending' | 'In Progress' | 'Completed' | 'Completed Late' | 'Late' | 'Blocked' | 'Aborted';
  overallProgress: number; // 0-100
  operationsCount: number;
  completedOperations: number;
  currentOperation?: string;
  plannedStart: string;
  plannedEnd: string;
  actualStart?: string;
  estimatedCompletion?: string;
  delayMinutes?: number;
}

// Backend response structures
// Helper to format datetime strings for display
const formatDateTime = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: '2-digit',
      day: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateStr;
  }
};

// Normalize backend work order to frontend interface
const normalizeWorkOrder = (
  backendWO: WorkOrderSummaryFromAPI,
  productionOrderId: number | string,
  productName: string
): WorkOrderExecution => {
  // Compute status from backend status
  const normalizedStatus = mapBackendStatus(backendWO.status);

  // Compute delay if actual_end exists and is after planned_end
  let delayMinutes: number | undefined;
  if (backendWO.actualEnd && backendWO.plannedEnd) {
    const plannedTime = new Date(backendWO.plannedEnd).getTime();
    const actualTime = new Date(backendWO.actualEnd).getTime();
    if (actualTime > plannedTime) {
      delayMinutes = Math.round((actualTime - plannedTime) / (1000 * 60));
    }
  }

  return {
    id: backendWO.id,
    workOrderId: backendWO.workOrderNumber,
    productionOrderId,
    productName,
    productionLine: '-', // Not available in Phase 1 backend data
    status: normalizedStatus,
    overallProgress: backendWO.overallProgress,
    operationsCount: backendWO.operationsCount,
    completedOperations: backendWO.completedOperations,
    currentOperation: undefined, // TODO: derive from execution events
    plannedStart: formatDateTime(backendWO.plannedStart),
    plannedEnd: formatDateTime(backendWO.plannedEnd),
    actualStart: formatDateTime(backendWO.actualStart),
    estimatedCompletion: formatDateTime(backendWO.actualEnd),
    delayMinutes,
  };
};

// Map backend status strings to UI statuses
const mapBackendStatus = (status: string): WorkOrderExecution['status'] => {
  const statusMap: Record<string, WorkOrderExecution['status']> = {
    'PLANNED': 'Pending',
    'PENDING': 'Pending',
    'IN_PROGRESS': 'In Progress',
    'COMPLETED': 'Completed',
    'COMPLETED_LATE': 'Completed Late',
    'LATE': 'Late',
    'BLOCKED': 'Blocked',
    'ABORTED': 'Aborted',
  };
  return statusMap[status] ?? 'Pending';
};

export function OperationList() {
  const { orderId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [workOrders, setWorkOrders] = useState<WorkOrderExecution[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const hasProductionOrderFilter = Boolean(orderId);

  const loadProductionOrder = async (productionOrderId: string | number): Promise<ProductionOrderDetailFromAPI> => {
    return productionOrderApi.get(productionOrderId);
  };

  useEffect(() => {
    const fetchWorkOrders = async () => {
      setLoading(true);
      setError(null);

      try {
        if (hasProductionOrderFilter && orderId) {
          const data = await loadProductionOrder(orderId);
          const normalized = data.workOrders.map((wo) =>
            normalizeWorkOrder(wo, data.id, data.productName)
          );
          setWorkOrders(normalized);
          return;
        }

        const productionOrders: ProductionOrderSummaryFromAPI[] = await productionOrderApi.list();
        const orderDetails = await Promise.all(
          productionOrders.map((productionOrder) => loadProductionOrder(productionOrder.id))
        );

        const normalized = orderDetails.flatMap((productionOrder) =>
          productionOrder.workOrders.map((wo) =>
            normalizeWorkOrder(wo, productionOrder.id, productionOrder.productName)
          )
        );
        setWorkOrders(normalized);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unable to load work orders';
        setError(message);
        toast.error(message);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkOrders();
  }, [hasProductionOrderFilter, orderId]);

  const filteredWorkOrders = useMemo(() => {
    let filtered = workOrders;

    if (filterStatus !== 'all') {
      filtered = filtered.filter(wo => wo.status === filterStatus);
    }

    if (searchValue) {
      filtered = filtered.filter(wo =>
        wo.workOrderId.toLowerCase().includes(searchValue.toLowerCase()) ||
        wo.productName.toLowerCase().includes(searchValue.toLowerCase()) ||
        wo.productionLine.toLowerCase().includes(searchValue.toLowerCase())
      );
    }

    return filtered;
  }, [workOrders, filterStatus, searchValue]);

  const stats = useMemo(() => ({
    total: workOrders.length,
    completed: workOrders.filter(wo => wo.status === 'Completed' || wo.status === 'Completed Late').length,
    inProgress: workOrders.filter(wo => wo.status === 'In Progress').length,
    pending: workOrders.filter(wo => wo.status === 'Pending').length,
    late: workOrders.filter(wo => wo.status === 'Late').length,
    overallProgress: workOrders.length > 0 ? Math.round(
      workOrders.reduce((sum, wo) => sum + wo.overallProgress, 0) / workOrders.length
    ) : 0,
  }), [workOrders]);

  const getStatusVariant = (status: string): "success" | "warning" | "error" | "info" | "neutral" => {
    switch (status) {
      case 'Completed': return 'success';
      case 'Completed Late': return 'warning';
      case 'In Progress': return 'info';
      case 'Pending': return 'neutral';
      case 'Late': return 'error';
      case 'Blocked': return 'error';
      case 'Aborted': return 'error';
      default: return 'neutral';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Completed': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'Completed Late': return <AlertCircle className="w-5 h-5 text-amber-600" />;
      case 'In Progress': return <Clock className="w-5 h-5 text-blue-600 animate-spin" style={{ animationDuration: '4s' }} />;
      case 'Late': return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'Aborted': return <AlertTriangle className="w-5 h-5 text-red-700" />;
      case 'Pending': return <Clock className="w-5 h-5 text-gray-400" />;
      default: return null;
    }
  };

  const subtitle = hasProductionOrderFilter
    ? `Filtered by Production Order: ${orderId || "-"}`
    : "All Work Orders";

  const contextNote = hasProductionOrderFilter
    ? "This screen shows execution status of Work Orders, filtered by a Production Order. Execution flow starts at Work Order level."
    : "This screen shows execution status of all Work Orders. Execution flow starts at Work Order level.";

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <PageHeader
        title="Execution – Work Orders"
        subtitle={subtitle}
        breadcrumb={
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span>Execution</span>
            <span>{">"}</span>
            <span className="font-medium text-gray-700">Work Orders</span>
          </div>
        }
        showBackButton={hasProductionOrderFilter}
        onBackClick={hasProductionOrderFilter ? () => navigate("/production-orders") : undefined}
      >
        <div className="flex items-center gap-4 ml-auto">
          {error ? (
            <div className="text-red-600 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm">Error loading data</span>
            </div>
          ) : (
            <div>
              <span className="text-sm text-gray-500">Context: </span>
              <span className="font-medium">{hasProductionOrderFilter ? `Production Order ${orderId}` : "All Work Orders"}</span>
            </div>
          )}
        </div>
      </PageHeader>

      <div className="px-6 py-3 border-b border-gray-100 bg-slate-50">
        <div className="flex items-start gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
          <Info className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
          <p>{contextNote}</p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 mx-auto mb-3 text-blue-500 animate-spin" style={{ animationDuration: '2s' }} />
            <div className="text-lg font-medium text-gray-600">Loading work orders...</div>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <div className="flex gap-3">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900">Failed to load work orders</h3>
                <p className="text-red-700 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        {!loading && !error && (
          <>
            <div className="grid grid-cols-6 gap-4 mb-6">
              <StatsCard
                title="Total WOs"
                value={stats.total}
                color="blue"
              />
              <StatsCard
                title="Completed"
                value={stats.completed}
                color="green"
                icon={CheckCircle}
              />
              <StatsCard
                title="In Progress"
                value={stats.inProgress}
                color="purple"
              />
              <StatsCard
                title="Pending"
                value={stats.pending}
                color="gray"
              />
              <StatsCard
                title="Late"
                value={stats.late}
                color="red"
                icon={AlertCircle}
              />
              <StatsCard
                title="Overall Progress"
                value={`${stats.overallProgress}%`}
                color="orange"
              />
            </div>

            {/* Filters */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <h2 className="text-xl font-bold">Work Orders</h2>

                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                >
                  <option value="all">All Status</option>
                  <option value="Pending">Pending</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Late">Late</option>
                  <option value="Completed">Completed</option>
                  <option value="Completed Late">Completed Late</option>
                  <option value="Blocked">Blocked</option>
                  <option value="Aborted">Aborted</option>
                </select>

                <div className="text-sm text-gray-600">
                  Showing: <strong>{filteredWorkOrders.length}</strong> work orders
                </div>
              </div>

              <div className="relative w-80">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search work orders..."
                  value={searchValue}
                  onChange={(e) => setSearchValue(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                />
              </div>
            </div>

            {/* Work Orders List */}
            <div className="space-y-3">
              {filteredWorkOrders.map((wo) => (
                <div
                  key={wo.id}
                  className="border rounded-lg p-5 hover:shadow-md transition-all bg-white cursor-pointer group"
                  onClick={() => navigate(`/work-orders/${wo.id}/operations`)}
                >
                  <div className="flex items-center gap-4">
                    {/* Status Icon */}
                    <div className="flex-shrink-0">
                      {getStatusIcon(wo.status)}
                    </div>

                    {/* WO Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-bold text-lg font-mono">{wo.workOrderId}</span>
                        <StatusBadge variant={getStatusVariant(wo.status)}>
                          {wo.status}
                        </StatusBadge>
                        {wo.delayMinutes && wo.delayMinutes > 0 && (
                          <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full font-medium">
                            ⚠ +{wo.delayMinutes}min delay
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-6 text-sm text-gray-600">
                        <span>{wo.productName}</span>
                        <span>•</span>
                        <span>{wo.productionLine}</span>
                        <span>•</span>
                        <span>
                          Operations: {wo.completedOperations}/{wo.operationsCount}
                        </span>
                        {wo.currentOperation && (
                          <>
                            <span>•</span>
                            <span className="font-medium text-blue-600">Current: {wo.currentOperation}</span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Progress */}
                    <div className="flex-shrink-0 w-48">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-500">Progress</span>
                        <span className="text-sm font-bold">{wo.overallProgress}%</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all ${
                            wo.status === 'Completed' || wo.status === 'Completed Late' ? 'bg-green-500' :
                            wo.status === 'Late' ? 'bg-red-500' :
                            wo.status === 'In Progress' ? 'bg-blue-500' :
                            'bg-gray-400'
                          }`}
                          style={{ width: `${wo.overallProgress}%` }}
                        />
                      </div>
                    </div>

                    {/* CTA */}
                    <button
                      className="flex-shrink-0 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 group-hover:border-blue-500 group-hover:text-blue-600 transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/work-orders/${wo.id}/operations`);
                      }}
                    >
                      <span className="font-medium">View</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {filteredWorkOrders.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <div className="text-lg font-medium mb-1">No work orders found</div>
                <div className="text-sm">Try adjusting your filters or search criteria</div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );

}
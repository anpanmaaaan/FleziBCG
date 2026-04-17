// Operation Execution Overview - Gantt Chart ONLY
// Click bar to navigate to detailed view

import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams, Link } from "react-router";
import { 
  ArrowLeft,
  ExternalLink,
  Activity,
  CheckCircle,
  TrendingUp,
  Clock,
  AlertTriangle,
} from "lucide-react";
import { PageHeader } from "@/app/components";
import { StatsCard } from "@/app/components";
import { GanttChart, OperationExecutionGantt, type GanttClickContext } from "@/app/components";
import { request } from "@/app/api";
import type { OperationExecutionStatus } from "@/app/api";
import {
  mapExecutionStatusText,
  getProgressPercentage as calcProgressPercent,
} from "@/app/api";

type OverviewOperation = OperationExecutionGantt & {
  operationId: number;
  operationNumber: string;
  backendStatus?: OperationExecutionStatus;
};

type ExecutionTimelineOperation = {
  operationId: number;
  operationNumber: string;
  sequence: number;
  name: string;
  workstation: string;
  status: OperationExecutionStatus;
  plannedStart: string | null;
  plannedEnd: string | null;
  actualStart: string | null;
  actualEnd: string | null;
  delayMinutes: number | null;
  timingStatus: "EARLY" | "ON_TIME" | "LATE";
  qcRequired: boolean;
};

type ExecutionTimelineResponse = {
  workOrderId: number;
  workOrderNumber: string;
  productionOrderId: number;
  productionOrderNumber: string;
  operations: ExecutionTimelineOperation[];
  derivedAt?: string;
};

const workOrderApi = {
  getExecutionTimeline(workOrderId: string) {
    return request<ExecutionTimelineResponse>(`/v1/work-orders/${encodeURIComponent(workOrderId)}/execution-timeline`);
  },
};

const mapTimelineStatusToGanttStatus = (
  status: OperationExecutionStatus,
): OperationExecutionGantt["status"] => {
  const statusText = mapExecutionStatusText(status);

  if (statusText === "Completed") {
    return "Completed";
  }
  if (statusText === "In Progress") {
    return "Running";
  }
  return "Not Started";
};

const toOverviewOperation = (operation: ExecutionTimelineOperation): OverviewOperation => {
  const plannedStart = operation.plannedStart || operation.actualStart || new Date().toISOString();
  const plannedEnd = operation.plannedEnd || operation.actualEnd || plannedStart;

  return {
    id: String(operation.operationId),
    operationId: operation.operationId,
    operationNumber: operation.operationNumber,
    sequence: operation.sequence,
    name: operation.name,
    workstation: operation.workstation || "N/A",
    backendStatus: operation.status,
    status: mapTimelineStatusToGanttStatus(operation.status),
    plannedStart,
    plannedEnd,
    actualStart: operation.actualStart || undefined,
    actualEnd: operation.actualEnd || undefined,
    currentTime: operation.status === "IN_PROGRESS" ? new Date().toISOString() : undefined,
    delayMinutes: operation.delayMinutes || undefined,
    qcRequired: operation.qcRequired,
  };
};

export function OperationExecutionOverview() {
  const { woId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Restore Gantt context from back-navigation params.
  const restoredMode = searchParams.get('mode') as 'shift' | 'day' | 'week' | 'fit_all' | 'fit_selection' | null;
  const restoredGroupBy = searchParams.get('groupBy') as 'none' | 'workstation' | 'area' | null;
  const restoredSelectedId = searchParams.get('sel') ?? undefined;

  const [selectedOperationId, setSelectedOperationId] = useState<string | undefined>(restoredSelectedId);
  const [operations, setOperations] = useState<OverviewOperation[]>([]);
  const [productionOrderId, setProductionOrderId] = useState<number | null>(null);
  const [productionOrderNumber, setProductionOrderNumber] = useState<string | null>(null);
  const [workOrderNumber, setWorkOrderNumber] = useState<string | null>(null);
  const [derivedAt, setDerivedAt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [breakdownVisibleCount, setBreakdownVisibleCount] = useState(80);

  useEffect(() => {
    setBreakdownVisibleCount(80);
  }, [woId]);

  useEffect(() => {
    let cancelled = false;

    const loadTimeline = async () => {
      if (!woId) {
        setError("Work order ID is missing in URL.");
        setOperations([]);
        setProductionOrderId(null);
        setProductionOrderNumber(null);
        setWorkOrderNumber(null);
        setDerivedAt(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const timeline = await workOrderApi.getExecutionTimeline(woId);

        if (cancelled) {
          return;
        }

        const mapped = timeline.operations.map(toOverviewOperation);
        setOperations(mapped);
        setProductionOrderId(timeline.productionOrderId);
        setProductionOrderNumber(timeline.productionOrderNumber);
        setWorkOrderNumber(timeline.workOrderNumber);
        setDerivedAt(timeline.derivedAt || null);
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : "Failed to load execution timeline.";
          setError(message);
          setOperations([]);
          setProductionOrderId(null);
          setProductionOrderNumber(null);
          setWorkOrderNumber(null);
          setDerivedAt(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadTimeline();

    return () => {
      cancelled = true;
    };
  }, [woId]);

  // Read-only visual summary from backend-derived timeline statuses.
  const stats = useMemo(() => {
    const completedOperations = operations.filter((op) => op.status === "Completed").length;
    const inProgressOperations = operations.filter((op) => op.status === "Running").length;
    const totalOperations = operations.length;

    return {
      totalOperations,
      completedOperations,
      inProgressOperations,
      overallProgress: calcProgressPercent({
        completedQty: completedOperations,
        targetQty: totalOperations,
      }),
    };
  }, [operations]);

  const breakdownItems = useMemo(
    () => operations.slice(0, breakdownVisibleCount),
    [operations, breakdownVisibleCount],
  );
  const hasMoreBreakdownItems = breakdownVisibleCount < operations.length;
  const hiddenBreakdownItemCount = Math.max(operations.length - breakdownVisibleCount, 0);

  const handleOperationClick = useCallback((operation: OperationExecutionGantt, context: GanttClickContext) => {
    const overviewOperation = operation as OverviewOperation;
    const canonicalOperationId = String(overviewOperation.operationId);
    setSelectedOperationId(canonicalOperationId);

    const params = new URLSearchParams({
      from: 'gantt',
      woId: String(woId ?? ''),
      mode: context.mode,
      groupBy: context.groupBy,
      sel: canonicalOperationId,
    });
    navigate(`/operations/${canonicalOperationId}/detail?${params.toString()}`);
  }, [navigate, woId]);

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <PageHeader
        title={
          <div className="flex items-center gap-4">
            <button 
              onClick={() => {
                if (productionOrderId !== null) {
                  navigate(`/production-orders/${productionOrderId}/work-orders`);
                }
              }}
              disabled={productionOrderId === null}
              className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            <div>
              <div className="text-sm text-gray-500">Work Order: {workOrderNumber || woId || "-"}</div>
              <div className="text-2xl font-bold">Operation Execution Overview</div>
            </div>
          </div>
        }
        showBackButton={false}
        actions={
          <>
            <Link 
              to="/station-execution"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" />
              Open in Station Execution
            </Link>
          </>
        }
      />

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {error && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-medium text-amber-800">Timeline unavailable</div>
              <div className="text-sm text-amber-700 mt-1">{error}</div>
            </div>
          </div>
        )}

        {derivedAt && (
          <div className="text-xs text-gray-500 mb-4">Timeline derived at {derivedAt}</div>
        )}

        {/* WO-level Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatsCard
            title="Total Operations"
            value={stats.totalOperations}
            color="blue"
            icon={Activity}
          />
          <StatsCard
            title="Completed"
            value={stats.completedOperations}
            color="green"
            icon={CheckCircle}
          />
          <StatsCard
            title="In Progress"
            value={stats.inProgressOperations}
            color="purple"
          />
          <StatsCard
            title="Overall Progress"
            value={`${stats.overallProgress}%`}
            color="orange"
            icon={TrendingUp}
          />
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <Clock className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-medium text-blue-800">Time-Based Gantt Chart</div>
            <div className="text-sm text-blue-600 mt-1">
              Click any operation bar to view detailed information. Gaps and delays are visible through bar positioning.
              {loading ? " Loading backend timeline..." : ""}
            </div>
          </div>
        </div>

        {/* Gantt Chart */}
        <GanttChart 
          operations={operations}
          onOperationClick={handleOperationClick}
          selectedOperationId={selectedOperationId}
          initialMode={restoredMode ?? undefined}
          groupBy={restoredGroupBy ?? undefined}
        />

        {/* Additional Info */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-bold mb-3 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Operations Breakdown
            </h3>
            <div className="space-y-2 text-sm">
              {breakdownItems.map((op) => (
                <div 
                  key={op.id} 
                  className="flex items-center justify-between p-2 rounded hover:bg-gray-50 cursor-pointer"
                  onClick={() => navigate(`/operations/${String(op.operationId)}/detail`)}
                >
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-gray-500">{op.sequence}</span>
                    <span>{op.operationNumber}</span>
                    <span>{op.name}</span>
                  </div>
                  <div className={`text-xs px-2 py-1 rounded ${
                    op.status === 'Completed' ? 'bg-green-100 text-green-700' :
                    op.status === 'Running' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {mapExecutionStatusText(op.backendStatus || "PENDING")}
                  </div>
                </div>
              ))}
              {hasMoreBreakdownItems && (
                <div className="pt-2">
                  <button
                    onClick={() => setBreakdownVisibleCount((prev) => prev + 120)}
                    className="w-full py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Load more operations ({hiddenBreakdownItemCount} remaining)
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-bold mb-3">Work Order Information</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Work Order ID:</span>
                <span className="font-medium font-mono">{workOrderNumber || woId || "-"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Production Order:</span>
                <span className="font-medium font-mono">{productionOrderNumber || "-"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Product:</span>
                <span className="font-medium">Engine Block Type A</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Production Line:</span>
                <span className="font-medium">Line A</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Quantity:</span>
                <span className="font-medium">50 pcs</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Route:</span>
                <span className="font-medium">DMES-R8</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

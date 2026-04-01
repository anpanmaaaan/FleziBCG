import { useState, useEffect } from "react";
import { useSearchParams } from "react-router";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { StatsCard } from "../components/StatsCard";
import { toast } from "sonner";
import { Play, ClipboardList, CheckCircle, AlertTriangle } from "lucide-react";

interface OperationDetail {
  id: number;
  operation_number: string;
  name: string;
  sequence: number;
  status: "PENDING" | "IN_PROGRESS" | "COMPLETED" | string;
  planned_start: string | null;
  planned_end: string | null;
  actual_start: string | null;
  actual_end: string | null;
  quantity: number;
  completed_qty: number;
  good_qty: number;
  scrap_qty: number;
  progress: number;
  work_order_id: number;
  work_order_number: string;
  production_order_id: number;
  production_order_number: string;
  qc_required: boolean;
}

const statusLabel = (status: string) => {
  switch (status) {
    case "PENDING":
      return "Pending";
    case "IN_PROGRESS":
      return "In Progress";
    case "COMPLETED":
      return "Completed";
    default:
      return status;
  }
};

const statusVariant = (status: string): "success" | "warning" | "error" | "info" | "neutral" => {
  switch (status) {
    case "COMPLETED":
      return "success";
    case "IN_PROGRESS":
      return "info";
    case "PENDING":
      return "neutral";
    default:
      return "warning";
  }
};

export function StationExecution() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryOperationId = searchParams.get("operationId") || "";

  const [operationId, setOperationId] = useState<string>(queryOperationId);
  const [operation, setOperation] = useState<OperationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [goodQty, setGoodQty] = useState<number>(0);
  const [scrapQty, setScrapQty] = useState<number>(0);

  useEffect(() => {
    if (queryOperationId) {
      setOperationId(queryOperationId);
      fetchOperation(queryOperationId);
    }
  }, [queryOperationId]);

  const fetchOperation = async (id: string) => {
    if (!id) {
      toast.error("Please enter an operation ID.");
      return;
    }

    setLoading(true);
    setOperation(null);

    try {
      const response = await fetch(`/api/v1/operations/${id}`);
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail || `Failed to load operation (${response.status})`);
      }
      const data: OperationDetail = await response.json();
      setOperation(data);
      setGoodQty(data.good_qty || 0);
      setScrapQty(data.scrap_qty || 0);
      setSearchParams({ operationId: id });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load operation.";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const performAction = async (apiPath: string, method: string, payload?: any) => {
    if (!operation) return;
    setActionLoading(true);

    try {
      const response = await fetch(`/api/v1/operations/${operation.id}/${apiPath}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: payload ? JSON.stringify(payload) : undefined,
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail || `Action failed (${response.status})`);
      }
      const data: OperationDetail = await response.json();
      setOperation(data);
      toast.success(`Operation updated to ${statusLabel(data.status)}.`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Action failed.";
      toast.error(message);
    } finally {
      setActionLoading(false);
      await fetchOperation(operationId);
    }
  };

  const startOperation = async () => {
    if (!operation) return;
    await performAction("start", "POST", { operator_id: null });
  };

  const reportQuantity = async () => {
    if (!operation) return;
    await performAction("report-quantity", "POST", {
      good_qty: goodQty,
      scrap_qty: scrapQty,
      operator_id: null,
    });
  };

  const completeOperation = async () => {
    if (!operation) return;
    const confirmed = window.confirm("Confirm complete operation?");
    if (!confirmed) return;
    await performAction("complete", "POST", { operator_id: null });
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title="Station Execution"
        showBackButton={false}
        actions={
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={operationId}
              onChange={(e) => setOperationId(e.target.value)}
              placeholder="Enter operation id"
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <button
              onClick={() => fetchOperation(operationId)}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Load
            </button>
          </div>
        }
      />

      <div className="p-6 flex-1 overflow-auto">
        {!operation ? (
          <div className="text-center py-20 text-gray-500">
            {loading ? "Loading operation..." : "Enter an operation ID and click Load."}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-lg border">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-lg font-semibold">Operation</h2>
                  <StatusBadge variant={statusVariant(operation.status)}>
                    {statusLabel(operation.status)}
                  </StatusBadge>
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
                  <div>
                    <p className="font-medium">{operation.operation_number}</p>
                    <p>{operation.name}</p>
                  </div>
                  <div>
                    <p className="font-medium">WO</p>
                    <p>{operation.work_order_number}</p>
                  </div>
                  <div>
                    <p className="font-medium">PO</p>
                    <p>{operation.production_order_number}</p>
                  </div>
                  <div>
                    <p className="font-medium">Qty</p>
                    <p>{operation.quantity}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg border grid grid-cols-3 gap-4">
                <StatsCard title="Completed" value={operation.completed_qty} color="blue" />
                <StatsCard title="Good" value={operation.good_qty} color="green" />
                <StatsCard title="Scrap" value={operation.scrap_qty} color="red" />
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg border grid md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Planned Start</p>
                <p>{operation.planned_start ?? "-"}</p>
              </div>
              <div>
                <p className="text-gray-500">Planned End</p>
                <p>{operation.planned_end ?? "-"}</p>
              </div>
              <div>
                <p className="text-gray-500">Actual Start</p>
                <p>{operation.actual_start ?? "-"}</p>
              </div>
              <div>
                <p className="text-gray-500">Actual End</p>
                <p>{operation.actual_end ?? "-"}</p>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg border space-y-4">
              {operation.status === "PENDING" && (
                <button
                  onClick={startOperation}
                  disabled={actionLoading}
                  className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Play className="inline w-4 h-4 mr-2" /> Start Operation
                </button>
              )}

              {operation.status === "IN_PROGRESS" && (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Good quantity</label>
                      <input
                        type="number"
                        min={0}
                        value={goodQty}
                        onChange={(e) => setGoodQty(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Scrap quantity</label>
                      <input
                        type="number"
                        min={0}
                        value={scrapQty}
                        onChange={(e) => setScrapQty(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={reportQuantity}
                      disabled={actionLoading}
                      className="flex-1 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      <ClipboardList className="inline w-4 h-4 mr-2" /> Report Quantity
                    </button>
                    <button
                      onClick={completeOperation}
                      disabled={actionLoading}
                      className="flex-1 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                    >
                      <CheckCircle className="inline w-4 h-4 mr-2" /> Complete Operation
                    </button>
                  </div>
                </>
              )}

              {operation.status === "COMPLETED" && (
                <div className="p-4 rounded-lg border border-green-200 bg-green-50 text-green-800">
                  <p className="font-semibold">Operation completed.</p>
                  <p>All write controls are disabled in completed state.</p>
                </div>
              )}

              <div className="flex items-center gap-2 text-sm text-gray-600">
                <AlertTriangle className="w-4 h-4 text-orange-500" />
                <span>Backend validates rules; frontend is UI-only.</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

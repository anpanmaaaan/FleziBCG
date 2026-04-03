import { useState, useEffect } from "react";
import { useSearchParams } from "react-router";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { StatsCard } from "../components/StatsCard";
import { toast } from "sonner";
import { Play, ClipboardList, CheckCircle, AlertTriangle } from "lucide-react";
import { operationApi, type OperationDetail } from "../api/operationApi";
import {
  mapExecutionStatusBadgeVariant,
  mapExecutionStatusText,
} from "../api/mappers/executionMapper";

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

  const isCanonicalOperationId = (value: string) => /^\d+$/.test(value.trim());

  const fetchOperation = async (id: string) => {
    const trimmedId = id.trim();

    if (!trimmedId) {
      toast.error("Please enter an operation ID.");
      return;
    }

    if (!isCanonicalOperationId(trimmedId)) {
      toast.error("Operation ID must be a numeric operation_id.");
      return;
    }

    setLoading(true);
    setOperation(null);

    try {
      const data = await operationApi.get(trimmedId);
      setOperation(data);
      setGoodQty(data.good_qty || 0);
      setScrapQty(data.scrap_qty || 0);
      setSearchParams({ operationId: trimmedId });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load operation.";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const startOperation = async () => {
    if (!operation) return;
    setActionLoading(true);

    try {
      const data = await operationApi.start(operation.id);
      toast.success("Operation updated to " + mapExecutionStatusText(data.status) + ".");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Action failed.";
      toast.error(message);
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
    }
  };

  const reportQuantity = async () => {
    if (!operation) return;
    setActionLoading(true);

    try {
      const data = await operationApi.reportQuantity(operation.id, {
        good_qty: goodQty,
        scrap_qty: scrapQty,
        operator_id: null,
      });
      toast.success("Operation updated to " + mapExecutionStatusText(data.status) + ".");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Action failed.";
      toast.error(message);
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
    }
  };

  const completeOperation = async () => {
    if (!operation) return;
    const confirmed = window.confirm("Confirm complete operation?");
    if (!confirmed) return;
    setActionLoading(true);

    try {
      const data = await operationApi.complete(operation.id);
      toast.success("Operation updated to " + mapExecutionStatusText(data.status) + ".");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Action failed.";
      toast.error(message);
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
    }
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
              inputMode="numeric"
              pattern="[0-9]*"
              value={operationId}
              onChange={(e) => setOperationId(e.target.value)}
              placeholder="Enter numeric operation_id"
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
                  <StatusBadge variant={mapExecutionStatusBadgeVariant(operation.status)}>
                    {mapExecutionStatusText(operation.status)}
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

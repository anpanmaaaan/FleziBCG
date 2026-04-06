import { useState, useEffect } from "react";
import { useSearchParams } from "react-router";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { StatsCard } from "../components/StatsCard";
import { toast } from "sonner";
import { Play, ClipboardList, CheckCircle, AlertTriangle, RefreshCw, Lock } from "lucide-react";
import { operationApi, type OperationDetail } from "../api/operationApi";
import { stationApi, type StationQueueItem } from "../api/stationApi";
import { HttpError } from "../api/httpClient";
import { useAuth } from "../auth/AuthContext";
import {
  mapExecutionStatusBadgeVariant,
  mapExecutionStatusText,
} from "../api/mappers/executionMapper";

export function StationExecution() {
  const { currentUser } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryOperationId = searchParams.get("operationId") || "";

  const [operationId, setOperationId] = useState<string>(queryOperationId);
  const [operation, setOperation] = useState<OperationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [queueLoading, setQueueLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [claimLoading, setClaimLoading] = useState(false);
  const [goodQty, setGoodQty] = useState<number>(0);
  const [scrapQty, setScrapQty] = useState<number>(0);
  const [stationScope, setStationScope] = useState<string>("-");
  const [queueItems, setQueueItems] = useState<StationQueueItem[]>([]);

  useEffect(() => {
    void refreshQueue();
  }, []);

  useEffect(() => {
    if (queryOperationId) {
      setOperationId(queryOperationId);
      void fetchOperation(queryOperationId);
    }
  }, [queryOperationId]);

  const isCanonicalOperationId = (value: string) => /^\d+$/.test(value.trim());

  const selectedQueueItem = operation
    ? queueItems.find((item) => item.operation_id === operation.id) ?? null
    : null;
  const claimState = selectedQueueItem?.claim.state ?? "none";
  const canExecuteByClaim = claimState === "mine";
  const canClockOnByStatus = operation?.status === "PENDING" || operation?.status === "PLANNED";

  const refreshQueue = async () => {
    setQueueLoading(true);
    try {
      const data = await stationApi.getQueue();
      setStationScope(data.station_scope_value || "-");
      setQueueItems(data.items);

      if (data.items.length === 0) {
        setOperation(null);
        return;
      }

      if (operation && data.items.some((item) => item.operation_id === operation.id)) {
        return;
      }

      const preferred = queryOperationId && /^\d+$/.test(queryOperationId)
        ? data.items.find((item) => item.operation_id === Number(queryOperationId))
        : null;
      const next = preferred ?? data.items[0];
      setOperationId(String(next.operation_id));
      setSearchParams({ operationId: String(next.operation_id) });
      await fetchOperation(String(next.operation_id));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load station queue.";
      toast.error(message);
    } finally {
      setQueueLoading(false);
    }
  };

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
      const data = await stationApi.getOperationDetail(Number(trimmedId));
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

  const selectQueueOperation = async (item: StationQueueItem) => {
    setOperationId(String(item.operation_id));
    setSearchParams({ operationId: String(item.operation_id) });
    await fetchOperation(String(item.operation_id));
  };

  const claimOperation = async () => {
    if (!operation) return;
    setClaimLoading(true);
    try {
      await stationApi.claim(operation.id, {});
      toast.success("Operation claimed.");
      await refreshQueue();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to claim operation.";
      toast.error(message);
    } finally {
      setClaimLoading(false);
    }
  };

  const releaseClaim = async () => {
    if (!operation) return;
    setClaimLoading(true);
    try {
      await stationApi.release(operation.id, { reason: "operator_release" });
      toast.success("Claim released.");
      await refreshQueue();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to release claim.";
      toast.error(message);
    } finally {
      setClaimLoading(false);
    }
  };

  const startOperation = async () => {
    if (!operation) return;
    setActionLoading(true);

    try {
      const data = await operationApi.start(operation.id, {
        operator_id: currentUser?.user_id ?? null,
      });
      toast.success("Operation updated to " + mapExecutionStatusText(data.status) + ".");
    } catch (err) {
      if (err instanceof HttpError && err.status === 403) {
        toast.error("Claim required");
      } else if (err instanceof HttpError && err.status === 409) {
        toast.error("Already started");
      } else {
        const message = err instanceof Error ? err.message : "Action failed.";
        toast.error(message);
      }
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
      await refreshQueue();
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
      await refreshQueue();
    }
  };

  const completeOperation = async () => {
    if (!operation) return;
    const confirmed = window.confirm("Confirm clock off / complete operation?");
    if (!confirmed) return;
    setActionLoading(true);

    try {
      const data = await operationApi.complete(operation.id, {
        operator_id: currentUser?.user_id ?? null,
        completed_at: new Date().toISOString(),
      });
      toast.success("Operation updated to " + mapExecutionStatusText(data.status) + ".");
    } catch (err) {
      if (err instanceof HttpError && err.status === 403) {
        toast.error("Claim required");
      } else if (err instanceof HttpError && err.status === 409) {
        toast.error("Operation already completed");
      } else {
        const message = err instanceof Error ? err.message : "Action failed.";
        toast.error(message);
      }
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
      await refreshQueue();
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title="Station Execution"
        showBackButton={false}
        actions={
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">Scope: {stationScope}</span>
            <button
              onClick={() => void refreshQueue()}
              disabled={queueLoading}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className="inline w-4 h-4 mr-1" /> Refresh Queue
            </button>
          </div>
        }
      />

      <div className="p-6 flex-1 overflow-auto">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 h-full">
          <div className="xl:col-span-1 border rounded-lg p-4 bg-gray-50 overflow-auto">
            <h2 className="font-semibold text-gray-900 mb-3">Station Queue</h2>
            {queueLoading && <p className="text-sm text-gray-500">Loading queue...</p>}
            {!queueLoading && queueItems.length === 0 && (
              <p className="text-sm text-gray-500">No PENDING or IN_PROGRESS operations for this station.</p>
            )}
            <div className="space-y-2">
              {queueItems.map((item) => {
                const active = operation?.id === item.operation_id;
                const isLocked = item.claim.state === "other";
                return (
                  <button
                    key={item.operation_id}
                    type="button"
                    onClick={() => void selectQueueOperation(item)}
                    className={`w-full text-left p-3 rounded-lg border transition ${
                      active
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 bg-white hover:border-gray-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-sm text-gray-900">{item.operation_number}</p>
                      <StatusBadge variant={mapExecutionStatusBadgeVariant(item.status)}>
                        {mapExecutionStatusText(item.status)}
                      </StatusBadge>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{item.name}</p>
                    <p className="text-xs text-gray-500 mt-1">WO {item.work_order_number} · PO {item.production_order_number}</p>
                    {item.claim.state === "mine" && (
                      <p className="text-xs text-green-700 mt-2">Claimed by you</p>
                    )}
                    {isLocked && (
                      <p className="text-xs text-orange-700 mt-2"><Lock className="inline w-3 h-3 mr-1" />Claimed by other operator</p>
                    )}
                  </button>
                );
              })}
            </div>

            <details className="mt-4 border-t pt-3">
              <summary className="text-sm text-gray-600 cursor-pointer">Manual operation ID fallback</summary>
              <div className="mt-3 flex items-center gap-2">
                <input
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  value={operationId}
                  onChange={(e) => setOperationId(e.target.value)}
                  placeholder="Enter numeric operation_id"
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-full"
                />
                <button
                  onClick={() => void fetchOperation(operationId)}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  Load
                </button>
              </div>
            </details>
          </div>

          <div className="xl:col-span-2 space-y-6">
          {!operation ? (
            <div className="text-center py-20 text-gray-500 border rounded-lg bg-white">
              {loading ? "Loading operation..." : "Select an operation from station queue."}
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

            <div className="bg-white p-4 rounded-lg border">
              {claimState === "none" && (
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm text-gray-700">Claim required before execution actions.</p>
                  <button
                    onClick={claimOperation}
                    disabled={claimLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    Claim Operation
                  </button>
                </div>
              )}
              {claimState === "mine" && (
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm text-green-700 font-medium">Operation claimed by you.</p>
                  <button
                    onClick={releaseClaim}
                    disabled={claimLoading}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Release Claim
                  </button>
                </div>
              )}
              {claimState === "other" && (
                <div className="text-sm text-orange-700 font-medium">
                  Claimed by another operator. Execution actions are disabled.
                </div>
              )}
            </div>

            <div className="bg-white p-4 rounded-lg border space-y-4">
              {canClockOnByStatus && (
                <button
                  onClick={startOperation}
                  disabled={actionLoading || !canExecuteByClaim}
                  title={!canExecuteByClaim ? "Claim required" : undefined}
                  className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Play className="inline w-4 h-4 mr-2" /> Clock On
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
                      disabled={actionLoading || !canExecuteByClaim}
                      className="flex-1 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      <ClipboardList className="inline w-4 h-4 mr-2" /> Report Quantity
                    </button>
                    <button
                      onClick={completeOperation}
                      disabled={actionLoading || !canExecuteByClaim}
                      title={!canExecuteByClaim ? "Claim required" : undefined}
                      className="flex-1 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                    >
                      <CheckCircle className="inline w-4 h-4 mr-2" /> Clock Off
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
                <span>Backend validates claim + execution rules; frontend is UI-only.</span>
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

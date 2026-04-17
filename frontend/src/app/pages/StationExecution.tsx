import { useState, useEffect } from "react";
import { useSearchParams } from "react-router";
import { PageHeader } from "@/app/components";
import { StatusBadge } from "@/app/components";
import { toast } from "sonner";
import { RefreshCw, Lock, X, ChevronDown } from "lucide-react";
import { operationApi, type OperationDetail } from "@/app/api";
import { stationApi, type StationQueueItem } from "@/app/api";
import { HttpError } from "@/app/api";
import { useAuth } from "@/app/auth";
import {
  mapExecutionStatusBadgeVariant,
  mapExecutionStatusText,
} from "@/app/api";

// ── Numeric Keypad Overlay ────────────────────────────────────────────────────

interface KeypadProps {
  label: string;
  value: number;
  onConfirm: (v: number) => void;
  onClose: () => void;
}

function NumericKeypad({ label, value, onConfirm, onClose }: KeypadProps) {
  const [draft, setDraft] = useState(String(value));

  const press = (key: string) => {
    if (key === "CLR") {
      setDraft("0");
    } else if (key === "OK") {
      onConfirm(Math.max(0, parseInt(draft, 10) || 0));
    } else {
      setDraft((prev) => {
        const next = prev === "0" ? key : prev + key;
        return next.length > 5 ? prev : next;
      });
    }
  };

  const rows = [
    ["7", "8", "9"],
    ["4", "5", "6"],
    ["1", "2", "3"],
    ["CLR", "0", "OK"],
  ];

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl p-6 w-72"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <span className="text-base font-semibold text-gray-700">{label}</span>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="text-4xl font-bold text-center text-gray-900 bg-gray-100 rounded-xl py-3 mb-5">
          {draft}
        </div>
        <div className="grid grid-cols-3 gap-3">
          {rows.flat().map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => press(key)}
              className={`h-14 rounded-xl text-lg font-semibold transition active:scale-95 ${
                key === "OK"
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : key === "CLR"
                  ? "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  : "bg-gray-100 text-gray-900 hover:bg-gray-200"
              }`}
            >
              {key}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Stepper Control ───────────────────────────────────────────────────────────

interface StepperProps {
  label: string;
  value: number;
  onChange: (v: number) => void;
}

function Stepper({ label, value, onChange }: StepperProps) {
  const [keypadOpen, setKeypadOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-medium text-gray-600">{label}</span>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onChange(Math.max(0, value - 1))}
          aria-label={`Decrease ${label}`}
          className="w-14 h-14 rounded-xl bg-gray-100 text-2xl font-bold text-gray-700 hover:bg-gray-200 active:scale-95 transition select-none"
        >
          −
        </button>
        <button
          type="button"
          onClick={() => setKeypadOpen(true)}
          className="flex-1 h-14 rounded-xl bg-white border-2 border-gray-300 text-2xl font-bold text-gray-900 hover:border-blue-400 transition"
        >
          {value}
        </button>
        <button
          type="button"
          onClick={() => onChange(value + 1)}
          aria-label={`Increase ${label}`}
          className="w-14 h-14 rounded-xl bg-gray-100 text-2xl font-bold text-gray-700 hover:bg-gray-200 active:scale-95 transition select-none"
        >
          +
        </button>
      </div>
      {keypadOpen && (
        <NumericKeypad
          label={label}
          value={value}
          onConfirm={(v) => {
            onChange(v);
            setKeypadOpen(false);
          }}
          onClose={() => setKeypadOpen(false)}
        />
      )}
    </div>
  );
}

// ── Queue List ────────────────────────────────────────────────────────────────

interface QueueListProps {
  items: StationQueueItem[];
  loading: boolean;
  activeOperationId?: number;
  onSelect: (item: StationQueueItem) => void;
}

function QueueList({ items, loading, activeOperationId, onSelect }: QueueListProps) {
  if (loading) {
    return <p className="text-sm text-gray-500 py-8 text-center">Loading...</p>;
  }
  if (items.length === 0) {
    return (
      <p className="text-sm text-gray-500 py-8 text-center">
        No operations in queue.
      </p>
    );
  }
  return (
    <div className="flex flex-col gap-2">
      {items.map((item) => {
        const active = activeOperationId === item.operation_id;
        const locked = item.claim.state === "other";
        return (
          <button
            key={item.operation_id}
            type="button"
            disabled={locked}
            onClick={() => onSelect(item)}
            className={`w-full text-left p-4 rounded-xl border-2 transition ${
              active
                ? "border-blue-500 bg-blue-50"
                : locked
                ? "border-gray-200 bg-gray-50 opacity-60 cursor-not-allowed"
                : "border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50 active:scale-[0.99]"
            }`}
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 min-w-0">
                {locked && <Lock className="w-4 h-4 text-orange-500 shrink-0" />}
                <p className="font-semibold text-base text-gray-900 truncate">
                  {item.name}
                </p>
              </div>
              <StatusBadge variant={mapExecutionStatusBadgeVariant(item.status)}>
                {mapExecutionStatusText(item.status)}
              </StatusBadge>
            </div>
            <p className="text-xs text-gray-500 mt-1">{item.operation_number}</p>
          </button>
        );
      })}
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

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
  const [queueOverlayOpen, setQueueOverlayOpen] = useState(false);

  // Initial queue load on mount
  useEffect(() => { void refreshQueue(); }, []);

  useEffect(() => {
    if (queryOperationId) {
      setOperationId(queryOperationId);
      void fetchOperation(queryOperationId);
    }
    // Intentional: run only when queryOperationId changes
  }, [queryOperationId]);

  const isCanonicalOperationId = (value: string) => /^\d+$/.test(value.trim());

  const selectedQueueItem = operation
    ? queueItems.find((item) => item.operation_id === operation.id) ?? null
    : null;
  const claimState = selectedQueueItem?.claim.state ?? "none";
  const canExecuteByClaim = claimState === "mine";
  const canClockOnByStatus =
    operation?.status === "PENDING" || operation?.status === "PLANNED";

  // Mode B = operator has claimed this operation
  const isExecutionMode = claimState === "mine";

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

      const preferred =
        queryOperationId && /^\d+$/.test(queryOperationId)
          ? data.items.find((item) => item.operation_id === Number(queryOperationId))
          : null;
      const next = preferred ?? data.items[0];
      setOperationId(String(next.operation_id));
      setSearchParams({ operationId: String(next.operation_id) });
      await fetchOperation(String(next.operation_id));
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to load station queue.");
    } finally {
      setQueueLoading(false);
    }
  };

  const fetchOperation = async (id: string) => {
    const trimmedId = id.trim();
    if (!trimmedId) return;
    if (!isCanonicalOperationId(trimmedId)) {
      toast.error("Operation ID must be numeric.");
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
      toast.error(err instanceof Error ? err.message : "Failed to load operation.");
    } finally {
      setLoading(false);
    }
  };

  const selectQueueOperation = async (item: StationQueueItem) => {
    setQueueOverlayOpen(false);
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
      toast.error(err instanceof Error ? err.message : "Failed to claim operation.");
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
      setQueueOverlayOpen(false);
      await refreshQueue();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to release claim.");
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
      toast.success("Clocked on — " + mapExecutionStatusText(data.status));
    } catch (err) {
      if (err instanceof HttpError && err.status === 403) {
        toast.error("Claim required");
      } else if (err instanceof HttpError && err.status === 409) {
        toast.error("Already started");
      } else {
        toast.error(err instanceof Error ? err.message : "Action failed.");
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
      toast.success("Quantity reported — " + mapExecutionStatusText(data.status));
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Action failed.");
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
      toast.success("Clocked off — " + mapExecutionStatusText(data.status));
    } catch (err) {
      if (err instanceof HttpError && err.status === 403) {
        toast.error("Claim required");
      } else if (err instanceof HttpError && err.status === 409) {
        toast.error("Operation already completed");
      } else {
        toast.error(err instanceof Error ? err.message : "Action failed.");
      }
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
      await refreshQueue();
    }
  };

  // ── MODE A — Operation Selection ──────────────────────────────────────────
  if (!isExecutionMode) {
    return (
      <div className="h-full flex flex-col bg-white">
        <PageHeader
          title="Station Execution"
          showBackButton={false}
          actions={
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-700 font-medium">
                Workstation: {stationScope}
              </span>
              <button
                onClick={() => void refreshQueue()}
                disabled={queueLoading}
                className="h-10 px-4 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                <RefreshCw className="inline w-4 h-4 mr-1" />
                Refresh
              </button>
            </div>
          }
        />

        <div className="flex-1 overflow-auto p-4 max-w-2xl mx-auto w-full">
          {/* Selected operation — awaiting claim */}
          {operation && claimState === "none" && (
            <div className="mb-4 bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center justify-between gap-4">
              <div className="min-w-0">
                <p className="font-semibold text-gray-900 truncate">{operation.name}</p>
                <div className="mt-1">
                  <StatusBadge
                    variant={mapExecutionStatusBadgeVariant(operation.status)}
                    size="sm"
                  >
                    {mapExecutionStatusText(operation.status)}
                  </StatusBadge>
                </div>
              </div>
              <button
                onClick={() => void claimOperation()}
                disabled={claimLoading}
                className="shrink-0 h-12 px-6 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-50"
              >
                {claimLoading ? "Claiming..." : "Claim"}
              </button>
            </div>
          )}

          {/* Operation claimed by someone else */}
          {operation && claimState === "other" && (
            <div className="mb-4 bg-orange-50 border border-orange-200 rounded-xl p-4 flex items-center gap-2 text-orange-800">
              <Lock className="w-4 h-4 shrink-0" />
              <p className="text-sm font-medium">
                Claimed by another operator. Select a different operation.
              </p>
            </div>
          )}

          {loading ? (
            <p className="text-center py-12 text-gray-500">Loading...</p>
          ) : (
            <>
              <QueueList
                items={queueItems}
                loading={queueLoading}
                activeOperationId={operation?.id}
                onSelect={(item) => void selectQueueOperation(item)}
              />
              <details className="mt-4 border-t pt-3">
                <summary className="text-sm text-gray-500 cursor-pointer select-none">
                  Enter operation ID manually
                </summary>
                <div className="mt-3 flex items-center gap-2">
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={operationId}
                    onChange={(e) => setOperationId(e.target.value)}
                    placeholder="Numeric operation ID"
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-full"
                  />
                  <button
                    onClick={() => void fetchOperation(operationId)}
                    disabled={loading}
                    className="h-10 px-4 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
                  >
                    Load
                  </button>
                </div>
              </details>
            </>
          )}
        </div>
      </div>
    );
  }

  // ── MODE B — Execution Mode (iPad landscape, no scroll) ──────────────────
  // Logically guaranteed: operation is non-null when isExecutionMode is true
  if (!operation) return null;

  return (
    <div className="h-full flex flex-col bg-gray-50 overflow-hidden">
      {/* Compact single-row header */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-b shadow-sm shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-sm text-gray-500 shrink-0 whitespace-nowrap">
            Workstation: {stationScope}
          </span>
          <span className="text-gray-300 shrink-0">|</span>
          <span className="font-semibold text-gray-900 truncate">{operation.name}</span>
          <StatusBadge
            variant={mapExecutionStatusBadgeVariant(operation.status)}
            size="sm"
          >
            {mapExecutionStatusText(operation.status)}
          </StatusBadge>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => void refreshQueue()}
            disabled={queueLoading}
            className="h-9 px-3 border border-gray-300 rounded-lg text-xs text-gray-600 hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className="inline w-3 h-3 mr-1" />
            Refresh
          </button>
          <button
            onClick={() => setQueueOverlayOpen((prev) => !prev)}
            className="h-9 px-3 border border-gray-300 rounded-lg text-xs text-gray-600 hover:bg-gray-50 flex items-center gap-1"
          >
            Queue
            <ChevronDown className="w-3 h-3" />
          </button>
          <button
            onClick={() => void releaseClaim()}
            disabled={claimLoading}
            className="h-9 px-3 border border-red-200 rounded-lg text-xs text-red-600 hover:bg-red-50 disabled:opacity-50"
          >
            Release
          </button>
        </div>
      </div>

      {/* Queue overlay */}
      {queueOverlayOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30"
          onClick={() => setQueueOverlayOpen(false)}
        >
          <div
            className="absolute top-16 right-4 w-80 bg-white rounded-xl shadow-2xl border p-4 max-h-96 overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Station Queue</h3>
              <button
                type="button"
                onClick={() => setQueueOverlayOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <QueueList
              items={queueItems}
              loading={queueLoading}
              activeOperationId={operation.id}
              onSelect={(item) => void selectQueueOperation(item)}
            />
          </div>
        </div>
      )}

      {/* Execution body — must not scroll on iPad landscape */}
      <div className="flex-1 flex flex-col p-4 gap-3 overflow-hidden">
        {/* Claim indicator */}
        <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-2 shrink-0">
          <p className="text-sm font-medium text-green-800">Operation claimed by you</p>
        </div>

        {/* Quantity summary */}
        <div className="grid grid-cols-3 gap-3 shrink-0">
          <div className="bg-white rounded-xl border p-3 text-center">
            <p className="text-xs text-gray-500 mb-1">Completed</p>
            <p className="text-2xl font-bold text-gray-900">{operation.completed_qty}</p>
          </div>
          <div className="bg-white rounded-xl border p-3 text-center">
            <p className="text-xs text-gray-500 mb-1">Good</p>
            <p className="text-2xl font-bold text-green-700">{operation.good_qty}</p>
          </div>
          <div className="bg-white rounded-xl border p-3 text-center">
            <p className="text-xs text-gray-500 mb-1">Scrap</p>
            <p className="text-2xl font-bold text-red-600">{operation.scrap_qty}</p>
          </div>
        </div>

        {/* COMPLETED */}
        {operation.status === "COMPLETED" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
              <p className="text-xl font-bold text-green-700">Operation Completed</p>
              <p className="text-sm text-green-600 mt-1">All write controls are disabled.</p>
            </div>
          </div>
        )}

        {/* ABORTED */}
        {operation.status === "ABORTED" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
              <p className="text-xl font-bold text-red-700">Operation Aborted</p>
            </div>
          </div>
        )}

        {/* PENDING / PLANNED → Clock On */}
        {canClockOnByStatus && (
          <div className="flex-1 flex flex-col justify-end gap-3 pb-2">
            {!canExecuteByClaim && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-800 text-center">
                Claim required
              </div>
            )}
            <button
              onClick={() => void startOperation()}
              disabled={actionLoading || !canExecuteByClaim}
              className="w-full h-16 bg-green-600 text-white text-xl font-bold rounded-2xl hover:bg-green-700 disabled:opacity-50 active:scale-[0.98] transition"
            >
              Clock On
            </button>
          </div>
        )}

        {/* IN_PROGRESS → Qty steppers + Report + Clock Off */}
        {operation.status === "IN_PROGRESS" && (
          <div className="flex-1 flex flex-col gap-3 min-h-0">
            {/* Stepper inputs */}
            <div className="bg-white rounded-xl border p-4 grid grid-cols-2 gap-6 shrink-0">
              <Stepper label="Good quantity" value={goodQty} onChange={setGoodQty} />
              <Stepper label="Scrap quantity" value={scrapQty} onChange={setScrapQty} />
            </div>

            {/* Action buttons */}
            <div className="flex flex-col gap-3 shrink-0">
              {!canExecuteByClaim && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-800 text-center">
                  Claim required
                </div>
              )}
              <button
                onClick={() => void reportQuantity()}
                disabled={actionLoading || !canExecuteByClaim}
                className="w-full h-14 bg-blue-600 text-white text-lg font-semibold rounded-2xl hover:bg-blue-700 disabled:opacity-50 active:scale-[0.98] transition"
              >
                Report Quantity
              </button>
              <button
                onClick={() => void completeOperation()}
                disabled={actionLoading || !canExecuteByClaim}
                title={!canExecuteByClaim ? "Claim required" : undefined}
                className="w-full h-16 bg-orange-600 text-white text-xl font-bold rounded-2xl hover:bg-orange-700 disabled:opacity-50 active:scale-[0.98] transition"
              >
                Clock Off
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

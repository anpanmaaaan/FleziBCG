import { type DowntimeReasonClass } from "@/app/api/operationApi";
const DOWNTIME_REASONS: { value: DowntimeReasonClass; label: string }[] = [
  { value: "PLANNED_MAINTENANCE", label: "station.downtime.reason.plannedMaintenance" },
  { value: "UNPLANNED_BREAKDOWN", label: "station.downtime.reason.unplannedBreakdown" },
  { value: "MATERIAL_SHORTAGE", label: "station.downtime.reason.materialShortage" },
  { value: "QUALITY_HOLD", label: "station.downtime.reason.qualityHold" },
  { value: "OTHER", label: "station.downtime.reason.other" },
];
function StartDowntimeModal({ open, onClose, onSubmit, loading }: {
  open: boolean;
  onClose: () => void;
  onSubmit: (reason: DowntimeReasonClass, note: string) => void;
  loading: boolean;
}) {
  const { t } = useI18n();
  const [reason, setReason] = useState<DowntimeReasonClass>("PLANNED_MAINTENANCE");
  const [note, setNote] = useState("");
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-96" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-bold mb-4">{t("station.action.startDowntime")}</h2>
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {t("station.downtime.reason.label")}
          <select
            className="mt-1 block w-full border border-gray-300 rounded-lg p-2"
            value={reason}
            onChange={e => setReason(e.target.value as DowntimeReasonClass)}
            disabled={loading}
          >
            {DOWNTIME_REASONS.map(opt => (
              <option key={opt.value} value={opt.value}>{t(opt.label as any)}</option>
            ))}
          </select>
        </label>
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {t("station.downtime.note.label")}
          <input
            className="mt-1 block w-full border border-gray-300 rounded-lg p-2"
            value={note}
            onChange={e => setNote(e.target.value)}
            placeholder={t("station.downtime.note.placeholder")}
            disabled={loading}
          />
        </label>
        <div className="flex gap-2 mt-4 justify-end">
          <button onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700" disabled={loading}>{t("common.action.cancel")}</button>
          <button
            onClick={() => onSubmit(reason, note)}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50"
            disabled={loading}
          >
            {t("station.action.startDowntime")}
          </button>
        </div>
      </div>
    </div>
  );
}
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
import { useI18n } from "@/app/i18n";

// ── Numeric Keypad Overlay ────────────────────────────────────────────────────

interface KeypadProps {
  label: string;
  value: number;
  onConfirm: (v: number) => void;
  onClose: () => void;
}

function NumericKeypad({ label, value, onConfirm, onClose }: KeypadProps) {
  const [draft, setDraft] = useState(String(value));

  const { t } = useI18n();
  const press = (key: string) => {
    if (key === t("station.keypad.clr")) {
      setDraft("0");
    } else if (key === t("station.keypad.ok")) {
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
    [t("station.keypad.clr"), "0", t("station.keypad.ok")],
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
  const { t } = useI18n();
  const [keypadOpen, setKeypadOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-medium text-gray-600">{label}</span>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onChange(Math.max(0, value - 1))}
          aria-label={t("station.aria.decrease", { label })}
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
          aria-label={t("station.aria.increase", { label })}
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
  const { t } = useI18n();
  if (loading) {
    return <p className="text-sm text-gray-500 py-8 text-center">{t("station.loading")}</p>;
  }
  if (items.length === 0) {
    return (
      <p className="text-sm text-gray-500 py-8 text-center">
        {t("station.queue.empty")}
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
    const [downtimeModalOpen, setDowntimeModalOpen] = useState(false);
    const [downtimeLoading, setDowntimeLoading] = useState(false);

      // ...existing code...
      // ...existing code...
      // ...existing code...
    // ...existing code...
    const startDowntime = async (reason: DowntimeReasonClass, note: string) => {
      if (!operation) return;
      setDowntimeLoading(true);
      try {
        await operationApi.startDowntime(operation.id, { reason_class: reason, note });
        toast.success(t("station.toast.downtimeStarted"));
        setDowntimeModalOpen(false);
        await fetchOperation(String(operation.id));
        await refreshQueue();
      } catch (err) {
        let msg = t("station.toast.downtimeFailed");
        if (err instanceof HttpError && err.status === 409 && typeof err.detail === "string") {
          if (err.detail.startsWith("STATE_")) msg = t(`station.reject.${err.detail}` as never);
          else if (err.detail.startsWith("DOWNTIME_")) msg = t(`station.reject.${err.detail}` as never);
          else if (err.detail.startsWith("INVALID_")) msg = t(`station.reject.${err.detail}` as never);
        }
        toast.error(msg);
      } finally {
        setDowntimeLoading(false);
      }
    };
  const { t } = useI18n();
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

  // canStartDowntime must be declared after operation is defined
  const canStartDowntime = operation && ["IN_PROGRESS", "PAUSED"].includes(operation.status);

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
    operation?.status === "PLANNED";

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
      toast.error(err instanceof Error ? err.message : t("station.toast.loadQueueFailed"));
    } finally {
      setQueueLoading(false);
    }
  };

  const fetchOperation = async (id: string) => {
    const trimmedId = id.trim();
    if (!trimmedId) return;
    if (!isCanonicalOperationId(trimmedId)) {
      toast.error(t("station.toast.idMustBeNumeric"));
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
      toast.error(err instanceof Error ? err.message : t("station.toast.loadOperationFailed"));
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
      toast.success(t("station.toast.claimed"));
      await refreshQueue();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("station.toast.claimFailed"));
    } finally {
      setClaimLoading(false);
    }
  };

  const releaseClaim = async () => {
    if (!operation) return;
    setClaimLoading(true);
    try {
      await stationApi.release(operation.id, { reason: "operator_release" });
      toast.success(t("station.toast.released"));
      setQueueOverlayOpen(false);
      await refreshQueue();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("station.toast.releaseFailed"));
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
      toast.success(t("station.toast.clockedOn") + mapExecutionStatusText(data.status));
    } catch (err) {
      if (err instanceof HttpError && err.status === 403) {
        toast.error(t("station.claim.required"));
      } else if (err instanceof HttpError && err.status === 409) {
        toast.error(t("station.toast.alreadyStarted"));
      } else {
        toast.error(err instanceof Error ? err.message : t("station.toast.actionFailed"));
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
      toast.success(t("station.toast.quantityReported") + mapExecutionStatusText(data.status));
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("station.toast.actionFailed"));
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
      await refreshQueue();
    }
  };

  const rejectReasonKey = (detail: unknown): string | null => {
    if (typeof detail !== "string") return null;
    const code = detail.trim();
    if (!code.startsWith("STATE_")) return null;
    return `station.reject.${code}`;
  };

  const pauseOperation = async () => {
    if (!operation) return;
    setActionLoading(true);
    try {
      const data = await operationApi.pause(operation.id, {});
      toast.success(t("station.toast.paused") + mapExecutionStatusText(data.status));
    } catch (err) {
      if (err instanceof HttpError && err.status === 403) {
        toast.error(t("station.claim.required"));
      } else if (err instanceof HttpError && err.status === 409) {
        const key = rejectReasonKey(err.detail);
        toast.error(key ? t(key as never) : t("station.toast.pauseFailed"));
      } else {
        toast.error(err instanceof Error ? err.message : t("station.toast.pauseFailed"));
      }
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
      await refreshQueue();
    }
  };

  const resumeOperation = async () => {
    if (!operation) return;
    setActionLoading(true);
    try {
      const data = await operationApi.resume(operation.id, {});
      toast.success(t("station.toast.resumed") + mapExecutionStatusText(data.status));
    } catch (err) {
      if (err instanceof HttpError && err.status === 403) {
        toast.error(t("station.claim.required"));
      } else if (err instanceof HttpError && err.status === 409) {
        const key = rejectReasonKey(err.detail);
        toast.error(key ? t(key as never) : t("station.toast.resumeFailed"));
      } else {
        toast.error(err instanceof Error ? err.message : t("station.toast.resumeFailed"));
      }
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
      await refreshQueue();
    }
  };

  const completeOperation = async () => {
    if (!operation) return;
    const confirmed = window.confirm(t("station.confirm.clockOff"));
    if (!confirmed) return;
    setActionLoading(true);
    try {
      const data = await operationApi.complete(operation.id, {
        operator_id: currentUser?.user_id ?? null,
        completed_at: new Date().toISOString(),
      });
      toast.success(t("station.toast.clockedOff") + mapExecutionStatusText(data.status));
    } catch (err) {
      if (err instanceof HttpError && err.status === 403) {
        toast.error(t("station.claim.required"));
      } else if (err instanceof HttpError && err.status === 409) {
        toast.error(t("station.toast.alreadyCompleted"));
      } else {
        toast.error(err instanceof Error ? err.message : t("station.toast.actionFailed"));
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
          title={t("station.title")}
          showBackButton={false}
          actions={
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-700 font-medium">
                {t("station.workstation.label")} {stationScope}
              </span>
              <button
                onClick={() => void refreshQueue()}
                disabled={queueLoading}
                className="h-10 px-4 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                <RefreshCw className="inline w-4 h-4 mr-1" />
                {t("station.action.refresh")}
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
                    {t(mapExecutionStatusText(operation.status) as import("@/app/i18n/keys").I18nSemanticKey)}
                  </StatusBadge>
                </div>
              </div>
              <button
                onClick={() => void claimOperation()}
                disabled={claimLoading}
                className="shrink-0 h-12 px-6 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-50"
              >
                {claimLoading ? t("station.action.claiming") : t("station.action.claim")}
              </button>
            </div>
          )}

          {/* Operation claimed by someone else */}
          {operation && claimState === "other" && (
            <div className="mb-4 bg-orange-50 border border-orange-200 rounded-xl p-4 flex items-center gap-2 text-orange-800">
              <Lock className="w-4 h-4 shrink-0" />
              <p className="text-sm font-medium">
                {t("station.claim.takenWarning")}
              </p>
            </div>
          )}

          {loading ? (
            <p className="text-center py-12 text-gray-500">{t("station.loading")}</p>
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
                  {t("station.manualEntry.label")}
                </summary>
                <div className="mt-3 flex items-center gap-2">
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={operationId}
                    onChange={(e) => setOperationId(e.target.value)}
                    placeholder={t("station.manualEntry.placeholder")}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-full"
                  />
                  <button
                    onClick={() => void fetchOperation(operationId)}
                    disabled={loading}
                    className="h-10 px-4 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
                  >
                    {t("station.action.load")}
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
            {t("station.workstation.label")} {stationScope}
          </span>
          <span className="text-gray-300 shrink-0">|</span>
          <span className="font-semibold text-gray-900 truncate">{operation.name}</span>
          <StatusBadge
            variant={mapExecutionStatusBadgeVariant(operation.status)}
            size="sm"
          >
            {t(mapExecutionStatusText(operation.status) as import("@/app/i18n/keys").I18nSemanticKey)}
          </StatusBadge>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => void refreshQueue()}
            disabled={queueLoading}
            className="h-9 px-3 border border-gray-300 rounded-lg text-xs text-gray-600 hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className="inline w-3 h-3 mr-1" />
            {t("station.action.refresh")}
          </button>
          <button
            onClick={() => setQueueOverlayOpen((prev) => !prev)}
            className="h-9 px-3 border border-gray-300 rounded-lg text-xs text-gray-600 hover:bg-gray-50 flex items-center gap-1"
          >
            {t("station.tab.queue")}
            <ChevronDown className="w-3 h-3" />
          </button>
          <button
            onClick={() => void releaseClaim()}
            disabled={claimLoading}
            className="h-9 px-3 border border-red-200 rounded-lg text-xs text-red-600 hover:bg-red-50 disabled:opacity-50"
          >
            {t("station.action.release")}
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
              <h3 className="font-semibold text-gray-900">{t("station.queue.title")}</h3>
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
          <p className="text-sm font-medium text-green-800">{t("station.claim.ownedBadge")}</p>
        </div>

        {/* Quantity summary */}
        <div className="grid grid-cols-3 gap-3 shrink-0">
          <div className="bg-white rounded-xl border p-3 text-center">
            <p className="text-xs text-gray-500 mb-1">{t("station.status.completed")}</p>
            <p className="text-2xl font-bold text-gray-900">{operation.completed_qty}</p>
          </div>
          <div className="bg-white rounded-xl border p-3 text-center">
            <p className="text-xs text-gray-500 mb-1">{t("station.qty.good")}</p>
            <p className="text-2xl font-bold text-green-700">{operation.good_qty}</p>
          </div>
          <div className="bg-white rounded-xl border p-3 text-center">
            <p className="text-xs text-gray-500 mb-1">{t("station.qty.scrap")}</p>
            <p className="text-2xl font-bold text-red-600">{operation.scrap_qty}</p>
          </div>
        </div>

        {/* COMPLETED */}
        {operation.status === "COMPLETED" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
              <p className="text-xl font-bold text-green-700">{t("station.status.completedHeading")}</p>
              <p className="text-sm text-green-600 mt-1">{t("station.completed.disabledNote")}</p>
            </div>
          </div>
        )}

        {/* ABORTED */}
        {operation.status === "ABORTED" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
              <p className="text-xl font-bold text-red-700">{t("station.status.abortedHeading")}</p>
            </div>
          </div>
        )}

        {/* PLANNED → Clock On */}
        {canClockOnByStatus && (
          <div className="flex-1 flex flex-col justify-end gap-3 pb-2">
            {!canExecuteByClaim && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-800 text-center">
                {t("station.claim.required")}
              </div>
            )}
            <button
              onClick={() => void startOperation()}
              disabled={actionLoading || !canExecuteByClaim}
              className="w-full h-16 bg-green-600 text-white text-xl font-bold rounded-2xl hover:bg-green-700 disabled:opacity-50 active:scale-[0.98] transition"
            >
              {t("station.action.clockOn")}
            </button>
          </div>
        )}

        {/* IN_PROGRESS → Qty steppers + Report + Clock Off */}
        {operation.status === "IN_PROGRESS" && (
          <div className="flex-1 flex flex-col gap-3 min-h-0">
            {/* Stepper inputs */}
            <div className="bg-white rounded-xl border p-4 grid grid-cols-2 gap-6 shrink-0">
              <Stepper label={t("station.input.goodQty")} value={goodQty} onChange={setGoodQty} />
              <Stepper label={t("station.input.scrapQty")} value={scrapQty} onChange={setScrapQty} />
            </div>

            {/* Action buttons */}
            <div className="flex flex-col gap-3 shrink-0">
              {!canExecuteByClaim && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-800 text-center">
                  {t("station.claim.required")}
                </div>
              )}
              <button
                onClick={() => void reportQuantity()}
                disabled={actionLoading || !canExecuteByClaim}
                className="w-full h-14 bg-blue-600 text-white text-lg font-semibold rounded-2xl hover:bg-blue-700 disabled:opacity-50 active:scale-[0.98] transition"
              >
                {t("station.action.reportQty")}
              </button>
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => void pauseOperation()}
                  disabled={actionLoading || !canExecuteByClaim}
                  title={!canExecuteByClaim ? t("station.claim.required") : undefined}
                  className="h-16 bg-amber-500 text-white text-lg font-semibold rounded-2xl hover:bg-amber-600 disabled:opacity-50 active:scale-[0.98] transition"
                >
                  {t("station.action.pause")}
                </button>
                <button
                  onClick={() => setDowntimeModalOpen(true)}
                  disabled={downtimeLoading || !canExecuteByClaim || !canStartDowntime}
                  title={!canExecuteByClaim ? t("station.claim.required") : undefined}
                  className="h-16 bg-blue-500 text-white text-lg font-semibold rounded-2xl hover:bg-blue-600 disabled:opacity-50 active:scale-[0.98] transition"
                >
                  {t("station.action.startDowntime")}
                </button>
                <button
                  onClick={() => void completeOperation()}
                  disabled={actionLoading || !canExecuteByClaim}
                  title={!canExecuteByClaim ? t("station.claim.required") : undefined}
                  className="h-16 bg-orange-600 text-white text-xl font-bold rounded-2xl hover:bg-orange-700 disabled:opacity-50 active:scale-[0.98] transition"
                >
                  {t("station.action.clockOff")}
                </button>
              </div>
            </div>
            <StartDowntimeModal
              open={downtimeModalOpen}
              onClose={() => setDowntimeModalOpen(false)}
              onSubmit={startDowntime}
              loading={downtimeLoading}
            />
          </div>
        )}

        {/* PAUSED → Resume */}
        {operation.status === "PAUSED" && (
          <div className="flex-1 flex flex-col justify-end gap-3 pb-2">
            <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center">
              <p className="text-xl font-bold text-amber-800">
                {t("station.status.pausedHeading")}
              </p>
              <p className="text-sm text-amber-700 mt-1">{t("station.paused.note")}</p>
            </div>
            {!canExecuteByClaim && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-800 text-center">
                {t("station.claim.required")}
              </div>
            )}
            <button
              onClick={() => void resumeOperation()}
              disabled={actionLoading || !canExecuteByClaim}
              className="w-full h-16 bg-green-600 text-white text-xl font-bold rounded-2xl hover:bg-green-700 disabled:opacity-50 active:scale-[0.98] transition"
            >
              {t("station.action.resume")}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

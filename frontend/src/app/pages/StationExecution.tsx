import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router";
import { PageHeader } from "@/app/components";
import { StatusBadge } from "@/app/components";
import { MockWarningBanner } from "@/app/components";
import { toast } from "sonner";
import { RefreshCw, Lock, X, ChevronDown, ArrowLeft, RotateCcw, Info } from "lucide-react";
import {
  fetchDowntimeReasons,
  operationApi,
  type DowntimeReasonOption,
  type OperationDetail,
} from "@/app/api";
import { stationApi, type StationQueueItem } from "@/app/api";
import { HttpError } from "@/app/api";
import { useAuth } from "@/app/auth";
import {
  mapExecutionStatusBadgeVariant,
  mapExecutionStatusText,
} from "@/app/api";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

function ReopenOperationModal({ open, onClose, onSubmit, loading }: {
  open: boolean;
  onClose: () => void;
  onSubmit: (reason: string) => void;
  loading: boolean;
}) {
  const { t } = useI18n();
  const [reason, setReason] = useState("");

  useEffect(() => {
    if (!open) {
      setReason("");
    }
  }, [open]);

  if (!open) return null;

  const trimmedReason = reason.trim();

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-96" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-bold mb-4">{t("station.action.reopen")}</h2>
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {t("station.reopen.reason.label")}
          <textarea
            className="mt-1 block w-full border border-gray-300 rounded-lg p-2 min-h-28 resize-y"
            value={reason}
            onChange={e => setReason(e.target.value)}
            placeholder={t("station.reopen.reason.placeholder")}
            disabled={loading}
          />
        </label>
        <p className="text-xs text-gray-500">{t("station.reopen.reason.helper")}</p>
        <div className="flex gap-2 mt-4 justify-end">
          <button onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700" disabled={loading}>
            {t("station.reopen.dialog.cancel")}
          </button>
          <button
            onClick={() => onSubmit(trimmedReason)}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50"
            disabled={loading || trimmedReason.length === 0}
          >
            {t("station.reopen.dialog.submit")}
          </button>
        </div>
      </div>
    </div>
  );
}

function StartDowntimeModal({ open, onClose, onSubmit, loading, reasons, reasonsLoading }: {
  open: boolean;
  onClose: () => void;
  onSubmit: (reasonCode: string, note: string) => void;
  loading: boolean;
  reasons: DowntimeReasonOption[];
  reasonsLoading: boolean;
}) {
  const { t } = useI18n();
  const [reasonCode, setReasonCode] = useState("");
  const [note, setNote] = useState("");

  useEffect(() => {
    if (!open) {
      setReasonCode("");
      setNote("");
      return;
    }

    setReasonCode((current) => {
      if (current && reasons.some((item) => item.reason_code === current)) {
        return current;
      }
      return reasons[0]?.reason_code ?? "";
    });
  }, [open, reasons]);

  if (!open) return null;

  const selectedReason = reasons.find((item) => item.reason_code === reasonCode) ?? null;
  const noteRequired = selectedReason?.requires_comment ?? false;
  const noteValue = note.trim();
  const submitDisabled =
    loading ||
    reasonsLoading ||
    !reasonCode ||
    (noteRequired && noteValue.length === 0);

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-96" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-bold mb-4">{t("station.action.startDowntime")}</h2>
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {t("station.downtime.reason.label")}
          <select
            className="mt-1 block w-full border border-gray-300 rounded-lg p-2"
            value={reasonCode}
            onChange={e => setReasonCode(e.target.value)}
            disabled={loading || reasonsLoading || reasons.length === 0}
          >
            {reasons.length === 0 ? (
              <option value="">{t("station.downtime.reason.empty")}</option>
            ) : (
              reasons.map((item) => (
                <option key={item.reason_code} value={item.reason_code}>{item.reason_name}</option>
              ))
            )}
          </select>
        </label>
        {selectedReason ? (
          <p className="mb-2 text-xs text-gray-500">
            {t("station.downtime.reason.groupPrefix")} {selectedReason.reason_group}
          </p>
        ) : null}
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {noteRequired ? t("station.downtime.note.requiredLabel") : t("station.downtime.note.label")}
          <input
            className="mt-1 block w-full border border-gray-300 rounded-lg p-2"
            value={note}
            onChange={e => setNote(e.target.value)}
            placeholder={noteRequired ? t("station.downtime.note.requiredPlaceholder") : t("station.downtime.note.placeholder")}
            disabled={loading || reasonsLoading}
          />
        </label>
        {reasonsLoading ? <p className="text-xs text-gray-500">{t("station.downtime.reason.loading")}</p> : null}
        {!reasonsLoading && reasons.length === 0 ? <p className="text-xs text-amber-700">{t("station.downtime.reason.emptyHelp")}</p> : null}
        <div className="flex gap-2 mt-4 justify-end">
          <button onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700" disabled={loading}>{t("common.action.cancel")}</button>
          <button
            onClick={() => onSubmit(reasonCode, noteValue)}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50"
            disabled={submitDisabled}
          >
            {t("station.action.startDowntime")}
          </button>
        </div>
      </div>
    </div>
  );
}

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
  const KEY_CLR = "__CLR__";
  const KEY_OK = "__OK__";
  const press = (key: string) => {
    if (key === KEY_CLR) {
      setDraft("0");
    } else if (key === KEY_OK) {
      onConfirm(Math.max(0, parseInt(draft, 10) || 0));
    } else {
      setDraft((prev) => {
        const next = prev === "0" ? key : prev + key;
        return next.length > 5 ? prev : next;
      });
    }
  };

  const rows: { id: string; label: string }[][] = [
    [{ id: "7", label: "7" }, { id: "8", label: "8" }, { id: "9", label: "9" }],
    [{ id: "4", label: "4" }, { id: "5", label: "5" }, { id: "6", label: "6" }],
    [{ id: "1", label: "1" }, { id: "2", label: "2" }, { id: "3", label: "3" }],
    [
      { id: KEY_CLR, label: t("station.keypad.clr") },
      { id: "0", label: "0" },
      { id: KEY_OK, label: t("station.keypad.ok") },
    ],
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
          {rows.flat().map((entry) => (
            <button
              key={entry.id}
              type="button"
              onClick={() => press(entry.id)}
              className={`h-14 rounded-xl text-lg font-semibold transition active:scale-95 ${
                entry.id === KEY_OK
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : entry.id === KEY_CLR
                  ? "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  : "bg-gray-100 text-gray-900 hover:bg-gray-200"
              }`}
            >
              {entry.label}
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
  labelClassName?: string;
  valueClassName?: string;
  disabled?: boolean;
  quickAddValues?: number[];
  quickAddTone?: "good" | "scrap";
  onReset?: () => void;
}

function Stepper({
  label,
  value,
  onChange,
  labelClassName,
  valueClassName,
  disabled = false,
  quickAddValues,
  quickAddTone = "good",
  onReset,
}: StepperProps) {
  const { t } = useI18n();
  const [keypadOpen, setKeypadOpen] = useState(false);
  const quickAddClass =
    quickAddTone === "scrap"
      ? "border-amber-200 bg-amber-50 text-amber-800 hover:bg-amber-100"
      : "border-emerald-200 bg-emerald-50 text-emerald-800 hover:bg-emerald-100";

  return (
    <div className="flex flex-col gap-3">
      <span className={`text-xl font-bold md:text-2xl lg:text-3xl ${disabled ? "text-gray-400" : labelClassName ?? "text-gray-700"}`}>{label}</span>
      {quickAddValues && quickAddValues.length > 0 && (
        <div className="flex flex-wrap gap-3">
          {quickAddValues.map((amount) => (
            <button
              key={amount}
              type="button"
              onClick={() => onChange(value + amount)}
              aria-label={t("station.input.quickAddAria", { amount, label })}
              disabled={disabled}
              className={`min-h-11 rounded-2xl border px-4 text-lg font-bold transition sm:min-h-12 sm:px-5 sm:text-xl md:min-h-14 md:px-6 md:text-2xl ${disabled ? "cursor-not-allowed border-gray-200 bg-gray-100 text-gray-300" : quickAddClass}`}
            >
              +{amount}
            </button>
          ))}
          {onReset && (
            <button
              type="button"
              onClick={onReset}
              aria-label={t("station.input.resetAria", { label })}
              disabled={disabled}
              className={`min-h-11 rounded-2xl border border-gray-200 px-4 text-lg font-bold transition sm:min-h-12 sm:px-5 sm:text-xl md:min-h-14 md:px-6 md:text-2xl ${disabled ? "cursor-not-allowed bg-gray-100 text-gray-300" : "bg-gray-100 text-gray-800 hover:bg-gray-200"}`}
            >
              <RotateCcw className="h-5 w-5 md:h-6 md:w-6" />
            </button>
          )}
        </div>
      )}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => onChange(Math.max(0, value - 1))}
          aria-label={t("station.aria.decrease", { label })}
          disabled={disabled}
          className="min-h-14 min-w-14 rounded-2xl bg-gray-100 text-2xl font-bold text-gray-700 hover:bg-gray-200 active:scale-95 transition select-none sm:min-h-16 sm:min-w-16 sm:text-3xl md:min-h-20 md:min-w-20 md:text-4xl disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-300"
        >
          −
        </button>
        <button
          type="button"
          onClick={() => setKeypadOpen(true)}
          disabled={disabled}
          className={`flex-1 min-h-14 rounded-2xl bg-white border px-4 py-3 text-center text-3xl font-bold text-gray-900 transition sm:min-h-16 sm:px-5 sm:py-4 sm:text-4xl md:min-h-18 md:px-6 md:py-4 md:text-5xl disabled:cursor-not-allowed disabled:border-gray-200 disabled:bg-gray-50 disabled:text-gray-400 ${valueClassName ?? "border-gray-200 hover:border-blue-300"}`}
        >
          {value}
        </button>
        <button
          type="button"
          onClick={() => onChange(value + 1)}
          aria-label={t("station.aria.increase", { label })}
          disabled={disabled}
          className="min-h-14 min-w-14 rounded-2xl bg-gray-100 text-2xl font-bold text-gray-700 hover:bg-gray-200 active:scale-95 transition select-none sm:min-h-16 sm:min-w-16 sm:text-3xl md:min-h-20 md:min-w-20 md:text-4xl disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-300"
        >
          +
        </button>
      </div>
      {keypadOpen && !disabled && (
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
  filter: QueueFilter;
  onFilterChange: (filter: QueueFilter) => void;
  onSelect: (item: StationQueueItem) => void;
}

type QueueFilter = "all" | "mine" | "ready" | "paused" | "blocked" | "downtime";

const isBackendClaimableQueueStatus = (status: StationQueueItem["status"]): boolean =>
  status === "PLANNED" || status === "IN_PROGRESS";

const matchesQueueFilter = (item: StationQueueItem, filter: QueueFilter): boolean => {
  switch (filter) {
    case "mine":
      return item.claim.state === "mine";
    case "ready":
      return isBackendClaimableQueueStatus(item.status) && !item.downtime_open;
    case "paused":
      return item.status === "PAUSED";
    case "blocked":
      return item.status === "BLOCKED";
    case "downtime":
      return item.downtime_open;
    case "all":
    default:
      return true;
  }
};

function QueueList({
  items,
  loading,
  activeOperationId,
  filter,
  onFilterChange,
  onSelect,
}: QueueListProps) {
  const { t } = useI18n();
  const hasMineClaim = items.some((item) => item.claim.state === "mine");

  const summary = useMemo(() => {
    return items.reduce(
      (acc, item) => {
        if (isBackendClaimableQueueStatus(item.status)) {
          acc.ready += 1;
        }
        if (item.status === "PAUSED") {
          acc.paused += 1;
        }
        if (item.status === "BLOCKED") {
          acc.blocked += 1;
        }
        if (item.downtime_open) {
          acc.downtime += 1;
        }
        if (item.claim.state === "mine") {
          acc.mine += 1;
        }
        return acc;
      },
      { ready: 0, paused: 0, blocked: 0, downtime: 0, mine: 0 },
    );
  }, [items]);

  const filteredItems = useMemo(
    () => items.filter((item) => matchesQueueFilter(item, filter)),
    [filter, items],
  );
  const selectedIsFilteredOut =
    activeOperationId !== undefined &&
    items.some((item) => item.operation_id === activeOperationId) &&
    !filteredItems.some((item) => item.operation_id === activeOperationId);

  const filterDefs: { key: QueueFilter; label: string }[] = [
    { key: "all", label: t("station.queue.filter.all") },
    { key: "mine", label: t("station.queue.filter.mine") },
    { key: "ready", label: t("station.queue.filter.ready") },
    { key: "paused", label: t("station.queue.filter.paused") },
    { key: "blocked", label: t("station.queue.filter.blocked") },
    { key: "downtime", label: t("station.queue.filter.downtime") },
  ];

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
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
        <div className="rounded-lg border bg-white px-3 py-2">
          <p className="text-[11px] text-gray-500">{t("station.queue.summary.ready")}</p>
          <p className="text-sm font-semibold text-gray-900">{summary.ready}</p>
        </div>
        <div className="rounded-lg border bg-white px-3 py-2">
          <p className="text-[11px] text-gray-500">{t("station.queue.summary.paused")}</p>
          <p className="text-sm font-semibold text-amber-700">{summary.paused}</p>
        </div>
        <div className="rounded-lg border bg-white px-3 py-2">
          <p className="text-[11px] text-gray-500">{t("station.queue.summary.blocked")}</p>
          <p className="text-sm font-semibold text-red-700">{summary.blocked}</p>
        </div>
        <div className="rounded-lg border bg-white px-3 py-2">
          <p className="text-[11px] text-gray-500">{t("station.queue.summary.downtime")}</p>
          <p className="text-sm font-semibold text-red-700">{summary.downtime}</p>
        </div>
        <div className="rounded-lg border bg-white px-3 py-2">
          <p className="text-[11px] text-gray-500">{t("station.queue.summary.mine")}</p>
          <p className="text-sm font-semibold text-blue-700">{summary.mine}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        {filterDefs.map((entry) => {
          const active = filter === entry.key;
          return (
            <button
              key={entry.key}
              type="button"
              onClick={() => onFilterChange(entry.key)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition ${
                active
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"
              }`}
            >
              {entry.label}
            </button>
          );
        })}
      </div>

      {selectedIsFilteredOut && (
        <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          {t("station.queue.selectedOutsideFilter")}
        </p>
      )}

      {filteredItems.length === 0 && (
        <p className="text-sm text-gray-500 py-6 text-center">{t("station.queue.emptyFiltered")}</p>
      )}

      {filteredItems.map((item) => {
        const active = activeOperationId === item.operation_id;
        const locked = item.claim.state === "other";
        const showDowntimeTag = item.downtime_open;
        const showBlockedDowntimeHint = item.status === "BLOCKED" && item.downtime_open;
        const isMine = item.claim.state === "mine";
        const isClaimableByStatus = isBackendClaimableQueueStatus(item.status);

        const rowTone =
          item.status === "BLOCKED"
            ? "border-red-200 bg-red-50"
            : item.status === "PAUSED"
            ? "border-amber-200 bg-amber-50"
            : "border-gray-200 bg-white";

        const claimHint =
          item.claim.state === "mine"
            ? t("station.claim.ownedBadge")
            : item.claim.state === "other"
            ? t("station.queue.claimedByOther")
            : isClaimableByStatus && !hasMineClaim
            ? t("station.queue.readyToClaim")
            : null;

        const claimHintTone =
          item.claim.state === "mine"
            ? "text-blue-700"
            : item.claim.state === "other"
            ? "text-orange-700"
            : "text-emerald-700";

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
                : `${rowTone} hover:border-blue-300 hover:bg-blue-50 active:scale-[0.99]`
            }`}
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 min-w-0">
                {locked && <Lock className="w-4 h-4 text-orange-500 shrink-0" />}
                {isMine && <span className="w-2.5 h-2.5 rounded-full bg-blue-600 shrink-0" aria-hidden="true" />}
                <p className="font-semibold text-base text-gray-900 truncate">
                  {item.name}
                </p>
              </div>
              <StatusBadge variant={mapExecutionStatusBadgeVariant(item.status)}>
                {t(mapExecutionStatusText(item.status) as I18nSemanticKey)}
              </StatusBadge>
            </div>
            <div className="mt-1 flex items-center gap-2 flex-wrap">
              <p className="text-xs text-gray-500">{item.operation_number}</p>
              {showDowntimeTag && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-xs font-semibold">
                  {t("station.queue.downtimeActive")}
                </span>
              )}
              {showBlockedDowntimeHint && (
                <span className="text-xs text-red-700 font-medium">
                  {t("station.queue.blockedByDowntime")}
                </span>
              )}
              {claimHint && <span className={`text-xs font-medium ${claimHintTone}`}>{claimHint}</span>}
            </div>
          </button>
        );
      })}
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

function KpiCard({ label, value, highlight = false }: { label: string; value: string | number; highlight?: boolean }) {
  return (
    <div className={`rounded-2xl border p-4 text-center md:p-5 ${highlight ? "border-blue-200 bg-blue-50/50 ring-2 ring-blue-100" : "border-slate-200 bg-white"}`}>
      <div className={`text-base font-medium sm:text-lg md:text-xl ${highlight ? "text-blue-700" : "text-slate-700"}`}>{label}</div>
      <div className={`mt-3 text-3xl leading-none sm:text-4xl md:text-5xl lg:text-6xl ${highlight ? "font-bold text-blue-700" : "font-bold text-slate-900"}`}>
        {value}
      </div>
    </div>
  );
}

function TimeCluster({
  targetTime,
  elapsed,
  overBy,
}: {
  targetTime: string;
  elapsed: string;
  overBy?: string | null;
}) {
  const { t } = useI18n();

  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 md:p-5">
      <div className="grid grid-cols-2 gap-3 sm:gap-5">
        <div>
          <div className="text-sm font-medium text-slate-600 sm:text-base md:text-lg">{t("station.timer.targetTime")}</div>
          <div className="mt-2 text-2xl font-semibold text-slate-900 sm:text-3xl md:text-4xl">{targetTime}</div>
        </div>
        <div>
          <div className="text-sm font-medium text-slate-600 sm:text-base md:text-lg">{t("station.timer.elapsed")}</div>
          <div className="mt-2 text-2xl font-semibold text-slate-900 sm:text-3xl md:text-4xl">{elapsed}</div>
          {overBy ? <div className="mt-2 text-xs font-medium text-amber-600 sm:text-sm md:text-base">{t("station.timer.overBy", { duration: overBy })}</div> : null}
        </div>
      </div>
    </div>
  );
}

export function StationExecution() {
  const [downtimeModalOpen, setDowntimeModalOpen] = useState(false);
  const [downtimeLoading, setDowntimeLoading] = useState(false);
  const [downtimeReasons, setDowntimeReasons] = useState<DowntimeReasonOption[]>([]);
  const [downtimeReasonsLoading, setDowntimeReasonsLoading] = useState(false);
  const [reopenModalOpen, setReopenModalOpen] = useState(false);

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
  const [queueFilter, setQueueFilter] = useState<QueueFilter>("all");
  const [queueOverlayOpen, setQueueOverlayOpen] = useState(false);
  const [forceSelectionMode, setForceSelectionMode] = useState(false);

  const getStatusLabel = (status: OperationDetail["status"]): string => {
    return t(mapExecutionStatusText(status) as I18nSemanticKey);
  };

  // Backend-derived capability check. Missing allowed_actions (e.g. detail not
  // yet loaded) means no actions are offered by the client — backend still
  // enforces on request.
  const canDo = (action: string) =>
    Array.isArray(operation?.allowed_actions) && operation!.allowed_actions.includes(action);

  // Initial queue load on mount
  useEffect(() => { void refreshQueue(); }, []);

  useEffect(() => {
    if (queryOperationId) {
      setOperationId(queryOperationId);
      void fetchOperation(queryOperationId);
    }
    // Intentional: run only when queryOperationId changes
  }, [queryOperationId]);

  useEffect(() => {
    if (downtimeModalOpen) {
      void loadDowntimeReasons();
    }
  }, [downtimeModalOpen]);

  const isCanonicalOperationId = (value: string) => /^\d+$/.test(value.trim());

  const selectedQueueItem = operation
    ? queueItems.find((item) => item.operation_id === operation.id) ?? null
    : null;
  const claimState = selectedQueueItem?.claim.state ?? "none";
  const ownedClaimOperationId =
    queueItems.find((item) => item.claim.state === "mine")?.operation_id ?? null;
  const ownsAnotherClaim =
    ownedClaimOperationId !== null && ownedClaimOperationId !== operation?.id;
  const canClaimByStatus = operation
    ? isBackendClaimableQueueStatus(operation.status)
    : false;
  const canClaimCurrentOperation = canClaimByStatus && !ownsAnotherClaim;
  const canExecuteByClaim = claimState === "mine";
  const canReportProduction = canExecuteByClaim && canDo("report_production");
  const canPauseExecution = canExecuteByClaim && canDo("pause_execution");
  const canStartDowntime = canExecuteByClaim && canDo("start_downtime");
  const canCompleteExecution = canExecuteByClaim && canDo("complete_execution");
  const canResumeExecution = canExecuteByClaim && canDo("resume_execution");
  const canEndDowntimeAction = canExecuteByClaim && canDo("end_downtime");
  const canCloseOperation = canDo("close_operation") && operation?.closure_status === "OPEN";
  const canReopenOperation = canDo("reopen_operation") && operation?.closure_status === "CLOSED";
  // Release is only safe on PLANNED. On IN_PROGRESS / PAUSED / BLOCKED the
  // operation has active execution context and the operator cannot reclaim after
  // releasing, creating an unrecoverable dead-end. Backend enforces the same
  // rule; the frontend guard removes the affordance proactively.
  const canReleaseClaim = claimState === "mine" && operation?.status === "PLANNED";
  const canClockOnByStatus =
    operation?.status === "PLANNED";

  // Mode B = operator has claimed this operation, unless user explicitly
  // navigates back to the full selection surface.
  const isExecutionMode = claimState === "mine" && !forceSelectionMode;

  const [timerNowMs, setTimerNowMs] = useState<number>(Date.now());

  const formatDuration = (ms: number): string => {
    const totalSeconds = Math.max(0, Math.floor(ms / 1000));
    const hh = Math.floor(totalSeconds / 3600);
    const mm = Math.floor((totalSeconds % 3600) / 60);
    const ss = totalSeconds % 60;
    return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
  };

  useEffect(() => {
    if (!isExecutionMode || !operation?.actual_start) {
      return;
    }
    const id = window.setInterval(() => setTimerNowMs(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [isExecutionMode, operation?.actual_start]);

  const elapsedExecutionMs = useMemo(() => {
    if (!operation?.actual_start) return null;
    const startedAtMs = new Date(operation.actual_start).getTime();
    if (Number.isNaN(startedAtMs)) return null;
    if (operation.actual_end) {
      const endedAtMs = new Date(operation.actual_end).getTime();
      if (!Number.isNaN(endedAtMs)) {
        return Math.max(0, endedAtMs - startedAtMs);
      }
    }
    return Math.max(0, timerNowMs - startedAtMs);
  }, [operation?.actual_start, operation?.actual_end, timerNowMs]);

  const targetExecutionMs = useMemo(() => {
    if (!operation?.planned_start || !operation?.planned_end) return null;
    const plannedStartMs = new Date(operation.planned_start).getTime();
    const plannedEndMs = new Date(operation.planned_end).getTime();
    if (Number.isNaN(plannedStartMs) || Number.isNaN(plannedEndMs)) return null;
    if (plannedEndMs <= plannedStartMs) return null;
    return plannedEndMs - plannedStartMs;
  }, [operation?.planned_end, operation?.planned_start]);

  const overTargetMs = useMemo(() => {
    if (elapsedExecutionMs === null || targetExecutionMs === null) return null;
    return elapsedExecutionMs > targetExecutionMs
      ? elapsedExecutionMs - targetExecutionMs
      : null;
  }, [elapsedExecutionMs, targetExecutionMs]);

  const targetTimeLabel = useMemo(() => {
    if (targetExecutionMs === null) return t("station.timer.unavailable");
    return formatDuration(targetExecutionMs);
  }, [formatDuration, targetExecutionMs, t]);

  const pausedTotalMs = operation?.paused_total_ms ?? 0;
  const downtimeTotalMs = operation?.downtime_total_ms ?? 0;

  const guidanceMessage = useMemo(() => {
    if (operation?.closure_status === "CLOSED") {
      return t("station.closed.guidance");
    }
    if (!canExecuteByClaim) return t("station.claim.required");
    if (operation?.status === "BLOCKED" && operation.downtime_open) {
      return t("station.hint.nextAction.endDowntime");
    }
    if (operation?.status === "PAUSED") {
      return operation.downtime_open
        ? t("station.hint.nextAction.endDowntime")
        : t("station.hint.nextAction.resume");
    }
    if (operation?.status === "IN_PROGRESS") {
      return t("station.hint.nextAction.reportQty");
    }
    if (operation?.status === "PLANNED") {
      return t("station.hint.nextAction.clockOn");
    }
    if (operation?.status === "COMPLETED") {
      return t("station.completed.disabledNote");
    }
    if (operation?.status === "ABORTED") {
      return t("station.status.abortedHeading");
    }
    return "";
  }, [canExecuteByClaim, operation?.downtime_open, operation?.status, t]);

  const reportingHint = useMemo(() => {
    if (operation?.closure_status === "CLOSED") {
      return t("station.closed.reportingDisabled");
    }
    if (canReportProduction) return t("station.input.deltaHint");
    if (operation?.status === "BLOCKED" && operation.downtime_open) {
      return t("station.input.disabledHint.blocked");
    }
    if (operation?.status === "PAUSED") {
      return t("station.input.disabledHint.paused");
    }
    return t("station.completed.disabledNote");
  }, [canReportProduction, operation?.downtime_open, operation?.status, t]);

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

  const loadDowntimeReasons = async () => {
    setDowntimeReasonsLoading(true);
    try {
      const data = await fetchDowntimeReasons();
      setDowntimeReasons(data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("station.downtime.reason.loadFailed"));
      setDowntimeReasons([]);
    } finally {
      setDowntimeReasonsLoading(false);
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
      // Quantity fields are deltas for the *next* report, not cumulative totals —
      // reset to 0 whenever the selected operation changes.
      setGoodQty(0);
      setScrapQty(0);
      setSearchParams({ operationId: trimmedId });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("station.toast.loadOperationFailed"));
    } finally {
      setLoading(false);
    }
  };

  const selectQueueOperation = async (item: StationQueueItem) => {
    setQueueOverlayOpen(false);
    setForceSelectionMode(false);
    setOperationId(String(item.operation_id));
    setSearchParams({ operationId: String(item.operation_id) });
    await fetchOperation(String(item.operation_id));
  };

  const claimOperation = async () => {
    if (!operation) return;
    setClaimLoading(true);
    try {
      await stationApi.claim(operation.id, {});
      setForceSelectionMode(false);
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

  const backToSelection = () => {
    setQueueOverlayOpen(false);
    setForceSelectionMode(true);
  };

  const startOperation = async () => {
    if (!operation) return;
    setActionLoading(true);
    try {
      const data = await operationApi.start(operation.id, {
        operator_id: currentUser?.user_id ?? null,
      });
      toast.success(t("station.toast.clockedOn") + getStatusLabel(data.status));
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
    if (goodQty <= 0 && scrapQty <= 0) {
      toast.error(t("station.input.deltaHint"));
      return;
    }
    setActionLoading(true);
    try {
      const data = await operationApi.reportQuantity(operation.id, {
        good_qty: goodQty,
        scrap_qty: scrapQty,
        operator_id: null,
      });
      toast.success(t("station.toast.quantityReported") + getStatusLabel(data.status));
      setGoodQty(0);
      setScrapQty(0);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("station.toast.actionFailed"));
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
      await refreshQueue();
    }
  };

  const startDowntime = async (reasonCode: string, note: string) => {
    if (!operation) return;
    setDowntimeLoading(true);
    try {
      await operationApi.startDowntime(operation.id, { reason_code: reasonCode, note });
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

  const endDowntime = async () => {
    if (!operation) return;
    setDowntimeLoading(true);
    try {
      await operationApi.endDowntime(operation.id, {});
      toast.success(t("station.toast.downtimeEnded"));
      await fetchOperation(String(operation.id));
      await refreshQueue();
    } catch (err) {
      let msg = t("station.toast.downtimeEndFailed");
      if (err instanceof HttpError && err.status === 409 && typeof err.detail === "string") {
        const code = err.detail.trim();
        if (code.startsWith("STATE_")) msg = t(`station.reject.${code}` as never);
      } else if (err instanceof HttpError && err.status === 403) {
        msg = t("station.claim.required");
      }
      toast.error(msg);
    } finally {
      setDowntimeLoading(false);
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
      toast.success(t("station.toast.paused") + getStatusLabel(data.status));
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
      toast.success(t("station.toast.resumed") + getStatusLabel(data.status));
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
      toast.success(t("station.toast.clockedOff") + getStatusLabel(data.status));
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

  const closeOperation = async () => {
    if (!operation) return;
    const confirmed = window.confirm(t("station.confirm.closeOperation"));
    if (!confirmed) return;
    setActionLoading(true);
    try {
      const data = await operationApi.close(operation.id, {});
      toast.success(t("station.toast.closed") + getStatusLabel(data.status));
    } catch (err) {
      if (err instanceof HttpError && err.status === 409) {
        const key = rejectReasonKey(err.detail);
        toast.error(key ? t(key as never) : t("station.toast.closeFailed"));
      } else {
        toast.error(err instanceof Error ? err.message : t("station.toast.closeFailed"));
      }
    } finally {
      setActionLoading(false);
      await fetchOperation(String(operation.id));
      await refreshQueue();
    }
  };

  const reopenOperation = async (reason: string) => {
    if (!operation) return;
    setActionLoading(true);
    try {
      const data = await operationApi.reopen(operation.id, { reason });
      toast.success(t("station.toast.reopened") + getStatusLabel(data.status));
      setReopenModalOpen(false);
    } catch (err) {
      if (err instanceof HttpError && err.status === 409) {
        const key = rejectReasonKey(err.detail);
        toast.error(key ? t(key as never) : t("station.toast.reopenFailed"));
      } else if (err instanceof HttpError && typeof err.detail === "string" && err.detail === "REOPEN_REASON_REQUIRED") {
        toast.error(t("station.reopen.reason.required"));
      } else {
        toast.error(err instanceof Error ? err.message : t("station.toast.reopenFailed"));
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
        <MockWarningBanner phase="PARTIAL" note={t("screenStatus.banner.deprecation.body" as any)} />

        <div className="flex-1 overflow-auto p-4 max-w-2xl mx-auto w-full">
          {/* Selected operation — awaiting claim */}
          {operation && claimState === "none" && canClaimByStatus && (
            <div className="mb-4 bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center justify-between gap-4">
              <div className="min-w-0">
                <p className="font-semibold text-gray-900 truncate">{operation.name}</p>
                <div className="mt-1">
                  <StatusBadge
                    variant={mapExecutionStatusBadgeVariant(operation.status)}
                    size="sm"
                  >
                    {getStatusLabel(operation.status)}
                  </StatusBadge>
                </div>
                {ownsAnotherClaim && (
                  <p className="mt-2 text-xs text-amber-700">
                    {t("station.claim.singleActiveHint")}
                  </p>
                )}
              </div>
              <button
                onClick={() => void claimOperation()}
                disabled={claimLoading || !canClaimCurrentOperation}
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
                filter={queueFilter}
                onFilterChange={setQueueFilter}
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

  const remainingQty = Math.max(0, operation.quantity - operation.completed_qty);

  return (
    <div className="h-full flex flex-col bg-gray-50 min-h-0 overflow-hidden">
      {/* Compact single-row header */}
      <div className="flex flex-col gap-3 px-3 py-3 bg-white border-b shadow-sm shrink-0 sm:px-4 lg:flex-row lg:items-center lg:justify-between">
        {/* Context row: station / operation name / status badges */}
        <div className="flex min-w-0 flex-wrap items-center gap-2 sm:gap-3">
          <span className="text-sm text-gray-500 shrink-0 whitespace-nowrap">
            {t("station.workstation.label")} {stationScope}
          </span>
          <span className="shrink-0 h-5 w-px bg-gray-300" aria-hidden="true" />
          <span className="font-bold text-base text-gray-900 truncate">{operation.name}</span>
          <StatusBadge
            variant={mapExecutionStatusBadgeVariant(operation.status)}
            size="sm"
          >
            {getStatusLabel(operation.status)}
          </StatusBadge>
          {operation.closure_status === "CLOSED" && (
            <span className="shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-900 text-white text-xs font-semibold">
              {t("station.closure.closedBadge")}
            </span>
          )}
          {operation.downtime_open && (
            <span className="shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-xs font-semibold">
              ● {t("station.downtime.active.banner")}
            </span>
          )}
        </div>
        {/* Control row: claim badge + nav/view controls + release command */}
        <div className="flex w-full flex-wrap items-center gap-2 sm:gap-3 shrink-0 lg:w-auto lg:flex-nowrap lg:justify-end">
          {/* Claim ownership indicator */}
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-green-100 text-green-800 text-sm font-semibold order-first sm:order-none">
            {t("station.claim.ownedBadge")}
          </span>
          {/* Nav / view controls */}
          <button
            onClick={backToSelection}
            className="h-10 sm:h-11 px-3 sm:px-4 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 active:scale-95 transition flex items-center gap-1.5"
          >
            <ArrowLeft className="w-4 h-4 shrink-0" />
            {t("station.action.backToSelection")}
          </button>
          <button
            onClick={() => void refreshQueue()}
            disabled={queueLoading}
            className="h-10 sm:h-11 px-3 sm:px-4 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 active:scale-95 transition disabled:opacity-50 flex items-center gap-1.5"
          >
            <RefreshCw className="w-4 h-4 shrink-0" />
            {t("station.action.refresh")}
          </button>
          <button
            onClick={() => setQueueOverlayOpen((prev) => !prev)}
            className="h-10 sm:h-11 px-3 sm:px-4 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 active:scale-95 transition flex items-center gap-1.5"
          >
            {t("station.tab.queue")}
            <ChevronDown className="w-4 h-4 shrink-0" />
          </button>
          {/* Divider before command-bearing Release */}
          <span className="shrink-0 h-7 w-px bg-gray-200" aria-hidden="true" />
          {/* Release — command-bearing, destructive. Disabled logic is backend-derived. */}
          <button
            onClick={() => void releaseClaim()}
            disabled={claimLoading || !canReleaseClaim}
            className="h-10 sm:h-11 px-3 sm:px-4 border border-red-200 rounded-lg text-sm text-red-600 hover:bg-red-50 active:scale-95 transition disabled:opacity-40 disabled:cursor-not-allowed"
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
            className="absolute top-16 left-2 right-2 sm:left-auto sm:right-4 w-auto sm:w-80 bg-white rounded-xl shadow-2xl border p-4 max-h-[70vh] overflow-auto"
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
              filter={queueFilter}
              onFilterChange={setQueueFilter}
              onSelect={(item) => void selectQueueOperation(item)}
            />
          </div>
        </div>
      )}

      {/* Compatibility path notice — always visible in execution mode */}
      <MockWarningBanner phase="PARTIAL" note={t("screenStatus.banner.deprecation.body" as any)} />

      {/* Execution body — must not scroll on iPad landscape */}
      <div className="flex-1 min-h-0 flex flex-col p-3 sm:p-4 gap-3 overflow-y-auto overflow-x-hidden overscroll-contain bg-slate-50">
        {/* Hero summary card */}
        <section className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm sm:p-5 md:p-6 shrink-0">
          <div className="mb-4 border-b border-slate-200 pb-4">
            <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm sm:text-base md:text-xl">
              <span className="whitespace-nowrap">
                <span className="text-slate-500">{t("station.context.workOrder")}:</span>{" "}
                <span className="font-semibold text-slate-900">{operation.work_order_number}</span>
              </span>
              <span className="whitespace-nowrap">
                <span className="text-slate-500">{t("station.context.productionOrder")}:</span>{" "}
                <span className="font-semibold text-slate-900">{operation.production_order_number}</span>
              </span>
              <span className="whitespace-nowrap">
                <span className="text-slate-500">{t("station.context.startedAt")}:</span>{" "}
                <span className="font-semibold text-slate-900">
                  {operation.actual_start
                    ? new Date(operation.actual_start).toLocaleString()
                    : t("station.context.notStarted")}
                </span>
              </span>
            </div>
          </div>

          <div className="grid gap-3 md:gap-4 lg:grid-cols-[1fr_1fr_1fr_minmax(280px,360px)]">
            <KpiCard label={t("station.qty.target")} value={operation.quantity} />
            <KpiCard label={t("station.qty.completed")} value={operation.completed_qty} />
            <KpiCard label={t("station.qty.remaining")} value={remainingQty} highlight />
            <TimeCluster
              targetTime={targetTimeLabel}
              elapsed={elapsedExecutionMs !== null ? formatDuration(elapsedExecutionMs) : t("station.timer.unavailable")}
              overBy={overTargetMs !== null ? formatDuration(overTargetMs) : null}
            />
          </div>

          <div className="mt-4 flex flex-wrap gap-x-4 sm:gap-x-8 gap-y-2 text-sm sm:text-base md:text-xl text-slate-700">
            <span><span className="text-slate-500">{t("station.qty.totalGood")}</span>: <span className="font-semibold text-emerald-700">{operation.good_qty}</span></span>
            <span><span className="text-slate-500">{t("station.qty.totalScrap")}</span>: <span className="font-semibold text-rose-600">{operation.scrap_qty}</span></span>
            {(operation.status === "PAUSED" || operation.status === "BLOCKED") && (
              <span>
                <span className="text-slate-500">{t("station.timer.pausedTotal")}</span>: {formatDuration(pausedTotalMs)}
              </span>
            )}
            {(operation.status === "PAUSED" || operation.status === "BLOCKED") && (
              <span>
                <span className="text-slate-500">{t("station.timer.downtimeTotal")}</span>: {formatDuration(downtimeTotalMs)}
              </span>
            )}
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <div className={`rounded-2xl border px-4 py-3 ${operation.closure_status === "CLOSED" ? "border-slate-300 bg-slate-100" : "border-slate-200 bg-slate-50"}`}>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t("station.closure.sectionTitle")}</p>
              <p className="mt-1 text-sm font-semibold text-slate-900">{t(operation.closure_status === "CLOSED" ? "station.closure.closedState" : "station.closure.openState")}</p>
              <p className="mt-1 text-xs text-slate-600">
                {t(operation.closure_status === "CLOSED" ? "station.closed.executionBlocked" : "station.closure.openHelper")}
              </p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t("station.reopen.audit.title")}</p>
              <p className="mt-1 text-sm text-slate-900">
                {t("station.reopen.audit.count", { count: operation.reopen_count ?? 0 })}
              </p>
              {operation.last_closed_at && (
                <p className="mt-1 text-xs text-slate-600">
                  {t("station.reopen.audit.lastClosed", {
                    at: new Date(operation.last_closed_at).toLocaleString(),
                    by: operation.last_closed_by ?? "-",
                  })}
                </p>
              )}
              {operation.last_reopened_at && (
                <p className="mt-1 text-xs text-slate-600">
                  {t("station.reopen.audit.lastReopened", {
                    at: new Date(operation.last_reopened_at).toLocaleString(),
                    by: operation.last_reopened_by ?? "-",
                  })}
                </p>
              )}
            </div>
          </div>
        </section>

        {/* Report / input block */}
        <section className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm sm:p-5 md:p-6 shrink-0">
          <p className="text-base font-semibold uppercase tracking-wide text-slate-500 md:text-lg mb-2">
            {t("station.block.inputReporting")}
          </p>
          <p className="mt-2 text-sm sm:text-base text-slate-600 md:text-xl mb-5">{reportingHint}</p>
          <div className="grid gap-5 lg:grid-cols-2 mb-6">
            <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
              <Stepper
                label={t("station.input.goodQtyDelta")}
                value={goodQty}
                onChange={setGoodQty}
                labelClassName="text-emerald-700"
                disabled={!canReportProduction}
                quickAddValues={[1, 5, 10, 20]}
                quickAddTone="good"
                onReset={() => setGoodQty(0)}
              />
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
              <Stepper
                label={t("station.input.scrapQtyDelta")}
                value={scrapQty}
                onChange={setScrapQty}
                labelClassName="text-amber-700"
                disabled={!canReportProduction}
                quickAddValues={[1, 2, 5]}
                quickAddTone="scrap"
                onReset={() => setScrapQty(0)}
              />
            </div>
          </div>
          <button
            onClick={() => void reportQuantity()}
            disabled={actionLoading || !canReportProduction}
            className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-md transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-blue-600 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
          >
            {t("station.action.reportQty")}
          </button>
        </section>

        {(canCloseOperation || canReopenOperation || operation.closure_status === "CLOSED") && (
          <section className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm sm:p-5 md:p-6 shrink-0">
            <p className="text-base font-semibold uppercase tracking-wide text-slate-500 md:text-lg mb-2">
              {t("station.closure.sectionTitle")}
            </p>
            <p className="mt-2 text-sm sm:text-base text-slate-600 md:text-xl mb-5">
              {t(operation.closure_status === "CLOSED" ? "station.closed.secondaryHint" : "station.closure.secondaryHint")}
            </p>
            <div className="flex flex-col gap-3">
              {canCloseOperation && (
                <button
                  onClick={() => void closeOperation()}
                  disabled={actionLoading || !canCloseOperation}
                  className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl border-2 border-slate-400 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                >
                  {t("station.action.closeOperation")}
                </button>
              )}
              {canReopenOperation && (
                <button
                  onClick={() => setReopenModalOpen(true)}
                  disabled={actionLoading || !canReopenOperation}
                  className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {t("station.action.reopen")}
                </button>
              )}
            </div>
          </section>
        )}

        {/* Guidance callout */}
        {guidanceMessage && (
          <div className="shrink-0 flex items-start gap-3 rounded-2xl border border-blue-200 bg-blue-50 px-4 py-3 sm:px-5">
            <Info className="mt-0.5 h-5 w-5 shrink-0 text-blue-500 sm:h-6 sm:w-6" aria-hidden="true" />
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-blue-700">{t("station.block.guidance")}</p>
              <p className="mt-1 text-sm text-blue-900 sm:text-base md:text-xl leading-snug">{guidanceMessage}</p>
            </div>
          </div>
        )}

        {/* Primary Action Zone */}
        <section className="shrink-0 flex flex-col gap-2 pb-1">
          {operation.status === "PLANNED" && (
            <button
              onClick={() => void startOperation()}
              disabled={actionLoading || operation.closure_status === "CLOSED" || !canExecuteByClaim || !canDo("start_execution")}
              className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold tracking-wide bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl"
            >
              {t("station.action.clockOn")}
            </button>
          )}

          {operation.status === "IN_PROGRESS" && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => void pauseOperation()}
                  disabled={actionLoading || operation.closure_status === "CLOSED" || !canPauseExecution}
                  className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-amber-400 text-slate-900 hover:bg-amber-500 disabled:opacity-50"
                >
                  {t("station.action.pause")}
                </button>
                <button
                  onClick={() => setDowntimeModalOpen(true)}
                  disabled={downtimeLoading || operation.closure_status === "CLOSED" || !canStartDowntime}
                  className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-slate-600 text-white hover:bg-slate-700 disabled:opacity-50"
                >
                  {t("station.action.startDowntime")}
                </button>
              </div>
              {canCompleteExecution && (
                <button
                  onClick={() => void completeOperation()}
                  disabled={actionLoading || operation.closure_status === "CLOSED" || !canCompleteExecution}
                  className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl border-2 border-amber-500 bg-white text-amber-700 hover:bg-amber-50 disabled:opacity-50"
                >
                  {t("station.action.completeOperation")}
                </button>
              )}
            </>
          )}

          {operation.status === "PAUSED" && (
            <>
              {!operation.downtime_open ? (
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => void resumeOperation()}
                    disabled={actionLoading || operation.closure_status === "CLOSED" || !canResumeExecution}
                    className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
                  >
                    {t("station.action.resume")}
                  </button>
                  <button
                    onClick={() => setDowntimeModalOpen(true)}
                    disabled={downtimeLoading || operation.closure_status === "CLOSED" || !canStartDowntime}
                    className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-slate-600 text-white hover:bg-slate-700 disabled:opacity-50"
                  >
                    {t("station.action.startDowntime")}
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => void endDowntime()}
                  disabled={downtimeLoading || operation.closure_status === "CLOSED" || !canEndDowntimeAction}
                  className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
                >
                  {t("station.action.endDowntime")}
                </button>
              )}
            </>
          )}

          {operation.status === "BLOCKED" && operation.downtime_open && (
            <button
              onClick={() => void endDowntime()}
              disabled={downtimeLoading || operation.closure_status === "CLOSED" || !canEndDowntimeAction}
              className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {t("station.action.endDowntime")}
            </button>
          )}
        </section>

        <ReopenOperationModal
          open={reopenModalOpen}
          onClose={() => setReopenModalOpen(false)}
          onSubmit={reopenOperation}
          loading={actionLoading}
        />

        <StartDowntimeModal
          open={downtimeModalOpen}
          onClose={() => setDowntimeModalOpen(false)}
          onSubmit={startDowntime}
          loading={downtimeLoading}
          reasons={downtimeReasons}
          reasonsLoading={downtimeReasonsLoading}
        />
      </div>
    </div>
  );
}

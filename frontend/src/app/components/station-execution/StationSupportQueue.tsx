import { Lock } from "lucide-react";
import { StatusBadge } from "@/app/components";
import { mapExecutionStatusBadgeVariant, mapExecutionStatusText, type StationQueueItem } from "@/app/api";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

interface StationSupportQueueProps {
  items: StationQueueItem[];
  loading: boolean;
  activeOperationId?: number;
  maxItems?: number;
  onSelect: (item: StationQueueItem) => void;
  onViewFullQueue: () => void;
}

export function StationSupportQueue({
  items,
  loading,
  activeOperationId,
  maxItems = 3,
  onSelect,
  onViewFullQueue,
}: StationSupportQueueProps) {
  const { t } = useI18n();

  if (loading) {
    return <p className="py-2 text-xs text-slate-500">{t("station.loading")}</p>;
  }

  const activeItem =
    typeof activeOperationId === "number"
      ? items.find((item) => item.operation_id === activeOperationId) ?? null
      : null;

  const nextItems = items.filter((item) => item.operation_id !== activeOperationId);
  const compactItems = activeItem
    ? [activeItem, ...nextItems].slice(0, maxItems)
    : items.slice(0, maxItems);

  const visibleCount = compactItems.length;

  return (
    <div className="flex flex-col gap-2.5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-base font-semibold text-slate-900">{t("station.supportQueue.title")}</p>
        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
          {t("station.supportQueue.totalQueued", { count: items.length })}
        </span>
      </div>

      {items.length === 0 ? (
        <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
          {t("station.supportQueue.noOtherQueuedWork")}
        </p>
      ) : (
        <>
          <p className="text-xs text-slate-500">
            {t("station.supportQueue.showingNext", { count: visibleCount })}
          </p>
          <div className="flex flex-col gap-2">
            {compactItems.map((item) => {
              const active = activeOperationId === item.operation_id;
              const lockedByOther = item.ownership?.owner_state === "other" && item.ownership?.has_open_session === true;
              const sessionHint =
                item.ownership?.owner_state === "mine" && item.ownership?.has_open_session
                  ? t("station.ownership.ownedBadge")
                  : item.ownership?.owner_state === "other" && item.ownership?.has_open_session
                  ? t("station.queue.ownedByOther")
                  : null;

              return (
                <button
                  key={item.operation_id}
                  type="button"
                  disabled={lockedByOther}
                  onClick={() => onSelect(item)}
                  className={`w-full rounded-lg border px-3 py-2 text-left transition ${
                    active
                      ? "border-blue-300 bg-blue-50"
                      : lockedByOther
                      ? "cursor-not-allowed border-slate-200 bg-slate-50 opacity-70"
                      : "border-slate-200 bg-white hover:border-blue-200 hover:bg-blue-50"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex min-w-0 items-center gap-1.5">
                      {lockedByOther ? <Lock className="h-3.5 w-3.5 shrink-0 text-orange-500" /> : null}
                      <span className="truncate text-sm font-medium text-slate-900">{item.name}</span>
                    </div>
                    <StatusBadge variant={mapExecutionStatusBadgeVariant(item.status)} size="sm">
                      {t(mapExecutionStatusText(item.status) as I18nSemanticKey)}
                    </StatusBadge>
                  </div>
                  <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
                    <span>{item.operation_number}</span>
                    {item.downtime_open ? (
                      <span className="rounded-full bg-red-100 px-2 py-0.5 font-medium text-red-700">
                        {t("station.queue.downtimeActive")}
                      </span>
                    ) : null}
                    {sessionHint ? <span className="text-blue-700">{sessionHint}</span> : null}
                  </div>
                </button>
              );
            })}
          </div>
        </>
      )}

      <button
        type="button"
        onClick={onViewFullQueue}
        className="min-h-10 self-start rounded-md border border-slate-300 bg-white px-3 text-xs font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95"
      >
        {t("station.supportQueue.viewFullQueue")}
      </button>
    </div>
  );
}
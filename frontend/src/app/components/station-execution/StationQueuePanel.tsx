import { useMemo } from "react";
import type { StationQueueItem } from "@/app/api";
import { useI18n } from "@/app/i18n";
import { QueueFilterBar, type QueueFilter } from "./QueueFilterBar";
import { QueueOperationCard } from "./QueueOperationCard";

interface StationQueuePanelProps {
  items: StationQueueItem[];
  loading: boolean;
  activeOperationId?: number;
  filter: QueueFilter;
  onFilterChange: (filter: QueueFilter) => void;
  onSelect: (item: StationQueueItem) => void;
}

export const isBackendClaimableQueueStatus = (status: StationQueueItem["status"]): boolean =>
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

export function StationQueuePanel({
  items,
  loading,
  activeOperationId,
  filter,
  onFilterChange,
  onSelect,
}: StationQueuePanelProps) {
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
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
        <div className="rounded-lg border bg-white px-3 py-2.5">
          <p className="text-xs sm:text-sm text-gray-500">{t("station.queue.summary.ready")}</p>
          <p className="text-sm sm:text-base font-semibold text-gray-900">{summary.ready}</p>
        </div>
        <div className="rounded-lg border bg-white px-3 py-2.5">
          <p className="text-xs sm:text-sm text-gray-500">{t("station.queue.summary.paused")}</p>
          <p className="text-sm sm:text-base font-semibold text-amber-700">{summary.paused}</p>
        </div>
        <div className="rounded-lg border bg-white px-3 py-2.5">
          <p className="text-xs sm:text-sm text-gray-500">{t("station.queue.summary.blocked")}</p>
          <p className="text-sm sm:text-base font-semibold text-red-700">{summary.blocked}</p>
        </div>
        <div className="rounded-lg border bg-white px-3 py-2.5">
          <p className="text-xs sm:text-sm text-gray-500">{t("station.queue.summary.downtime")}</p>
          <p className="text-sm sm:text-base font-semibold text-red-700">{summary.downtime}</p>
        </div>
        <div className="rounded-lg border bg-white px-3 py-2.5">
          <p className="text-xs sm:text-sm text-gray-500">{t("station.queue.summary.mine")}</p>
          <p className="text-sm sm:text-base font-semibold text-blue-700">{summary.mine}</p>
        </div>
      </div>

      <QueueFilterBar filter={filter} onFilterChange={onFilterChange} />

      {selectedIsFilteredOut && (
        <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          {t("station.queue.selectedOutsideFilter")}
        </p>
      )}

      {filteredItems.length === 0 && (
        <p className="text-sm text-gray-500 py-6 text-center">{t("station.queue.emptyFiltered")}</p>
      )}

      {filteredItems.map((item) => (
        <QueueOperationCard
          key={item.operation_id}
          item={item}
          active={activeOperationId === item.operation_id}
          hasMineClaim={hasMineClaim}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}

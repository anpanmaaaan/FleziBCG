import { useI18n } from "@/app/i18n";

export type QueueFilter = "all" | "mine" | "ready" | "paused" | "blocked" | "downtime";

interface QueueFilterBarProps {
  filter: QueueFilter;
  onFilterChange: (filter: QueueFilter) => void;
}

export function QueueFilterBar({ filter, onFilterChange }: QueueFilterBarProps) {
  const { t } = useI18n();

  const filterDefs: { key: QueueFilter; label: string }[] = [
    { key: "all", label: t("station.queue.filter.all") },
    { key: "mine", label: t("station.queue.filter.mine") },
    { key: "ready", label: t("station.queue.filter.ready") },
    { key: "paused", label: t("station.queue.filter.paused") },
    { key: "blocked", label: t("station.queue.filter.blocked") },
    { key: "downtime", label: t("station.queue.filter.downtime") },
  ];

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-1">
      {filterDefs.map((entry) => {
        const active = filter === entry.key;
        return (
          <button
            key={entry.key}
            type="button"
            onClick={() => onFilterChange(entry.key)}
            className={`shrink-0 px-3 py-2 min-h-[36px] rounded-full text-xs font-semibold border transition active:scale-95 ${
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
  );
}

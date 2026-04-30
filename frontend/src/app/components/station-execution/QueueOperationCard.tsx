import { Lock } from "lucide-react";
import { StatusBadge } from "@/app/components";
import { mapExecutionStatusBadgeVariant, mapExecutionStatusText, type StationQueueItem } from "@/app/api";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

const isBackendClaimableQueueStatus = (status: StationQueueItem["status"]): boolean =>
  status === "PLANNED" || status === "IN_PROGRESS";

interface QueueOperationCardProps {
  item: StationQueueItem;
  active: boolean;
  hasMineClaim: boolean;
  onSelect: (item: StationQueueItem) => void;
}

export function QueueOperationCard({ item, active, hasMineClaim, onSelect }: QueueOperationCardProps) {
  const { t } = useI18n();

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
}

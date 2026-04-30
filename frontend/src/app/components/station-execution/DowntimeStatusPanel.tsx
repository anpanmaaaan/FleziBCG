import { useI18n } from "@/app/i18n";

export interface DowntimeStatusPanelProps {
  downtimeOpen: boolean;
}

export function DowntimeStatusPanel({ downtimeOpen }: DowntimeStatusPanelProps) {
  const { t } = useI18n();

  if (!downtimeOpen) {
    return null;
  }

  return (
    <span className="shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-xs font-semibold">
      ● {t("station.downtime.active.banner")}
    </span>
  );
}

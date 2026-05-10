import type { ReactNode } from "react";
import { AlertTriangle, Info } from "lucide-react";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

export type StationAndonSeverity = "info" | "warning" | "danger";

interface StationAndonBannerProps {
  severity: StationAndonSeverity;
  titleKey: string;
  messageKey: string;
  recoveryKey?: string;
  live?: boolean;
  actionArea?: ReactNode;
}

export function StationAndonBanner({
  severity,
  titleKey,
  messageKey,
  recoveryKey,
  live = false,
  actionArea,
}: StationAndonBannerProps) {
  const { t } = useI18n();

  const palette =
    severity === "danger"
      ? "border-red-200 bg-red-50 text-red-950"
      : severity === "warning"
      ? "border-amber-200 bg-amber-50 text-amber-950"
      : "border-blue-200 bg-blue-50 text-blue-950";

  const icon =
    severity === "info" ? (
      <Info className="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-600" aria-hidden="true" />
    ) : (
      <AlertTriangle
        className={`mt-0.5 h-5 w-5 flex-shrink-0 ${severity === "danger" ? "text-red-600" : "text-amber-600"}`}
        aria-hidden="true"
      />
    );

  return (
    <div
      className={`rounded-2xl border px-4 py-3 ${palette}`}
      role={live ? "alert" : "status"}
      aria-live={live ? "assertive" : "polite"}
    >
      <div className="flex items-start gap-3">
        {icon}
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide">
            {t(titleKey as I18nSemanticKey)}
          </p>
          <p className="mt-1 text-sm leading-snug sm:text-base">
            {t(messageKey as I18nSemanticKey)}
          </p>
          {recoveryKey ? (
            <p className="mt-1 text-xs font-medium sm:text-sm">
              {t(recoveryKey as I18nSemanticKey)}
            </p>
          ) : null}
        </div>
      </div>
      {actionArea ? <div className="mt-3">{actionArea}</div> : null}
    </div>
  );
}
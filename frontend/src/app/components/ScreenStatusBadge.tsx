import { useI18n } from "@/app/i18n";
import type { ScreenPhase } from "@/app/screenStatus";

interface ScreenStatusBadgeProps {
  phase: ScreenPhase;
  size?: "sm" | "md";
  className?: string;
}

const PHASE_STYLES: Record<ScreenPhase, string> = {
  CONNECTED: "bg-green-100 text-green-800 border-green-200",
  PARTIAL:   "bg-blue-100 text-blue-800 border-blue-200",
  MOCK:      "bg-amber-100 text-amber-800 border-amber-200",
  SHELL:     "bg-gray-100 text-gray-600 border-gray-200",
  FUTURE:    "bg-slate-100 text-slate-600 border-slate-200",
  DISABLED:  "bg-gray-100 text-gray-400 border-gray-200",
  UNKNOWN:   "bg-gray-100 text-gray-500 border-gray-200",
};

const PHASE_I18N_KEY: Record<ScreenPhase, `screenStatus.badge.${string}`> = {
  CONNECTED: "screenStatus.badge.connected",
  PARTIAL:   "screenStatus.badge.partial",
  MOCK:      "screenStatus.badge.mock",
  SHELL:     "screenStatus.badge.shell",
  FUTURE:    "screenStatus.badge.future",
  DISABLED:  "screenStatus.badge.disabled",
  UNKNOWN:   "screenStatus.badge.unknown",
} as const;

export function ScreenStatusBadge({ phase, size = "sm", className = "" }: ScreenStatusBadgeProps) {
  const { t } = useI18n();

  const sizeClass = size === "sm"
    ? "px-1.5 py-0.5 text-xs"
    : "px-2 py-1 text-sm";

  return (
    <span
      className={`inline-flex items-center font-medium rounded border ${PHASE_STYLES[phase]} ${sizeClass} ${className}`}
      aria-label={`Screen status: ${phase}`}
    >
      {t(PHASE_I18N_KEY[phase])}
    </span>
  );
}

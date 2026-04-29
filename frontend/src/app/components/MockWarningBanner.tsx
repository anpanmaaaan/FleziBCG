import { useState } from "react";
import { AlertTriangle, Info, X } from "lucide-react";
import { useI18n } from "@/app/i18n";
import type { ScreenPhase } from "@/app/screenStatus";

interface BannerConfig {
  wrapperClass: string;
  iconClass: string;
  Icon: React.ComponentType<{ className?: string }>;
  titleKey: `screenStatus.banner.${string}`;
  bodyKey: `screenStatus.banner.${string}`;
}

const PHASE_CONFIG: Partial<Record<ScreenPhase, BannerConfig>> = {
  MOCK: {
    wrapperClass: "bg-amber-50 border-amber-300 text-amber-900",
    iconClass:    "text-amber-500",
    Icon:         AlertTriangle,
    titleKey:     "screenStatus.banner.mock.title",
    bodyKey:      "screenStatus.banner.mock.body",
  },
  PARTIAL: {
    wrapperClass: "bg-blue-50 border-blue-300 text-blue-900",
    iconClass:    "text-blue-500",
    Icon:         Info,
    titleKey:     "screenStatus.banner.partial.title",
    bodyKey:      "screenStatus.banner.partial.body",
  },
  FUTURE: {
    wrapperClass: "bg-slate-50 border-slate-300 text-slate-700",
    iconClass:    "text-slate-400",
    Icon:         Info,
    titleKey:     "screenStatus.banner.future.title",
    bodyKey:      "screenStatus.banner.future.body",
  },
  SHELL: {
    wrapperClass: "bg-slate-50 border-slate-300 text-slate-700",
    iconClass:    "text-slate-400",
    Icon:         Info,
    titleKey:     "screenStatus.banner.shell.title",
    bodyKey:      "screenStatus.banner.shell.body",
  },
  DISABLED: {
    wrapperClass: "bg-gray-50 border-gray-300 text-gray-600",
    iconClass:    "text-gray-400",
    Icon:         Info,
    titleKey:     "screenStatus.banner.shell.title",
    bodyKey:      "screenStatus.banner.shell.body",
  },
};

interface MockWarningBannerProps {
  phase: ScreenPhase;
  /** Optional extra note appended after the body text */
  note?: string;
}

export function MockWarningBanner({ phase, note }: MockWarningBannerProps) {
  const { t } = useI18n();
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;
  if (phase === "CONNECTED" || phase === "UNKNOWN") return null;

  const config = PHASE_CONFIG[phase];
  if (!config) return null;

  const { Icon } = config;

  return (
    <div
      className={`flex items-start gap-3 border-b px-4 py-3 shrink-0 ${config.wrapperClass}`}
      role="alert"
    >
      <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${config.iconClass}`} aria-hidden="true" />
      <div className="flex-1 min-w-0">
        <span className="font-semibold text-sm">{t(config.titleKey)}</span>
        <span className="text-sm"> — {t(config.bodyKey)}</span>
        {note && <span className="text-sm"> {note}</span>}
      </div>
      <button
        type="button"
        onClick={() => setDismissed(true)}
        className="shrink-0 p-1 rounded hover:bg-black/10 transition-colors"
        aria-label="Dismiss"
      >
        <X className="w-3.5 h-3.5" aria-hidden="true" />
      </button>
    </div>
  );
}

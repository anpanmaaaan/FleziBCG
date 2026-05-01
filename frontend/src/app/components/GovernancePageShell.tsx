import { ReactNode } from "react";
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import type { ScreenPhase } from "@/app/screenStatus";

interface GovernancePageShellProps {
  /** Page title */
  title: string;
  /** Optional page subtitle/description */
  subtitle?: string;
  /** Screen phase for status badge (SHELL, MOCK, PARTIAL, CONNECTED) */
  phase: ScreenPhase;
  /** Optional note appended to MockWarningBanner */
  bannerNote?: string;
  /** Optional action buttons or controls (rendered right of header) */
  actions?: ReactNode;
  /** Main content area */
  children: ReactNode;
  /** Optional className for the wrapper div */
  className?: string;
}

/**
 * GovernancePageShell — consistent layout for governance/admin screens.
 * 
 * Provides:
 * - MockWarningBanner disclosure at top
 * - Standardized header with title, subtitle, phase badge
 * - Main content area
 * - Optional action buttons
 * 
 * Governance & Admin screens must preserve:
 * - Backend truth boundaries (no fake governance invented on FE)
 * - Shell/mock disclosure visibility
 * - Disabled state for unsupported backend actions
 */
export function GovernancePageShell({
  title,
  subtitle,
  phase,
  bannerNote,
  actions,
  children,
  className = "",
}: GovernancePageShellProps) {
  return (
    <div className={`h-full flex flex-col bg-white ${className}`}>
      <MockWarningBanner phase={phase} note={bannerNote} />

      <div className="flex-1 flex flex-col p-6">
        {/* Page Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between mb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
              <ScreenStatusBadge phase={phase} />
            </div>
            {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">{children}</div>
      </div>
    </div>
  );
}

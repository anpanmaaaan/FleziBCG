import { useLocation } from "react-router";
import { MockWarningBanner } from "./MockWarningBanner";
import { ScreenStatusBadge } from "./ScreenStatusBadge";
import {
  type ScreenPhase,
  getScreenStatusMatchByRoute,
  isFutureLikeStatus,
  isMockLikeStatus,
} from "@/app/screenStatus";

const BANNER_SUPPRESSED_SCREEN_IDS = new Set<string>([
  "oeeDeepDive",
  "stationExecution",
]);

const UNKNOWN_STATUS = {
  routePattern: "",
  phase: "UNKNOWN" as ScreenPhase,
  dataSource: "NONE" as const,
};

export function RouteStatusBanner() {
  const location = useLocation();
  const statusMatch = getScreenStatusMatchByRoute(location.pathname);
  const statusEntry = statusMatch?.entry ?? UNKNOWN_STATUS;

  const shouldShowGlobalBanner =
    !BANNER_SUPPRESSED_SCREEN_IDS.has(statusMatch?.screenId ?? "") &&
    (isMockLikeStatus(statusEntry.phase) ||
      isFutureLikeStatus(statusEntry.phase) ||
      statusEntry.phase === "PARTIAL");

  return (
    <>
      <div className="flex justify-end border-b border-gray-200 bg-slate-50 px-6 py-2">
        <ScreenStatusBadge phase={statusEntry.phase} size="sm" />
      </div>
      {shouldShowGlobalBanner && (
        <MockWarningBanner phase={statusEntry.phase} note={statusEntry.notes} />
      )}
    </>
  );
}

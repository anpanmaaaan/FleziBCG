// Station Session — PARTIAL (backend-connected)
// Shows current session state from GET /v1/station/sessions/current.
// Session truth is managed by the backend execution system.

import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { stationApi } from "@/app/api/stationApi";
import type { StationSessionItem } from "@/app/api/stationApi";
import {
  normalizeStationCommandError,
  type StationCommandErrorMessage,
} from "@/app/components/station-execution/stationCommandErrorMessages";
import { OpenSessionPanel } from "@/app/components/station-execution/OpenSessionPanel";
import { IdentifyOperatorPanel } from "@/app/components/station-execution/IdentifyOperatorPanel";
import { BindEquipmentPanel } from "@/app/components/station-execution/BindEquipmentPanel";
import { CloseSessionPanel } from "@/app/components/station-execution/CloseSessionPanel";
import type { I18nSemanticKey } from "@/app/i18n/keys";

export function StationSession() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const stationId = searchParams.get("stationId") ?? "";
  const [session, setSession] = useState<StationSessionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [closing, setClosing] = useState(false);
  const [opening, setOpening] = useState(false);
  const [showCloseConfirm, setShowCloseConfirm] = useState(false);
  const [commandError, setCommandError] = useState<StationCommandErrorMessage | null>(null);

  const presentSessionError = (error: unknown) => {
    const normalized = normalizeStationCommandError(error);
    setCommandError(normalized);
  };

  const loadSession = () => {
    if (!stationId) {
      setSession(null);
      setCommandError(null);
      setShowCloseConfirm(false);
      setLoading(false);
      return;
    }

    setLoading(true);
    stationApi
      .getCurrentSession(stationId)
      .then((res) => {
        setSession(res.session ?? null);
        setCommandError(null);
        setShowCloseConfirm(false);
      })
      .catch((error) => presentSessionError(error))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadSession(); }, [stationId]);

  const handleClose = () => {
    if (!session) return;
    setClosing(true);
    stationApi
      .closeSession(session.session_id)
      .then((updated) => {
        setSession(updated);
        setCommandError(null);
        setShowCloseConfirm(false);
        toast.success(t("stationSession.toast.closed" as I18nSemanticKey));
      })
      .catch((error) => presentSessionError(error))
      .finally(() => setClosing(false));
  };

  const handleOpenSession = () => {
    if (!stationId) return;

    setOpening(true);
    stationApi
      .openSession({ station_id: stationId })
      .then((opened) => {
        setSession(opened);
        setCommandError(null);
        setShowCloseConfirm(false);
        toast.success(t("stationSession.toast.opened" as I18nSemanticKey));
      })
      .catch((error) => presentSessionError(error))
      .finally(() => setOpening(false));
  };

  const goToOperatorIdentification = () => {
    const params = new URLSearchParams();
    if (stationId) {
      params.set("stationId", stationId);
    }
    if (session?.session_id) {
      params.set("sessionId", session.session_id);
    }
    const query = params.toString();
    navigate(query ? `/operator-identification?${query}` : "/operator-identification");
  };

  const goToEquipmentBinding = () => {
    const params = new URLSearchParams();
    if (stationId) {
      params.set("stationId", stationId);
    }
    if (session?.session_id) {
      params.set("sessionId", session.session_id);
    }
    const query = params.toString();
    navigate(query ? `/equipment-binding?${query}` : "/equipment-binding");
  };

  const goToStationQueue = () => {
    navigate("/station");
  };

  const equipmentChecklistState = commandError?.code === "EQUIPMENT_REQUIRED"
    ? session?.equipment_id
      ? "bound"
      : "required_missing"
    : session?.equipment_id
    ? "bound"
    : session
    ? "optional_unknown"
    : "not_confirmed";

  /**
   * BT-CORE-004: UI navigation readiness only - not backend authorization.
   * Backend revalidates session/operator/equipment on execution mutation commands.
   */
  const canNavigateToQueueByVisibleSetupState =
    Boolean(stationId) &&
    session?.status === "open" &&
    Boolean(session?.operator_user_id) &&
    equipmentChecklistState !== "required_missing";

  const navigationBlockedHint = !stationId
    ? ("stationSession.cta.helper.selectStation" as I18nSemanticKey)
    : !session
    ? ("stationSession.cta.helper.openSession" as I18nSemanticKey)
    : session.status !== "open"
    ? ("stationSession.cta.helper.openSession" as I18nSemanticKey)
    : !session.operator_user_id
    ? ("stationSession.cta.helper.identifyOperator" as I18nSemanticKey)
    : equipmentChecklistState === "required_missing"
    ? ("stationSession.cta.helper.bindEquipment" as I18nSemanticKey)
    : null;

  const isOpenSession = session?.status === "open";

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 p-4">
      <header className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <h1 className="text-2xl font-semibold text-slate-900">
            {t("stationSession.setup.title" as I18nSemanticKey)}
          </h1>
          <ScreenStatusBadge phase="CONNECTED" />
        </div>
        <button
          onClick={loadSession}
          disabled={loading}
          className="inline-flex min-h-11 items-center gap-1 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 transition hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:opacity-50"
        >
          <RefreshCw className="h-3 w-3" aria-hidden="true" />
          {t("common.action.refresh" as I18nSemanticKey)}
        </button>
      </header>

      {commandError ? (
        <aside
          role="alert"
          className={`rounded-lg border px-4 py-3 ${commandError.severity === "danger"
            ? "border-red-200 bg-red-50 text-red-800"
            : "border-amber-200 bg-amber-50 text-amber-800"}`}
        >
          <p className="font-semibold">{t(commandError.titleKey as I18nSemanticKey)}</p>
          <p className="mt-1 text-sm">{t(commandError.messageKey as I18nSemanticKey)}</p>
          <p className="mt-1 text-xs">{t(commandError.recoveryKey as I18nSemanticKey)}</p>
        </aside>
      ) : null}

      {!stationId ? (
        <aside role="alert" className="rounded-lg border border-amber-200 bg-amber-50 p-4 sm:p-5">
          <p className="font-semibold text-amber-900">{t("stationSession.empty.missingStation.title" as I18nSemanticKey)}</p>
          <p className="mt-1 text-sm text-amber-800">{t("stationSession.empty.missingStation.message" as I18nSemanticKey)}</p>
          <button
            type="button"
            onClick={() => navigate("/")}
            className="mt-3 min-h-11 rounded-lg border border-slate-300 bg-white px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
          >
            {t("stationSession.empty.missingStation.cta" as I18nSemanticKey)}
          </button>
        </aside>
      ) : (
        <>
          <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
            <OpenSessionPanel
              sessionId={session?.session_id ?? null}
              openedAt={session?.opened_at ?? null}
              sessionStatus={session?.status ?? null}
              loading={loading}
              opening={opening}
              onOpenSession={handleOpenSession}
              onEndSessionClick={() => setShowCloseConfirm(true)}
              onRefresh={loadSession}
            />

            <IdentifyOperatorPanel
              operatorUserId={session?.operator_user_id ?? null}
              sessionOpen={isOpenSession}
              onIdentifyOperator={goToOperatorIdentification}
            />

            <BindEquipmentPanel
              equipmentId={session?.equipment_id ?? null}
              equipmentChecklistState={equipmentChecklistState}
              sessionOpen={isOpenSession}
              onBindEquipment={goToEquipmentBinding}
            />
          </section>

          <button
            type="button"
            onClick={goToStationQueue}
            disabled={!canNavigateToQueueByVisibleSetupState}
            className="min-h-14 w-full rounded-lg border border-blue-600 bg-blue-600 px-4 text-base font-semibold text-white transition hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {t("stationSession.cta.enterQueue" as I18nSemanticKey)}
          </button>

          {navigationBlockedHint ? (
            <p className="text-center text-xs text-slate-600">{t(navigationBlockedHint)}</p>
          ) : null}

          <CloseSessionPanel
            isSessionOpen={isOpenSession}
            showCloseConfirm={showCloseConfirm}
            closing={closing}
            commandError={null}
            onClose={() => setShowCloseConfirm(true)}
            onConfirmClose={handleClose}
            onCancelClose={() => setShowCloseConfirm(false)}
          />
        </>
      )}
    </div>
  );
}



// Station Session — CONNECTED (backend API)
// Shows current session state from GET /v1/station/sessions/current.
// Session truth is managed by the backend execution system.
//
// Mode A composition per FE-SE-MODEA-SIMPLIFY-09 (spec v1.1):
// - Single 3-row card (Session / Operator / Equipment) — no StationWorkflowShell, no StationEntryPanel.
// - Single top-banner error surface — no inline error blocks, no toast on failure.
// - Single primary CTA "Enter queue" below the card.
// - CloseSessionPanel renders as a sibling only while showCloseConfirm is true (owns close lifecycle).
// - Empty state (no stationId) short-circuits the page to an amber notice.

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

  // Per FE-SE-MODEA-SIMPLIFY-09 IR-05:
  // Failure surface is the top banner only. No toast.error on command failure.
  // normalizeStationCommandError always returns a non-null template (FALLBACK if unmatched).
  const presentSessionError = (error: unknown) => {
    setCommandError(normalizeStationCommandError(error));
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
    if (!stationId) {
      // Empty-state short-circuit prevents reaching this branch in the main path.
      return;
    }
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

  const normalizedSessionStatus = session?.status?.toUpperCase() ?? null;
  const isOpenSession = normalizedSessionStatus === "OPEN";

  /**
   * BT-CORE-004: UI navigation readiness only — not backend authorization.
   * Backend revalidates session/operator/equipment on every execution mutation command.
   * See station-session-command-guard-enforcement-contract.md.
   */
  const canNavigateToQueueByVisibleSetupState =
    Boolean(stationId) &&
    isOpenSession &&
    Boolean(session?.operator_user_id) &&
    equipmentChecklistState !== "required_missing";

  const navigationBlockedHint = !stationId
    ? t("stationSession.cta.helper.selectStation" as I18nSemanticKey)
    : !session || !isOpenSession
    ? t("stationSession.cta.helper.openSession" as I18nSemanticKey)
    : !session.operator_user_id
    ? t("stationSession.cta.helper.identifyOperator" as I18nSemanticKey)
    : equipmentChecklistState === "required_missing"
    ? t("stationSession.cta.helper.bindEquipment" as I18nSemanticKey)
    : null;

  // Empty-state short-circuit per IR-06: no station selected.
  if (!stationId) {
    return (
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 p-4">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-gray-900">
              {t("stationSession.setup.title" as I18nSemanticKey)}
            </h1>
            <ScreenStatusBadge phase="CONNECTED" />
          </div>
        </header>
        <aside
          role="alert"
          className="rounded-lg border border-amber-200 bg-amber-50 p-4 sm:p-5"
        >
          <p className="text-sm font-semibold text-amber-900">
            {t("stationSession.empty.missingStation.title" as I18nSemanticKey)}
          </p>
          <p className="mt-1 text-sm text-amber-800">
            {t("stationSession.empty.missingStation.message" as I18nSemanticKey)}
          </p>
          <button
            type="button"
            onClick={() => navigate("/")}
            className="mt-3 min-h-11 rounded-lg border border-amber-600 bg-amber-600 px-4 text-sm font-semibold text-white transition hover:bg-amber-700 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600 focus-visible:ring-offset-2"
          >
            {t("stationSession.empty.missingStation.cta" as I18nSemanticKey)}
          </button>
        </aside>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 p-4">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("stationSession.setup.title" as I18nSemanticKey)}
          </h1>
          <ScreenStatusBadge phase="CONNECTED" />
        </div>
        <button
          type="button"
          onClick={loadSession}
          disabled={loading}
          className="flex items-center gap-1 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm text-gray-600 transition hover:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:opacity-50"
        >
          <RefreshCw className="h-3 w-3" aria-hidden="true" />
          {t("common.action.refresh" as I18nSemanticKey)}
        </button>
      </header>

      {commandError ? (
        <aside
          role="alert"
          className={`rounded-lg border px-4 py-3 text-sm ${
            commandError.severity === "danger"
              ? "border-red-200 bg-red-50 text-red-800"
              : "border-amber-200 bg-amber-50 text-amber-800"
          }`}
        >
          <p className="font-semibold">{t(commandError.titleKey as I18nSemanticKey)}</p>
          <p className="mt-1">{t(commandError.messageKey as I18nSemanticKey)}</p>
          <p className="mt-1 text-xs">{t(commandError.recoveryKey as I18nSemanticKey)}</p>
        </aside>
      ) : null}

      {loading ? (
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-400">
          {t("stationSession.label.loading_session" as I18nSemanticKey)}
        </div>
      ) : (
        <>
          {/* 3-row composite card: Session / Operator / Equipment */}
          <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <OpenSessionPanel
              sessionId={session?.session_id ?? null}
              openedAt={session?.opened_at ?? null}
              isOpen={isOpenSession}
              loading={loading}
              opening={opening}
              onOpenSession={handleOpenSession}
              onEndSessionClick={() => setShowCloseConfirm(true)}
            />
            <div className="border-t border-slate-200">
              <IdentifyOperatorPanel
                operatorUserId={session?.operator_user_id ?? null}
                sessionOpen={isOpenSession}
                onIdentifyOperator={goToOperatorIdentification}
              />
            </div>
            <div className="border-t border-slate-200">
              <BindEquipmentPanel
                equipmentId={session?.equipment_id ?? null}
                equipmentChecklistState={equipmentChecklistState}
                sessionOpen={isOpenSession}
                onBindEquipment={goToEquipmentBinding}
              />
            </div>
          </section>

          {/* Primary CTA + helper hint (no separate hint card) */}
          <button
            type="button"
            onClick={goToStationQueue}
            disabled={!canNavigateToQueueByVisibleSetupState}
            className="min-h-14 w-full rounded-lg border border-blue-600 bg-blue-600 px-4 text-base font-semibold text-white transition hover:bg-blue-700 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {t("stationSession.cta.enterQueue" as I18nSemanticKey)}
          </button>
          {navigationBlockedHint ? (
            <p className="text-center text-xs text-slate-600">{navigationBlockedHint}</p>
          ) : null}

          {/* Close-confirm dialog sibling (mounted only while confirming). */}
          {showCloseConfirm && isOpenSession ? (
            <CloseSessionPanel
              isSessionOpen={isOpenSession}
              showCloseConfirm={showCloseConfirm}
              closing={closing}
              commandError={commandError}
              canContinueToQueue={canNavigateToQueueByVisibleSetupState}
              onContinueToQueue={goToStationQueue}
              onClose={() => setShowCloseConfirm(true)}
              onConfirmClose={handleClose}
              onCancelClose={() => setShowCloseConfirm(false)}
            />
          ) : null}
        </>
      )}
    </div>
  );
}



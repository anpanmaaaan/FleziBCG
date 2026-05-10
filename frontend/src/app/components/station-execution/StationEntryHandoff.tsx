import type { ReactNode } from "react";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

export type HandoffStationState = "selected" | "missing" | "not_confirmed";
export type HandoffSessionState = "open" | "missing" | "closed" | "not_confirmed";
export type HandoffOperatorState = "identified" | "missing" | "not_confirmed";
export type HandoffEquipmentState =
  | "bound"
  | "required_missing"
  | "optional_unknown"
  | "missing"
  | "not_confirmed";
export type HandoffOperationState = "selected" | "queue_only" | "not_selected" | "not_confirmed";

interface HandoffCta {
  labelKey: string;
  onClick: () => void;
  tone?: "primary" | "neutral";
}

interface StationEntryHandoffProps {
  stationState: HandoffStationState;
  sessionState: HandoffSessionState;
  operatorState: HandoffOperatorState;
  equipmentState: HandoffEquipmentState;
  nextStepKey: string;
  operationState?: HandoffOperationState;
  ctas?: HandoffCta[];
  footer?: ReactNode;
}

function getBadgeClass(statusTone: "good" | "warn" | "neutral") {
  if (statusTone === "good") {
    return "bg-emerald-50 text-emerald-700 border-emerald-200";
  }
  if (statusTone === "warn") {
    return "bg-amber-50 text-amber-700 border-amber-200";
  }
  return "bg-slate-50 text-slate-600 border-slate-200";
}

export function StationEntryHandoff({
  stationState,
  sessionState,
  operatorState,
  equipmentState,
  nextStepKey,
  operationState,
  ctas,
  footer,
}: StationEntryHandoffProps) {
  const { t } = useI18n();

  const stationTone = stationState === "selected" ? "good" : stationState === "missing" ? "warn" : "neutral";
  const sessionTone = sessionState === "open" ? "good" : sessionState === "missing" || sessionState === "closed" ? "warn" : "neutral";
  const operatorTone = operatorState === "identified" ? "good" : operatorState === "missing" ? "warn" : "neutral";
  const equipmentTone = equipmentState === "bound" ? "good" : equipmentState === "required_missing" || equipmentState === "missing" ? "warn" : "neutral";
  const operationTone =
    operationState === "selected" ? "good" : operationState === "not_selected" ? "warn" : "neutral";

  return (
    <section className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <h2 className="text-sm font-semibold text-slate-900">{t("station.handoff.title")}</h2>
        <span className="rounded-full border border-slate-200 bg-white px-2 py-0.5 text-xs text-slate-600">
          {t("station.handoff.sourceOfTruth")}
        </span>
      </div>

      <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-white bg-white px-3 py-2 text-sm">
          <p className="text-xs text-slate-500">{t("station.handoff.station")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${getBadgeClass(stationTone)}`}>
            {t(`station.handoff.state.station.${stationState}` as I18nSemanticKey)}
          </p>
        </div>
        <div className="rounded-lg border border-white bg-white px-3 py-2 text-sm">
          <p className="text-xs text-slate-500">{t("station.handoff.session")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${getBadgeClass(sessionTone)}`}>
            {t(`station.handoff.state.session.${sessionState}` as I18nSemanticKey)}
          </p>
        </div>
        <div className="rounded-lg border border-white bg-white px-3 py-2 text-sm">
          <p className="text-xs text-slate-500">{t("station.handoff.operator")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${getBadgeClass(operatorTone)}`}>
            {t(`station.handoff.state.operator.${operatorState}` as I18nSemanticKey)}
          </p>
        </div>
        <div className="rounded-lg border border-white bg-white px-3 py-2 text-sm">
          <p className="text-xs text-slate-500">{t("station.handoff.equipment")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${getBadgeClass(equipmentTone)}`}>
            {t(`station.handoff.state.equipment.${equipmentState}` as I18nSemanticKey)}
          </p>
        </div>
      </div>

      {typeof operationState === "string" ? (
        <div className="mt-2 rounded-lg border border-white bg-white px-3 py-2 text-sm">
          <p className="text-xs text-slate-500">{t("station.handoff.operation")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${getBadgeClass(operationTone)}`}>
            {t(`station.handoff.state.operation.${operationState}` as I18nSemanticKey)}
          </p>
        </div>
      ) : null}

      <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-700">{t("station.handoff.nextStep")}</p>
        <p className="mt-1 text-sm text-blue-900">{t(nextStepKey as I18nSemanticKey)}</p>
      </div>

      {ctas && ctas.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {ctas.map((cta) => (
            <button
              key={cta.labelKey}
              type="button"
              onClick={cta.onClick}
              className={`min-h-10 rounded-lg border px-3 text-sm font-medium transition active:scale-95 ${
                cta.tone === "primary"
                  ? "border-blue-600 bg-blue-600 text-white hover:bg-blue-700"
                  : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              {t(cta.labelKey as I18nSemanticKey)}
            </button>
          ))}
        </div>
      ) : null}

      {footer ? <div className="mt-2 text-xs text-slate-500">{footer}</div> : null}
    </section>
  );
}

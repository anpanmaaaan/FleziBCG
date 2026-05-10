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

function getTokenRowClass(statusTone: "good" | "warn" | "neutral") {
  if (statusTone === "good") {
    return "border-emerald-200 bg-emerald-50";
  }
  if (statusTone === "warn") {
    return "border-amber-200 bg-amber-50";
  }
  return "border-slate-200 bg-slate-50";
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

  const primaryCta = ctas?.find((cta) => cta.tone === "primary") ?? null;
  const secondaryCtas = ctas?.filter((cta) => cta !== primaryCta) ?? [];

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-900">{t("station.handoff.title")}</h2>
          <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs text-slate-600">
            {t("station.handoff.sourceOfTruth")}
          </span>
        </div>
        <span className="text-xs font-medium text-slate-600">{t("station.handoff.nextStep")}</span>
      </div>

      <p className="mt-1 text-sm text-blue-900">{t(nextStepKey as I18nSemanticKey)}</p>

      <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-5">
        <div className={`rounded-md border px-2.5 py-2 text-sm ${getTokenRowClass(stationTone)}`}>
          <p className="text-[11px] text-slate-500">{t("station.handoff.station")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium ${getBadgeClass(stationTone)}`}>
            {t(`station.handoff.state.station.${stationState}` as I18nSemanticKey)}
          </p>
        </div>
        <div className={`rounded-md border px-2.5 py-2 text-sm ${getTokenRowClass(sessionTone)}`}>
          <p className="text-[11px] text-slate-500">{t("station.handoff.session")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium ${getBadgeClass(sessionTone)}`}>
            {t(`station.handoff.state.session.${sessionState}` as I18nSemanticKey)}
          </p>
        </div>
        <div className={`rounded-md border px-2.5 py-2 text-sm ${getTokenRowClass(operatorTone)}`}>
          <p className="text-[11px] text-slate-500">{t("station.handoff.operator")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium ${getBadgeClass(operatorTone)}`}>
            {t(`station.handoff.state.operator.${operatorState}` as I18nSemanticKey)}
          </p>
        </div>
        <div className={`rounded-md border px-2.5 py-2 text-sm ${getTokenRowClass(equipmentTone)}`}>
          <p className="text-[11px] text-slate-500">{t("station.handoff.equipment")}</p>
          <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium ${getBadgeClass(equipmentTone)}`}>
            {t(`station.handoff.state.equipment.${equipmentState}` as I18nSemanticKey)}
          </p>
        </div>
        {typeof operationState === "string" ? (
          <div className={`rounded-md border px-2.5 py-2 text-sm ${getTokenRowClass(operationTone)}`}>
            <p className="text-[11px] text-slate-500">{t("station.handoff.operation")}</p>
            <p className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium ${getBadgeClass(operationTone)}`}>
              {t(`station.handoff.state.operation.${operationState}` as I18nSemanticKey)}
            </p>
          </div>
        ) : null}
      </div>

      {primaryCta ? (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={primaryCta.onClick}
            className="min-h-10 rounded-lg border border-blue-600 bg-blue-600 px-3 text-sm font-medium text-white transition hover:bg-blue-700 active:scale-95"
          >
            {t(primaryCta.labelKey as I18nSemanticKey)}
          </button>

          {secondaryCtas.length > 0 ? (
            <span className="text-xs text-slate-500">{t("station.handoff.secondaryRoutes")}</span>
          ) : null}

          {secondaryCtas.map((cta) => (
            <button
              key={cta.labelKey}
              type="button"
              onClick={cta.onClick}
              className="min-h-9 rounded-md border border-slate-300 bg-white px-2.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95"
            >
              {t(cta.labelKey as I18nSemanticKey)}
            </button>
          ))}
        </div>
      ) : ctas && ctas.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {ctas.map((cta) => (
            <button
              key={cta.labelKey}
              type="button"
              onClick={cta.onClick}
              className="min-h-9 rounded-md border border-slate-300 bg-white px-2.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95"
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

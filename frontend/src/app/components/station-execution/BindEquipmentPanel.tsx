import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

// Per FE-SE-MODEA-SIMPLIFY-09 IR-04:
// Renders as an inline row inside the parent 3-row card (a <div>, not its own <section>).
// Drops the Cpu icon, the section border, and the standalone hint paragraph.
interface BindEquipmentPanelProps {
  equipmentId: string | null;
  equipmentChecklistState: string;
  sessionOpen: boolean;
  onBindEquipment: () => void;
}

export function BindEquipmentPanel({
  equipmentId,
  equipmentChecklistState,
  sessionOpen,
  onBindEquipment,
}: BindEquipmentPanelProps) {
  const { t } = useI18n();

  const bound = sessionOpen && Boolean(equipmentId);
  const requiredMissing = sessionOpen && equipmentChecklistState === "required_missing";
  const optional = sessionOpen && !equipmentId && equipmentChecklistState === "optional_unknown";

  // Status pill: Bound (emerald) | Not yet (amber) | Optional (slate) | Not confirmed (slate)
  const statusClass = bound
    ? "bg-emerald-50 text-emerald-800"
    : requiredMissing
    ? "bg-amber-50 text-amber-900"
    : "bg-slate-100 text-slate-700";
  const statusSymbol = bound ? "●" : requiredMissing ? "○" : optional ? "−" : "○";
  const statusKey: I18nSemanticKey = bound
    ? ("stationSession.row.status.bound" as I18nSemanticKey)
    : requiredMissing
    ? ("stationSession.row.status.notYet" as I18nSemanticKey)
    : optional
    ? ("stationSession.row.status.optional" as I18nSemanticKey)
    : ("stationSession.row.status.notConfirmed" as I18nSemanticKey);

  const subtext = bound && equipmentId
    ? t("stationSession.row.equipment.subtext.bound" as I18nSemanticKey, {
        equipmentId,
      })
    : requiredMissing
    ? t("stationSession.row.equipment.subtext.required" as I18nSemanticKey)
    : optional
    ? t("stationSession.row.equipment.subtext.optional" as I18nSemanticKey)
    : t("stationSession.row.equipment.subtext.sessionFirst" as I18nSemanticKey);

  const showAction = sessionOpen && !bound && (requiredMissing || optional);

  return (
    <div className="flex items-center gap-3 p-4 sm:p-5">
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
          bound ? "bg-emerald-50 text-emerald-900" : "bg-slate-100 text-slate-700"
        }`}
        aria-hidden="true"
      >
        3
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-900">
            {t("stationSession.row.equipment.title" as I18nSemanticKey)}
          </h2>
          <span
            className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${statusClass}`}
          >
            <span aria-hidden="true">{statusSymbol}</span>
            <span>{t(statusKey)}</span>
          </span>
        </div>
        <p className="mt-1 text-xs text-slate-600">{subtext}</p>
      </div>
      {showAction ? (
        <button
          type="button"
          onClick={onBindEquipment}
          className="min-h-11 shrink-0 rounded-lg border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
        >
          {t("stationSession.row.equipment.action.bind" as I18nSemanticKey)}
        </button>
      ) : null}
    </div>
  );
}

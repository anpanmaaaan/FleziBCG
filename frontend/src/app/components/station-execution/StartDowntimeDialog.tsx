import { useEffect, useState } from "react";
import type { DowntimeReasonOption } from "@/app/api";
import { useI18n } from "@/app/i18n";

export interface StartDowntimeDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (reasonCode: string, note: string) => void;
  loading: boolean;
  reasons: DowntimeReasonOption[];
  reasonsLoading: boolean;
}

export function StartDowntimeDialog({
  open,
  onClose,
  onSubmit,
  loading,
  reasons,
  reasonsLoading,
}: StartDowntimeDialogProps) {
  const { t } = useI18n();
  const [reasonCode, setReasonCode] = useState("");
  const [note, setNote] = useState("");

  useEffect(() => {
    if (!open) {
      setReasonCode("");
      setNote("");
      return;
    }

    setReasonCode((current) => {
      if (current && reasons.some((item) => item.reason_code === current)) {
        return current;
      }
      return reasons[0]?.reason_code ?? "";
    });
  }, [open, reasons]);

  if (!open) return null;

  const selectedReason = reasons.find((item) => item.reason_code === reasonCode) ?? null;
  const noteRequired = selectedReason?.requires_comment ?? false;
  const noteValue = note.trim();
  const submitDisabled =
    loading ||
    reasonsLoading ||
    !reasonCode ||
    (noteRequired && noteValue.length === 0);

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-96" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-bold mb-4">{t("station.action.startDowntime")}</h2>
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {t("station.downtime.reason.label")}
          <select
            className="mt-1 block w-full border border-gray-300 rounded-lg p-2"
            value={reasonCode}
            onChange={(e) => setReasonCode(e.target.value)}
            disabled={loading || reasonsLoading || reasons.length === 0}
          >
            {reasons.length === 0 ? (
              <option value="">{t("station.downtime.reason.empty")}</option>
            ) : (
              reasons.map((item) => (
                <option key={item.reason_code} value={item.reason_code}>{item.reason_name}</option>
              ))
            )}
          </select>
        </label>
        {selectedReason ? (
          <p className="mb-2 text-xs text-gray-500">
            {t("station.downtime.reason.groupPrefix")} {selectedReason.reason_group}
          </p>
        ) : null}
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {noteRequired ? t("station.downtime.note.requiredLabel") : t("station.downtime.note.label")}
          <input
            className="mt-1 block w-full border border-gray-300 rounded-lg p-2"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder={noteRequired ? t("station.downtime.note.requiredPlaceholder") : t("station.downtime.note.placeholder")}
            disabled={loading || reasonsLoading}
          />
        </label>
        {reasonsLoading ? <p className="text-xs text-gray-500">{t("station.downtime.reason.loading")}</p> : null}
        {!reasonsLoading && reasons.length === 0 ? <p className="text-xs text-amber-700">{t("station.downtime.reason.emptyHelp")}</p> : null}
        <div className="flex gap-2 mt-4 justify-end">
          <button onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700" disabled={loading}>{t("common.action.cancel")}</button>
          <button
            onClick={() => onSubmit(reasonCode, noteValue)}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50"
            disabled={submitDisabled}
          >
            {t("station.action.startDowntime")}
          </button>
        </div>
      </div>
    </div>
  );
}

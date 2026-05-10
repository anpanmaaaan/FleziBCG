import { useEffect, useRef, useState } from "react";
import type { DowntimeReasonOption } from "@/app/api";
import { useI18n } from "@/app/i18n";
import { Dialog } from "@/app/components/Dialog/Dialog";

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
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const reasonSelectRef = useRef<HTMLSelectElement | null>(null);

  useEffect(() => {
    if (!open) {
      setReasonCode("");
      setNote("");
      setSubmitAttempted(false);
      return;
    }

    setReasonCode((current) => {
      if (current && reasons.some((item) => item.reason_code === current)) {
        return current;
      }
      return reasons[0]?.reason_code ?? "";
    });
    setSubmitAttempted(false);
  }, [open, reasons]);

  const selectedReason = reasons.find((item) => item.reason_code === reasonCode) ?? null;
  const noteRequired = selectedReason?.requires_comment ?? false;
  const noteValue = note.trim();
  const reasonInvalid = submitAttempted && !reasonCode;
  const noteInvalid = submitAttempted && noteRequired && noteValue.length === 0;

  const handleSubmit = () => {
    setSubmitAttempted(true);
    if (loading || reasonsLoading || !reasonCode || (noteRequired && noteValue.length === 0)) {
      return;
    }
    onSubmit(reasonCode, noteValue);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      titleId="start-downtime-dialog-title"
      initialFocusRef={reasonSelectRef}
    >
      <h2 id="start-downtime-dialog-title" className="mb-4 text-lg font-bold">
        {t("station.action.startDowntime")}
      </h2>
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {t("station.downtime.reason.label")}
          <select
            ref={reasonSelectRef}
            className="mt-1 block min-h-[44px] w-full rounded-lg border border-gray-300 p-3 focus-visible:outline-2 focus-visible:outline-blue-600 focus-visible:outline-offset-2"
            value={reasonCode}
            onChange={(e) => setReasonCode(e.target.value)}
            disabled={loading || reasonsLoading || reasons.length === 0}
            aria-required="true"
            aria-invalid={reasonInvalid}
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
          <textarea
            className="mt-1 block min-h-[72px] w-full resize-y rounded-lg border border-gray-300 p-3 focus-visible:outline-2 focus-visible:outline-blue-600 focus-visible:outline-offset-2"
            rows={3}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder={noteRequired ? t("station.downtime.note.requiredPlaceholder") : t("station.downtime.note.placeholder")}
            disabled={loading || reasonsLoading}
            aria-required={noteRequired ? "true" : "false"}
            aria-invalid={noteInvalid}
          />
        </label>
        {reasonsLoading ? <p className="text-xs text-gray-500">{t("station.downtime.reason.loading")}</p> : null}
        {!reasonsLoading && reasons.length === 0 ? <p className="text-xs text-amber-700">{t("station.downtime.reason.emptyHelp")}</p> : null}
        <div className="flex gap-3 mt-5 justify-end">
          <button
            onClick={onClose}
            className="min-h-11 rounded-lg bg-gray-200 px-5 py-2 text-gray-700 transition active:scale-95 focus-visible:outline-2 focus-visible:outline-blue-600 focus-visible:outline-offset-2"
            disabled={loading}
          >
            {t("common.action.cancel")}
          </button>
          <button
            onClick={handleSubmit}
            className="min-h-11 rounded-lg bg-blue-600 px-5 py-2 font-semibold text-white transition hover:bg-blue-700 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-blue-600 focus-visible:outline-offset-2"
            disabled={loading || reasonsLoading || reasons.length === 0}
          >
            {t("station.action.startDowntime")}
          </button>
        </div>
    </Dialog>
  );
}

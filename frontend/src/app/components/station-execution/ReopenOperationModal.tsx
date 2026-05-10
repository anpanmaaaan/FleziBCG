import { useEffect, useRef, useState } from "react";
import { useI18n } from "@/app/i18n";
import { Dialog } from "@/app/components/Dialog/Dialog";

export interface ReopenOperationModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (reason: string) => void;
  loading: boolean;
}

export function ReopenOperationModal({
  open,
  onClose,
  onSubmit,
  loading,
}: ReopenOperationModalProps) {
  const { t } = useI18n();
  const [reason, setReason] = useState("");
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const reasonInputRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (!open) {
      setReason("");
      setSubmitAttempted(false);
    }
  }, [open]);

  const trimmedReason = reason.trim();
  const reasonInvalid = submitAttempted && trimmedReason.length === 0;

  const handleSubmit = () => {
    setSubmitAttempted(true);
    if (loading || trimmedReason.length === 0) {
      return;
    }
    onSubmit(trimmedReason);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      titleId="reopen-operation-dialog-title"
      initialFocusRef={reasonInputRef}
    >
      <h2 id="reopen-operation-dialog-title" className="mb-4 text-lg font-bold">
        {t("station.action.reopen")}
      </h2>
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {t("station.reopen.reason.label")}
          <textarea
            ref={reasonInputRef}
            className="mt-1 block min-h-28 w-full resize-y rounded-lg border border-gray-300 p-2 focus-visible:outline-2 focus-visible:outline-blue-600 focus-visible:outline-offset-2"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder={t("station.reopen.reason.placeholder")}
            disabled={loading}
            aria-required="true"
            aria-invalid={reasonInvalid}
          />
        </label>
        <p className="text-xs text-gray-500">{t("station.reopen.reason.helper")}</p>
        <div className="flex gap-3 mt-5 justify-end">
          <button
            onClick={onClose}
            className="min-h-11 rounded-lg bg-gray-200 px-5 py-2 text-gray-700 transition active:scale-95 focus-visible:outline-2 focus-visible:outline-blue-600 focus-visible:outline-offset-2"
            disabled={loading}
          >
            {t("station.reopen.dialog.cancel")}
          </button>
          <button
            onClick={handleSubmit}
            className="min-h-11 rounded-lg bg-blue-600 px-5 py-2 font-semibold text-white transition hover:bg-blue-700 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-blue-600 focus-visible:outline-offset-2"
            disabled={loading}
          >
            {t("station.reopen.dialog.submit")}
          </button>
        </div>
    </Dialog>
  );
}

import { useEffect, useState } from "react";
import { useI18n } from "@/app/i18n";

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

  useEffect(() => {
    if (!open) {
      setReason("");
    }
  }, [open]);

  if (!open) return null;

  const trimmedReason = reason.trim();

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-96" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-bold mb-4">{t("station.action.reopen")}</h2>
        <label className="block mb-2 text-sm font-medium text-gray-700">
          {t("station.reopen.reason.label")}
          <textarea
            className="mt-1 block w-full border border-gray-300 rounded-lg p-2 min-h-28 resize-y"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder={t("station.reopen.reason.placeholder")}
            disabled={loading}
          />
        </label>
        <p className="text-xs text-gray-500">{t("station.reopen.reason.helper")}</p>
        <div className="flex gap-2 mt-4 justify-end">
          <button onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700" disabled={loading}>
            {t("station.reopen.dialog.cancel")}
          </button>
          <button
            onClick={() => onSubmit(trimmedReason)}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50"
            disabled={loading || trimmedReason.length === 0}
          >
            {t("station.reopen.dialog.submit")}
          </button>
        </div>
      </div>
    </div>
  );
}

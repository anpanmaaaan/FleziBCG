// Measurement Entry — SHELL
// To-be visualization for QC measurement input and submission.
// Pass/fail evaluation and disposition are managed by the backend quality domain.

import { useState } from "react";
import { Lock, Ruler, AlertTriangle } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_CHARACTERISTICS = [
  { id: "CH-001", name: "Dimension A", unit: "mm", spec: "25±0.5", lower: 24.5, upper: 25.5 },
  { id: "CH-002", name: "Dimension B", unit: "mm", spec: "15±0.3", lower: 14.7, upper: 15.3 },
  { id: "CH-003", name: "Surface Finish", unit: "µm", spec: "<2.0", lower: 0, upper: 2.0 },
];

export function MeasurementEntry() {
  const { t } = useI18n();
  const [selectedOp, setSelectedOp] = useState<string>("");
  const [measurements, setMeasurements] = useState<Record<string, string>>({});

  const handleMeasurementChange = (charId: string, value: string) => {
    setMeasurements((prev) => ({ ...prev, [charId]: value }));
  };

  return (
    <div className="flex flex-col gap-4 p-4 max-w-4xl mx-auto">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">
          {t("measurementEntry.title")}
        </h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("measurementEntry.notice.shell")} />

      {/* Operation selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Select Operation</label>
        <select
          value={selectedOp}
          onChange={(e) => setSelectedOp(e.target.value)}
          className="block w-full border border-gray-200 rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
          aria-label="Select operation for measurement"
        >
          <option value="">— Select an operation —</option>
          <option value="OP-010">OP-010 — Turning</option>
          <option value="OP-020">OP-020 — Grinding</option>
          <option value="OP-030">OP-030 — Assembly</option>
        </select>
      </div>

      {!selectedOp ? (
        <div className="flex items-center gap-2 p-4 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600">
          <AlertTriangle className="w-4 h-4" />
          {t("measurementEntry.noOperation")}
        </div>
      ) : (
        <>
          {/* Characteristics table */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
              <Ruler className="w-4 h-4 text-blue-500" />
              {t("measurementEntry.section.characteristics")}
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                  <th className="px-4 py-2 text-left">{t("measurementEntry.col.characteristic")}</th>
                  <th className="px-4 py-2 text-left">{t("measurementEntry.col.spec")}</th>
                  <th className="px-4 py-2 text-left">{t("measurementEntry.col.value")}</th>
                  <th className="px-4 py-2 text-left">{t("measurementEntry.col.status")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {MOCK_CHARACTERISTICS.map((char) => {
                  const value = measurements[char.id];
                  const numValue = value ? parseFloat(value) : null;
                  const isPass = numValue !== null && numValue >= char.lower && numValue <= char.upper;
                  const showStatus = value !== undefined && value !== "";

                  return (
                    <tr key={char.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="font-medium text-gray-800">{char.name}</div>
                        <div className="text-xs text-gray-500">{char.unit}</div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{char.spec}</td>
                      <td className="px-4 py-3">
                        <input
                          type="number"
                          step="0.1"
                          placeholder="Enter value"
                          value={value || ""}
                          onChange={(e) => handleMeasurementChange(char.id, e.target.value)}
                          className="border border-gray-200 rounded px-2 py-1 text-sm w-24 focus:outline-none focus:ring-1 focus:ring-blue-300"
                          aria-label={`Measurement for ${char.name}`}
                        />
                      </td>
                      <td className="px-4 py-3">
                        {showStatus ? (
                          <span className={`text-xs font-medium px-2 py-1 rounded ${isPass ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                            {isPass ? "PREVIEW PASS" : "PREVIEW FAIL"}
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400 italic">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Action buttons — all disabled */}
          <div className="flex gap-3">
            <button
              disabled
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-300 text-gray-600 text-sm cursor-not-allowed"
              title={t("measurementEntry.hint.disabled")}
            >
              <Lock className="w-4 h-4" />
              {t("measurementEntry.action.submit")}
            </button>
            <button
              disabled
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-300 text-gray-600 text-sm cursor-not-allowed"
              title={t("measurementEntry.hint.disabled")}
            >
              <Lock className="w-4 h-4" />
              {t("measurementEntry.action.evaluate")}
            </button>
          </div>

          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
            ⚠ Pass/fail preview is for layout visualization only. Backend quality domain evaluates measurements and determines official disposition.
          </p>
        </>
      )}
    </div>
  );
}

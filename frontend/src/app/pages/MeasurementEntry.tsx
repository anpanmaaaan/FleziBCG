import { useCallback, useMemo, useRef, useState } from "react";
import { AlertTriangle, CheckCircle2, ClipboardCheck, Plus, Trash2 } from "lucide-react";
import { BackendRequiredNotice, MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import {
  qualityApi,
  type QualityMeasurementInput,
  type QualityMeasurementSubmitResponse,
  type QualityOperationRequirementsResponse,
} from "@/app/api";
import { HttpError } from "@/app/api";
import { useI18n } from "@/app/i18n";

interface MeasurementRow {
  key: string;
  itemCode: string;
  measuredValue: string;
  lowerLimit: string;
  upperLimit: string;
}

let _rowSeq = 1;
const nextKey = () => `r${_rowSeq++}`;

const EMPTY_ROW: MeasurementRow = {
  key: nextKey(),
  itemCode: "",
  measuredValue: "",
  lowerLimit: "",
  upperLimit: "",
};

function requirementToRow(item: QualityOperationRequirementsResponse["items"][number]): MeasurementRow {
  return {
    key: nextKey(),
    itemCode: item.item_code,
    measuredValue: "",
    lowerLimit: item.lower_limit == null ? "" : String(item.lower_limit),
    upperLimit: item.upper_limit == null ? "" : String(item.upper_limit),
  };
}

export function MeasurementEntry() {
  const { t } = useI18n();
  const [operationId, setOperationId] = useState("");
  const [rows, setRows] = useState<MeasurementRow[]>([EMPTY_ROW]);
  const [requirements, setRequirements] = useState<QualityOperationRequirementsResponse | null>(null);
  const [loadingRequirements, setLoadingRequirements] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QualityMeasurementSubmitResponse | null>(null);
  const addBtnRef = useRef<HTMLButtonElement>(null);
  const hasRequirementTemplate = (requirements?.items.length ?? 0) > 0;
  const hasCompleteRequiredMeasurements = useMemo(() => {
    if (!requirements || !requirements.qc_required || !hasRequirementTemplate) {
      return false;
    }
    const requiredCodes = requirements.items
      .filter((item) => item.required)
      .map((item) => item.item_code);

    return requiredCodes.every((itemCode) => {
      const row = rows.find((candidate) => candidate.itemCode.trim() === itemCode);
      if (!row) return false;
      const measured = Number(row.measuredValue);
      return row.measuredValue.trim().length > 0 && Number.isFinite(measured);
    });
  }, [hasRequirementTemplate, requirements, rows]);

  const canSubmit = useMemo(() => {
    const opId = Number(operationId);
    if (!Number.isInteger(opId) || opId <= 0) {
      return false;
    }
    if (!requirements || requirements.operation_id !== opId || !requirements.qc_required) {
      return false;
    }
    if (hasRequirementTemplate) {
      return hasCompleteRequiredMeasurements;
    }
    return rows.some((row) => row.itemCode.trim() && row.measuredValue.trim());
  }, [
    hasCompleteRequiredMeasurements,
    hasRequirementTemplate,
    operationId,
    requirements,
    rows,
  ]);

  const updateRow = (rowKey: string, field: keyof MeasurementRow, value: string) => {
    setRows((prev) => prev.map((row) => (row.key === rowKey ? { ...row, [field]: value } : row)));
  };

  const addRow = useCallback(() => {
    setRows((prev) => [
      ...prev,
      { key: nextKey(), itemCode: "", measuredValue: "", lowerLimit: "", upperLimit: "" },
    ]);
    // shift focus to the new row's item-code input on next paint
    requestAnimationFrame(() => {
      const inputs = document.querySelectorAll<HTMLInputElement>("[data-measurement-item-code]");
      const last = inputs[inputs.length - 1];
      last?.focus();
    });
  }, []);

  const loadRequirements = async () => {
    setError(null);
    setResult(null);

    const opId = Number(operationId);
    if (!Number.isInteger(opId) || opId <= 0) {
      setError(t("measurementEntry.error.invalidOperationId"));
      return;
    }

    try {
      setLoadingRequirements(true);
      const response = await qualityApi.getRequirements(opId);
      setRequirements(response);
      setRows(
        response.items.length > 0
          ? response.items.map(requirementToRow)
          : [{ key: nextKey(), itemCode: "", measuredValue: "", lowerLimit: "", upperLimit: "" }]
      );
    } catch (err) {
      setRequirements(null);
      if (err instanceof HttpError) {
        setError(
          typeof err.detail === "string"
            ? err.detail
            : t("measurementEntry.error.requirementsLoadFailed")
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("measurementEntry.error.requirementsLoadFailed"));
      }
    } finally {
      setLoadingRequirements(false);
    }
  };

  const removeRow = useCallback((rowKey: string) => {
    setRows((prev) => {
      if (prev.length <= 1) return prev;
      return prev.filter((r) => r.key !== rowKey);
    });
  }, []);

  const buildPayload = (): { operation_id: number; measurements: QualityMeasurementInput[] } => {
    const opId = Number(operationId);
    const measurements: QualityMeasurementInput[] = [];
    for (const row of rows) {
      if (!row.itemCode.trim() || !row.measuredValue.trim()) {
        continue;
      }
      const measured = Number(row.measuredValue);
      if (!Number.isFinite(measured)) {
        continue;
      }
      measurements.push({
        item_code: row.itemCode.trim(),
        measured_value: measured,
      });
    }

    return {
      operation_id: opId,
      measurements,
    };
  };

  const submitMeasurement = async () => {
    setError(null);
    setResult(null);

    if (!canSubmit) {
      setError(
        hasRequirementTemplate
          ? t("measurementEntry.error.requiredIncomplete")
          : t("measurementEntry.error.invalidInput")
      );
      return;
    }

    try {
      setSubmitting(true);
      const payload = buildPayload();
      const response = await qualityApi.submitMeasurement(payload);
      setResult(response);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(typeof err.detail === "string" ? err.detail : t("measurementEntry.error.submitFailed"));
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("measurementEntry.error.submitFailed"));
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 p-4">
      <MockWarningBanner phase="PARTIAL" note={t("measurementEntry.notice.partial")} />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("measurementEntry.title")}</h1>
        <ScreenStatusBadge phase="PARTIAL" />
      </div>

      <BackendRequiredNotice message={t("measurementEntry.notice.backend") } />

      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700" htmlFor="operation-id-input">
              {t("measurementEntry.field.operationId")}
            </label>
            <input
              id="operation-id-input"
              type="number"
              min={1}
              value={operationId}
              onChange={(e) => setOperationId(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200"
              placeholder={t("measurementEntry.field.operationIdPlaceholder")}
            />
          </div>
          <button
            type="button"
            onClick={() => void loadRequirements()}
            disabled={loadingRequirements}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loadingRequirements
              ? t("measurementEntry.action.loadingRequirements")
              : t("measurementEntry.action.loadRequirements")}
          </button>
        </div>

        {requirements ? (
          <div className="mt-3 rounded-md border border-blue-200 bg-blue-50 p-3 text-sm text-gray-800">
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
              <div>
                {t("measurementEntry.requirements.operation")} <span className="font-medium">{requirements.operation_number}</span>
              </div>
              <div>
                {t("measurementEntry.requirements.template")} <span className="font-medium">{requirements.template_code ?? t("measurementEntry.state.none")}</span>
              </div>
            </div>
            <div className="mt-2 text-xs text-gray-600">
              {requirements.qc_required
                ? hasRequirementTemplate && !hasCompleteRequiredMeasurements
                  ? t("measurementEntry.state.requiredIncomplete")
                  : t("measurementEntry.state.requirementsLoaded")
                : t("measurementEntry.state.qcNotRequired")}
            </div>
          </div>
        ) : (
          <div className="mt-3 text-xs text-gray-500">{t("measurementEntry.state.requirementsMissing")}</div>
        )}
      </div>

      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
        <div className="flex items-center gap-2 border-b border-gray-100 px-4 py-3 text-sm font-semibold text-gray-700">
          <ClipboardCheck className="h-4 w-4 text-blue-600" />
          {t("measurementEntry.section.characteristics")}
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
              <th className="px-4 py-2 text-left">{t("measurementEntry.col.characteristic")}</th>
              <th className="px-4 py-2 text-left">{t("measurementEntry.col.value")}</th>
              <th className="px-4 py-2 text-left">{t("measurementEntry.col.lower")}</th>
              <th className="px-4 py-2 text-left">{t("measurementEntry.col.upper")}</th>
              <th className="px-4 py-2" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {rows.map((row) => (
              <tr key={row.key} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <input
                    data-measurement-item-code
                    value={row.itemCode}
                    onChange={(e) => updateRow(row.key, "itemCode", e.target.value)}
                    readOnly={hasRequirementTemplate}
                    className="w-full rounded border border-gray-300 px-2 py-1 read-only:bg-gray-50 read-only:text-gray-600 read-only:outline-none"
                    placeholder={t("measurementEntry.field.itemCodePlaceholder")}
                  />
                </td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    step="0.0001"
                    value={row.measuredValue}
                    onChange={(e) => updateRow(row.key, "measuredValue", e.target.value)}
                    className="w-full rounded border border-gray-300 px-2 py-1"
                    placeholder={t("measurementEntry.field.measuredPlaceholder")}
                  />
                </td>
                <td className="px-4 py-3">
                  <div className="rounded border border-gray-200 bg-gray-50 px-2 py-1 text-sm text-gray-600">
                    {row.lowerLimit || t("measurementEntry.state.none")}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="rounded border border-gray-200 bg-gray-50 px-2 py-1 text-sm text-gray-600">
                    {row.upperLimit || t("measurementEntry.state.none")}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <button
                    type="button"
                    onClick={() => removeRow(row.key)}
                    disabled={rows.length <= 1 || hasRequirementTemplate}
                    aria-label={t("measurementEntry.action.removeRow")}
                    className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="border-t border-gray-100 px-4 py-2">
          <button
            ref={addBtnRef}
            type="button"
            onClick={addRow}
            disabled={hasRequirementTemplate}
            className="inline-flex items-center gap-1.5 rounded px-2 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Plus className="h-3.5 w-3.5" />
            {t("measurementEntry.action.addRow")}
          </button>
        </div>
      </div>

      {error ? (
        <div className="flex items-start gap-2 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={submitMeasurement}
          disabled={!canSubmit || submitting}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
        >
          {submitting ? t("measurementEntry.action.submitting") : t("measurementEntry.action.submit")}
        </button>
        <span className="text-xs text-gray-500">{t("measurementEntry.hint.backendAuthoritative")}</span>
      </div>

      {result ? (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-green-800">
            <CheckCircle2 className="h-4 w-4" />
            {t("measurementEntry.result.title")}
          </div>
          <div className="mb-3 grid grid-cols-1 gap-2 text-sm text-gray-800 md:grid-cols-2">
            <div>{t("measurementEntry.result.qualityStatus")} <span className="font-medium">{result.quality_status}</span></div>
            <div>{t("measurementEntry.result.reviewStatus")} <span className="font-medium">{result.review_status}</span></div>
            <div>{t("measurementEntry.result.acceptedRelease")} <span className="font-medium">{result.accepted_good_release_qty}</span></div>
            <div>{t("measurementEntry.result.heldPending")} <span className="font-medium">{result.held_pending_good_qty}</span></div>
            <div>{t("measurementEntry.result.holdId")} <span className="font-medium">{result.hold_id ?? "-"}</span></div>
            <div>{t("measurementEntry.result.recordId")} <span className="font-medium">{result.measurement_record_id}</span></div>
          </div>
          {result.values.length > 0 ? (
            <div className="overflow-hidden rounded border border-green-200">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-green-100 text-gray-600">
                    <th className="px-3 py-1.5 text-left">{t("measurementEntry.result.col.item")}</th>
                    <th className="px-3 py-1.5 text-right">{t("measurementEntry.result.col.measured")}</th>
                    <th className="px-3 py-1.5 text-right">{t("measurementEntry.result.col.lower")}</th>
                    <th className="px-3 py-1.5 text-right">{t("measurementEntry.result.col.upper")}</th>
                    <th className="px-3 py-1.5 text-center">{t("measurementEntry.result.col.spec")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-green-100">
                  {result.values.map((v) => (
                    <tr
                      key={v.item_code}
                      className={v.is_within_spec ? "bg-white" : "bg-red-50"}
                    >
                      <td className="px-3 py-1.5 font-mono font-medium text-gray-800">{v.item_code}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{v.measured_value}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums text-gray-500">{v.lower_limit ?? "—"}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums text-gray-500">{v.upper_limit ?? "—"}</td>
                      <td className="px-3 py-1.5 text-center">
                        {v.is_within_spec ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                            <CheckCircle2 className="h-3 w-3" />
                            {t("measurementEntry.result.pass")}
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                            <AlertTriangle className="h-3 w-3" />
                            {t("measurementEntry.result.fail")}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

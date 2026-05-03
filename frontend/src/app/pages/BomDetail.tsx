import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router";
import { ArrowLeft, FileText, Lock } from "lucide-react";
import { BackendRequiredNotice, MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { HttpError } from "@/app/api";
import { useI18n } from "@/app/i18n";
import { productApi } from "@/app/api/productApi";
import type { BomFromAPI, BomItemCreateRequest, BomItemUpdateRequest, BomUpdateRequest } from "@/app/api/productApi";

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toUpperCase();
  const map: Record<string, string> = {
    RELEASED: "bg-green-100 text-green-800 border-green-200",
    DRAFT: "bg-yellow-100 text-yellow-800 border-yellow-200",
    RETIRED: "bg-gray-100 text-gray-600 border-gray-200",
  };
  const cls = map[normalized] ?? "bg-gray-100 text-gray-600 border-gray-200";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}

export function BomDetail() {
  const { t } = useI18n();
  const { bomId } = useParams<{ bomId: string }>();
  const [searchParams] = useSearchParams();
  const productId = searchParams.get("productId") ?? "";

  const [bom, setBom] = useState<BomFromAPI | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionBusy, setActionBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const [metaEditOpen, setMetaEditOpen] = useState(false);
  const [metaForm, setMetaForm] = useState({
    bomName: "",
    effectiveFrom: "",
    effectiveTo: "",
    description: "",
  });

  const [itemCreateOpen, setItemCreateOpen] = useState(false);
  const [itemCreateForm, setItemCreateForm] = useState({
    componentProductId: "",
    lineNo: "",
    quantity: "",
    unitOfMeasure: "PCS",
    scrapFactor: "",
    referenceDesignator: "",
    notes: "",
  });

  const [editingItemId, setEditingItemId] = useState<string | null>(null);
  const [itemEditForm, setItemEditForm] = useState({
    quantity: "",
    unitOfMeasure: "",
    scrapFactor: "",
    referenceDesignator: "",
    notes: "",
  });

  const resolveWriteError = (err: unknown): string => {
    if (err instanceof HttpError) {
      if (err.status === 401) return t("bomWrite.error.unauthorized");
      if (err.status === 403) return t("bomWrite.error.manageForbidden");
      if (err.status === 404) return t("bomWrite.error.notFound");
      if (err.status === 409) return t("bomWrite.error.conflict");
      if (err.status === 422) return t("bomWrite.error.validation");
      if (typeof err.message === "string" && err.message.trim().length > 0) return err.message;
    }
    return t("bomWrite.error.actionFailed");
  };

  const resetMetaForm = (row: BomFromAPI) => {
    setMetaForm({
      bomName: row.bom_name ?? "",
      effectiveFrom: row.effective_from ?? "",
      effectiveTo: row.effective_to ?? "",
      description: row.description ?? "",
    });
  };

  const loadBom = async (signal?: AbortSignal) => {
    if (!productId || !bomId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await productApi.getProductBom(productId, bomId, signal);
      setBom(data);
      if (!metaEditOpen) {
        resetMetaForm(data);
      }
    } catch (err: unknown) {
      if ((err as { name?: string })?.name === "AbortError") return;
      if (err instanceof HttpError) {
        if (err.status === 401) {
          setError("unauthorized");
        } else if (err.status === 403) {
          setError("forbidden");
        } else if (err.status === 404) {
          setError("notFound");
        } else {
          setError("load");
        }
      } else {
        setError("load");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!productId || !bomId) return;
    const controller = new AbortController();
    void loadBom(controller.signal);
    return () => controller.abort();
  }, [productId, bomId]);

  const runAction = async (action: () => Promise<void>, successMessage: string) => {
    setActionBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      await action();
      setActionMessage(successMessage);
      await loadBom();
    } catch (err: unknown) {
      setActionError(resolveWriteError(err));
    } finally {
      setActionBusy(false);
    }
  };

  const submitMetadataUpdate = async () => {
    if (!bom || !productId) return;
    if (!metaForm.bomName.trim()) {
      setActionError(t("bomWrite.error.required"));
      return;
    }
    if (metaForm.effectiveFrom && metaForm.effectiveTo && metaForm.effectiveFrom > metaForm.effectiveTo) {
      setActionError(t("bomWrite.error.effectiveRange"));
      return;
    }

    const payload: BomUpdateRequest = {
      bom_name: metaForm.bomName.trim() || null,
      effective_from: metaForm.effectiveFrom || null,
      effective_to: metaForm.effectiveTo || null,
      description: metaForm.description.trim() || null,
    };

    await runAction(
      async () => {
        await productApi.updateProductBom(productId, bom.bom_id, payload);
        setMetaEditOpen(false);
      },
      t("bomWrite.success.updated"),
    );
  };

  const submitAddItem = async () => {
    if (!bom || !productId) return;
    const lineNo = Number(itemCreateForm.lineNo);
    const quantity = Number(itemCreateForm.quantity);

    if (!itemCreateForm.componentProductId.trim() || !itemCreateForm.unitOfMeasure.trim()) {
      setActionError(t("bomWrite.error.required"));
      return;
    }
    if (!Number.isFinite(lineNo) || lineNo <= 0 || !Number.isInteger(lineNo)) {
      setActionError(t("bomWrite.error.invalidLineNo"));
      return;
    }
    if (!Number.isFinite(quantity) || quantity <= 0) {
      setActionError(t("bomWrite.error.invalidQuantity"));
      return;
    }

    let scrapFactor: number | null | undefined = null;
    if (itemCreateForm.scrapFactor.trim()) {
      const parsed = Number(itemCreateForm.scrapFactor);
      if (!Number.isFinite(parsed) || parsed < 0) {
        setActionError(t("bomWrite.error.invalidScrap"));
        return;
      }
      scrapFactor = parsed;
    }

    const payload: BomItemCreateRequest = {
      component_product_id: itemCreateForm.componentProductId.trim(),
      line_no: lineNo,
      quantity,
      unit_of_measure: itemCreateForm.unitOfMeasure.trim(),
      scrap_factor: scrapFactor,
      reference_designator: itemCreateForm.referenceDesignator.trim() || null,
      notes: itemCreateForm.notes.trim() || null,
    };

    await runAction(
      async () => {
        await productApi.addProductBomItem(productId, bom.bom_id, payload);
        setItemCreateOpen(false);
        setItemCreateForm({
          componentProductId: "",
          lineNo: "",
          quantity: "",
          unitOfMeasure: "PCS",
          scrapFactor: "",
          referenceDesignator: "",
          notes: "",
        });
      },
      t("bomWrite.success.itemAdded"),
    );
  };

  const startItemEdit = (item: BomFromAPI["items"][number]) => {
    setEditingItemId(item.bom_item_id);
    setItemEditForm({
      quantity: String(item.quantity ?? ""),
      unitOfMeasure: item.unit_of_measure ?? "",
      scrapFactor: item.scrap_factor == null ? "" : String(item.scrap_factor),
      referenceDesignator: item.reference_designator ?? "",
      notes: item.notes ?? "",
    });
    setActionError(null);
  };

  const submitItemEdit = async (bomItemId: string) => {
    if (!bom || !productId) return;
    const quantity = Number(itemEditForm.quantity);

    if (!Number.isFinite(quantity) || quantity <= 0 || !itemEditForm.unitOfMeasure.trim()) {
      setActionError(t("bomWrite.error.required"));
      return;
    }

    let scrapFactor: number | null | undefined = null;
    if (itemEditForm.scrapFactor.trim()) {
      const parsed = Number(itemEditForm.scrapFactor);
      if (!Number.isFinite(parsed) || parsed < 0) {
        setActionError(t("bomWrite.error.invalidScrap"));
        return;
      }
      scrapFactor = parsed;
    }

    const payload: BomItemUpdateRequest = {
      quantity,
      unit_of_measure: itemEditForm.unitOfMeasure.trim(),
      scrap_factor: scrapFactor,
      reference_designator: itemEditForm.referenceDesignator.trim() || null,
      notes: itemEditForm.notes.trim() || null,
    };

    await runAction(
      async () => {
        await productApi.updateProductBomItem(productId, bom.bom_id, bomItemId, payload);
        setEditingItemId(null);
      },
      t("bomWrite.success.itemUpdated"),
    );
  };

  const removeItem = async (bomItemId: string) => {
    if (!bom || !productId) return;
    if (!confirm(t("bomWrite.confirm.removeItem"))) return;
    await runAction(
      async () => {
        await productApi.removeProductBomItem(productId, bom.bom_id, bomItemId);
      },
      t("bomWrite.success.itemRemoved"),
    );
  };

  const canEditMetadata = bom?.lifecycle_status === "DRAFT";
  const canRelease = bom?.lifecycle_status === "DRAFT";
  const canRetire = bom?.lifecycle_status === "DRAFT" || bom?.lifecycle_status === "RELEASED";
  const canMutateItems = bom?.lifecycle_status === "DRAFT";

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="PARTIAL"
        note="BOM component truth is loaded from backend MMD API. Backend remains authorization and lifecycle source of truth."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        <div className="mb-4">
          <Link to="/bom" className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
            <ArrowLeft className="w-4 h-4" />
            {t("bomDetail.back")}
          </Link>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("bomDetail.title")}</h1>
            <ScreenStatusBadge phase="PARTIAL" />
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled={!canRelease || actionBusy}
              onClick={() => {
                if (!bom || !productId) return;
                void runAction(
                  async () => {
                    await productApi.releaseProductBom(productId, bom.bom_id);
                  },
                  t("bomWrite.success.released"),
                );
              }}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm border ${
                !canRelease || actionBusy
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed border-gray-200"
                  : "bg-emerald-600 text-white hover:bg-emerald-700 border-emerald-700"
              }`}
            >
              {canRelease ? null : <Lock className="w-3.5 h-3.5" />}
              {t("bomDetail.action.release")}
            </button>
            <button
              disabled={!canRetire || actionBusy}
              onClick={() => {
                if (!bom || !productId) return;
                void runAction(
                  async () => {
                    await productApi.retireProductBom(productId, bom.bom_id);
                  },
                  t("bomWrite.success.retired"),
                );
              }}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm border ${
                !canRetire || actionBusy
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed border-gray-200"
                  : "bg-orange-600 text-white hover:bg-orange-700 border-orange-700"
              }`}
            >
              {canRetire ? null : <Lock className="w-3.5 h-3.5" />}
              {t("bomDetail.action.retire")}
            </button>
            <button
              disabled={!canEditMetadata || actionBusy}
              onClick={() => {
                if (!bom) return;
                setMetaEditOpen((v) => !v);
                resetMetaForm(bom);
                setActionError(null);
              }}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm border ${
                !canEditMetadata || actionBusy
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed border-gray-200"
                  : "bg-blue-600 text-white hover:bg-blue-700 border-blue-700"
              }`}
            >
              {canEditMetadata ? null : <Lock className="w-3.5 h-3.5" />}
              {t("bomDetail.action.edit")}
            </button>
          </div>
        </div>

        <BackendRequiredNotice message={t("bomWrite.notice.backendAuth")} tone="blue" />

        {!productId && (
          <div className="mt-4 p-6 text-center text-gray-400 border border-gray-200 rounded-lg">
            {t("bomDetail.notice.productContextRequired")}
          </div>
        )}

        {loading && <p className="mt-4 text-sm text-gray-500">{t("bomDetail.loading")}</p>}

        {!loading && error && (
          <div className="mt-4 p-4 border border-red-200 rounded-lg bg-red-50">
            <p className="text-sm text-red-700">
              {error === "notFound"
                ? t("bomDetail.error.notFound")
                : error === "unauthorized"
                  ? t("bomList.error.unauthorized")
                  : error === "forbidden"
                    ? t("bomList.error.forbidden")
                    : t("bomDetail.error.load")}
            </p>
          </div>
        )}

        {actionMessage && (
          <div className="mt-4 rounded border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800">{actionMessage}</div>
        )}
        {actionError && (
          <div className="mt-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{actionError}</div>
        )}

        {bom && !loading && !error && (
          <>
            <div className="mb-6 mt-4">
              <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">{t("bomDetail.section.header")}</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.bomCode")}</div>
                  <div className="font-mono text-sm font-medium text-slate-700">{bom.bom_code}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.bomName")}</div>
                  <div className="text-sm text-slate-900">{bom.bom_name}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.status")}</div>
                  <StatusBadge status={bom.lifecycle_status} />
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomDetail.field.effectiveFrom")}</div>
                  <div className="text-sm text-slate-700">{bom.effective_from ?? "-"}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomDetail.field.effectiveTo")}</div>
                  <div className="text-sm text-slate-700">{bom.effective_to ?? "-"}</div>
                </div>
                {bom.description && (
                  <div className="col-span-2 md:col-span-3">
                    <div className="text-xs text-gray-500 mb-1">{t("bomDetail.field.description")}</div>
                    <div className="text-sm text-slate-700">{bom.description}</div>
                  </div>
                )}
              </div>
            </div>

            {metaEditOpen && canEditMetadata && (
              <div className="mb-5 rounded-lg border border-blue-200 bg-blue-50 p-4">
                <h3 className="text-sm font-semibold text-blue-900 mb-3">{t("bomWrite.action.updateMetadata")}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input
                    value={metaForm.bomName}
                    onChange={(e) => setMetaForm((prev) => ({ ...prev, bomName: e.target.value }))}
                    placeholder={t("bomWrite.field.bomName")}
                    className="rounded border border-blue-200 px-3 py-2 text-sm"
                  />
                  <div />
                  <input
                    type="date"
                    value={metaForm.effectiveFrom}
                    onChange={(e) => setMetaForm((prev) => ({ ...prev, effectiveFrom: e.target.value }))}
                    className="rounded border border-blue-200 px-3 py-2 text-sm"
                  />
                  <input
                    type="date"
                    value={metaForm.effectiveTo}
                    onChange={(e) => setMetaForm((prev) => ({ ...prev, effectiveTo: e.target.value }))}
                    className="rounded border border-blue-200 px-3 py-2 text-sm"
                  />
                  <textarea
                    value={metaForm.description}
                    onChange={(e) => setMetaForm((prev) => ({ ...prev, description: e.target.value }))}
                    placeholder={t("bomWrite.field.description")}
                    className="md:col-span-2 rounded border border-blue-200 px-3 py-2 text-sm"
                    rows={2}
                  />
                </div>
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={() => void submitMetadataUpdate()}
                    disabled={actionBusy}
                    className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                  >
                    {actionBusy ? t("bomWrite.action.saving") : t("bomWrite.action.submitUpdate")}
                  </button>
                  <button
                    onClick={() => setMetaEditOpen(false)}
                    disabled={actionBusy}
                    className="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed"
                  >
                    {t("bomWrite.action.cancel")}
                  </button>
                </div>
              </div>
            )}

            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">{t("bomDetail.section.components")}</h2>
                <button
                  disabled={!canMutateItems || actionBusy}
                  onClick={() => {
                    setItemCreateOpen((v) => !v);
                    setActionError(null);
                  }}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm border ${
                    !canMutateItems || actionBusy
                      ? "bg-gray-100 text-gray-400 cursor-not-allowed border-gray-200"
                      : "bg-blue-600 text-white hover:bg-blue-700 border-blue-700"
                  }`}
                >
                  {!canMutateItems ? <Lock className="w-3.5 h-3.5" /> : null}
                  {t("bomDetail.action.addComponent")}
                </button>
              </div>

              {itemCreateOpen && canMutateItems && (
                <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 p-4">
                  <h3 className="text-sm font-semibold text-blue-900 mb-3">{t("bomWrite.action.addItem")}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input
                      value={itemCreateForm.componentProductId}
                      onChange={(e) => setItemCreateForm((prev) => ({ ...prev, componentProductId: e.target.value }))}
                      placeholder={t("bomWrite.field.componentProductId")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={itemCreateForm.lineNo}
                      onChange={(e) => setItemCreateForm((prev) => ({ ...prev, lineNo: e.target.value }))}
                      placeholder={t("bomWrite.field.lineNo")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <input
                      type="number"
                      min={0.0001}
                      step={0.0001}
                      value={itemCreateForm.quantity}
                      onChange={(e) => setItemCreateForm((prev) => ({ ...prev, quantity: e.target.value }))}
                      placeholder={t("bomWrite.field.quantity")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <input
                      value={itemCreateForm.unitOfMeasure}
                      onChange={(e) => setItemCreateForm((prev) => ({ ...prev, unitOfMeasure: e.target.value }))}
                      placeholder={t("bomWrite.field.unitOfMeasure")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <input
                      type="number"
                      min={0}
                      step={0.0001}
                      value={itemCreateForm.scrapFactor}
                      onChange={(e) => setItemCreateForm((prev) => ({ ...prev, scrapFactor: e.target.value }))}
                      placeholder={t("bomWrite.field.scrapFactor")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <input
                      value={itemCreateForm.referenceDesignator}
                      onChange={(e) => setItemCreateForm((prev) => ({ ...prev, referenceDesignator: e.target.value }))}
                      placeholder={t("bomWrite.field.referenceDesignator")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <textarea
                      value={itemCreateForm.notes}
                      onChange={(e) => setItemCreateForm((prev) => ({ ...prev, notes: e.target.value }))}
                      placeholder={t("bomWrite.field.notes")}
                      rows={2}
                      className="md:col-span-3 rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                  </div>
                  <div className="mt-3 flex gap-2">
                    <button
                      onClick={() => void submitAddItem()}
                      disabled={actionBusy}
                      className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                    >
                      {actionBusy ? t("bomWrite.action.saving") : t("bomWrite.action.submitAddItem")}
                    </button>
                    <button
                      onClick={() => setItemCreateOpen(false)}
                      disabled={actionBusy}
                      className="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed"
                    >
                      {t("bomWrite.action.cancel")}
                    </button>
                  </div>
                </div>
              )}

              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.lineNo")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.componentId")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.quantity")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.uom")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.scrapFactor")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomWrite.col.actions")}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {bom.items.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-gray-400">{t("bomDetail.empty")}</td>
                      </tr>
                    ) : (
                      bom.items.map((c) => (
                        <tr key={c.bom_item_id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-slate-500 font-mono text-xs">{c.line_no}</td>
                          <td className="px-4 py-3 font-mono text-xs text-slate-700">{c.component_product_id}</td>
                          <td className="px-4 py-3 text-slate-700">{c.quantity}</td>
                          <td className="px-4 py-3 text-slate-600">{c.unit_of_measure}</td>
                          <td className="px-4 py-3 text-slate-600">{c.scrap_factor != null ? `${c.scrap_factor}%` : "-"}</td>
                          <td className="px-4 py-3">
                            {canMutateItems ? (
                              <div className="flex gap-2">
                                <button
                                  onClick={() => startItemEdit(c)}
                                  disabled={actionBusy}
                                  className="rounded border border-blue-200 bg-white px-2 py-1 text-xs text-blue-700 hover:bg-blue-50 disabled:cursor-not-allowed"
                                >
                                  {t("bomWrite.action.editItem")}
                                </button>
                                <button
                                  onClick={() => void removeItem(c.bom_item_id)}
                                  disabled={actionBusy}
                                  className="rounded border border-red-200 bg-white px-2 py-1 text-xs text-red-700 hover:bg-red-50 disabled:cursor-not-allowed"
                                >
                                  {t("bomWrite.action.removeItem")}
                                </button>
                              </div>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-xs text-gray-400">
                                <Lock className="w-3 h-3" />
                                {t("bomWrite.state.locked")}
                              </span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {editingItemId && canMutateItems && (
                <div className="mt-4 rounded-lg border border-blue-200 bg-blue-50 p-4">
                  <h3 className="text-sm font-semibold text-blue-900 mb-3">{t("bomWrite.action.updateItem")}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input
                      type="number"
                      min={0.0001}
                      step={0.0001}
                      value={itemEditForm.quantity}
                      onChange={(e) => setItemEditForm((prev) => ({ ...prev, quantity: e.target.value }))}
                      placeholder={t("bomWrite.field.quantity")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <input
                      value={itemEditForm.unitOfMeasure}
                      onChange={(e) => setItemEditForm((prev) => ({ ...prev, unitOfMeasure: e.target.value }))}
                      placeholder={t("bomWrite.field.unitOfMeasure")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <input
                      type="number"
                      min={0}
                      step={0.0001}
                      value={itemEditForm.scrapFactor}
                      onChange={(e) => setItemEditForm((prev) => ({ ...prev, scrapFactor: e.target.value }))}
                      placeholder={t("bomWrite.field.scrapFactor")}
                      className="rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <input
                      value={itemEditForm.referenceDesignator}
                      onChange={(e) => setItemEditForm((prev) => ({ ...prev, referenceDesignator: e.target.value }))}
                      placeholder={t("bomWrite.field.referenceDesignator")}
                      className="md:col-span-1 rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                    <textarea
                      value={itemEditForm.notes}
                      onChange={(e) => setItemEditForm((prev) => ({ ...prev, notes: e.target.value }))}
                      placeholder={t("bomWrite.field.notes")}
                      rows={2}
                      className="md:col-span-2 rounded border border-blue-200 px-3 py-2 text-sm"
                    />
                  </div>
                  <div className="mt-3 flex gap-2">
                    <button
                      onClick={() => void submitItemEdit(editingItemId)}
                      disabled={actionBusy}
                      className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                    >
                      {actionBusy ? t("bomWrite.action.saving") : t("bomWrite.action.submitUpdateItem")}
                    </button>
                    <button
                      onClick={() => setEditingItemId(null)}
                      disabled={actionBusy}
                      className="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed"
                    >
                      {t("bomWrite.action.cancel")}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

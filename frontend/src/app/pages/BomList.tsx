import { useEffect, useState } from "react";
import { Link } from "react-router";
import { Eye, FileText, Lock, Plus, Search, Upload } from "lucide-react";
import { BackendRequiredNotice, MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { HttpError } from "@/app/api";
import { useI18n } from "@/app/i18n";
import { productApi } from "@/app/api/productApi";
import type { BomCreateRequest, BomItemFromAPI, ProductItemFromAPI } from "@/app/api/productApi";

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

export function BomList() {
  const { t } = useI18n();
  const [products, setProducts] = useState<ProductItemFromAPI[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productsError, setProductsError] = useState<string | null>(null);

  const [selectedProductId, setSelectedProductId] = useState<string>("");
  const [boms, setBoms] = useState<BomItemFromAPI[]>([]);
  const [bomsLoading, setBomsLoading] = useState(false);
  const [bomsError, setBomsError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [createMessage, setCreateMessage] = useState<string | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createForm, setCreateForm] = useState({
    bomCode: "",
    bomName: "",
    effectiveFrom: "",
    effectiveTo: "",
    description: "",
  });

  const mapWriteError = (error: unknown): string => {
    if (error instanceof HttpError) {
      if (error.status === 401) return t("bomWrite.error.unauthorized");
      if (error.status === 403) return t("bomWrite.error.manageForbidden");
      if (error.status === 404) return t("bomWrite.error.notFound");
      if (error.status === 409) return t("bomWrite.error.conflict");
      if (error.status === 422) return t("bomWrite.error.validation");
      if (typeof error.message === "string" && error.message.trim().length > 0) return error.message;
    }
    return t("bomWrite.error.actionFailed");
  };

  const loadBoms = async (productId: string, signal?: AbortSignal) => {
    setBomsLoading(true);
    setBomsError(null);
    try {
      const data = await productApi.listProductBoms(productId, signal);
      setBoms(data);
    } catch (err: unknown) {
      if ((err as { name?: string })?.name === "AbortError") return;
      if (err instanceof HttpError) {
        if (err.status === 401) {
          setBomsError("unauthorized");
        } else if (err.status === 403) {
          setBomsError("forbidden");
        } else {
          setBomsError("load");
        }
      } else {
        setBomsError("load");
      }
    } finally {
      setBomsLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    setProductsLoading(true);
    setProductsError(null);
    productApi
      .listProducts(controller.signal)
      .then((data) => {
        setProducts(data);
        setProductsLoading(false);
      })
      .catch((err) => {
        if (err?.name === "AbortError") return;
        if (err?.status === 401) {
          setProductsError("unauthorized");
        } else if (err?.status === 403) {
          setProductsError("forbidden");
        } else {
          setProductsError("load");
        }
        setProductsLoading(false);
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!selectedProductId) {
      setBoms([]);
      setBomsError(null);
      return;
    }
    const controller = new AbortController();
    void loadBoms(selectedProductId, controller.signal);
    return () => controller.abort();
  }, [selectedProductId]);

  const onSubmitCreate = async () => {
    if (!selectedProductId) return;
    setCreateError(null);
    setCreateMessage(null);

    if (!createForm.bomCode.trim() || !createForm.bomName.trim()) {
      setCreateError(t("bomWrite.error.required"));
      return;
    }
    if (createForm.effectiveFrom && createForm.effectiveTo && createForm.effectiveFrom > createForm.effectiveTo) {
      setCreateError(t("bomWrite.error.effectiveRange"));
      return;
    }

    const payload: BomCreateRequest = {
      bom_code: createForm.bomCode.trim(),
      bom_name: createForm.bomName.trim(),
      effective_from: createForm.effectiveFrom || null,
      effective_to: createForm.effectiveTo || null,
      description: createForm.description.trim() || null,
    };

    setCreateSubmitting(true);
    try {
      await productApi.createProductBom(selectedProductId, payload);
      setCreateMessage(t("bomWrite.success.created"));
      setCreateOpen(false);
      setCreateForm({ bomCode: "", bomName: "", effectiveFrom: "", effectiveTo: "", description: "" });
      await loadBoms(selectedProductId);
    } catch (error: unknown) {
      setCreateError(mapWriteError(error));
    } finally {
      setCreateSubmitting(false);
    }
  };

  const filtered = boms.filter(
    (b) =>
      b.bom_code.toLowerCase().includes(search.toLowerCase()) ||
      b.bom_name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="PARTIAL"
        note="BOM definitions are loaded from backend manufacturing master data API. Product context is required for BOM lookup."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("bomList.title")}</h1>
            <ScreenStatusBadge phase="PARTIAL" />
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
              title={t("bomWrite.notice.backendAuth")}
            >
              <Lock className="w-3.5 h-3.5" />
              <Upload className="w-3.5 h-3.5" />
              {t("bomList.action.import")}
            </button>
            <button
              disabled={!selectedProductId || createSubmitting}
              onClick={() => {
                setCreateOpen((v) => !v);
                setCreateError(null);
                setCreateMessage(null);
              }}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm border ${
                !selectedProductId || createSubmitting
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed border-gray-200"
                  : "bg-blue-600 text-white hover:bg-blue-700 border-blue-700"
              }`}
              title={!selectedProductId ? t("bomWrite.notice.selectProductFirst") : t("bomWrite.action.create")}
            >
              <Plus className="w-3.5 h-3.5" />
              {t("bomList.action.create")}
            </button>
          </div>
        </div>

        <BackendRequiredNotice message={t("bomList.notice.backendRead")} tone="blue" />
        <p className="mt-3 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
          {t("bomWrite.notice.backendAuth")}
        </p>

        {createMessage && (
          <div className="mt-3 rounded border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800">
            {createMessage}
          </div>
        )}

        {createOpen && selectedProductId && (
          <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50 p-4">
            <h2 className="mb-3 text-sm font-semibold text-blue-900">{t("bomWrite.action.create")}</h2>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <input
                value={createForm.bomCode}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, bomCode: e.target.value }))}
                placeholder={t("bomWrite.field.bomCode")}
                className="rounded border border-blue-200 px-3 py-2 text-sm"
              />
              <input
                value={createForm.bomName}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, bomName: e.target.value }))}
                placeholder={t("bomWrite.field.bomName")}
                className="rounded border border-blue-200 px-3 py-2 text-sm"
              />
              <input
                type="date"
                value={createForm.effectiveFrom}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, effectiveFrom: e.target.value }))}
                className="rounded border border-blue-200 px-3 py-2 text-sm"
              />
              <input
                type="date"
                value={createForm.effectiveTo}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, effectiveTo: e.target.value }))}
                className="rounded border border-blue-200 px-3 py-2 text-sm"
              />
              <textarea
                value={createForm.description}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, description: e.target.value }))}
                placeholder={t("bomWrite.field.description")}
                className="md:col-span-2 rounded border border-blue-200 px-3 py-2 text-sm"
                rows={2}
              />
            </div>
            {createError && <p className="mt-3 text-sm text-red-700">{createError}</p>}
            <div className="mt-3 flex items-center gap-2">
              <button
                onClick={() => void onSubmitCreate()}
                disabled={createSubmitting}
                className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
              >
                {createSubmitting ? t("bomWrite.action.saving") : t("bomWrite.action.submitCreate")}
              </button>
              <button
                onClick={() => setCreateOpen(false)}
                disabled={createSubmitting}
                className="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed"
              >
                {t("bomWrite.action.cancel")}
              </button>
            </div>
          </div>
        )}

        <div className="mb-4 mt-3">
          {productsLoading ? (
            <p className="text-sm text-gray-500">{t("bomList.loading")}</p>
          ) : productsError ? (
            <p className="text-sm text-red-600">
              {productsError === "unauthorized"
                ? t("bomList.error.unauthorized")
                : productsError === "forbidden"
                  ? t("bomList.error.forbidden")
                  : t("bomList.error.load")}
            </p>
          ) : (
            <select
              value={selectedProductId}
              onChange={(e) => setSelectedProductId(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[260px]"
            >
              <option value="">{t("bomList.select.product.placeholder")}</option>
              {products.map((p) => (
                <option key={p.product_id} value={p.product_id}>
                  {p.product_code} - {p.product_name}
                </option>
              ))}
            </select>
          )}
        </div>

        {!selectedProductId && !productsLoading && !productsError && (
          <div className="p-6 text-center text-gray-400 border border-gray-200 rounded-lg">
            {t("bomList.notice.selectProduct")}
          </div>
        )}

        {selectedProductId && (
          <>
            <div className="flex items-center gap-2 mb-4">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={t("bomList.search.placeholder")}
                  className="w-full pl-9 pr-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {bomsLoading ? (
              <p className="text-sm text-gray-500">{t("bomList.loading")}</p>
            ) : bomsError ? (
              <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                <p className="text-sm text-red-700">
                  {bomsError === "unauthorized"
                    ? t("bomList.error.unauthorized")
                    : bomsError === "forbidden"
                      ? t("bomList.error.forbidden")
                      : t("bomList.error.load")}
                </p>
                <button onClick={() => void loadBoms(selectedProductId)} className="mt-2 text-xs text-blue-600 hover:underline">
                  {t("bomList.action.retry")}
                </button>
              </div>
            ) : (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.bomCode")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.bomName")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.status")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.updated")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filtered.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-gray-400">{t("bomList.empty")}</td>
                      </tr>
                    ) : (
                      filtered.map((bom) => (
                        <tr key={bom.bom_id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-mono text-xs font-medium text-slate-700">{bom.bom_code}</td>
                          <td className="px-4 py-3 text-slate-900">{bom.bom_name}</td>
                          <td className="px-4 py-3"><StatusBadge status={bom.lifecycle_status} /></td>
                          <td className="px-4 py-3 text-gray-400 text-xs">{new Date(bom.updated_at).toLocaleDateString()}</td>
                          <td className="px-4 py-3">
                            <Link
                              to={`/bom/${bom.bom_id}?productId=${encodeURIComponent(bom.product_id)}`}
                              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
                            >
                              <Eye className="w-3.5 h-3.5" />
                              {t("bomList.action.view")}
                            </Link>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import { Link } from "react-router";
import { Search, Plus, Upload, Lock, Eye, FileText } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { productApi } from "@/app/api/productApi";
import type { ProductItemFromAPI, BomItemFromAPI } from "@/app/api/productApi";

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
    setBomsLoading(true);
    setBomsError(null);
    productApi
      .listProductBoms(selectedProductId, controller.signal)
      .then((data) => {
        setBoms(data);
        setBomsLoading(false);
      })
      .catch((err) => {
        if (err?.name === "AbortError") return;
        if (err?.status === 401) {
          setBomsError("unauthorized");
        } else if (err?.status === 403) {
          setBomsError("forbidden");
        } else {
          setBomsError("load");
        }
        setBomsLoading(false);
      });
    return () => controller.abort();
  }, [selectedProductId]);

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
        {/* Header */}
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
              title="Backend MMD governance workflow required"
            >
              <Lock className="w-3.5 h-3.5" />
              {t("bomList.action.import")}
            </button>
            <button
              disabled
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
              title="Backend MMD governance workflow required"
            >
              <Lock className="w-3.5 h-3.5" />
              <Plus className="w-3.5 h-3.5" />
              {t("bomList.action.create")}
            </button>
          </div>
        </div>

        <BackendRequiredNotice
          message={t("bomList.notice.backendRead")}
          tone="blue"
        />

        {/* Product selector */}
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
                  {p.product_code} — {p.product_name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* No product selected */}
        {!selectedProductId && !productsLoading && !productsError && (
          <div className="p-6 text-center text-gray-400 border border-gray-200 rounded-lg">
            {t("bomList.notice.selectProduct")}
          </div>
        )}

        {/* BOMs section (only when product selected) */}
        {selectedProductId && (
          <>
            {/* Search */}
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
                <button
                  onClick={() => setSelectedProductId((id) => id)}
                  className="mt-2 text-xs text-blue-600 hover:underline"
                >
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
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
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

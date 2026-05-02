import { useState, useEffect } from "react";
import { Link, useParams, useSearchParams } from "react-router";
import { ArrowLeft, Lock, FileText } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { productApi } from "@/app/api/productApi";
import type { BomFromAPI } from "@/app/api/productApi";

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

  useEffect(() => {
    if (!productId || !bomId) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    productApi
      .getProductBom(productId, bomId, controller.signal)
      .then((data) => {
        setBom(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err?.name === "AbortError") return;
        if (err?.status === 401) {
          setError("unauthorized");
        } else if (err?.status === 403) {
          setError("forbidden");
        } else if (err?.status === 404) {
          setError("notFound");
        } else {
          setError("load");
        }
        setLoading(false);
      });
    return () => controller.abort();
  }, [productId, bomId]);

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="PARTIAL"
        note="BOM component truth is loaded from backend MMD API. All create/edit/release/retire actions require backend connection."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Back nav */}
        <div className="mb-4">
          <Link to="/bom" className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
            <ArrowLeft className="w-4 h-4" />
            {t("bomDetail.back")}
          </Link>
        </div>

        {/* Header row */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("bomDetail.title")}</h1>
            <ScreenStatusBadge phase="PARTIAL" />
          </div>
          <div className="flex items-center gap-2">
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("bomDetail.action.release")}
            </button>
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("bomDetail.action.retire")}
            </button>
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("bomDetail.action.edit")}
            </button>
          </div>
        </div>

        <BackendRequiredNotice message={t("bomDetail.notice.shell")} tone="blue" />

        {/* No product context */}
        {!productId && (
          <div className="mt-4 p-6 text-center text-gray-400 border border-gray-200 rounded-lg">
            {t("bomDetail.notice.productContextRequired")}
          </div>
        )}

        {/* Loading */}
        {productId && loading && (
          <p className="mt-4 text-sm text-gray-500">{t("bomDetail.loading")}</p>
        )}

        {/* Error */}
        {productId && !loading && error && (
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

        {/* BOM content */}
        {productId && !loading && !error && bom && (
          <>
            {/* BOM Header */}
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
                  <div className="text-sm text-slate-700">{bom.effective_from ?? "—"}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomDetail.field.effectiveTo")}</div>
                  <div className="text-sm text-slate-700">{bom.effective_to ?? "—"}</div>
                </div>
                {bom.description && (
                  <div className="col-span-2 md:col-span-3">
                    <div className="text-xs text-gray-500 mb-1">{t("bomDetail.field.description")}</div>
                    <div className="text-sm text-slate-700">{bom.description}</div>
                  </div>
                )}
              </div>
            </div>

            {/* BOM Components */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">{t("bomDetail.section.components")}</h2>
                <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
                  <Lock className="w-3.5 h-3.5" />
                  {t("bomDetail.action.addComponent")}
                </button>
              </div>
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.lineNo")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.componentId")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.quantity")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.uom")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.scrapFactor")}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {bom.items.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-gray-400">{t("bomDetail.empty")}</td>
                      </tr>
                    ) : (
                      bom.items.map((c) => (
                        <tr key={c.bom_item_id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-slate-500 font-mono text-xs">{c.line_no}</td>
                          <td className="px-4 py-3 font-mono text-xs text-slate-700">{c.component_product_id}</td>
                          <td className="px-4 py-3 text-slate-700">{c.quantity}</td>
                          <td className="px-4 py-3 text-slate-600">{c.unit_of_measure}</td>
                          <td className="px-4 py-3 text-slate-600">{c.scrap_factor != null ? `${c.scrap_factor}%` : "—"}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

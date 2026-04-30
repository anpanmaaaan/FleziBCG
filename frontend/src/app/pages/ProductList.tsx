import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { BackendRequiredNotice, PageHeader, ProductLifecycleBadge } from "@/app/components";
import { HttpError, productApi, type ProductItemFromAPI } from "@/app/api";
import { useI18n } from "@/app/i18n";

export function ProductList() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [products, setProducts] = useState<ProductItemFromAPI[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const resolveErrorMessage = (error: unknown): string => {
    if (error instanceof HttpError) {
      if (error.status === 401) {
        return t("productList.error.unauthorized");
      }
      if (error.status === 403) {
        return t("productList.error.forbidden");
      }
      if (typeof error.message === "string" && error.message.trim().length > 0) {
        return error.message;
      }
    }
    return t("productList.error.load");
  };

  const loadProducts = async (signal?: AbortSignal) => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const rows = await productApi.listProducts(signal);
      setProducts(rows);
    } catch (error) {
      if (signal?.aborted) {
        return;
      }
      setErrorMessage(resolveErrorMessage(error));
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    void loadProducts(controller.signal);
    return () => controller.abort();
  }, []);

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title={t("productList.title")}
        subtitle={t("productList.notice.shell")}
        actions={(
          <button
            type="button"
            disabled
            className="inline-flex items-center rounded-lg border border-gray-300 bg-gray-100 px-4 py-2 text-sm text-gray-500 cursor-not-allowed"
            title={t("productList.notice.shell")}
          >
            {t("productList.action.create")}
          </button>
        )}
      />

      <div className="flex-1 overflow-auto p-6 space-y-4">
        <BackendRequiredNotice message={t("productList.notice.shell")} tone="blue" />

        {loading && (
          <div className="rounded-lg border border-gray-200 bg-white px-4 py-10 text-center text-sm text-gray-500 shadow-sm">
            {t("productList.loading")}
          </div>
        )}

        {!loading && errorMessage && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-800 shadow-sm">
            <p>{errorMessage}</p>
            <button
              type="button"
              onClick={() => void loadProducts()}
              className="mt-3 inline-flex rounded border border-red-300 bg-white px-3 py-1.5 hover:bg-red-100"
            >
              {t("productList.action.retry")}
            </button>
          </div>
        )}

        {!loading && !errorMessage && (
          <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="w-full">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("productList.col.productCode")}</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("productList.col.productName")}</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("productList.col.lifecycle")}</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("productList.col.updated")}</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("productList.col.actions")}</th>
                </tr>
              </thead>
              <tbody>
                {products.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-10 text-center text-sm text-gray-500">
                      {t("productList.empty")}
                    </td>
                  </tr>
                )}

                {products.map((product) => (
                  <tr key={product.product_id} className="border-b last:border-b-0">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{product.product_code}</td>
                    <td className="px-4 py-3 text-sm text-gray-800">{product.product_name}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      <ProductLifecycleBadge value={product.lifecycle_status} />
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{new Date(product.updated_at).toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm">
                      <button
                        type="button"
                        onClick={() => navigate(`/products/${product.product_id}`)}
                        className="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50"
                      >
                        {t("productList.action.view")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

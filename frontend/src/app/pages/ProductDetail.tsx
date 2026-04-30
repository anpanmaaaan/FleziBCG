import { useEffect, useState } from "react";
import { useParams } from "react-router";
import {
  BackendRequiredNotice,
  PageHeader,
  ProductLifecycleBadge,
  ProductTypeBadge,
  ScreenStatusBadge,
} from "@/app/components";
import { HttpError, productApi, type ProductItemFromAPI } from "@/app/api";
import { useI18n } from "@/app/i18n";

export function ProductDetail() {
  const { t } = useI18n();
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<ProductItemFromAPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [missingProductId, setMissingProductId] = useState(false);

  const resolveErrorMessage = (error: unknown): string => {
    if (error instanceof HttpError) {
      if (error.status === 401) {
        return t("productDetail.error.unauthorized");
      }
      if (error.status === 403) {
        return t("productDetail.error.forbidden");
      }
      if (typeof error.message === "string" && error.message.trim().length > 0) {
        return error.message;
      }
    }
    return t("productDetail.error.load");
  };

  const loadProduct = async (signal?: AbortSignal) => {
    if (!productId) {
      setMissingProductId(true);
      setNotFound(false);
      setProduct(null);
      setErrorMessage(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setNotFound(false);
    setMissingProductId(false);
    try {
      const row = await productApi.getProduct(productId, signal);
      setProduct(row);
    } catch (error) {
      if (signal?.aborted) {
        return;
      }
      if (error instanceof HttpError && error.status === 404) {
        setNotFound(true);
        setProduct(null);
      } else {
        setErrorMessage(resolveErrorMessage(error));
        setProduct(null);
      }
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    const controller = new AbortController();

    void loadProduct(controller.signal);
    return () => controller.abort();
  }, [productId, t]);

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title={t("productDetail.title")}
        subtitle={t("productDetail.notice.shell")}
        showBackButton
        actions={(
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-500 bg-gray-100 cursor-not-allowed"
              title={t("productDetail.notice.shell")}
            >
              {t("productDetail.action.release")}
            </button>
            <button
              type="button"
              disabled
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-500 bg-gray-100 cursor-not-allowed"
              title={t("productDetail.notice.shell")}
            >
              {t("productDetail.action.retire")}
            </button>
          </div>
        )}
      />

      <div className="flex-1 overflow-auto p-6 space-y-4">
        <BackendRequiredNotice message={t("productDetail.notice.shell")} tone="blue" />

        {loading && (
          <div className="rounded-lg border border-gray-200 bg-white px-4 py-10 text-center text-sm text-gray-500 shadow-sm">
            {t("productDetail.loading")}
          </div>
        )}

        {!loading && missingProductId && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-10 text-center text-sm text-amber-900">
            {t("productDetail.missingProductId")}
          </div>
        )}

        {!loading && !missingProductId && notFound && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-10 text-center text-sm text-amber-900">
            {t("productDetail.notFound")}
          </div>
        )}

        {!loading && !missingProductId && !notFound && errorMessage && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-800 shadow-sm">
            <p>{errorMessage}</p>
            <button
              type="button"
              onClick={() => void loadProduct()}
              className="mt-3 inline-flex rounded border border-red-300 bg-white px-3 py-1.5 hover:bg-red-100"
            >
              {t("productDetail.action.retry")}
            </button>
          </div>
        )}

        {!loading && !missingProductId && !notFound && !errorMessage && product && (
          <>
            <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center gap-3 mb-3">
                <h2 className="text-base font-semibold text-gray-900">{t("productDetail.section.summary")}</h2>
                <ScreenStatusBadge phase="PARTIAL" size="sm" />
              </div>
              <div className="text-sm text-gray-700 mb-2">
                <span className="font-medium">{t("productDetail.field.productId")}: </span>
                <span>{product.product_id}</span>
              </div>
              <div className="text-sm text-gray-700 mb-2">
                <span className="font-medium">{t("productDetail.field.lifecycle")}: </span>
                <ProductLifecycleBadge value={product.lifecycle_status} />
              </div>
              <div className="text-sm text-gray-700 mb-2">
                <span className="font-medium">{t("productList.col.productCode")}: </span>
                <span>{product.product_code}</span>
              </div>
              <div className="text-sm text-gray-700 mb-2">
                <span className="font-medium">{t("productList.col.productName")}: </span>
                <span>{product.product_name}</span>
              </div>
              <div className="text-sm text-gray-700 mb-2">
                <span className="font-medium">{t("productDetail.field.productType")}: </span>
                <ProductTypeBadge value={product.product_type} />
              </div>
              <p className="text-sm text-gray-500">{t("productDetail.placeholder.summary")}</p>
            </div>

            <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <h2 className="text-base font-semibold text-gray-900 mb-3">{t("productDetail.section.routing")}</h2>
              <p className="text-sm text-gray-500">{t("productDetail.placeholder.routing")}</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

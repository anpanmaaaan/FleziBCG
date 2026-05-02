import { useEffect, useState } from "react";
import { useParams } from "react-router";
import {
  BackendRequiredNotice,
  PageHeader,
  ProductLifecycleBadge,
  ProductTypeBadge,
  ScreenStatusBadge,
} from "@/app/components";
import { HttpError, productApi, type ProductItemFromAPI, type ProductVersionItemFromAPI } from "@/app/api";
import { useI18n } from "@/app/i18n";

export function ProductDetail() {
  const { t } = useI18n();
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<ProductItemFromAPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [missingProductId, setMissingProductId] = useState(false);

  const [versions, setVersions] = useState<ProductVersionItemFromAPI[]>([]);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [versionsError, setVersionsError] = useState<string | null>(null);

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

  const loadVersions = async (signal?: AbortSignal) => {
    if (!productId) return;
    setVersionsLoading(true);
    setVersionsError(null);
    try {
      const rows = await productApi.listProductVersions(productId, signal);
      if (!signal?.aborted) {
        setVersions(rows);
      }
    } catch (error) {
      if (signal?.aborted) return;
      setVersionsError(t("productDetail.versions.error"));
    } finally {
      if (!signal?.aborted) {
        setVersionsLoading(false);
      }
    }
  };

  useEffect(() => {
    const controller = new AbortController();

    void loadProduct(controller.signal);
    void loadVersions(controller.signal);
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

            <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center gap-3 mb-3">
                <h2 className="text-base font-semibold text-gray-900">{t("productDetail.section.versions")}</h2>
                <ScreenStatusBadge phase="PARTIAL" size="sm" />
              </div>

              {versionsLoading && (
                <p className="text-sm text-gray-500">{t("productDetail.versions.loading")}</p>
              )}

              {!versionsLoading && versionsError && (
                <p className="text-sm text-red-600">{versionsError}</p>
              )}

              {!versionsLoading && !versionsError && versions.length === 0 && (
                <p className="text-sm text-gray-500">{t("productDetail.versions.empty")}</p>
              )}

              {!versionsLoading && !versionsError && versions.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left border-collapse">
                    <thead>
                      <tr className="border-b border-gray-200 text-gray-600">
                        <th className="py-2 pr-4 font-medium">{t("productDetail.versions.col.versionCode")}</th>
                        <th className="py-2 pr-4 font-medium">{t("productDetail.versions.col.versionName")}</th>
                        <th className="py-2 pr-4 font-medium">{t("productDetail.versions.col.lifecycle")}</th>
                        <th className="py-2 pr-4 font-medium">{t("productDetail.versions.col.isCurrent")}</th>
                        <th className="py-2 pr-4 font-medium">{t("productDetail.versions.col.effectiveFrom")}</th>
                        <th className="py-2 pr-4 font-medium">{t("productDetail.versions.col.effectiveTo")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {versions.map((v) => (
                        <tr key={v.product_version_id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 pr-4 font-mono text-xs text-gray-800">{v.version_code}</td>
                          <td className="py-2 pr-4 text-gray-700">{v.version_name ?? t("common.na")}</td>
                          <td className="py-2 pr-4">
                            <span className="inline-block rounded px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-700">
                              {v.lifecycle_status}
                            </span>
                          </td>
                          <td className="py-2 pr-4">
                            {v.is_current ? (
                              <span className="inline-block rounded px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700">
                                {t("common.yes")}
                              </span>
                            ) : (
                              <span className="text-gray-400 text-xs">{t("common.no")}</span>
                            )}
                          </td>
                          <td className="py-2 pr-4 text-gray-600">{v.effective_from ?? t("common.na")}</td>
                          <td className="py-2 pr-4 text-gray-600">{v.effective_to ?? t("common.na")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

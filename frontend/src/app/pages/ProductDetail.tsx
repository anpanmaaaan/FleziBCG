import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { toast } from "sonner";
import {
  BackendRequiredNotice,
  PageHeader,
  ProductLifecycleBadge,
  ProductTypeBadge,
  ScreenStatusBadge,
} from "@/app/components";
import {
  HttpError,
  productApi,
  type ProductItemFromAPI,
  type ProductVersionCreateRequest,
  type ProductVersionItemFromAPI,
  type ProductVersionUpdateRequest,
} from "@/app/api";
import { useI18n } from "@/app/i18n";

interface CreateVersionFormState {
  versionCode: string;
  versionName: string;
  effectiveFrom: string;
  effectiveTo: string;
  description: string;
}

interface EditVersionFormState {
  versionName: string;
  effectiveFrom: string;
  effectiveTo: string;
  description: string;
}

const EMPTY_CREATE_FORM: CreateVersionFormState = {
  versionCode: "",
  versionName: "",
  effectiveFrom: "",
  effectiveTo: "",
  description: "",
};

const EMPTY_EDIT_FORM: EditVersionFormState = {
  versionName: "",
  effectiveFrom: "",
  effectiveTo: "",
  description: "",
};

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
  const [versionActionError, setVersionActionError] = useState<string | null>(null);
  const [createForm, setCreateForm] = useState<CreateVersionFormState>(EMPTY_CREATE_FORM);
  const [editingVersionId, setEditingVersionId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<EditVersionFormState>(EMPTY_EDIT_FORM);
  const [mutationBusyKey, setMutationBusyKey] = useState<string | null>(null);

  const editingVersion = editingVersionId
    ? versions.find((version) => version.product_version_id === editingVersionId) ?? null
    : null;

  const normalizeOptionalText = (value: string): string | undefined => {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : undefined;
  };

  const normalizeOptionalDate = (value: string): string | undefined => {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : undefined;
  };

  const mapVersionDetailToMessage = (detail: unknown): string | null => {
    if (typeof detail !== "string") {
      return null;
    }

    switch (detail.trim()) {
      case "Product not found":
      case "Product version not found":
        return t("productDetail.versions.error.notFound");
      case "version_code is required":
        return t("productDetail.versions.error.versionCodeRequired");
      case "Duplicate version_code in product":
        return t("productDetail.versions.error.duplicateVersionCode");
      case "effective_from must be less than or equal to effective_to":
        return t("productDetail.versions.error.effectiveRange");
      case "Only DRAFT product versions can be updated":
        return t("productDetail.versions.error.updateDraftOnly");
      case "Only DRAFT product versions can be released":
        return t("productDetail.versions.error.releaseDraftOnly");
      case "Product version is already RETIRED":
        return t("productDetail.versions.error.alreadyRetired");
      case "Current product version cannot be retired":
        return t("productDetail.versions.error.currentRetireBlocked");
      case "Only DRAFT or RELEASED product versions can be retired":
        return t("productDetail.versions.error.retireLifecycleBlocked");
      default:
        return null;
    }
  };

  const resolveVersionActionError = (error: unknown): string => {
    if (error instanceof HttpError) {
      if (error.status === 401) {
        return t("productDetail.error.unauthorized");
      }
      if (error.status === 403) {
        return t("productDetail.versions.error.manageForbidden");
      }
      if (error.status === 404) {
        return t("productDetail.versions.error.notFound");
      }

      const mapped = mapVersionDetailToMessage(error.detail) ?? mapVersionDetailToMessage(error.message);
      if (mapped) {
        return mapped;
      }

      if (typeof error.message === "string" && error.message.trim().length > 0) {
        return error.message;
      }
    }

    return t("productDetail.versions.error.actionFailed");
  };

  const validateEffectiveRange = (effectiveFrom: string, effectiveTo: string): string | null => {
    if (effectiveFrom && effectiveTo && effectiveFrom > effectiveTo) {
      return t("productDetail.versions.error.effectiveRange");
    }
    return null;
  };

  const resetCreateForm = () => {
    setCreateForm(EMPTY_CREATE_FORM);
  };

  const beginEditVersion = (version: ProductVersionItemFromAPI) => {
    setEditingVersionId(version.product_version_id);
    setEditForm({
      versionName: version.version_name ?? "",
      effectiveFrom: version.effective_from ?? "",
      effectiveTo: version.effective_to ?? "",
      description: version.description ?? "",
    });
    setVersionActionError(null);
  };

  const cancelEditVersion = () => {
    setEditingVersionId(null);
    setEditForm(EMPTY_EDIT_FORM);
  };

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

  const createVersion = async () => {
    if (!productId) {
      return;
    }

    const versionCode = createForm.versionCode.trim();
    if (!versionCode) {
      setVersionActionError(t("productDetail.versions.error.versionCodeRequired"));
      return;
    }

    const rangeError = validateEffectiveRange(createForm.effectiveFrom, createForm.effectiveTo);
    if (rangeError) {
      setVersionActionError(rangeError);
      return;
    }

    const payload: ProductVersionCreateRequest = {
      version_code: versionCode,
      version_name: normalizeOptionalText(createForm.versionName),
      effective_from: normalizeOptionalDate(createForm.effectiveFrom),
      effective_to: normalizeOptionalDate(createForm.effectiveTo),
      description: normalizeOptionalText(createForm.description),
    };

    setMutationBusyKey("create");
    setVersionActionError(null);
    try {
      await productApi.createProductVersion(productId, payload);
      toast.success(t("productDetail.versions.success.created"));
      resetCreateForm();
      await loadVersions();
    } catch (error) {
      setVersionActionError(resolveVersionActionError(error));
    } finally {
      setMutationBusyKey(null);
    }
  };

  const saveVersionEdit = async () => {
    if (!productId || !editingVersionId) {
      return;
    }

    const rangeError = validateEffectiveRange(editForm.effectiveFrom, editForm.effectiveTo);
    if (rangeError) {
      setVersionActionError(rangeError);
      return;
    }

    const payload: ProductVersionUpdateRequest = {
      version_name: normalizeOptionalText(editForm.versionName),
      effective_from: normalizeOptionalDate(editForm.effectiveFrom),
      effective_to: normalizeOptionalDate(editForm.effectiveTo),
      description: normalizeOptionalText(editForm.description),
    };

    setMutationBusyKey(`edit:${editingVersionId}`);
    setVersionActionError(null);
    try {
      await productApi.updateProductVersion(productId, editingVersionId, payload);
      toast.success(t("productDetail.versions.success.updated"));
      cancelEditVersion();
      await loadVersions();
    } catch (error) {
      setVersionActionError(resolveVersionActionError(error));
    } finally {
      setMutationBusyKey(null);
    }
  };

  const releaseVersion = async (version: ProductVersionItemFromAPI) => {
    if (!productId) {
      return;
    }
    if (!window.confirm(t("productDetail.versions.confirm.release"))) {
      return;
    }

    setMutationBusyKey(`release:${version.product_version_id}`);
    setVersionActionError(null);
    try {
      await productApi.releaseProductVersion(productId, version.product_version_id);
      toast.success(t("productDetail.versions.success.released"));
      if (editingVersionId === version.product_version_id) {
        cancelEditVersion();
      }
      await loadVersions();
    } catch (error) {
      setVersionActionError(resolveVersionActionError(error));
    } finally {
      setMutationBusyKey(null);
    }
  };

  const retireVersion = async (version: ProductVersionItemFromAPI) => {
    if (!productId) {
      return;
    }
    if (!window.confirm(t("productDetail.versions.confirm.retire"))) {
      return;
    }

    setMutationBusyKey(`retire:${version.product_version_id}`);
    setVersionActionError(null);
    try {
      await productApi.retireProductVersion(productId, version.product_version_id);
      toast.success(t("productDetail.versions.success.retired"));
      if (editingVersionId === version.product_version_id) {
        cancelEditVersion();
      }
      await loadVersions();
    } catch (error) {
      setVersionActionError(resolveVersionActionError(error));
    } finally {
      setMutationBusyKey(null);
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

              <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
                <p>{t("productDetail.versions.notice.governance")}</p>
                <p className="mt-1 text-blue-800">{t("productDetail.versions.notice.editDraftOnly")}</p>
              </div>

              {versionActionError && (
                <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                  {versionActionError}
                </div>
              )}

              <div className="mb-5 rounded-lg border border-gray-200 bg-gray-50 p-4">
                <h3 className="text-sm font-semibold text-gray-900">{t("productDetail.versions.form.createTitle")}</h3>
                <div className="mt-3 grid gap-3 md:grid-cols-2">
                  <label className="block text-sm text-gray-700">
                    <span className="mb-1 block font-medium">{t("productDetail.versions.form.versionCode")}</span>
                    <input
                      type="text"
                      value={createForm.versionCode}
                      onChange={(event) => setCreateForm((current) => ({ ...current, versionCode: event.target.value }))}
                      placeholder={t("productDetail.versions.form.versionCodePlaceholder")}
                      className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                    />
                  </label>
                  <label className="block text-sm text-gray-700">
                    <span className="mb-1 block font-medium">{t("productDetail.versions.form.versionName")}</span>
                    <input
                      type="text"
                      value={createForm.versionName}
                      onChange={(event) => setCreateForm((current) => ({ ...current, versionName: event.target.value }))}
                      placeholder={t("productDetail.versions.form.versionNamePlaceholder")}
                      className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                    />
                  </label>
                  <label className="block text-sm text-gray-700">
                    <span className="mb-1 block font-medium">{t("productDetail.versions.form.effectiveFrom")}</span>
                    <input
                      type="date"
                      value={createForm.effectiveFrom}
                      onChange={(event) => setCreateForm((current) => ({ ...current, effectiveFrom: event.target.value }))}
                      className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                    />
                  </label>
                  <label className="block text-sm text-gray-700">
                    <span className="mb-1 block font-medium">{t("productDetail.versions.form.effectiveTo")}</span>
                    <input
                      type="date"
                      value={createForm.effectiveTo}
                      onChange={(event) => setCreateForm((current) => ({ ...current, effectiveTo: event.target.value }))}
                      className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                    />
                  </label>
                </div>
                <label className="mt-3 block text-sm text-gray-700">
                  <span className="mb-1 block font-medium">{t("productDetail.versions.form.description")}</span>
                  <textarea
                    value={createForm.description}
                    onChange={(event) => setCreateForm((current) => ({ ...current, description: event.target.value }))}
                    placeholder={t("productDetail.versions.form.descriptionPlaceholder")}
                    className="min-h-24 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                  />
                </label>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    onClick={() => void createVersion()}
                    disabled={mutationBusyKey !== null}
                    className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-gray-400"
                  >
                    {t("productDetail.versions.action.create")}
                  </button>
                  <button
                    type="button"
                    onClick={resetCreateForm}
                    disabled={mutationBusyKey !== null}
                    className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 disabled:cursor-not-allowed disabled:text-gray-400"
                  >
                    {t("productDetail.versions.action.clear")}
                  </button>
                </div>
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
                        <th className="py-2 pr-4 font-medium">{t("productDetail.versions.col.actions")}</th>
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
                          <td className="py-2 pr-4">
                            <div className="flex flex-wrap gap-2">
                              <button
                                type="button"
                                onClick={() => beginEditVersion(v)}
                                disabled={mutationBusyKey !== null || v.lifecycle_status !== "DRAFT"}
                                className="rounded border border-gray-300 bg-white px-2.5 py-1 text-xs font-medium text-gray-700 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-400"
                              >
                                {t("productDetail.versions.action.edit")}
                              </button>
                              <button
                                type="button"
                                onClick={() => void releaseVersion(v)}
                                disabled={mutationBusyKey !== null || v.lifecycle_status !== "DRAFT"}
                                className="rounded border border-blue-300 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 disabled:cursor-not-allowed disabled:border-gray-200 disabled:bg-gray-100 disabled:text-gray-400"
                              >
                                {t("productDetail.versions.action.release")}
                              </button>
                              <button
                                type="button"
                                onClick={() => void retireVersion(v)}
                                disabled={mutationBusyKey !== null || v.is_current || !["DRAFT", "RELEASED"].includes(v.lifecycle_status)}
                                className="rounded border border-amber-300 bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-800 disabled:cursor-not-allowed disabled:border-gray-200 disabled:bg-gray-100 disabled:text-gray-400"
                              >
                                {t("productDetail.versions.action.retire")}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {editingVersion && (
                <div className="mt-5 rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900">{t("productDetail.versions.form.editTitle")}</h3>
                      <p className="mt-1 text-xs text-gray-600">
                        {t("productDetail.versions.form.versionCodeReadonly")} <span className="font-mono">{editingVersion.version_code}</span>
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={cancelEditVersion}
                      disabled={mutationBusyKey !== null}
                      className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 disabled:cursor-not-allowed disabled:text-gray-400"
                    >
                      {t("productDetail.versions.action.cancelEdit")}
                    </button>
                  </div>

                  <div className="mt-3 grid gap-3 md:grid-cols-2">
                    <label className="block text-sm text-gray-700">
                      <span className="mb-1 block font-medium">{t("productDetail.versions.form.versionName")}</span>
                      <input
                        type="text"
                        value={editForm.versionName}
                        onChange={(event) => setEditForm((current) => ({ ...current, versionName: event.target.value }))}
                        placeholder={t("productDetail.versions.form.versionNamePlaceholder")}
                        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                      />
                    </label>
                    <div className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700">
                      <span className="block font-medium text-gray-900">{t("productDetail.versions.form.versionCode")}</span>
                      <span className="mt-1 block font-mono text-xs text-gray-800">{editingVersion.version_code}</span>
                    </div>
                    <label className="block text-sm text-gray-700">
                      <span className="mb-1 block font-medium">{t("productDetail.versions.form.effectiveFrom")}</span>
                      <input
                        type="date"
                        value={editForm.effectiveFrom}
                        onChange={(event) => setEditForm((current) => ({ ...current, effectiveFrom: event.target.value }))}
                        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                      />
                    </label>
                    <label className="block text-sm text-gray-700">
                      <span className="mb-1 block font-medium">{t("productDetail.versions.form.effectiveTo")}</span>
                      <input
                        type="date"
                        value={editForm.effectiveTo}
                        onChange={(event) => setEditForm((current) => ({ ...current, effectiveTo: event.target.value }))}
                        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                      />
                    </label>
                  </div>

                  <label className="mt-3 block text-sm text-gray-700">
                    <span className="mb-1 block font-medium">{t("productDetail.versions.form.description")}</span>
                    <textarea
                      value={editForm.description}
                      onChange={(event) => setEditForm((current) => ({ ...current, description: event.target.value }))}
                      placeholder={t("productDetail.versions.form.descriptionPlaceholder")}
                      className="min-h-24 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
                    />
                  </label>

                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={() => void saveVersionEdit()}
                      disabled={mutationBusyKey !== null}
                      className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-gray-400"
                    >
                      {t("productDetail.versions.action.saveEdit")}
                    </button>
                    <button
                      type="button"
                      onClick={cancelEditVersion}
                      disabled={mutationBusyKey !== null}
                      className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 disabled:cursor-not-allowed disabled:text-gray-400"
                    >
                      {t("productDetail.versions.action.cancelEdit")}
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

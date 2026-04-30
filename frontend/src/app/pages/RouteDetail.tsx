import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router";
import { HttpError, routingApi, type RoutingItemFromAPI } from "@/app/api";
import {
  BackendRequiredNotice,
  PageHeader,
  RoutingLifecycleBadge,
  RoutingOperationSequenceBadge,
} from "@/app/components";
import { useI18n } from "@/app/i18n";

export function RouteDetail() {
  const { t } = useI18n();
  const { routeId } = useParams<{ routeId: string }>();
  const [routing, setRouting] = useState<RoutingItemFromAPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [missingRouteId, setMissingRouteId] = useState(false);

  const resolveErrorMessage = (error: unknown): string => {
    if (error instanceof HttpError) {
      if (error.status === 401) {
        return t("routeDetail.error.unauthorized");
      }
      if (error.status === 403) {
        return t("routeDetail.error.forbidden");
      }
      if (typeof error.message === "string" && error.message.trim().length > 0) {
        return error.message;
      }
    }
    return t("routeDetail.error.load");
  };

  const loadRouting = async (signal?: AbortSignal) => {
    if (!routeId) {
      setMissingRouteId(true);
      setNotFound(false);
      setRouting(null);
      setErrorMessage(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setNotFound(false);
    setMissingRouteId(false);
    try {
      const row = await routingApi.getRouting(routeId, signal);
      setRouting(row);
    } catch (error) {
      if (signal?.aborted) {
        return;
      }
      if (error instanceof HttpError && error.status === 404) {
        setNotFound(true);
        setRouting(null);
      } else {
        setErrorMessage(resolveErrorMessage(error));
        setRouting(null);
      }
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    void loadRouting(controller.signal);
    return () => controller.abort();
  }, [routeId]);

  const sortedOperations = useMemo(() => {
    return [...(routing?.operations || [])].sort((a, b) => a.sequence_no - b.sequence_no);
  }, [routing]);

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title={t("routeDetail.title")}
        subtitle={t("routeDetail.notice.backendRequired")}
        showBackButton
        actions={(
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-500 bg-gray-100 cursor-not-allowed"
              title={t("routeDetail.notice.backendRequired")}
            >
              {t("routeDetail.action.save")}
            </button>
          </div>
        )}
      />

      <div className="flex-1 overflow-auto p-6 space-y-4">
        <BackendRequiredNotice message={t("routeDetail.notice.backendRequired")} tone="blue" />

        {loading && (
          <div className="rounded-lg border border-gray-200 bg-white px-4 py-10 text-center text-sm text-gray-500 shadow-sm">
            {t("routeDetail.loading")}
          </div>
        )}

        {!loading && missingRouteId && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-10 text-center text-sm text-amber-900">
            {t("routeDetail.missingRoutingId")}
          </div>
        )}

        {!loading && !missingRouteId && notFound && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-10 text-center text-sm text-amber-900">
            {t("routeDetail.notFound")}
          </div>
        )}

        {!loading && !missingRouteId && !notFound && errorMessage && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-800 shadow-sm">
            <p>{errorMessage}</p>
            <button
              type="button"
              onClick={() => void loadRouting()}
              className="mt-3 inline-flex rounded border border-red-300 bg-white px-3 py-1.5 hover:bg-red-100"
            >
              {t("routeDetail.action.retry")}
            </button>
          </div>
        )}

        {!loading && !missingRouteId && !notFound && !errorMessage && routing && (
          <>
            <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center gap-3 mb-3">
                <h2 className="text-base font-semibold text-gray-900">{routing.routing_name}</h2>
                <RoutingLifecycleBadge status={routing.lifecycle_status} />
              </div>
              <div className="text-sm text-gray-700 mb-2">
                <span className="font-medium">{t("routeDetail.field.routingId")}: </span>
                <span>{routing.routing_id}</span>
              </div>
              <div className="text-sm text-gray-700 mb-2">
                <span className="font-medium">{t("routeDetail.field.routingCode")}: </span>
                <span>{routing.routing_code}</span>
              </div>
              <div className="text-sm text-gray-700 mb-2">
                <span className="font-medium">{t("routeDetail.field.productId")}: </span>
                <span>{routing.product_id}</span>
              </div>
              <div className="text-sm text-gray-700">
                <span className="font-medium">{t("routeList.col.lastUpdated")}: </span>
                <span>{new Date(routing.updated_at).toLocaleString()}</span>
              </div>
            </div>

            <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <h2 className="text-base font-semibold text-gray-900 mb-3">{t("routeDetail.operations.title")}</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("routeDetail.col.seq")}</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("routeDetail.col.operation")}</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("routeDetail.col.stdTime")}</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">{t("routeDetail.col.workCenter")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedOperations.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-4 py-8 text-center text-sm text-gray-500">
                          {t("routeDetail.empty.operations")}
                        </td>
                      </tr>
                    )}
                    {sortedOperations.map((operation) => (
                      <tr key={operation.operation_id} className="border-b last:border-b-0">
                        <td className="px-4 py-3 text-sm text-gray-800">
                          <RoutingOperationSequenceBadge sequence={operation.sequence_no} />
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-800">
                          <div className="font-medium">{operation.operation_code}</div>
                          <div className="text-xs text-gray-600">{operation.operation_name}</div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-800">{operation.standard_cycle_time ?? "-"}</td>
                        <td className="px-4 py-3 text-sm text-gray-800">{operation.required_resource_type ?? "-"}</td>
                      </tr>
                    ))}
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

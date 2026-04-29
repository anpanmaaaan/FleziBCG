import { useEffect, useMemo, useState } from "react";
import { Download, Search } from "lucide-react";
import { useNavigate } from "react-router";
import { HttpError, routingApi, type RoutingItemFromAPI } from "@/app/api";
import { BackendRequiredNotice, RoutingLifecycleBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";

export function RouteList() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const [searchRoute, setSearchRoute] = useState("");
  const [routings, setRoutings] = useState<RoutingItemFromAPI[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const resolveErrorMessage = (error: unknown): string => {
    if (error instanceof HttpError) {
      if (error.status === 401) {
        return t("routeList.error.unauthorized");
      }
      if (error.status === 403) {
        return t("routeList.error.forbidden");
      }
      if (typeof error.message === "string" && error.message.trim().length > 0) {
        return error.message;
      }
    }
    return t("routeList.error.load");
  };

  const loadRoutings = async (signal?: AbortSignal) => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const rows = await routingApi.listRoutings(signal);
      setRoutings(rows);
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
    void loadRoutings(controller.signal);
    return () => controller.abort();
  }, []);

  const filteredRoutings = useMemo(() => {
    return routings.filter((routing) => {
      const q = searchRoute.trim().toLowerCase();
      if (!q) {
        return true;
      }
      return (
        routing.routing_code.toLowerCase().includes(q)
        || routing.routing_name.toLowerCase().includes(q)
      );
    });
  }, [routings, searchRoute]);

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="flex-1 overflow-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl">{t("routeList.title")}</h2>
          <button className="flex items-center gap-2 px-4 py-2 border rounded hover:bg-gray-50">
            <Download className="w-4 h-4" />
            <span>{t("routeList.action.export")}</span>
          </button>
        </div>

        <BackendRequiredNotice message={t("routeList.notice.backendRequired")} tone="amber" />

        {loading && (
          <div className="rounded-lg border bg-white px-4 py-10 text-center text-sm text-gray-500">
            {t("routeList.loading")}
          </div>
        )}

        {!loading && errorMessage && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-800">
            <p className="mb-3">{errorMessage}</p>
            <button
              type="button"
              onClick={() => void loadRoutings()}
              className="px-3 py-1.5 rounded border border-red-300 bg-white hover:bg-red-100"
            >
              {t("routeList.action.retry")}
            </button>
          </div>
        )}

        {!loading && !errorMessage && (
          <div className="border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left w-2/5">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm uppercase">{t("routeList.col.route")}</span>
                    </div>
                    <div className="relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                      <input
                        type="text"
                        placeholder={t("routeList.search.placeholder")}
                        value={searchRoute}
                        onChange={(e) => setSearchRoute(e.target.value)}
                        className="w-full pl-9 pr-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                      />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left w-1/5">
                    <div className="text-sm uppercase">{t("routeList.col.lastUpdated")}</div>
                  </th>
                  <th className="px-6 py-3 text-left w-1/5">
                    <div className="text-sm uppercase">{t("routeList.col.status")}</div>
                  </th>
                  <th className="px-6 py-3 text-left w-1/5">
                    <span className="text-sm uppercase">{t("routeList.col.action")}</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredRoutings.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-10 text-center text-sm text-gray-500">
                      {t("routeList.empty")}
                    </td>
                  </tr>
                )}

                {filteredRoutings.map((routing, index) => (
                  <tr key={routing.routing_id} className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{routing.routing_code}</div>
                      <div className="text-xs text-gray-600">{routing.routing_name}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">{new Date(routing.updated_at).toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <RoutingLifecycleBadge status={routing.lifecycle_status} />
                    </td>
                    <td className="px-6 py-4">
                      <button
                        type="button"
                        className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50"
                        onClick={() => navigate(`/routes/${routing.routing_id}`)}
                      >
                        {t("routeList.action.view")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        )}
      </div>
    </div>
  );
}
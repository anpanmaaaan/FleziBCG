import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router";
import { Lock, Server } from "lucide-react";
import { HttpError, routingApi, type ResourceRequirementItemFromAPI, type RoutingItemFromAPI, type RoutingOperationItemFromAPI } from "@/app/api";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface ResourceRequirementRow {
  requirement_id: string;
  operation_code: string;
  operation_name: string;
  routing_code: string;
  resource_type: string;
  capability: string;
  quantity_required: number;
  notes: string | null;
  status: string;
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    DRAFT: "bg-yellow-100 text-yellow-800 border-yellow-200",
    RELEASED: "bg-green-100 text-green-800 border-green-200",
    RETIRED: "bg-gray-100 text-gray-600 border-gray-200",
    ACTIVE: "bg-green-100 text-green-800 border-green-200",
    PENDING: "bg-yellow-100 text-yellow-800 border-yellow-200",
    INACTIVE: "bg-gray-100 text-gray-600 border-gray-200",
  };
  const cls = map[status.toUpperCase()] ?? "bg-gray-100 text-gray-600 border-gray-200";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}

export function ResourceRequirements() {
  const { t } = useI18n();
  const [searchParams] = useSearchParams();
  const [reqs, setReqs] = useState<ResourceRequirementRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const routeId = searchParams.get("routeId") ?? searchParams.get("routingId");
  const operationId = searchParams.get("operationId");

  const resolveErrorMessage = (error: unknown): string => {
    if (error instanceof HttpError && typeof error.message === "string" && error.message.trim().length > 0) {
      return error.message;
    }
    return t("common.error.load_failed");
  };

  const toRow = (
    requirement: ResourceRequirementItemFromAPI,
    routing: RoutingItemFromAPI,
    operation: RoutingOperationItemFromAPI,
  ): ResourceRequirementRow => ({
    requirement_id: requirement.requirement_id,
    operation_code: operation.operation_code,
    operation_name: operation.operation_name,
    routing_code: routing.routing_code,
    resource_type: requirement.required_resource_type,
    capability: requirement.required_capability_code,
    quantity_required: requirement.quantity_required,
    notes: requirement.notes ?? requirement.metadata_json ?? null,
    status: routing.lifecycle_status,
  });

  useEffect(() => {
    const controller = new AbortController();

    const loadRequirements = async () => {
      setLoading(true);
      setErrorMessage(null);

      try {
        // Guard impossible filter combinations early.
        if (operationId && !routeId) {
          setReqs([]);
          setErrorMessage(t("resourceReqs.error.invalidFilter"));
          return;
        }

        // Filtered mode: a specific routing and operation.
        if (routeId && operationId) {
          const routing = await routingApi.getRouting(routeId, controller.signal);
          const operation = routing.operations.find((item) => item.operation_id === operationId);

          if (!operation) {
            setReqs([]);
            return;
          }

          const requirements = await routingApi.listResourceRequirements(routeId, operationId, controller.signal);
          setReqs(requirements.map((item) => toRow(item, routing, operation)));
          return;
        }

        // Filtered mode: all operations in a specific routing.
        if (routeId) {
          const routing = await routingApi.getRouting(routeId, controller.signal);
          const nested = await Promise.all(
            routing.operations.map(async (operation) => {
              const requirements = await routingApi.listResourceRequirements(
                routing.routing_id,
                operation.operation_id,
                controller.signal,
              );
              return requirements.map((item) => toRow(item, routing, operation));
            }),
          );
          setReqs(nested.flat());
          return;
        }

        // Global mode: collect requirements for all operations in all routings.
        const routings = await routingApi.listRoutings(controller.signal);
        const nested = await Promise.all(
          routings.flatMap((routing) =>
            routing.operations.map(async (operation) => {
              const requirements = await routingApi.listResourceRequirements(
                routing.routing_id,
                operation.operation_id,
                controller.signal,
              );
              return requirements.map((item) => toRow(item, routing, operation));
            }),
          ),
        );

        const rows = nested.flat().sort((a, b) => {
          const byRouting = a.routing_code.localeCompare(b.routing_code);
          if (byRouting !== 0) {
            return byRouting;
          }
          const byOperation = a.operation_code.localeCompare(b.operation_code);
          if (byOperation !== 0) {
            return byOperation;
          }
          return a.requirement_id.localeCompare(b.requirement_id);
        });
        setReqs(rows);
      } catch (error) {
        if (controller.signal.aborted) {
          return;
        }
        setReqs([]);
        setErrorMessage(resolveErrorMessage(error));
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    void loadRequirements();
    return () => controller.abort();
  }, [routeId, operationId, t]);

  const scopeText = useMemo(() => {
    if (routeId && operationId) {
      return `${t("resourceReqs.scope.routing")}: ${routeId} | ${t("resourceReqs.scope.operation")}: ${operationId}`;
    }
    if (routeId) {
      return `${t("resourceReqs.scope.routing")}: ${routeId}`;
    }
    return t("resourceReqs.scope.global");
  }, [operationId, routeId, t]);

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="PARTIAL"
        note="Resource applicability and capability requirements are read from backend MMD APIs. Mutation actions remain backend-governed."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Server className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("resourceReqs.title")}</h1>
            <ScreenStatusBadge phase="PARTIAL" />
          </div>
          <button
            disabled
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
            title="Backend MMD governance workflow required"
          >
            <Lock className="w-3.5 h-3.5" />
            {t("resourceReqs.action.assign")}
          </button>
        </div>

        <BackendRequiredNotice message={t("resourceReqs.notice.read")} tone="blue" />

        {loading && (
          <div className="rounded-lg border border-gray-200 bg-white px-4 py-10 text-center text-sm text-gray-500 shadow-sm mb-4">
            {t("resourceReqs.loading")}
          </div>
        )}

        {!loading && errorMessage && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-800 shadow-sm mb-4">
            {errorMessage}
          </div>
        )}

        {/* Summary info */}
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
          <div className="flex items-center justify-between gap-4">
            <span><strong>{t("resourceReqs.scope.label")}:</strong> {scopeText}</span>
            {(routeId || operationId) && (
              <Link to="/resource-requirements" className="text-xs text-blue-600 hover:text-blue-800 font-medium shrink-0">
                {t("resourceReqs.action.clearFilter")}
              </Link>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="border border-gray-200 rounded-lg overflow-x-auto">
          <table className="w-full text-sm min-w-[900px]">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.operation")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.resource")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.capability")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.quantity")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.notes")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("resourceReqs.col.status")}</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {!loading && reqs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-400">{t("resourceReqs.empty")}</td>
                </tr>
              ) : (
                reqs.map((r) => (
                  <tr key={r.requirement_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900">{r.operation_name}</div>
                      <div className="text-xs text-gray-400 font-mono">{r.operation_code}</div>
                      <div className="text-xs text-gray-400">{r.routing_code}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-slate-900">{r.resource_type}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-0.5 rounded border text-xs bg-purple-50 text-purple-700 border-purple-200">{r.capability}</span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">{r.quantity_required}</td>
                    <td className="px-4 py-3 text-xs text-gray-600 max-w-[240px]">{r.notes ?? "—"}</td>
                    <td className="px-4 py-3"><StatusBadge status={r.status} /></td>
                    <td className="px-4 py-3">
                      <button disabled className="inline-flex items-center gap-1 text-xs text-gray-400 cursor-not-allowed" title="Backend MMD governance workflow required">
                        <Lock className="w-3 h-3" />
                        Edit
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <p className="mt-4 text-xs text-gray-400">
          {t("resourceReqs.footer.readonly")}
        </p>
      </div>
    </div>
  );
}

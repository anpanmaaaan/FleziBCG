import { useState, useMemo, useEffect } from "react";
import { Search, Settings, ArrowUpDown, Calendar } from "lucide-react";
import {
  BackendRequiredNotice,
  ColumnManagerDialog,
  ColumnConfig,
  PageHeader,
  StatusBadge,
} from "@/app/components";
import { toast } from "sonner";
import { HttpError, productionOrderApi } from "@/app/api";
import { useI18n } from "@/app/i18n";

interface ProductionOrderRow {
  id: string | number;
  serialNumber?: string;
  lotId?: string;
  customer?: string;
  productName?: string;
  routeId?: string;
  priority?: string;
  machineNumber?: string;
  quantity?: number;
  plannedStartDate?: string;
  plannedCompletionDate?: string;
  actualStartDate?: string;
  actualCompletionDate?: string;
  releasedDate?: string;
  assignee?: string;
  department?: string;
  status?: string;
  progress?: number | null;
  materialCode?: string;
}

const statusLabelMap: Record<string, string> = {
  PENDING: "common.status.pending",
  IN_PROGRESS: "common.status.inProgress",
  COMPLETED: "common.status.completed",
  LATE: "common.status.late",
  BLOCKED: "common.status.blocked",
};

function getStatusLabel(status: string | undefined, t: (key: string) => string) {
  if (!status) return "-";
  const key = statusLabelMap[status];
  return key ? t(key) : status;
}

function getStatusVariant(status?: string): "neutral" | "info" | "success" | "warning" | "error" {
  switch (status) {
    case "COMPLETED":
      return "success";
    case "IN_PROGRESS":
      return "info";
    case "LATE":
      return "warning";
    case "BLOCKED":
      return "error";
    default:
      return "neutral";
  }
}

function normalizeProductionOrder(order: ProductionOrderRow): ProductionOrderRow {
  return {
    id: order.id,
    serialNumber: order.serialNumber ?? "",
    lotId: order.lotId ?? "",
    customer: order.customer ?? "",
    productName: order.productName ?? "",
    routeId: order.routeId ?? "",
    priority: order.priority ?? "",
    machineNumber: order.machineNumber ?? "",
    quantity: order.quantity ?? 0,
    plannedStartDate: order.plannedStartDate ?? "",
    plannedCompletionDate: order.plannedCompletionDate ?? "",
    actualStartDate: order.actualStartDate ?? "",
    actualCompletionDate: order.actualCompletionDate ?? "",
    releasedDate: order.releasedDate ?? "",
    assignee: order.assignee ?? "",
    department: order.department ?? "",
    status: order.status ?? "PENDING",
    progress: order.progress ?? 0,
    materialCode: order.materialCode ?? "",
  };
}

const DEFAULT_COLUMNS: ColumnConfig[] = [
  { id: 'productionOrder', label: 'Production Order', visible: true, order: 0 },
  { id: 'serialNumber', label: 'Serial Number', visible: true, order: 1 },
  { id: 'lotId', label: 'LOT ID', visible: true, order: 2 },
  { id: 'customer', label: 'Customer', visible: true, order: 3 },
  { id: 'productName', label: 'Product Name', visible: false, order: 4 },
  { id: 'routeId', label: 'Route ID', visible: true, order: 5 },
  { id: 'priority', label: 'Priority', visible: true, order: 6 },
  { id: 'machineNumber', label: 'Machine Number', visible: false, order: 7 },
  { id: 'quantity', label: 'Quantity', visible: true, order: 8 },
  { id: 'plannedStartDate', label: 'Planned Start Date', visible: false, order: 9 },
  { id: 'plannedCompletion', label: 'Planned Completion', visible: true, order: 10 },
  { id: 'actualStartDate', label: 'Actual Start Date', visible: false, order: 11 },
  { id: 'actualCompletion', label: 'Actual Completion', visible: false, order: 12 },
  { id: 'releasedDate', label: 'Released Date', visible: true, order: 13 },
  { id: 'assignee', label: 'Assignee', visible: true, order: 14 },
  { id: 'department', label: 'Department', visible: false, order: 15 },
  { id: 'status', label: 'Status', visible: false, order: 16 },
  { id: 'progress', label: 'Progress', visible: false, order: 17 },
  { id: 'materialCode', label: 'Material Code', visible: false, order: 18 },
];

export function ProductionOrderList() {
  const { t } = useI18n();
  const [orders, setOrders] = useState<ProductionOrderRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [columnManagerOpen, setColumnManagerOpen] = useState(false);
  const [columns, setColumns] = useState<ColumnConfig[]>(DEFAULT_COLUMNS);
  const [searchValues, setSearchValues] = useState<Record<string, string>>({
    productionOrder: '',
    serialNumber: '',
    routeId: '',
  });

  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(30);

  const resolveErrorMessage = (err: unknown) => {
    if (err instanceof HttpError) {
      if (err.status === 401) {
        return t("poList.error.unauthorized");
      }
      if (err.status === 403) {
        return t("poList.error.forbidden");
      }
      if (typeof err.message === "string" && err.message.trim().length > 0) {
        return err.message;
      }
    }

    return t("poList.error.loadFailed");
  };

  // Sort columns by order
  const sortedColumns = useMemo(() => {
    return [...columns].sort((a, b) => a.order - b.order);
  }, [columns]);

  // Get visible columns
  const visibleColumns = useMemo(() => {
    return sortedColumns.filter(col => col.visible);
  }, [sortedColumns]);

  const filteredOrders = orders.filter(order => {
    return Object.keys(searchValues).every(key => {
      const value = searchValues[key];
      if (!value) return true;
      
      const orderValue = (order as any)[key];
      if (orderValue === undefined) return true;
      
      return String(orderValue).toLowerCase().includes(value.toLowerCase());
    });
  });

  const totalPages = Math.ceil(filteredOrders.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedOrders = filteredOrders.slice(startIndex, startIndex + itemsPerPage);

  const handleColumnSave = (newColumns: ColumnConfig[]) => {
    setColumns(newColumns);
    toast.success(t("poList.toast.columnsSaved"));
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'High': return 'text-red-600 bg-red-50';
      case 'Medium': return 'text-yellow-600 bg-yellow-50';
      case 'Low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const renderCellContent = (column: ColumnConfig, order: any) => {
    switch (column.id) {
      case 'productionOrder':
        return (
          <div>
            <div className="font-medium">{order.id}</div>
            <div className="text-sm text-gray-500">Route: {order.routeId}</div>
          </div>
        );
      case 'serialNumber':
        return order.serialNumber;
      case 'lotId':
        return order.lotId || '-';
      case 'customer':
        return order.customer || '-';
      case 'productName':
        return order.productName || '-';
      case 'routeId':
        return order.routeId;
      case 'priority':
        return order.priority ? (
          <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(order.priority)}`}>
            {order.priority}
          </span>
        ) : '-';
      case 'machineNumber':
        return order.machineNumber || '-';
      case 'quantity':
        return order.quantity?.toLocaleString();
      case 'plannedStartDate':
        return order.plannedStartDate || '-';
      case 'plannedCompletion':
        return order.plannedCompletionDate || '-';
      case 'actualStartDate':
        return order.actualStartDate || '-';
      case 'actualCompletion':
        return order.actualCompletionDate || '-';
      case 'releasedDate':
        return order.releasedDate || '-';
      case 'assignee':
        return order.assignee || '-';
      case 'department':
        return order.department || '-';
      case 'status':
        return <StatusBadge variant={getStatusVariant(order.status)} size="sm">{getStatusLabel(order.status, t)}</StatusBadge>;
      case 'progress':
        return (
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full" 
                style={{ width: `${order.progress ?? 0}%` }}
              />
            </div>
            <span className="text-xs text-gray-600">{order.progress ?? 0}%</span>
          </div>
        );
      case 'materialCode':
        return order.materialCode || '-';
      default:
        return '-';
    }
  };

  const loadOrders = async (signal?: AbortSignal) => {
      setLoading(true);
      setError(null);

      try {
        const data = await productionOrderApi.list();
        if (signal?.aborted) {
          return;
        }
        if (!Array.isArray(data)) {
          throw new Error('Unexpected response from production orders endpoint');
        }

        setOrders(data.map(normalizeProductionOrder));
      } catch (err) {
        if (signal?.aborted) {
          return;
        }
        const message = resolveErrorMessage(err);
        setError(message);
        toast.error(message);
      } finally {
        if (!signal?.aborted) {
          setLoading(false);
        }
      }
  };

  useEffect(() => {
    const controller = new AbortController();
    void loadOrders(controller.signal);
    return () => controller.abort();
  }, []);

  const visibleColumnsCount = visibleColumns.length;

  return (
    <div className="h-full flex flex-col bg-white">
      <PageHeader
        title={t("poList.title")}
        subtitle={t("poList.subtitle.readOnly")}
        actions={(
          <button
            type="button"
            onClick={() => setColumnManagerOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus-ring"
            aria-haspopup="dialog"
            aria-expanded={columnManagerOpen}
          >
            <Settings className="h-4 w-4" />
            <span>{t("poList.columns.button", { count: visibleColumnsCount })}</span>
          </button>
        )}
      />

      <div className="flex-1 overflow-auto p-6 space-y-4">
        <BackendRequiredNotice message={t("poList.notice.backendRead")} tone="blue" />

        {loading && (
          <div className="rounded-lg border border-gray-200 bg-white px-4 py-10 text-center text-sm text-gray-500 shadow-sm">
            {t("poList.loading")}
          </div>
        )}

        {!loading && error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-800 shadow-sm">
            <p>{error}</p>
            <button
              type="button"
              onClick={() => void loadOrders()}
              className="mt-3 inline-flex rounded border border-red-300 bg-white px-3 py-1.5 hover:bg-red-100"
            >
              {t("poList.action.retry")}
            </button>
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="overflow-hidden rounded-lg border border-gray-200 shadow-sm">
              <div className="overflow-x-auto bg-white">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      {visibleColumns.map((column) => (
                        <th key={column.id} className="px-4 py-3 text-left min-w-[180px]">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-sm uppercase font-semibold">{column.label}</span>
                            <ArrowUpDown className="w-4 h-4 cursor-pointer hover:text-blue-600" />
                          </div>
                          <div className="relative">
                            {column.id === 'plannedCompletion' || column.id === 'releasedDate' || 
                            column.id === 'plannedStartDate' || column.id === 'actualStartDate' || 
                            column.id === 'actualCompletion' ? (
                              <>
                                <input
                                  type="text"
                                  placeholder="MM/DD/YYYY"
                                  value={searchValues[column.id] || ''}
                                  onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                                  className="w-full pr-9 pl-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                                />
                                <Calendar className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" />
                              </>
                            ) : column.id === 'priority' ? (
                              <select
                                value={searchValues[column.id] || ''}
                                onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                                className="w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                              >
                                <option value="">{t("common.filter.all")}</option>
                                <option value="High">{t("common.priority.high")}</option>
                                <option value="Medium">{t("common.priority.medium")}</option>
                                <option value="Low">{t("common.priority.low")}</option>
                              </select>
                            ) : column.id === 'status' ? (
                              <select
                                value={searchValues[column.id] || ''}
                                onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                                className="w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                              >
                                <option value="">{t("common.filter.all")}</option>
                                <option value="PENDING">{t("common.status.pending")}</option>
                                <option value="IN_PROGRESS">{t("common.status.inProgress")}</option>
                                <option value="COMPLETED">{t("common.status.completed")}</option>
                                <option value="LATE">{t("common.status.late")}</option>
                              </select>
                            ) : column.id === 'progress' ? (
                              <input
                                type="number"
                                placeholder="0-100"
                                min="0"
                                max="100"
                                value={searchValues[column.id] || ''}
                                onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                                className="w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                              />
                            ) : (
                              <>
                                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                <input
                                  type="text"
                                  placeholder={t("poList.search.placeholder")}
                                  value={searchValues[column.id] || ''}
                                  onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                                  className="w-full pl-9 pr-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                                />
                              </>
                            )}
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedOrders.length === 0 && (
                      <tr>
                        <td colSpan={Math.max(visibleColumns.length, 1)} className="px-4 py-10 text-center text-sm text-gray-500">
                          {t("poList.empty")}
                        </td>
                      </tr>
                    )}

                    {paginatedOrders.map((order, index) => (
                      <tr
                        key={order.id}
                        className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors`}
                      >
                        {visibleColumns.map((column) => (
                          <td key={column.id} className="px-4 py-3">
                            {renderCellContent(column, order)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-2 flex flex-col items-start gap-3 text-sm text-gray-600 md:flex-row md:items-center md:justify-between">
              <span>
                {t("poList.results.summary", {
                  start: filteredOrders.length === 0 ? 0 : startIndex + 1,
                  end: Math.min(startIndex + itemsPerPage, filteredOrders.length),
                  total: filteredOrders.length,
                })}
              </span>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  «
                </button>
                <button
                  type="button"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ‹
                </button>
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => i + 1).map(page => (
                  <button
                    type="button"
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-1 border rounded ${
                      currentPage === page ? 'bg-blue-500 text-white' : 'hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage >= totalPages}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ›
                </button>
                <button
                  type="button"
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage >= totalPages}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  »
                </button>
              </div>
              <select
                value={itemsPerPage}
                onChange={(e) => {
                  setItemsPerPage(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-focus-ring"
              >
                <option value={30}>{t("poList.pagination.perPage30")}</option>
                <option value={50}>{t("poList.pagination.perPage50")}</option>
                <option value={100}>{t("poList.pagination.perPage100")}</option>
              </select>
            </div>
          </>
        )}
      </div>

      {/* Dialogs */}
      <ColumnManagerDialog
        open={columnManagerOpen}
        onOpenChange={setColumnManagerOpen}
        columns={columns}
        onSave={handleColumnSave}
      />
    </div>
  );
}
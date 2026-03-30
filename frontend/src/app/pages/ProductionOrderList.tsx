import { useState, useMemo } from "react";
import { Search, Plus, Edit, Trash2, Eye, Filter, Download, ChevronDown, Settings, ArrowUpDown, Calendar } from "lucide-react";
import { productionOrders as initialOrders } from "../data/mockData";
import { ColumnManagerDialog, ColumnConfig } from "../components/ColumnManagerDialog";
import { useNavigate } from "react-router";
import { toast } from "sonner";

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
  const navigate = useNavigate();
  const [orders, setOrders] = useState(initialOrders);
  const [columnManagerOpen, setColumnManagerOpen] = useState(false);
  const [columns, setColumns] = useState<ColumnConfig[]>(DEFAULT_COLUMNS);
  const [searchValues, setSearchValues] = useState<Record<string, string>>({
    productionOrder: '',
    serialNumber: '',
    routeId: '',
  });

  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(30);

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
    toast.success('Column settings saved');
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
        return order.plannedCompletionDate;
      case 'actualStartDate':
        return order.actualStartDate || '-';
      case 'actualCompletion':
        return order.actualCompletionDate || '-';
      case 'releasedDate':
        return order.releasedDate;
      case 'assignee':
        return order.assignee || '-';
      case 'department':
        return order.department || '-';
      case 'status':
        return (
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            order.status === 'COMPLETED' ? 'bg-green-50 text-green-600' :
            order.status === 'IN_PROGRESS' ? 'bg-blue-50 text-blue-600' :
            order.status === 'LATE' ? 'bg-red-50 text-red-600' :
            'bg-gray-50 text-gray-600'
          }`}>
            {order.status}
          </span>
        );
      case 'progress':
        return (
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full" 
                style={{ width: `${order.progress}%` }}
              />
            </div>
            <span className="text-xs text-gray-600">{order.progress}%</span>
          </div>
        );
      case 'materialCode':
        return order.materialCode || '-';
      default:
        return '-';
    }
  };

  const visibleColumnsCount = visibleColumns.length;

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl">Production Order List</h2>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setColumnManagerOpen(true)}
              className="flex items-center gap-2 px-4 py-2 border rounded hover:bg-gray-50"
            >
              <Settings className="w-4 h-4" />
              <span>Columns ({visibleColumnsCount})</span>
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
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
                              className="w-full pr-9 pl-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <Calendar className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" />
                          </>
                        ) : column.id === 'priority' ? (
                          <select
                            value={searchValues[column.id] || ''}
                            onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                            className="w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">All</option>
                            <option value="High">High</option>
                            <option value="Medium">Medium</option>
                            <option value="Low">Low</option>
                          </select>
                        ) : column.id === 'status' ? (
                          <select
                            value={searchValues[column.id] || ''}
                            onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                            className="w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">All</option>
                            <option value="PENDING">Pending</option>
                            <option value="IN_PROGRESS">In Progress</option>
                            <option value="COMPLETED">Completed</option>
                            <option value="LATE">Late</option>
                          </select>
                        ) : column.id === 'progress' ? (
                          <input
                            type="number"
                            placeholder="0-100"
                            min="0"
                            max="100"
                            value={searchValues[column.id] || ''}
                            onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                            className="w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        ) : (
                          <>
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                            <input
                              type="text"
                              placeholder="Search"
                              value={searchValues[column.id] || ''}
                              onChange={(e) => setSearchValues(prev => ({ ...prev, [column.id]: e.target.value }))}
                              className="w-full pl-9 pr-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </>
                        )}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {paginatedOrders.map((order, index) => (
                  <tr 
                    key={order.id} 
                    className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 cursor-pointer transition-colors`}
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

        {/* Pagination */}
        <div className="mt-6 flex items-center justify-center gap-2">
          <span className="text-sm text-gray-600">
            Showing {startIndex + 1} - {Math.min(startIndex + itemsPerPage, filteredOrders.length)} of {filteredOrders.length} results
          </span>
          <div className="flex items-center gap-1 ml-4">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              «
            </button>
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ‹
            </button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => i + 1).map(page => (
              <button
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
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage >= totalPages}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ›
            </button>
            <button
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
            className="ml-4 px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={30}>30 / page</option>
            <option value={50}>50 / page</option>
            <option value={100}>100 / page</option>
          </select>
        </div>
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
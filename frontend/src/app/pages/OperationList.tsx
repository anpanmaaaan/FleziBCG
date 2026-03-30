// Work Order Execution Status List
// Shows high-level WO execution status, not individual operations detail

import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router";
import { Search, CheckCircle, Clock, AlertCircle, ChevronRight } from "lucide-react";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { StatsCard } from "../components/StatsCard";

// Work Order Execution (aggregate status)
interface WorkOrderExecution {
  id: string;
  workOrderId: string;
  productionOrderId: string;
  productName: string;
  productionLine: string;
  status: 'Pending' | 'In Progress' | 'Completed' | 'Late' | 'Blocked';
  overallProgress: number; // 0-100
  operationsCount: number;
  completedOperations: number;
  currentOperation?: string;
  plannedStart: string;
  plannedEnd: string;
  actualStart?: string;
  estimatedCompletion?: string;
  delayMinutes?: number;
}

// Mock Work Orders for this Production Order
const mockWorkOrders: WorkOrderExecution[] = [
  {
    id: 'WO-001',
    workOrderId: 'WO-2024-001',
    productionOrderId: 'PO-001',
    productName: 'Engine Block Type A',
    productionLine: 'Line A',
    status: 'In Progress',
    overallProgress: 45,
    operationsCount: 5,
    completedOperations: 2,
    currentOperation: 'Surface Grinding',
    plannedStart: '2024-04-15 07:00',
    plannedEnd: '2024-04-15 18:00',
    actualStart: '2024-04-15 07:05',
    estimatedCompletion: '2024-04-15 18:30',
    delayMinutes: 30,
  },
  {
    id: 'WO-002',
    workOrderId: 'WO-2024-002',
    productionOrderId: 'PO-001',
    productName: 'Engine Block Type A',
    productionLine: 'Line A',
    status: 'Pending',
    overallProgress: 0,
    operationsCount: 5,
    completedOperations: 0,
    plannedStart: '2024-04-15 18:00',
    plannedEnd: '2024-04-16 03:00',
  },
  {
    id: 'WO-003',
    workOrderId: 'WO-2024-003',
    productionOrderId: 'PO-001',
    productName: 'Engine Block Type B',
    productionLine: 'Line B',
    status: 'Completed',
    overallProgress: 100,
    operationsCount: 4,
    completedOperations: 4,
    plannedStart: '2024-04-14 07:00',
    plannedEnd: '2024-04-14 15:00',
    actualStart: '2024-04-14 07:00',
    estimatedCompletion: '2024-04-14 14:45',
  },
  {
    id: 'WO-004',
    workOrderId: 'WO-2024-004',
    productionOrderId: 'PO-001',
    productName: 'Engine Block Type C',
    productionLine: 'Line C',
    status: 'Late',
    overallProgress: 68,
    operationsCount: 6,
    completedOperations: 4,
    currentOperation: 'Quality Inspection',
    plannedStart: '2024-04-14 08:00',
    plannedEnd: '2024-04-14 18:00',
    actualStart: '2024-04-14 08:20',
    estimatedCompletion: '2024-04-14 20:15',
    delayMinutes: 135,
  },
];

export function OperationList() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [workOrders] = useState<WorkOrderExecution[]>(mockWorkOrders);
  const [searchValue, setSearchValue] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const filteredWorkOrders = useMemo(() => {
    let filtered = workOrders;

    if (filterStatus !== 'all') {
      filtered = filtered.filter(wo => wo.status === filterStatus);
    }

    if (searchValue) {
      filtered = filtered.filter(wo =>
        wo.workOrderId.toLowerCase().includes(searchValue.toLowerCase()) ||
        wo.productName.toLowerCase().includes(searchValue.toLowerCase()) ||
        wo.productionLine.toLowerCase().includes(searchValue.toLowerCase())
      );
    }

    return filtered;
  }, [workOrders, filterStatus, searchValue]);

  const stats = useMemo(() => ({
    total: workOrders.length,
    completed: workOrders.filter(wo => wo.status === 'Completed').length,
    inProgress: workOrders.filter(wo => wo.status === 'In Progress').length,
    pending: workOrders.filter(wo => wo.status === 'Pending').length,
    late: workOrders.filter(wo => wo.status === 'Late').length,
    overallProgress: Math.round(
      workOrders.reduce((sum, wo) => sum + wo.overallProgress, 0) / workOrders.length
    ),
  }), [workOrders]);

  const getStatusVariant = (status: string): "success" | "warning" | "error" | "info" | "neutral" => {
    switch (status) {
      case 'Completed': return 'success';
      case 'In Progress': return 'info';
      case 'Pending': return 'neutral';
      case 'Late': return 'error';
      case 'Blocked': return 'error';
      default: return 'neutral';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Completed': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'In Progress': return <Clock className="w-5 h-5 text-blue-600 animate-spin" style={{ animationDuration: '4s' }} />;
      case 'Late': return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'Pending': return <Clock className="w-5 h-5 text-gray-400" />;
      default: return null;
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <PageHeader 
        title={
          <div>
            <div className="text-sm text-gray-500 mb-1">Production Order: {orderId}</div>
            <div className="text-2xl font-bold">Work Order Execution Status</div>
          </div>
        }
        showBackButton={true}
        onBackClick={() => navigate("/production-orders")}
      >
        <div className="flex items-center gap-4 ml-auto">
          <div>
            <span className="text-sm text-gray-500">Route: </span>
            <span className="font-medium">DMES-R8</span>
          </div>
        </div>
      </PageHeader>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-6 gap-4 mb-6">
          <StatsCard
            title="Total WOs"
            value={stats.total}
            color="blue"
          />
          <StatsCard
            title="Completed"
            value={stats.completed}
            color="green"
            icon={CheckCircle}
          />
          <StatsCard
            title="In Progress"
            value={stats.inProgress}
            color="purple"
          />
          <StatsCard
            title="Pending"
            value={stats.pending}
            color="gray"
          />
          <StatsCard
            title="Late"
            value={stats.late}
            color="red"
            icon={AlertCircle}
          />
          <StatsCard
            title="Overall Progress"
            value={`${stats.overallProgress}%`}
            color="orange"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-bold">Work Orders</h2>
            
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Late">Late</option>
              <option value="Completed">Completed</option>
              <option value="Blocked">Blocked</option>
            </select>

            <div className="text-sm text-gray-600">
              Showing: <strong>{filteredWorkOrders.length}</strong> work orders
            </div>
          </div>

          <div className="relative w-80">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search work orders..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="w-full pl-9 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Work Orders List */}
        <div className="space-y-3">
          {filteredWorkOrders.map((wo) => (
            <div 
              key={wo.id} 
              className="border rounded-lg p-5 hover:shadow-md transition-all bg-white cursor-pointer group"
              onClick={() => navigate(`/operation/${wo.id}`)}
            >
              <div className="flex items-center gap-4">
                {/* Status Icon */}
                <div className="flex-shrink-0">
                  {getStatusIcon(wo.status)}
                </div>

                {/* WO Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-bold text-lg font-mono">{wo.workOrderId}</span>
                    <StatusBadge variant={getStatusVariant(wo.status)}>
                      {wo.status}
                    </StatusBadge>
                    {wo.delayMinutes && wo.delayMinutes > 0 && (
                      <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full font-medium">
                        ⚠ +{wo.delayMinutes}min delay
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-6 text-sm text-gray-600">
                    <span>{wo.productName}</span>
                    <span>•</span>
                    <span>{wo.productionLine}</span>
                    <span>•</span>
                    <span>
                      Operations: {wo.completedOperations}/{wo.operationsCount}
                    </span>
                    {wo.currentOperation && (
                      <>
                        <span>•</span>
                        <span className="font-medium text-blue-600">Current: {wo.currentOperation}</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Progress */}
                <div className="flex-shrink-0 w-48">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">Progress</span>
                    <span className="text-sm font-bold">{wo.overallProgress}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        wo.status === 'Completed' ? 'bg-green-500' :
                        wo.status === 'Late' ? 'bg-red-500' :
                        wo.status === 'In Progress' ? 'bg-blue-500' :
                        'bg-gray-400'
                      }`}
                      style={{ width: `${wo.overallProgress}%` }}
                    />
                  </div>
                </div>

                {/* CTA */}
                <button
                  className="flex-shrink-0 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 group-hover:border-blue-500 group-hover:text-blue-600 transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/operation/${wo.id}`);
                  }}
                >
                  <span className="font-medium">View</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredWorkOrders.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <div className="text-lg font-medium mb-1">No work orders found</div>
            <div className="text-sm">Try adjusting your filters or search criteria</div>
          </div>
        )}
      </div>
    </div>
  );
}

// Operation Execution Overview - Gantt Chart ONLY
// Click bar to navigate to detailed view

import { useState } from "react";
import { useNavigate, useParams, Link } from "react-router";
import { 
  ArrowLeft,
  ExternalLink,
  Activity,
  CheckCircle,
  TrendingUp,
  Clock
} from "lucide-react";
import { PageHeader } from "../components/PageHeader";
import { StatsCard } from "../components/StatsCard";
import { GanttChart, OperationExecutionGantt } from "../components/GanttChart";

// ============ MOCK DATA ============
const mockOperationSequence: OperationExecutionGantt[] = [
  {
    id: 'OP-010',
    sequence: 10,
    name: 'Material Preparation',
    workstation: 'WS-00',
    operatorName: 'Tom Brown',
    status: 'Completed',
    plannedStart: '2024-04-15T07:00:00',
    plannedEnd: '2024-04-15T08:30:00',
    actualStart: '2024-04-15T07:00:00',
    actualEnd: '2024-04-15T08:15:00', // Early finish
    qcRequired: false,
  },
  {
    id: 'OP-020',
    sequence: 20,
    name: 'Machining - Bore Drilling',
    workstation: 'WS-01',
    operatorName: 'John Smith',
    status: 'Running',
    plannedStart: '2024-04-15T08:30:00',
    plannedEnd: '2024-04-15T13:00:00',
    actualStart: '2024-04-15T08:35:00', // Started 5min late
    currentTime: '2024-04-15T11:30:00', // Current position
    delayMinutes: 45,
    qcRequired: true,
  },
  {
    id: 'OP-030',
    sequence: 30,
    name: 'Surface Treatment',
    workstation: 'WS-02',
    status: 'Not Started',
    plannedStart: '2024-04-15T13:00:00',
    plannedEnd: '2024-04-15T18:00:00',
    qcRequired: true,
  },
  {
    id: 'OP-040',
    sequence: 40,
    name: 'Quality Inspection',
    workstation: 'WS-QC',
    status: 'Not Started',
    plannedStart: '2024-04-15T18:00:00',
    plannedEnd: '2024-04-15T23:00:00',
    qcRequired: true,
  },
];

export function OperationExecutionOverview() {
  const { woId } = useParams();
  const navigate = useNavigate();
  const [selectedOperationId, setSelectedOperationId] = useState<string | undefined>();

  // Calculate WO-level stats
  const stats = {
    totalOperations: mockOperationSequence.length,
    completedOperations: mockOperationSequence.filter(op => op.status === 'Completed').length,
    inProgressOperations: mockOperationSequence.filter(op => op.status === 'Running').length,
    overallProgress: Math.round(
      mockOperationSequence.reduce((sum, op) => {
        if (op.status === 'Completed') return sum + 100;
        if (op.status === 'Running') return sum + 50; // Estimate 50% for running
        return sum;
      }, 0) / mockOperationSequence.length
    ),
  };

  const handleOperationClick = (operation: OperationExecutionGantt) => {
    // Navigate to detail view
    navigate(`/operation-detail/${operation.id}`);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <PageHeader
        title={
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate(`/production-order/PO-001`)}
              className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            <div>
              <div className="text-sm text-gray-500">Work Order: {woId || 'WO-2024-001'}</div>
              <div className="text-2xl font-bold">Operation Execution Overview</div>
            </div>
          </div>
        }
        showBackButton={false}
        actions={
          <>
            <Link 
              to="/station-execution"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" />
              Open in Station Execution
            </Link>
          </>
        }
      />

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* WO-level Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatsCard
            title="Total Operations"
            value={stats.totalOperations}
            color="blue"
            icon={Activity}
          />
          <StatsCard
            title="Completed"
            value={stats.completedOperations}
            color="green"
            icon={CheckCircle}
          />
          <StatsCard
            title="In Progress"
            value={stats.inProgressOperations}
            color="purple"
          />
          <StatsCard
            title="Overall Progress"
            value={`${stats.overallProgress}%`}
            color="orange"
            icon={TrendingUp}
          />
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <Clock className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-medium text-blue-800">Time-Based Gantt Chart</div>
            <div className="text-sm text-blue-600 mt-1">
              Click any operation bar to view detailed information. Gaps and delays are visible through bar positioning.
            </div>
          </div>
        </div>

        {/* Gantt Chart */}
        <GanttChart 
          operations={mockOperationSequence}
          onOperationClick={handleOperationClick}
          selectedOperationId={selectedOperationId}
        />

        {/* Additional Info */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-bold mb-3 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Operations Breakdown
            </h3>
            <div className="space-y-2 text-sm">
              {mockOperationSequence.map(op => (
                <div 
                  key={op.id} 
                  className="flex items-center justify-between p-2 rounded hover:bg-gray-50 cursor-pointer"
                  onClick={() => handleOperationClick(op)}
                >
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-gray-500">{op.sequence}</span>
                    <span>{op.name}</span>
                  </div>
                  <div className={`text-xs px-2 py-1 rounded ${
                    op.status === 'Completed' ? 'bg-green-100 text-green-700' :
                    op.status === 'Running' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {op.status}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-bold mb-3">Work Order Information</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Work Order ID:</span>
                <span className="font-medium font-mono">{woId || 'WO-2024-001'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Production Order:</span>
                <span className="font-medium font-mono">PO-001</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Product:</span>
                <span className="font-medium">Engine Block Type A</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Production Line:</span>
                <span className="font-medium">Line A</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Quantity:</span>
                <span className="font-medium">50 pcs</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Route:</span>
                <span className="font-medium">DMES-R8</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

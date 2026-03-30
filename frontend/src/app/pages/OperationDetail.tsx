// Operation Execution Overview (Gantt-centric)
// Shows operation sequence timeline for a Work Order

import { useState } from "react";
import { useNavigate, useParams, Link } from "react-router";
import { 
  Clock,
  AlertTriangle,
  Package,
  Activity,
  FileText,
  History,
  Shield,
  CheckCircle,
  XCircle,
  TrendingUp,
  ExternalLink,
  ArrowLeft,
  Play,
  Pause
} from "lucide-react";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { StatsCard } from "../components/StatsCard";

// ============ TYPES ============
interface OperationExecution {
  id: string;
  sequence: number;
  name: string;
  description: string;
  workOrderId: string;
  productionOrderId: string;
  status: 'Pending' | 'In Progress' | 'Completed' | 'Blocked' | 'Paused';
  productionLine: string;
  workstation: string;
  workCenter: string;
  machineId: string;
  machineName: string;
  operatorId?: string;
  operatorName?: string;
  setupTime: number;
  runTime: number;
  quantity: number;
  completedQty: number;
  goodQty: number;
  scrapQty: number;
  progress: number;
  startTime?: string;
  endTime?: string;
  plannedStart: string;
  plannedEnd: string;
  estimatedCompletion: string;
  qcRequired: boolean;
  qcStatus?: 'Pending' | 'Passed' | 'Failed';
  timing: 'On-time' | 'Late' | 'Early';
  delayMinutes?: number;
  blockReason?: string;
}

interface QCCheckpoint {
  id: string;
  name: string;
  type: 'Dimensional' | 'Visual' | 'Functional' | 'Material';
  status: 'Pending' | 'Passed' | 'Failed' | 'Skipped';
  result?: string;
  inspector?: string;
  timestamp?: string;
  specification: string;
  actualValue?: string;
}

interface MaterialItem {
  id: string;
  materialCode: string;
  materialName: string;
  requiredQty: number;
  consumedQty: number;
  unit: string;
  lotNumber?: string;
  status: 'Available' | 'In Use' | 'Depleted' | 'Overused';
}

interface TimelineEvent {
  id: string;
  timestamp: string;
  type: 'Status Change' | 'Operator Action' | 'System Event' | 'Quality Event' | 'Material Event';
  description: string;
  user?: string;
  details?: string;
}

// ============ MOCK DATA ============
// Operation Sequence for Work Order
const mockOperationSequence: OperationExecution[] = [
  {
    id: 'OP-010',
    sequence: 10,
    name: 'Material Preparation',
    description: 'Cut and prepare raw material',
    productionOrderId: 'PO-001',
    workOrderId: 'WO-2024-001',
    status: 'Completed',
    productionLine: 'Line A',
    workstation: 'WS-00',
    workCenter: 'MC-00',
    machineId: 'SAW-01',
    machineName: 'Band Saw #1',
    operatorId: 'OP-121',
    operatorName: 'Tom Brown',
    setupTime: 15,
    runTime: 3,
    quantity: 50,
    completedQty: 50,
    goodQty: 50,
    scrapQty: 0,
    progress: 100,
    startTime: '2024-04-15 07:00',
    endTime: '2024-04-15 08:15',
    plannedStart: '2024-04-15 07:00',
    plannedEnd: '2024-04-15 08:30',
    estimatedCompletion: '2024-04-15 08:15',
    qcRequired: false,
    timing: 'Early',
  },
  {
    id: 'OP-020',
    sequence: 20,
    name: 'Machining - Bore Drilling',
    description: 'Precision drilling operation for main bore with 0.01mm tolerance',
    productionOrderId: 'PO-001',
    workOrderId: 'WO-2024-001',
    status: 'In Progress',
    productionLine: 'Line A',
    workstation: 'WS-01',
    workCenter: 'MC-01',
    machineId: 'MACHINE-01',
    machineName: 'CNC Drill Press #1',
    operatorId: 'OP-123',
    operatorName: 'John Smith',
    setupTime: 30,
    runTime: 5,
    quantity: 50,
    completedQty: 32,
    goodQty: 30,
    scrapQty: 2,
    progress: 64,
    startTime: '2024-04-15 08:30',
    plannedStart: '2024-04-15 08:30',
    plannedEnd: '2024-04-15 13:00',
    estimatedCompletion: '2024-04-15 14:45',
    qcRequired: true,
    qcStatus: 'Pending',
    timing: 'Late',
    delayMinutes: 45,
  },
  {
    id: 'OP-030',
    sequence: 30,
    name: 'Surface Treatment',
    description: 'Apply protective coating',
    productionOrderId: 'PO-001',
    workOrderId: 'WO-2024-001',
    status: 'Pending',
    productionLine: 'Line A',
    workstation: 'WS-02',
    workCenter: 'MC-02',
    machineId: 'COAT-01',
    machineName: 'Coating Station #1',
    setupTime: 20,
    runTime: 8,
    quantity: 50,
    completedQty: 0,
    goodQty: 0,
    scrapQty: 0,
    progress: 0,
    plannedStart: '2024-04-15 13:00',
    plannedEnd: '2024-04-15 18:00',
    estimatedCompletion: '2024-04-15 18:00',
    qcRequired: true,
    timing: 'On-time',
  },
  {
    id: 'OP-040',
    sequence: 40,
    name: 'Quality Inspection',
    description: 'Final inspection and testing',
    productionOrderId: 'PO-001',
    workOrderId: 'WO-2024-001',
    status: 'Pending',
    productionLine: 'Line A',
    workstation: 'WS-QC',
    workCenter: 'QC-01',
    machineId: 'CMM-01',
    machineName: 'CMM Inspection',
    setupTime: 10,
    runTime: 10,
    quantity: 50,
    completedQty: 0,
    goodQty: 0,
    scrapQty: 0,
    progress: 0,
    plannedStart: '2024-04-15 18:00',
    plannedEnd: '2024-04-15 23:00',
    estimatedCompletion: '2024-04-15 23:00',
    qcRequired: true,
    timing: 'On-time',
  },
];

const mockQCCheckpoints: QCCheckpoint[] = [
  {
    id: 'QC-001',
    name: 'Bore Diameter Check',
    type: 'Dimensional',
    status: 'Passed',
    result: 'Within tolerance',
    inspector: 'Mary Johnson',
    timestamp: '2024-04-15 10:30',
    specification: '50.00mm ± 0.01mm',
    actualValue: '50.005mm',
  },
  {
    id: 'QC-002',
    name: 'Surface Finish Inspection',
    type: 'Visual',
    status: 'Passed',
    result: 'No defects',
    inspector: 'Mary Johnson',
    timestamp: '2024-04-15 10:35',
    specification: 'Ra 1.6μm max',
    actualValue: 'Ra 1.2μm',
  },
  {
    id: 'QC-003',
    name: 'Perpendicularity Check',
    type: 'Dimensional',
    status: 'Pending',
    specification: '0.05mm per 100mm',
  },
];

const mockMaterials: MaterialItem[] = [
  {
    id: 'MAT-001',
    materialCode: 'STL-4140',
    materialName: 'Alloy Steel 4140',
    requiredQty: 50,
    consumedQty: 32,
    unit: 'pcs',
    lotNumber: 'LOT-2024-0415-001',
    status: 'In Use',
  },
  {
    id: 'MAT-002',
    materialCode: 'TOOL-CB-10',
    materialName: 'Carbide Drill Bit 10mm',
    requiredQty: 1,
    consumedQty: 1,
    unit: 'pcs',
    lotNumber: 'TOOL-2024-0401',
    status: 'In Use',
  },
  {
    id: 'MAT-003',
    materialCode: 'COOL-SYN-5L',
    materialName: 'Synthetic Coolant',
    requiredQty: 10,
    consumedQty: 6.5,
    unit: 'L',
    status: 'In Use',
  },
];

const mockTimeline: TimelineEvent[] = [
  {
    id: 'EVT-001',
    timestamp: '2024-04-15 08:30',
    type: 'Status Change',
    description: 'Operation started',
    user: 'John Smith',
    details: 'Status changed from Pending to In Progress',
  },
  {
    id: 'EVT-002',
    timestamp: '2024-04-15 08:45',
    type: 'Operator Action',
    description: 'Setup completed',
    user: 'John Smith',
    details: 'Machine setup and calibration completed',
  },
  {
    id: 'EVT-003',
    timestamp: '2024-04-15 09:00',
    type: 'Material Event',
    description: 'Material LOT-2024-0415-001 scanned',
    user: 'John Smith',
  },
  {
    id: 'EVT-004',
    timestamp: '2024-04-15 10:30',
    type: 'Quality Event',
    description: 'QC Checkpoint passed',
    user: 'Mary Johnson',
    details: 'Bore Diameter Check - Passed',
  },
];

type TabType = 'overview' | 'quality' | 'materials' | 'timeline' | 'documents';

export function OperationDetail() {
  const { operationId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [selectedOperationId, setSelectedOperationId] = useState<string>('OP-020');

  // Get selected operation
  const selectedOperation = mockOperationSequence.find(op => op.id === selectedOperationId);
  const currentOperation = selectedOperation || mockOperationSequence[1];

  const getStatusVariant = (status: string): "success" | "warning" | "error" | "info" | "neutral" => {
    switch (status) {
      case 'Completed': return 'success';
      case 'In Progress': return 'info';
      case 'Pending': return 'neutral';
      case 'Blocked': return 'error';
      case 'Paused': return 'warning';
      default: return 'neutral';
    }
  };

  const getTimingColor = (timing: string) => {
    switch (timing) {
      case 'On-time': return 'text-green-600';
      case 'Early': return 'text-blue-600';
      case 'Late': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'quality', label: 'Quality', icon: Shield },
    { id: 'materials', label: 'Materials', icon: Package },
    { id: 'timeline', label: 'Timeline', icon: History },
    { id: 'documents', label: 'Documents', icon: FileText },
  ] as const;

  // Calculate WO-level stats
  const woStats = {
    totalOperations: mockOperationSequence.length,
    completedOperations: mockOperationSequence.filter(op => op.status === 'Completed').length,
    inProgressOperations: mockOperationSequence.filter(op => op.status === 'In Progress').length,
    overallProgress: Math.round(mockOperationSequence.reduce((sum, op) => sum + op.progress, 0) / mockOperationSequence.length),
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <PageHeader
        title={
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate(`/production-order/${currentOperation.productionOrderId}`)}
              className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            <div>
              <div className="text-sm text-gray-500">Work Order: {currentOperation.workOrderId}</div>
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

      {/* WO-level Stats */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="grid grid-cols-4 gap-4">
          <StatsCard
            title="Total Operations"
            value={woStats.totalOperations}
            color="blue"
            icon={Activity}
          />
          <StatsCard
            title="Completed"
            value={woStats.completedOperations}
            color="green"
            icon={CheckCircle}
          />
          <StatsCard
            title="In Progress"
            value={woStats.inProgressOperations}
            color="purple"
          />
          <StatsCard
            title="Overall Progress"
            value={`${woStats.overallProgress}%`}
            color="orange"
          />
        </div>
      </div>

      {/* Gantt Chart Section */}
      <div className="bg-white border-b border-gray-200 px-6 py-6">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-600" />
          Operation Sequence Timeline (Gantt)
        </h3>

        <div className="space-y-3">
          {mockOperationSequence.map((op) => {
            const isSelected = op.id === selectedOperationId;
            const progressWidth = op.progress;
            
            return (
              <div 
                key={op.id}
                onClick={() => setSelectedOperationId(op.id)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  isSelected 
                    ? 'border-blue-500 bg-blue-50 shadow-md' 
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                }`}
              >
                <div className="flex items-center gap-4">
                  {/* Sequence Badge */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                    op.status === 'Completed' ? 'bg-green-100 text-green-700' :
                    op.status === 'In Progress' ? 'bg-blue-100 text-blue-700' :
                    op.status === 'Blocked' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {op.sequence}
                  </div>

                  {/* Operation Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-bold">{op.name}</span>
                      <StatusBadge variant={getStatusVariant(op.status)} size="sm">
                        {op.status}
                      </StatusBadge>
                      {op.status === 'In Progress' && (
                        <span className="text-xs flex items-center gap-1 text-blue-600">
                          <Play className="w-3 h-3 animate-pulse" />
                          Running
                        </span>
                      )}
                      {op.delayMinutes && op.delayMinutes > 0 && (
                        <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded font-medium">
                          ⚠ +{op.delayMinutes}min delay
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{op.workstation}</span>
                      <span>•</span>
                      <span>{op.operatorName || 'Not assigned'}</span>
                      {op.status !== 'Pending' && (
                        <>
                          <span>•</span>
                          <span>{op.completedQty}/{op.quantity} units</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Gantt Bar */}
                  <div className="flex-1 max-w-xl">
                    <div className="flex items-center gap-2 text-xs text-gray-600 mb-2">
                      <Clock className="w-3 h-3" />
                      <span className="font-medium">Planned:</span>
                      <span>{op.plannedStart} → {op.plannedEnd}</span>
                    </div>
                    
                    {/* Planned bar (outline) */}
                    <div className="relative h-8 mb-1">
                      <div className="absolute inset-0 border-2 border-dashed border-gray-300 rounded-lg" />
                      
                      {/* Actual bar (filled) */}
                      {op.status !== 'Pending' && (
                        <div className="absolute inset-0 flex items-center px-1">
                          <div 
                            className={`h-6 rounded transition-all ${
                              op.status === 'Completed' ? 'bg-green-500' :
                              op.status === 'In Progress' ? 'bg-blue-500' :
                              op.status === 'Blocked' ? 'bg-red-500' :
                              'bg-gray-400'
                            }`}
                            style={{ width: `${progressWidth}%` }}
                          />
                        </div>
                      )}
                      
                      {/* Progress text */}
                      <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-700">
                        {progressWidth}%
                      </span>
                    </div>
                    
                    {op.startTime && (
                      <div className="text-xs text-gray-500">
                        <span className="font-medium">Actual:</span> {op.startTime}
                        {op.endTime && ` → ${op.endTime}`}
                        {!op.endTime && op.estimatedCompletion && ` → Est. ${op.estimatedCompletion}`}
                      </div>
                    )}
                  </div>

                  {/* Timing */}
                  <div className={`text-sm font-medium ${getTimingColor(op.timing)} flex-shrink-0`}>
                    {op.timing}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Left: Operation Summary Panel */}
        <div className="w-80 bg-white border-r border-gray-200 p-6 overflow-auto">
          <h3 className="text-lg font-bold mb-4">Selected Operation</h3>
          
          <div className="space-y-4">
            <div>
              <div className="text-sm text-gray-500">Operation ID</div>
              <div className="font-mono font-bold text-lg text-blue-600">{currentOperation.id}</div>
            </div>

            <div>
              <div className="text-sm text-gray-500">Sequence</div>
              <div className="font-bold text-2xl">{currentOperation.sequence}</div>
            </div>

            <div>
              <div className="text-sm text-gray-500">Name</div>
              <div className="font-medium">{currentOperation.name}</div>
            </div>

            <div>
              <div className="text-sm text-gray-500">Station / Workcenter</div>
              <div className="font-medium">{currentOperation.workstation} / {currentOperation.workCenter}</div>
            </div>

            <div>
              <div className="text-sm text-gray-500">Status</div>
              <StatusBadge variant={getStatusVariant(currentOperation.status)}>
                {currentOperation.status}
              </StatusBadge>
            </div>

            <div>
              <div className="text-sm text-gray-500">Progress</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all"
                    style={{ width: `${currentOperation.progress}%` }}
                  />
                </div>
                <span className="font-bold">{currentOperation.progress}%</span>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="text-sm text-gray-500 mb-2">Planned vs Actual</div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Planned Start:</span>
                  <span className="font-medium">{currentOperation.plannedStart}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Actual Start:</span>
                  <span className="font-medium">{currentOperation.startTime || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Planned End:</span>
                  <span className="font-medium">{currentOperation.plannedEnd}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Est. Completion:</span>
                  <span className={`font-medium ${currentOperation.timing === 'Late' ? 'text-red-600' : ''}`}>
                    {currentOperation.estimatedCompletion}
                  </span>
                </div>
              </div>
            </div>

            {currentOperation.delayMinutes && currentOperation.delayMinutes > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center gap-2 text-red-800 font-medium mb-1">
                  <AlertTriangle className="w-4 h-4" />
                  Delay Alert
                </div>
                <div className="text-sm text-red-600">
                  +{currentOperation.delayMinutes} minutes behind schedule
                </div>
              </div>
            )}

            {currentOperation.blockReason && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center gap-2 text-red-800 font-medium mb-1">
                  <XCircle className="w-4 h-4" />
                  Blocked
                </div>
                <div className="text-sm text-red-600">{currentOperation.blockReason}</div>
              </div>
            )}
          </div>
        </div>

        {/* Main Content - Contextual Tabs */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Tabs */}
          <div className="bg-white border-b border-gray-200 px-6">
            <div className="flex gap-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as TabType)}
                    className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2 ${
                      activeTab === tab.id
                        ? 'text-blue-600 border-blue-600'
                        : 'text-gray-500 border-transparent hover:text-gray-700'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-auto p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Stats Row */}
                <div className="grid grid-cols-5 gap-4">
                  <StatsCard
                    title="Completed Qty"
                    value={`${currentOperation.completedQty}/${currentOperation.quantity}`}
                    color="blue"
                    icon={Package}
                  />
                  <StatsCard
                    title="Good Quantity"
                    value={currentOperation.goodQty}
                    color="green"
                    icon={CheckCircle}
                  />
                  <StatsCard
                    title="Scrap Quantity"
                    value={currentOperation.scrapQty}
                    color="red"
                    icon={XCircle}
                  />
                  <StatsCard
                    title="Progress"
                    value={`${currentOperation.progress}%`}
                    color="purple"
                    icon={TrendingUp}
                  />
                  <StatsCard
                    title="Yield Rate"
                    value={`${((currentOperation.goodQty / currentOperation.completedQty) * 100 || 0).toFixed(1)}%`}
                    color="cyan"
                  />
                </div>

                {/* Resource & Location Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg border p-6">
                    <h3 className="text-lg font-bold mb-4">Location & Equipment</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Production Line</span>
                        <span className="font-medium">{currentOperation.productionLine}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Work Center</span>
                        <span className="font-medium">{currentOperation.workCenter}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Workstation</span>
                        <span className="font-medium">{currentOperation.workstation}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Machine</span>
                        <span className="font-medium">{currentOperation.machineName}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Machine ID</span>
                        <span className="font-medium text-blue-600">{currentOperation.machineId}</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg border p-6">
                    <h3 className="text-lg font-bold mb-4">Time & Quantity</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Setup Time</span>
                        <span className="font-medium">{currentOperation.setupTime} min</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Run Time / Unit</span>
                        <span className="font-medium">{currentOperation.runTime} min</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Planned Quantity</span>
                        <span className="font-medium">{currentOperation.quantity} pcs</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Completed Quantity</span>
                        <span className="font-medium text-blue-600">{currentOperation.completedQty} pcs</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Remaining</span>
                        <span className="font-medium text-orange-600">{currentOperation.quantity - currentOperation.completedQty} pcs</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Operator Info */}
                {currentOperation.operatorName && (
                  <div className="bg-white rounded-lg border p-6">
                    <h3 className="text-lg font-bold mb-4">Operator Assignment</h3>
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-2xl font-bold text-blue-600">
                          {currentOperation.operatorName.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <div className="font-bold text-lg">{currentOperation.operatorName}</div>
                        <div className="text-sm text-gray-500">Operator ID: {currentOperation.operatorId}</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Operation Description */}
                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">Operation Description</h3>
                  <p className="text-gray-700 leading-relaxed">{currentOperation.description}</p>
                </div>
              </div>
            )}

            {/* Quality Tab */}
            {activeTab === 'quality' && (
              <div className="space-y-6">
                {/* Quality Summary */}
                <div className="grid grid-cols-4 gap-4">
                  <StatsCard
                    title="QC Checkpoints"
                    value={mockQCCheckpoints.length}
                    color="blue"
                    icon={Shield}
                  />
                  <StatsCard
                    title="Passed"
                    value={mockQCCheckpoints.filter(c => c.status === 'Passed').length}
                    color="green"
                    icon={CheckCircle}
                  />
                  <StatsCard
                    title="Pending"
                    value={mockQCCheckpoints.filter(c => c.status === 'Pending').length}
                    color="orange"
                    icon={Clock}
                  />
                  <StatsCard
                    title="First Pass Yield"
                    value="93.8%"
                    color="cyan"
                    icon={TrendingUp}
                  />
                </div>

                {/* QC Checkpoints */}
                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">Quality Checkpoints (Read-Only)</h3>
                  <div className="space-y-3">
                    {mockQCCheckpoints.map((checkpoint) => (
                      <div key={checkpoint.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-bold">{checkpoint.name}</h4>
                              <StatusBadge 
                                variant={
                                  checkpoint.status === 'Passed' ? 'success' :
                                  checkpoint.status === 'Failed' ? 'error' :
                                  checkpoint.status === 'Pending' ? 'warning' : 'neutral'
                                }
                                size="sm"
                              >
                                {checkpoint.status}
                              </StatusBadge>
                              <span className="text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">
                                {checkpoint.type}
                              </span>
                            </div>
                            <div className="text-sm text-gray-500">ID: {checkpoint.id}</div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Specification: </span>
                            <span className="font-medium">{checkpoint.specification}</span>
                          </div>
                          {checkpoint.actualValue && (
                            <div>
                              <span className="text-gray-500">Actual Value: </span>
                              <span className="font-medium text-green-600">{checkpoint.actualValue}</span>
                            </div>
                          )}
                          {checkpoint.inspector && (
                            <div>
                              <span className="text-gray-500">Inspector: </span>
                              <span className="font-medium">{checkpoint.inspector}</span>
                            </div>
                          )}
                          {checkpoint.timestamp && (
                            <div>
                              <span className="text-gray-500">Timestamp: </span>
                              <span className="font-medium">{checkpoint.timestamp}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Materials Tab - READ ONLY */}
            {activeTab === 'materials' && (
              <div className="space-y-6">
                {/* Read-only Notice */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-blue-800">Read-Only View (Phase 1)</div>
                    <div className="text-sm text-blue-600 mt-1">
                      This view is for analysis only. Material consumption and adjustments are performed in Station Execution.
                    </div>
                  </div>
                </div>

                {/* Material Summary */}
                <div className="grid grid-cols-4 gap-4">
                  <StatsCard
                    title="Total Materials"
                    value={mockMaterials.length}
                    color="blue"
                    icon={Package}
                  />
                  <StatsCard
                    title="In Use"
                    value={mockMaterials.filter(m => m.status === 'In Use').length}
                    color="green"
                  />
                  <StatsCard
                    title="Consumption Rate"
                    value="64%"
                    color="purple"
                  />
                  <StatsCard
                    title="Status"
                    value={mockMaterials.some(m => m.status === 'Overused') ? 'Alert' : 'OK'}
                    color={mockMaterials.some(m => m.status === 'Overused') ? 'red' : 'green'}
                  />
                </div>

                {/* Materials List */}
                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">Bill of Materials (BOM)</h3>
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">Material Code</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">Material Name</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">Required</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">Consumed</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">Remaining</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">Lot Number</th>
                        <th className="text-left px-4 py-2 text-sm font-medium text-gray-600">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {mockMaterials.map((material) => {
                        const remaining = material.requiredQty - material.consumedQty;
                        const isOverused = remaining < 0;
                        
                        return (
                          <tr key={material.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 font-mono text-sm">{material.materialCode}</td>
                            <td className="px-4 py-3">{material.materialName}</td>
                            <td className="px-4 py-3">{material.requiredQty} {material.unit}</td>
                            <td className="px-4 py-3 font-medium">{material.consumedQty} {material.unit}</td>
                            <td className={`px-4 py-3 font-medium ${isOverused ? 'text-red-600' : 'text-orange-600'}`}>
                              {remaining} {material.unit}
                              {isOverused && <span className="ml-2 text-xs bg-red-100 px-2 py-0.5 rounded">Overused</span>}
                            </td>
                            <td className="px-4 py-3 font-mono text-xs">{material.lotNumber || '-'}</td>
                            <td className="px-4 py-3">
                              <StatusBadge 
                                variant={
                                  material.status === 'Overused' ? 'error' :
                                  material.status === 'In Use' ? 'success' : 'neutral'
                                }
                                size="sm"
                              >
                                {material.status}
                              </StatusBadge>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Traceability */}
                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">Traceability Information</h3>
                  <div className="space-y-4">
                    <div className="border rounded-lg p-4">
                      <div className="font-medium mb-2">Material: Alloy Steel 4140</div>
                      <div className="text-sm space-y-1 text-gray-600">
                        <div><span className="font-medium">Lot Number:</span> LOT-2024-0415-001</div>
                        <div><span className="font-medium">Supplier:</span> ABC Steel Corp.</div>
                        <div><span className="font-medium">Received Date:</span> 2024-04-10</div>
                        <div><span className="font-medium">Heat Number:</span> H-45678-2024</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Timeline Tab */}
            {activeTab === 'timeline' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">Operation Timeline</h3>
                  <div className="space-y-4">
                    {mockTimeline.map((event, index) => (
                      <div key={event.id} className="flex gap-4">
                        <div className="flex flex-col items-center">
                          <div className={`w-3 h-3 rounded-full ${
                            event.type === 'Status Change' ? 'bg-blue-500' :
                            event.type === 'Quality Event' ? 'bg-green-500' :
                            event.type === 'Material Event' ? 'bg-purple-500' :
                            event.type === 'System Event' ? 'bg-red-500' :
                            'bg-gray-500'
                          }`} />
                          {index < mockTimeline.length - 1 && (
                            <div className="w-0.5 h-full bg-gray-300 flex-1 mt-1" />
                          )}
                        </div>
                        <div className="flex-1 pb-4">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">{event.description}</span>
                            <span className="text-xs text-gray-500">{event.timestamp}</span>
                          </div>
                          {event.user && (
                            <div className="text-sm text-gray-600">By: {event.user}</div>
                          )}
                          {event.details && (
                            <div className="text-sm text-gray-500 mt-1">{event.details}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Documents Tab */}
            {activeTab === 'documents' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg border p-6">
                  <h3 className="text-lg font-bold mb-4">Work Instructions & Documents</h3>
                  <div className="space-y-3">
                    <div className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-3">
                        <FileText className="w-10 h-10 text-blue-600" />
                        <div className="flex-1">
                          <div className="font-medium">Work Instruction - Bore Drilling</div>
                          <div className="text-sm text-gray-500">PDF • 2.4 MB • Updated 2024-04-10</div>
                        </div>
                      </div>
                    </div>
                    <div className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-3">
                        <FileText className="w-10 h-10 text-green-600" />
                        <div className="flex-1">
                          <div className="font-medium">Quality Control Procedure</div>
                          <div className="text-sm text-gray-500">PDF • 1.8 MB • Updated 2024-04-05</div>
                        </div>
                      </div>
                    </div>
                    <div className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-3">
                        <FileText className="w-10 h-10 text-purple-600" />
                        <div className="flex-1">
                          <div className="font-medium">Safety Guidelines</div>
                          <div className="text-sm text-gray-500">PDF • 0.9 MB • Updated 2024-03-20</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

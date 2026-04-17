import { useState } from "react";
import { useParams, useNavigate } from "react-router";
import {
  Play, Pause, CheckCircle2, Circle, Settings, Users, Clock,
  CheckCircle, FileText, ArrowLeft, Download, Save, Plus,
  ChevronDown, ChevronRight, Edit2, Copy, Trash2, X
} from "lucide-react";
import { PageHeader } from "@/app/components";

// Types
interface Operation {
  id: string;
  sequence: string;
  name: string;
  description?: string;
  type: 'Setup' | 'Process' | 'Inspection' | 'Wait' | 'Transport';
  workCenter: string;
  machine?: string;
  setupTime: number;
  runTimePerUnit: number;
  waitTime?: number;
  laborRequired: number;
  skill?: string;
  skillLevel?: string;
  tools?: string[];
  qcRequired: boolean;
  qcParameters?: string[];
  workInstructions?: string;
  attachments?: string[];
  dependencies?: string[];
  parallelAllowed: boolean;
}

interface RouteData {
  id: string;
  name: string;
  version: string;
  status: 'Active' | 'Inactive' | 'Draft' | 'Under Review';
  description: string;
  productNumber?: string;
  effectiveFrom: string;
  effectiveTo?: string;
  createdBy: string;
  createdDate: string;
  lastModifiedBy: string;
  lastModifiedDate: string;
  tags: string[];
}

export function RouteDetail() {
  const { routeId } = useParams<{ routeId: string }>();
  const navigate = useNavigate();
  
  const [expandedOperations, setExpandedOperations] = useState<Set<string>>(new Set());
  const [selectedOperations, setSelectedOperations] = useState<Set<string>>(new Set());
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [editingOperation, setEditingOperation] = useState<Operation | null>(null);
  const [isDirty, setIsDirty] = useState(false);

  // Skills - Automotive Industry (Job Categories)
  const [skills] = useState<string[]>([
    'Press Operator',
    'Die Setup Technician',
    'Spot Welding Operator',
    'MIG Welder',
    'Robotic Welding Operator',
    'Body Assembly Welder',
    'Welding Inspector',
    'Paint Prep Operator',
    'Paint Spray Operator',
    'Paint Line Operator',
    'Paint Inspector',
    'Assembly Operator',
    'Trim & Final Assembly',
    'Engine Assembly Specialist',
    'Transmission Assembly Specialist',
    'Chassis Assembly Operator',
    'QC Inspector',
    'First Off Inspector',
    'Final Inspection Auditor',
    'CMM Operator',
    'CNC Operator',
    'Machining Operator',
    'Deburring Operator',
    'Material Handler',
    'Forklift Operator',
    'Kitting/Sequencing Operator',
    'Functional Test Operator',
    'Leak Test Operator',
    'Team Leader',
    'Line Supervisor',
  ]);

  // Skill Levels
  const [skillLevels] = useState<string[]>([
    'Level I',
    'Level II',
    'Level III',
    'Basic',
    'Advanced',
    'Expert',
    'Certified',
    'Senior',
    'Junior',
  ]);

  // Mock route data
  const [routeData, setRouteData] = useState<RouteData>({
    id: routeId || '',
    name: 'HAL-X002',
    version: '1.0',
    status: 'Active',
    description: 'Standard machining route for HAL series components',
    productNumber: 'HAL-X002-001',
    effectiveFrom: '01/01/2024',
    createdBy: 'John Smith',
    createdDate: '12/15/2023',
    lastModifiedBy: 'Sarah Johnson',
    lastModifiedDate: '06/04/2024',
    tags: ['Machining', 'Standard', 'HAL-Series'],
  });

  // Mock operations data
  const [operations, setOperations] = useState<Operation[]>([
    {
      id: 'OP-001',
      sequence: '010',
      name: 'Material Kitting',
      description: 'Prepare and kit all materials for body assembly',
      type: 'Setup',
      workCenter: 'WC-100',
      machine: 'KITTING-STATION-01',
      setupTime: 5,
      runTimePerUnit: 3,
      waitTime: 0,
      laborRequired: 1,
      skill: 'Kitting/Sequencing Operator',
      skillLevel: 'Basic',
      tools: ['Barcode Scanner', 'Material Cart'],
      qcRequired: false,
      workInstructions: 'Follow kitting sequence as per BOM, scan all parts',
      parallelAllowed: false,
    },
    {
      id: 'OP-002',
      sequence: '020',
      name: 'Body Panel Stamping',
      description: 'Stamping operation for door panel',
      type: 'Process',
      workCenter: 'WC-200',
      machine: 'PRESS-2500T-01',
      setupTime: 30,
      runTimePerUnit: 12,
      waitTime: 2,
      laborRequired: 2,
      skill: 'Press Operator',
      skillLevel: 'Level II',
      tools: ['Die Set #DP-450', 'Lift Assist', 'Safety Guards'],
      qcRequired: true,
      qcParameters: ['Panel dimensions ±0.5mm', 'Surface defects check', 'Edge quality'],
      workInstructions: 'Set press to 2200T, cycle time 12sec, inspect first 3 pieces',
      attachments: ['WI-PRESS-200-v3.pdf', 'die-setup-guide.pdf'],
      parallelAllowed: false,
    },
    {
      id: 'OP-003',
      sequence: '030',
      name: 'Spot Welding - Body Assembly',
      description: 'Robotic spot welding for body side panel',
      type: 'Process',
      workCenter: 'WC-300',
      machine: 'ROBOT-WELD-CELL-03',
      setupTime: 10,
      runTimePerUnit: 45,
      waitTime: 5,
      laborRequired: 1,
      skill: 'Robotic Welding Operator',
      skillLevel: 'Certified',
      tools: ['Welding Gun Tips', 'Fixture Clamps', 'Weld Monitor'],
      qcRequired: true,
      qcParameters: ['Weld nugget size 6-8mm', 'Weld count verification', 'Visual inspection'],
      workInstructions: 'Load program BODY-SIDE-R-v2.2, verify all 48 weld points',
      parallelAllowed: false,
    },
    {
      id: 'OP-004',
      sequence: '040',
      name: 'Paint Line - E-Coat',
      description: 'Electrophoretic coating for corrosion protection',
      type: 'Process',
      workCenter: 'WC-400',
      machine: 'ECOAT-TANK-01',
      setupTime: 5,
      runTimePerUnit: 180,
      waitTime: 120,
      laborRequired: 1,
      skill: 'Paint Line Operator',
      skillLevel: 'Advanced',
      tools: ['Thickness Gauge', 'pH Tester'],
      qcRequired: true,
      qcParameters: ['Coating thickness 20-25 microns', 'Coverage 100%', 'Surface preparation'],
      workInstructions: 'Bath temp 32°C, immersion time 180sec, check thickness at 5 points',
      parallelAllowed: false,
    },
    {
      id: 'OP-005',
      sequence: '050',
      name: 'Final Body Inspection',
      description: 'Dimensional and visual quality inspection',
      type: 'Inspection',
      workCenter: 'WC-500',
      machine: 'CMM-BODY-01',
      setupTime: 5,
      runTimePerUnit: 25,
      waitTime: 0,
      laborRequired: 1,
      skill: 'QC Inspector',
      skillLevel: 'Level III',
      tools: ['CMM Probe', 'Gap/Flush Gauge', 'Paint Thickness Gauge'],
      qcRequired: true,
      qcParameters: ['Body dimensions per CAD', 'Panel gaps 3-5mm', 'Paint thickness', 'Surface defects'],
      workInstructions: 'Follow inspection plan IP-BODY-001, check critical dimensions',
      attachments: ['inspection-checklist-body.pdf'],
      parallelAllowed: false,
    },
  ]);

  const toggleExpand = (operationId: string) => {
    setExpandedOperations(prev => {
      const newSet = new Set(prev);
      if (newSet.has(operationId)) {
        newSet.delete(operationId);
      } else {
        newSet.add(operationId);
      }
      return newSet;
    });
  };

  const handleDeleteOperation = (operationId: string) => {
    if (window.confirm('Are you sure you want to delete this operation?')) {
      setOperations(prev => prev.filter(op => op.id !== operationId));
      setIsDirty(true);
    }
  };

  const handleDuplicateOperation = (operation: Operation) => {
    const newOp = {
      ...operation,
      id: `OP-${Date.now()}`,
      sequence: String(Number(operation.sequence) + 5).padStart(3, '0'),
      name: `${operation.name} (Copy)`,
    };
    setOperations(prev => [...prev, newOp]);
    setIsDirty(true);
  };

  const handleEditOperation = (operation: Operation) => {
    setEditingOperation(operation);
    setShowAddDialog(true);
  };

  const moveOperation = (operationId: string, direction: 'up' | 'down') => {
    const index = operations.findIndex(op => op.id === operationId);
    if (index === -1) return;
    
    if (direction === 'up' && index > 0) {
      const newOps = [...operations];
      [newOps[index], newOps[index - 1]] = [newOps[index - 1], newOps[index]];
      setOperations(newOps);
      setIsDirty(true);
    } else if (direction === 'down' && index < operations.length - 1) {
      const newOps = [...operations];
      [newOps[index], newOps[index + 1]] = [newOps[index + 1], newOps[index]];
      setOperations(newOps);
      setIsDirty(true);
    }
  };

  const calculateTotalTime = () => {
    return operations.reduce((total, op) => {
      return total + op.setupTime + op.runTimePerUnit + (op.waitTime || 0);
    }, 0);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'bg-green-100 text-green-800';
      case 'Inactive': return 'bg-gray-100 text-gray-800';
      case 'Draft': return 'bg-blue-100 text-blue-800';
      case 'Under Review': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <PageHeader title="ROUTE MANAGEMENT" showBackButton={false} />

      {/* Breadcrumb & Actions Bar */}
      <div className="border-b bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/routes')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Routes</span>
            </button>
            <span className="text-gray-400">/</span>
            <h1 className="text-2xl font-semibold">{routeData.name}</h1>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(routeData.status)}`}>
              {routeData.status}
            </span>
            <span className="text-sm text-gray-500">v{routeData.version}</span>
            
            {/* Summary Info */}
            <div className="flex items-center gap-4 ml-6 text-sm text-gray-600">
              <span>Operations: <strong>{operations.length}</strong></span>
              <span>Total Time: <strong>{calculateTotalTime()} min</strong></span>
              <span>QC Points: <strong>{operations.filter(op => op.qcRequired).length}</strong></span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              Validate
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Cancel
            </button>
            <button 
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!isDirty}
            >
              <Save className="w-4 h-4" />
              Save Changes
            </button>
          </div>
        </div>
      </div>

      {/* Content Area - Full Width */}
      <div className="flex-1 overflow-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Operations Sequence</h2>
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
              <Download className="w-4 h-4" />
              Import Template
            </button>
            <button
              onClick={() => setShowAddDialog(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Operation
            </button>
          </div>
        </div>

        {/* Operations Table */}
        <div className="border rounded-lg overflow-hidden bg-white">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="w-10 px-4 py-3"></th>
                <th className="w-10 px-4 py-3"></th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">SEQ</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">OPERATION</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">TYPE</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">WORK CENTER</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">STD TIME</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">QC</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {operations.map((operation: Operation, index: number) => (
                <OperationRow
                  key={operation.id}
                  operation={operation}
                  index={index}
                  isExpanded={expandedOperations.has(operation.id)}
                  isSelected={selectedOperations.has(operation.id)}
                  isFirst={index === 0}
                  isLast={index === operations.length - 1}
                  toggleExpand={toggleExpand}
                  handleDeleteOperation={handleDeleteOperation}
                  handleDuplicateOperation={handleDuplicateOperation}
                  handleEditOperation={handleEditOperation}
                  moveOperation={moveOperation}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Operation Dialog */}
      {showAddDialog && (
        <OperationDialog
          operation={editingOperation}
          onClose={() => {
            setShowAddDialog(false);
            setEditingOperation(null);
          }}
          onSave={(operation) => {
            if (editingOperation) {
              setOperations(prev => prev.map(op => op.id === operation.id ? operation : op));
            } else {
              setOperations(prev => [...prev, operation]);
            }
            setIsDirty(true);
            setShowAddDialog(false);
            setEditingOperation(null);
          }}
          skills={skills}
          skillLevels={skillLevels}
        />
      )}
    </div>
  );
}

// Operation Row Component
function OperationRow({
  operation,
  index,
  isExpanded,
  isSelected,
  isFirst,
  isLast,
  toggleExpand,
  handleDeleteOperation,
  handleDuplicateOperation,
  handleEditOperation,
  moveOperation,
}: {
  operation: Operation;
  index: number;
  isExpanded: boolean;
  isSelected: boolean;
  isFirst: boolean;
  isLast: boolean;
  toggleExpand: (id: string) => void;
  handleDeleteOperation: (id: string) => void;
  handleDuplicateOperation: (op: Operation) => void;
  handleEditOperation: (op: Operation) => void;
  moveOperation: (id: string, direction: 'up' | 'down') => void;
}) {
  const totalTime = operation.setupTime + operation.runTimePerUnit + (operation.waitTime || 0);

  return (
    <>
      <tr className={`border-b hover:bg-gray-50 ${isSelected ? 'bg-blue-50' : ''}`}>
        <td className="px-4 py-4">
          <button
            onClick={() => toggleExpand(operation.id)}
            className="p-1 hover:bg-gray-200 rounded"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>
        </td>
        <td className="px-4 py-4">
          <div className="flex flex-col gap-1">
            <button
              onClick={() => moveOperation(operation.id, 'up')}
              disabled={isFirst}
              className="p-0.5 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronDown className="w-3 h-3 rotate-180" />
            </button>
            <button
              onClick={() => moveOperation(operation.id, 'down')}
              disabled={isLast}
              className="p-0.5 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronDown className="w-3 h-3" />
            </button>
          </div>
        </td>
        <td className="px-6 py-4 font-mono font-semibold text-blue-600">{operation.sequence}</td>
        <td className="px-6 py-4">
          <div className="font-medium">{operation.name}</div>
          {operation.description && (
            <div className="text-sm text-gray-500 mt-1">{operation.description}</div>
          )}
        </td>
        <td className="px-6 py-4">
          <span className="text-sm">{operation.type}</span>
        </td>
        <td className="px-6 py-4">
          <div className="font-medium">{operation.workCenter}</div>
          {operation.machine && (
            <div className="text-sm text-gray-500">{operation.machine}</div>
          )}
        </td>
        <td className="px-6 py-4">
          <div className="flex items-center gap-1 text-sm">
            <Clock className="w-3 h-3 text-gray-400" />
            <span className="font-medium">{totalTime} min</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            S: {operation.setupTime} | R: {operation.runTimePerUnit}
          </div>
        </td>
        <td className="px-6 py-4">
          {operation.qcRequired ? (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
              <CheckCircle className="w-3 h-3" />
              Required
            </span>
          ) : (
            <span className="text-gray-400 text-sm">-</span>
          )}
        </td>
        <td className="px-6 py-4">
          <div className="flex items-center gap-1">
            <button
              onClick={() => handleEditOperation(operation)}
              className="p-2 hover:bg-gray-200 rounded"
              title="Edit"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleDuplicateOperation(operation)}
              className="p-2 hover:bg-gray-200 rounded"
              title="Duplicate"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleDeleteOperation(operation.id)}
              className="p-2 hover:bg-red-100 rounded text-red-600"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </td>
      </tr>

      {/* Expanded Details */}
      {isExpanded && (
        <tr className="bg-gray-50 border-b">
          <td colSpan={9} className="px-16 py-4">
            <div className="grid grid-cols-3 gap-6 text-sm">
              <div>
                <h4 className="font-semibold text-gray-700 mb-3">Timing Details</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Setup Time:</span>
                    <span className="font-medium">{operation.setupTime} min</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Run Time/Unit:</span>
                    <span className="font-medium">{operation.runTimePerUnit} min</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Wait Time:</span>
                    <span className="font-medium">{operation.waitTime || 0} min</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-700 mb-3">Resources</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Labor Required:</span>
                    <span className="font-medium">{operation.laborRequired}</span>
                  </div>
                  {operation.skill && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Skill:</span>
                      <span className="font-medium">{operation.skill}</span>
                    </div>
                  )}
                  {operation.skillLevel && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Level:</span>
                      <span className="font-medium">{operation.skillLevel}</span>
                    </div>
                  )}
                  {operation.tools && operation.tools.length > 0 && (
                    <div>
                      <span className="text-gray-600">Tools:</span>
                      <ul className="mt-1 space-y-1">
                        {operation.tools.map((tool, i) => (
                          <li key={i} className="text-gray-700 text-xs">• {tool}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-700 mb-3">Quality Control</h4>
                {operation.qcRequired && operation.qcParameters ? (
                  <div className="space-y-2">
                    {operation.qcParameters.map((param, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700 text-xs">{param}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <span className="text-gray-500">No QC requirements</span>
                )}
              </div>

              {operation.workInstructions && (
                <div className="col-span-3">
                  <h4 className="font-semibold text-gray-700 mb-2">Work Instructions</h4>
                  <p className="text-gray-700 bg-white p-3 rounded border">
                    {operation.workInstructions}
                  </p>
                </div>
              )}

              {operation.attachments && operation.attachments.length > 0 && (
                <div className="col-span-3">
                  <h4 className="font-semibold text-gray-700 mb-2">Attachments</h4>
                  <div className="flex gap-2">
                    {operation.attachments.map((file, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-white border rounded text-xs"
                      >
                        <FileText className="w-3 h-3" />
                        {file}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

// Operation Dialog Component
function OperationDialog({
  operation,
  onClose,
  onSave,
  skills,
  skillLevels,
}: {
  operation: Operation | null;
  onClose: () => void;
  onSave: (operation: Operation) => void;
  skills: string[];
  skillLevels: string[];
}) {
  const [form, setForm] = useState<Operation>(
    operation || {
      id: `OP-${Date.now()}`,
      sequence: '050',
      name: '',
      description: '',
      type: 'Process',
      workCenter: '',
      machine: '',
      setupTime: 0,
      runTimePerUnit: 0,
      waitTime: 0,
      laborRequired: 1,
      skillLevel: '',
      tools: [],
      qcRequired: false,
      qcParameters: [],
      workInstructions: '',
      attachments: [],
      dependencies: [],
      parallelAllowed: false,
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(form);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white z-10">
          <h3 className="text-xl font-semibold">
            {operation ? 'Edit Operation' : 'Add New Operation'}
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sequence Number <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.sequence}
                onChange={(e) => setForm({ ...form, sequence: e.target.value })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Operation Type <span className="text-red-500">*</span>
              </label>
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value as any })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
              >
                <option value="Setup">Setup</option>
                <option value="Process">Process</option>
                <option value="Inspection">Inspection</option>
                <option value="Wait">Wait</option>
                <option value="Transport">Transport</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Operation Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
              className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
            />
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Work Center <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.workCenter}
                onChange={(e) => setForm({ ...form, workCenter: e.target.value })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Machine/Equipment
              </label>
              <input
                type="text"
                value={form.machine}
                onChange={(e) => setForm({ ...form, machine: e.target.value })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Setup Time (min)
              </label>
              <input
                type="number"
                value={form.setupTime}
                onChange={(e) => setForm({ ...form, setupTime: Number(e.target.value) })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                min="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Run Time/Unit (min)
              </label>
              <input
                type="number"
                value={form.runTimePerUnit}
                onChange={(e) => setForm({ ...form, runTimePerUnit: Number(e.target.value) })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                min="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Wait Time (min)
              </label>
              <input
                type="number"
                value={form.waitTime}
                onChange={(e) => setForm({ ...form, waitTime: Number(e.target.value) })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                min="0"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Labor Required
              </label>
              <input
                type="number"
                value={form.laborRequired}
                onChange={(e) => setForm({ ...form, laborRequired: Number(e.target.value) })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
                min="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Skill
              </label>
              <select
                value={form.skill}
                onChange={(e) => setForm({ ...form, skill: e.target.value })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
              >
                <option value="">Select Skill</option>
                {skills.map(skill => (
                  <option key={skill} value={skill}>{skill}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Level
              </label>
              <select
                value={form.skillLevel}
                onChange={(e) => setForm({ ...form, skillLevel: e.target.value })}
                className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
              >
                <option value="">Select Level</option>
                {skillLevels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Work Instructions
            </label>
            <textarea
              value={form.workInstructions}
              onChange={(e) => setForm({ ...form, workInstructions: e.target.value })}
              rows={4}
              className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
              placeholder="Detailed work instructions for operators..."
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="qcRequired"
              checked={form.qcRequired}
              onChange={(e) => setForm({ ...form, qcRequired: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <label htmlFor="qcRequired" className="text-sm font-medium text-gray-700">
              Quality Control Required
            </label>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {operation ? 'Update Operation' : 'Add Operation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
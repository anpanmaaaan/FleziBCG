import { useState, useMemo } from "react";
import { Search, Plus, AlertTriangle, CheckCircle, Clock, XCircle, Filter } from "lucide-react";
import { toast } from "sonner";

interface Defect {
  id: string;
  defect_no: string;
  wo_id: string;
  product_id: string;
  product_name: string;
  serial_no?: string;
  station_id: string;
  station_name: string;
  operator_id: string;
  defect_type: 'Dimensional' | 'Visual' | 'Assembly' | 'Material' | 'Process';
  severity: 'Critical' | 'Major' | 'Minor';
  description: string;
  root_cause?: string;
  detected_at: string;
  status: 'Open' | 'In Repair' | 'Repaired' | 'Verified' | 'Rejected' | 'Scrapped';
  assigned_to?: string;
  resolution_time?: number; // minutes
  repair_station?: string;
}

const mockDefects: Defect[] = [
  {
    id: 'DEF-001',
    defect_no: 'DEF-2024-001',
    wo_id: 'WO-2024-001',
    product_id: 'PROD-001',
    product_name: 'Engine Block',
    serial_no: 'SN-001234',
    station_id: 'ST-01',
    station_name: 'Machining Center 1',
    operator_id: 'OP-123',
    defect_type: 'Dimensional',
    severity: 'Critical',
    description: 'Bore diameter out of tolerance: 50.10mm (spec: 50.00±0.05mm)',
    root_cause: 'Tool wear detected',
    detected_at: '2024-04-15 08:30',
    status: 'In Repair',
    assigned_to: 'OP-456',
    repair_station: 'REPAIR-01',
  },
  {
    id: 'DEF-002',
    defect_no: 'DEF-2024-002',
    wo_id: 'WO-2024-003',
    product_id: 'PROD-003',
    product_name: 'Cylinder Head',
    serial_no: 'SN-001235',
    station_id: 'ST-02',
    station_name: 'Assembly Line 1',
    operator_id: 'OP-124',
    defect_type: 'Assembly',
    severity: 'Major',
    description: 'Missing bolt at position A3',
    detected_at: '2024-04-15 09:15',
    status: 'Open',
  },
  {
    id: 'DEF-003',
    defect_no: 'DEF-2024-003',
    wo_id: 'WO-2024-002',
    product_id: 'PROD-002',
    product_name: 'Transmission Housing',
    serial_no: 'SN-001236',
    station_id: 'ST-03',
    station_name: 'Grinding Station',
    operator_id: 'OP-125',
    defect_type: 'Visual',
    severity: 'Minor',
    description: 'Surface scratch detected, length 5mm',
    detected_at: '2024-04-15 10:00',
    status: 'Repaired',
    assigned_to: 'OP-789',
    repair_station: 'REPAIR-02',
    resolution_time: 45,
  },
  {
    id: 'DEF-004',
    defect_no: 'DEF-2024-004',
    wo_id: 'WO-2024-005',
    product_id: 'PROD-004',
    product_name: 'Camshaft',
    serial_no: 'SN-001237',
    station_id: 'ST-04',
    station_name: 'Heat Treatment',
    operator_id: 'OP-126',
    defect_type: 'Material',
    severity: 'Critical',
    description: 'Material hardness below specification',
    root_cause: 'Incorrect heat treatment temperature',
    detected_at: '2024-04-15 11:20',
    status: 'Scrapped',
  },
  {
    id: 'DEF-005',
    defect_no: 'DEF-2024-005',
    wo_id: 'WO-2024-006',
    product_id: 'PROD-001',
    product_name: 'Engine Block',
    serial_no: 'SN-001238',
    station_id: 'ST-05',
    station_name: 'Final Inspection',
    operator_id: 'QC-001',
    defect_type: 'Process',
    severity: 'Major',
    description: 'Torque verification failed on 3 bolts',
    detected_at: '2024-04-15 12:00',
    status: 'Verified',
    assigned_to: 'OP-456',
    repair_station: 'REPAIR-01',
    resolution_time: 30,
  },
];

export function DefectManagement() {
  const [defects, setDefects] = useState(mockDefects);
  const [searchValue, setSearchValue] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');

  const filteredDefects = useMemo(() => {
    let filtered = defects;

    if (filterStatus !== 'all') {
      filtered = filtered.filter(d => d.status === filterStatus);
    }

    if (filterSeverity !== 'all') {
      filtered = filtered.filter(d => d.severity === filterSeverity);
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(d => d.defect_type === filterType);
    }

    if (searchValue) {
      filtered = filtered.filter(d =>
        d.defect_no.toLowerCase().includes(searchValue.toLowerCase()) ||
        d.product_name.toLowerCase().includes(searchValue.toLowerCase()) ||
        d.description.toLowerCase().includes(searchValue.toLowerCase()) ||
        d.serial_no?.toLowerCase().includes(searchValue.toLowerCase())
      );
    }

    return filtered.sort((a, b) => new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime());
  }, [defects, filterStatus, filterSeverity, filterType, searchValue]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Open': return 'bg-red-100 text-red-800';
      case 'In Repair': return 'bg-yellow-100 text-yellow-800';
      case 'Repaired': return 'bg-blue-100 text-blue-800';
      case 'Verified': return 'bg-green-100 text-green-800';
      case 'Rejected': return 'bg-purple-100 text-purple-800';
      case 'Scrapped': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'bg-red-100 text-red-800';
      case 'Major': return 'bg-orange-100 text-orange-800';
      case 'Minor': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Dimensional': return 'bg-blue-100 text-blue-800';
      case 'Visual': return 'bg-purple-100 text-purple-800';
      case 'Assembly': return 'bg-green-100 text-green-800';
      case 'Material': return 'bg-red-100 text-red-800';
      case 'Process': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const stats = useMemo(() => ({
    open: defects.filter(d => d.status === 'Open').length,
    inRepair: defects.filter(d => d.status === 'In Repair').length,
    critical: defects.filter(d => d.severity === 'Critical').length,
    avgResolutionTime: Math.round(
      defects.filter(d => d.resolution_time).reduce((acc, d) => acc + (d.resolution_time || 0), 0) /
      defects.filter(d => d.resolution_time).length
    ) || 0,
  }), [defects]);

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="flex-1 flex flex-col p-6">
        {/* Filters */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search defects..."
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-80"
              />
            </div>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
            >
              <option value="all">All Status</option>
              <option value="Open">Open</option>
              <option value="In Repair">In Repair</option>
              <option value="Repaired">Repaired</option>
              <option value="Verified">Verified</option>
              <option value="Rejected">Rejected</option>
              <option value="Scrapped">Scrapped</option>
            </select>

            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
            >
              <option value="all">All Severity</option>
              <option value="Critical">Critical</option>
              <option value="Major">Major</option>
              <option value="Minor">Minor</option>
            </select>

            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
            >
              <option value="all">All Types</option>
              <option value="Dimensional">Dimensional</option>
              <option value="Visual">Visual</option>
              <option value="Assembly">Assembly</option>
              <option value="Material">Material</option>
              <option value="Process">Process</option>
            </select>

            <div className="text-sm text-gray-600">
              Total: <strong>{filteredDefects.length}</strong> defects
            </div>
          </div>

          <button
            onClick={() => toast.info('Record Defect feature coming soon')}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Record Defect
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-red-600 font-medium">Open Defects</div>
                <div className="text-2xl font-bold text-red-800">{stats.open}</div>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-lg border border-yellow-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-yellow-600 font-medium">In Repair</div>
                <div className="text-2xl font-bold text-yellow-800">{stats.inRepair}</div>
              </div>
              <Clock className="w-8 h-8 text-yellow-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-orange-600 font-medium">Critical</div>
                <div className="text-2xl font-bold text-orange-800">{stats.critical}</div>
              </div>
              <XCircle className="w-8 h-8 text-orange-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-blue-600 font-medium">Avg Resolution</div>
                <div className="text-2xl font-bold text-blue-800">{stats.avgResolutionTime} min</div>
              </div>
              <CheckCircle className="w-8 h-8 text-blue-500" />
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto border rounded-lg">
          <table className="w-full">
            <thead className="bg-gray-50 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Defect No
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product / Serial
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Station
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Detected
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assigned To
                </th>
              </tr>
            </thead>
            <tbody className="bg-background divide-y divide-surface-divider">
              {filteredDefects.map((defect) => (
                <tr key={defect.id} className="hover:bg-gray-50 cursor-pointer">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-blue-600">{defect.defect_no}</div>
                    <div className="text-sm text-gray-500">{defect.wo_id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium">{defect.product_name}</div>
                    <div className="text-sm text-gray-500 font-mono">{defect.serial_no || '-'}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div>{defect.station_id}</div>
                    <div className="text-sm text-gray-500">{defect.station_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(defect.defect_type)}`}>
                      {defect.defect_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(defect.severity)}`}>
                      {defect.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 max-w-xs">
                    <div className="text-sm">{defect.description}</div>
                    {defect.root_cause && (
                      <div className="text-xs text-gray-500 mt-1">Root: {defect.root_cause}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(defect.status)}`}>
                      {defect.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm">{defect.detected_at}</div>
                    {defect.resolution_time && (
                      <div className="text-xs text-gray-500">Fixed in {defect.resolution_time}m</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm">{defect.assigned_to || '-'}</div>
                    {defect.repair_station && (
                      <div className="text-xs text-gray-500">{defect.repair_station}</div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
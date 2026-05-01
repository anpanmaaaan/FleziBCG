import { useState, useMemo } from "react";
import { Search, Plus, CheckCircle2, XCircle, AlertCircle, Edit2, Trash2, Lock } from "lucide-react";
import { toast } from "sonner";
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface QCCheckpoint {
  id: string;
  checkpoint_name: string;
  station_id: string;
  station_name: string;
  operation_id?: string;
  product_id?: string;
  qc_type: 'Dimensional' | 'Visual' | 'Functional' | 'Torque' | 'Pressure';
  parameter: string;
  specification: string;
  lower_limit?: number;
  upper_limit?: number;
  unit: string;
  frequency: 'Every Unit' | 'First/Last' | 'Hourly' | 'Random';
  mandatory: boolean;
  status: 'Active' | 'Inactive';
}

const mockCheckpoints: QCCheckpoint[] = [
  {
    id: 'QC-001',
    checkpoint_name: 'Bore Diameter Check',
    station_id: 'ST-01',
    station_name: 'Machining Center 1',
    operation_id: 'OP-010',
    product_id: 'PROD-001',
    qc_type: 'Dimensional',
    parameter: 'Bore Diameter',
    specification: '50.00 ± 0.05 mm',
    lower_limit: 49.95,
    upper_limit: 50.05,
    unit: 'mm',
    frequency: 'Every Unit',
    mandatory: true,
    status: 'Active',
  },
  {
    id: 'QC-002',
    checkpoint_name: 'Surface Finish Inspection',
    station_id: 'ST-02',
    station_name: 'Grinding Station',
    qc_type: 'Visual',
    parameter: 'Surface Roughness',
    specification: 'Ra ≤ 1.6 μm',
    upper_limit: 1.6,
    unit: 'μm',
    frequency: 'First/Last',
    mandatory: true,
    status: 'Active',
  },
  {
    id: 'QC-003',
    checkpoint_name: 'Torque Verification',
    station_id: 'ST-03',
    station_name: 'Assembly Line 1',
    operation_id: 'OP-030',
    qc_type: 'Torque',
    parameter: 'Bolt Torque',
    specification: '25 ± 2 Nm',
    lower_limit: 23,
    upper_limit: 27,
    unit: 'Nm',
    frequency: 'Every Unit',
    mandatory: true,
    status: 'Active',
  },
  {
    id: 'QC-004',
    checkpoint_name: 'Leak Test',
    station_id: 'ST-04',
    station_name: 'Testing Station',
    qc_type: 'Pressure',
    parameter: 'Pressure Drop',
    specification: '≤ 5 kPa/min',
    upper_limit: 5,
    unit: 'kPa/min',
    frequency: 'Every Unit',
    mandatory: true,
    status: 'Active',
  },
  {
    id: 'QC-005',
    checkpoint_name: 'Weight Check',
    station_id: 'ST-02',
    station_name: 'Grinding Station',
    qc_type: 'Dimensional',
    parameter: 'Component Weight',
    specification: '2.5 ± 0.1 kg',
    lower_limit: 2.4,
    upper_limit: 2.6,
    unit: 'kg',
    frequency: 'Hourly',
    mandatory: false,
    status: 'Active',
  },
];

export function QCCheckpoints() {
  const { t } = useI18n();
  const [checkpoints, setCheckpoints] = useState(mockCheckpoints);
  const [searchValue, setSearchValue] = useState('');
  const [filterStation, setFilterStation] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');

  const stations = useMemo(() => {
    const uniqueStations = new Set(checkpoints.map(cp => cp.station_id));
    return Array.from(uniqueStations);
  }, [checkpoints]);

  const qcTypes = ['Dimensional', 'Visual', 'Functional', 'Torque', 'Pressure'];

  const filteredCheckpoints = useMemo(() => {
    let filtered = checkpoints;

    if (filterStation !== 'all') {
      filtered = filtered.filter(cp => cp.station_id === filterStation);
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(cp => cp.qc_type === filterType);
    }

    if (searchValue) {
      filtered = filtered.filter(cp =>
        cp.checkpoint_name.toLowerCase().includes(searchValue.toLowerCase()) ||
        cp.parameter.toLowerCase().includes(searchValue.toLowerCase()) ||
        cp.station_name.toLowerCase().includes(searchValue.toLowerCase())
      );
    }

    return filtered;
  }, [checkpoints, filterStation, filterType, searchValue]);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Dimensional': return 'bg-blue-100 text-blue-800';
      case 'Visual': return 'bg-purple-100 text-purple-800';
      case 'Functional': return 'bg-green-100 text-green-800';
      case 'Torque': return 'bg-orange-100 text-orange-800';
      case 'Pressure': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getFrequencyColor = (frequency: string) => {
    switch (frequency) {
      case 'Every Unit': return 'bg-red-100 text-red-800';
      case 'First/Last': return 'bg-yellow-100 text-yellow-800';
      case 'Hourly': return 'bg-blue-100 text-blue-800';
      case 'Random': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleEdit = (checkpoint: QCCheckpoint) => {
    toast.info(`Edit checkpoint: ${checkpoint.checkpoint_name}`);
  };

  const handleDelete = (checkpoint: QCCheckpoint) => {
    toast.error(`Delete checkpoint: ${checkpoint.checkpoint_name}`);
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner phase="MOCK" note="Quality checkpoint configuration is not yet connected to backend truth. Use this for visualization only." />
      <div className="flex-1 flex flex-col p-6">
        {/* Page header with status badge */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">Quality Checkpoints</h1>
            <ScreenStatusBadge phase="MOCK" />
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search checkpoints..."
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-80"
              />
            </div>

            <select
              value={filterStation}
              onChange={(e) => setFilterStation(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
            >
              <option value="all">All Stations</option>
              {stations.map(station => (
                <option key={station} value={station}>{station}</option>
              ))}
            </select>

            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
            >
              <option value="all">All Types</option>
              {qcTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>

            <div className="text-sm text-gray-600">
              Total: <strong>{filteredCheckpoints.length}</strong> checkpoints
            </div>
          </div>

          <button
            disabled
            onClick={() => toast.info('Add QC Checkpoint feature coming soon')}
            className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
            title="This action is not available for mock data"
          >
            <Lock className="w-4 h-4" />
            Add Checkpoint (Future)
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-blue-600 font-medium">Active Checkpoints</div>
                <div className="text-2xl font-bold text-blue-800">
                  {checkpoints.filter(cp => cp.status === 'Active').length}
                </div>
              </div>
              <CheckCircle2 className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-purple-600 font-medium">Mandatory</div>
                <div className="text-2xl font-bold text-purple-800">
                  {checkpoints.filter(cp => cp.mandatory).length}
                </div>
              </div>
              <AlertCircle className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-green-600 font-medium">Every Unit</div>
                <div className="text-2xl font-bold text-green-800">
                  {checkpoints.filter(cp => cp.frequency === 'Every Unit').length}
                </div>
              </div>
              <CheckCircle2 className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-orange-600 font-medium">Stations Covered</div>
                <div className="text-2xl font-bold text-orange-800">{stations.length}</div>
              </div>
              <CheckCircle2 className="w-8 h-8 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto border rounded-lg">
          <table className="w-full">
            <thead className="bg-gray-50 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Checkpoint Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Station
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Parameter
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Specification
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Frequency
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mandatory
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-background divide-y divide-surface-divider">
              {filteredCheckpoints.map((checkpoint) => (
                <tr key={checkpoint.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium">{checkpoint.checkpoint_name}</div>
                    <div className="text-sm text-gray-500">{checkpoint.id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div>{checkpoint.station_id}</div>
                    <div className="text-sm text-gray-500">{checkpoint.station_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(checkpoint.qc_type)}`}>
                      {checkpoint.qc_type}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium">{checkpoint.parameter}</div>
                    <div className="text-sm text-gray-500">{checkpoint.unit}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-mono text-sm">{checkpoint.specification}</div>
                    {checkpoint.lower_limit && checkpoint.upper_limit && (
                      <div className="text-xs text-gray-500">
                        [{checkpoint.lower_limit} - {checkpoint.upper_limit}]
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getFrequencyColor(checkpoint.frequency)}`}>
                      {checkpoint.frequency}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {checkpoint.mandatory ? (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                        Yes
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                        No
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      checkpoint.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {checkpoint.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <button
                        disabled
                        onClick={() => handleEdit(checkpoint)}
                        className="p-2 text-gray-400 cursor-not-allowed"
                        title="Edit is not available for mock data"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        disabled
                        onClick={() => handleDelete(checkpoint)}
                        className="p-2 text-gray-400 cursor-not-allowed"
                        title="Delete is not available for mock data"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
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
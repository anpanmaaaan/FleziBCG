import { useState, useEffect } from "react";
import { Play, Pause, CheckCircle, XCircle, Clock, User, Scan, FileText, AlertTriangle, BookOpen, Package, Target } from "lucide-react";
import { toast } from "sonner";

interface Operator {
  id: string;
  name: string;
  badge_no: string;
  skill_level: string;
}

interface WorkOrder {
  wo_id: string;
  product_id: string;
  product_name: string;
  operation_id: string;
  operation_name: string;
  sequence_no: number;
  target_time: number; // seconds
  work_instructions?: string;
  qc_checkpoints?: QCCheckpoint[];
  parts_list?: PartItem[];
}

interface QCCheckpoint {
  id: string;
  name: string;
  type: 'Dimensional' | 'Visual' | 'Functional' | 'Torque' | 'Pressure';
  spec: string;
  lower_limit?: number;
  upper_limit?: number;
  unit?: string;
  mandatory: boolean;
}

interface PartItem {
  part_no: string;
  part_name: string;
  qty_required: number;
  qty_consumed: number;
  unit: string;
}

interface ExecutionSession {
  exec_id: string;
  wo_id: string;
  operator_id: string;
  station_id: string;
  start_time: string;
  end_time?: string;
  status: 'In Progress' | 'Completed' | 'Paused';
  result?: 'OK' | 'NG';
  qc_results?: QCResult[];
  andon_called?: boolean;
}

interface QCResult {
  checkpoint_id: string;
  value: string | number;
  result: 'Pass' | 'Fail';
  timestamp: string;
}

const mockOperators: Operator[] = [
  { id: 'OP-123', name: 'John Smith', badge_no: 'B-001', skill_level: 'Expert' },
  { id: 'OP-124', name: 'Mary Johnson', badge_no: 'B-002', skill_level: 'Advanced' },
  { id: 'OP-125', name: 'Robert Lee', badge_no: 'B-003', skill_level: 'Basic' },
];

const mockNextWO: WorkOrder = {
  wo_id: 'WO-2024-001',
  product_id: 'PROD-001',
  product_name: 'Engine Block',
  operation_id: 'OP-010',
  operation_name: 'Machining - Bore Drilling',
  sequence_no: 1,
  target_time: 300, // 5 minutes
  work_instructions: `1. Verify part alignment on fixture
2. Check tool offset before machining
3. Apply coolant during drilling
4. Inspect bore diameter after completion
5. Clean swarf from workpiece`,
  qc_checkpoints: [
    {
      id: 'QC-001',
      name: 'Bore Diameter',
      type: 'Dimensional',
      spec: '50.00 ± 0.02 mm',
      lower_limit: 49.98,
      upper_limit: 50.02,
      unit: 'mm',
      mandatory: true,
    },
    {
      id: 'QC-002',
      name: 'Surface Finish',
      type: 'Visual',
      spec: 'No scratches or burrs',
      mandatory: true,
    },
    {
      id: 'QC-003',
      name: 'Bolt Torque',
      type: 'Torque',
      spec: '25 ± 2 Nm',
      lower_limit: 23,
      upper_limit: 27,
      unit: 'Nm',
      mandatory: true,
    },
  ],
  parts_list: [
    { part_no: 'BOLT-M8-50', part_name: 'M8 x 50mm Bolt', qty_required: 4, qty_consumed: 0, unit: 'pcs' },
    { part_no: 'WASHER-M8', part_name: 'M8 Washer', qty_required: 4, qty_consumed: 0, unit: 'pcs' },
    { part_no: 'COOLANT-A', part_name: 'Cutting Coolant Type A', qty_required: 0.5, qty_consumed: 0, unit: 'L' },
  ],
};

export function StationExecution() {
  const [currentOperator, setCurrentOperator] = useState<Operator | null>(null);
  const [currentWO, setCurrentWO] = useState<WorkOrder | null>(null);
  const [session, setSession] = useState<ExecutionSession | null>(null);
  const [scannedSerial, setScannedSerial] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);
  const [loginMode, setLoginMode] = useState<'badge' | 'pin'>('badge');
  const [badgeInput, setBadgeInput] = useState('');
  const [pinInput, setPinInput] = useState('');
  const [showQCModal, setShowQCModal] = useState(false);
  const [currentQCIndex, setCurrentQCIndex] = useState(0);
  const [qcValue, setQcValue] = useState('');
  const [partsList, setPartsList] = useState<PartItem[]>([]);

  // Timer for elapsed time
  useEffect(() => {
    let interval: any;
    if (session?.status === 'In Progress') {
      interval = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [session]);

  const handleOperatorLogin = () => {
    if (loginMode === 'badge' && badgeInput) {
      const operator = mockOperators.find(op => op.badge_no === badgeInput);
      if (operator) {
        setCurrentOperator(operator);
        toast.success(`Welcome, ${operator.name}!`);
        setBadgeInput('');
      } else {
        toast.error('Operator not found');
      }
    } else if (loginMode === 'pin' && pinInput) {
      // Mock PIN validation
      const operator = mockOperators[0];
      setCurrentOperator(operator);
      toast.success(`Welcome, ${operator.name}!`);
      setPinInput('');
    }
  };

  const handleScanSerial = () => {
    if (scannedSerial) {
      toast.success(`Serial scanned: ${scannedSerial}`);
      setCurrentWO(mockNextWO);
      setPartsList(mockNextWO.parts_list || []);
    }
  };

  const handleStartExecution = () => {
    if (!currentOperator || !currentWO) {
      toast.error('Please login and scan serial first');
      return;
    }

    const newSession: ExecutionSession = {
      exec_id: `EXEC-${Date.now()}`,
      wo_id: currentWO.wo_id,
      operator_id: currentOperator.id,
      station_id: 'ST-01',
      start_time: new Date().toISOString(),
      status: 'In Progress',
    };

    setSession(newSession);
    setElapsedTime(0);
    toast.success('Execution started');
  };

  const handlePauseExecution = () => {
    if (session) {
      setSession({ ...session, status: 'Paused' });
      toast.warning('Execution paused');
    }
  };

  const handleResumeExecution = () => {
    if (session) {
      setSession({ ...session, status: 'In Progress' });
      toast.info('Execution resumed');
    }
  };

  const handleCompleteExecution = (result: 'OK' | 'NG') => {
    if (session) {
      const completedSession: ExecutionSession = {
        ...session,
        end_time: new Date().toISOString(),
        status: 'Completed',
        result,
      };
      setSession(completedSession);
      toast.success(`Execution completed: ${result}`);
      
      // Reset for next WO
      setTimeout(() => {
        setCurrentWO(null);
        setScannedSerial('');
        setSession(null);
        setElapsedTime(0);
        setQcValue('');
      }, 2000);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleQCModalOpen = (index: number) => {
    setCurrentQCIndex(index);
    setQcValue('');
    setShowQCModal(true);
  };

  const handleQCModalClose = () => {
    setShowQCModal(false);
    setQcValue('');
  };

  const handleQCSubmit = () => {
    if (session && currentWO && currentQCIndex < (currentWO.qc_checkpoints?.length || 0)) {
      const checkpoint = currentWO.qc_checkpoints![currentQCIndex];
      const value = parseFloat(qcValue);
      let result: 'Pass' | 'Fail' = 'Pass';

      if (checkpoint.type === 'Dimensional' || checkpoint.type === 'Torque' || checkpoint.type === 'Pressure') {
        if (value < (checkpoint.lower_limit || 0) || value > (checkpoint.upper_limit || 0)) {
          result = 'Fail';
        }
      } else if (checkpoint.type === 'Visual' || checkpoint.type === 'Functional') {
        // For visual and functional checks, assume 'Pass' if value is 'Pass'
        if (qcValue.toLowerCase() !== 'pass') {
          result = 'Fail';
        }
      }

      const newQCResult: QCResult = {
        checkpoint_id: checkpoint.id,
        value: value || qcValue,
        result,
        timestamp: new Date().toISOString(),
      };

      setSession({
        ...session,
        qc_results: [...(session.qc_results || []), newQCResult],
      });

      if (result === 'Fail') {
        toast.error(`QC Checkpoint ${checkpoint.name} failed`);
      } else {
        toast.success(`QC Checkpoint ${checkpoint.name} passed`);
      }

      setQcValue('');
      setShowQCModal(false);
    }
  };

  const handlePartConsumption = (partIndex: number) => {
    const updatedPartsList = partsList.map((part, index) => {
      if (index === partIndex && part.qty_consumed < part.qty_required) {
        return {
          ...part,
          qty_consumed: part.qty_consumed + 1,
        };
      }
      return part;
    });

    setPartsList(updatedPartsList);
    toast.success(`Part ${updatedPartsList[partIndex].part_name} consumed`);
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Operator Login Section */}
        {!currentOperator ? (
          <div className="max-w-2xl mx-auto mt-20">
            <div className="bg-white rounded-lg shadow-lg p-8 border border-gray-200">
              <div className="text-center mb-6">
                <User className="w-16 h-16 text-blue-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-800">Operator Login</h2>
                <p className="text-gray-600 mt-2">Please login to start execution</p>
              </div>

              <div className="flex gap-2 mb-6">
                <button
                  onClick={() => setLoginMode('badge')}
                  className={`flex-1 py-2 px-4 rounded-lg ${
                    loginMode === 'badge' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  Badge Scan
                </button>
                <button
                  onClick={() => setLoginMode('pin')}
                  className={`flex-1 py-2 px-4 rounded-lg ${
                    loginMode === 'pin' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  PIN Code
                </button>
              </div>

              {loginMode === 'badge' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Scan Badge Number
                  </label>
                  <input
                    type="text"
                    value={badgeInput}
                    onChange={(e) => setBadgeInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleOperatorLogin()}
                    placeholder="B-001"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Enter PIN Code
                  </label>
                  <input
                    type="password"
                    value={pinInput}
                    onChange={(e) => setPinInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleOperatorLogin()}
                    placeholder="****"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>
              )}

              <button
                onClick={handleOperatorLogin}
                className="w-full mt-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Login
              </button>

              <div className="mt-6 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800 font-medium">Demo Credentials:</p>
                <p className="text-xs text-blue-600 mt-1">Badge: B-001, B-002, or B-003</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col">
            {/* Operator Info Bar */}
            <div className="mb-6 p-4 bg-white rounded-lg shadow border border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <User className="w-10 h-10 text-blue-600" />
                  <div>
                    <div className="font-bold text-lg">{currentOperator.name}</div>
                    <div className="text-sm text-gray-600">
                      Badge: {currentOperator.badge_no} | Skill: {currentOperator.skill_level}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setCurrentOperator(null);
                    setCurrentWO(null);
                    setSession(null);
                    toast.info('Logged out');
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Logout
                </button>
              </div>
            </div>

            {/* Serial Scan Section */}
            {!currentWO && !session && (
              <div className="max-w-2xl mx-auto mt-10">
                <div className="bg-white rounded-lg shadow-lg p-8 border border-gray-200">
                  <div className="text-center mb-6">
                    <Scan className="w-16 h-16 text-green-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-800">Scan Serial Number</h2>
                    <p className="text-gray-600 mt-2">Scan barcode to load work order</p>
                  </div>

                  <input
                    type="text"
                    value={scannedSerial}
                    onChange={(e) => setScannedSerial(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleScanSerial()}
                    placeholder="Scan or enter serial number..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-center text-lg"
                    autoFocus
                  />

                  <button
                    onClick={handleScanSerial}
                    className="w-full mt-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                  >
                    Load Work Order
                  </button>

                  <div className="mt-6 p-3 bg-green-50 rounded-lg">
                    <p className="text-sm text-green-800 font-medium">Demo Serial Numbers:</p>
                    <p className="text-xs text-green-600 mt-1">SN-001234, SN-001235, SN-001236</p>
                  </div>
                </div>
              </div>
            )}

            {/* Main Execution Section - 3 Column Layout */}
            {currentWO && (
              <div className="flex-1 grid grid-cols-12 gap-6">
                {/* Left Column: Work Order Info + Work Instructions */}
                <div className="col-span-4 flex flex-col gap-6">
                  {/* Work Order Details */}
                  <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <FileText className="w-5 h-5 text-blue-600" />
                      Work Order Details
                    </h3>

                    <div className="space-y-3">
                      <div>
                        <label className="text-xs text-gray-600 uppercase">Work Order</label>
                        <div className="font-mono font-bold text-lg text-blue-600">{currentWO.wo_id}</div>
                      </div>

                      <div>
                        <label className="text-xs text-gray-600 uppercase">Product</label>
                        <div className="font-medium">{currentWO.product_name}</div>
                        <div className="text-xs text-gray-500">{currentWO.product_id}</div>
                      </div>

                      <div>
                        <label className="text-xs text-gray-600 uppercase">Operation</label>
                        <div className="font-medium">{currentWO.operation_name}</div>
                        <div className="text-xs text-gray-500">{currentWO.operation_id}</div>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs text-gray-600 uppercase">Sequence</label>
                          <div className="font-mono font-bold text-xl text-blue-600">{currentWO.sequence_no}</div>
                        </div>
                        <div>
                          <label className="text-xs text-gray-600 uppercase">Target Time</label>
                          <div className="font-mono font-bold text-xl text-green-600">{formatTime(currentWO.target_time)}</div>
                        </div>
                      </div>

                      <div>
                        <label className="text-xs text-gray-600 uppercase">Serial Number</label>
                        <div className="font-mono font-bold">{scannedSerial}</div>
                      </div>
                    </div>
                  </div>

                  {/* Work Instructions */}
                  {currentWO.work_instructions && (
                    <div className="bg-white rounded-lg shadow p-6 border border-gray-200 flex-1 overflow-auto">
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <BookOpen className="w-5 h-5 text-purple-600" />
                        Work Instructions
                      </h3>

                      <div className="space-y-2">
                        {currentWO.work_instructions.split('\n').map((instruction, index) => (
                          <div key={index} className="flex items-start gap-3 p-2 hover:bg-gray-50 rounded">
                            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-xs font-bold">
                              {index + 1}
                            </div>
                            <p className="text-sm text-gray-700 flex-1">{instruction}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Middle Column: Execution Control + Timer */}
                <div className="col-span-4 flex flex-col gap-6">
                  {/* Timer Display */}
                  <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg shadow-lg p-8 text-white">
                    <div className="text-center">
                      <div className="text-sm font-medium mb-2 opacity-90">Elapsed Time</div>
                      <div className="text-7xl font-mono font-bold tracking-tight">
                        {formatTime(elapsedTime)}
                      </div>
                      <div className="text-sm mt-3 font-medium">
                        {session?.status === 'In Progress' && (
                          <span className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 rounded-full">
                            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                            Running
                          </span>
                        )}
                        {session?.status === 'Paused' && (
                          <span className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 rounded-full">
                            <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                            Paused
                          </span>
                        )}
                        {!session && (
                          <span className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 rounded-full">
                            Ready to start
                          </span>
                        )}
                      </div>
                      
                      {/* Target vs Actual */}
                      <div className="mt-6 pt-6 border-t border-white/20">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <div className="opacity-75 mb-1">Target</div>
                            <div className="text-2xl font-bold">{formatTime(currentWO.target_time)}</div>
                          </div>
                          <div>
                            <div className="opacity-75 mb-1">Actual</div>
                            <div className={`text-2xl font-bold ${
                              elapsedTime > currentWO.target_time ? 'text-red-300' : 'text-green-300'
                            }`}>
                              {formatTime(elapsedTime)}
                            </div>
                          </div>
                        </div>
                        {elapsedTime > currentWO.target_time && session?.status === 'In Progress' && (
                          <div className="mt-3 text-xs bg-red-500/30 px-3 py-2 rounded-lg font-medium">
                            ⚠️ Over target by {formatTime(elapsedTime - currentWO.target_time)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Control Buttons */}
                  <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <Clock className="w-5 h-5 text-green-600" />
                      Execution Control
                    </h3>

                    <div className="space-y-3">
                      {!session && (
                        <button
                          onClick={handleStartExecution}
                          className="w-full py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2 text-lg font-medium shadow-lg hover:shadow-xl transition-all"
                        >
                          <Play className="w-6 h-6" />
                          Start Execution
                        </button>
                      )}

                      {session?.status === 'In Progress' && (
                        <>
                          <button
                            onClick={handlePauseExecution}
                            className="w-full py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 flex items-center justify-center gap-2 font-medium"
                          >
                            <Pause className="w-5 h-5" />
                            Pause
                          </button>
                          
                          {/* Andon Call Button */}
                          <button
                            onClick={() => {
                              if (session) {
                                setSession({ ...session, andon_called: true });
                                toast.error('🚨 ANDON CALL - Help requested!');
                              }
                            }}
                            className={`w-full py-3 ${
                              session.andon_called 
                                ? 'bg-red-800 text-white' 
                                : 'bg-red-600 text-white'
                            } rounded-lg hover:bg-red-700 flex items-center justify-center gap-2 font-medium ${
                              !session.andon_called ? 'animate-pulse' : ''
                            }`}
                          >
                            <AlertTriangle className="w-5 h-5" />
                            {session.andon_called ? 'Help Requested ✓' : 'Call for Help (Andon)'}
                          </button>
                        </>
                      )}

                      {session?.status === 'Paused' && (
                        <button
                          onClick={handleResumeExecution}
                          className="w-full py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 text-lg font-medium"
                        >
                          <Play className="w-6 h-6" />
                          Resume
                        </button>
                      )}

                      {session && (
                        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200">
                          <button
                            onClick={() => handleCompleteExecution('OK')}
                            className="py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2 font-medium shadow hover:shadow-lg transition-all"
                          >
                            <CheckCircle className="w-5 h-5" />
                            Complete OK
                          </button>
                          <button
                            onClick={() => handleCompleteExecution('NG')}
                            className="py-4 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center justify-center gap-2 font-medium shadow hover:shadow-lg transition-all"
                          >
                            <XCircle className="w-5 h-5" />
                            Complete NG
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Session Info */}
                    {session && (
                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <div className="text-xs text-gray-600 font-medium mb-2">Session Info</div>
                        <div className="text-xs text-gray-500 space-y-1">
                          <div className="flex justify-between">
                            <span>Exec ID:</span>
                            <span className="font-mono">{session.exec_id}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Started:</span>
                            <span>{new Date(session.start_time).toLocaleTimeString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Station:</span>
                            <span className="font-mono">{session.station_id}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Right Column: QC Checkpoints + Parts List */}
                <div className="col-span-4 flex flex-col gap-6 overflow-auto">
                  {/* QC Checkpoints */}
                  {currentWO.qc_checkpoints && currentWO.qc_checkpoints.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        QC Checkpoints
                        <span className="ml-auto text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full font-medium">
                          {currentWO.qc_checkpoints.length} Required
                        </span>
                      </h3>

                      <div className="space-y-3">
                        {currentWO.qc_checkpoints.map((checkpoint, index) => {
                          const qcResult = session?.qc_results?.find(r => r.checkpoint_id === checkpoint.id);
                          
                          return (
                            <div 
                              key={checkpoint.id} 
                              className={`p-4 rounded-lg border-2 transition-all ${
                                qcResult 
                                  ? qcResult.result === 'Pass' 
                                    ? 'bg-green-50 border-green-300' 
                                    : 'bg-red-50 border-red-300'
                                  : 'bg-gray-50 border-gray-200'
                              }`}
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <div className="font-bold text-sm">{checkpoint.name}</div>
                                    {checkpoint.mandatory && (
                                      <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded font-medium">
                                        Mandatory
                                      </span>
                                    )}
                                  </div>
                                  <div className="text-xs text-gray-600 mb-2">
                                    <div className="font-medium">{checkpoint.type}</div>
                                    <div className="text-gray-500">Spec: {checkpoint.spec}</div>
                                  </div>
                                  {qcResult && (
                                    <div className={`text-xs font-medium mt-2 ${
                                      qcResult.result === 'Pass' ? 'text-green-600' : 'text-red-600'
                                    }`}>
                                      {qcResult.result === 'Pass' ? '✓' : '✗'} {qcResult.result} - Value: {qcResult.value}
                                    </div>
                                  )}
                                </div>
                                <button
                                  onClick={() => handleQCModalOpen(index)}
                                  disabled={!!qcResult}
                                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                                    qcResult
                                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                                      : 'bg-blue-600 text-white hover:bg-blue-700 shadow hover:shadow-lg'
                                  }`}
                                >
                                  {qcResult ? 'Checked' : 'Check'}
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Parts List */}
                  {partsList.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <Package className="w-5 h-5 text-orange-600" />
                        Parts & Materials
                        <span className="ml-auto text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded-full font-medium">
                          {partsList.length} Items
                        </span>
                      </h3>

                      <div className="space-y-3">
                        {partsList.map((part, index) => {
                          const isComplete = part.qty_consumed >= part.qty_required;
                          const progress = (part.qty_consumed / part.qty_required) * 100;
                          
                          return (
                            <div 
                              key={part.part_no} 
                              className={`p-4 rounded-lg border-2 transition-all ${
                                isComplete 
                                  ? 'bg-green-50 border-green-300' 
                                  : 'bg-gray-50 border-gray-200'
                              }`}
                            >
                              <div className="flex items-start justify-between gap-3 mb-2">
                                <div className="flex-1">
                                  <div className="font-bold text-sm mb-1">{part.part_name}</div>
                                  <div className="text-xs text-gray-500 font-mono">{part.part_no}</div>
                                </div>
                                <button
                                  onClick={() => handlePartConsumption(index)}
                                  disabled={isComplete}
                                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                                    isComplete
                                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                                      : 'bg-orange-600 text-white hover:bg-orange-700 shadow hover:shadow-lg'
                                  }`}
                                >
                                  {isComplete ? 'Complete' : 'Consume'}
                                </button>
                              </div>
                              
                              {/* Progress bar */}
                              <div className="space-y-1">
                                <div className="flex justify-between text-xs text-gray-600">
                                  <span>Progress</span>
                                  <span className="font-medium">
                                    {part.qty_consumed} / {part.qty_required} {part.unit}
                                  </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                  <div 
                                    className={`h-full transition-all ${
                                      isComplete ? 'bg-green-500' : 'bg-orange-500'
                                    }`}
                                    style={{ width: `${progress}%` }}
                                  ></div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* QC Modal */}
      {showQCModal && currentWO && currentWO.qc_checkpoints && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              QC Checkpoint {currentQCIndex + 1} of {currentWO.qc_checkpoints.length}
            </h3>

            {currentWO.qc_checkpoints[currentQCIndex] && (
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="font-bold text-lg mb-2">
                    {currentWO.qc_checkpoints[currentQCIndex].name}
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div><span className="font-medium">Type:</span> {currentWO.qc_checkpoints[currentQCIndex].type}</div>
                    <div><span className="font-medium">Specification:</span> {currentWO.qc_checkpoints[currentQCIndex].spec}</div>
                    {currentWO.qc_checkpoints[currentQCIndex].unit && (
                      <div><span className="font-medium">Unit:</span> {currentWO.qc_checkpoints[currentQCIndex].unit}</div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Enter Measured Value
                  </label>
                  <input
                    type="text"
                    value={qcValue}
                    onChange={(e) => setQcValue(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleQCSubmit()}
                    placeholder={
                      currentWO.qc_checkpoints[currentQCIndex].type === 'Visual' || 
                      currentWO.qc_checkpoints[currentQCIndex].type === 'Functional' 
                        ? 'Enter "Pass" or "Fail"' 
                        : 'Enter measured value'
                    }
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleQCSubmit}
                    className="flex-1 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                  >
                    Submit
                  </button>
                  <button
                    onClick={handleQCModalClose}
                    className="flex-1 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

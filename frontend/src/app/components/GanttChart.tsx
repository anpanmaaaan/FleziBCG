// TRUE Gantt Chart Component for MES Operation Execution Tracking
// Time-based positioning, NOT percentage-based
// ISA-95 compliant

import { memo, useMemo } from 'react';
import { FixedSizeList, type ListChildComponentProps } from 'react-window';
import { Clock, AlertTriangle } from 'lucide-react';

// ============ TYPES ============
export interface OperationExecutionGantt {
  id: string;
  sequence: number;
  name: string;
  workstation: string;
  operatorName?: string;
  status: 'Not Started' | 'Running' | 'Completed' | 'Delayed' | 'Blocked';
  
  // Time values (ISO string or timestamp)
  plannedStart: string;
  plannedEnd: string;
  actualStart?: string;
  actualEnd?: string;
  
  // For running operations
  currentTime?: string; // Real-time position
  
  // Metadata
  delayMinutes?: number;
  qcRequired?: boolean;
}

interface GanttChartProps {
  operations: OperationExecutionGantt[];
  onOperationClick?: (operation: OperationExecutionGantt) => void;
  selectedOperationId?: string;
  timeZone?: string; // 'shift' or 'day'
}

type TimeScale = {
  start: number;
  end: number;
  duration: number;
  startDate: Date;
  endDate: Date;
};

type TimeGridLine = {
  position: number;
  label: string;
  isHour: boolean;
};

type GanttRowData = {
  operations: OperationExecutionGantt[];
  selectedOperationId?: string;
  timeScale: TimeScale;
  onOperationClick?: (operation: OperationExecutionGantt) => void;
};

const ROW_HEIGHT_PX = 64;
const ROWS_VIEWPORT_HEIGHT_PX = 640;
const LABEL_WIDTH_PX = 256;
const LABEL_GAP_PX = 16;
const TIMELINE_LEFT_OFFSET_PX = LABEL_WIDTH_PX + LABEL_GAP_PX;

// ============ TIME UTILITIES ============
const parseTime = (timeStr: string): Date => {
  return new Date(timeStr);
};

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });
};

const formatTimeShort = (date: Date): string => {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit',
    hour12: false 
  });
};

const calculateTimeScale = (operations: OperationExecutionGantt[]): TimeScale | null => {
  if (operations.length === 0) {
    return null;
  }

  let minTime = Number.POSITIVE_INFINITY;
  let maxTime = Number.NEGATIVE_INFINITY;

  for (const op of operations) {
    const times = [
      parseTime(op.plannedStart).getTime(),
      parseTime(op.plannedEnd).getTime(),
      op.actualStart ? parseTime(op.actualStart).getTime() : 0,
      op.actualEnd ? parseTime(op.actualEnd).getTime() : 0,
      op.currentTime ? parseTime(op.currentTime).getTime() : 0,
    ];

    for (const value of times) {
      if (value <= 0) {
        continue;
      }
      if (value < minTime) {
        minTime = value;
      }
      if (value > maxTime) {
        maxTime = value;
      }
    }
  }

  if (!Number.isFinite(minTime) || !Number.isFinite(maxTime)) {
    return null;
  }

  const baseDuration = Math.max(maxTime - minTime, 1);
  const padding = baseDuration * 0.1;
  const timelineStart = minTime - padding;
  const timelineEnd = maxTime + padding;
  const timelineDuration = Math.max(timelineEnd - timelineStart, 1);

  return {
    start: timelineStart,
    end: timelineEnd,
    duration: timelineDuration,
    startDate: new Date(timelineStart),
    endDate: new Date(timelineEnd),
  };
};

const buildTimeGrid = (timeScale: TimeScale): TimeGridLine[] => {
  const gridLines: TimeGridLine[] = [];
  const duration = timeScale.duration;
  const hourInMs = 60 * 60 * 1000;

  // Determine interval based on duration
  let interval = hourInMs; // 1 hour default
  if (duration < 4 * hourInMs) {
    interval = 30 * 60 * 1000; // 30 minutes for short durations
  } else if (duration > 12 * hourInMs) {
    interval = 2 * hourInMs; // 2 hours for long durations
  }

  let currentTime = Math.ceil(timeScale.start / interval) * interval;

  while (currentTime <= timeScale.end) {
    const position = ((currentTime - timeScale.start) / timeScale.duration) * 100;
    const date = new Date(currentTime);

    gridLines.push({
      position,
      label: formatTime(date),
      isHour: date.getMinutes() === 0,
    });

    currentTime += interval;
  }

  return gridLines;
};

const timeToPosition = (timeStr: string, timeScale: TimeScale): number => {
  const time = parseTime(timeStr).getTime();
  const position = ((time - timeScale.start) / timeScale.duration) * 100;
  return Math.max(0, Math.min(100, position));
};

const getBarGeometry = (op: OperationExecutionGantt, timeScale: TimeScale) => {
  let startTime: string;
  let endTime: string;

  if (op.status === 'Not Started') {
    startTime = op.plannedStart;
    endTime = op.plannedEnd;
  } else if (op.status === 'Running') {
    startTime = op.actualStart || op.plannedStart;
    endTime = op.currentTime || op.plannedEnd;
  } else {
    startTime = op.actualStart || op.plannedStart;
    endTime = op.actualEnd || op.plannedEnd;
  }

  const left = timeToPosition(startTime, timeScale);
  const right = timeToPosition(endTime, timeScale);
  const width = Math.max(right - left, 0.5);

  return { left, width };
};

const getPlannedWindow = (op: OperationExecutionGantt, timeScale: TimeScale) => {
  const left = timeToPosition(op.plannedStart, timeScale);
  const right = timeToPosition(op.plannedEnd, timeScale);
  const width = Math.max(right - left, 0.5);
  return { left, width };
};

const getBarStyle = (op: OperationExecutionGantt) => {
  switch (op.status) {
    case 'Not Started':
      return 'bg-gray-300 border-2 border-dashed border-gray-400';
    case 'Running':
      return 'bg-blue-500';
    case 'Completed':
      return 'bg-green-500';
    case 'Delayed':
      return 'bg-red-500';
    case 'Blocked':
      return 'bg-red-600';
    default:
      return 'bg-gray-400';
  }
};

const areRowPropsEqual = (
  prevProps: ListChildComponentProps<GanttRowData>,
  nextProps: ListChildComponentProps<GanttRowData>,
) => {
  if (prevProps.index !== nextProps.index) {
    return false;
  }

  const prevData = prevProps.data;
  const nextData = nextProps.data;
  const prevOp = prevData.operations[prevProps.index];
  const nextOp = nextData.operations[nextProps.index];

  if (!prevOp || !nextOp) {
    return false;
  }

  if (prevOp !== nextOp || prevOp.id !== nextOp.id) {
    return false;
  }

  if (prevData.timeScale !== nextData.timeScale) {
    return false;
  }

  const wasSelected = prevData.selectedOperationId === prevOp.id;
  const isSelected = nextData.selectedOperationId === nextOp.id;
  if (wasSelected !== isSelected) {
    return false;
  }

  const prevStyle = prevProps.style;
  const nextStyle = nextProps.style;
  return (
    prevStyle.top === nextStyle.top &&
    prevStyle.left === nextStyle.left &&
    prevStyle.height === nextStyle.height &&
    prevStyle.width === nextStyle.width
  );
};

const GanttRow = memo(function GanttRow({ index, style, data }: ListChildComponentProps<GanttRowData>) {
  const op = data.operations[index];
  const isSelected = op.id === data.selectedOperationId;
  const barGeo = getBarGeometry(op, data.timeScale);
  const plannedGeo = getPlannedWindow(op, data.timeScale);

  if (import.meta.env.DEV && typeof window !== 'undefined') {
    const debugRenderCount = window.localStorage.getItem('gantt.debug.row.renders') === '1';
    if (debugRenderCount) {
      console.count(`GanttRow render ${op.id}`);
    }
  }

  return (
    <div style={style} className="flex border-b border-gray-100">
      <div className="flex h-full items-center" style={{ width: LABEL_WIDTH_PX, paddingRight: LABEL_GAP_PX }}>
        <div className="flex items-center gap-3 w-full">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 ${
            op.status === 'Completed' ? 'bg-green-100 text-green-700' :
            op.status === 'Running' ? 'bg-blue-100 text-blue-700' :
            op.status === 'Delayed' ? 'bg-red-100 text-red-700' :
            'bg-gray-100 text-gray-600'
          }`}>
            {op.sequence}
          </div>

          <div className="flex-1 min-w-0">
            <div className="font-medium text-sm truncate">{op.name}</div>
            <div className="text-xs text-gray-500 truncate">{op.workstation}</div>
          </div>
        </div>
      </div>

      <div className="relative flex-1 min-w-0 h-full">
        {op.status !== 'Not Started' && (
          <div
            className="absolute top-2 bottom-2 bg-gray-100 rounded opacity-50"
            style={{
              left: `${plannedGeo.left}%`,
              width: `${plannedGeo.width}%`,
            }}
          />
        )}

        <div
          onClick={() => data.onOperationClick?.(op)}
          className={`absolute top-3 bottom-3 rounded cursor-pointer transition-all ${getBarStyle(op)} ${
            isSelected ? 'ring-4 ring-blue-300 ring-opacity-50 shadow-lg' : 'hover:shadow-md'
          }`}
          style={{
            left: `${barGeo.left}%`,
            width: `${barGeo.width}%`,
          }}
        >
          <div className="h-full flex items-center justify-between px-3 text-white text-xs font-medium">
            <span className="truncate">
              {op.status === 'Running' && '▶ '}
              {op.operatorName || op.name}
            </span>

            {op.delayMinutes && op.delayMinutes > 0 && (
              <span className="flex items-center gap-1 ml-2 bg-white bg-opacity-20 px-2 py-0.5 rounded">
                <AlertTriangle className="w-3 h-3" />
                +{op.delayMinutes}m
              </span>
            )}
          </div>

          {op.status === 'Running' && (
            <div className="absolute inset-0 border-2 border-white border-opacity-40 rounded animate-pulse" />
          )}
        </div>

        <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity pointer-events-none">
          <div className="absolute top-0 left-2 text-xs text-gray-600 bg-white px-1 rounded">
            {op.actualStart ? formatTime(parseTime(op.actualStart)) : formatTime(parseTime(op.plannedStart))}
          </div>
          <div className="absolute top-0 right-2 text-xs text-gray-600 bg-white px-1 rounded">
            {op.actualEnd ? formatTime(parseTime(op.actualEnd)) :
             op.currentTime ? formatTime(parseTime(op.currentTime)) :
             formatTime(parseTime(op.plannedEnd))}
          </div>
        </div>
      </div>
    </div>
  );
}, areRowPropsEqual);

// ============ GANTT CHART COMPONENT ============
export function GanttChart({ 
  operations, 
  onOperationClick, 
  selectedOperationId,
  timeZone = 'shift'
}: GanttChartProps) {
  void timeZone;

  // ============ TIME SCALE CALCULATION ============
  const timeScale = useMemo(() => calculateTimeScale(operations), [operations]);

  // ============ TIME GRID ============
  const timeGrid = useMemo(() => {
    if (!timeScale) {
      return [] as TimeGridLine[];
    }
    return buildTimeGrid(timeScale);
  }, [timeScale]);

  // All hooks must run before any early return.
  // rowData is only consumed in the render path below that guards timeScale !== null.
  const rowData = useMemo<GanttRowData | null>(() => {
    if (!timeScale) {
      return null;
    }
    return {
      operations,
      selectedOperationId,
      timeScale,
      onOperationClick,
    };
  }, [operations, selectedOperationId, timeScale, onOperationClick]);

  const listHeight = Math.min(ROWS_VIEWPORT_HEIGHT_PX, Math.max(operations.length * ROW_HEIGHT_PX, ROW_HEIGHT_PX));

  if (!timeScale || operations.length === 0 || rowData === null) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <div className="text-lg font-medium">No operations to display</div>
      </div>
    );
  }
  
  // ============ RENDER ============
  return (
    <div className="bg-white rounded-lg border">
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold">Operation Execution Timeline</h3>
            <div className="text-sm text-gray-500 mt-1">
              Time-based Gantt • {formatTime(timeScale.startDate)} → {formatTime(timeScale.endDate)}
            </div>
          </div>
          
          {/* Legend */}
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-8 h-3 bg-gray-300 border-2 border-dashed border-gray-400 rounded" />
              <span>Not Started</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-8 h-3 bg-blue-500 rounded" />
              <span>Running</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-8 h-3 bg-green-500 rounded" />
              <span>Completed</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-8 h-3 bg-red-500 rounded" />
              <span>Delayed</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Gantt Chart */}
      <div className="p-6">
        <div className="flex">
          <div style={{ width: TIMELINE_LEFT_OFFSET_PX }} className="flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="h-12 relative border-b border-gray-300">
              {timeGrid.map((grid, idx) => (
                <div
                  key={idx}
                  className="absolute top-0 bottom-0"
                  style={{ left: `${grid.position}%` }}
                >
                  <div className={`h-full ${grid.isHour ? 'border-l-2 border-gray-400' : 'border-l border-gray-300'}`} />
                  <div className={`absolute top-1 -translate-x-1/2 text-xs ${grid.isHour ? 'font-medium text-gray-700' : 'text-gray-500'}`}>
                    {grid.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="relative">
          <div
            className="absolute top-0 bottom-0 pointer-events-none"
            style={{ left: TIMELINE_LEFT_OFFSET_PX, right: 0 }}
          >
            {timeGrid.map((grid, gridIdx) => (
              <div
                key={gridIdx}
                className={`absolute top-0 bottom-0 ${grid.isHour ? 'border-l border-gray-200' : 'border-l border-gray-100'}`}
                style={{ left: `${grid.position}%` }}
              />
            ))}
          </div>

          <FixedSizeList
            height={listHeight}
            width="100%"
            itemCount={operations.length}
            itemSize={ROW_HEIGHT_PX}
            itemData={rowData}
            itemKey={(index, data) => data.operations[index]?.id ?? String(index)}
          >
            {GanttRow}
          </FixedSizeList>
        </div>
      </div>
      
      {/* Footer info */}
      <div className="border-t p-3 bg-gray-50 text-xs text-gray-600">
        <div className="flex items-center gap-6">
          <span>📊 Time-based positioning (not percentage)</span>
          <span>•</span>
          <span>Gaps and overlaps are visible</span>
          <span>•</span>
          <span>Planned window shown as background reference</span>
        </div>
      </div>
    </div>
  );
}

// ============ SAMPLE DATA STRUCTURE ============
/*
const sampleOperations: OperationExecutionGantt[] = [
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
  },
  {
    id: 'OP-030',
    sequence: 30,
    name: 'Surface Treatment',
    workstation: 'WS-02',
    status: 'Not Started',
    plannedStart: '2024-04-15T13:00:00',
    plannedEnd: '2024-04-15T18:00:00',
  },
];

// Time-based positioning explanation:
// 1. Calculate timeline bounds: min(all start times) to max(all end times)
// 2. For each operation bar:
//    - position (left) = ((startTime - timelineStart) / timelineDuration) * 100%
//    - width = ((endTime - startTime) / timelineDuration) * 100%
// 3. Bars align to actual time, NOT to planned slots
// 4. Delays/overruns visible through bar extension beyond planned window
// 5. Gaps between operations visible through empty space
*/

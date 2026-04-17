// TRUE Gantt Chart Component for MES Operation Execution Tracking
// Time-based positioning, NOT percentage-based
// ISA-95 compliant

import { memo, useEffect, useMemo, useState } from 'react';
import { FixedSizeList, type ListChildComponentProps } from 'react-window';
import { Clock, AlertTriangle, ChevronDown, ChevronRight } from 'lucide-react';

// ============ TYPES ============
export interface OperationExecutionGantt {
  id: string;
  sequence: number;
  name: string;
  workstation: string;
  area?: string;
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

type GanttTimelineMode = 'shift' | 'day' | 'week' | 'fit_all' | 'fit_selection';

export type GanttClickContext = {
  mode: GanttTimelineMode;
  groupBy: 'none' | 'workstation' | 'area';
  viewportStart: number;
  viewportEnd: number;
};

interface GanttChartProps {
  operations: OperationExecutionGantt[];
  onOperationClick?: (operation: OperationExecutionGantt, context: GanttClickContext) => void;
  selectedOperationId?: string;
  timeZone?: string; // 'shift' or 'day'
  groupBy?: 'none' | 'workstation' | 'area';
  /** Restored mode from back-navigation. Takes priority over timeZone. */
  initialMode?: GanttTimelineMode;
}

type GanttViewport = {
  visibleStartMs: number;
  visibleEndMs: number;
  mode: GanttTimelineMode;
};

type TimeGridLine = {
  position: number;
  label: string;
  isHour: boolean;
};

type NormalizedOperationExecutionGantt = {
  raw: OperationExecutionGantt;
  id: string;
  status: OperationExecutionGantt['status'];
  sequence: number;
  name: string;
  workstation: string;
  area?: string;
  operatorName?: string;
  plannedStartMs: number;
  plannedEndMs: number;
  actualStartMs?: number;
  actualEndMs?: number;
  currentTimeMs?: number;
  delayMinutes?: number;
  qcRequired?: boolean;
};

type GanttRowGroup = {
  id: string;
  label: string;
  summary: GanttGroupSummary;
  operations: NormalizedOperationExecutionGantt[];
};

type GanttGroupSummary = {
  total: number;
  running: number;
  blocked: number;
  delayed: number;
};

type GanttRenderRow =
  | {
      type: 'group';
      groupKey: string;
      groupLabel: string;
      summary: GanttGroupSummary;
      collapsed: boolean;
    }
  | {
      type: 'operation';
      operation: NormalizedOperationExecutionGantt;
    };

type GanttRowData = {
  rows: GanttRenderRow[];
  selectedOperationId?: string;
  viewport: GanttViewport;
  nowMs: number;
  onOperationClick?: (operation: OperationExecutionGantt) => void;
  onGroupToggle: (groupKey: string) => void;
};

const ROW_HEIGHT_PX = 64;
const ROWS_VIEWPORT_HEIGHT_PX = 640;
const LABEL_WIDTH_PX = 256;
const LABEL_GAP_PX = 16;
const TIMELINE_LEFT_OFFSET_PX = LABEL_WIDTH_PX + LABEL_GAP_PX;
const MIN_TIMELINE_DURATION_MS = 60 * 1000;
const GROUP_THRESHOLD = 200;

// ============ TIME UTILITIES ============
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

const resolveTimelineMode = (timeZone: string | undefined): GanttTimelineMode => {
  if (timeZone === 'day') {
    return 'day';
  }
  if (timeZone === 'week') {
    return 'week';
  }
  if (timeZone === 'fit_all') {
    return 'fit_all';
  }
  if (timeZone === 'fit_selection') {
    return 'fit_selection';
  }
  return 'shift';
};

const normalizeOperation = (op: OperationExecutionGantt): NormalizedOperationExecutionGantt => {
  const plannedStartMs = new Date(op.plannedStart).getTime();
  const plannedEndMs = new Date(op.plannedEnd).getTime();

  return {
    raw: op,
    id: op.id,
    status: op.status,
    sequence: op.sequence,
    name: op.name,
    workstation: op.workstation,
    area: op.area,
    operatorName: op.operatorName,
    plannedStartMs,
    plannedEndMs,
    actualStartMs: op.actualStart ? new Date(op.actualStart).getTime() : undefined,
    actualEndMs: op.actualEnd ? new Date(op.actualEnd).getTime() : undefined,
    currentTimeMs: op.currentTime ? new Date(op.currentTime).getTime() : undefined,
    delayMinutes: op.delayMinutes,
    qcRequired: op.qcRequired,
  };
};

const buildShiftViewport = (anchorMs: number): GanttViewport => {
  const shiftDurationMs = 8 * 60 * 60 * 1000;
  const anchorDate = new Date(anchorMs);
  const shiftStartDate = new Date(anchorDate);
  shiftStartDate.setHours(Math.floor(anchorDate.getHours() / 8) * 8, 0, 0, 0);
  const visibleStartMs = shiftStartDate.getTime();
  return {
    visibleStartMs,
    visibleEndMs: visibleStartMs + shiftDurationMs,
    mode: 'shift',
  };
};

const buildDayViewport = (anchorMs: number): GanttViewport => {
  const startDate = new Date(anchorMs);
  startDate.setHours(0, 0, 0, 0);
  const visibleStartMs = startDate.getTime();
  return {
    visibleStartMs,
    visibleEndMs: visibleStartMs + 24 * 60 * 60 * 1000,
    mode: 'day',
  };
};

const buildWeekViewport = (anchorMs: number): GanttViewport => {
  const startDate = new Date(anchorMs);
  const dayOfWeek = startDate.getDay();
  const mondayOffset = (dayOfWeek + 6) % 7;
  startDate.setDate(startDate.getDate() - mondayOffset);
  startDate.setHours(0, 0, 0, 0);
  const visibleStartMs = startDate.getTime();
  return {
    visibleStartMs,
    visibleEndMs: visibleStartMs + 7 * 24 * 60 * 60 * 1000,
    mode: 'week',
  };
};

const buildFitAllViewport = (operations: NormalizedOperationExecutionGantt[]): GanttViewport | null => {
  if (operations.length === 0) {
    return null;
  }

  let minMs = Number.POSITIVE_INFINITY;
  let maxMs = Number.NEGATIVE_INFINITY;

  for (const op of operations) {
    const values = [op.plannedStartMs, op.plannedEndMs, op.actualStartMs, op.actualEndMs];
    for (const value of values) {
      if (typeof value !== 'number' || Number.isNaN(value)) {
        continue;
      }
      if (value < minMs) {
        minMs = value;
      }
      if (value > maxMs) {
        maxMs = value;
      }
    }
  }

  if (!Number.isFinite(minMs) || !Number.isFinite(maxMs)) {
    return null;
  }

  const duration = Math.max(maxMs - minMs, MIN_TIMELINE_DURATION_MS);
  const padding = duration * 0.1;
  return {
    visibleStartMs: minMs - padding,
    visibleEndMs: maxMs + padding,
    mode: 'fit_all',
  };
};

const buildFitSelectionViewport = (
  operations: NormalizedOperationExecutionGantt[],
  selectedOperationId: string | undefined,
): GanttViewport | null => {
  if (!selectedOperationId) {
    return null;
  }
  const selected = operations.find((op) => op.id === selectedOperationId);
  if (!selected) {
    return null;
  }

  const startMs = selected.actualStartMs ?? selected.plannedStartMs;
  const endMs = selected.actualEndMs ?? selected.plannedEndMs;
  const duration = Math.max(endMs - startMs, MIN_TIMELINE_DURATION_MS);
  const padding = Math.max(duration * 0.5, 30 * 60 * 1000);

  return {
    visibleStartMs: startMs - padding,
    visibleEndMs: endMs + padding,
    mode: 'fit_selection',
  };
};

const chooseGridInterval = (durationMs: number, mode: GanttTimelineMode): number => {
  const intervalCandidatesMs = [
    15 * 60 * 1000,
    30 * 60 * 1000,
    60 * 60 * 1000,
    2 * 60 * 60 * 1000,
    3 * 60 * 60 * 1000,
    4 * 60 * 60 * 1000,
    6 * 60 * 60 * 1000,
    8 * 60 * 60 * 1000,
    12 * 60 * 60 * 1000,
    24 * 60 * 60 * 1000,
  ];

  const hardCap = mode === 'week' ? 84 : 48;
  for (const intervalMs of intervalCandidatesMs) {
    const tickCount = Math.ceil(durationMs / intervalMs) + 1;
    if (tickCount <= hardCap) {
      return intervalMs;
    }
  }
  return intervalCandidatesMs[intervalCandidatesMs.length - 1];
};

const buildTimeGrid = (viewport: GanttViewport): TimeGridLine[] => {
  const gridLines: TimeGridLine[] = [];
  const durationMs = Math.max(viewport.visibleEndMs - viewport.visibleStartMs, MIN_TIMELINE_DURATION_MS);
  const intervalMs = chooseGridInterval(durationMs, viewport.mode);

  let currentTimeMs = Math.ceil(viewport.visibleStartMs / intervalMs) * intervalMs;

  while (currentTimeMs <= viewport.visibleEndMs) {
    const position = ((currentTimeMs - viewport.visibleStartMs) / durationMs) * 100;
    const date = new Date(currentTimeMs);

    gridLines.push({
      position,
      label: formatTime(date),
      isHour: date.getMinutes() === 0,
    });

    currentTimeMs += intervalMs;
  }

  return gridLines;
};

const timeToPosition = (timeMs: number, viewport: GanttViewport): number => {
  const durationMs = Math.max(viewport.visibleEndMs - viewport.visibleStartMs, MIN_TIMELINE_DURATION_MS);
  const position = ((timeMs - viewport.visibleStartMs) / durationMs) * 100;
  return Math.max(0, Math.min(100, position));
};

const getBarGeometry = (
  op: NormalizedOperationExecutionGantt,
  viewport: GanttViewport,
  nowMs: number,
) => {
  let startTimeMs: number;
  let endTimeMs: number;

  if (op.status === 'Not Started') {
    startTimeMs = op.plannedStartMs;
    endTimeMs = op.plannedEndMs;
  } else if (op.status === 'Running') {
    startTimeMs = op.actualStartMs ?? op.plannedStartMs;
    endTimeMs = op.currentTimeMs ?? nowMs;
  } else {
    startTimeMs = op.actualStartMs ?? op.plannedStartMs;
    endTimeMs = op.actualEndMs ?? op.plannedEndMs;
  }

  const left = timeToPosition(startTimeMs, viewport);
  const right = timeToPosition(endTimeMs, viewport);
  const width = Math.max(right - left, 0.5);

  return { left, width };
};

const getPlannedWindow = (op: NormalizedOperationExecutionGantt, viewport: GanttViewport) => {
  const left = timeToPosition(op.plannedStartMs, viewport);
  const right = timeToPosition(op.plannedEndMs, viewport);
  const width = Math.max(right - left, 0.5);
  return { left, width };
};

const getBarStyle = (op: NormalizedOperationExecutionGantt) => {
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

const createEmptyGroupSummary = (): GanttGroupSummary => ({
  total: 0,
  running: 0,
  blocked: 0,
  delayed: 0,
});

const resolveEffectiveGroupBy = (
  groupBy: GanttChartProps['groupBy'],
  operationCount: number,
): NonNullable<GanttChartProps['groupBy']> => {
  if (groupBy) {
    return groupBy;
  }

  return operationCount > GROUP_THRESHOLD ? 'workstation' : 'none';
};

const getGroupLabel = (
  operation: NormalizedOperationExecutionGantt,
  groupMode: Exclude<NonNullable<GanttChartProps['groupBy']>, 'none'>,
): string => {
  if (groupMode === 'area') {
    return operation.area?.trim() || 'Unassigned Area';
  }

  return operation.workstation.trim() || 'Unassigned Workstation';
};

const formatGroupModeLabel = (groupMode: NonNullable<GanttChartProps['groupBy']>): string => {
  if (groupMode === 'workstation') {
    return 'Workstation';
  }
  if (groupMode === 'area') {
    return 'Area';
  }
  return 'Flat';
};

const formatTimelineModeLabel = (mode: GanttTimelineMode): string => {
  if (mode === 'fit_selection') {
    return 'Fit Selection';
  }
  if (mode === 'fit_all') {
    return 'Fit All';
  }
  return mode.charAt(0).toUpperCase() + mode.slice(1);
};

const renderSummaryPill = (label: string, value: number, className: string) => (
  <span className={`inline-flex items-center rounded-full px-2.5 py-1 font-medium ${className}`}>
    {label}: {value}
  </span>
);

const areRowPropsEqual = (
  prevProps: ListChildComponentProps<GanttRowData>,
  nextProps: ListChildComponentProps<GanttRowData>,
) => {
  if (prevProps.index !== nextProps.index) {
    return false;
  }

  const prevData = prevProps.data;
  const nextData = nextProps.data;
  const prevRow = prevData.rows[prevProps.index];
  const nextRow = nextData.rows[nextProps.index];

  if (!prevRow || !nextRow || prevRow.type !== nextRow.type) {
    return false;
  }

  if (prevRow.type === 'group') {
    if (
      prevRow.groupKey !== nextRow.groupKey ||
      prevRow.groupLabel !== nextRow.groupLabel ||
      prevRow.collapsed !== nextRow.collapsed ||
      prevRow.summary.total !== nextRow.summary.total ||
      prevRow.summary.running !== nextRow.summary.running ||
      prevRow.summary.blocked !== nextRow.summary.blocked ||
      prevRow.summary.delayed !== nextRow.summary.delayed
    ) {
      return false;
    }
  } else {
    const prevOp = prevRow.operation;
    const nextOp = nextRow.operation;

    if (prevOp !== nextOp || prevOp.id !== nextOp.id) {
      return false;
    }

    if (prevData.viewport !== nextData.viewport) {
      return false;
    }

    if (
      prevData.nowMs !== nextData.nowMs &&
      (prevOp.status === 'Running' || nextOp.status === 'Running')
    ) {
      return false;
    }

    const wasSelected = prevData.selectedOperationId === prevOp.id;
    const isSelected = nextData.selectedOperationId === nextOp.id;
    if (wasSelected !== isSelected) {
      return false;
    }
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
  const row = data.rows[index];

  if (!row) {
    return null;
  }

  if (row.type === 'group') {
    const GroupIcon = row.collapsed ? ChevronRight : ChevronDown;

    return (
      <div
        style={style}
        className="flex border-b border-slate-200 bg-slate-50/95"
      >
        <div className="flex h-full items-center" style={{ width: LABEL_WIDTH_PX, paddingRight: LABEL_GAP_PX }}>
          <div
            className="flex h-full w-full cursor-pointer items-center gap-3 rounded-md px-3 focus:outline-none focus:ring-2 focus:ring-focus-ring"
            onClick={() => data.onGroupToggle(row.groupKey)}
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                data.onGroupToggle(row.groupKey);
              }
            }}
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-200 text-slate-700">
              <GroupIcon className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-semibold text-slate-900">{row.groupLabel}</div>
              <div className="text-xs text-slate-500">{row.summary.total} operations</div>
            </div>
          </div>
        </div>

        <div className="flex min-w-0 flex-1 items-center justify-between gap-3 pr-4">
          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-600">
            {renderSummaryPill('Total', row.summary.total, 'bg-slate-200 text-slate-700')}
            {renderSummaryPill('Running', row.summary.running, 'bg-blue-100 text-blue-700')}
            {renderSummaryPill('Blocked', row.summary.blocked, 'bg-red-100 text-red-700')}
            {renderSummaryPill('Delayed', row.summary.delayed, 'bg-amber-100 text-amber-800')}
          </div>
          <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
            {row.collapsed ? 'Collapsed' : 'Expanded'}
          </div>
        </div>
      </div>
    );
  }

  const op = row.operation;
  const isSelected = op.id === data.selectedOperationId;
  const barGeo = getBarGeometry(op, data.viewport, data.nowMs);
  const plannedGeo = getPlannedWindow(op, data.viewport);
  const hoverEndMs =
    op.status === 'Not Started'
      ? op.plannedEndMs
      : op.status === 'Running'
        ? (op.currentTimeMs ?? data.nowMs)
        : (op.actualEndMs ?? op.plannedEndMs);

  if (import.meta.env.DEV && typeof window !== 'undefined') {
    const debugRenderCount = window.localStorage.getItem('gantt.debug.row.renders') === '1';
    if (debugRenderCount) {
      console.count(`GanttRow render ${op.id}`);
    }
  }

  return (
    <div
      style={style}
      className="flex border-b border-gray-100 cursor-pointer"
      onClick={() => data.onOperationClick?.(op.raw)}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          data.onOperationClick?.(op.raw);
        }
      }}
    >
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
          onClick={(event) => {
            event.stopPropagation();
            data.onOperationClick?.(op.raw);
          }}
          className={`absolute top-3 bottom-3 rounded cursor-pointer transition-all ${getBarStyle(op)} ${
            isSelected ? 'ring-4 ring-focus-ring ring-opacity-50 shadow-lg' : 'hover:shadow-md'
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
            {formatTime(new Date(op.actualStartMs ?? op.plannedStartMs))}
          </div>
          <div className="absolute top-0 right-2 text-xs text-gray-600 bg-white px-1 rounded">
            {formatTime(new Date(hoverEndMs))}
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
  timeZone = 'shift',
  groupBy,
  initialMode,
}: GanttChartProps) {
  // `initialMode` (from back-navigation) takes priority over timeZone.
  const initialTimelineMode = useMemo(
    () => initialMode ?? resolveTimelineMode(timeZone),
    [initialMode, timeZone],
  );
  const [timelineMode, setTimelineMode] = useState<GanttTimelineMode>(initialTimelineMode);
  const [hasUserSelectedTimelineMode, setHasUserSelectedTimelineMode] = useState(false);
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(() => new Set());

  useEffect(() => {
    if (!hasUserSelectedTimelineMode) {
      setTimelineMode(initialTimelineMode);
    }
  }, [hasUserSelectedTimelineMode, initialTimelineMode]);

  const normalizedOperations = useMemo(
    () => operations.map((op) => normalizeOperation(op)),
    [operations],
  );

  const effectiveGroupBy = useMemo(
    () => resolveEffectiveGroupBy(groupBy, normalizedOperations.length),
    [groupBy, normalizedOperations.length],
  );

  const groupedRows = useMemo<GanttRowGroup[]>(() => {
    if (effectiveGroupBy === 'none') {
      return [];
    }

    if (
      effectiveGroupBy === 'area' &&
      !normalizedOperations.some((op) => Boolean(op.area?.trim()))
    ) {
      return [];
    }

    const groupMap = new Map<string, GanttRowGroup>();
    for (const op of normalizedOperations) {
      const label = getGroupLabel(op, effectiveGroupBy);
      const key = `${effectiveGroupBy}:${label}`;
      const existing = groupMap.get(key);
      if (existing) {
        existing.operations.push(op);
        existing.summary.total += 1;
        if (op.status === 'Running') {
          existing.summary.running += 1;
        }
        if (op.status === 'Blocked') {
          existing.summary.blocked += 1;
        }
        if (op.status === 'Delayed') {
          existing.summary.delayed += 1;
        }
      } else {
        const summary = createEmptyGroupSummary();
        summary.total = 1;
        if (op.status === 'Running') {
          summary.running = 1;
        }
        if (op.status === 'Blocked') {
          summary.blocked = 1;
        }
        if (op.status === 'Delayed') {
          summary.delayed = 1;
        }

        groupMap.set(key, {
          id: key,
          label,
          summary,
          operations: [op],
        });
      }
    }

    return Array.from(groupMap.values());
  }, [normalizedOperations, effectiveGroupBy]);

  const isGroupedRendering = effectiveGroupBy !== 'none' && groupedRows.length > 0;

  useEffect(() => {
    setCollapsedGroups(new Set());
  }, [effectiveGroupBy]);

  const flattenedOperations = useMemo(
    () => normalizedOperations,
    [normalizedOperations],
  );

  const renderRows = useMemo<GanttRenderRow[]>(() => {
    if (!isGroupedRendering) {
      return normalizedOperations.map((operation) => ({
        type: 'operation',
        operation,
      }));
    }

    return groupedRows.flatMap((group) => {
      const collapsed = collapsedGroups.has(group.id);
      const rows: GanttRenderRow[] = [
        {
          type: 'group',
          groupKey: group.id,
          groupLabel: group.label,
          summary: group.summary,
          collapsed,
        },
      ];

      if (collapsed) {
        return rows;
      }

      return rows.concat(
        group.operations.map((operation) => ({
          type: 'operation',
          operation,
        })),
      );
    });
  }, [collapsedGroups, groupedRows, isGroupedRendering, normalizedOperations]);

  const handleGroupToggle = (groupKey: string) => {
    setCollapsedGroups((previous) => {
      const next = new Set(previous);
      if (next.has(groupKey)) {
        next.delete(groupKey);
      } else {
        next.add(groupKey);
      }
      return next;
    });
  };

  const visibleOperationCount = useMemo(
    () => renderRows.filter((row) => row.type === 'operation').length,
    [renderRows],
  );

  const timelineControls = useMemo(
    () => [
      {
        mode: 'shift' as const,
        label: 'Shift',
        title: 'Focus on the active shift horizon.',
      },
      {
        mode: 'day' as const,
        label: 'Day',
        title: 'Expand the viewport to the current day.',
      },
      {
        mode: 'week' as const,
        label: 'Week',
        title: 'Expand the viewport to the full week.',
      },
      {
        mode: 'fit_selection' as const,
        label: 'Fit Selection',
        title: selectedOperationId
          ? 'Analyze the selected operation in a focused window.'
          : 'Select an operation to enable focused analysis.',
        disabled: !selectedOperationId,
      },
      {
        mode: 'fit_all' as const,
        label: 'Fit All',
        title: 'Analyze the full work order horizon without changing the default mode.',
        badge: 'Analyze',
        secondary: true,
      },
    ],
    [selectedOperationId],
  );

  const handleTimelineModeSelect = (mode: GanttTimelineMode) => {
    setHasUserSelectedTimelineMode(true);
    setTimelineMode(mode);
  };

  const anchorMs = useMemo(() => {
    const selected = selectedOperationId
      ? flattenedOperations.find((op) => op.id === selectedOperationId)
      : undefined;
    if (selected) {
      return selected.plannedStartMs;
    }

    if (flattenedOperations.length > 0) {
      return flattenedOperations[0].plannedStartMs;
    }
    return Date.now();
  }, [flattenedOperations, selectedOperationId]);

  const viewport = useMemo(() => {
    if (flattenedOperations.length === 0) {
      return null;
    }

    if (timelineMode === 'fit_all') {
      const fitAllViewport = buildFitAllViewport(flattenedOperations);
      if (fitAllViewport) {
        return fitAllViewport;
      }
    }

    if (timelineMode === 'fit_selection') {
      const fitSelectionViewport = buildFitSelectionViewport(flattenedOperations, selectedOperationId);
      if (fitSelectionViewport) {
        return fitSelectionViewport;
      }
      const fallbackFitAll = buildFitAllViewport(flattenedOperations);
      if (fallbackFitAll) {
        return fallbackFitAll;
      }
    }

    if (timelineMode === 'day') {
      return buildDayViewport(anchorMs);
    }

    if (timelineMode === 'week') {
      return buildWeekViewport(anchorMs);
    }

    return buildShiftViewport(anchorMs);
  }, [flattenedOperations, timelineMode, anchorMs, selectedOperationId]);

  const nowMs = useMemo(() => {
    let maxCurrentTimeMs = Number.NEGATIVE_INFINITY;
    for (const op of flattenedOperations) {
      if (op.status !== 'Running') {
        continue;
      }
      if (typeof op.currentTimeMs === 'number' && op.currentTimeMs > maxCurrentTimeMs) {
        maxCurrentTimeMs = op.currentTimeMs;
      }
    }
    if (Number.isFinite(maxCurrentTimeMs)) {
      return maxCurrentTimeMs;
    }
    return Date.now();
  }, [flattenedOperations]);

  // ============ TIME GRID ============
  const timeGrid = useMemo(() => {
    if (!viewport) {
      return [] as TimeGridLine[];
    }
    return buildTimeGrid(viewport);
  }, [viewport]);

  const nowIndicatorPosition = useMemo(() => {
    if (!viewport) {
      return null;
    }
    if (nowMs < viewport.visibleStartMs || nowMs > viewport.visibleEndMs) {
      return null;
    }
    return timeToPosition(nowMs, viewport);
  }, [viewport, nowMs]);

  // Wrap onOperationClick to inject click context (mode, groupBy, viewport).
  const wrappedOnOperationClick = useMemo<GanttRowData['onOperationClick']>(() => {
    if (!onOperationClick || !viewport) {
      return undefined;
    }
    return (op: OperationExecutionGantt) => {
      onOperationClick(op, {
        mode: timelineMode,
        groupBy: effectiveGroupBy,
        viewportStart: viewport.visibleStartMs,
        viewportEnd: viewport.visibleEndMs,
      });
    };
  }, [onOperationClick, timelineMode, effectiveGroupBy, viewport]);

  // All hooks must run before any early return.
  // rowData is only consumed in the render path below that guards viewport !== null.
  const rowData = useMemo<GanttRowData | null>(() => {
    if (!viewport) {
      return null;
    }
    return {
      rows: renderRows,
      selectedOperationId,
      viewport,
      nowMs,
      onOperationClick: wrappedOnOperationClick,
      onGroupToggle: handleGroupToggle,
    };
  }, [renderRows, selectedOperationId, viewport, nowMs, wrappedOnOperationClick]);

  const listHeight = Math.min(
    ROWS_VIEWPORT_HEIGHT_PX,
    Math.max(renderRows.length * ROW_HEIGHT_PX, ROW_HEIGHT_PX),
  );

  if (!viewport || flattenedOperations.length === 0 || rowData === null) {
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
              Time-based Gantt • {formatTime(new Date(viewport.visibleStartMs))} → {formatTime(new Date(viewport.visibleEndMs))}
              {' '}• {flattenedOperations.length} ops
              {' '}• {isGroupedRendering ? `Grouped by ${formatGroupModeLabel(effectiveGroupBy)}` : 'Flat view'}
              {' '}• Mode: {formatTimelineModeLabel(timelineMode)}
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              {timelineControls.map((control) => {
                const isActive = control.mode === timelineMode;
                const isDisabled = control.disabled === true;

                return (
                  <button
                    key={control.mode}
                    type="button"
                    title={control.title}
                    disabled={isDisabled}
                    onClick={() => handleTimelineModeSelect(control.mode)}
                    className={[
                      'inline-flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-medium transition-colors',
                      isActive
                        ? control.secondary
                          ? 'border-slate-900 bg-slate-900 text-white'
                          : 'border-blue-600 bg-blue-600 text-white'
                        : control.secondary
                          ? 'border-slate-300 bg-slate-50 text-slate-700 hover:border-slate-400 hover:bg-slate-100'
                          : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 hover:bg-gray-50',
                      isDisabled ? 'cursor-not-allowed border-gray-200 bg-gray-100 text-gray-400 hover:border-gray-200 hover:bg-gray-100' : '',
                    ].join(' ')}
                  >
                    <span>{control.label}</span>
                    {control.badge && (
                      <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
                        isActive ? 'bg-white/20 text-white' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {control.badge}
                      </span>
                    )}
                  </button>
                );
              })}
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
              {nowIndicatorPosition !== null && (
                <div className="absolute top-0 bottom-0 pointer-events-none" style={{ left: `${nowIndicatorPosition}%` }}>
                  <div className="h-full border-l-2 border-blue-500" />
                </div>
              )}
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
            {nowIndicatorPosition !== null && (
              <div
                className="absolute top-0 bottom-0 border-l-2 border-blue-200"
                style={{ left: `${nowIndicatorPosition}%` }}
              />
            )}
          </div>

          <FixedSizeList
            height={listHeight}
            width="100%"
            itemCount={renderRows.length}
            itemSize={ROW_HEIGHT_PX}
            itemData={rowData}
            itemKey={(index, data) => {
              const row = data.rows[index];
              if (!row) {
                return String(index);
              }
              return row.type === 'group' ? `group:${row.groupKey}` : row.operation.id;
            }}
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
          {isGroupedRendering && (
            <>
              <span>•</span>
              <span>{renderRows.length - visibleOperationCount} group headers in virtual list</span>
            </>
          )}
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

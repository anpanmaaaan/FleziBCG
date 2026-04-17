import { useMemo, useState } from 'react';
import { Link } from 'react-router';
import { PageHeader } from '@/app/components';
import { GanttChart, type OperationExecutionGantt } from '@/app/components';

const BASE_START = new Date('2026-04-05T08:00:00Z').getTime();

const buildSyntheticOperations = (count: number): OperationExecutionGantt[] => {
  return Array.from({ length: count }, (_, index) => {
    const sequence = index + 1;
    const start = BASE_START + index * 5 * 60 * 1000;
    const plannedDurationMinutes = 20 + (index % 5) * 10;
    const plannedEnd = start + plannedDurationMinutes * 60 * 1000;

    const statusBucket = index % 4;
    const isRunning = statusBucket === 1;
    const isCompleted = statusBucket === 2;
    const isDelayed = statusBucket === 3;

    const actualStart = isRunning || isCompleted || isDelayed ? start + 2 * 60 * 1000 : undefined;
    const actualEnd = isCompleted || isDelayed ? plannedEnd + (isDelayed ? 8 : -3) * 60 * 1000 : undefined;
    const currentTime = isRunning ? start + 15 * 60 * 1000 : undefined;

    const status: OperationExecutionGantt['status'] =
      statusBucket === 0 ? 'Not Started' :
      isRunning ? 'Running' :
      isCompleted ? 'Completed' :
      'Delayed';

    return {
      id: `stress-op-${sequence}`,
      sequence,
      name: `Synthetic Operation ${sequence}`,
      workstation: `WS-${String((index % 20) + 1).padStart(2, '0')}`,
      operatorName: isRunning || isCompleted ? `Operator ${(index % 12) + 1}` : undefined,
      status,
      plannedStart: new Date(start).toISOString(),
      plannedEnd: new Date(plannedEnd).toISOString(),
      actualStart: actualStart ? new Date(actualStart).toISOString() : undefined,
      actualEnd: actualEnd ? new Date(actualEnd).toISOString() : undefined,
      currentTime: currentTime ? new Date(currentTime).toISOString() : undefined,
      delayMinutes: isDelayed ? 8 : undefined,
      qcRequired: index % 6 === 0,
    };
  });
};

export function GanttStressTestPage() {
  const [selectedOperationId, setSelectedOperationId] = useState<string | undefined>();

  const operations = useMemo(() => buildSyntheticOperations(2000), []);

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <PageHeader
        title="Gantt Stress Test (DEV only)"
        subtitle="Synthetic 2,000-row workload for virtualization verification"
        showBackButton={false}
        actions={
          <Link
            to="/work-orders"
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Back to Work Orders
          </Link>
        }
      />

      <div className="flex-1 overflow-auto p-6 space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
          Rendering 2,000 operations with virtual rows. Set localStorage key
          <span className="font-mono"> gantt.debug.row.renders=1</span> to inspect row render counts in console.
          Selected operation: <span className="font-mono">{selectedOperationId || '-'}</span>
        </div>

        <GanttChart
          operations={operations}
          selectedOperationId={selectedOperationId}
          onOperationClick={(operation) => setSelectedOperationId(operation.id)}
        />
      </div>
    </div>
  );
}

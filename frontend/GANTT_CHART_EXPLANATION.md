# 📊 TRUE MES GANTT CHART - Technical Explanation

## 🎯 Purpose

This is a **time-based Gantt chart** for MES Operation Execution Tracking, NOT a project management Gantt or progress bar list.

---

## 🏭 Business Context (ISA-95)

### Manufacturing Execution Reality:
- Operations execute sequentially on the shop floor
- Each operation has **planned schedule** (expectation) vs **actual execution** (reality)
- Operators **DO NOT adjust schedules** - they execute and report
- Delays, early finishes, and overruns must be **immediately visible**
- Gaps and overlaps between operations indicate problems

### Key Principle:
> **ONE BAR = ONE OPERATION EXECUTION**
> 
> The bar position and width are **calculated from TIME**, not percentage.

---

## 📐 Gantt Visualization Rules

### Axes:
- **X-axis:** Continuous time scale (hours/minutes within a shift)
- **Y-axis:** Ordered Operation Sequence (Op 10, 20, 30, 40...)

### Single Bar Behavior (CRITICAL):
Each operation is displayed as a **SINGLE horizontal bar**:
- The **planned schedule** defines the EXPECTED time window
- The **actual execution** defines the REAL bar shape

```
NOT THIS (2 bars):
Planned:  [========]
Actual:      [==========]

BUT THIS (1 bar with context):
         planned window
         [  reference  ]
            [=====]
         actual bar
```

---

## 🎨 Visual Interpretation

### Bar Positioning:
| Scenario | Visual Result |
|----------|---------------|
| **Started late** | Bar starts **to the right** of planned start |
| **Finished early** | Bar ends **to the left** of planned end |
| **Overran** | Bar extends **beyond** planned end boundary |
| **On-time** | Bar aligns with planned window |

### Planned Time Display:
Shown **implicitly** using:
- Faint background region (gray background)
- Vertical plan markers
- Grid lines at time intervals

**NOT** shown as a separate bar.

---

## 🎨 Execution States via Color

| Status | Color | Visual Style | Meaning |
|--------|-------|--------------|---------|
| **Not Started** | Gray | `bg-gray-300` + dashed border | Aligned to planned time, waiting |
| **Running** | Blue | `bg-blue-500` solid + pulse animation | Growing from actualStart to currentTime |
| **Completed (on-time)** | Green | `bg-green-500` solid | Finished within planned window |
| **Delayed** | Red | `bg-red-500` solid | Extends beyond plannedEnd |
| **Blocked** | Dark Red | `bg-red-600` solid | Stopped due to issue |

---

## ⚙️ Time-Based Positioning Algorithm

### Core Formula:

```typescript
// 1. Calculate timeline bounds
const timelineStart = min(all start times) - padding
const timelineEnd = max(all end times) + padding
const timelineDuration = timelineEnd - timelineStart

// 2. Convert time to pixel position (0-100%)
const timeToPosition = (timeStr: string): number => {
  const time = parseTime(timeStr).getTime(); // milliseconds
  const position = ((time - timelineStart) / timelineDuration) * 100;
  return position; // percentage
}

// 3. Calculate bar geometry
const barLeft = timeToPosition(operation.actualStart || operation.plannedStart)
const barRight = timeToPosition(operation.actualEnd || operation.currentTime || operation.plannedEnd)
const barWidth = barRight - barLeft
```

### Example Calculation:

```typescript
// Timeline: 07:00 to 18:00 (11 hours = 39,600,000 ms)
timelineStart = 1713160800000  // 07:00
timelineDuration = 39600000

// Operation: Started at 08:35, planned at 08:30
operation.plannedStart = '2024-04-15T08:30:00'  // 1713166200000
operation.actualStart = '2024-04-15T08:35:00'   // 1713166500000

// Planned position
plannedLeft = ((1713166200000 - 1713160800000) / 39600000) * 100
            = (5400000 / 39600000) * 100
            = 13.64%

// Actual position
actualLeft = ((1713166500000 - 1713160800000) / 39600000) * 100
           = (5700000 / 39600000) * 100
           = 14.39%

// The bar starts at 14.39%, not 13.64%
// The 0.75% gap shows the 5-minute delay visually
```

---

## 📊 Data Structure

```typescript
interface OperationExecutionGantt {
  id: string;
  sequence: number;
  name: string;
  workstation: string;
  operatorName?: string;
  status: 'Not Started' | 'Running' | 'Completed' | 'Delayed' | 'Blocked';
  
  // TIME VALUES (critical)
  plannedStart: string;    // ISO 8601: "2024-04-15T07:00:00"
  plannedEnd: string;      // ISO 8601: "2024-04-15T08:30:00"
  actualStart?: string;    // When operator actually started
  actualEnd?: string;      // When operator actually finished
  currentTime?: string;    // For running operations
  
  // Metadata
  delayMinutes?: number;   // Calculated delay
  qcRequired?: boolean;
}
```

### Sample Data:

```typescript
const operations: OperationExecutionGantt[] = [
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
    actualEnd: '2024-04-15T08:15:00',  // Early finish!
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
    actualStart: '2024-04-15T08:35:00',  // Started 5min late
    currentTime: '2024-04-15T11:30:00',  // Current position
    delayMinutes: 45,
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
```

---

## 🚫 Strict Constraints

### ❌ DO NOT:
1. Render planned and actual as **two separate bars**
2. Use **progress bars** (width ≠ completion %)
3. Use **completion percentages** for bar width
4. Show time deviation via **text labels only**
5. Use **arbitrary positioning** not based on time

### ✅ DO:
1. Calculate position from **actual time values**
2. Show gaps and overlaps **through spacing**
3. Use **color** to encode execution state
4. Make delays visible through **bar extension**
5. Keep timeline **deterministic and reusable**

---

## 🔍 Visual Problem Detection

### Gap Detection:
```
OP-10: [====]           ← Ended 08:15
           ↓ GAP (20 min)
OP-20:         [========] ← Started 08:35 (planned 08:30)
```
**Interpretation:** 20-minute gap indicates potential bottleneck or waiting time.

### Overlap Detection:
```
OP-10: [==========]     ← Should end 08:30
OP-20:      [========]  ← Started 08:20 (planned 08:30)
      overlap!
```
**Interpretation:** Impossible sequence or data error.

### Delay Detection:
```
Planned window: [................]
Actual bar:     [===================] ← extends beyond
                                  ↑ Overrun visible
```
**Interpretation:** Operation took longer than planned.

---

## 🎯 Key Advantages

### 1. Time Accuracy:
- Every pixel represents actual time
- Proportional to duration
- No percentage distortion

### 2. Visual Analysis:
- Gaps immediately visible
- Delays show as bar extension
- Early finish shows as shorter bar

### 3. Shop Floor Reality:
- Reflects actual execution sequence
- Shows cumulative delays
- Identifies bottlenecks

### 4. ISA-95 Compliant:
- Separates planned vs actual
- Shows execution hierarchy (WO → Operations)
- Tracks production performance

---

## 🛠️ Component Architecture

```
GanttChart.tsx
├── Time Scale Calculation
│   └── Find min/max times, add padding
├── Positioning Functions
│   ├── timeToPosition(time) → pixel %
│   └── getBarGeometry(operation) → { left, width }
├── Styling Functions
│   └── getBarStyle(operation) → CSS classes
├── Time Grid Generator
│   └── Generate hour/minute markers
└── Render
    ├── Y-axis: Operation labels
    ├── X-axis: Time grid
    └── Bars: Positioned by time
```

---

## 📚 Usage Example

```typescript
import { GanttChart, OperationExecutionGantt } from './components/GanttChart';

function OperationOverview() {
  const [operations, setOperations] = useState<OperationExecutionGantt[]>([...]);
  
  const handleOperationClick = (op: OperationExecutionGantt) => {
    navigate(`/operation-detail/${op.id}`);
  };
  
  return (
    <GanttChart 
      operations={operations}
      onOperationClick={handleOperationClick}
      selectedOperationId={selectedId}
    />
  );
}
```

---

## 🎓 Learning Points

### For Frontend Developers:
- **Time-based positioning** is fundamentally different from percentage
- Use `Date.getTime()` for precise calculations
- CSS `left` and `width` in % are mapped from milliseconds
- Grid lines must align to actual time intervals

### For MES Domain:
- Gantt shows **execution reality**, not planning
- Planned schedule is **reference context**, not the main visual
- Gaps and delays must be **immediately obvious**
- Color encodes **current state**, position encodes **time**

---

## 🔧 Customization Points

### Time Interval:
Adjust based on duration:
- < 4 hours: 30-minute intervals
- 4-12 hours: 1-hour intervals
- > 12 hours: 2-hour intervals

### Planned Window Display:
- Background region (current implementation)
- Vertical markers at start/end
- Dashed outline behind actual bar

### Real-time Updates:
For running operations, update `currentTime` every minute:
```typescript
useEffect(() => {
  const timer = setInterval(() => {
    setOperations(ops => ops.map(op => 
      op.status === 'Running' 
        ? { ...op, currentTime: new Date().toISOString() }
        : op
    ));
  }, 60000); // 1 minute
  return () => clearInterval(timer);
}, []);
```

---

## 📐 Mathematical Proof

Given:
- Timeline spans `T_start` to `T_end`
- Operation starts at `O_start`, ends at `O_end`

Positioning formula:
```
position(t) = ((t - T_start) / (T_end - T_start)) × 100%
```

Properties:
1. **Linear:** Equal time intervals map to equal pixel distances
2. **Proportional:** 1-hour operation is twice as long as 30-minute operation
3. **Bounded:** All operations fit within [0%, 100%]
4. **Continuous:** No gaps in timeline representation

---

**📅 Last Updated:** 2024-04-15  
**🔖 Version:** 1.0 (Phase 1 - Read-Only)  
**👤 Author:** MES Development Team

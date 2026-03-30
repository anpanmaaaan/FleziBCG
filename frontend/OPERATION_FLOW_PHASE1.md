# 📋 OPERATION FLOW - PHASE 1 (READ-ONLY ANALYSIS)

**Nguyên tắc:** Tất cả "Operation" trong UI Phase 1 đều là **Operation Execution** (runtime).  
UI chỉ **xem – điều hướng – phân tích**, KHÔNG điều khiển.

---

## 🎯 I. KHÁI NIỆM (3 LEVELS)

### 1. Operation Definition (Template/Routing)
- ❌ **KHÔNG dùng** trong UI Phase 1
- Thuộc master data / routing configuration

### 2. Operation Execution (Runtime Instance)
- ✅ **DÙNG** trong tất cả UI Phase 1
- 1 công đoạn đang chạy / đã chạy
- Có status, progress, QC, materials runtime

### 3. Work Order Execution (Aggregate Status)
- ✅ **DÙNG** trong Operation List (đã refactor)
- Tổng hợp trạng thái tất cả operations trong 1 WO

---

## 🔄 II. NAVIGATION FLOW (4 MÀN HÌNH)

```
┌─────────────────────────────────────────────────┐
│  1. Production Orders List                      │
│     (Entry point từ Production module)          │
└────────────────┬────────────────────────────────┘
                 │ Click "View Operations"
                 ▼
┌─────────────────────────────────────────────────┐
│  2. Work Order Execution Status List            │
│     (OperationList.tsx - REFACTORED)            │
│                                                  │
│  - Show WO-level aggregate status               │
│  - Each row = 1 Work Order                      │
│  - CTA: "View" → Navigate to Overview           │
└────────────────┬────────────────────────────────┘
                 │ Click "View"
                 ▼
┌─────────────────────────────────────────────────┐
│  3. Operation Execution Overview (Gantt)        │
│     (OperationDetail.tsx - REFACTORED)          │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │  GANTT CHART - Operation Sequence         │  │
│  │  - Row 1: [10] Material Prep    100% ✓   │  │
│  │  - Row 2: [20] Machining        64%  ⚠   │  │ ← Click bar
│  │  - Row 3: [30] Surface Treat    0%        │  │
│  │  - Row 4: [40] QC Inspection    0%        │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌─────────────┬──────────────────────────────┐ │
│  │  Summary    │  Tabs (Contextual)           │ │
│  │  Panel      │  - Overview                  │ │
│  │             │  - Quality (read-only)       │ │
│  │  Selected:  │  - Materials (read-only)     │ │
│  │  OP-020     │  - Timeline                  │ │
│  │             │  - Documents                 │ │
│  └─────────────┴──────────────────────────────┘ │
└────────────────┬────────────────────────────────┘
                 │ Click "Open in Station Execution"
                 ▼
┌─────────────────────────────────────────────────┐
│  4. Station Execution                           │
│     (StationExecution.tsx - NO CHANGE)          │
│                                                  │
│  - ONLY place to Start/Pause/Complete          │
│  - QC input (enter values)                     │
│  - Material consume                            │
│  - Andon call                                  │
└─────────────────────────────────────────────────┘
```

---

## 📊 III. CHI TIẾT TỪNG MÀN HÌNH

### 🟦 Màn 1: Production Orders List
**File:** `/src/app/pages/ProductionOrderList.tsx`  
**Route:** `/production-orders`

**Không đổi** - màn này vẫn như cũ.

---

### 🟩 Màn 2: Work Order Execution Status List (REFACTORED)
**File:** `/src/app/pages/OperationList.tsx`  
**Route:** `/production-order/:orderId`

#### ✅ Thay đổi:
1. **Đổi khái niệm:**
   - Từ "Operation List" → **"Work Order Execution Status"**
   - Mỗi dòng = 1 Work Order (aggregate status)
   - Không phải list operations chi tiết nữa

2. **Data model:**
   ```typescript
   interface WorkOrderExecution {
     workOrderId: string;
     productName: string;
     productionLine: string;
     status: 'Pending' | 'In Progress' | 'Completed' | 'Late' | 'Blocked';
     overallProgress: number;           // 0-100% (aggregate)
     operationsCount: number;           // Total ops
     completedOperations: number;       // Done ops
     currentOperation?: string;         // Which OP is running
     delayMinutes?: number;             // Delay alert
   }
   ```

3. **UI Components:**
   - ✅ Status icon (✓ ⏱ ⚠)
   - ✅ WO ID (bold, font-mono)
   - ✅ Product name + Line
   - ✅ Operations count (e.g., "2/5 completed")
   - ✅ Current operation indicator
   - ✅ **Slim progress bar** (chỉ là visual, không encode trạng thái)
   - ✅ Delay badge (nếu có)
   - ✅ **Single CTA: "View"** → Navigate to Overview (Gantt)

4. **Loại bỏ:**
   - ❌ Operation-level details
   - ❌ QC / Materials
   - ❌ Timeline
   - ❌ Multiple action buttons (Start/Pause/Complete)

5. **Stats cards:**
   - Total WOs, Completed, In Progress, Pending, Late, Overall Progress

---

### 🟨 Màn 3: Operation Execution Overview (GANTT)
**File:** `/src/app/pages/OperationDetail.tsx`  
**Route:** `/operation/:operationId`

#### ✅ Thay đổi:
1. **Gantt Chart - CORE:**
   - **Full width, prominent position** (ngay sau WO stats)
   - Mỗi row = 1 Operation Execution
   - Columns:
     - Sequence badge (10, 20, 30...)
     - Operation name + status
     - Workstation + Operator
     - **Gantt bar** (planned outline + actual filled)
     - Progress % overlay
     - Timing (On-time/Late/Early)

2. **Gantt Color Spec:**
   ```
   Planned:     gray dashed outline
   Pending:     gray fill (dashed)
   Running:     blue solid
   Completed:   green solid (on-time)
   Late:        orange/red solid + ⚠
   Blocked:     red solid + ⛔
   ```

3. **Interactive:**
   - ✅ **Click bar → select operation**
   - ✅ Selected bar: blue border + blue-50 background
   - ✅ Hover: show tooltip (planned vs actual, delay)
   - ❌ NO drag/resize
   - ❌ NO reschedule
   - ❌ NO action buttons in Gantt

4. **Layout:**
   ```
   ┌─────────────────────────────────────────────┐
   │  Header + Back + "Open in Station Exec"    │
   ├─────────────────────────────────────────────┤
   │  WO-level Stats (4 cards)                  │
   ├─────────────────────────────────────────────┤
   │  GANTT CHART                                │
   │  (Operation Sequence Timeline)              │
   ├──────────┬──────────────────────────────────┤
   │ Summary  │  Tabs (Contextual to selected)  │
   │ Panel    │  - Overview                      │
   │ (Left)   │  - Quality                       │
   │          │  - Materials                     │
   │          │  - Timeline                      │
   │          │  - Documents                     │
   └──────────┴──────────────────────────────────┘
   ```

5. **Left Summary Panel:**
   - Operation ID, Sequence, Name
   - Station / Workcenter
   - Status badge
   - Progress bar
   - Planned vs Actual comparison table
   - Delay alert (if any)
   - Block reason (if blocked)

6. **Tabs - Contextual:**
   - Hiển thị data của **operation được chọn** từ Gantt
   - 5 tabs: Overview, Quality, Materials, Timeline, Documents
   - ❌ Loại bỏ "Execution" tab

7. **Materials Tab - READ ONLY:**
   - ✅ Blue alert banner: "Read-Only View (Phase 1)"
   - ✅ BOM table với Required/Consumed/Remaining
   - ✅ Overuse detection (highlight red)
   - ✅ Lot traceability
   - ❌ NO action buttons (consume, adjust, change lot)

---

### 🟥 Màn 4: Station Execution (NO CHANGE)
**File:** `/src/app/pages/StationExecution.tsx`  
**Route:** `/station-execution`

#### ✅ Vai trò:
- **DUY NHẤT nơi điều khiển execution**
- Start / Pause / Resume / Complete
- QC input (enter measured values)
- Material consume
- Andon call

#### ❌ Các màn khác:
- KHÔNG lặp lại chức năng này
- Chỉ link về đây qua button "Open in Station Execution"

---

## 🎨 IV. COLOR CODING (UNIFIED)

### Status Colors (Operations)
```
Completed (on-time):  green-500
In Progress:          blue-500
Late:                 red-500 / orange-500
Blocked:              red-600
Pending:              gray-400
Paused:               yellow-500
```

### Gantt Bar Colors
```
Planned outline:      border-gray-300 dashed
Actual filled:        bg-{color} based on status
Progress overlay:     white text with mix-blend-difference
```

### Timing Indicators
```
On-time:              text-green-600
Early:                text-blue-600
Late:                 text-red-600
```

---

## 🔑 V. KEY PRINCIPLES (Phase 1)

### ✅ DO:
1. **View và analyze** execution status
2. **Navigate** giữa các màn hình với context rõ ràng
3. **Highlight** delays, blocks, issues
4. **Aggregate** WO-level progress từ operations
5. **Link** to Station Execution khi cần thực thi

### ❌ DON'T:
1. **Control execution** ngoài Station Execution
2. **Duplicate** execution buttons ở nhiều nơi
3. **Mix** Operation Definition với Operation Execution
4. **Allow** material consume/adjust ngoài Station Execution
5. **Show** QC input forms (chỉ show results read-only)

---

## 📐 VI. DATA FLOW

```
┌─────────────────────────────────────────────┐
│  Production Order (PO-001)                  │
└────────────────┬────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌───────▼──────┐
│ WO-2024-001  │  │ WO-2024-002  │
└───────┬──────┘  └──────────────┘
        │
   ┌────┴────┬────┬────┐
   │         │    │    │
┌──▼──┐  ┌──▼──┐ ┌▼─┐ ┌▼─┐
│OP-10│  │OP-20│ │30│ │40│
└─────┘  └─────┘ └──┘ └──┘
```

- 1 PO có nhiều WO
- 1 WO có nhiều Operation Executions (theo sequence)
- UI hiển thị từ top-down: PO → WO → OP

---

## 🚀 VII. PHÁT TRIỂN TIẾP THEO (Phase 2+)

### Phase 2: Interactive Gantt
- Drag & drop to reschedule
- Add/remove operations dynamically
- Capacity planning overlay
- Resource allocation

### Phase 3: Execution Control
- Start/Pause/Complete từ Gantt
- Quick QC input modal
- Material consume quick action

### Phase 4: Advanced Analytics
- Bottleneck detection AI
- Predictive delay alerts
- Optimal scheduling suggestions

---

## 📝 VIII. CHECKLIST FOR DEVELOPERS

### Khi làm việc với Operation UI:
- [ ] Đã phân biệt rõ Operation Definition vs Execution?
- [ ] UI chỉ đọc (Phase 1) hay có quyền sửa?
- [ ] Navigation flow đúng: WO List → Overview → Detail → Station Exec?
- [ ] Gantt bar color đúng spec?
- [ ] Materials tab có banner "Read-Only"?
- [ ] Không có execution buttons ngoài Station Execution?
- [ ] Progress bar chỉ là visual, không encode logic?
- [ ] Comments trong code ghi rõ "Operation Execution" thay vì "Operation"?

---

## 🎯 IX. SUMMARY

| Màn hình | Vai trò | Level | Actions |
|----------|---------|-------|---------|
| WO Execution Status List | Aggregate WO status | WO-level | View (navigate to Overview) |
| Operation Execution Overview | Gantt timeline | OP-level (sequence) | Click bar (select OP) |
| Operation Execution Detail | Deep dive 1 OP | OP-level (single) | Read-only tabs, Link to Station Exec |
| Station Execution | Control execution | OP-level (runtime) | Start/Pause/Complete, QC input, Material consume |

**Mỗi màn 1 vai – 1 nhiệm vụ – không chồng chéo!**

---

**📅 Last Updated:** 2024-04-15  
**🔖 Version:** Phase 1 (Read-Only Analysis)  
**👤 Maintained by:** MES Development Team

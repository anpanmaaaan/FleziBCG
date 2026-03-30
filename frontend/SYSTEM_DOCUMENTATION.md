# 📘 MES LITE - UNIVERSAL MANUFACTURING EDITION
## TÀI LIỆU HỆ THỐNG CHI TIẾT

**Phiên bản:** 1.0  
**Ngày cập nhật:** 27/03/2026  
**Tác giả:** MES Development Team

---

# 📑 MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Cấu trúc dữ liệu](#3-cấu-trúc-dữ-liệu)
4. [Chức năng theo Module](#4-chức-năng-theo-module)
5. [Navigation Flow](#5-navigation-flow)
6. [API Endpoints](#6-api-endpoints)
7. [Hướng dẫn sử dụng](#7-hướng-dẫn-sử-dụng)

---

# 1. TỔNG QUAN HỆ THỐNG

## 1.1. Giới thiệu

**MES Lite - Universal Manufacturing Edition** là hệ thống quản lý sản xuất (Manufacturing Execution System) được thiết kế cho mọi ngành sản xuất rời rạc (discrete manufacturing), đặc biệt phù hợp với:

- ✅ Sản xuất linh kiện ô tô (Automotive Parts)
- ✅ Lắp ráp điện tử (Electronics Assembly)
- ✅ Cơ khí chế tạo (Mechanical Manufacturing)
- ✅ Sản xuất thiết bị (Equipment Manufacturing)

## 1.2. Mục đích

Hệ thống cung cấp các chức năng cốt lõi:

1. **Production Planning** - Lập kế hoạch sản xuất (PO/WO)
2. **Routing & Operations** - Định tuyến và trình tự công đoạn
3. **Dispatch Management** - Điều phối lệnh sản xuất
4. **Execution Tracking** - Theo dõi thực thi real-time
5. **Quality Management** - Quản lý chất lượng (QC/Defects)
6. **Traceability** - Truy xuất nguồn gốc (Genealogy)
7. **APS Scheduling** - Lập lịch sản xuất thông minh
8. **Dashboard & Analytics** - Báo cáo và phân tích (OEE, KPI)

## 1.3. Người dùng (Actors)

| Vai trò | Mô tả | Chức năng chính |
|---------|-------|-----------------|
| **Line Operator** | Công nhân sản xuất | Thực hiện công việc tại station, nhập kết quả |
| **Supervisor** | Giám sát viên | Theo dõi tiến độ, xử lý defect, xem KPI |
| **Planner** | Kế hoạch viên | Tạo Production Order, routing, scheduling |
| **Quality Inspector** | Thanh tra chất lượng | QC checkpoint, ghi nhận defect |
| **System Admin** | Quản trị hệ thống | Cấu hình system, user, master data |

## 1.4. Đặc điểm nổi bật

- 🚀 **Real-time tracking** - Theo dõi sản xuất thời gian thực
- 📊 **OEE Deep Dive** - Phân tích hiệu suất thiết bị chi tiết
- 🔍 **Full traceability** - Truy xuất nguồn gốc hoàn chỉnh
- 🎯 **ISA-95 compliant** - Tuân thủ chuẩn ISA-95 (Line → Stations)
- 💡 **Universal design** - Không giới hạn ngành sản xuất cụ thể
- 🎨 **Modern UI** - Giao diện hiện đại với Tailwind CSS v4

---

# 2. KIẾN TRÚC HỆ THỐNG

## 2.1. Technology Stack

### Frontend
```
- Framework: React 18.3.1 + TypeScript
- Routing: React Router 7.13.0 (Data Mode)
- Styling: Tailwind CSS v4
- UI Components: Radix UI, shadcn/ui
- Charts: Recharts 2.15.2
- Icons: Lucide React
- Visualization: React Flow (Genealogy tree)
- State: React Hooks (local state)
```

### Backend
```
- Runtime: Deno (Edge Functions)
- Framework: Hono (Web Server)
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth
- Storage: Supabase Storage (optional)
```

## 2.2. Architecture Pattern

**Three-tier Architecture:**

```
┌─────────────────────────────────────────────┐
│         FRONTEND (React + TS)               │
│   - Pages (UI Components)                   │
│   - Components (Reusable)                   │
│   - Routes (Navigation)                     │
│   - Mock Data (Development)                 │
└──────────────────┬──────────────────────────┘
                   │
                   │ HTTP/REST + Supabase Client
                   │
┌──────────────────▼──────────────────────────┐
│      SERVER (Supabase Edge Function)        │
│   - Hono Web Server                         │
│   - Business Logic                          │
│   - API Endpoints                           │
│   - Auth Middleware                         │
└──────────────────┬──────────────────────────┘
                   │
                   │ SQL + Supabase JS Client
                   │
┌──────────────────▼──────────────────────────┐
│       DATABASE (Supabase PostgreSQL)        │
│   - Production Orders                       │
│   - Routes & Operations                     │
│   - Execution Records                       │
│   - Quality & Defects                       │
│   - Materials & Traceability                │
└─────────────────────────────────────────────┘
```

## 2.3. Folder Structure

```
/
├── src/
│   ├── app/
│   │   ├── components/          # Reusable components
│   │   │   ├── Layout.tsx       # Main layout + sidebar
│   │   │   ├── TopBar.tsx       # Top navigation bar
│   │   │   ├── PageHeader.tsx   # Page header component
│   │   │   ├── StatsCard.tsx    # Statistics card
│   │   │   ├── StatusBadge.tsx  # Status badge
│   │   │   └── ui/              # shadcn/ui components
│   │   ├── pages/               # Page components
│   │   │   ├── Home.tsx         # Execution Tracking
│   │   │   ├── Dashboard.tsx    # Main dashboard
│   │   │   ├── OEEDeepDive.tsx  # OEE analytics
│   │   │   ├── ProductionOrderList.tsx
│   │   │   ├── DispatchQueue.tsx
│   │   │   ├── RouteList.tsx
│   │   │   ├── RouteDetail.tsx
│   │   │   ├── OperationList.tsx
│   │   │   ├── OperationDetail.tsx
│   │   │   ├── StationExecution.tsx
│   │   │   ├── QCCheckpoints.tsx
│   │   │   ├── DefectManagement.tsx
│   │   │   ├── Traceability.tsx
│   │   │   └── APSScheduling.tsx
│   │   ├── data/
│   │   │   ├── mockData.ts      # Mock production data
│   │   │   └── oee-mock-data.ts # Mock OEE data
│   │   ├── routes.ts            # Route configuration
│   │   └── App.tsx              # Main app entry
│   ├── types/
│   │   └── database.ts          # TypeScript types
│   ├── utils/
│   │   └── supabase.ts          # Supabase client
│   ├── examples/
│   │   └── SupabaseExample.tsx  # Integration example
│   └── styles/
│       ├── index.css            # Main styles
│       ├── tailwind.css         # Tailwind config
│       ├── theme.css            # Design tokens
│       └── fonts.css            # Font imports
├── supabase/
│   └── functions/
│       └── server/
│           ├── index.tsx        # API server
│           ├── db.tsx           # Database operations
│           └── kv_store.tsx     # Key-value store
├── utils/
│   └── supabase/
│       └── info.tsx             # Supabase config
└── package.json
```

## 2.4. ISA-95 Model

Hệ thống tuân thủ chuẩn ISA-95 Level 3 (MES):

```
Enterprise (ERP) - Level 4
        ↓
   MES Lite - Level 3
        ↓
┌────────────────────┐
│       SITE         │
└────────┬───────────┘
         │
    ┌────▼─────┐
    │  AREA    │
    └────┬─────┘
         │
    ┌────▼──────────┐
    │  LINE         │ ← Production Line (DL2, BLK1, BLK2...)
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │  STATION      │ ← Work Center (3000, 2000...)
    └───────────────┘
```

---

# 3. CẤU TRÚC DỮ LIỆU

## 3.1. Data Models (TypeScript Interfaces)

### 3.1.1. ProductionOrder

**Mô tả:** Lệnh sản xuất - đơn vị kế hoạch chính

```typescript
interface ProductionOrder {
  id: string;                    // Mã PO (e.g., "PO-001")
  serialNumber: string;          // Serial number sản phẩm
  lotId?: string;                // Mã lô (optional)
  routeId: string;               // Route ID (DMES-R11, DMES-R8...)
  machineNumber?: string;        // Mã máy (optional)
  quantity: number;              // Số lượng cần sản xuất
  
  // Dates
  plannedCompletionDate: string; // Ngày dự kiến hoàn thành
  releasedDate: string;          // Ngày phát hành
  releaseDate: string;           // Ngày release
  plannedStartDate?: string;     // Ngày dự kiến bắt đầu
  actualStartDate?: string;      // Ngày thực tế bắt đầu
  actualCompletionDate?: string; // Ngày thực tế hoàn thành
  
  // Status & Progress
  status: 'IN_PROGRESS' | 'COMPLETED' | 'PENDING' | 'LATE';
  progress: number;              // 0-100%
  
  // Additional info
  line?: string;                 // Production line
  customer?: string;             // Khách hàng
  priority?: 'High' | 'Medium' | 'Low';
  assignee?: string;             // Người phụ trách
  department?: string;           // Phòng ban
  productName?: string;          // Tên sản phẩm
  materialCode?: string;         // Mã nguyên vật liệu
}
```

**Ví dụ:**
```json
{
  "id": "1",
  "serialNumber": "01082024",
  "routeId": "DMES-R11",
  "quantity": 100,
  "plannedCompletionDate": "10/04/2024",
  "releasedDate": "10/04/2024",
  "status": "IN_PROGRESS",
  "progress": 45,
  "priority": "High",
  "productName": "Widget A"
}
```

---

### 3.1.2. Route

**Mô tả:** Routing - định nghĩa quy trình sản xuất

```typescript
interface Route {
  id: string;              // Route ID (e.g., "DMES-R11")
  name: string;            // Tên route
  version: string;         // Phiên bản
  product_id?: string;     // Sản phẩm áp dụng
  status: 'Active' | 'Inactive' | 'Draft';
  description?: string;    // Mô tả
  created_at?: string;
  updated_at?: string;
}
```

**Ví dụ:**
```json
{
  "id": "DMES-R11",
  "name": "Assembly Route V1",
  "version": "1.0",
  "status": "Active",
  "description": "Standard assembly process for Widget A"
}
```

---

### 3.1.3. Operation

**Mô tả:** Công đoạn - một bước trong routing

```typescript
interface Operation {
  id: string;                    // Operation ID (e.g., "OP_110000")
  route_id: string;              // Thuộc route nào
  sequence: number;              // Thứ tự (10, 20, 30...)
  name: string;                  // Tên operation
  station_id: string;            // Station thực hiện
  station_name: string;          // Tên station
  cycle_time?: number;           // Thời gian chu kỳ (seconds)
  status: 'Pending' | 'In Progress' | 'Completed' | 'Blocked' | 'Skipped';
  notes?: string;
  created_at?: string;
  updated_at?: string;
}
```

**Ví dụ:**
```json
{
  "id": "OP_110000",
  "route_id": "DMES-R11",
  "sequence": 10,
  "name": "Assembly Front Panel",
  "station_id": "3000",
  "station_name": "Assembly Station 1",
  "cycle_time": 120,
  "status": "In Progress"
}
```

---

### 3.1.4. Station

**Mô tả:** Trạm làm việc - nơi thực hiện operation

```typescript
interface Station {
  id: string;              // Station ID (e.g., "3000")
  name: string;            // Tên station
  line_id: string;         // Thuộc line nào (DL2, BLK1...)
  line_name: string;       // Tên line
  type?: string;           // Loại station
  status: 'Available' | 'Occupied' | 'Maintenance' | 'Offline';
  created_at?: string;
  updated_at?: string;
}
```

---

### 3.1.5. ExecutionRecord

**Mô tả:** Bản ghi thực thi - tracking công việc operator

```typescript
interface ExecutionRecord {
  id: string;
  production_order_id: string;   // PO đang thực hiện
  operation_id: string;          // Operation đang làm
  station_id: string;            // Tại station nào
  operator_id?: string;          // Operator ID
  operator_name?: string;        // Tên operator
  status: 'Started' | 'Paused' | 'Completed' | 'Failed';
  start_time?: string;           // Thời gian bắt đầu
  end_time?: string;             // Thời gian kết thúc
  quantity_completed?: number;   // Số lượng hoàn thành
  quantity_rejected?: number;    // Số lượng bị reject
  notes?: string;
  created_at?: string;
  updated_at?: string;
}
```

---

### 3.1.6. QualityCheckpoint & QualityResult

**Mô tả:** Điểm kiểm tra chất lượng và kết quả

```typescript
interface QualityCheckpoint {
  id: string;
  operation_id: string;          // Thuộc operation nào
  checkpoint_name: string;       // Tên checkpoint
  checkpoint_type: 'Dimensional' | 'Visual' | 'Functional' | 'Other';
  specification?: string;        // Tiêu chuẩn
  is_mandatory: boolean;         // Bắt buộc hay không
}

interface QualityResult {
  id: string;
  execution_record_id: string;   // Thuộc execution nào
  checkpoint_id: string;         // Checkpoint nào
  result: 'Pass' | 'Fail' | 'NA';
  measured_value?: string;       // Giá trị đo được
  inspector_id?: string;         // Người kiểm tra
  inspector_name?: string;
  timestamp?: string;
  notes?: string;
}
```

---

### 3.1.7. Defect

**Mô tả:** Lỗi sản xuất

```typescript
interface Defect {
  id: string;
  production_order_id?: string;
  operation_id?: string;
  defect_code: string;           // Mã lỗi
  defect_name: string;           // Tên lỗi
  category?: string;             // Loại lỗi
  severity: 'Critical' | 'Major' | 'Minor';
  quantity: number;              // Số lượng lỗi
  detected_by?: string;          // Người phát hiện
  detected_at?: string;          // Thời gian phát hiện
  status: 'Open' | 'In Review' | 'Resolved' | 'Closed';
  resolution?: string;           // Cách giải quyết
  notes?: string;
}
```

---

### 3.1.8. Material & MaterialConsumption

**Mô tả:** Nguyên vật liệu và tiêu hao

```typescript
interface Material {
  id: string;
  material_code: string;         // Mã NVL
  material_name: string;         // Tên NVL
  material_type?: string;        // Loại
  unit_of_measure?: string;      // Đơn vị (kg, pcs, m...)
  current_stock?: number;        // Tồn kho hiện tại
  min_stock?: number;            // Tồn kho tối thiểu
  max_stock?: number;            // Tồn kho tối đa
}

interface MaterialConsumption {
  id: string;
  execution_record_id: string;   // Execution nào tiêu hao
  material_id: string;           // NVL nào
  quantity_used: number;         // Số lượng dùng
  lot_number?: string;           // Lot number
  consumed_at?: string;          // Thời gian
}
```

---

## 3.2. Mock Data Structure

Hiện tại hệ thống sử dụng **mock data** cho development trong file `/src/app/data/mockData.ts`:

### Production Orders (11 items)
```typescript
export const productionOrders: ProductionOrder[] = [
  { id: '1', serialNumber: '01082024', routeId: 'DMES-R11', ... },
  { id: '2', serialNumber: '01_16102024_BLK2', routeId: 'DMES-R11', ... },
  ...
]
```

### Production Lines (6 lines)
```typescript
export const productionLines: ProductionLine[] = [
  { id: 'DL2', name: 'DL2', shift: '1/2', lateStatus: 'Late', orders: [...] },
  { id: 'BLK1', name: 'BLK1', shift: '1/2', orders: [...] },
  ...
]
```

### Operations (3 items)
```typescript
export const operations: Operation[] = [
  { id: 'OP_110000', productionOrderId: 'P02-BLK1', workstation: '3000', ... },
  ...
]
```

### Routes (4 items)
```typescript
export const routes: Route[] = [
  { id: 'HAL-X002', name: 'HAL-X002', status: 'Active', ... },
  { id: 'DMES-R4', name: 'DMES-R4', status: 'Inactive', ... },
  ...
]
```

---

# 4. CHỨC NĂNG THEO MODULE

## 4.1. 📊 Dashboard Module

**File:** `/src/app/pages/Dashboard.tsx`  
**Route:** `/dashboard`

### Chức năng:
- ✅ Hiển thị KPI tổng quan (Production volume, OEE, Quality rate)
- ✅ Chart xu hướng sản xuất
- ✅ Top defects
- ✅ Alert và notifications
- ⏳ Real-time updates (TODO)

### Components sử dụng:
- `StatsCard` - Hiển thị metrics
- `recharts` - Visualization

---

## 4.2. 📈 Performance Analytics Module

### 4.2.1. OEE Deep Dive

**File:** `/src/app/pages/OEEDeepDive.tsx`  
**Route:** `/performance/oee-deep-dive`

### Chức năng:
- ✅ **OEE Analysis** - Overall Equipment Effectiveness
  - Availability (Khả dụng)
  - Performance (Hiệu suất)
  - Quality (Chất lượng)
  
- ✅ **Loss Analysis** - Phân tích mất mát
  - Downtime losses (Dừng máy)
  - Speed losses (Giảm tốc)
  - Quality losses (Lỗi chất lượng)
  
- ✅ **Trend Charts** - Biểu đồ xu hướng
  - Daily/Weekly/Monthly trends
  - Line comparison
  - Target vs Actual
  
- ✅ **Pareto Analysis** - 80/20 rule
  - Top loss contributors
  - Focus areas

### Data structure:
```typescript
// OEE Metrics
{
  availability: 85.2,    // %
  performance: 92.4,     // %
  quality: 97.8,         // %
  oee: 77.0,            // % (A × P × Q)
  targetOEE: 85.0
}

// Loss categories
{
  plannedDowntime: 120,  // minutes
  unplannedDowntime: 45,
  speedLoss: 30,
  qualityLoss: 15
}
```

---

## 4.3. 🏭 Production Management Module

### 4.3.1. Production Order List

**File:** `/src/app/pages/ProductionOrderList.tsx`  
**Route:** `/production-orders`

### Chức năng:
- ✅ **List tất cả Production Orders**
  - Filterable table
  - Search by serial number, route
  - Sort by date, status, priority
  
- ✅ **Column customization**
  - Show/hide columns
  - Reorder columns (TODO)
  
- ✅ **Add new Production Order**
  - Dialog form
  - Validation
  
- ✅ **View details**
  - Click to navigate to Operation List

### Table columns:
| Column | Description | Type |
|--------|-------------|------|
| Serial Number | Số serial sản phẩm | text |
| Route ID | Routing áp dụng | text |
| Quantity | Số lượng | number |
| Status | Trạng thái | badge |
| Progress | % hoàn thành | progress bar |
| Released Date | Ngày phát hành | date |
| Planned Completion | Ngày dự kiến hoàn thành | date |

### Actions:
- ➕ Add Production Order
- 👁️ View Operations
- 🔍 Search & Filter
- ⚙️ Manage Columns

---

### 4.3.2. Dispatch Queue

**File:** `/src/app/pages/DispatchQueue.tsx`  
**Route:** `/dispatch`

### Chức năng:
- ✅ **Queue Management** - Quản lý hàng đợi
  - Pending orders
  - Priority sorting
  - Dispatch to lines
  
- ✅ **Drag & Drop** - Sắp xếp ưu tiên
  - Reorder queue
  - Assign to lines
  
- ⏳ **Real-time status** (TODO)
  - Line availability
  - Capacity planning

---

### 4.3.3. Execution Tracking (Home)

**File:** `/src/app/pages/Home.tsx`  
**Route:** `/` (default)

### Chức năng:
- ✅ **Real-time production tracking**
  - Production lines status
  - Active orders per line
  - Order cards with progress
  
- ✅ **Line-based view**
  - DL2, BLK1, BLK2, BLK3, DL3, DL4
  - Shift information
  - Late status indicators
  
- ✅ **Order cards**
  - Order ID
  - Quantity
  - Progress bar
  - Status badge (Late, On Time, Completed)
  - Workers count
  
- ✅ **Queue section**
  - Pending orders
  - Release dates

### Layout:
```
┌────────────────────────────────────┐
│  Production Lines Status           │
├────────────────────────────────────┤
│  Line: DL2        Shift: 1/2       │
│  ┌──────────┐  ┌──────────┐       │
│  │ PO4DL2   │  │ PO3DL2   │       │
│  │ 51000    │  │ 52000    │       │
│  │ ▓▓▓░░░░  │  │ ░░░░░░░  │       │
│  │ Late     │  │ Late     │       │
│  └──────────┘  └──────────┘       │
├────────────────────────────────────┤
│  Queue                             │
│  - P02-BLK1                        │
│  - PO03-BLK2                       │
└────────────────────────────────────┘
```

---

### 4.3.4. Station Execution

**File:** `/src/app/pages/StationExecution.tsx`  
**Route:** `/station-execution`

### Chức năng:
- ✅ **Operator interface** - Giao diện cho công nhân
  - Select station
  - Select production order
  - Select operation
  
- ✅ **Execution controls**
  - Start work
  - Pause work
  - Complete work
  - Report defects
  
- ✅ **Input tracking**
  - Quantity completed
  - Quantity rejected
  - Time tracking
  - Notes
  
- ✅ **QC integration**
  - Mandatory checkpoints
  - Pass/Fail results
  - Inspector signature

### Workflow:
```
1. Select Station → 2. Scan/Select PO → 3. Select Operation
              ↓
4. Start Work → 5. Perform Tasks → 6. QC Check
              ↓
7. Complete → 8. Submit Results
```

---

## 4.4. 🛣️ Routes & Operations Module

### 4.4.1. Route List

**File:** `/src/app/pages/RouteList.tsx`  
**Route:** `/routes`

### Chức năng:
- ✅ **List all routes**
  - Active/Inactive status
  - Last updated date
  - Quick search
  
- ✅ **Route details**
  - Click to view operations
  
- ⏳ **Version management** (TODO)
  - Create new version
  - Compare versions

---

### 4.4.2. Route Detail

**File:** `/src/app/pages/RouteDetail.tsx`  
**Route:** `/routes/:routeId`

### Chức năng:
- ✅ **Operation sequence editor**
  - List operations in order
  - Sequence numbers (10, 20, 30...)
  - Station assignments
  
- ✅ **Operation details**
  - Name, type
  - Cycle time
  - Work center
  - QC requirements
  
- ⏳ **Drag & Drop reorder** (TODO)
- ⏳ **Add/Edit/Delete operations** (TODO)

---

### 4.4.3. Operation List

**File:** `/src/app/pages/OperationList.tsx`  
**Route:** `/production-order/:orderId`

### Chức năng:
- ✅ **Operations for specific PO**
  - Filtered by production order
  - Execution status
  - Progress tracking
  
- ✅ **Breadcrumb navigation**
  - Production Orders → Operation List
  
- ✅ **Click to operation detail**
  - Deep dive into single operation

---

### 4.4.4. Operation Detail

**File:** `/src/app/pages/OperationDetail.tsx`  
**Route:** `/operation/:operationId`

### Chức năng comprehensive với **6 tabs:**

#### Tab 1: Overview
- Operation info (ID, name, status, progress)
- Timeline (planned vs actual)
- Current execution status

#### Tab 2: Execution History
- All execution records
- Operator names
- Start/End times
- Quantity completed/rejected
- Timeline view

#### Tab 3: Quality Checkpoints
- QC checkpoint list
- Mandatory checkpoints highlighted
- Pass/Fail status
- Inspector information
- Trend analysis

#### Tab 4: Defects
- Defects found in this operation
- Defect codes & categories
- Severity levels
- Resolution status
- Pareto chart

#### Tab 5: Materials
- Material consumption
- Lot tracking
- Quantity used
- Material availability

#### Tab 6: Documentation
- Work instructions
- Safety guidelines
- Technical drawings
- Videos/Photos

### Navigation flow:
```
Home → Production Order → Operation List → Operation Detail
                              ↑                    ↓
                              └────────────────────┘
                              (Breadcrumb back)
```

---

## 4.5. ✅ Quality Management Module

### 4.5.1. QC Checkpoints

**File:** `/src/app/pages/QCCheckpoints.tsx`  
**Route:** `/quality`

### Chức năng:
- ✅ **Checkpoint configuration**
  - Define checkpoints
  - Link to operations
  - Set specifications
  
- ✅ **Checkpoint types**
  - Dimensional (Kích thước)
  - Visual (Trực quan)
  - Functional (Chức năng)
  - Other
  
- ✅ **Mandatory flag**
  - Must-pass checkpoints
  - Optional checkpoints

---

### 4.5.2. Defect Management

**File:** `/src/app/pages/DefectManagement.tsx`  
**Route:** `/defects`

### Chức năng:
- ✅ **Defect tracking**
  - All defects list
  - Filter by status, severity
  - Search by code, name
  
- ✅ **Defect details**
  - Defect code
  - Category
  - Severity (Critical, Major, Minor)
  - Quantity
  - Detected by/at
  
- ✅ **Status workflow**
  - Open → In Review → Resolved → Closed
  
- ✅ **Analytics**
  - Top defects (Pareto)
  - Trend by time
  - By line/station/operator

---

## 4.6. 🔍 Traceability Module

**File:** `/src/app/pages/Traceability.tsx`  
**Route:** `/traceability`

### Chức năng:
- ✅ **Genealogy tree** - Truy xuất nguồn gốc
  - Forward traceability (Sản phẩm → Nguyên liệu nào)
  - Backward traceability (Nguyên liệu → Sản phẩm nào)
  
- ✅ **Visualization**
  - React Flow diagram
  - Parent-child relationships
  - Material lot numbers
  
- ✅ **Search**
  - By product serial
  - By material lot
  - By production order
  
- ⏳ **Full lineage** (TODO)
  - Multi-level BOM
  - Assembly relationships

---

## 4.7. 📅 APS Scheduling Module

**File:** `/src/app/pages/APSScheduling.tsx`  
**Route:** `/scheduling`

### Chức năng:
- ✅ **Gantt chart** - Lịch sản xuất
  - Timeline view
  - Line-based rows
  - Order bars
  
- ✅ **Scheduling algorithms**
  - FIFO (First In First Out)
  - EDD (Earliest Due Date)
  - SPT (Shortest Processing Time)
  
- ✅ **Drag & Drop**
  - Reschedule orders
  - Change line assignments
  
- ✅ **Capacity planning**
  - Line capacity
  - Available hours
  - Utilization %
  
- ⏳ **Constraint-based scheduling** (TODO)
  - Material availability
  - Tool availability
  - Skill requirements

---

# 5. NAVIGATION FLOW

## 5.1. Sidebar Menu Structure

```
📊 Dashboard
   └─ Dashboard

📈 Performance
   ├─ OEE Deep Dive ✅ (100%)

🏭 Production
   ├─ Production Orders ✅ (75%)
   ├─ Dispatch Queue ✅ (80%)
   ├─ Execution Tracking ✅ (100%)
   └─ Station Execution ✅ (100%)

🛣️ Routes & Operations
   ├─ Route List ✅ (85%)
   └─ Operation List ✅ (100%)

✅ Quality
   ├─ QC Checkpoints ✅ (85%)
   ├─ Defect Management ✅ (85%)
   └─ Traceability ✅ (75%)

📅 APS Scheduling ✅ (90%)

⚙️ Settings
```

## 5.2. User Journey Examples

### Journey 1: Create và Track Production Order
```
1. Vào Production Orders
2. Click "Add Production Order"
3. Fill form (serial, route, quantity...)
4. Submit
5. View trong list
6. Click order → View Operations
7. Click operation → View detail với 6 tabs
8. Monitor progress real-time
```

### Journey 2: Operator thực hiện công việc
```
1. Vào Station Execution
2. Select station (e.g., "3000")
3. Scan/Select Production Order
4. Select Operation to perform
5. Click "Start Work"
6. Perform tasks
7. Complete QC checkpoints
8. Enter quantity completed
9. Click "Complete Work"
10. System records execution
```

### Journey 3: Quality Inspector kiểm tra
```
1. Vào QC Checkpoints
2. View pending checkpoints
3. Select checkpoint
4. Perform inspection
5. Enter measured value
6. Mark Pass/Fail
7. Add notes
8. Submit result
9. If Fail → Create defect
10. Vào Defect Management → Track resolution
```

### Journey 4: Supervisor phân tích OEE
```
1. Vào Performance → OEE Deep Dive
2. Select date range
3. View OEE breakdown (A × P × Q)
4. Analyze loss categories
5. Check Pareto chart (top losses)
6. Drill down to specific line
7. View trend charts
8. Identify improvement opportunities
9. Export report
```

---

# 6. API ENDPOINTS

## 6.1. Server Base URL

```
https://ftyrfhfjvowcqsxsjtlq.supabase.co/functions/v1/make-server-380ff3c6
```

## 6.2. Endpoints List

### Production Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/production-orders` | Lấy tất cả PO |
| GET | `/production-orders/:id` | Lấy PO theo ID |
| POST | `/production-orders` | Tạo PO mới |
| PUT | `/production-orders/:id` | Cập nhật PO |
| DELETE | `/production-orders/:id` | Xóa PO |

**Example Request:**
```javascript
// GET all production orders
const response = await callServer('/production-orders');

// POST create new
const response = await callServer('/production-orders', {
  method: 'POST',
  body: JSON.stringify({
    id: 'PO-001',
    product_id: 'PROD-001',
    quantity: 100,
    route_id: 'ROUTE-001',
    priority: 'High',
    status: 'Planned'
  })
});
```

---

### Routes & Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/routes` | Lấy tất cả routes |
| GET | `/routes/:id` | Lấy route theo ID |
| GET | `/routes/:id/operations` | Lấy operations của route |

---

### Stations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stations` | Lấy tất cả stations |
| GET | `/stations/:id` | Lấy station theo ID |

---

### Execution

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/execution/start` | Bắt đầu thực thi |
| POST | `/execution/complete` | Hoàn thành thực thi |
| GET | `/execution/station/:stationId` | Lấy execution theo station |

**Example:**
```javascript
// Start execution
const response = await callServer('/execution/start', {
  method: 'POST',
  body: JSON.stringify({
    id: 'EXE-001',
    production_order_id: 'PO-001',
    operation_id: 'OP-110000',
    station_id: '3000',
    operator_id: 'OPR-001',
    operator_name: 'John Doe'
  })
});

// Complete execution
const response = await callServer('/execution/complete', {
  method: 'POST',
  body: JSON.stringify({
    execution_id: 'EXE-001',
    quantity_completed: 50,
    quantity_rejected: 2,
    notes: 'Completed successfully'
  })
});
```

---

### Quality

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/quality/result` | Submit QC result |
| GET | `/quality/execution/:executionId` | Lấy QC results |

---

### Defects

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/defects` | Tạo defect mới |
| GET | `/defects` | Lấy tất cả defects |

---

### KV Store (Optional)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/kv/:key` | Lấy value từ KV store |
| POST | `/kv/:key` | Set value vào KV store |

---

## 6.3. Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message here"
}
```

---

# 7. HƯỚNG DẪN SỬ DỤNG

## 7.1. Setup & Installation

### Prerequisites
- Node.js 18+
- pnpm (hoặc npm/yarn)
- Supabase account

### Steps

1. **Clone repository**
```bash
git clone <repo-url>
cd mes-lite
```

2. **Install dependencies**
```bash
pnpm install
```

3. **Configure Supabase**
- File đã có: `/utils/supabase/info.tsx`
- Project ID: `ftyrfhfjvowcqsxsjtlq`
- Keys đã configured

4. **Run development server**
```bash
pnpm dev
```

5. **Access application**
```
http://localhost:5173
```

---

## 7.2. Connecting to Database

### Option 1: Using Supabase Client (Direct)

```typescript
import { supabase } from '/src/utils/supabase';

// Query
const { data, error } = await supabase
  .from('production_orders')
  .select('*')
  .order('created_at', { ascending: false });
```

### Option 2: Using Server API (Recommended)

```typescript
import { callServer } from '/src/utils/supabase';

// GET
const response = await callServer('/production-orders');

// POST
const response = await callServer('/production-orders', {
  method: 'POST',
  body: JSON.stringify({ ... })
});
```

---

## 7.3. Creating New Features

### Step 1: Define TypeScript types
```typescript
// In /src/types/database.ts
export interface MyNewEntity {
  id: string;
  name: string;
  // ...
}
```

### Step 2: Create database table
```sql
-- In Supabase SQL Editor
CREATE TABLE my_new_entity (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Step 3: Add server endpoints
```typescript
// In /supabase/functions/server/db.tsx
export async function getAllMyEntities() {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('my_new_entity')
    .select('*');
  if (error) throw new Error(error.message);
  return data;
}
```

```typescript
// In /supabase/functions/server/index.tsx
app.get("/make-server-380ff3c6/my-entities", async (c) => {
  try {
    const data = await db.getAllMyEntities();
    return c.json({ success: true, data });
  } catch (error) {
    return c.json({ success: false, error: error.message }, 500);
  }
});
```

### Step 4: Create React page
```typescript
// In /src/app/pages/MyNewPage.tsx
import { useEffect, useState } from 'react';
import { callServer } from '/src/utils/supabase';

export function MyNewPage() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    async function fetchData() {
      const response = await callServer('/my-entities');
      if (response.success) {
        setData(response.data);
      }
    }
    fetchData();
  }, []);
  
  return (
    <div>
      {/* Your UI here */}
    </div>
  );
}
```

### Step 5: Add route
```typescript
// In /src/app/routes.ts
import { MyNewPage } from "./pages/MyNewPage";

// Add to children array:
{ path: "my-new-page", Component: MyNewPage }
```

### Step 6: Add to sidebar
```typescript
// In /src/app/components/Layout.tsx
<Link to="/my-new-page" ...>
  My New Page
</Link>
```

---

## 7.4. Best Practices

### Code Organization
- ✅ One component per file
- ✅ Reusable components in `/components`
- ✅ Page components in `/pages`
- ✅ Types in `/types`
- ✅ Mock data in `/data`

### Naming Conventions
- ✅ PascalCase for components: `ProductionOrderList.tsx`
- ✅ camelCase for functions: `getAllProductionOrders()`
- ✅ UPPER_CASE for constants: `API_BASE_URL`
- ✅ kebab-case for routes: `/production-orders`

### State Management
- ✅ Use React Hooks (useState, useEffect)
- ✅ Local state for UI
- ✅ Server state via Supabase
- ⏳ Global state with Context API (if needed)

### Error Handling
```typescript
try {
  const response = await callServer('/endpoint');
  if (response.success) {
    // Handle success
  } else {
    console.error('Error:', response.error);
  }
} catch (error) {
  console.error('Network error:', error);
}
```

### Loading States
```typescript
const [loading, setLoading] = useState(true);

useEffect(() => {
  async function fetch() {
    setLoading(true);
    try {
      const data = await callServer('/endpoint');
      // Process data
    } finally {
      setLoading(false);
    }
  }
  fetch();
}, []);

if (loading) return <div>Loading...</div>;
```

---

## 7.5. Troubleshooting

### Issue: Cannot connect to Supabase
**Solution:**
- Check `/utils/supabase/info.tsx` có đúng credentials
- Verify network connection
- Check Supabase dashboard cho service status

### Issue: Mock data not showing
**Solution:**
- Check import paths
- Verify data structure matches interface
- Console.log to debug

### Issue: Route not working
**Solution:**
- Check `/src/app/routes.ts` có route được define
- Verify component import
- Check URL spelling

### Issue: API endpoint returns 500
**Solution:**
- Check server logs in Supabase Edge Functions
- Verify database table exists
- Check SQL query syntax
- Verify authentication

---

# 8. ROADMAP & TODO

## 8.1. Completed Features ✅

- [x] Basic UI layout với sidebar + topbar
- [x] Dashboard với KPI cards
- [x] OEE Deep Dive comprehensive
- [x] Production Order list + CRUD
- [x] Dispatch Queue
- [x] Execution Tracking (Home)
- [x] Station Execution interface
- [x] Route List + Route Detail
- [x] Operation List + Operation Detail (6 tabs)
- [x] QC Checkpoints management
- [x] Defect Management
- [x] Traceability genealogy
- [x] APS Scheduling Gantt
- [x] Supabase integration setup
- [x] Mock data structure
- [x] TypeScript types
- [x] API endpoints ready

## 8.2. In Progress ⏳

- [ ] Connect real database (waiting for schema from user)
- [ ] Real-time subscriptions
- [ ] User authentication

## 8.3. Planned Features 🔜

### High Priority
- [ ] Advanced search & filters
- [ ] Export to Excel/PDF
- [ ] Notifications & alerts
- [ ] Mobile responsive optimization
- [ ] Dark mode

### Medium Priority
- [ ] User management
- [ ] Role-based access control
- [ ] Audit trail
- [ ] Report builder
- [ ] Email notifications
- [ ] Barcode scanning

### Low Priority
- [ ] Multi-language support
- [ ] Custom themes
- [ ] Advanced analytics (AI/ML)
- [ ] Integration with ERP
- [ ] Mobile app

---

# 9. GLOSSARY (Thuật ngữ)

| Term | Vietnamese | Description |
|------|------------|-------------|
| **MES** | Hệ thống thực thi sản xuất | Manufacturing Execution System |
| **APS** | Lập lịch sản xuất nâng cao | Advanced Planning & Scheduling |
| **OEE** | Hiệu suất thiết bị tổng thể | Overall Equipment Effectiveness |
| **PO** | Lệnh sản xuất | Production Order |
| **WO** | Lệnh làm việc | Work Order |
| **Route** | Quy trình | Manufacturing route/process |
| **Operation** | Công đoạn | Operation/Step in process |
| **Station** | Trạm làm việc | Work station |
| **QC** | Kiểm soát chất lượng | Quality Control |
| **Defect** | Lỗi sản phẩm | Manufacturing defect |
| **Genealogy** | Truy xuất nguồn gốc | Product traceability |
| **Dispatch** | Điều phối | Work dispatch/assignment |
| **Execution** | Thực thi | Work execution |
| **Checkpoint** | Điểm kiểm tra | Quality checkpoint |
| **Lot** | Lô sản xuất | Production lot/batch |

---

# 10. CONTACT & SUPPORT

## 10.1. Documentation
- Hệ thống documentation: `/SYSTEM_DOCUMENTATION.md`
- Supabase setup guide: `/SUPABASE_SETUP_GUIDE.md`
- Integration example: `/src/examples/SupabaseExample.tsx`

## 10.2. Technical Support
- GitHub Issues: [Create issue]
- Email: support@example.com
- Slack: #mes-lite-support

## 10.3. Contributing
1. Fork repository
2. Create feature branch
3. Make changes
4. Submit pull request
5. Code review

---

# 📝 CHANGELOG ok

## Version 1.0.0 (Current)
- ✅ Initial release
- ✅ All core modules implemented
- ✅ Mock data working
- ✅ Supabase integration ready
- ✅ Comprehensive documentation

---

**© 2026 MES Lite Development Team. All rights reserved.**

*Tài liệu này được cập nhật thường xuyên. Kiểm tra version mới nhất trên repository.*

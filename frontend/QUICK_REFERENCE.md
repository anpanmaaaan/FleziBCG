# ⚡ MES LITE - QUICK REFERENCE GUIDE

**Hướng dẫn nhanh cho người dùng và developer**

---

## 🎯 TÓM TẮT HỆ THỐNG

MES Lite là hệ thống quản lý sản xuất với **8 modules chính**:

1. **Dashboard** - Tổng quan KPI và metrics
2. **Performance Analytics** - Phân tích OEE chi tiết
3. **Production Orders** - Quản lý lệnh sản xuất
4. **Dispatch** - Điều phối sản xuất
5. **Execution Tracking** - Theo dõi thực thi real-time
6. **Quality** - Quản lý chất lượng (QC + Defects)
7. **Traceability** - Truy xuất nguồn gốc
8. **APS Scheduling** - Lập lịch sản xuất

---

## 🗂️ CẤU TRÚC DỮ LIỆU CHÍNH

### 1. Production Order (Lệnh sản xuất)
```typescript
{
  id: "PO-001",
  serialNumber: "01082024",
  routeId: "DMES-R11",
  quantity: 100,
  status: "IN_PROGRESS" | "COMPLETED" | "PENDING" | "LATE",
  progress: 45,  // %
  priority: "High" | "Medium" | "Low"
}
```

### 2. Operation (Công đoạn)
```typescript
{
  id: "OP_110000",
  route_id: "DMES-R11",
  sequence: 10,
  name: "Assembly Front Panel",
  station_id: "3000",
  status: "Pending" | "In Progress" | "Completed",
  cycle_time: 120  // seconds
}
```

### 3. Execution Record (Bản ghi thực thi)
```typescript
{
  id: "EXE-001",
  production_order_id: "PO-001",
  operation_id: "OP_110000",
  station_id: "3000",
  operator_name: "John Doe",
  status: "Started" | "Completed",
  quantity_completed: 50
}
```

### 4. Quality Result (Kết quả QC)
```typescript
{
  checkpoint_id: "QC-001",
  result: "Pass" | "Fail" | "NA",
  measured_value: "5.02mm",
  inspector_name: "Jane Smith"
}
```

### 5. Defect (Lỗi)
```typescript
{
  defect_code: "DEF-001",
  defect_name: "Scratch",
  severity: "Critical" | "Major" | "Minor",
  status: "Open" | "Resolved" | "Closed"
}
```

---

## 🚀 WORKFLOW CHÍNH

### Workflow 1: Tạo Production Order → Thực thi
```
1. Production Orders → Add New PO
2. Fill: Serial, Route, Quantity, Priority
3. Submit → PO created
4. Dispatch → Assign to Line
5. Station Execution → Operator thực hiện
6. Complete → Record saved
```

### Workflow 2: Operator thực hiện công việc
```
1. Station Execution
2. Select Station (e.g., "3000")
3. Scan/Select Production Order
4. Select Operation
5. Click "Start Work"
6. Perform tasks
7. Complete QC checkpoints
8. Enter quantity completed
9. Click "Complete Work"
```

### Workflow 3: Quality Inspector kiểm tra
```
1. QC Checkpoints
2. View pending checkpoints
3. Perform inspection
4. Mark Pass/Fail
5. If Fail → Create Defect
6. Defect Management → Track
```

---

## 📁 FILE LOCATIONS

### Pages (Screens)
```
/src/app/pages/
├── Dashboard.tsx           # Dashboard chính
├── OEEDeepDive.tsx        # Phân tích OEE
├── ProductionOrderList.tsx # Danh sách PO
├── DispatchQueue.tsx       # Điều phối
├── Home.tsx               # Execution Tracking
├── StationExecution.tsx    # Giao diện operator
├── RouteList.tsx          # Danh sách Route
├── RouteDetail.tsx        # Chi tiết Route
├── OperationList.tsx      # Danh sách Operation
├── OperationExecutionOverview.tsx # Tổng quan execution theo WO
├── OperationExecutionDetail.tsx   # Chi tiết execution của 1 operation
├── QCCheckpoints.tsx      # QC checkpoints
├── DefectManagement.tsx   # Quản lý lỗi
├── Traceability.tsx       # Truy xuất nguồn gốc
└── APSScheduling.tsx      # Lập lịch
```

### Components
```
/src/app/components/
├── Layout.tsx             # Sidebar + Layout chính
├── TopBar.tsx            # Top navigation bar
├── PageHeader.tsx        # Page header với breadcrumb
├── StatsCard.tsx         # Card hiển thị metrics
├── StatusBadge.tsx       # Badge cho status
└── ui/                   # shadcn/ui components
```

### Data & Types
```
/src/app/data/
├── mockData.ts           # Mock data cho development
└── oee-mock-data.ts      # Mock data cho OEE

/src/types/
└── database.ts           # TypeScript interfaces
```

### Backend
```
/supabase/functions/server/
├── index.tsx             # API server (Hono)
├── db.tsx               # Database operations
└── kv_store.tsx         # Key-value store

/utils/supabase/
└── info.tsx             # Supabase credentials
```

---

## 🔌 API ENDPOINTS

**Base URL:** `https://ftyrfhfjvowcqsxsjtlq.supabase.co/functions/v1/make-server-380ff3c6`

### Production Orders
- `GET /production-orders` - Lấy tất cả
- `GET /production-orders/:id` - Lấy theo ID
- `POST /production-orders` - Tạo mới
- `PUT /production-orders/:id` - Cập nhật
- `DELETE /production-orders/:id` - Xóa

### Execution
- `POST /execution/start` - Bắt đầu
- `POST /execution/complete` - Hoàn thành
- `GET /execution/station/:stationId` - Lấy theo station

### Quality
- `POST /quality/result` - Submit QC
- `GET /quality/execution/:executionId` - Lấy QC results

### Defects
- `POST /defects` - Tạo defect
- `GET /defects` - Lấy tất cả defects

---

## 💻 CODE EXAMPLES

### 1. Fetch Data từ Server
```typescript
import { callServer } from '/src/utils/supabase';

// GET
const response = await callServer('/production-orders');
if (response.success) {
  console.log(response.data);
}

// POST
const response = await callServer('/production-orders', {
  method: 'POST',
  body: JSON.stringify({
    id: 'PO-001',
    product_name: 'Widget A',
    quantity: 100
  })
});
```

### 2. Query Supabase Direct
```typescript
import { supabase } from '/src/utils/supabase';

const { data, error } = await supabase
  .from('production_orders')
  .select('*')
  .eq('status', 'IN_PROGRESS')
  .order('created_at', { ascending: false });
```

### 3. Real-time Subscription
```typescript
useEffect(() => {
  const channel = supabase
    .channel('production_orders_changes')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'production_orders',
    }, (payload) => {
      console.log('Change detected:', payload);
      // Refresh data
    })
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}, []);
```

### 4. Create React Page
```typescript
import { useEffect, useState } from 'react';
import { callServer } from '/src/utils/supabase';
import { PageHeader } from '../components/PageHeader';

export function MyNewPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await callServer('/my-endpoint');
        if (response.success) {
          setData(response.data);
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <PageHeader 
        title="My New Page" 
        description="Description here"
      />
      {/* Your content */}
    </div>
  );
}
```

---

## 🎨 UI COMPONENTS

### Button
```tsx
import { Button } from "@/components/ui/button";

<Button variant="default">Click me</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
```

### Card
```tsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content here
  </CardContent>
</Card>
```

### Table
```tsx
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Column 1</TableHead>
      <TableHead>Column 2</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Data 1</TableCell>
      <TableCell>Data 2</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Badge
```tsx
import { Badge } from "@/components/ui/badge";

<Badge variant="default">Active</Badge>
<Badge variant="destructive">Error</Badge>
<Badge variant="outline">Pending</Badge>
```

---

## 🗺️ NAVIGATION MAP

```
/ (Home - Execution Tracking)
│
├── /dashboard (Dashboard)
│
├── /performance/oee-deep-dive (OEE Deep Dive)
│
├── /production-orders (Production Order List)
│   └── /production-orders/:orderId/work-orders (Work Order Execution Status)
│       └── /work-orders/:woId/operations (Operation Execution Overview)
│           └── /operations/:operationId/detail (Operation Execution Detail)
│
├── /dispatch (Dispatch Queue)
│
├── /station-execution (Station Execution)
│
├── /routes (Route List)
│   └── /routes/:routeId (Route Detail)
│
├── /quality (QC Checkpoints)
│
├── /defects (Defect Management)
│
├── /traceability (Traceability)
│
├── /scheduling (APS Scheduling)
│
└── /settings (Settings)
```

---

## 🔧 COMMON TASKS

### Task 1: Thêm route mới
1. Tạo component trong `/src/app/pages/MyPage.tsx`
2. Import vào `/src/app/routes.ts`
3. Thêm vào array children
4. Thêm link trong `/src/app/components/Layout.tsx`

### Task 2: Tạo API endpoint mới
1. Thêm function trong `/supabase/functions/server/db.tsx`
2. Thêm endpoint trong `/supabase/functions/server/index.tsx`
3. Test với Postman/Thunder Client

### Task 3: Tạo database table mới
1. Vào Supabase SQL Editor
2. Run CREATE TABLE statement
3. Thêm TypeScript interface vào `/src/types/database.ts`
4. Tạo CRUD functions trong `db.tsx`

### Task 4: Thêm mock data
1. Vào `/src/app/data/mockData.ts`
2. Define interface (nếu chưa có)
3. Export const array
4. Import và sử dụng trong component

---

## 📊 METRICS & KPIs

### OEE Formula
```
OEE = Availability × Performance × Quality

Availability = (Operating Time / Planned Production Time) × 100%
Performance = (Actual Output / Theoretical Output) × 100%
Quality = (Good Output / Total Output) × 100%
```

### Status Values
```
Production Order Status:
- PENDING: Chưa bắt đầu
- IN_PROGRESS: Đang thực hiện
- COMPLETED: Hoàn thành
- LATE: Trễ hạn

Operation Status:
- Ready: Sẵn sàng
- In Progress: Đang thực hiện
- Completed: Hoàn thành
- Blocked: Bị chặn

Defect Severity:
- Critical: Nghiêm trọng
- Major: Quan trọng
- Minor: Nhỏ
```

---

## 🐛 TROUBLESHOOTING

### "Cannot read properties of undefined"
→ Check data structure, add optional chaining `?.`

### "Network request failed"
→ Check Supabase URL & API keys in `/utils/supabase/info.tsx`

### "Table does not exist"
→ Create table trong Supabase SQL Editor

### "Route not found"
→ Check spelling trong `/src/app/routes.ts`

### Mock data không hiển thị
→ Check import path, verify export/import syntax

---

## 📚 CHEAT SHEET

### Import paths
```typescript
// Components
import { Layout } from './components/Layout';
import { Button } from './components/ui/button';

// Utils
import { supabase, callServer } from '/src/utils/supabase';

// Types
import type { ProductionOrder } from '/src/types/database';

// Data
import { productionOrders } from '../data/mockData';
```

### Tailwind CSS Classes (Most used)
```css
/* Layout */
flex, grid, hidden, block, inline-block

/* Spacing */
p-4, px-6, py-3, m-4, mx-auto, gap-4

/* Sizing */
w-full, h-screen, max-w-7xl, min-h-[400px]

/* Colors */
bg-white, text-slate-700, border-slate-200
bg-blue-500, text-blue-600, hover:bg-blue-600

/* Typography */
text-sm, text-lg, text-2xl, font-bold, font-medium

/* Borders */
border, border-2, rounded-lg, shadow-sm

/* Flexbox */
justify-between, items-center, flex-col, flex-1

/* States */
hover:bg-gray-100, focus:ring-2, active:scale-95
```

### React Hooks patterns
```typescript
// State
const [data, setData] = useState<Type[]>([]);
const [loading, setLoading] = useState(true);

// Effect
useEffect(() => {
  // Fetch data
  return () => {
    // Cleanup
  };
}, [dependencies]);

// Callback
const handleClick = useCallback(() => {
  // Handle
}, [deps]);
```

---

## 🎓 LEARNING RESOURCES

### Documentation
- [Full System Docs](/SYSTEM_DOCUMENTATION.md)
- [Supabase Setup](/SUPABASE_SETUP_GUIDE.md)
- [Code Example](/src/examples/SupabaseExample.tsx)

### External Resources
- React: https://react.dev
- TypeScript: https://typescriptlang.org
- Tailwind CSS: https://tailwindcss.com
- Supabase: https://supabase.com/docs
- shadcn/ui: https://ui.shadcn.com

---

**💡 TIP:** Bookmark tài liệu này để tra cứu nhanh!

**📧 Need help?** Check `/SYSTEM_DOCUMENTATION.md` cho thông tin chi tiết hơn.

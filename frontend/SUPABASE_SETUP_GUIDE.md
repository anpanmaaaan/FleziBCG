# 🚀 HƯỚNG DẪN SETUP SUPABASE CHO MES LITE - STEP BY STEP

## ✅ **ĐÃ HOÀN TẤT**
- [x] Supabase client installed (`@supabase/supabase-js`)
- [x] Project ID & API keys configured
- [x] Frontend helper utils created (`/src/utils/supabase.ts`)
- [x] Server infrastructure ready (`/supabase/functions/server/`)
- [x] KV Store table available

---

## 📊 **BƯỚC 1: TẠO DATABASE SCHEMA TRÊN SUPABASE**

### 1.1. Truy cập Supabase Dashboard
Vào link: **https://supabase.com/dashboard/project/ftyrfhfjvowcqsxsjtlq/editor**

### 1.2. Tạo Tables cho MES Lite

**Bạn cần share DB schema của bạn với tôi**, hoặc sử dụng schema mẫu dưới đây:

#### **Schema mẫu cho MES Universal Manufacturing:**

```sql
-- ===========================
-- 1. PRODUCTION ORDERS TABLE
-- ===========================
CREATE TABLE production_orders (
  id TEXT PRIMARY KEY,
  product_id TEXT NOT NULL,
  product_name TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  route_id TEXT NOT NULL,
  priority TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
  status TEXT NOT NULL CHECK (status IN ('Planned', 'Released', 'In Progress', 'Completed', 'On Hold', 'Cancelled')),
  target_start_date TIMESTAMP,
  target_end_date TIMESTAMP,
  actual_start_date TIMESTAMP,
  actual_end_date TIMESTAMP,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 2. ROUTES TABLE
-- ===========================
CREATE TABLE routes (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  product_id TEXT,
  status TEXT CHECK (status IN ('Active', 'Inactive', 'Draft')),
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 3. OPERATIONS TABLE
-- ===========================
CREATE TABLE operations (
  id TEXT PRIMARY KEY,
  route_id TEXT NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
  sequence INTEGER NOT NULL,
  name TEXT NOT NULL,
  station_id TEXT NOT NULL,
  station_name TEXT NOT NULL,
  cycle_time INTEGER, -- seconds
  status TEXT CHECK (status IN ('Pending', 'In Progress', 'Completed', 'Blocked', 'Skipped')),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 4. STATIONS TABLE
-- ===========================
CREATE TABLE stations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  line_id TEXT NOT NULL,
  line_name TEXT NOT NULL,
  type TEXT,
  status TEXT CHECK (status IN ('Available', 'Occupied', 'Maintenance', 'Offline')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 5. EXECUTION RECORDS TABLE
-- ===========================
CREATE TABLE execution_records (
  id TEXT PRIMARY KEY,
  production_order_id TEXT NOT NULL REFERENCES production_orders(id),
  operation_id TEXT NOT NULL REFERENCES operations(id),
  station_id TEXT NOT NULL REFERENCES stations(id),
  operator_id TEXT,
  operator_name TEXT,
  status TEXT CHECK (status IN ('Started', 'Paused', 'Completed', 'Failed')),
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  quantity_completed INTEGER DEFAULT 0,
  quantity_rejected INTEGER DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 6. QUALITY CHECKPOINTS TABLE
-- ===========================
CREATE TABLE quality_checkpoints (
  id TEXT PRIMARY KEY,
  operation_id TEXT NOT NULL REFERENCES operations(id),
  checkpoint_name TEXT NOT NULL,
  checkpoint_type TEXT CHECK (checkpoint_type IN ('Dimensional', 'Visual', 'Functional', 'Other')),
  specification TEXT,
  is_mandatory BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 7. QUALITY RESULTS TABLE
-- ===========================
CREATE TABLE quality_results (
  id TEXT PRIMARY KEY,
  execution_record_id TEXT NOT NULL REFERENCES execution_records(id),
  checkpoint_id TEXT NOT NULL REFERENCES quality_checkpoints(id),
  result TEXT CHECK (result IN ('Pass', 'Fail', 'NA')),
  measured_value TEXT,
  inspector_id TEXT,
  inspector_name TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 8. DEFECTS TABLE
-- ===========================
CREATE TABLE defects (
  id TEXT PRIMARY KEY,
  production_order_id TEXT REFERENCES production_orders(id),
  operation_id TEXT REFERENCES operations(id),
  defect_code TEXT NOT NULL,
  defect_name TEXT NOT NULL,
  category TEXT,
  severity TEXT CHECK (severity IN ('Critical', 'Major', 'Minor')),
  quantity INTEGER DEFAULT 1,
  detected_by TEXT,
  detected_at TIMESTAMP DEFAULT NOW(),
  status TEXT CHECK (status IN ('Open', 'In Review', 'Resolved', 'Closed')),
  resolution TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 9. MATERIALS TABLE
-- ===========================
CREATE TABLE materials (
  id TEXT PRIMARY KEY,
  material_code TEXT NOT NULL UNIQUE,
  material_name TEXT NOT NULL,
  material_type TEXT,
  unit_of_measure TEXT,
  current_stock NUMERIC DEFAULT 0,
  min_stock NUMERIC,
  max_stock NUMERIC,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- 10. MATERIAL CONSUMPTION TABLE
-- ===========================
CREATE TABLE material_consumption (
  id TEXT PRIMARY KEY,
  execution_record_id TEXT NOT NULL REFERENCES execution_records(id),
  material_id TEXT NOT NULL REFERENCES materials(id),
  quantity_used NUMERIC NOT NULL,
  lot_number TEXT,
  consumed_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- INDEXES FOR PERFORMANCE
-- ===========================
CREATE INDEX idx_production_orders_status ON production_orders(status);
CREATE INDEX idx_production_orders_priority ON production_orders(priority);
CREATE INDEX idx_operations_route_id ON operations(route_id);
CREATE INDEX idx_execution_records_po_id ON execution_records(production_order_id);
CREATE INDEX idx_execution_records_station_id ON execution_records(station_id);
CREATE INDEX idx_quality_results_execution_id ON quality_results(execution_record_id);
CREATE INDEX idx_defects_po_id ON defects(production_order_id);
CREATE INDEX idx_material_consumption_execution_id ON material_consumption(execution_record_id);
```

### 1.3. Run SQL Script

1. Copy toàn bộ SQL ở trên
2. Paste vào SQL Editor trên Supabase
3. Click "Run" để tạo tables

---

## 🔧 **BƯỚC 2: TẠO SERVER ENDPOINTS**

Tôi đã chuẩn bị sẵn file `/supabase/functions/server/db.tsx` (sẽ tạo ở step tiếp theo).

Server sẽ expose các endpoints:

### Production Orders
- `GET /make-server-380ff3c6/production-orders` - Lấy tất cả
- `GET /make-server-380ff3c6/production-orders/:id` - Lấy theo ID
- `POST /make-server-380ff3c6/production-orders` - Tạo mới
- `PUT /make-server-380ff3c6/production-orders/:id` - Cập nhật
- `DELETE /make-server-380ff3c6/production-orders/:id` - Xóa

### Routes & Operations
- `GET /make-server-380ff3c6/routes` - Lấy tất cả routes
- `GET /make-server-380ff3c6/routes/:id/operations` - Lấy operations của route

### Execution
- `POST /make-server-380ff3c6/execution/start` - Bắt đầu thực thi
- `POST /make-server-380ff3c6/execution/complete` - Hoàn thành
- `GET /make-server-380ff3c6/execution/:stationId` - Lấy theo station

### Quality
- `POST /make-server-380ff3c6/quality/checkpoint` - Submit QC result
- `GET /make-server-380ff3c6/quality/:executionId` - Lấy QC results

---

## 📱 **BƯỚC 3: SỬ DỤNG TRONG FRONTEND**

### 3.1. Import Supabase Client

```tsx
import { supabase, callServer } from '/src/utils/supabase';
```

### 3.2. Example: Fetch Production Orders

```tsx
// Option 1: Gọi trực tiếp Supabase (realtime)
const { data, error } = await supabase
  .from('production_orders')
  .select('*')
  .order('created_at', { ascending: false });

// Option 2: Gọi qua server API (có business logic)
const data = await callServer('/production-orders');
```

### 3.3. Example: Create Production Order

```tsx
const newOrder = await callServer('/production-orders', {
  method: 'POST',
  body: JSON.stringify({
    id: 'PO-' + Date.now(),
    product_id: 'PROD-001',
    product_name: 'Widget A',
    quantity: 100,
    route_id: 'ROUTE-001',
    priority: 'High',
    status: 'Planned',
  }),
});
```

---

## 🎯 **BƯỚC TIẾP THEO**

1. **Share DB Schema của bạn** - Tôi sẽ tạo đúng chuẩn
2. **Tôi sẽ tạo server endpoints** - CRUD cho tất cả entities
3. **Tôi sẽ update frontend components** - Connect với real data

---

## ❓ **CÂU HỎI CHO BẠN**

1. Bạn đã có DB schema chưa? Nếu có, share cho tôi
2. Bạn muốn dùng schema mẫu ở trên không?
3. Bạn cần thêm tables nào khác? (Users, Shifts, Downtime, etc.)
4. Bạn có cần authentication/authorization không?

**Sau khi bạn trả lời, tôi sẽ:**
- Tạo đầy đủ server endpoints
- Tạo TypeScript types
- Update frontend components để connect real data
- Setup real-time subscriptions (nếu cần)

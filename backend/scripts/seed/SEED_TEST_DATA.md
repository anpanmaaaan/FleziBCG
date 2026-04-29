# Hướng dẫn Seed Test Data

## Cách sử dụng nhanh

**Master Data (Products & Routings) — Chạy trước:**
```bash
cd backend
.venv\Scripts\python scripts/seed/seed_products_and_routing.py
```

**Execution Test Data (Operations & Claims):**
```bash
.venv\Scripts\python scripts/seed/seed_test_data.py
```

---

## Master Data: Products & Routings

### Cấu trúc Sản phẩm & Routing

```
Products (6):
├─ WIDGET-A (FINISHED_GOOD)
│  └─ R-WIDGET-A Routing (3 ops: Assembly → Install Motor → QC)
├─ WIDGET-B (FINISHED_GOOD)
│  └─ R-WIDGET-B Routing (4 ops: Assembly → Install Motor → Install Bearing → QC)
├─ FRAME-001 (SEMI_FINISHED)
│  └─ R-FRAME Routing (2 ops: Cut & Prepare → Weld Assembly)
├─ MOTOR-STD (COMPONENT)
├─ BEARING-001 (COMPONENT)
└─ CONNECTOR-A (COMPONENT)
```

### Resource Requirements

| Product | Operation | Required Capability | Qty |
|---------|-----------|-------------------|-----|
| WIDGET-A | OP-10 (Assembly Frame) | ASSEMBLY_WORKER | 2 |
| WIDGET-A | OP-20 (Install Motor) | ASSEMBLY_WORKER | 1 |
| WIDGET-A | OP-20 (Install Motor) | MOTOR_SPECIALIST | 1 |
| WIDGET-A | OP-30 (Test & QC) | QC_INSPECTOR | 1 |
| WIDGET-B | OP-10 (Assembly Frame) | ASSEMBLY_WORKER | 2 |
| WIDGET-B | OP-30 (Test & QC) | QC_INSPECTOR_SENIOR | 1 |
| FRAME-001 | OP-20 (Weld Assembly) | WELDER | 1 |

---

## Execution Test Data: Operations & Claims

### Scenario 1: Station Queue (3 Operations)
- **Nơi:** STATION-A
- **Users:** alice, bob (Operators)
- **Data:**
  - 3 operations (OP-001, OP-002, OP-003) - all PLANNED
  - Có sẵn trong queue để claim/execute

### Scenario 2: In-Progress with Claim  
- **Nơi:** STATION-B
- **Users:** alice-b (Operator), supervisor (Supervisor)
- **Data:**
  - OP-001: IN_PROGRESS (đã hoàn thành 5/25 cái)
  - OP-002: PLANNED
  - Giả lập tình huống đang làm việc

### Scenario 3: Multi-Station Operations
- **Nơi:** STATION-A, STATION-B, STATION-C
- **Users:** operator-A, operator-B, operator-C (Operators)
- **Data:**
  - 3 operations across 3 stations
  - Test case cho multi-station workflow

---

## Xem dữ liệu

### Option 1: PostgreSQL CLI
```bash
psql -h localhost -U mes -d mes -W
# password: mes

# Query examples
SELECT * FROM production_orders WHERE order_number LIKE 'TEST-DEMO-%';
SELECT * FROM work_orders WHERE work_order_number LIKE 'TEST-DEMO-%';
SELECT * FROM operations WHERE operation_number LIKE 'TEST-DEMO-%';
```

### Option 2: CloudBeaver UI (Database IDE)
```
http://localhost:8978
```
Cần khởi động với profile dev-tools trước:
```bash
docker-compose --profile dev-tools up -d
```

### Option 3: Frontend UI
```
http://localhost
```
Login với user `demo` / `demo123`, sau đó chọn station và xem queue

---

## Dữ liệu được giữ lại (Persistent)

✓ **Data KHÔNG bị xóa tự động** như trong tests  
✓ Stored trong Docker volume `docker_postgres_data`  
✓ Tồn tại khi container restart  
✓ Giữ lại khi chạy tests (tests tạo/xóa data riêng)

---

## Xóa seed data (nếu cần reset)

```bash
cd backend
psql -h localhost -U mes -d mes -W << EOF
-- Xóa seed data TEST-DEMO-*
DELETE FROM operation_claims WHERE operation_id IN (
  SELECT id FROM operations WHERE operation_number LIKE 'TEST-DEMO-%'
);
DELETE FROM execution_events WHERE operation_id IN (
  SELECT id FROM operations WHERE operation_number LIKE 'TEST-DEMO-%'
);
DELETE FROM operations WHERE operation_number LIKE 'TEST-DEMO-%';
DELETE FROM work_orders WHERE work_order_number LIKE 'TEST-DEMO-%';
DELETE FROM production_orders WHERE order_number LIKE 'TEST-DEMO-%';
COMMIT;
EOF
```

---

## Database URL

- **Host:** localhost (hoặc `db` nếu từ Docker container)
- **Port:** 5432
- **Database:** mes
- **User:** mes
- **Password:** mes

---

## Cấu trúc dữ liệu

Mỗi scenario tạo:
1. **ProductionOrder** — Lệnh sản xuất, định nghĩa sản phẩm & số lượng
2. **WorkOrder** — Đơn hàng công việc, gộp các operation
3. **Operations** — Các công việc cụ thể tại station
4. **Users + Roles** — Operator/Supervisor assignments per station
5. **Scopes** — Station scopes cho authorization

Không tạo:
- ExecutionEvents (manual hoặc qua UI)
- OperationClaims (manual hoặc qua API claim endpoint)
